"""Exact arithmetic and finite controls; this is not an all-size theorem checker."""
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import gzip
import hashlib
import importlib.util
import itertools
import json
import sys


def need(condition, message):
    if not condition:
        raise ValueError(message)


ROOT = Path(__file__).resolve().parents[2]
PKG = ROOT / 'research/staged544-mixed-fourth-entry'
ENGINE = PKG / 'vendor/exact_root.py'
need(hashlib.sha256(ENGINE.read_bytes()).hexdigest() ==
     '565e0d7de2fcd7587045f11731dfaba202e18f93e3a7a8178374f4933e502fbe', 'engine pin')
spec = importlib.util.spec_from_file_location('exact_root_checked', ENGINE)
E = importlib.util.module_from_spec(spec)
spec.loader.exec_module(E)

profile = {1: 8060060, 2: 2310120, 3: 751813, 4: 327210,
           5: 66425, 8: 25920, 48: 138492}
result = json.loads((PKG / 'RESULT.json').read_text())
need(profile == {int(k): v for k, v in result['profile'].items()}, 'mixed profile')
b = Q('.001730979115670792472760579929302792893760378764')
upper = b + Q(1, 10**48)
signs = E.certify_bracket(profile, b, upper)
kappa = Q('.00173097911567079247276057')
q = b - Q(1, 10**28)
a_eff = (b + q) / 2
eps = 1 - Q(1, 10**30)
beta = 1 - Q(3, 10**30)
xi = eps * (1 + q) - Q(3, 32) + Q(1, 10**30)
stop = Q(1, 10**32)

c = Q(8667, 5000000)
a1, a2 = c * (1-c), c * (1-c*c)
bit_h = {1: 381024, 2: 400416, 3: 22752, 4: 26880,
         5: 29376, 6: 17376, 7: 26784, 42: 288}
fallback = 32 * 64**2 * sum(bit_h.values())
scale = 10**16
signed_bit = {r: n * scale for r, n in bit_h.items()}
signed_bit[1] += fallback
signed_bit[64] = -28416 * scale
bit_sign = E.moment(signed_bit, c)
linear = (sum(r*n for r, n in bit_h.items()) + Q(fallback, scale)) / (64*28416)
need(bit_sign[1] < 0 and linear < 1, 'two strict BIT moments')
need(a1 == Q('.00173039532444') and a2 == Q('.001733394791695384296'), 'bootstrap')
need(7**16 < 2**45, 'unconditional Strassen exponent')

powers = {
    'main': 1-eps*q, 'global_router': 1-a_eff,
    'gaussian': eps-q*beta, 'group_router': eps-a_eff*beta,
    'group_scans': eps-beta, 'boundary': eps-xi+Q(29,32),
    'union': eps+Q(1,2)-xi, 'products': 1-eps,
    'crt': 1-a2+2*(1-eps),
    'halo_arithmetic': eps+beta+144-400,
    'halo_metadata': eps+50-400, 'cached_phases_and_recovery': Q(0),
}
side = {
    'dimension_below_one': 1-eps, 'group_below_dimension': eps-beta,
    'group_positive': beta, 'group_headers': 1-beta,
    'membership': 1-beta-2*(1-eps),
    'shifted_guard': 1-beta-2*xi+2,
    'cap_above_band': xi-Q(1,2), 'cap_below_phase': 2-xi,
    'bounded_individual_chirp': 1-xi,
    'core_above_faces': 400-48-beta,
    'leaf_saving': (1-stop)*b-q,
    'bit_above_internal': a2-a_eff, 'internal_above_q': a_eff-q,
    'root_above_q': b-q, 'crt_table_guard': Q(64)-4,
}
slacks = {name: 1-kappa-power for name, power in powers.items()}
need(all(x > 0 for x in slacks.values()), 'every paid cost has strict room')
need(all(x > 0 for x in side.values()), 'every side condition has strict room')
need(kappa > Q(result['conditional_kappa']), 'strict improvement over PR4088 claim')
need(E.moment(E.signed(profile), a_eff)[1] < 0, 'internal moment')

rejected = {
    'old_Vd_crt': 1-kappa-eps,
    'old_g_union_scans': 1-kappa-(eps+beta+Q(1,2)-xi),
    'old_per_record_d_chirp': 1-kappa-eps,
    'old_theta_chirp_guard': 1-beta-2*xi+eps,
    'no_group_gap_membership': 1-eps-2*(1-eps),
}
need(all(x < 0 for x in rejected.values()), 'old routes must fail at this point')

# Audit actual scalar denominators after reduction, including negative raw ones.
sys.path.insert(0, str(PKG / 'vendor'))
import audit_core
coefficient_rows = {}
for kind, orientation in itertools.product(['THREE', 'FOUR'], ['base', 'extra']):
    path = PKG / f'inputs/{kind}-{orientation}.json.gz'
    word = json.loads(gzip.decompress(path.read_bytes()))
    audit_core.hygiene(word)
    gates, cleanup = audit_core.program(word)
    gates = gates + cleanup
    denominators = Counter()
    for gate in gates:
        if gate[0] == 'add':
            value = Q(gate[3], gate[4])
        elif gate[0] == 'scale':
            value = Q(gate[2], gate[3])
        elif gate[0] == 'corr':
            value = Q(gate[4])
        else:
            continue
        denominators[value.denominator] += 1
        need(value.denominator & (value.denominator-1) == 0, 'common dyadic grid')
    coefficient_rows[f'{kind}-{orientation}'] = {
        'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'events': len(gates), 'reduced_denominators': dict(denominators),
    }

# Cached products must recompute after a zero, and need no division.
cached_cases = cached_updates = 0
for radices in [(2,2,2), (3,4,3), (2,3,4,2)]:
    tables = [[Q((j+2*i)%5-2, 3) for j in range(r)] for i, r in enumerate(radices)]
    previous = None
    prefixes = [Q(1)] * (len(radices)+1)
    updates = 0
    for address in itertools.product(*(range(r) for r in radices)):
        first = 0 if previous is None else next(i for i, (a,b0) in enumerate(zip(address,previous)) if a!=b0)
        for i in range(first,len(radices)):
            prefixes[i+1] = prefixes[i] * tables[i][address[i]]
            updates += 1
        direct = Q(1)
        for i,j in enumerate(address):
            direct *= tables[i][j]
        need(prefixes[-1] == direct, 'cached phase product')
        previous = address
        cached_cases += 1
    need(updates <= 2*__import__('math').prod(radices), 'amortized product updates')
    cached_updates += updates

print(json.dumps({
    'status': 'PASS_EXACT_LEDGER_AND_FINITE_COMPOSITION_CONTROLS',
    'kappa_candidate': str(kappa), 'root_bracket': list(map(str,[b,upper])),
    'root_signs': [[str(x) for x in row] for row in signs],
    'bit_moment': list(map(str,bit_sign)), 'bit_linear_moment': str(linear),
    'parameters': {name:str(value) for name,value in
                   dict(q=q,a_eff=a_eff,a2=a2,epsilon=eps,beta=beta,xi=xi,stop=stop).items()},
    'cost_slacks': {k:str(v) for k,v in slacks.items()},
    'side_slacks': {k:str(v) for k,v in side.items()},
    'rejected_routes': {k:str(v) for k,v in rejected.items()},
    'scalar_sources': coefficient_rows,
    'cached_product_cases': cached_cases, 'cached_product_updates': cached_updates,
    'all_size_machine_proof_checked_by_this_script': False,
    'unconditional_multiplication_claimed_by_this_script': False,
}, indent=2, sort_keys=True))
