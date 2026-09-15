#!/usr/bin/env python3
"""Offline companion-skill installer. Dry-run unless --apply is explicit.

Follows the earlier upgrade workflow: preflight all bytes, refuse changed local
files, stage, preserve exact rollback copies, then publish. No CAD/MCP operations.
Run from the source checkout; --skills-dir is an explicit confirmed discovery root.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import uuid

REPO = Path(__file__).resolve().parent
RECEIPT = '.fcskill-install.json'
IGNORED = {'__pycache__', '.pytest_cache'}


class InstallError(RuntimeError):
    pass


def sha(data):
    return hashlib.sha256(data).hexdigest()


def checked_root(path):
    path = Path(path).expanduser().absolute()
    for p in (path, *path.parents):
        if p.is_symlink() or (hasattr(p, 'is_junction') and p.is_junction()):
            raise InstallError(f'Refusing linked root: {p}')
    if not path.is_dir():
        raise InstallError(f'Expected an existing explicit directory: {path}')
    return path.resolve()


def safe_path(root, relative):
    if not isinstance(relative,str) or not relative or '\\' in relative or ':' in relative or '\0' in relative:
        raise InstallError('Invalid relative path')
    pure = PurePosixPath(relative)
    if pure.is_absolute() or any(p in ('','.','..') for p in relative.split('/')):
        raise InstallError('Expected canonical relative path')
    result = root
    for part in pure.parts:
        result = result/part
        if result.is_symlink() or (hasattr(result, 'is_junction') and result.is_junction()):
            raise InstallError(f'Refusing linked path: {result}')
    if not result.resolve().is_relative_to(root.resolve()):
        raise InstallError('Path escaped its root')
    return result


def files_under(root):
    for path in sorted(root.rglob('*')):
        rel = path.relative_to(root)
        if any(part in IGNORED for part in rel.parts) or path.suffix in ('.pyc','.pyo'):
            continue
        safe_path(root, rel.as_posix())
        if path.is_file():
            yield rel.as_posix(),path


def snapshot(root):
    if not root.exists():
        return None
    if not root.is_dir() or (root/'.git').exists():
        raise InstallError('Destination must be a skill directory, not a file or Git checkout')
    return {rel:sha(path.read_bytes()) for rel,path in files_under(root)}


def identity(root):
    entry = safe_path(root,'SKILL.md')
    if not entry.is_file():
        raise InstallError(f'No SKILL.md: {root}')
    content = entry.read_text(encoding='utf-8')
    front = content.split('---',2)
    if len(front)!=3 or front[0].strip():
        raise InstallError('Missing skill frontmatter')
    match = re.search(r'^name:\s*[\"\']?([a-z0-9-]+)[\"\']?\s*$',front[1],re.M)
    if not match or not re.search(r'^description:\s*\S',front[1],re.M):
        raise InstallError('Missing skill name/description')
    return match.group(1)


def payload(repo, spec):
    source = repo if spec['source']=='.' else safe_path(repo,spec['source'])
    if identity(source)!=spec['name']:
        raise InstallError('Source skill identity mismatch')
    result = {}
    for rel in spec['include']:
        selected = safe_path(source,rel)
        if not selected.exists():
            raise InstallError(f'Missing payload: {rel}')
        items = files_under(selected) if selected.is_dir() else [('',selected)]
        for _, path in items:
            name = path.relative_to(source).as_posix()
            result[name] = path.read_bytes()
    return result


def plan_install(repo, selection, skills_dir, baseline_root=None):
    repo, root = checked_root(repo), checked_root(skills_dir)
    if selection not in ('core','blockfolk','all'):
        raise InstallError('Unknown selection')
    catalog = json.loads((repo/'skill-packages.json').read_text(encoding='utf-8'))
    if catalog['schema_version']!=1:
        raise InstallError('Unsupported package catalog')
    keys = ['core','blockfolk'] if selection=='all' else [selection]
    selected_names = [catalog['packages'][key]['name'] for key in keys]
    if len(set(selected_names))!=len(selected_names):
        raise InstallError('Selected packages must have distinct peer skill names')
    baseline = checked_root(baseline_root) if baseline_root else None
    rows = []
    for key in keys:
        spec = catalog['packages'][key]
        name = spec['name']
        dependency = spec.get('requires')
        if dependency and dependency not in selected_names:
            dep = safe_path(root,dependency)
            if not dep.is_dir() or identity(dep)!=dependency or not (dep/'scripts/fcskill/__init__.py').is_file():
                raise InstallError('Blockfolk requires a separately installed general FreeCAD skill')
        data = payload(repo,spec)
        expected = {rel:sha(value) for rel,value in data.items()}
        target = safe_path(root,name)
        before = snapshot(target)
        action = 'ADD'
        if before is not None:
            if identity(target)!=name:
                raise InstallError('Existing destination has another skill identity')
            existing_payload = {k:v for k,v in before.items() if k!=RECEIPT}
            if existing_payload==expected:
                action = 'UNCHANGED'
            else:
                managed = False
                if RECEIPT in before:
                    old = json.loads((target/RECEIPT).read_text(encoding='utf-8'))
                    managed = old.get('name')==name and old.get('files')==existing_payload
                known = snapshot(safe_path(baseline,name)) if baseline else None
                if not managed and before!=known:
                    raise InstallError(f'Conflict: {name}; local/unmanaged modifications require an exact known baseline, not force')
                action = 'REPLACE'
        rows.append(dict(key=key,name=name,action=action,before=before,files=expected))
    return dict(status='DRY_RUN',skills_dir=str(root),selection=selection,packages=rows)


def _publish_directory(staged, target):
    os.replace(staged,target)


def install(repo, selection, skills_dir, backups_dir, baseline_root=None):
    repo, root, backups = checked_root(repo),checked_root(skills_dir),checked_root(backups_dir)
    if backups.is_relative_to(root) or root.is_relative_to(backups):
        raise InstallError('Backup directory must be separate from the discovery root and its ancestors')
    plan = plan_install(repo,selection,root,baseline_root)
    if all(row['action']=='UNCHANGED' for row in plan['packages']):
        return {**plan,'status':'ALREADY_INSTALLED','backup_directory':None}
    lock = root/'.fcskill-install.lock'
    with lock.open('x',encoding='utf-8') as output:
        output.write(str(os.getpid()))
    txn = None
    changed = []
    try:
        plan = plan_install(repo,selection,root,baseline_root)
        txn = backups/('skills-'+uuid.uuid4().hex)
        txn.mkdir()
        catalog = json.loads((repo/'skill-packages.json').read_text(encoding='utf-8'))
        # Stage every selected payload before changing any destination.
        for row in plan['packages']:
            if row['action']=='UNCHANGED': continue
            stage = txn/'stage'/row['name']
            stage.mkdir(parents=True)
            data = payload(repo,catalog['packages'][row['key']])
            if {r:sha(v) for r,v in data.items()}!=row['files']:
                raise InstallError('Source changed during staging')
            for rel,value in data.items():
                p=safe_path(stage,rel)
                p.parent.mkdir(parents=True,exist_ok=True)
                p.write_bytes(value)
            (stage/RECEIPT).write_text(json.dumps({'schema_version':1,'name':row['name'],'files':row['files']},indent=2)+'\n',encoding='utf-8')
            row['after'] = snapshot(stage)
            if {k:v for k,v in row['after'].items() if k!=RECEIPT}!=row['files']:
                raise InstallError('Staged bytes differ')
        for row in plan['packages']:
            if row['action']=='UNCHANGED': continue
            target = safe_path(root,row['name'])
            if snapshot(target)!=row['before']:
                raise InstallError('Concurrent destination change')
            old = txn/'before'/row['name']
            if target.exists():
                old.parent.mkdir(exist_ok=True)
                os.replace(target,old)
                changed.append(row)
                if snapshot(old)!=row['before']:
                    raise InstallError('Backup bytes differ')
            else:
                changed.append(row)
            _publish_directory(txn/'stage'/row['name'],target)
            if snapshot(target)!=row['after']:
                raise InstallError('Installed bytes differ')
        report={**plan,'status':'APPLIED','backup_directory':str(txn)}
        (txn/'receipt.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        return report
    except BaseException:
        recovery=[]
        for row in reversed(changed):
            target=safe_path(root,row['name'])
            try:
                current=snapshot(target)
                if current is not None:
                    if current!=row['after']:
                        raise InstallError('Concurrent edits block rollback; preserve for review')
                    failed=txn/'failed-publication'/row['name']
                    failed.parent.mkdir(exist_ok=True)
                    os.replace(target,failed)
                old=txn/'before'/row['name']
                if old.exists(): os.replace(old,target)
            except Exception as exc:
                recovery.append(str(exc))
        if txn:
            (txn/'failed-install.json').write_text(json.dumps({'plan':plan,'recovery_errors':recovery},indent=2),encoding='utf-8')
        if recovery: raise InstallError('Rollback needs review: '+str(recovery))
        raise
    finally:
        lock.unlink()


def rollback(receipt, apply=False):
    receipt=Path(receipt).expanduser().absolute()
    txn=checked_root(receipt.parent)
    receipt=safe_path(txn,receipt.name)
    report=json.loads(receipt.read_text(encoding='utf-8'))
    root=checked_root(report['skills_dir'])
    if txn.is_relative_to(root) or root.is_relative_to(txn):
        raise InstallError('Invalid backup/discovery relationship')
    if report.get('status')!='APPLIED' or (txn/'rollback.json').exists():
        raise InstallError('Not an unconsumed successful installation receipt')
    changes=[r for r in report['packages'] if r['action']!='UNCHANGED']
    def preflight():
        for row in changes:
            if snapshot(safe_path(root,row['name']))!=row['after']:
                raise InstallError('Installed files changed; refusing rollback overwrite')
            if snapshot(safe_path(txn,'before/'+row['name']))!=row['before']:
                raise InstallError('Backup changed or missing')
    preflight()
    if not apply: return {'status':'ROLLBACK_DRY_RUN','skills_dir':str(root),'skills':[r['name'] for r in changes]}
    lock=root/'.fcskill-install.lock'
    with lock.open('x') as out: out.write(str(os.getpid()))
    moved=[]
    try:
        preflight()
        for row in reversed(changes):
            target=safe_path(root,row['name'])
            displaced=txn/'rolled-back'/row['name']
            displaced.parent.mkdir(exist_ok=True)
            os.replace(target,displaced)
            moved.append(row)
            old=txn/'before'/row['name']
            if old.exists(): os.replace(old,target)
        result={'status':'ROLLED_BACK','skills_dir':str(root),'preserved_replaced_files':str(txn/'rolled-back')}
        (txn/'rollback.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
        return result
    except BaseException:
        # If restoration fails partway, recover the installed state from the
        # displaced directories; never delete either version or later edits.
        recovery=[]
        for row in reversed(moved):
            target=safe_path(root,row['name'])
            try:
                current=snapshot(target)
                if current is not None:
                    if current!=row['before']:
                        raise InstallError('Concurrent edits block rollback recovery')
                    old=txn/'before'/row['name']
                    old.parent.mkdir(exist_ok=True)
                    os.replace(target,old)
                os.replace(txn/'rolled-back'/row['name'],target)
            except Exception as exc:
                recovery.append(str(exc))
        if recovery: raise InstallError(f'Rollback recovery needs review at {txn}: {recovery}')
        raise
    finally:
        lock.unlink()


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('selection',choices=['core','blockfolk','all','rollback'])
    parser.add_argument('--skills-dir',type=Path)
    parser.add_argument('--backups-dir',type=Path)
    parser.add_argument('--baseline-root',type=Path,help='Known peer skill snapshot root; never a force-overwrite option')
    parser.add_argument('--receipt',type=Path)
    parser.add_argument('--apply',action='store_true')
    args=parser.parse_args(argv)
    try:
        if args.selection=='rollback':
            if not args.receipt: raise InstallError('--receipt required')
            result=rollback(args.receipt,args.apply)
        else:
            if not args.skills_dir: raise InstallError('--skills-dir must be explicitly resolved')
            if args.apply:
                if not args.backups_dir: raise InstallError('--backups-dir required with --apply')
                result=install(REPO,args.selection,args.skills_dir,args.backups_dir,args.baseline_root)
            else: result=plan_install(REPO,args.selection,args.skills_dir,args.baseline_root)
        print(json.dumps(result,indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({'status':'REFUSED_OR_FAILED','error':str(exc)},indent=2))
        return 2


if __name__=='__main__':
    raise SystemExit(main())
