#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Review the sole post-release assertion-mode guard hardening.

The executed runner and hardened runner must differ by exactly the one guard
below. With assertions enabled, both guards do nothing; every other AST node
is required to agree. The only executed control invokes the hardened entry
under -O and requires its explicit rejection before creating a work tree.
This does not repeat or reattribute the completed scientific release.
Substantial OpenAI assistance under the user's direction.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile


MESSAGE = 'Python assertions must be enabled'
OLD = b'    assert __debug__\n'
NEW = b"    if not __debug__: raise RuntimeError('Python assertions must be enabled')\n"


def need(value, message):
    if not value:
        raise RuntimeError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def strip_guard(raw, hardened):
    tree = ast.parse(raw.decode('utf-8'))
    mains = [node for node in tree.body
             if isinstance(node, ast.FunctionDef) and node.name == 'main']
    need(len(mains) == 1, 'one top-level main function')
    main = mains[0]
    expected = ast.parse(NEW.decode().strip() if hardened else OLD.decode().strip()).body[0]
    signature = ast.dump(expected, include_attributes=False)
    matches = [i for i, node in enumerate(main.body)
               if ast.dump(node, include_attributes=False) == signature]
    need(len(matches) == 1, 'one exact guard directly in main')
    position = matches[0]
    guard = main.body.pop(position)
    # Removing the guard must leave its scientific successor in place. This
    # binds the -O rejection to the entry before source checks or work creation.
    need(position < len(main.body), 'guard has an unchanged successor')
    following = main.body[position]
    need(isinstance(following, ast.Expr)
         and isinstance(following.value, ast.Call)
         and isinstance(following.value.func, ast.Name)
         and following.value.func.id == 'verify_source'
         and not following.value.args and not following.value.keywords,
         'guard occurs immediately before verify_source()')
    return tree, position, guard.lineno


def review_sources(executed, hardened):
    need(executed.count(OLD) == 1, 'exactly one original guard byte preimage')
    need(hardened == executed.replace(OLD, NEW, 1),
         'hardened runner differs only by the exact one-site guard replacement')
    before, old_index, old_line = strip_guard(executed, False)
    after, new_index, new_line = strip_guard(hardened, True)
    before_ast = ast.dump(before, include_attributes=False)
    after_ast = ast.dump(after, include_attributes=False)
    need(old_index == new_index and old_line == new_line,
         'unchanged position of the entry guard')
    need(before_ast == after_ast, 'all remaining source AST nodes agree exactly')
    # Both modes must remain syntactically valid; no scientific code executes.
    for raw in (executed, hardened):
        for optimize in (0, 1):
            compile(raw, '<reviewed-release-runner>', 'exec', optimize=optimize)
    return dict(
        executed_runner_sha256=sha(executed), hardened_runner_sha256=sha(hardened),
        exact_replacement=dict(old=OLD.decode(), new=NEW.decode(), occurrences=1),
        guard_line=old_line, guard_main_statement_index=old_index,
        remaining_ast_sha256=sha(before_ast.encode('utf-8')),
        remaining_assertions=sum(isinstance(node, ast.Assert) for node in ast.walk(before)),
        remaining_ast_identical=True,
        normal_mode_reason='With __debug__ True, the original assertion succeeds and the replacement conditional body is skipped. Every remaining AST node and its order are identical.',
        compilation_modes_checked=[0, 1])


def optimized_entry_control(hardened):
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1')
    environment.pop('PYTHONOPTIMIZE', None)
    with tempfile.TemporaryDirectory(prefix='receiver-runner-guard-') as name:
        work = Path(name) / 'must-not-be-created'
        need(not work.exists(), 'fresh negative-control work path')
        result = subprocess.run(
            [sys.executable, '-O', '-B', str(hardened), '--work', str(work)],
            cwd=hardened.parent, env=environment, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)
        output = result.stdout.decode('utf-8', errors='replace')
        need(result.returncode == 1, 'optimized entry must report the explicit RuntimeError')
        need(output.rstrip().endswith('RuntimeError: ' + MESSAGE),
             'optimized entry failed for a reason other than the intended guard')
        need(not work.exists(), 'optimized entry created its forbidden work directory')
        return dict(
            optimization_flag='-O', exit_code=result.returncode,
            exact_terminal_error='RuntimeError: ' + MESSAGE,
            work_directory_created=False, output_sha256=sha(result.stdout),
            scientific_release_executed=False)


def main():
    need(__debug__, 'Run this review with Python assertions enabled')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--executed', type=Path, required=True)
    parser.add_argument('--hardened', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    executed, hardened = args.executed.resolve(), args.hardened.resolve()
    need(executed.is_file() and hardened.is_file(), 'both runner sources are required')
    need(not args.out.exists(), 'fresh review receipt path')
    comparison = review_sources(executed.read_bytes(), hardened.read_bytes())
    control = optimized_entry_control(hardened)
    result = dict(
        status='PASS_RUNNER_ASSERTION_GUARD_EQUIVALENCE',
        reviewer_sha256=sha(Path(__file__).read_bytes()),
        source_comparison=comparison, optimized_entry_control=control,
        python=sys.version, platform=platform.platform(),
        full_release_repeated=False,
        scope='The completed nonoptimized release remains attributed to the retained executed runner. Its hardened successor differs only by the explicit assertion-mode rejection guard. No native, owner, price, or ordinary/outer gate is rerun or changed by this review.')
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print(result['status'])


if __name__ == '__main__':
    main()
