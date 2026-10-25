#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Bind the source-specific proofs and reprice the complete conditional join.

This is finite exact evidence for ADMISSION.md, not an automated scientific
acceptance decision. Prepared for Ross Richardson with OpenAI Codex assistance.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import gzip
import json
from pathlib import Path
import tarfile
import types

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PRIOR = REPO / 'research/complex-pooled-full-admission'
PROFILE = {1:8060040, 2:2310120, 3:751788, 4:327240,
           5:66420, 8:25920, 48:138492}


def need(ok, why):
    if not ok:
        raise ValueError(why)


def load(path):
    return json.loads(path.read_bytes())


def sha(raw):
    return sha256(raw).hexdigest()


def authenticated():
    pins = load(HERE / 'ADMISSION-PINS.json')
    for path, record in pins['files'].items():
        target = REPO / path
        need(not target.is_symlink(), 'ordinary pinned file: ' + path)
        raw = target.read_bytes()
        need(len(raw) == record['bytes'] and sha(raw) == record['sha256'], 'join input pin: ' + path)
    return pins


def complete_profile(native, host):
    need(native['status'] == 'PASS_SOURCE_SPECIFIC_NATIVE_ALL_PARAMETER_ADMISSION',
         'native source-specific certificate')
    need(host['status'] == 'PASS' and host['hosting']['calls'] == 3240,
         'complete source-specific hosting certificate')
    total = Counter({int(r): n for r, n in host['hosting']['residual_profile'].items()})
    counts = host['hosting']['provider_counts']
    need(counts == {'gauge44':1568, 'extra':592, 'extra-four':1080}, 'actual provider selector')
    for provider, multiplicity in counts.items():
        record = native['active_providers'][provider]
        for rank, number in record['child_profile'].items():
            total[int(rank)] += multiplicity * number
        need(set(record['local']) == {'forward', 'backward'}, 'both literal native orientations')
        for direction in record['local'].values():
            need(direction['all_exact_columns'] == 632 and direction['private_work_erased']
                 and direction['zero_buffers_returned_to_zero'] == 91, 'complete dirty input and private endpoint')
    need(dict(total) == PROFILE, 'all native restoration and idle children in joined profile')
    # Close the native-proof -> actual-global-provider source edge explicitly.
    manifest = load(PRIOR / 'PHYSICAL-GLOBAL-PINS.json')['bundle']
    raw = (PRIOR / manifest['path']).read_bytes()
    need(sha(raw) == manifest['sha256'], 'exact global bundle in join')
    with tarfile.open(PRIOR / manifest['path']) as archive:
        member = archive.extractfile('data/PHYSICAL-PROJECTION.json').read()
    need(sha(member) == manifest['files']['data/PHYSICAL-PROJECTION.json']['sha256'],
         'exact physical provider projection')
    projection = json.loads(member)
    local_manifest = load(PRIOR / 'PHYSICAL-PINS.json')['bundle']
    local_path = PRIOR / local_manifest['path']
    need(sha(local_path.read_bytes()) == local_manifest['sha256'] ==
         native['prior_physical_bundle_sha256'], 'same exact local native bundle')
    actual = {}
    with tarfile.open(local_path) as archive:
        for provider in native['active_providers']:
            for name in ('CANONICAL-WORD.json.gz', 'LOCAL-PROGRAMS.json.gz',
                         'CLIFFORD-RECIPES.json', 'RESIDUAL-ADAPTERS.json'):
                path = 'native/' + provider + '/' + name
                body = archive.extractfile(path).read()
                need(sha(body) == local_manifest['files'][path]['sha256'], 'exact native member')
                actual[provider, name] = body
    for provider, record in native['active_providers'].items():
        physical = projection['local_providers'][provider]
        regenerated = record['regenerated_scientific_json_sha256']
        for name, field in (('CANONICAL-WORD.json.gz', 'canonical_word_sha256'),
                            ('LOCAL-PROGRAMS.json.gz', 'local_programs_sha256'),
                            ('CLIFFORD-RECIPES.json', 'exact_local_clifford_recipe_sha256'),
                            ('RESIDUAL-ADAPTERS.json', 'residual_adapter_sha256')):
            need(sha(actual[provider, name]) == physical[field], 'actual serialized native source')
        for name in ('CANONICAL-WORD.json.gz', 'LOCAL-PROGRAMS.json.gz'):
            scientific = json.loads(gzip.decompress(actual[provider, name]))
            need(sha(json.dumps(scientific, sort_keys=True, separators=(',', ':')).encode()) ==
                 regenerated[name], 'same complete scientific native JSON')
        need(physical['physical_program_binding'] == regenerated['LOCAL-PROGRAMS.json.gz'],
             'native theorem is for actual global provider: ' + provider)
        need(len(physical['widths']) == 408 and record['persistent_inputs_each_orientation'] == 632,
             'complete native role/hosting boundary')
    return total


def rates(profile):
    path = PRIOR / 'joint_bound.py'
    module = types.ModuleType('authenticated_pooled_interval_arithmetic')
    module.__file__ = str(path)
    # Imports only stdlib; no source-adjacent import cache can replace this body.
    exec(compile(path.read_bytes(), str(path), 'exec', optimize=0), module.__dict__)
    sigma, alpha, eta, tau = Q('.99826995'), Q('.99827'), Q(1, 10**6), Q(332353,332929)
    lower, upper = module.moment(profile, 73, 322560, 1-sigma)
    need(lower <= upper < 0 and tau < sigma < alpha, 'strict complete moment and B1 ordering')
    internal, leaf = sigma-eta*(sigma-tau), sigma+eta*(1-sigma)
    phi, beta, kappa = 1-Q(997,1000)*(1-alpha), Q(41544341,41616125), Q(1,580)
    need(internal < alpha and leaf < alpha and Q('.998') < alpha,
         'all stopped-tree and reservation powers')
    need(500*(1-alpha) < 1 and beta < phi and Q('.9981') < phi,
         'failed-guard fallback, full router and Gaussian costs')
    need((1-kappa)-phi == Q(1949,2900000000) > 0, 'remaining outer logarithm is paid')
    expected = load(PRIOR / 'evidence/PHYSICAL-GLOBAL.json')['physical_layer_rate']
    need(list(map(str, (lower, upper))) == expected['moment_minus_one'] and
         str(internal) == expected['internal_exponent'] and str(leaf) == expected['leaf_exponent'],
         'same complete invoice and exact guard/stopped-tree source')
    return dict(sigma=str(sigma), tau=str(tau), alpha_layer=str(alpha),
                moment_minus_one=list(map(str, (lower, upper))),
                internal_exponent=str(internal), leaf_exponent=str(leaf),
                Phi=str(phi), beta_router=str(beta), Gaussian_payload_power='9981/10000',
                final_log_gap=str((1-kappa)-phi), kappa=str(kappa),
                selected_kappa_comparison_only='0.001672660197076918')


def certificate():
    authenticated()
    native = load(HERE / 'evidence/NATIVE-ADMISSION.json')
    host = load(HERE / 'evidence/HOSTING-ADMISSION.json')
    machine = load(HERE / 'evidence/MACHINE-ADMISSION.json')
    need(machine.get('status', '').startswith('PASS_'), 'machine source-specific certificate')
    profile = complete_profile(native, host)
    costs = rates(profile)
    # The old outer proof/evidence is retained, not rerun or broadened here.
    outer = load(PRIOR / 'evidence/OUTER-DOMAIN.json')
    need(outer['exact_exponents']['kappa'] == costs['kappa'] and
         outer['exact_exponents']['final_log_gap'] == costs['final_log_gap'] and
         not outer['numerical_payload_executed'] and not outer['production_native_constructors_executed'],
         'preserve precise prior outer evidence scope')
    proof_hashes = {name:sha((HERE / name).read_bytes()) for name in
                    ('NATIVE-ADMISSION.md', 'HOSTING-ADMISSION.md', 'MACHINE-ADMISSION.md', 'ADMISSION.md')}
    receipt_hashes = {name:sha((HERE / 'evidence' / name).read_bytes()) for name in
                      ('NATIVE-ADMISSION.json', 'HOSTING-ADMISSION.json', 'MACHINE-ADMISSION.json')}
    # Real counterexample to an overbroad finite-width ABI. For C's first row,
    # a*u+b*v=2M with a=(1+i)/2,b=(1-i)/2. Each input component fits h bits.
    # Exact guarded execution requires spare denominator/magnitude budget.
    overflow_controls = 0
    for width in range(2, 9):
        maximum = (1 << (width-1)) - 1
        real = Q(maximum-(-maximum), 2) + Q(maximum+maximum, 2)
        imaginary = Q(maximum+(-maximum), 2) + Q(maximum-maximum, 2)
        need(real == 2*maximum > maximum and imaginary == 0,
             'fitting inputs alone do not imply a safe internal finite-width C call')
        overflow_controls += 1
    return dict(schema=1, status='PASS_SOURCE_SPECIFIC_CONDITIONAL_ADMISSION_JOIN',
                claim='Written source-specific pooled admission and conditional integer kappa=1/580; no frontier decision',
                scientific_head='a929a3fa36301bdfcffe82afd37434dd9e3c4887',
                profile=dict(sorted(profile.items())), rank_mass=sum(r*n for r,n in profile.items()),
                costs=costs, written_proof_sha256=proof_hashes, finite_receipt_sha256=receipt_hashes,
                discharged=['all-positive-f native operators and exact private cleanup',
                            'complete chronological whole-family hosting and all-cover transport',
                            'source-specific pooled fixed-controller and internal recursive realization'],
                retained_hypotheses=['B_ordinary (including BIT H1-H5)', 'P_elementary',
                                     'G_modern (complete retained physical component and analytic contracts)', 'BHP'],
                modern_premises_identical_to_selected_legacy=False,
                internal_execution_domain='reachable guarded-root calls; incoming height a plus internal prefix allowance A(e) <= Delta, with caller tail reserve',
                overbroad_h_bit_domain_counterexamples=overflow_controls,
                production_payload_executed=False, formal_kernel_verified=False,
                independent_human_admission=False, selected_frontier_changed=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--check', type=Path)
    args = parser.parse_args()
    result = json.loads(json.dumps(certificate()))
    if args.check:
        need(result == load(args.check), 'fresh admission join equals recorded receipt')
    raw = json.dumps(result, sort_keys=True, indent=2) + '\n'
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(raw)
    print(raw, end='')


if __name__ == '__main__':
    main()
