#!/usr/bin/env python3
"""Exact paired complex endpoint and signed B4 controller, not a local supplier.

Gaussian arithmetic is pairs of integers divided by a common power of two.
The Laurent proof and native convolution execution use separate models.
Prepared with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from pathlib import Path
import gzip
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = Path('/Users/ross/git/math/integer-mult-bounds')
SOURCE = ROOT / 'research/kernel92-frame-composition/vendor/pr531/inputs/data-base'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def hash_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ga(a, b):
    return (a[0]+b[0], a[1]+b[1])


def gm(a, b):
    return (a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0])


def gn(a):
    return (-a[0], -a[1])


def norm(p, e):
    p = {x:a for x,a in p.items() if a != (0, 0)}
    if not p:
        return ({}, 0)
    while e and all(not ((r|i)&1) for r,i in p.values()):
        p = {x:(r//2, i//2) for x,(r,i) in p.items()}
        e -= 1
    return (p, e)


ONE = ({0:(1,0)}, 0)
ZERO = ({}, 0)


def padd(a, b):
    ap, ae = a
    bp, be = b
    e = max(ae, be)
    p = {x:(r << (e-ae), i << (e-ae)) for x,(r,i) in ap.items()}
    for x,(r,i) in bp.items():
        p[x] = ga(p.get(x, (0,0)), (r << (e-be), i << (e-be)))
    return norm(p,e)


def pneg(a):
    return ({x:gn(z) for x,z in a[0].items()}, a[1])


def trans(a, mask):
    return ({x^mask:z for x,z in a[0].items()}, a[1])


def direction(a, mask, sign=1):
    """Apply C_mask^(sign) = ((1+sign*i)I+(1-sign*i)X)/2."""
    p,e = a
    q = {}
    for x,z in p.items():
        q[x] = ga(q.get(x,(0,0)), gm((1,sign),z))
        q[x^mask] = ga(q.get(x^mask,(0,0)), gm((1,-sign),z))
    return norm(q,e+1)


def kernels(axes):
    p = ONE
    for mask,sign in axes:
        p = direction(p,mask,sign)
    return p


def product(a,b):
    p={}
    for x,u in a[0].items():
        for y,v in b[0].items():
            p[x^y]=ga(p.get(x^y,(0,0)),gm(u,v))
    return norm(p,a[1]+b[1])


def conj(a):
    return ({x:(r,-i) for x,(r,i) in a[0].items()},a[1])


def phase_kernel(n, axes):
    """Independently form H diag(i^wt(P_U x)) H from the actual projector."""
    vals=[]
    units=((1,0),(0,1),(-1,0),(0,-1))
    for x in range(1<<n):
        projected=0
        for v in axes:
            if (v&x).bit_count()&1:
                projected ^= v
        vals.append(units[projected.bit_count()%4])
    for bit in range(n):
        step=1<<bit
        for base in range(0,1<<n,step*2):
            for j in range(base,base+step):
                a,b=vals[j],vals[j+step]
                vals[j],vals[j+step]=ga(a,b),ga(a,gn(b))
    return norm(dict(enumerate(vals)),n)


def orthobasis(q,n=9):
    z=next(i for i in range(n) if not(q>>i)&1)
    a=q^(1<<z)
    order=list(range(n));order[z],order[0]=order[0],order[z]
    b=[(1<<i)^(a if (a>>i)&1 else 0) for i in order]
    need(b[0]==q,'port first in chart')
    need(all((u&v).bit_count()%2==int(i==j)
             for i,u in enumerate(b) for j,v in enumerate(b)),'orthogonal chart')
    return b


def native_port_contracts():
    path=SOURCE/'split-centres/CANONICAL-WORD.json.gz'
    d=json.loads(gzip.decompress(path.read_bytes()))
    ports=d['ports']
    records=[]
    for q in ports:
        b=orthobasis(q)
        for k in (2,3):
            p,qq,r=b[:1],b[1:k],b[k:]
            # The defining projector calculation does not import native recipes.
            cp,cq,cr=[phase_kernel(9,u) for u in (p,qq,r)]
            full=phase_kernel(9,[1<<i for i in range(9)])
            for u,c in ((p,cp),(qq,cq),(r,cr)):
                factors=kernels([(v,1 if v.bit_count()%4==1 else -1) for v in u])
                need(c==factors,'actual q_U phase versus signed native factors')
            need(product(product(cp,cq),cr)==full,'orthogonal phase additivity')
            c_pout=phase_kernel(9,p+r)
            c_qout=phase_kernel(9,qq+r)
            need(product(c_pout,conj(cp))==cr,'source paired residual')
            need(product(c_qout,conj(cq))==cr,'target paired residual')
            off=product(c_qout,conj(cp))
            characteristic_p=0
            characteristic_q=0
            for v in p:characteristic_p^=v
            for v in qq:characteristic_q^=v
            need(off==trans(full,characteristic_p),'off-diagonal F X_c(P)')
            kval=product(cq,conj(cp))
            need(conj(kval)==trans(kval,characteristic_p^characteristic_q),
                 'backward translation supplies inverse K')
            need(trans(kval,characteristic_p)==product(cp,cq),'forward terminal translation')
            need(trans(conj(kval),characteristic_q)==product(cp,cq),'backward terminal translation')
            need(off!=full,'terminal translation omission has a witness')
            # rho fixes P+Q and swaps the residual basis with a fresh coordinate block.
            # Negative signed native factors require the explicitly listed translation.
            exterior_alignment=sum(1<<j for j,v in enumerate(r) if v.bit_count()%4==3)
            records.append({'q':q,'k':k,'P':p,'Q':qq,'R':r,
                            'exterior_alignment_mask_local':exterior_alignment})
    need(len(records)==224,'all retained 112 ports, both common ranks')
    return {'ports':len(ports),'contracts':len(records),'state_columns_per_port':512,
            'projector_kernels_checked':672,'source_sha256':hash_file(path),
            'records':records}


def laurent_b4(mutant=None):
    """Identity over Z[z,z^-1], independent of the Gaussian convolution model."""
    def addpoly(a,b):
        return {j:a.get(j,0)+b.get(j,0) for j in a.keys()|b.keys()
                if a.get(j,0)+b.get(j,0)}
    rows=[[{0:1} if i==j else {} for j in range(8)] for i in range(8)]
    def scalar(dst,src,c):
        rows[dst]=[addpoly(a,{j:c*v for j,v in b.items()})
                   for a,b in zip(rows[dst],rows[src])]
    def local(pair,reverse=False):
        x,y=2*pair,2*pair+1
        dst,src=(x,y) if reverse else (y,x)
        exponent=-1 if reverse and mutant!='backward_inverse' else 1
        sign=-1 if reverse and mutant!='backward_sign' else 1
        rows[dst]=[addpoly(a,{j+exponent:sign*v for j,v in b.items()})
                   for a,b in zip(rows[dst],rows[src])]
    def bridge(dst,src,c):
        scalar(2*dst,2*src,c)
        scalar(2*src+1,2*dst+1,-c if mutant!='bridge_sign' else c)
    local(0)
    for p in range(4):
        local(p,True)
        if p<3:bridge(p,p+1,1)
        local(p)
        if p<3:bridge(p,p+1,-1)
    for p in reversed(range(3)):bridge(p+1,p,1)
    want=[[{} for _ in range(8)]for _ in range(8)]
    for p in range(4):
        want[2*p][2*p+1]={-1:-1}
        want[2*p+1][2*p]={1:1}
    return rows==want,rows


def native_b4(k=2,mutant=None):
    """Execute the nine residual directions on all 8*2^(k+9) Gaussian columns.

    Translation invariance turns the full kernel check into an all-input check.
    Coordinates: P=e0, Q=e1..e(k-1), each residual block has dimension one.
    """
    n=k+9
    rows=[[ONE if i==j else ZERO for j in range(8)] for i in range(8)]
    characteristic_p=1
    characteristic_q=(1<<k)-2
    char_a=characteristic_p^characteristic_q
    def dirrow(dst,axes):
        for axis,sign in axes:
            rows[dst]=[direction(a,axis,sign)for a in rows[dst]]
    def add(dst,src,sign=1,axes=()):
        p=rows[src]
        for axis,sgn in axes:p=[direction(a,axis,sgn)for a in p]
        if sign<0:p=[pneg(a)for a in p]
        rows[dst]=[padd(a,b)for a,b in zip(rows[dst],p)]
    common=[(1,-1)]+[(1<<i,1)for i in range(1,k)]
    def local(stage,p,reverse=False):
        x,y=2*p,2*p+1
        # A genuine address translation conjugation, not replacing K by a symbol.
        if reverse and mutant!='backward_translation':
            rows[x]=[trans(a,char_a)for a in rows[x]]
        before=[list(rows[x]),list(rows[y])]
        if reverse:add(x,y,-1 if mutant!='backward_sign' else 1,common)
        else:add(y,x,1,common)
        if reverse and mutant!='backward_translation':
            rows[x]=[trans(a,char_a)for a in rows[x]]
        dirrow(x,[(1<<(k+stage),1)])
        dirrow(y,[(1<<(k+stage),1)])
    def idle(p,first,last):
        axes=[(1<<(k+j),1)for j in range(first+1,last+1)]
        dirrow(2*p,axes);dirrow(2*p+1,axes)
    def bridge(dst,src,c):
        add(2*dst,2*src,c)
        add(2*src+1,2*dst+1,-c)
    local(0,0)
    for p in range(4):
        local(2*p+1,p,True)
        if p<3:
            idle(p+1,-1,2*p+1);bridge(p,p+1,1)
        local(2*p+2,p)
        if p<3:
            idle(p+1,2*p+1,2*p+2);bridge(p,p+1,-1)
        else:
            for j in range(4):idle(j,2*j+2,8)
    for p in reversed(range(3)):bridge(p+1,p,1)
    for p in range(4):
        x,y=2*p,2*p+1
        rows[x],rows[y]=rows[y],[pneg(a)for a in rows[x]]
        if mutant!='terminal_translation':
            rows[x]=[trans(a,characteristic_p)for a in rows[x]]
            rows[y]=[trans(a,characteristic_q)for a in rows[y]]
    f=kernels([(1<<j,1)for j in range(n)])
    want=[[f if i==j else ZERO for j in range(8)]for i in range(8)]
    mismatches=[]
    for i in range(8):
        for j in range(8):
            if rows[i][j]!=want[i][j]:
                delta=padd(rows[i][j],pneg(want[i][j]))
                x,z=next(iter(delta[0].items()))
                mismatches.append({'output_bank':i,'input_bank':j,'displacement':x,
                                   'real_numerator':z[0],'imag_numerator':z[1],
                                   'denominator_power':delta[1]})
    return {'k':k,'address_dimension':n,'address_states':1<<n,
            'all_input_columns':8*(1<<n),'all_output_kernel_coefficients':64*(1<<n),
            'pass':not mismatches,'first_mismatch':mismatches[:1]}


def main():
    template_path=SOURCE/'split-centres/GLOBAL-TEMPLATE.json.gz'
    phase_path=SOURCE/'work/complex-nine-native/DATA-PHASES.json'
    template=json.loads(gzip.decompress(template_path.read_bytes()))
    need([e.get('coefficient')for e in template['recipe']if e['kind']=='bridge']
         ==[1,-1,1,-1,1,-1,1,1,1],'signed B4 source recipe')
    need([e['reverse']for e in template['recipe']if e['kind']=='local']
         ==[False,True,False,True,False,True,False,True,False],
         'alternating B4 orientations')
    need(laurent_b4()[0],'universal Laurent B4 identity')
    laurent_controls={m:not laurent_b4(m)[0]
                      for m in ('backward_inverse','backward_sign','bridge_sign')}
    need(all(laurent_controls.values()),'Laurent defect controls')
    native=[native_b4(k)for k in (2,3)]
    need(all(z['pass']for z in native),'independent native B4 endpoint')
    native_controls={m:native_b4(2,m)for m in
                     ('backward_translation','backward_sign','terminal_translation')}
    need(all(not z['pass']for z in native_controls.values()),'native defect controls')
    out={'status':'PASS_PAIRED_COMPLEX_ENDPOINT_NO_LOCAL_WORD_NO_NEW_KAPPA',
         'source_recipe':{'template_sha256':hash_file(template_path),
                          'data_phases_sha256':hash_file(phase_path)},
         'actual_native_contracts':native_port_contracts(),
         'universal_laurent_identity':True,'laurent_controls':laurent_controls,
         'native_b4':native,'native_controls':native_controls,
         'scope':'All-input paired endpoint and arbitrary-invertible-K signed controller. A compatible cheaper local scalar word, source lowering, owner realization and all-size transfer are not supplied.'}
    (HERE/'ENDPOINT.json').write_text(json.dumps(out,indent=2)+'\n')
    print(out['status'])
    print(json.dumps({'native_b4':native,'laurent_controls':laurent_controls,
                      'native_controls':{m:z['first_mismatch']for m,z in native_controls.items()}}))


if __name__=='__main__':
    main()
