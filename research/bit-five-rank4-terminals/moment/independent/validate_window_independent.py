#!/usr/bin/env python3
"""Verify preserved independent window evidence without updating it.

Default output is stdout only. Temporary relocation/fault-control copies
are made inside this directory and removed. Source and receipts stay intact.
"""
import ast
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(path, optimized=False, args=()):
    command = [sys.executable, '-B']+(['-O'] if optimized else [])+[str(path),*args]
    return subprocess.run(command, capture_output=True, text=True)


def main():
    source = HERE/'check_window_independent.py'
    context = HERE/'source-context/global_k.py'
    receipt = HERE/'WINDOW-INDEPENDENT-RESULT.json'
    before = {p.name:sha(p) for p in (source, context, receipt)}
    expected = json.loads(receipt.read_text())
    need(not any(isinstance(node, ast.Assert) for node in ast.walk(ast.parse(source.read_text()))),
         'no assert-dependent checks')
    for optimized in (False, True):
        got = run(source, optimized)
        need(got.returncode == 0 and json.loads(got.stdout) == expected, 'preserved exact receipt')
        bad = run(source, optimized, ['--force-failure'])
        need(bad.returncode != 0 and 'forced explicit window failure' in bad.stderr,
             'explicit failure remains active')
    with tempfile.TemporaryDirectory(prefix='window-relocation-', dir=HERE) as tmp:
        relocated = Path(tmp)
        (relocated/'source-context').mkdir()
        shutil.copyfile(source, relocated/source.name)
        shutil.copyfile(context, relocated/'source-context/global_k.py')
        for optimized in (False, True):
            got = run(relocated/source.name, optimized)
            need(got.returncode == 0 and json.loads(got.stdout) == expected,
                 'two-file relocated receipt')
        # Only the temporary context is mutated; the original pin must reject it.
        with (relocated/'source-context/global_k.py').open('ab') as stream:
            stream.write(b'\n# deliberate source pin corruption\n')
        for optimized in (False, True):
            bad = run(relocated/source.name, optimized)
            need(bad.returncode != 0 and 'frozen source SHA256' in bad.stderr,
                 'corrupt relocated source rejected')
    need(before == {p.name:sha(p) for p in (source, context, receipt)}, 'original files unchanged')
    out = {'status':'PASS_PORTABLE_INDEPENDENT_WINDOW_REVIEW',
           'normal_optimized_identical':True, 'original_receipt_preserved':True,
           'relocated_two_file_check_passed':True,
           'explicit_failure_rejected_both_modes':True, 'corrupt_source_rejected_both_modes':True,
           'source_execution':False, 'absolute_run_or_git_runtime_dependency':False,
           'persistent_writes':False, 'inputs':before,
           'checker_evidence':'finite exact rational identity/sign checks; all-parameter proof in WINDOW-REVIEW.md'}
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
