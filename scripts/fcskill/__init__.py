"""Native operational checks, not an independent engineering verifier."""
__version__ = '2.0.0'

def identity():
    from pathlib import Path
    from .contracts import file_hash
    root = Path(__file__).resolve().parent
    return {'version': __version__, 'path': str(root),
            'modules': {p.name: file_hash(p) for p in sorted(root.glob('*.py'))}}
