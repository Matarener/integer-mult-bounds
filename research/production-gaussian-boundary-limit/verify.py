"""Exact corroboration of the written uniform theorem, never a limit estimator.
JoyboyBrian, substantial OpenAI Codex assistance. Apache-2.0.
"""
import hashlib
import importlib.util
import json
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def authenticate():
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    count = 0
    for row in manifest['files']:
        if row['usage'] == 'input':
            payload = (ROOT / row['path']).read_bytes()
            need(hashlib.sha256(payload).hexdigest() == row['sha256'], 'source hash: ' + row['path'])
            count += 1
    return count


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def products(Q, last):
    values = [F(1)]
    for r in range(1, last + 1):
        values.append(values[-1] * (1 - Q**r))
    return values


def full_coefficient(Q, n, i, j):
    p = products(Q, n)
    return sum((Q**r * p[j+r] / (p[i]*p[j-i+r]*p[j]*p[r])
                for r in range(n-j)), F())


def relative_checks(old):
    records = []
    for q, m in ((F(1,2),4), (F(2,3),8), (F(3,4),12)):
        Q=q*q; n=3*m+2; i=m; j=2*m; last=4*m+20
        p=products(Q,last)
        tail=Q**(last+1)/(1-Q)
        lo=p[-1]*(1-tail); hi=p[-1]
        eps=Q**(m+1)/((1-Q)*(1-Q**(m+1)))
        value=full_coefficient(Q,n,i,j)
        need(0<lo<=hi and eps<F(1,4),'nonvacuous product interval')
        need(lo**3*value >= 1-4*eps,'certified relative lower bound')
        # Even the upper enclosure of P certifies the upper bound in these cases.
        need(hi**3*value <= 1,'certified relative upper bound')
        need(value == old.coefficient(q,n,i,j),'retained full coefficient equality')
        partial=sum((Q**r/p[r] for r in range(m+1)), F())
        need(partial == 1/p[m], 'exact truncated weight telescoping')
        first=1/(p[i]*p[j-i])
        need(hi**3*first < 1-4*eps,'dropping positive r-tail falsifies relative bound')
        edge=full_coefficient(Q,n,0,j)
        need(hi**3*edge < 1-4*eps,'omitting i>=m falsifies relative bound')
        records.append({'q':str(q),'m':m,'N':n,'eps':str(eps),
                        'normalized_lower_dyadic':str(F(int(lo**3*value*2**80),2**80)),
                        'normalized_upper_dyadic':str(F(-int(-hi**3*value*2**80)+1,2**80))})
    # Independent elimination, using the predecessor's separately expressed inverse routine.
    entries=0
    for q in (F(1,2),F(2,3)):
        for n in (3,5,7):
            inverse=old.exact_inverse([[q**((i-j)**2) for j in range(n)] for i in range(n)])
            for i in range(n):
                for j in range(i,n):
                    need(inverse[i][j] == (-1)**(i+j)*q**(j-i)*full_coefficient(q*q,n,i,j),
                         'independent exact elimination versus full coefficient')
                    entries+=1
    return {'cases':records,'eliminated_entries':entries,'controls':['discarded-r-tail','missing-edge-distance']}


def scaled_geometry(old, source):
    setup, expression=source.source_expression()
    original=old.geometry_checks(setup,expression)
    checked=0
    for h, sqrtb, R in ((F(1,32),F(1,2),F(2)),
                        (F(1,64),F(1,4),F(2)),
                        (F(3,200),F(1,2),F(1))):
        b=sqrtb**2; s=h*sqrtb; theta=h*h; n=int(1/theta); J=int(R/s)
        need(2*J<=n,'finite geometry admissibility')
        for i in sorted({0,1,J//2,J-1}):
            for j in sorted({i,min(i+1,J-1),J-1}):
                for dx,dy in ((0,0),(0,1),(1,0),(1,1)):
                    x=s*(i+dx); y=s*(j+dy)
                    if x>y:
                        continue
                    target=b/F(4)-(y*y-x*x)
                    for u,v in ((i,j),(n-1-i,n-1-j)):
                        need(abs(b*old.gauge(theta,u,v)-target)<=12*(R+1)**2*h,
                             'rescaled compact exponent envelope')
                        checked+=1
        # The unscaled old cell width would give a different limiting exponent.
        need(s*s != h*h,'missing sqrt(b) scaling discriminator')
    return {'source_geometry':original,'scaled_exponent_checks':checked,
            'controls':['missing-sqrt-b-grid','retained-floor-offset','both-edge-orientations']}


def scale_checks():
    rows=[]
    # Exact rational subsequences check exponents, floors and ceilings only.
    # The all-real b,h assertion is proved in PROOF.md, not sampled here.
    for k in range(1,7):
        h=F(1,2**(10*k)); R=2**k
        for sqrtb in (F(1), F(1,2**k), F(3,2**(k+2))):
            b=sqrtb**2
            if b < F(1,2**(2*k)):
                continue
            s=h*sqrtb; raw=F(2**(2*k))/b
            m=-(-raw.numerator//raw.denominator); J=int(R/s); n=int(1/(h*h))
            need(2*J<=n and J>=m and n-J>=m+1,'joint regime geometry')
            need(m*s*(R+1)<=F(4,2**(6*k)),'uniform exceptional-area power')
            need(R*12*(R+1)**2*h<=F(48,2**(7*k)),'uniform compact exponent power')
            need(48*h*h/(b*b)<=F(48,2**(16*k)),'uniform product-drift power')
            rows.append({'h':str(h),'b':str(b),'m':m,'J':J,'N':n})
    # Ceiling alpha is not replaced by its unrounded real precursor.
    for t in (F(1,2),F(3,2),F(11,3)):
        alpha=-(-t.numerator//t.denominator)
        need(t<=alpha<t+1 and alpha*alpha<(t+1)**2,'ceiling-square bound')
    need(canonical({'ok':True})!=canonical({'ok':1}),'typed receipt control')
    return {'regime_rows':rows,'controls':['ceiling-retained','typed-bool-int']}


def run():
    authenticated=authenticate()
    old=load('retained_half_line_model','research/gaussian-half-line-operator-limit/model.py')
    source=load('retained_gaussian_source','research/broad-phase-cell-inverse-bound/verify.py')
    return {'authenticated_inputs':authenticated, 'relative_products':relative_checks(old),
            'geometry':scaled_geometry(old,source), 'scales':scale_checks(),
            'claim':'exact finite corroboration; the uniform production theorem is PROOF.md; no rounded or physical caller admission'}


def main():
    expected=json.loads((HERE/'RESULT.json').read_text())
    actual=run()
    need(canonical(actual)==canonical(expected),'complete typed receipt mismatch')
    print('PASS_PRODUCTION_GAUSSIAN_BOUNDARY_LIMIT')
    print(hashlib.sha256(canonical(actual).encode()).hexdigest())


if __name__=='__main__':
    main()
