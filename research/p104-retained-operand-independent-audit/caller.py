#!/usr/bin/env python3
"""Physical caller binding of the PR6144 and PR6167 words with the maintainers' independent caller checker.  Apache-2.0.

Runs the generalized caller route checker of the PR6030 admission review
(docs/research/pr-intake-evidence/pr6030-audit, Douglas Colkitt with OpenAI Codex, adapted from the reviewed
PR5550/PR5599 checker) unchanged: its prepare.py copies the pinned sources into a fresh temporary directory, the
original positive control must reproduce its frozen output digest, and then the checker runs on the PR6144 and
PR6167 words through its P104_WORD / P104_RESULT inputs.  Nothing from the PR6144 or PR6167 packages is executed.
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import json, os, subprocess, sys, tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REVIEW = ROOT/'docs/research/pr-intake-evidence/pr6030-audit'
CHECK = 'source/research/p104-caller-independent-audit/capsule/outputs/p104-caller-route-audit-v2-20261025/check.py'
CONTROL_SHA256 = 'b51a7d19c10faea7d569a48e9536db8ba1e7418f8dd8dfb25646cc87cc9c4009'  # PR6030-audit VALIDATION.json
WORDS = {'6144': ROOT/'research/p104-root-relay-descent-2', '6167': ROOT/'research/p104-retained-operand-descent'}


def need(ok, why):
    if not ok:
        raise ValueError(why)


def run(argv, cwd, env=None):
    clean = {k: v for k, v in os.environ.items() if not k.startswith('P104_')}
    done = subprocess.run([sys.executable, '-I', '-B']+argv, cwd=cwd, env=clean | (env or {}),
                          capture_output=True, timeout=550)
    need(done.returncode == 0, 'caller run failed: %s' % done.stderr.decode()[-2000:])
    return done.stdout


def main():
    out = {}
    with tempfile.TemporaryDirectory(prefix='p104-6167-caller-') as tmp:
        work = Path(tmp)/'work'
        run([str(REVIEW/'prepare.py'), str(work)], ROOT)
        control = run(['run_caller.py', 'control'], work)
        need(sha256(control).hexdigest() == CONTROL_SHA256, 'positive control reproduces its frozen digest')
        print('PASS caller positive control', CONTROL_SHA256[:16], flush=True)
        out['positive_control_sha256'] = CONTROL_SHA256
        for k, P in WORDS.items():
            raw = run([CHECK], work, {'P104_WORD': str(P/'WORD.json.gz'), 'P104_RESULT': str(P/'RESULT.json')})
            r = json.loads(raw)
            cost = json.loads((P/'RESULT.json').read_text())['complete_cost']
            need(r['status'] == 'PASS_SCOPED_CALLER_AND_TARGET_BINDING', 'caller status '+k)
            need(Counter({int(a): b for a, b in r['paid'].items()}) == Counter({int(a): b for a, b in cost['paid'].items()}) and
                 Counter({int(a): b for a, b in r['targets'].items()}) == Counter({int(a): b for a, b in cost['targets'].items()}),
                 'caller invoice equals complete_cost '+k)
            out[k] = {'status': r['status'], 'output_sha256': sha256(raw).hexdigest(), 'native_checks': r['native_checks'],
                      'paid_calls': sum(r['paid'].values()), 'productive_fields': sum(r['targets'].values()),
                      'controls_rejected': sorted(r['controls']),
                      'ordinary_pass_upper': r['ordinary']['abstract_address_phase_scalar_pass_upper'],
                      'retained_raw_scalar_upper': r['ordinary']['retained_raw_scalar_upper']}
            print('PASS caller', k, json.dumps(out[k], sort_keys=True)[:200], flush=True)
    path = HERE/'CALLER.json'
    if '--write' in sys.argv:
        path.write_text(json.dumps(out, indent=1, sort_keys=True)+'\n')
    else:
        need(json.loads(path.read_text()) == out, 'caller result equals CALLER.json')
    print('PASS_P104_6144_6167_CALLER_BINDING')


if __name__ == '__main__':
    main()
