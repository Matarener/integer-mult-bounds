#!/usr/bin/env python3
"""Run the exact witness normally and optimized; preserve reproducible receipts."""
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shlex
import subprocess
import sys


def need(condition, label):
    if not condition:
        raise RuntimeError(label)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    root = Path(__file__).resolve().parent
    witness = root/'witness.py'
    source_hash = sha(witness)
    proof_hash = sha(root/'PROOF.md')
    tree = ast.parse(witness.read_text())
    need(not any(isinstance(node, ast.Assert) for node in ast.walk(tree)),
         'witness contains an optimization-sensitive assert')
    results = []
    outputs = []
    for mode, flags in [('normal', []), ('optimized', ['-O'])]:
        command = [sys.executable, *flags, str(witness)]
        result = subprocess.run(command, capture_output=True, text=True, cwd=root)
        output_path = root/f'VALIDATION-{mode}.json'
        output_path.write_text(result.stdout)
        need(result.returncode == 0, f'{mode} witness failed: {result.stderr}')
        payload = json.loads(result.stdout)
        need(payload['status'] == 'PASS_EXACT_NATIVE_CONSTITUENTS_AND_NONCOMMUTATIVE_RESOLVENT',
             f'{mode} status')
        need(payload['source_sha256'] == source_hash, f'{mode} source hash')
        need(payload['proof_sha256'] == proof_hash, f'{mode} proof hash')
        outputs.append(result.stdout)
        # A false explicit check must terminate even when Python optimization is enabled.
        probe_code = ('import runpy,sys; '
                      'runpy.run_path(sys.argv[1])["need"](False,"forced validation defect")')
        probe_command = [sys.executable, *flags, '-c', probe_code, str(witness)]
        probe = subprocess.run(probe_command, capture_output=True, text=True, cwd=root)
        probe_path = root/f'VALIDATION-{mode}-forced-defect.txt'
        probe_path.write_text(probe.stderr)
        need(probe.returncode != 0 and 'RuntimeError: forced validation defect' in probe.stderr,
             f'{mode} false explicit check did not terminate')
        results.append({
            'mode': mode,
            'command': shlex.join(command),
            'exit_code': result.returncode,
            'output_file': output_path.name,
            'output_sha256': sha(output_path),
            'forced_defect_command': shlex.join(probe_command),
            'forced_defect_exit_code': probe.returncode,
            'forced_defect_file': probe_path.name,
            'forced_defect_sha256': sha(probe_path),
        })
    need(outputs[0] == outputs[1], 'normal and optimized outputs differ')
    need(sha(witness) == source_hash, 'source changed during validation')
    receipt = {
        'status': 'PASS_NORMAL_AND_OPTIMIZED_WITH_EXPLICIT_FAILURE_CHECKS',
        'utc': datetime.now(timezone.utc).isoformat(),
        'working_directory': str(root),
        'witness_source_sha256': source_hash,
        'proof_sha256': proof_hash,
        'validation_source_sha256': sha(Path(__file__).resolve()),
        'normal_and_optimized_outputs_identical': True,
        'witness_has_no_ast_assert_nodes': True,
        'runs': results,
    }
    (root/'VALIDATION.json').write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
