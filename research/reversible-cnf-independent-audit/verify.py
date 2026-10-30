#!/usr/bin/env python3
"""Source-bound independent reversible CNF audit. Apache-2.0.

Hiroki KUMAZAKI with substantial OpenAI Codex assistance.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
SOURCE = ROOT / 'research/native-tensor-cutoff'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def module_from_source(name, path, text=None):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    exec(compile(path.read_bytes() if text is None else text, str(path), 'exec'), module.__dict__)
    return module


def compiler(text=None):
    # Execute the actual compiler with its actual exact.py dependency, without
    # changing either source. Restore the import namespace immediately after.
    old = sys.modules.get('exact')
    try:
        sys.modules['exact'] = module_from_source('exact', SOURCE / 'exact.py')
        return module_from_source('reviewed_cnf', SOURCE / 'reversible_cnf.py', text)
    finally:
        if old is None:
            sys.modules.pop('exact', None)
        else:
            sys.modules['exact'] = old


def mutated_source(old, new):
    text = (SOURCE / 'reversible_cnf.py').read_text()
    need(text.count(old) == 1, 'unique mutation anchor required')
    return compiler(text.replace(old, new))


def calculate():
    pins = json.loads((PACKAGE / 'SOURCES.json').read_text())
    inputs = [row for row in pins['files'] if row['usage'] == 'input']
    need(len(inputs) == 6, 'exact source-input closure')
    for row in inputs:
        need(hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'],
             'source digest mismatch: ' + row['path'])
    literal = module_from_source('independent_literal', PACKAGE / 'literal.py')
    audit = module_from_source('independent_audit', PACKAGE / 'audit.py')
    return {'status':'PASS_REVERSIBLE_CNF_INDEPENDENT_AUDIT',
            'reviewed_source_head':'18354f41de4dc7bfda4692e814cf1d91a6d619ef',
            'authenticated_inputs':len(inputs),
            'checks':audit.run(compiler(), literal, mutated_source),
            'source_compiler_executed':True, 'source_evaluator_or_verifier_used':False,
            'new_hardness_theorem_or_kappa':False}


def main():
    result = calculate()
    expected = json.loads((PACKAGE / 'RESULT.json').read_text())
    need(result == expected, 'computed receipt differs from committed RESULT.json')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
