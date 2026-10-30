from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys

B = Path(__file__).resolve().parent
request = json.loads((B/'REQUEST.json').read_text())
for name, key in [('check.py', 'code_sha256'), ('CONTRACT.md', 'contract_sha256'),
                  ('INPUTS.json', 'inputs_sha256'), ('run_pair.py', 'runner_sha256'), ('inventory.py', 'inventory_code_sha256'),
                  ('INVENTORY.json', 'inventory_sha256'), ('NOMINATION.json', 'nomination_sha256')]:
    if hashlib.sha256((B/name).read_bytes()).hexdigest() != request[key]:
        raise ValueError('frozen request mismatch: '+name)
for mode, flags in [('normal', []), ('optimized', ['-O'])]:
    trace = B/('TRACE-'+mode+'.jsonl')
    if trace.exists():
        raise ValueError('preserve old trace; do not repeat frozen run')
    env = dict(os.environ, P104_NATIVE_TRACE=str(trace))
    with (B/('RESULT-'+mode+'.json')).open('xb') as out, (B/('STDERR-'+mode+'.txt')).open('xb') as err:
        result = subprocess.run([sys.executable, *flags, '-B', str(B/'check.py')],
                                stdout=out, stderr=err, env=env, timeout=70)
    if result.returncode or (B/('STDERR-'+mode+'.txt')).stat().st_size:
        raise ValueError('mode failed: '+mode+'; code '+str(result.returncode)+'; see retained stderr/trace')
    with (B/('RESULT-'+mode+'.json')).open() as stream:
        parsed = json.load(stream)
    if parsed['status'] != 'PASS_SCOPED_HIGH_RANK_AND_PRIVATE_NATIVE_MAPS':
        raise ValueError('missing scientific marker')
    del parsed
sha = hashlib.sha256()
with (B/'RESULT-normal.json').open('rb') as left, (B/'RESULT-optimized.json').open('rb') as right:
    while True:
        a, b = left.read(65536), right.read(65536)
        if a != b:
            raise ValueError('complete scientific normal/optimized bytes differ')
        if not a:
            break
        sha.update(a)
receipt = {'schema':'exact-pair-equality/v2', 'complete_output_equal':True,
           'scientific_fields_excluded':0, 'modes':2,
           'operational_traces_separate':True, 'result_sha256':sha.hexdigest(),
           'request_sha256':hashlib.sha256((B/'REQUEST.json').read_bytes()).hexdigest()}
(B/'PAIR-RECEIPT.json').write_text(json.dumps(receipt, indent=2)+'\n')
print(json.dumps(receipt))
