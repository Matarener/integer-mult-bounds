#!/usr/bin/env python3
"""Code-disjoint exact T16 moment and outer-witness scoring, not supplier admission.

Nick Petalas. Apache-2.0. Source equations and supplier data retain the PR1094,
PR3308, PR589 and balanced-assembly predecessor credit recorded in the receipt.
"""
import argparse
from decimal import Decimal, localcontext
from fractions import Fraction as F
import hashlib
import json
from math import isqrt
from pathlib import Path
import sys

BASELINE = F('0.001672660197076918')
BIT_ENDPOINT = F('1733427039589844234749/1000000000000000000000000')
BIT_PROFILE = {1: 381024, 2: 400416, 3: 22752, 4: 26880,
               5: 29376, 6: 17376, 7: 26784, 42: 288}
ETA = F(1, 10**24)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def show(value):
    with localcontext() as context:
        context.prec = 65
        return str(Decimal(value.numerator) / Decimal(value.denominator))


def ceil_div(numerator, denominator):
    return -(-numerator // denominator)


def root_table(base, bits, precision):
    """Enclose base**(2**-j), j=1..bits, by outward integer square roots."""
    require(1 <= base <= 256 and 1 <= bits <= 256 and bits + 32 <= precision <= 512,
            'root-table domain')
    scale = 1 << precision
    lo = base.numerator * scale // base.denominator
    hi = ceil_div(base.numerator * scale, base.denominator)
    roots = []
    for _ in range(bits):
        lo = isqrt(lo * scale)
        square = hi * scale
        upper_root = isqrt(square)
        hi = upper_root + (upper_root * upper_root != square)
        roots.append((lo, hi))
    return roots


def dyadic_product(numerator, roots, precision):
    """Interval for base**(numerator/2**len(roots)); numerator is nonnegative."""
    bits = len(roots)
    require(0 <= numerator < 1 << bits, 'proper fractional exponent')
    scale = 1 << precision
    lo = hi = scale
    for index, (left, right) in enumerate(roots):
        if numerator & (1 << (bits - index - 1)):
            lo = lo * left // scale
            hi = ceil_div(hi * right, scale)
    return F(lo, scale), F(hi, scale)


def power_bounds(base, exponent, bits=160, precision=256):
    require(F(1) <= base <= 256 and 0 <= exponent < 1, 'power domain')
    denominator = 1 << bits
    tick = exponent * denominator
    below = tick.numerator // tick.denominator
    above = ceil_div(tick.numerator, tick.denominator)
    roots = root_table(base, bits, precision)
    lower = dyadic_product(below, roots, precision)[0]
    upper = base if above == denominator else dyadic_product(above, roots, precision)[1]
    require(lower <= upper, 'power enclosure order')
    return lower, upper


def moment(profile, width, live, exponent, surcharge, bits=160, precision=256):
    require(1 <= len(profile) <= 64 and 2 <= width <= 256 and live > 0 and
            all(type(r) is int and type(n) is int and 0 < r < width and n > 0
                for r, n in profile.items()), 'moment domain')
    lower = upper = F(0)
    for rank, count in profile.items():
        lo, hi = power_bounds(F(width, rank), exponent, bits, precision)
        factor = F(rank * count, width * live)
        lower += factor * lo
        upper += factor * hi
    if surcharge:
        lo, hi = power_bounds(F(width), exponent, bits, precision)
        factor = F(32 * width * sum(profile.values()), 10**16 * live)
        lower += factor * lo
        upper += factor * hi
    return lower, upper


def endpoint_decisions(profile, width, live, endpoint, surcharge):
    require(width * width > 2 * max(profile)**2, 'halving guard')
    rows = []
    for value, accepted in [(endpoint, True), (endpoint + F(1, 10**24), False)]:
        low, high = moment(profile, width, live, value, surcharge)
        tight_low, tight_high = moment(profile, width, live, value, surcharge, 192, 320)
        require(low <= tight_low <= tight_high <= high, 'higher-precision enclosure containment')
        require((high < 1) if accepted else (low > 1), 'strict moment endpoint decision')
        rows.append(dict(endpoint=str(value), accept=accepted,
                         residual=[str(low - 1), str(high - 1)],
                         tighter_residual=[str(tight_low - 1), str(tight_high - 1)]))
    return rows


def bootstrap(bit_cap, complex_cap, count=7, eta=ETA, beta=ETA):
    require(1 <= count <= 16 and 0 < eta < F(1, 2) and 0 < beta < 1,
            'bootstrap parameter domain')
    target = min(bit_cap, (1 - beta) * complex_cap) - F(1, 10**27)
    prior = F(384599, 10**10)
    rows = []
    for _ in range(count):
        saving = target * (1 - target + prior)
        gap = min(target - saving, 1 - saving - target,
                  1 - saving - target * (1 - prior), 1 - target)
        require(prior < saving < target < 1 - saving and gap > 0, 'bootstrap inequalities')
        cut = max(ceil_div((36 / gap**2).numerator, (36 / gap**2).denominator),
                  ceil_div((1032 / gap).numerator, (1032 / gap).denominator))
        require(cut * gap**2 >= 36 and cut * gap >= 1032, 'fixed-allowance cutoff arithmetic')
        rows.append(dict(exponent=str(saving), gap=str(gap), cutoff_log2=str(cut)))
        prior = saving
    return prior, rows


def outer_slacks(saving, cap, kappa, eta=ETA, beta=ETA):
    """All 47 raw constraints, reduced only under the explicit cap>saving premise."""
    require(0 < saving < cap < F(1, 32), 'outer domain')
    q = saving - 2 * saving * eta
    reservation = q + eta / 4
    epsilon = (1 - eta) / (1 + q)
    layer = epsilon * q
    alpha = (layer + 1 - epsilon) / 2
    delta = eta / 8
    half_gap = (saving - q) / 2
    leaf = (1 - beta) * cap
    slacks = dict(bit_positive=saving, complex_above_bit=cap - saving,
                  complex_below_one_over32=F(1, 32) - cap, beta_positive=beta,
                  beta_below_one=1 - beta, leaf_saving_above_bit=leaf - saving,
                  q_positive=q, q_below_internal=saving - q, q_below_leaf=leaf - q,
                  c_positive=reservation, c_below_one=1 - reservation,
                  q_below_reservations=reservation - q,
                  lambda_above_tau=half_gap, lambda_above_sigma=cap - (saving + q) / 2,
                  lambda_above_internal=half_gap, lambda_prime_above_lambda=half_gap,
                  compact_leaf=leaf - q, compact_reservations=reservation - q,
                  lambda_prime_below_one=q, epsilon_positive=epsilon,
                  epsilon_below_one=1 - epsilon, guard_width=1 - epsilon,
                  K_geometry=1 - epsilon * (1 + reservation), K_dominates_log=epsilon * reservation,
                  record_suffix=1 - epsilon, phase_local=1 - epsilon - delta,
                  phase_boundary=alpha - delta, gamma_sublinear=1 - epsilon - alpha,
                  cell_above_band=epsilon - (1 - alpha) / 2,
                  prime_interval_packing=1 - epsilon, alpha_positive=alpha,
                  alpha_below_one=1 - alpha, alpha_below_one_fourth=F(1, 4) - alpha,
                  delta_positive=delta, delta_below_one_eighth=F(1, 8) - delta,
                  short_record_fallback=epsilon - saving, small_field_exposure=1 - epsilon - layer,
                  artificial_boundary=8 - epsilon + alpha - delta - layer,
                  literal_scalar_guard=F(1), row_product_gap=F(23971789, 25))
    margins = dict(balanced_prefix=1 - epsilon, coordinate_movement=saving,
                   compact_phase_layer=layer, bulk_exposure=saving,
                   Gaussian_arithmetic=min(1 - epsilon - delta, alpha - delta),
                   scalar_work=1 - epsilon - delta, dimension=epsilon)
    slacks.update({name + '_above_kappa': value - kappa for name, value in margins.items()})
    require(len(slacks) == 47 and min(margins.values()) == layer, '47-constraint reduction')
    return slacks, layer


def outer_decisions(bit_cap, complex_cap, kappa, eta=ETA, beta=ETA, count=7):
    saving, chain = bootstrap(bit_cap, complex_cap, count, eta, beta)
    slacks, margin = outer_slacks(saving, complex_cap, kappa, eta, beta)
    require(all(value > 0 for value in slacks.values()), 'all 47 strict outer constraints')
    cap = min(bit_cap, complex_cap)
    ceiling = cap / (1 + cap)
    require(kappa < margin < ceiling, 'fixed-family outer ceiling')
    next_slacks, _ = outer_slacks(saving, complex_cap, kappa + F(1, 10**18), eta, beta)
    require(next_slacks['compact_phase_layer_above_kappa'] <= 0, 'next headline grid rejects')
    controls = []
    for name, e, b, value, failed_key in [
        ('zero_eta', F(0), beta, kappa, 'q_below_reservations'),
        ('zero_beta', eta, F(0), kappa, 'beta_positive'),
        ('unit_beta', eta, F(1), kappa, 'beta_below_one'),
        ('margin_equality', eta, beta, margin, 'compact_phase_layer_above_kappa')]:
        failed, _ = outer_slacks(saving, complex_cap, value, e, b)
        require(failed[failed_key] <= 0, 'reason-matched outer control: ' + name)
        controls.append(name)
    return dict(bootstrap=chain, slacks={k: str(v) for k, v in slacks.items()},
                margin=str(margin), fixed_family_ceiling=str(ceiling),
                fixed_family_ceiling_decimal=show(ceiling), ceiling_gap=str(ceiling - kappa),
                controls=['next_headline_grid'] + controls)


def parameter_probe(bit_cap, complex_cap, kappa):
    cap = min(bit_cap, complex_cap)
    ceiling = cap / (1 + cap)
    root_upper = cap + F(1, 10**24)
    supplier_ceiling = root_upper / (1 + root_upper)
    require(0 < ceiling - kappa < supplier_ceiling - kappa < F(1, 10**18),
            'even endpoint-refined parameter-only headroom is sub-grid')
    variants = []
    for exponent in (8, 12, 16, 24, 32):
        eta = beta = F(1, 10**exponent)
        for count in (7, 8, 10):
            saving, _ = bootstrap(bit_cap, complex_cap, count, eta, beta)
            _, margin = outer_slacks(saving, complex_cap, F(0), eta, beta)
            require(margin < ceiling, 'parameter variant respects proved family ceiling')
            variants.append(dict(eta=str(eta), beta=str(beta), bootstrap_steps=count,
                                 margin=str(margin), gain_over_headline=str(margin - kappa)))
    return dict(status='NO_MEANINGFUL_PARAMETER_ONLY_HEADROOM_IN_THIS_FAMILY',
                criterion='Any improvement is less than one existing 10^-18 headline-grid unit.',
                fixed_endpoint_ceiling=str(ceiling), fixed_endpoint_gap=str(ceiling - kappa),
                rejected_endpoint_ceiling=str(supplier_ceiling),
                rejected_endpoint_gap=str(supplier_ceiling - kappa), variants=variants)


def score(assembly):
    require(assembly['surcharge_model'] == {'complex': False, 'bit': True},
            'reviewed native/bit surcharge conventions')
    require(assembly['provider_counts'] == {'gauge44': 144}, 'fixed T16 invocation count')
    profile = {int(rank): count for rank, count in assembly['complex_profile'].items()}
    require(73 * 14336 - sum(rank * count for rank, count in profile.items()) == 5120,
            'unchanged complete rank mass')
    require(F(assembly['bit_lower']) == BIT_ENDPOINT, 'unchanged bit cap')
    native = F(assembly['complex_lower'])
    conservative = F(assembly['conservative_complex_lower'])
    headline = F(assembly['kappa'])
    conservative_headline = F(assembly['conservative_kappa'])
    bit = endpoint_decisions(BIT_PROFILE, 64, 28416, BIT_ENDPOINT, True)
    complex_decisions = endpoint_decisions(profile, 73, 14336, native, False)
    fallback = endpoint_decisions(profile, 73, 14336, conservative, True)
    require(moment(profile, 73, 14336, native, True)[0] > 1,
            'native endpoint rejects the conservative surcharge')
    require(moment(BIT_PROFILE, 64, 28416, BIT_ENDPOINT + F(1, 10**24), False)[1] < 1,
            'omitting bit surcharge changes the rejected endpoint')
    outer = outer_decisions(BIT_ENDPOINT, native, headline)
    conservative_outer = outer_decisions(BIT_ENDPOINT, conservative, conservative_headline)
    if 'outer' in assembly:
        require(outer['slacks'] == assembly['outer'], 'primary native 47 slacks agree exactly')
        require(outer['bootstrap'] == assembly['bootstrap'], 'primary native bootstrap agrees exactly')
        require(conservative_outer['slacks'] == assembly['conservative_outer'],
                'primary conservative 47 slacks agree exactly')
        require(conservative_outer['bootstrap'] == assembly['conservative_bootstrap'],
                'primary conservative bootstrap agrees exactly')
    return dict(status='PASS_INDEPENDENT_T16_EXACT_SCORE', baseline=str(BASELINE),
                kappa=str(headline), kappa_decimal=show(headline), delta_vs_selected=str(headline - BASELINE),
                delta_vs_pr3308=str(headline - F('0.001673618490895016')),
                complex_lower=str(native), conservative_complex_lower=str(conservative),
                bit_lower=str(BIT_ENDPOINT), complex_profile=assembly['complex_profile'], bit_profile=BIT_PROFILE,
                model_controls=['native_endpoint_rejects_old_surcharge', 'bit_surcharge_is_load_bearing'],
                bit=bit, complex=complex_decisions, conservative_complex=fallback,
                outer=outer, conservative_outer=conservative_outer,
                parameters=parameter_probe(BIT_ENDPOINT, native, headline),
                scope='Arithmetic only; physical/placement and full-invoice gates are separate.',
                cutoff_scope='Bootstrap cutoff rows are fixed-allowance arithmetic samples, not actual carried-constant thresholds.',
                method='Integer square-root dyadic power enclosures at 160/256 and 192/320 bits; no producer imports.')


def bounded_bytes(path):
    require(path.is_file() and not path.is_symlink() and path.stat().st_size <= 16 * 1024**2,
            'regular source file within 16 MiB limit')
    return path.read_bytes()


def bind_candidate(assembly, data, invoice_path, audit_path, bit_path):
    names = {'OWNERS.json.gz': data / 'OWNERS.json.gz', 'PLAN.json': data / 'PLAN.json',
             'SPEC.json': data / 'SPEC.json', 'PREFIX-AND-INVOICE.json': invoice_path,
             'OWNERS-AND-PROFILE.json': audit_path, 'PR589-EXPECTED.json': bit_path}
    payloads = {name: bounded_bytes(path) for name, path in names.items()}
    hashes = {name: hashlib.sha256(raw).hexdigest() for name, raw in payloads.items()}
    spec = json.loads(payloads['SPEC.json'])
    plan = json.loads(payloads['PLAN.json'])
    invoice = json.loads(payloads['PREFIX-AND-INVOICE.json'])
    audit = json.loads(payloads['OWNERS-AND-PROFILE.json'])
    bit = json.loads(payloads['PR589-EXPECTED.json'])
    require(spec['data']['owners_sha256'] == hashes['OWNERS.json.gz'] and
            spec['data']['plan_sha256'] == hashes['PLAN.json'], 'frozen candidate data hashes')
    require(plan['assignment_sha256'] == hashes['OWNERS.json.gz'], 'plan owner hash')
    require(plan['profile'] == assembly['complex_profile'] == audit['paid_profile'] ==
            spec['expected']['global_profile'], 'source/profile/scoring binding')
    require(invoice['owner_audit_sha256'] == hashes['OWNERS-AND-PROFILE.json'] ==
            assembly['input_sha256']['owner_audit'], 'owner audit hash chain')
    require(assembly['input_sha256']['fresh_invoice'] == hashes['PREFIX-AND-INVOICE.json'],
            'full invoice hash chain')
    require(hashes['PR589-EXPECTED.json'] == assembly['input_sha256']['package:inputs/PR589-EXPECTED.json'] ==
            'b9f0e5ca038abe837b0007c8fe006f366a6f02009244ac57705a8a200e2301f4', 'unchanged bit source hash')
    require({int(r): n for r, n in bit['nine']['profile'].items()} == BIT_PROFILE and
            F(bit['nine']['bit_lower']) == BIT_ENDPOINT, 'unchanged bit source data')
    require(all(F(spec['expected'][key]) == F(assembly[key]) for key in
                ('complex_lower', 'conservative_complex_lower')), 'source primitive endpoint binding')
    require(F(spec['expected']['kappa']) == F(assembly['kappa']), 'source headline binding')
    require(spec['expected']['live'] == invoice['live'] == 14336 and
            spec['expected']['provider_counts'] == invoice['provider_counts'] ==
            assembly['provider_counts'] == {'gauge44': 144}, 'source caller normalization')
    return hashes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assembly', type=Path, required=True)
    parser.add_argument('--data', type=Path)
    parser.add_argument('--invoice', type=Path)
    parser.add_argument('--owners-audit', type=Path)
    parser.add_argument('--bit-source', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), 'fresh output only')
    bundle = (args.data, args.invoice, args.owners_audit, args.bit_source)
    require(all(bundle) or not any(bundle), 'provide all four source-binding arguments or none')
    source = bounded_bytes(args.assembly)
    assembly = json.loads(source)
    hashes = bind_candidate(assembly, *bundle) if all(bundle) else None
    result = score(assembly)
    result['assembly_sha256'] = hashlib.sha256(source).hexdigest()
    result['source_sha256'] = hashes
    result['scorer_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    with args.output.open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(result['status'], result['kappa_decimal'])


if __name__ == '__main__':
    main()
