#!/usr/bin/env python3
"""Bounded independent equality-cut audit; Hiroki KUMAZAKI / OpenAI Codex.

Apache-2.0. Reads pinned proof inputs, imports only this package's separately
written checkers, and compares a deterministic receipt. No Git or network.
"""
import hashlib
import importlib.util
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(name):
    # Compile source directly so a stale sibling bytecode cache cannot replace
    # the checks even in a direct standalone replay outside the generic runner.
    path = PACKAGE / (name + '.py')
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


def calculate():
    sources = json.loads((PACKAGE / 'SOURCES.json').read_text())
    inputs = [row for row in sources['files'] if row['usage'] == 'input']
    require(len(inputs) == 3, 'expected proof, README and license inputs')
    for row in inputs:
        digest = hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest()
        require(digest == row['sha256'], 'source digest mismatch: ' + row['path'])
    return {
        'status': 'PASS_NATIVE_EQUALITY_INDEPENDENT_AUDIT',
        'reviewed_source_head': '97db3fb45cd93a350e300781d75440d14e6a1f73',
        'authenticated_inputs': len(inputs),
        'stabilizers': load('stabilizers').run(),
        'contracts': load('contracts').run(),
        'scope': 'PR5588 PROOF.md sections3–5; written all-size proof plus finite exact controls',
        'source_verifier_imported': False,
        'new_kappa_or_supplier_admission': False,
    }


def main():
    result = calculate()
    expected = json.loads((PACKAGE / 'RESULT.json').read_text())
    require(result == expected, 'computed evidence differs from committed RESULT.json')
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
