#!/usr/bin/env python3
"""Fresh bounded owner replay and independent exact invoice/dual review of PR3815.

The upstream changed-clock construction is credited to Erwan Secousses /
ChaloupeMusic; PR3802 reached the same value first. This review claims neither
a new value nor authorship of their construction. The parent task separately
runs complete admission. Apache-2.0; substantial OpenAI Codex assistance.
"""
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from packing_certificate import certify

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SOURCE = HERE.parent/'sources/PR3815'
PACKAGE = SOURCE/'research/staged544-clock-ceiling'
SUPPLIER = SOURCE/'research/staged544-producer-return'
FROZEN = REPO/'research/kappa-global-continuation/inputs/kappa-consumer-followup/artifact/live-source/research/staged544-producer-return'
COMMIT = '77ffbf287b6ca198b4a31e3835db3bae60718b93'


def rank(rows):
    pivots = {}
    for row in rows:
        while row:
            bit = row.bit_length()
            if bit in pivots:
                row ^= pivots[bit]
            else:
                pivots[bit] = row
                break
    return len(pivots)


def main():
    path = REPO/'research/kappa-global-continuation/invoice-analysis/invoice.py'
    spec = importlib.util.spec_from_file_location('pr3815_independent_invoice', path)
    I = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(I)
    frozen_receipt = I.read(path.parent/'evidence/RESULT.json')
    I.need(I.digest(path) == frozen_receipt['script_sha256'], 'frozen invoice interface')
    I.need(I.digest(I.ENGINE_PATH) == frozen_receipt['arithmetic_engine_sha256'], 'frozen outward arithmetic')
    same = ['owner_audit.py', 'PROOF.md', 'inputs/ORDER.json', 'inputs/DISPATCH.json',
            'inputs/NATIVE-base.json.gz', 'inputs/NATIVE-extra.json.gz',
            'inputs/PLAN.json.gz', 'inputs/TEMPLATE.json.gz', 'inputs/PROFILE.json']
    for name in same:
        I.need((FROZEN/name).read_bytes() == (SUPPLIER/name).read_bytes(), 'attached baseline matches source: '+name)
    manifest = I.read(PACKAGE/'SOURCES.json')
    source_checks = {}
    for entry in manifest['files']:
        if entry['usage'] != 'input':
            continue
        p = SOURCE/entry['path']
        I.need(I.digest(p) == entry['sha256'], 'upstream exact input hash: '+entry['path'])
        source_checks[entry['path']] = entry['sha256']
    # The source verifier includes the byte-identical owner audit, 1,321,920
    # allocation rows, helper/data nonaliasing and all documented controls.
    with tempfile.TemporaryDirectory(prefix='pr3815-review-', dir=HERE) as temp:
        env = dict(os.environ, TMPDIR=temp)
        run = subprocess.run([sys.executable, '-B', str(PACKAGE/'verify.py')],
                             capture_output=True, text=True, env=env)
    I.need(run.returncode == 0, 'fresh upstream owner/clock/price replay: '+run.stderr[-1200:])
    upstream = json.loads(run.stdout)
    I.need(upstream['status'] == 'PASS_STAGED544_CHANGED_CLOCK_CEILING_OWNERS_AND_PRICE', 'fresh upstream status')
    template = I.read(SUPPLIER/'inputs/TEMPLATE.json.gz')
    bins = Counter()
    for child in template['idle_children']:
        bins[child['rank']] += 1
    I.need(bins == {8: 672, 16: 448, 32: 448, 48: 448}, 'actual source idle bin inventory')
    widths, local = None, None
    for tag in ('base', 'extra'):
        word = I.read(SUPPLIER/f'inputs/NATIVE-{tag}.json.gz')
        got = [rank(word['frames'][word['final'][r]])-rank(word['frames'][word['start'][r]])
               for r in range(224, 632)]
        I.need(widths is None or widths == got, 'both providers have identical ordered widths')
        widths = got
        profile = {int(r): n for r, n in word['local_profile'].items()}
        I.need(local is None or local == profile, 'both native paid profiles agree')
        local = profile
    I.need(local == I.LOCAL, 'attached native local profile')
    supply = Counter(widths)
    I.need(supply == {4: 26, 5: 2, 6: 18, 7: 53, 8: 96, 9: 213}, 'actual native width inventory')
    profile = {int(r): n for r, n in upstream['profile'].items()}
    I.need(profile == {int(r): n for r, n in I.read(PACKAGE/'inputs/PROFILE.json').items()}, 'audited complete profile')
    independent_root = I.root(profile, 73, 322560)
    I.need(F(independent_root['rational'][0]) == I.TARGET, 'independent invoice root equals target')
    I.need(sum(r*n for r, n in profile.items()) == 65088*360, 'unchanged complete raw deficit')
    # A basis nomination is read from the credited source. Every inequality is
    # separately rebuilt with our frozen normalized-cost enclosures.
    source_cert = I.module(PACKAGE/'ceiling_certificate.py', 'pr3815_basis_nomination')
    common = dict(dimension=73, productive=896, calls=9, local=local,
                  bins=bins, supply=supply, basis=source_cert.BASIS)
    upper = F(independent_root['rational'][1])
    ceiling = certify(I, endpoint=upper, **common)
    I.need(ceiling['patterns_checked'] == 2551 and ceiling['strictly_excludes_endpoint'],
           'independent normalized-cost dual over all patterns')
    low_control = certify(I, endpoint=I.TARGET, **common)
    I.need(not low_control['strictly_excludes_endpoint'], 'independent root-lower control')
    bad_control = certify(I, endpoint=upper, perturb_width9=F(1, 10**30), **common)
    I.need(not bad_control['dual_feasible'], 'independent perturbed-dual control')
    old_root = I.root(I.BASE, 73, 322560)
    gain = F(independent_root['rational'][0])-F(old_root['rational'][0])
    I.need(gain > 0 and gain == F(upstream['gain_lower_over_pr3734']), 'strict attached-baseline gain')
    fee = F(1, 10**46)+F(1, 10**70)
    headline = I.TARGET-fee
    I.need(headline == F(upstream['recorded_release_kappa']), 'source outer headline conversion')
    files = [Path(__file__), Path(__file__).with_name('packing_certificate.py'), path, I.ENGINE_PATH,
             PACKAGE/'verify.py', PACKAGE/'clock.py', PACKAGE/'ceiling_certificate.py',
             PACKAGE/'SOURCES.json', PACKAGE/'PRICE.json', PACKAGE/'inputs/ORDER.json',
             PACKAGE/'inputs/FILL.json.gz', PACKAGE/'inputs/PROFILE.json', PACKAGE/'evidence/RELEASE.json']
    result = {
        'status': 'PASS_FRESH_PR3815_OWNERS_AND_INDEPENDENT_EXACT_PRICE_DUAL',
        'source_commit': COMMIT,
        'source_url': 'https://github.com/CrocSwap/integer-mult-bounds/pull/3815',
        'input_sha256': {str(p.relative_to(REPO)): I.digest(p) for p in files},
        'byte_identical_to_attached_baseline': same,
        'upstream_input_manifest_checked': source_checks,
        'fresh_upstream_verifier': upstream,
        'independent_root': independent_root,
        'independent_clock_independent_ceiling': ceiling,
        'independent_controls': ['root_lower_not_excluded', 'perturbed_width9_dual_rejected'],
        'attached_baseline_root': old_root,
        'strict_root_lower_gain': str(gain), 'strict_root_lower_gain_decimal': I.decimal(gain),
        'conditional_kappa': str(headline), 'conditional_kappa_decimal': I.decimal(headline, 90),
        'retained_bit_cap': str(I.BIT_ROOT), 'below_retained_bit_cap': headline < I.BIT_ROOT,
        'fresh_complete_admission_rerun_by_this_script': False,
        'scope': ('Fresh bounded upstream owner verification plus separately implemented exact '
                  'normalized invoice/dual checks. Complete admission is a parent-task gate. '
                  'The global packing ceiling applies to this supplier, idle template and one '
                  'paid remainder per bin, under any clock or replica count. All inherited '
                  'all-size compiler, physical realization, precision/recovery, analytic '
                  'and BIT assumptions remain. This adoption improves the attached baseline; '
                  'the value was already attained upstream by PR3802 and PR3815.')
    }
    (HERE/'PR3815-INDEPENDENT-REVIEW.json').write_text(json.dumps(result, indent=2)+'\n')
    print(result['status'])
    print('root', independent_root['decimal'], 'gain', I.decimal(gain), 'patterns', ceiling['patterns_checked'])


if __name__ == '__main__':
    main()
