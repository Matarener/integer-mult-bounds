#!/usr/bin/env python3
"""Complete own-visit differentials for bulk supported H6 cubic blocks.

The source exploratory nullities are only rational upper bounds.  This
screen grants each such direction a free compatible diagonal extraction;
no algebraic factor construction or new supplier is thereby asserted.
"""
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
import hashlib, importlib.util, json, sys
import numpy as np

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPO = Path('/Users/ross/git/math/integer-mult-bounds')
OLD = Path('/Users/ross/git/math/.research-automation/runs/kappa-3605-successor-20261018T0940Z/major-frontier/complex-alternative')
PRE = HERE.parent/'partial-support'

def load(name, path):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

e = load('bulk_e8', REPO/'research/niemeier-lattices/code/e8_cubed.py')
b = load('bulk_budget', OLD/'optimistic_budget.py')

def basis(rows):
    piv={}
    for raw in rows:
        x=int(raw)
        for k in sorted(piv,reverse=True):
            if (x>>k)&1:x^=piv[k]
        if x:
            k=x.bit_length()-1
            for j in list(piv):
                if (piv[j]>>k)&1:piv[j]^=x
            piv[k]=x
    return tuple(piv[k] for k in sorted(piv,reverse=True))

def perp(U):
    out=[]
    for j in range(17):
        if any((u>>j)&1 for u in U):continue
        x=1<<j
        for u in U:
            if (u&x).bit_count()%2:x^=1<<(u.bit_length()-1)
        out.append(x)
    # All free coordinates, rather than all zero columns, are needed.
    pivots={u.bit_length()-1 for u in U};out=[]
    for j in range(17):
        if j in pivots:continue
        x=1<<j
        for u in U:
            if (u&x).bit_count()%2:x^=1<<(u.bit_length()-1)
        out.append(x)
    return basis(out)

def intersection(U,V):
    return perp(basis(perp(U)+perp(V)))

def geometry(packed, ids):
    U=basis(packed[i] for i in ids);P=perp(U);W=intersection(U,P)
    assert all(not((u&w).bit_count()%2) for u in U for w in W)
    return {'ports':len(ids),'U_rank':len(U),'U':list(U),'perp_rank':len(P),
            'radical_rank':len(W),'radical':list(W)}

def delta_invoice(geo, centres, w, k):
    p,u=geo['ports'],geo['U_rank'];assert 0<=w<=geo['radical_rank']
    d=Counter()
    def add(path,n):
        for r in path:
            if r:d[r]+=n
    add([u-1,17-u],p);add([16],-p)
    if w:add([w,16-w],p);add([16],-p)
    add([u,17-u],centres);add([17],-centres)
    add([u-w],centres);add([17],-centres)
    d=Counter({r:n for r,n in d.items() if n})
    saving=centres*(17-u+w)
    assert sum(r*n for r,n in d.items())==-saving
    bb=k+F(1,10**24)
    pos=[(F(r*n),r) for r,n in d.items() if n>0]
    neg=[(F(-r*n),r) for r,n in d.items() if n<0]
    pl,pu=b.oracle.pressure(pos,49,bb);nl,nu=b.oracle.pressure(neg,49,bb)
    lo,hi=pl-nu-saving,pu-nl-saving
    return {'target':str(k),'exponent':str(bb),'centres_granted':centres,
            'source_path':[r for r in (u-1,17-u) if r],
            'target_path':[r for r in (w,16-w) if r],
            'ordinary_selected_centre_path':[r for r in (u,17-u) if r],
            'private_return_rank':u-w,'private_rank_saved':saving,
            'per_stage_histogram_delta':{str(r):n for r,n in sorted(d.items())},
            'm49_margin_loss_per_stage':b.interval(lo,hi),
            'all_arity_sign':'WORSE' if lo>0 else 'BETTER' if hi<0 else 'UNRESOLVED'}

def setup():
    roots,fourth=e.e8_shells();z=np.zeros_like(fourth)
    pure=np.concatenate([np.concatenate([fourth,z],axis=1),np.concatenate([z,fourth],axis=1)])
    mixed=np.concatenate([np.repeat(roots,240,axis=0),np.tile(np.repeat(roots,2,axis=0),(120,1))*np.tile([1,-1],14400)[:,None]],axis=1)
    ports=np.concatenate([pure,mixed]);_,packed,_=e.binary_labels(roots,ports)
    assert ports.shape==(30960,16)
    return roots,fourth,ports,packed

def main():
    roots,fourth,ports,packed=setup()
    source=json.loads((PRE/'SCREEN.json').read_text());rows=[]
    for prior in source['rows']:
        normal=np.array(prior['normal'],dtype=np.int64)
        character=(ports.astype(np.int64)@normal//4)&1
        ids=np.flatnonzero(character==prior['support_character'])
        geo=geometry(packed,ids);assert geo['ports']==prior['support_count']
        g=prior['supported_cubic_dimension_upper']
        records=[]
        for w in sorted({0,geo['radical_rank']}):
            records.extend(dict(delta_invoice(geo,g,w,k),target_radical_visit=w) for k in map(F,('.002','.003','.005')))
        rows.append({'normal_index':prior['normal_index'],'normal':prior['normal'],
                     'support_character':prior['support_character'],'geometry':geo,
                     'rational_supported_dimension_upper':g,'prices':records})
    # New, small-support cubics from root-pairing filters.  These do not
    # inherit an isolated coefficient factor merely because they are cubic.
    rr=np.r_[roots[0],np.zeros(8,dtype=np.int64)]
    linear=ports.astype(np.int64)@rr
    unary=linear*(linear*linear-16)
    candidates=[]
    for name,values,granted in [('root_unary_filter',unary[:,None],1)]:
        ids=np.flatnonzero(np.any(values,axis=1));geo=geometry(packed,ids)
        prices=[dict(delta_invoice(geo,granted,w,k),target_radical_visit=w)
                for w in sorted({0,geo['radical_rank']}) for k in map(F,('.002','.003','.005'))]
        candidates.append({'name':name,'definition':'l(p)*(l(p)^2-16), l(p)=p dot (root0,0)',
                           'geometry':geo,'centres_granted':granted,'prices':prices})
    assert all(z['all_arity_sign']=='WORSE' for x in rows for z in x['prices'])
    assert all(z['all_arity_sign']=='WORSE' for x in candidates for z in x['prices'])
    out={'status':'PASS_SCOPED_COMPLETE_OWN_VISIT_COST_OBSTRUCTIONS_NO_NEW_KAPPA',
         'pin':b.PIN,'source_screen_sha256':hashlib.sha256((PRE/'SCREEN.json').read_bytes()).hexdigest(),
         'source_hashes':{str(REPO/'research/niemeier-lattices/code/e8_cubed.py'):hashlib.sha256((REPO/'research/niemeier-lattices/code/e8_cubed.py').read_bytes()).hexdigest(),
                          str(OLD/'optimistic_budget.py'):hashlib.sha256((OLD/'optimistic_budget.py').read_bytes()).hexdigest()},
         'hyperplane_rows':rows,'smaller_support_candidates':candidates,
         'proof':'The complete differential has rank mass -saving and unchanged ordinary role count/stock/pads. Hence Delta(pressure-D)/L = m^b sum_r DeltaH_r r^(1-b), whose sign is independent of m>0. Exact positive-series bounds at m49 prove each displayed sign for every arity.',
         'assumptions':'New own source visits on the entire declared support union; common gather U, optional common target radical W, monotone ordinary paths, one private U-to-W return per isolated centre, same total816 K centres. Free compatible coefficient extraction and zero scalar lowering cost are granted.',
         'limits':'Full hyperplane supports only, plus the one displayed unary filter. The sampled modular nullity gives only a rational upper bound. No arbitrary smaller union, changed coefficient factor, shared visits, nonmonotone source contract, full H6 network, precision/native/owner or kappa implication.'}
    (HERE/'SCREEN.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(out['status'])
    for x in rows:
        print(x['normal_index'],x['support_character'],x['geometry']['ports'],'U',x['geometry']['U_rank'],'rad',x['geometry']['radical_rank'],'g<=',x['rational_supported_dimension_upper'],[(z['target_radical_visit'],z['m49_margin_loss_per_stage']['lo']) for z in x['prices'] if z['target']=='1/500'])
    for x in candidates:print(x['name'],x['geometry'])

if __name__=='__main__':main()
