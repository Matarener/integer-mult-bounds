#!/usr/bin/env python3
"""Free helper endpoints of PR5561 under the audited P104 endpoint contract.  Apache-2.0.

Prepared for Matarener with Claude (Anthropic), via Claude Code.
The scientific checker is Chris R / Clear1nsight's byte-pinned PR5550 caller and
target-binding audit (research/p104-caller-independent-audit, substantial OpenAI
Codex assistance).  This file changes only four literal input lines of a temporary
copy and never edits the canonical capsule.

Steps:
  1. authenticate every input by SHA-256 (canonical PR5550 capsule, PR5545 word,
     package-local PR5561 words and invoice extract);
  2. census of nonzero helper starts and below-FULL helper finals in the PR5545 word;
  3. positive control: the patched checker on the PR5545 word with the PR5545 invoice
     reproduces PR5550's complete frozen scientific output byte for byte;
  4. the patched checker on both PR5561 words (headline and starts-only);
  5. negative controls: a changed helper endpoint and a changed invoice are rejected.
"""
from collections import Counter
from pathlib import Path
import gzip
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
AUDIT = ROOT/'research/p104-caller-independent-audit'
CAPSULE = AUDIT/'capsule'
CHECK = 'outputs/p104-caller-route-audit-v2-20261025/check.py'
PR5545_WORD = ROOT/'research/p104-full-frame-contact/WORD.json.gz'
EXPECTED_5550 = 'b51a7d19c10faea7d569a48e9536db8ba1e7418f8dd8dfb25646cc87cc9c4009'

REPLACEMENTS = (
    ("    word = read(PRIOR/'sources/contact/WORD.json.gz')\n",
     "    word = read(Path(os.environ['P104_WORD']))\n"
     "    FREE = json.loads(Path(os.environ['P104_INVOICE']).read_text())\n"),
    ("helper_profile == Counter({4:51, 5:36, 7:24, 8:122, 9:294})",
     "helper_profile == Counter({int(k):v for k,v in json.loads(os.environ['P104_PROFILE']).items()})"),
    ("    costs = source['complete_cost']\n",
     "    costs = FREE\n"),
    ("nr['local_routes'] == 5334000 and sum(paid_local.values()) == 3624",
     "nr['local_routes'] == (sum(paid_local.values())+2*527+208+4*104+4*8)*1000 and sum(paid_local.values()) == int(os.environ['P104_MOVES'])"),
)

PARTS = {
    'headline': {'word': 'pr5561-WORD.json.gz', 'moves': 3454, 'paid': 66852, 'pairs': 32,
                 'profile': {4: 83, 5: 5, 8: 14, 9: 425}},
    'starts_only': {'word': 'pr5561-WORD-STARTS-ONLY.json.gz', 'moves': 3483, 'paid': 67374, 'pairs': 35,
                    'profile': {4: 83, 5: 5, 7: 1, 8: 34, 9: 404}},
}


def need(ok, why):
    if not ok:
        raise ValueError(why)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith('.gz') else raw)


def authenticate():
    pins = json.loads((HERE/'SOURCES.json').read_text())
    for row in pins['files']:
        need(sha(ROOT/row['path']) == row['sha256'], 'source pin '+row['path'])
    for name, digest in pins['package_inputs'].items():
        need(sha(HERE/'inputs'/name) == digest, 'package input '+name)
    inventory = json.loads((AUDIT/'CAPSULE-INVENTORY.json').read_text())['files']
    for name, digest in inventory.items():
        if name.startswith('capsule/'):
            need(sha(AUDIT/name) == digest, 'PR5550 capsule byte '+name)


def endpoint_census(word):
    frames = word['frames']
    main = set(word['live']) | {r+112 for r in word['live']}
    helpers = [r for r in range(word['public']) if r not in main]
    starts = Counter(len(frames[word['initial'][r]]) for r in helpers)
    finals = Counter(len(frames[word['final'][r]]) for r in helpers)
    pairs = {(word['initial'][r], word['final'][r]) for r in helpers}
    return {'helpers': len(helpers), 'start_dims': dict(sorted(starts.items())), 'final_dims': dict(sorted(finals.items())),
            'nonzero_starts': sum(n for d, n in starts.items() if d), 'below_full_finals': sum(n for d, n in finals.items() if d < 9),
            'distinct_endpoint_pairs': len(pairs)}


def run(work, word_path, invoice, profile, moves):
    inv = work/'invoice.json'
    inv.write_text(json.dumps(invoice))
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', P104_WORD=str(word_path), P104_INVOICE=str(inv),
               P104_PROFILE=json.dumps(profile), P104_MOVES=str(moves))
    env.pop('P104_TRACE_FILE', None)
    command = [sys.executable, '-X', 'pycache_prefix='+str(work/'bytecode')] + (['-O'] if sys.flags.optimize else []) + \
              ['-B', str(work/'capsule'/'outputs/p104-caller-route-audit-v2-20261025/check_free.py')]
    done = subprocess.run(command, cwd=work/'capsule', env=env, capture_output=True, timeout=300)
    return done.returncode, done.stdout, done.stderr.decode(errors='replace')


def main():
    authenticate()
    print('PASS authenticated canonical PR5550 capsule, PR5545 word and PR5561 inputs', flush=True)
    base = read(PR5545_WORD)
    census_5545 = endpoint_census(base)
    need((census_5545['nonzero_starts'], census_5545['below_full_finals'], census_5545['distinct_endpoint_pairs']) == (192, 65, 40),
         'PR5545 already has 192 nonzero helper starts, 65 below-FULL finals and 40 endpoint pairs')
    print('PASS PR5545 endpoint census', census_5545, flush=True)
    invoice = json.loads((HERE/'inputs/INVOICE.json').read_text())
    results = {'pr5545_census': census_5545}
    with tempfile.TemporaryDirectory(prefix='p104-free-endpoint-contract-') as tmp:
        work = Path(tmp)
        shutil.copytree(CAPSULE, work/'capsule')
        text = (work/'capsule'/CHECK).read_text()
        need(hashlib.sha256(text.encode()).hexdigest() == sha(CAPSULE/CHECK), 'pinned PR5550 checker')
        for old, new in REPLACEMENTS:
            need(text.count(old) == 1, 'literal present once: '+old.strip()[:60])
            text = text.replace(old, new)
        (work/'capsule'/CHECK).with_name('check_free.py').write_text(text)
        # Positive control: the PR5545 word and invoice give PR5550's frozen output byte for byte.
        source = read(CAPSULE/'outputs/p104-contact-reassessment-20261025/sources/contact/RESULT.json')
        code, out, err = run(work, CAPSULE/'outputs/p104-contact-reassessment-20261025/sources/contact/WORD.json.gz',
                             source['complete_cost'], {4: 51, 5: 36, 7: 24, 8: 122, 9: 294}, 3624)
        need(code == 0 and not err, 'positive control failed: '+err[-2000:])
        need(hashlib.sha256(out).hexdigest() == EXPECTED_5550 == hashlib.sha256(gzip.decompress((AUDIT/'expected/caller.json.gz').read_bytes())).hexdigest(),
             'patched checker reproduces the complete PR5550 output on PR5545')
        print('PASS positive control: patched checker reproduces PR5550 output', EXPECTED_5550, flush=True)
        for part, spec in PARTS.items():
            word_path = HERE/'inputs'/spec['word']
            word = read(word_path)
            census = endpoint_census(word)
            need(census['distinct_endpoint_pairs'] == spec['pairs'], part+' endpoint pairs')
            code, out, err = run(work, word_path, invoice['parts'][part], spec['profile'], spec['moves'])
            need(code == 0 and not err, part+' checker failed: '+err[-2000:])
            res = json.loads(out)
            need(res['status'] == 'PASS_SCOPED_CALLER_AND_TARGET_BINDING' and res['kappa_claim'] is None, part+' scoped status')
            need(sum(res['paid'].values()) == spec['paid'] and sum(res['targets'].values()) == 12814, part+' invoice')
            need(len(res['helper_normalizers']) == 527 and res['native_checks']['fresh_helpers'] == 9486, part+' helper coverage')
            need(len(res['controls']) == 10, part+' all ten PR5550 controls reject')
            o = res['ordinary']
            need(o['abstract_address_phase_scalar_pass_upper'] <= o['retained_raw_scalar_upper'], part+' ordinary allowance')
            results[part] = {'census': census, 'paid_jobs': spec['paid'], 'productive_fields': 12814,
                             'exact_native_checks': res['native_checks']['distinct_signed_Pauli_and_independent_phase_anchors'],
                             'ordinary_passes': o['abstract_address_phase_scalar_pass_upper'], 'ordinary_allowance': o['retained_raw_scalar_upper'],
                             'certified_kappa_of_source': invoice['parts'][part]['kappa'], 'output_sha256': hashlib.sha256(out).hexdigest()}
            print('PASS', part, results[part], flush=True)
        # Negative controls on the headline word.
        word = read(HERE/'inputs/pr5561-WORD.json.gz')
        main_regs = set(word['live']) | {r+112 for r in word['live']}
        h = next(r for r in range(735) if r not in main_regs and len(word['frames'][word['initial'][r]]))
        zero = next(i for i, f in enumerate(word['frames']) if not f)
        bad = json.loads(json.dumps(word))
        bad['initial'][h] = zero
        bad_path = work/'bad-endpoint.json.gz'
        bad_path.write_bytes(gzip.compress(json.dumps(bad).encode(), mtime=0))
        code, _, err = run(work, bad_path, invoice['parts']['headline'], PARTS['headline']['profile'], 3454)
        need(code != 0 and 'ValueError' in err, 'changed helper endpoint rejected')
        wrong = json.loads(json.dumps(invoice['parts']['headline']))
        wrong['paid']['1'] += 1
        code, _, err = run(work, HERE/'inputs/pr5561-WORD.json.gz', wrong, PARTS['headline']['profile'], 3454)
        need(code != 0 and 'complete unchanged paid/target invoice' in err, 'changed invoice rejected')
        results['negative_controls'] = {'changed_helper_endpoint': 'rejected', 'changed_invoice': 'rejected'}
        print('PASS negative controls', results['negative_controls'], flush=True)
    expected = json.loads((HERE/'RESULT.json').read_text())
    if '--write' in sys.argv:
        (HERE/'RESULT.json').write_text(json.dumps(results, indent=1, sort_keys=True)+'\n')
    else:
        need(json.loads(json.dumps(results)) == expected, 'complete result equals RESULT.json')
    print('PASS_P104_FREE_ENDPOINT_CONTRACT_AUDIT')


if __name__ == '__main__':
    main()
