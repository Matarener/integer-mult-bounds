# SPDX-License-Identifier: Apache-2.0
"""Bounded exact reuse/rounding replay; ordinary execution never rewrites receipts."""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json
from cache import (Arithmetic,WindowCache,dense_inverse,principal,need,
                   rounded_weighted_inverse,residual_certificate,round_nearest_integer,recover_known_integer,inverse_height_bound)
from fixtures import source_fixture,cyclic_fixture
from reference import inverse as independent_inverse
ROOT=Path(__file__).resolve().parent

def result():
    for name,digest in json.loads((ROOT/'INPUTS.json').read_text()).items():
        need(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,'source hash '+name)
    cases=[('upstream-setup-3',source_fixture(),[F(1)]*3,[1,2,3])]
    H,D=cyclic_fixture();cases.append(('weighted-cyclic-13',H,D,[1,2,4,8]))
    rows=[];total=0;restored=0
    for name,H,D,widths in cases:
        for width in widths:
            for method in ('schur','woodbury'):
                cache=WindowCache(H,list(range(width)),D);source=cache._source
                costs=[];max_residual=F(0);max_error=F(0);max_height=0
                baseline=Arithmetic();dense_inverse(principal(H,range(width)),baseline)
                for t in range(2*len(H)):
                    incoming=(width+t)%len(H)
                    costs.append(cache.slide(incoming,cache.source_digest,method))
                    A=principal(H,cache.labels);Q=independent_inverse(A)
                    need(cache.inverse==tuple(map(tuple,Q)),'independent exact inverse')
                    n=len(A)
                    for side in (0,1):
                        for i in range(n):
                            for j in range(n):
                                value=sum(((A[i][k]*cache.inverse[k][j] if side==0 else cache.inverse[i][k]*A[k][j]) for k in range(n)),F(0))
                                need(value==F(i==j),'two-sided exact inverse')
                    # Correlated payloads: duplicate/scaled columns do not require independence.
                    x=[F((-1)**i*(i+1)) for i in cache.labels]
                    b=[sum((A[i][j]*x[j] for j in range(n)),F(0)) for i in range(n)]
                    need(cache.apply(b)==tuple(x),'exact integer-valued solve')
                    Z=rounded_weighted_inverse(cache,16)
                    cert=residual_certificate(H,cache.labels,D,Z);rho=F(cert['residual'])
                    dw=[D[i] for i in cache.labels];bw=[b[i]/dw[i] for i in range(n)]
                    approximate=[dw[i]*sum((Z[i][j]*bw[j] for j in range(n)),F(0)) for i in range(n)]
                    error=max(abs(a-e) for a,e in zip(approximate,x))
                    bound=max(dw)*F(cert['inverse_error_bound'])*max(abs(v) for v in bw)
                    need(error<=bound<F(1,2),'weighted recovery bound')
                    need(recover_known_integer(approximate,bound)==tuple(x),'strict integer recovery')
                    for payload in (b,[2*v for v in b],[-v for v in b]):
                        target=cache.apply(payload)
                        need(tuple(sum((Q[i][j]*payload[j] for j in range(n)),F(0)) for i in range(n))==target,'correlated payload layout')
                    max_residual=max(max_residual,rho);max_error=max(max_error,error)
                    max_height=max(max_height,max(max(abs(v.numerator).bit_length(),v.denominator.bit_length()) for row in cache.inverse for v in row))
                    need(max_height<=inverse_height_bound(H,width),'uniform reduced height bound')
                    need(source==cache._source,'frozen global old-H unchanged')
                    total+=1;restored+=1
                rows.append({'fixture':name,'width':width,'method':method,'slides':len(costs),
                             'fresh_dense_field_ops':baseline.total(),'update_field_ops_min':min(costs),'update_field_ops_max':max(costs),
                             'maximum_weighted_residual':str(max_residual),'maximum_actual_physical_error':str(max_error),
                             'maximum_reduced_inverse_bit_length':max_height})
    return {'schema_version':1,'status':'PASS_SLIDING_WINDOW_INVERSE','slides':total,'integer_recoveries':restored,
            'rows':rows,'scope':'Exact arithmetic preparation and sufficient residual recovery; no physical compiler, wall-time speedup or kappa claim.'}

if __name__=='__main__':
    data=result();need(data==json.loads((ROOT/'RESULT.json').read_text()),'receipt drift')
    print(data['status'],data['slides'],'slides')
