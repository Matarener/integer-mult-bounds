#!/usr/bin/env python3
"""Construct complete spectator row prefixes and check the outer contract.

zxv, with substantial OpenAI Codex assistance. Apache-2.0.
The source global-H, support-router, compact layout and outer results retain
all predecessor credit. This reference is indexed; tape costs use the proof.
"""
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import argparse
import json
import random
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LEDGER = 'research/pr4359-p7-padding/dependencies/compiler-refill/endpoint.py'
SUPPORT = 'research/kappa-observation-integration/release-work/current/package/vendor/pr1673/capped-phase-fusion/'
CAP = F(1, 32)
ZERO = (F(0), F(0))


def need(value, message):
    if not value:
        raise ValueError(message)


def ceildiv(a, b):
    return -((-a)//b)


def authenticate():
    pins = {}
    for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if row['usage'] == 'input':
            data = (ROOT/row['path']).read_bytes()
            need(sha256(data).hexdigest() == row['sha256'], 'Source changed: '+row['path'])
            pins[row['path']] = row['sha256']
    text = (ROOT/(SUPPORT+'TENSOR-COMPILER.md')).read_text()
    need('schedule is identical on every axis and every coarse-label block' in text,
         'Actual row-independent H schedule')
    text = (ROOT/'notes/compact-control-layout.tex').read_text()
    need('as identity on the reserved and spectator coordinates' in text,
         'Actual completed reserved-field contract')
    module = types.ModuleType('pinned_outer')
    module.__file__ = str(ROOT/LEDGER)
    exec(compile((ROOT/LEDGER).read_bytes(), module.__file__, 'exec'), module.__dict__)
    return module, pins


def plan(n, selected, K, G, Q):
    selected = tuple(selected)
    need(n >= 1 and K >= 1 and G >= 1 and Q >= 1, 'Positive geometry')
    need(len(selected) % K == 0 and len(selected) > 0, 'Whole neighborhoods')
    h = len(selected)//K
    need(len(set(selected)) == len(selected) and all(0 <= s < n for s in selected),
         'Disjoint complete neighborhoods')
    for j in range(h):
        block = selected[j*K:(j+1)*K]
        need(block == tuple(range(block[0], block[0]+K)), 'Contiguous original neighborhood')
    R = K*ceildiv((Q-1).bit_length(), K)
    front, back = K*ceildiv(2*h*G, K), K*ceildiv(h*G, K)
    start = R+front
    target = tuple(range(start, start+h*K))
    need(start+h*K+back <= n, 'Spectator prefix and all complete fields fit')
    mapping = dict(zip(selected, target))
    for src, dst in zip(sorted(set(target)-set(selected)), sorted(set(selected)-set(target))):
        mapping[src] = dst
    # The sparse extension touches only S union T, irrespective of R.
    domain = set(selected)|set(target)
    need(set(mapping) == domain and set(mapping.values()) == domain, 'Bijective extension')
    inverse = {v:k for k,v in mapping.items()}
    need(all(inverse.get(i, i) not in selected for i in range(R)),
         'Every physical row bit comes from a genuine spectator')
    rows = 1 << R
    padded = Q*ceildiv(rows, Q)
    need(rows >= Q and rows <= padded < 2*rows and padded % Q == 0, 'One bounded row padding')
    return dict(n=n, h=h, K=K, G=G, Q=Q, R=R, front=front, back=back,
                target=target, mapping=mapping, inverse=inverse,
                rows=rows, padded_rows=padded, selected=selected)


def address(x, mapping, n):
    y = x
    for src, dst in mapping.items():
        bit = (x >> (n-1-src)) & 1
        mask = 1 << (n-1-dst)
        y = (y & ~mask) | (bit << (n-1-dst))
    return y


def permute(values, mapping, n):
    out = [ZERO]*len(values)
    for x, value in enumerate(values):
        out[address(x, mapping, n)] = value
    return out


def mul(a, b):
    return (a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0])


def c_tensor(values, bits, n):
    out = list(values)
    for bit in bits:
        mask = 1 << (n-1-bit)
        for x in range(len(out)):
            if x & mask:
                continue
            ar, ai = out[x]
            br, bi = out[x|mask]
            out[x] = ((ar-ai+br+bi)/2, (ar+ai-br+bi)/2)
            out[x|mask] = ((ar+ai+br-bi)/2, (-ar+ai+br+bi)/2)
    return out


def diagonal(values, n, salt):
    # Deliberately address-dependent: coarse-label tables cannot be commuted.
    phases = ((F(1),F(0)), (F(0),F(1)), (F(-1),F(0)), (F(0),F(-1)))
    return [mul(v, phases[((x*salt) ^ (x >> 1)).bit_count() % 4])
            for x,v in enumerate(values)]


def wrapped(values, p, row_dependent=False, bad_padding=False,
            skip_inverse=False, diagonal_too_early=False):
    n, R = p['n'], p['R']
    need(len(values) == 1 << n, 'Full global binary rectangle')
    data = permute(values, p['mapping'], n)
    width = 1 << (n-R)
    rows = [data[i*width:(i+1)*width] for i in range(p['rows'])]
    rows += [[ZERO]*width for _ in range(p['padded_rows']-p['rows'])]
    need(len(rows) % p['Q'] == 0, 'Full product stock, not maximum-only stock')
    # A completed-callee fixture may permute arbitrary dirty rows internally.
    # It returns I_ROW tensor C, not an implementation of the fast supplier.
    rows = rows[1:]+rows[:1]
    bits = [s-R for s in p['target'][::p['K']]]
    rows = [c_tensor(row, bits, n-R) for row in rows]
    rows = rows[-1:]+rows[:-1]
    if row_dependent:
        rows = [[mul(v, (F(-1),F(0))) if j & 1 else v for v in row]
                for j,row in enumerate(rows)]
    if bad_padding:
        need(len(rows) > p['rows'], 'Control needs a padded row')
        rows[-1][0] = (F(1),F(0))
    need(all(v == ZERO for row in rows[p['rows']:] for v in row), 'Padded rows return to zero')
    data = [v for row in rows[:p['rows']] for v in row]
    if diagonal_too_early:
        data = diagonal(data, n, 7)
    if not skip_inverse:
        data = permute(data, p['inverse'], n)
    return data


def source_rows(module, p):
    out = module.ledger(p)
    need(len(out['strict_checks']) == 54 and len(out['functional_checks']) == 3,
         'Exact source inventory')
    values = dict(out['strict_checks'], **out['functional_checks'])
    # Replace active-width stock fit by the proved ambient spectator fit.
    del values['new_BIT_row_stock_sublinear_in_active_group']
    rho, nu, zeta = (p[k] for k in ('rho','nu','zeta'))
    values.update(spectator_stock_global=1-nu*p['epsilon']-zeta,
                  spectator_stock_group=1-nu*p['beta']-zeta,
                  global_precision_guard=1-rho*p['epsilon'],
                  group_precision_guard=1-rho*p['beta'])
    need(len(values) == 60, '54 strict, four functional and two new precision checks')
    return values, out['margins']


def witness(U, B, kappa, rho, nu, zeta):
    need(rho >= 1 and 0 <= nu < 1 and 0 <= zeta < 1, 'Growth domain')
    M = min(U,B,CAP)
    E = min(F(1),1/rho,(1-zeta)/nu) if nu else min(F(1),1/rho)
    low = max(kappa/M,F(1,2))
    need(low < E, 'Positive advancing contract')
    eps = (low+E)/2
    q = (kappa/eps+M)/2
    a,b = (2*q+M)/3,(q+2*M)/3
    eta = min((2*eps-1)/2,(1-eps)/2)
    beta = 2*eps-1-eta
    h = min((eps-F(1,2))/2,F(1,64))
    return dict(kappa=kappa,complex_uniform_saving=U,bit_saving=B,
                epsilon=eps,beta=beta,q=q,a=a,b=b,stop=(b-a)/(2*b),
                r0=(1-rho*eps)/4,layout=F(3,32)-eps*q-h,
                rho=rho,nu=nu,zeta=zeta)


def encode(value):
    if isinstance(value,F): return str(value)
    if isinstance(value,dict): return {k:encode(v) for k,v in value.items()}
    if isinstance(value,(tuple,list)): return [encode(v) for v in value]
    return value


def run():
    module,pins = authenticate()
    rng = random.Random(6062)
    geometry = semantic = basis = 0
    max_prefix_ratio = F(0)
    for _ in range(600):
        K = rng.randint(1,4)
        h = rng.randint(1,6)
        Q = rng.choice([1,3,5,6,15,45])
        R = K*ceildiv((Q-1).bit_length(),K)
        n = R+K*ceildiv(2*h,K)+h*K+K*ceildiv(h,K)+rng.randint(0,20)
        starts = rng.sample(range(0,n-K+1,K),h)
        selected = tuple(x+j for x in starts for j in range(K))
        p = plan(n,selected,K,1,Q)
        need(len(p['mapping']) <= 2*h*K, 'Support independent of row-prefix length')
        for x in range(n):
            need(p['inverse'].get(p['mapping'].get(x,x),p['mapping'].get(x,x)) == x,
                 'All coordinate positions restored')
        geometry += 1
    # Complete basis-column check of every one-bit source location at n=6.
    for selected in range(6):
        p = plan(6,(selected,),1,1,1)
        for column in range(64):
            values = [ZERO]*64
            values[column] = (F(1),F(0))
            expected = [ZERO]*64
            expected[column] = (F(1,2),F(1,2))
            expected[column ^ (1 << (5-selected))] = (F(1,2),F(-1,2))
            need(wrapped(values,p) == expected, 'Complete Gaussian operator column')
            basis += 1
    fixtures = []
    for n in (7,8,9):
        for Q in (3,5):
            for s in range(n):
                if (Q-1).bit_length()+4 > n:
                    continue
                fixtures.append(plan(n,(s,),1,1,Q))
    for n,Q in ((11,6),(12,15)):
        for _ in range(6):
            fixtures.append(plan(n,tuple(rng.sample(range(n),2)),1,1,Q))
    for p in fixtures:
        n=p['n']
        values=[(F(rng.randint(-4,4)),F(rng.randint(-4,4))) for _ in range(1 << n)]
        inputs=diagonal(values,n,3)
        expected=diagonal(c_tensor(inputs,p['selected'][::p['K']],n),n,7)
        actual=diagonal(wrapped(inputs,p),n,7)
        need(actual == expected, 'Arbitrary dirty payload and surrounding label-dependent diagonals')
        max_prefix_ratio=max(max_prefix_ratio,F(p['R'],p['h']))
        semantic += 1
    p=plan(12,(0,1),1,1,15)
    values=[(F(i%7-3),F(i%5-2)) for i in range(4096)]
    inputs=diagonal(values,12,3)
    expected=diagonal(c_tensor(inputs,(0,1),12),12,7)
    controls={}
    for label,kw in [('missing_inverse',dict(skip_inverse=True)),
                     ('row_dependent_endpoint',dict(row_dependent=True)),
                     ('coarse_diagonal_before_restoration',dict(diagonal_too_early=True))]:
        actual=wrapped(inputs,p,**kw)
        if not kw.get('diagonal_too_early'):
            actual=diagonal(actual,12,7)
        need(actual != expected,'Reject '+label)
        controls[label]='rejected by exact Gaussian output'
    for label,fn in [('nonzero_padded_return',lambda:wrapped(inputs,p,bad_padding=True)),
                     ('incomplete_microbox',lambda:wrapped(inputs[:-1],p)),
                     ('insufficient_ambient_space',lambda:plan(5,(0,),1,1,15))]:
        try: fn()
        except ValueError: controls[label]='rejected by explicit contract check'
        else: raise ValueError('Control accepted: '+label)
    # Product 3*5 is required; padding only to max(3,5) does not clear it.
    wrong_rows=5*ceildiv(p['rows'],5)
    need(wrong_rows % 15 != 0,'Maximum-only stock control')
    controls['maximum_instead_of_product']='rejected by product divisibility'

    parameter_count=0
    for U in (F('.004'),F('.012'),F('.02'),F('.05')):
        for B in (F('.004'),F('.012'),F('.02'),F('.05')):
            for rho in (F(1),F(5,4),F(3,2),F(7,4)):
                for nu in (F(0),F(1,250),F(1,2),F(9,10)):
                    for zeta in (F(0),F('.1'),F('.4'),F('.6')):
                        M=min(U,B,CAP)
                        E=min(F(1),1/rho,(1-zeta)/nu) if nu else min(F(1),1/rho)
                        top=M*E
                        if E <= F(1,2) or top <= module.OLD_BASELINE: continue
                        for kappa in ((top+module.OLD_BASELINE)/2,top-F(1,10**24)):
                            point=witness(U,B,kappa,rho,nu,zeta)
                            checks,rows=source_rows(module,point)
                            need(len(rows)==9 and all(v>0 for v in checks.values()),'Full positive outer witness')
                            parameter_count += 1
    point=witness(F('.02'),F('.02'),F('.011'),F(3,2),F(1,2),F('.6'))
    checks,rows=source_rows(module,point)
    need(all(v>0 for v in checks.values()),'Target-scale constructive example')
    need(point['zeta']/(1-point['nu']) > 1,'Example cannot fit stock inside active width')
    encoded=[]
    for logp in (480,960,1920):
        precision=1 << logp
        G=4*logp+6
        K=128*G
        for x in (point['epsilon'],point['beta']):
            eh=x*logp
            er=(point['nu']*x+point['zeta'])*logp
            need(eh.denominator==er.denominator==1,'Encoded integral powers')
            h=1 << eh.numerator
            reserve=100*((1 << er.numerator)*logp**3+logp+1)
            R=K*ceildiv(reserve,K)
            required=R+K*ceildiv(2*h*G,K)+h*K+K*ceildiv(h*G,K)+logp**2
            need(required < precision//16,'Encoded ambient-prefix capacity')
            support=2*h*K
            free=precision//16-R
            need(free > 9*support*G+2*(support+1)*logp**2,'Router reservoirs and protected suffix fit outside the row prefix')
            d=1 << (point['epsilon']*logp).numerator
            need(K+64*logp < precision//(12*d),'Complete neighborhoods fit original long axes')
            need(K >= G+4*logp+10,'Actual finite compact-control guard')
            encoded.append(dict(log2p=logp,width_power=x,stock_power=point['nu']*x+point['zeta'],
                                row_bits_log2_upper=R.bit_length(),required_bits_log2_upper=required.bit_length(),
                                address_bits_log2=logp-4))
    return encode(dict(status='PASS_SPECTATOR_ROW_RESERVOIR',source_sha256=pins,
        geometry_cases=geometry,complete_gaussian_basis_columns=basis,
        arbitrary_payload_fixtures=semantic,max_fixture_row_bits_per_active_bit=max_prefix_ratio,
        controls=controls,outer_witnesses=parameter_count,outer_predicates=60,
        constructive_example=dict(parameters=point,margins=rows,
            minimum_strict_slack=min(checks.values()),old_active_stock_boundary=F(6,5)),
        encoded_production_layouts=encoded,
        scope='Constructive conditional spectator-prefix theorem and exact indexed reference. Retained router/callee/tape/precision/analytic contracts remain. No new finite supplier, kappa or full multiplier.'))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit',action='store_true')
    args=parser.parse_args()
    result=run()
    if args.emit: print(json.dumps(result,indent=2,sort_keys=True))
    else:
        need(result==json.loads((HERE/'RESULT.json').read_text()),'Receipt mismatch')
        print(result['status'],'basis_columns='+str(result['complete_gaussian_basis_columns']),
              'outer_witnesses='+str(result['outer_witnesses']),'RECEIPT_MATCH no_new_kappa')


if __name__=='__main__': main()
