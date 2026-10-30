"""Check the source boundary and the cost of identity-native coframe words.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
Retain all source and compiler notices under inputs/.
"""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import gzip
import importlib.util
import json
import sys

R=Path(__file__).resolve().parent


def need(ok,message):
    if not ok:raise ValueError(message)


def rank(vectors):
    pivots={}
    for x in vectors:
        while x:
            bit=x.bit_length()-1
            if bit in pivots:x^=pivots[bit]
            else:pivots[bit]=x;break
    return len(pivots)


def symp(x,y,n):
    mask=(1<<n)-1
    return ((x&mask)&(y>>n)).bit_count()%2 ^ (((y&mask)&(x>>n)).bit_count()%2)


def span(basis):
    result=[0]
    for b in basis:result += [x^b for x in result]
    return frozenset(result)


def lagrangians(n):
    found={}
    for basis in combinations(range(1,1<<(2*n)),n):
        if all(not symp(x,y,n) for x,y in combinations(basis,2)) and rank(basis)==n:
            found.setdefault(span(basis),basis)
    return list(found.values())


def metric_checks():
    reports=[]
    for n in (1,2,3):
        lags=lagrangians(n);expected=1
        for i in range(1,n+1):expected*=2**i+1
        need(len(lags)==expected,'Complete small Lagrangian domain')
        distances=[[rank(a+b)-n for b in lags] for a in lags]
        for i,row in enumerate(distances):
            need(row[i]==0 and all((i==j)==(d==0) for j,d in enumerate(row)),'Metric separation')
            for j,d in enumerate(row):
                need(d==distances[j][i],'Metric symmetry')
                need(all(d<=row[k]+distances[k][j] for k in range(len(lags))),'All metric triangles')
        reports.append(dict(axes=n,lagrangians=len(lags),triangles=len(lags)**3))
    # A separate group enumeration checks the upper-right block rank convention.
    matrices=[]
    for x in range(1,16):
        for z in range(1,16):
            if not symp(x,z,2):continue
            rest=[u for u in range(1,16) if not symp(u,x,2) and not symp(u,z,2)]
            for y in rest:
                for w in rest:
                    if symp(y,w,2):matrices.append((x,y,z,w))
    need(len(matrices)==len(set(matrices))==720,'Complete Sp(4,2)')
    def action(cols,v):
        out=0
        for i,c in enumerate(cols):
            if v>>i&1:out^=c
        return out
    tables=[[action(m,v) for v in range(16)]for m in matrices]
    inverses=[]
    for table in tables:
        inv=[0]*16
        for i,v in enumerate(table):inv[v]=i
        inverses.append(inv)
    grades=[rank([m[2]&3,m[3]&3])for m in matrices];counter=Counter(grades);orientation_controls=0
    for i,a in enumerate(matrices):
        for j,b in enumerate(matrices):
            product=[tables[i][v]for v in b];grade=rank([product[2]&3,product[3]&3])
            need(grade<=grades[i]+grades[j],'Gaussian rank product subadditivity')
            # For B A^-1, use inverse-image coframes A^-1 Z and B^-1 Z.
            transition=[tables[j][inverses[i][1<<k]] for k in range(4)]
            actual=rank([transition[2]&3,transition[3]&3])
            inverse_distance=rank([inverses[i][4],inverses[i][8],inverses[j][4],inverses[j][8]])-2
            need(actual==inverse_distance,'Inverse-image physical coframe convention')
            wrong=rank([a[2],a[3],b[2],b[3]])-2
            orientation_controls+=actual!=wrong
    need(counter=={0:48,1:288,2:384} and orientation_controls>0,'Separate ranks and wrong-orientation controls')
    return dict(lagrangian_domains=reports,symplectic_matrices=720,products=720**2,
                rank_histogram=dict(sorted(counter.items())),wrong_image_convention_rejected=orientation_controls)


def owner(role):
    need(role[0] in ('L','C'),'Declared role kind')
    return role[1]+(632 if role[0]=='C' else 0)


def source_check(c,program,back):
    dimensions=[len(f)for f in c['frames']];state=c['start'][:]+[None]
    rows=[{i:F(1)}for i in range(632)]+[{}];paths=[[]for i in range(632)];centers=[];adapters=[];zero_original_queries=[];zero_centre_queries=[]
    for index,e in enumerate(program):
        op=e[0]
        if op=='scalar':
            g,f=e[1:];d=owner(g[1])
            if g[0]=='clear':
                need(d==632,'No original CLEAR or zero-header reset');rows[d]={};state[d]=f
            else:
                need(state[d]==f,'Actual scalar destination frame')
                if g[0] in ('add','copy'):
                    s=owner(g[2]);need(state[s]==f,'Actual common source frame')
                    if g[0]=='copy':need(d==632,'No original overwrite');rows[d]=rows[s].copy()
                    else:
                        need(d!=s,'Distinct scalar operands');a=F(g[3],g[4])
                        for k,v in rows[s].items():
                            rows[d][k]=rows[d].get(k,F(0))+a*v
                            if not rows[d][k]:del rows[d][k]
                else:
                    need(g[0]=='scale','Known scalar opcode');a=F(g[2],g[3]);need(a!=0,'No original destructive scale')
                    rows[d]={k:a*v for k,v in rows[d].items()}
        elif op=='warp':
            _,role,g,a,b=e;d=owner(role)
            need(state[d]==a and dimensions[a]==dimensions[b],'Identity native warp preserves coframe dimension');state[d]=b
        elif op in ('climb','center'):
            if op=='climb':_,_,d,a,b,k=e
            else:_,d,a,b,k=e;d+=632
            need(state[d]==a,'Literal transport continuity');state[d]=b
            if not rows[d]:(zero_original_queries if d<632 else zero_centre_queries).append(index)
            if d<632:paths[d].append((dimensions[a],dimensions[b]))
            else:centers.append((dimensions[a],dimensions[b]))
        elif op=='adapter':adapters.append(e)
        else:need(op=='phase','Known metadata record')
    need(state[:632]==c['final'] and rows[632]=={},'All final frames and owned return')
    for i,row in enumerate(rows[:632]):
        expected={i:F(1)}
        if back and i<112:expected[i+112]=F(-1)
        if not back and 112<=i<224:expected[i-112]=F(1)
        need(row==expected,'All identity-native original columns')
    need(Counter((e[1],e[2])for e in adapters)==Counter((kind,i)for kind in ('old_to_new','new_to_old')for i in range(224)),'All main boundary normalizers are present')
    need(len(centers)==8 and all(set(edge)=={0,8}for edge in centers),'Eight charged centre transitions')
    need(not zero_original_queries and not zero_centre_queries,'No literal whole-zero query omission escapes the bound')
    need(all((dimensions[c['start'][i]],dimensions[c['final'][i]])==((1,9)if i<112 else(0,8))for i in range(224)),'All224 actual main endpoint pairs')
    for i,path in enumerate(paths):
        current=dimensions[c['start'][i]]
        for a,b in path:need(current==a,'Persistent field dimension path');current=b
        need(current==dimensions[c['final'][i]],'Path reaches actual endpoint')
    return dict(direction='backward'if back else'forward',events=len(program),original_columns=632,
                independent_helpers=408,main_normalizers=len(adapters),centre_transports=len(centers),zero_original_queries=zero_original_queries,zero_centre_queries=zero_centre_queries),paths,centers


def coordinate_checks(c,paths,centers):
    # These are corroborating choices, not an optimization search.
    reports=[]
    for shift in range(9):
        order=list(range(shift,9))+list(range(shift));masks=[0]+[sum(1<<i for i in order[:d])for d in range(1,10)]
        masks[1]=1;masks[8]=510;masks[9]=511
        dims=[len(f)for f in c['frames']]
        paid=Counter((masks[a]^masks[b]).bit_count()for path in paths for a,b in path)
        paid.update((masks[a]^masks[b]).bit_count()for a,b in centers);paid.pop(0,None)
        targets=Counter((masks[dims[a]]^masks[dims[b]]).bit_count()for a,b in zip(c['start'][224:],c['final'][224:]));targets.pop(0,None)
        for i,path in enumerate(paths):
            ranks=[(masks[a]^masks[b]).bit_count()for a,b in path]
            endpoint=(masks[dims[c['start'][i]]]^masks[dims[c['final'][i]]]).bit_count()
            need(sum(ranks)>=endpoint,'Every actual field path pays its endpoint')
        need(targets=={4:28,7:1,8:47,9:332},'Actual two-sided changed helper targets')
        deficit=sum(k*n for k,n in paid.items())-sum(k*n for k,n in targets.items())
        need(deficit>=232*8,'Complete rank-mass deficit')
        reports.append(dict(shift=shift,paid=dict(sorted(paid.items())),targets=dict(sorted(targets.items())),rank_mass_deficit=deficit))
    # The old final dimension alone misprices 50 helpers in this source.
    incorrect=Counter(len(c['frames'][f])for f in c['final'][224:])
    need(incorrect!=targets,'Final-dimension-only target control')
    return reports


def run():
    pins=json.loads((R/'INPUTS.json').read_text())
    for p in pins:need(sha256((R/p['local']).read_bytes()).hexdigest()==p['sha256'],'Frozen input '+p['local'])
    word=json.loads(gzip.decompress((R/'inputs/WORD.json.gz').read_bytes()));c=word['canonical']
    spec=importlib.util.spec_from_file_location('credited_coframe_source',R/'inputs/native_core.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
    reports=[];fixtures=[];free=[]
    for name in ('forward','backward'):
        program=word['programs'][name];back=name=='backward'
        rows,paid,norm=old.replay(c,program,back)
        need(all(rows[i]==old.expected(i,back)for i in range(632)),'Retained full free-group endpoint')
        free.append(dict(direction=name,paid=dict(sorted(paid.items())),maxnorm=str(norm)))
        report,paths,centers=source_check(c,program,back);reports.append(report);fixtures.append(coordinate_checks(c,paths,centers))
    negative=[]
    for label,mutate in [('missing_main_adapter',lambda p:p.pop(next(i for i,e in enumerate(p)if e[0]=='adapter'))),
                          ('original_clear',lambda p:p.insert(0,['scalar',['clear',['L',0]],c['start'][0]])),
                          ('missing_centre',lambda p:p.pop(next(i for i,e in enumerate(p)if e[0]=='center'))),
                          ('changed_scalar_frame',lambda p:p[next(i for i,e in enumerate(p)if e[0]=='scalar'and e[1][0]=='add')].__setitem__(2,1))]:
        p=json.loads(json.dumps(word['programs']['forward']));mutate(p)
        try:source_check(c,p,False)
        except ValueError:negative.append(label)
        else:raise ValueError('Source mutation accepted '+label)
    metric=metric_checks()
    return dict(status='PASS_IDENTITY_NATIVE_COFRAME_COST_OBSTRUCTION',source=reports,retained_free_group=free,
                metric=metric,coordinate_fixtures=fixtures,rejected_controls=negative,
                theorem=dict(exponents='0<t<=1',paid_minus_changed_helper_moment_lower_bound='232*8^t',
                             main_paths=224,centre_transports=8,rank_mass_deficit_lower_bound=1856,
                             scope='Identity logical native generators, continuous exact coframe transports on every retained original, all helper grades debited and replaced, and no original clear or free zero-only header jump.',
                             excluded='Nonidentity native generators, charged changed ownership/zero-receiver operations, arbitrary callers not satisfying this contract, and a global multiplication lower bound.'))


def main():
    result=json.loads(json.dumps(run()))
    if '--write' in sys.argv:(R/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:need(result==json.loads((R/'RESULT.json').read_text()),'Exact published result')
    print(result['status'])


if __name__=='__main__':main()
