"""Small JSON-safe records; operation state and engineering judgment are separate."""
from dataclasses import dataclass, field, asdict
import hashlib
import json
import math
from pathlib import Path

def file_hash(path):
    h = hashlib.sha256()
    with open(path, 'rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Atomic replacement of task-owned evidence only.
    tmp = path.with_name(path.name + '.tmp')
    tmp.write_text(json.dumps(value, indent=2, allow_nan=False), encoding='utf8')
    tmp.replace(path)

def positive(value, label, allow_zero=False):
    if not math.isfinite(value) or (value < 0 if allow_zero else value <= 0):
        raise ValueError(f'{label} must be finite and {"nonnegative" if allow_zero else "positive"}')

@dataclass
class Evidence:
    method: str
    operands: list
    frame: str
    units: str
    tolerance: dict
    value: object = None
    coverage: str = 'CHECKED_OPERANDS_ONLY'
    status: str = 'UNVERIFIED'
    requirement: str | None = None
    diagnostics: list = field(default_factory=list)
    unchecked: list = field(default_factory=list)

    def record(self):
        if self.status not in ('MEASURED', 'PASS', 'FAIL', 'UNVERIFIED'):
            raise ValueError('Unknown evidence status')
        if self.status in ('PASS', 'FAIL') and not self.requirement:
            raise ValueError('Engineering judgment requires a declared requirement')
        value = asdict(self)
        json.dumps(value, allow_nan=False)
        return value

def aggregate(required, expected_ids):
    """Missing, duplicated, or undeclared predicates prevent complete PASS."""
    ids = [r.requirement for r in required]
    if len(ids) != len(set(ids)) or set(ids) != set(expected_ids):
        return 'UNVERIFIED'
    if any(r.status == 'FAIL' for r in required):
        return 'FAIL'
    return 'PASS' if all(r.status == 'PASS' for r in required) else 'UNVERIFIED'
