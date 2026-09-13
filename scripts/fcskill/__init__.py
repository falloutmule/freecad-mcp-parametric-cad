"""Native operational checks, not an independent engineering verifier."""
__version__ = '2.1.0.dev1'

def identity():
    from pathlib import Path
    from .contracts import file_hash
    root = Path(__file__).resolve().parent
    return {'version': __version__, 'path': str(root),
            'modules': {p.relative_to(root).as_posix(): file_hash(p) for p in sorted(root.rglob('*.py'))}}


def capabilities():
    """Report available helpers without claiming native acceptance."""
    from .runtime import capabilities as report
    return report()
