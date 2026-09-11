"""Ownership, preflight, and recoverable operation records. No server replacement."""
from contextlib import contextmanager
import json
import os
from pathlib import Path
import threading
import uuid
import zipfile
from .contracts import file_hash, write_json

def canonical(path):
    return str(Path(path).resolve())

def outside_tree(path, tree):
    p, t = Path(path).resolve(), Path(tree).resolve()
    if p == t or t in p.parents:
        raise ValueError('Scratch path is inside protected tree')
    return str(p)

def preflight(path, expected_sha256=None):
    p = Path(path).resolve(strict=True)
    with p.open('rb') as handle:
        prefix = handle.read(512)
    if prefix.lstrip().startswith(b'version https://git-lfs.github.com/spec/v1'):
        raise ValueError('Unhydrated Git LFS pointer')
    digest = file_hash(p)
    if expected_sha256 and digest.lower() != expected_sha256.lower():
        raise ValueError('Source checksum mismatch')
    if p.suffix.lower() in ('.step', '.stp'):
        if not prefix.lstrip().startswith(b'ISO-10303-21;'):
            raise ValueError('Not a supported STEP text payload')
    elif p.suffix.lower() in ('.fcstd', '.zip'):
        with zipfile.ZipFile(p) as z:
            if z.testzip() is not None:
                raise ValueError('Corrupt archive payload')
            if p.suffix.lower() == '.fcstd' and 'Document.xml' not in z.namelist():
                raise ValueError('FCStd missing Document.xml')
    elif not prefix:
        raise ValueError('Empty source')
    return {'path': str(p), 'sha256': digest, 'size': p.stat().st_size,
            'scope': 'file integrity/format only; not geometry or security approval'}

def inventory():
    import FreeCAD as App
    rows = []
    for d in App.listDocuments().values():
        modified, api = None, None
        if App.GuiUp:
            import FreeCADGui as Gui
            gd = Gui.getDocument(d.Name)
            if hasattr(gd, 'Modified'):
                modified, api = bool(gd.Modified), 'Gui.Document.Modified'
        rows.append({'name': d.Name, 'label': d.Label,
                     'path': canonical(d.FileName) if d.FileName else None,
                     'modified': modified, 'modified_api': api,
                     'objects': [(o.Name, o.TypeId) for o in d.Objects]})
    return rows

def gui_thread():
    import FreeCAD as App
    if App.GuiUp:
        from PySide import QtCore, QtWidgets
        if QtCore.QThread.currentThread() != QtWidgets.QApplication.instance().thread():
            raise RuntimeError('Document operations require GUI thread')

_writer = threading.RLock()

@contextmanager
def writer():
    gui_thread()
    if not _writer.acquire(blocking=False):
        raise RuntimeError('Another helper mutation is active in this process')
    try:
        yield
    finally:
        _writer.release()

class OwnedDocument:
    """Explicit capability for a document created by this helper, not a name match."""
    def __init__(self, doc):
        self.doc = doc
        self.path = None

    @classmethod
    def create(cls, name):
        import FreeCAD as App
        with writer():
            return cls(App.newDocument(name))

    def save_new(self, path):
        target = Path(path).resolve()
        if target.exists():
            raise FileExistsError('Refusing to overwrite an existing file')
        target.parent.mkdir(parents=True, exist_ok=True)
        with writer():
            self.doc.recompute()
            self.doc.saveAs(str(target))
            # App.saveAs does not clear GUI Modified on the tested 1.1.3 build.
            # GUI save writes only the newly claimed path and updates GUI state.
            import FreeCAD as App
            if App.GuiUp:
                import FreeCADGui as Gui
                if not Gui.getDocument(self.doc.Name).save():
                    raise RuntimeError('GUI save failed')
        self.path = str(target)
        if canonical(self.doc.FileName) != self.path:
            raise RuntimeError('Unexpected document save destination')
        return preflight(target)

    def reopen(self):
        import FreeCAD as App
        if not self.path or canonical(self.doc.FileName) != self.path:
            raise RuntimeError('Exact owned path required')
        if App.getDocument(self.doc.Name) != self.doc:
            raise RuntimeError('Owned document identity changed')
        row = next(r for r in inventory() if r['name'] == self.doc.Name)
        if row['modified'] is not False:
            raise RuntimeError('Refusing to close modified or unknown-state document')
        preflight(self.path)
        with writer():
            App.closeDocument(self.doc.Name)
            self.doc = App.openDocument(self.path)
            if canonical(self.doc.FileName) != self.path:
                raise RuntimeError('Reopen resolved to another file')
            self.doc.recompute()
        return self.doc

class Operation:
    """Durable journal; uncertain crash/timeout is not retried automatically."""
    def __init__(self, directory, target, input_identity, intended_output, operation_id=None):
        self.id = operation_id or uuid.uuid4().hex
        if not self.id.replace('-', '').isalnum():
            raise ValueError('Unsafe operation ID')
        self.path = Path(directory).resolve() / (self.id + '.json')
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.record = {'id': self.id, 'pid': os.getpid(), 'target': target,
                       'input': input_identity, 'output': intended_output, 'state': 'PREPARED'}
        with self.path.open('x', encoding='utf8') as f:
            json.dump(self.record, f)

    def run(self, mutation, postcondition):
        with writer():
            actual=json.loads(self.path.read_text(encoding='utf8'))
            if actual['state']!='PREPARED' or actual!=self.record:
                raise RuntimeError('Operation already started or record changed; recover, do not replay')
            self.record['state'] = 'RUNNING'; write_json(self.path, self.record)
            try:
                result = mutation()
                proof = postcondition()
                if proof is not True:
                    self.record['state'] = 'UNRESOLVED'
                else:
                    self.record['state'] = 'COMPLETED'
                write_json(self.path, self.record)
                return result
            except Exception as exc:
                self.record.update(state='UNRESOLVED', error=str(exc))
                write_json(self.path, self.record)
                raise

def recover_operation(path, postcondition, still_running=False):
    record = json.loads(Path(path).read_text(encoding='utf8'))
    if still_running:
        return {'state': 'RUNNING', 'retry_safe': False, 'record': record}
    try:
        proof = postcondition(record)
    except Exception:
        proof = None
    # Read-only recovery; caller must establish operation-specific identity.
    state = 'COMPLETED' if proof is True else 'UNRESOLVED'
    return {'state': state, 'retry_safe': False, 'record': record}
