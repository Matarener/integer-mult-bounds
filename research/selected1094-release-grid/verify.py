"""Exact selected1094 release-grid refinement. Apache-2.0, Nick Petalas."""
from collections import Counter
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import sys
import uuid

# Authenticate all three modules before import, and bypass existing bytecode caches.
P = Path(__file__).resolve().parent
_pins = json.loads((P / 'BINDINGS.json').read_bytes())
for _name in ('base_two_moment', 'moment', 'outer'):
    _raw = (P / 'vendor' / (_name + '.py')).read_bytes()
    if hashlib.sha256(_raw).hexdigest() != _pins['vendor/' + _name + '.py']['sha256']:
        raise ValueError('engine source binding')
sys.path.insert(0, str(P / 'vendor'))
sys.dont_write_bytecode = True
sys.pycache_prefix = str(P / ('.unused-bytecode-' + uuid.uuid4().hex))
import base_two_moment as B
import moment as M
import outer as A

P = Path(__file__).resolve().parent
KAPPA = Q('0.001672660197076918658752')
ETA = Q(1, 10**24)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(name):
    return json.loads((P / name).read_bytes())


def source_bindings():
    bindings = read('BINDINGS.json')
    require(len(bindings) == 9, 'complete frozen source inventory')
    for name, row in bindings.items():
        raw = (P / name).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row['sha256'], name)
    selected, assembly = read('inputs/selected-result.json'), read('inputs/ASSEMBLY.json')
    require(selected['certificate_sha256'] == bindings['inputs/ASSEMBLY.json']['sha256'],
            'selected certificate binding')
    require(selected['kappa'] == assembly['kappa'], 'baseline kappa')
    for name in ('moment', 'base_two_moment', 'outer'):
        require(assembly['input_sha256']['engines/' + name + '.py'] ==
                bindings['vendor/' + name + '.py']['sha256'], 'selected engine')
    for name, key in [('owners', 'owner_audit'), ('invoice', 'fresh_invoice')]:
        require(assembly['input_sha256'][key] == bindings['inputs/' + name + '.json']['sha256'],
                'selected finite receipt')
    require(assembly['input_sha256']['package:inputs/PR589-EXPECTED.json'] ==
            bindings['inputs/PR589-EXPECTED.json']['sha256'], 'selected BIT source')
    return assembly


def profile(raw, width, live, deficit):
    require(type(raw) is dict and 1 <= len(raw) <= 16, 'profile size')
    require(type(width) is int and type(live) is int and 1 < width <= 73 and live > 0,
            'primitive domain')
    require(all(type(k) is str and k.isdigit() and str(int(k)) == k and
                0 < int(k) < width and type(n) is int and n > 0 for k, n in raw.items()),
            'strict profile types')
    h = {int(r): n for r, n in raw.items()}
    require(width * live - sum(r * n for r, n in h.items()) == deficit, 'rank mass')
    require(width**2 > 2 * max(h)**2, 'halving')
    return h


def supplier(h, width, live, endpoint, bad):
    rows = []
    for a, accept in [(endpoint, True), (endpoint + ETA, False)]:
        lo, hi = M.moment(h, width, live, a, bad)
        left, right = B.moment(width, live, list(h.items()), a)
        if bad:
            fl, fu = B.moment(width, live, [(1, 32 * width**2 * sum(h.values()))], a)
            left, right = left + fl / 10**16, right + fu / 10**16
        require(0 < lo <= hi and 0 < left <= right, 'interval order')
        require((hi < 1 and right < 1) if accept else (lo > 1 and left > 1),
                'strict complete supplier moment')
        rows.append(dict(endpoint=str(a), accepted=accept,
                         mercator_minus_one=[str(lo - 1), str(hi - 1)],
                         base_two_minus_one=[str(left - 1), str(right - 1)]))
    return rows


def physical_invoice(assembly):
    owner, inv = read('inputs/owners.json'), read('inputs/invoice.json')
    require(owner['paid_profile'] == assembly['complex_profile'], 'complete profile binding')
    require(inv['owner_audit_sha256'] == assembly['input_sha256']['owner_audit'], 'invoice owner')
    require(owner['template_sha256'] == inv['template_sha256'] == assembly['template_sha256'],
            'unchanged controller')
    require(len(inv['selected_calls']) == inv['complete_invocation_sweeps'] == 144, 'all calls')
    require(inv['physical_stock_identity'] == dict(data_and_owner_families=14336,
            local_helpers=480, private_centres=8, coefficient_work=2), 'paid physical stock')
    require(inv['physical'] == owner['physical'] == 14826 and inv['live'] == owner['live'] == 14336,
            'stock and live roles')
    local = Counter()
    for call in inv['selected_calls']:
        local.update({int(r): n for r, n in inv['providers'][call['provider_id']]['paid_profile'].items()})
    require(dict(local) == {int(r): n for r, n in inv['selected_local_paid_profile'].items()},
            'all144 local profiles')
    remainder = Counter({int(r): n for r, n in owner['paid_profile'].items()})
    remainder.subtract(local)
    require(all(n >= 0 for n in remainder.values()) and sum(remainder.values()) == 7526,
            'all idle remainders paid')
    require(inv['global_prefix_bits'] == 397 and inv['charged_prefix_bits'] == 512,
            'unchanged precision tariff')
    require(len(inv['strict_checks']) == 9 and all(v is True for v in inv['strict_checks'].values()),
            'inherited finite guards')
    return finite_guards(inv, owner)


def finite_guards(inv, owner):
    group = 2**1296
    for j in range(1, 37):
        group *= 2**(2*j) - 1
    stock, mass = group * inv['physical'], group * owner['rank_mass']
    logical = group * inv['conservative_pervertex_used'] + 64
    router = inv['compiler'] * (logical + 1) * (stock + 1)**2
    literal = 2 * 2**30000 * stock**2 + 8 * mass + 4 * stock + 4 + 32 * 73
    total = mass + 2**100000
    checks = dict(local_primitive_bound=inv['local_primitive_bound'] < 2**48,
                  logical=logical < 2**6050, router=router < 2**30000,
                  literal=literal < 2**100000, mass=total < 2**100001,
                  precision=32*73*total**2 < 2**210000, tape=2*total+18 < 2**210000,
                  row=2*stock.bit_length()+9909+252+1024 < 20161,
                  halving=73**2 > 2*48**2)
    require(checks == inv['strict_checks'] and all(checks.values()), 'recomputed full finite guards')
    return checks


def bootstrap(complex_endpoint, bit_endpoint):
    s = min(bit_endpoint, (1-ETA)*complex_endpoint) - Q(1, 10**27)
    require(0 < s < bit_endpoint and s < (1-ETA)*complex_endpoint, 'effective endpoint')
    old, rows = Q(384599, 10**10), []
    for _ in range(7):
        a = (1-s)*s + s*old
        gap = min(s-a, 1-a-s, 1-a-s*(1-old), 1-s)
        require(old < a < s < 1-a and gap > 0, 'bootstrap admissibility')
        cut = max((36/gap**2).__ceil__(), (2*(4+512)/gap).__ceil__())
        require(cut*gap**2 >= 36 and cut*gap >= 2*(4+512), 'paid bootstrap cutoff')
        rows.append(dict(exponent=str(a), gap=str(gap), cutoff_log2=str(cut)))
        old = a
    return old, rows


def outer(a, b, kappa, eta=ETA, beta=ETA):
    bridge = {'semantic': {'C0': {'base': 2, 'exponent': 210000}, 'strict_literal_gap': 1},
              'rows': {'degree_gap': Q(10**6) - Q(51*20161, 25)}}
    value = A.assembly(a, b, bridge, kappa, eta=eta, beta=beta)
    slacks, margins = value['strict_constraints'], value['margins']
    require(len(slacks) == 47 and len(margins) == 7 and all(x > 0 for x in slacks.values()),
            'all47 strict outer inequalities')
    require(all(x > kappa for x in margins.values()), 'all7 complete transfer margins')
    return value


def reject(action, name):
    try:
        action()
    except (ValueError, AssertionError):
        return name
    raise ValueError('control accepted: ' + name)


def verify():
    assembly = source_bindings()
    finite = physical_invoice(assembly)
    bit = read('inputs/PR589-EXPECTED.json')['nine']
    complex_h = profile(assembly['complex_profile'], 73, 14336, 5120)
    bit_h = profile(bit['profile'], 64, bit['bit']['live'], 10272)
    b, c = Q(assembly['complex_lower']), Q(assembly['bit_lower'])
    require(c == Q(bit['bit_lower']) and b < c, 'selected primitive endpoints')
    cm, bm = supplier(complex_h, 73, 14336, b, False), supplier(bit_h, 64, 28416, c, True)
    a, chain = bootstrap(b, c)
    require(chain == assembly['bootstrap'], 'identical paid bootstrap')
    baseline = outer(a, b, Q(assembly['kappa']))
    require({k: str(v) for k, v in baseline['strict_constraints'].items()} == assembly['outer'],
            'exact selected baseline47 reproduction')
    candidate = outer(a, b, KAPPA)
    require(KAPPA > Q(assembly['kappa']), 'strict improvement')
    controls = [reject(lambda: outer(a, b, KAPPA + ETA), 'next24_grid'),
                reject(lambda: outer(a, b, KAPPA, eta=Q(0)), 'zero_eta'),
                reject(lambda: outer(a, b, KAPPA, beta=Q(0)), 'zero_beta'),
                reject(lambda: outer(a, b, KAPPA, beta=Q(1)), 'unit_beta')]
    malformed = dict(assembly['complex_profile'], **{'1': True})
    controls.append(reject(lambda: profile(malformed, 73, 14336, 5120), 'boolean_count'))
    unpaid = dict(assembly['complex_profile']); unpaid['48'] -= 1
    controls.append(reject(lambda: profile(unpaid, 73, 14336, 5120), 'unpaid_child'))
    require(M.moment(bit_h, 64, 28416, c+ETA, False)[1] < 1, 'omitted surcharge control')
    require(M.moment(complex_h, 73, 14336, b, True)[0] > 1, 'wrong complex surcharge control')
    return dict(status='PASS_SELECTED1094_RELEASE_GRID', kappa=str(KAPPA),
                gain=str(KAPPA-Q(assembly['kappa'])), primitive_delta=0, finite=finite,
                complex_moments=cm, bit_moments=bm, bootstrap=chain,
                outer={k: str(v) for k, v in candidate['strict_constraints'].items()},
                margins={k: str(v) for k, v in candidate['margins'].items()},
                absorption_gap=str(candidate['absorption_gap']), controls=controls,
                scope='Conditional selected finite construction; only final release grid changes.')


if __name__ == '__main__':
    result = verify()
    if (P / 'CERTIFICATE.json').exists():
        require(json.dumps(result, sort_keys=True) ==
                json.dumps(read('CERTIFICATE.json'), sort_keys=True),
                'strict typed committed certificate equality')
    print(json.dumps(result, indent=2))
