"""Exact source-bound checks for the dyadic block compiler. Apache-2.0.
Dugongue with substantial OpenAI assistance; no new kappa claim.
"""
from pathlib import Path
from fractions import Fraction as Q
import ast,gzip,hashlib,json,random,sys,types
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def need(ok,why):
    if not ok:raise ValueError(why)

def load_local():
    # Execute the authenticated bytes; do not trust a preexisting bytecode cache.
    data=(HERE/'gauge.py').read_bytes()
    mod=types.ModuleType('unit_gauge_authenticated');mod.__file__=str(HERE/'gauge.py')
    sys.modules[mod.__name__]=mod;exec(compile(data,mod.__file__,'exec'),mod.__dict__)
    return mod

B=load_local()

def read(name):return json.loads((HERE/name).read_text(encoding='utf-8'))

def authenticated_sources():
    out={}
    for row in read('SOURCES.json')['files']:
        if row['usage']=='input':
            data=(ROOT/row['path']).read_bytes()
            need(hashlib.sha256(data).hexdigest()==row['sha256'],'Changed input: '+row['path'])
            out[row['path']]=data
    return out

def transpose(M):return [list(row)for row in zip(*M)]

def state(n,m):
    size=n+m+1
    rows={('X',i):[Q(k==i)for k in range(size)]for i in range(n)}
    rows.update({('Y',j):[Q(k==n+j)for k in range(size)]for j in range(m)})
    rows['T',0]=[Q(k==n+m)for k in range(size)]
    return rows

def execute(program,n,m):
    rows=state(n,m);size=n+m+1
    for e in program:
        if e[0]=='clear':
            need(e[1]==['T',0],'Only owned temporary may be cleared')
            rows['T',0]=[Q(0)]*size
        elif e[0]=='query':
            need(e[1]==['T',0] and e[2]==0,'Source cases use the exact identity query')
        elif e[0]=='scale':
            a=tuple(e[1]);q=Q(e[2],e[3]);need(a in rows and a[0] in ('X','Y') and q>0 and q==B.power(B.valuation(q)),'Legal native SCALE')
            rows[a]=[q*x for x in rows[a]]
        else:
            need(e[0]=='add','Known opcode');a,b=tuple(e[1]),tuple(e[2])
            need(a!=b and a in rows and b in rows,'Distinct valid roles')
            q=Q(e[3],e[4]);B.valuation(q);need(q!=0,'Nonzero ADD')
            rows[a]=[x+q*y for x,y in zip(rows[a],rows[b])]
    return rows

def check_semantics(M,program,owned):
    M=[[Q(x)for x in row]for row in M];m,n=len(M),len(M[0]);actual=execute(program,n,m);original=state(n,m)
    for i in range(n):need(actual['X',i]==original['X',i],'Source column changed')
    for j in range(m):
        wanted=[original['Y',j][k]+sum(M[j][i]*original['X',i][k]for i in range(n))for k in range(n+m+1)]
        need(actual['Y',j]==wanted,'Destination or dirty-owned column mismatch')
    need(actual['T',0]==([Q(0)]*(n+m+1) if owned else original['T',0]),'Owned output condition')
    return n+m+1

def gate_map(program):
    phase=None;counts={};out={}
    for i,e in enumerate(program):
        if e[0]=='phase':phase=e[1]
        if e[0]=='scalar':
            g=e[1];roles=g[1:3]if g[0]in('add','copy')else g[1:2]
            if all(r[0]=='L'for r in roles):
                j=counts.get(phase,0);out[phase,j]=i;counts[phase]=j+1
    return out

def source_matrix(words,case,backward):
    program=words['backward'if backward else 'forward'];mapping=gate_map(program)
    a=mapping[case['phase'],case['first_ordinal']];b=mapping[case['phase'],case['last_ordinal']]
    need(a<=b,'Ordered source window')
    window=program[a:b+1]
    need(len(window)==case['last_ordinal']-case['first_ordinal']+1,'Contiguous actual scalar source window')
    for e in window:
        need(e[0]=='scalar'and e[1][0]=='add'and e[2]==case['frame'],'Only common-chart ADDs, no hidden warp/climb/scale')
        need(all(r[0]=='L'for r in e[1][1:3]),'Only persistent source fields')
    sources=sorted({e[1][2][1]for e in window});targets=sorted({e[1][1][1]for e in window})
    need(not set(sources)&set(targets),'Bipartite source/destination disjointness')
    need(all(0<=r<632 for r in sources+targets),'Original 632-field ABI')
    need(sources==(case['target_roles']if backward else case['source_roles'])and targets==(case['source_roles']if backward else case['target_roles']),'Exact source roles')
    M=[[Q(0)for _ in sources]for _ in targets]
    for e in window:
        g=e[1];M[targets.index(g[1][1])][sources.index(g[2][1])]+=Q(g[3],g[4])
    expected=[[Q(x)for x in row]for row in case['matrix']]
    if backward:expected=[[-x for x in row]for row in transpose(expected)]
    need(M==expected,'Authenticated source coefficients')
    return M,window,[a,b]

def source_pricer(data):
    tree=ast.parse(data.decode('utf-8'))
    node=next(x for x in tree.body if isinstance(x,ast.FunctionDef)and x.name=='primitive_allowance')
    module=ast.Module(body=[node],type_ignores=[]);namespace={'Q':Q,'need':need}
    exec(compile(module,'authenticated primitive_allowance','exec'),namespace)
    return namespace['primitive_allowance']

def plan_price(program,price):
    total=0
    for e in program:
        if e[0]=='query':need(e[2]==0,'No paid source query');continue
        total+=price(e)
    return total

def rejects(action,label):
    try:action()
    except (ValueError,KeyError,IndexError,StopIteration):return
    raise ValueError('Invalid control accepted: '+label)

def certificate(M,r):
    m,n=len(M),len(M[0]);p=[0]+r['source_exponents']+r['target_exponents']
    edges=[(0,i,4,0) for i in range(1,1+n+m)]
    edges += [(1+i,1+n+j,2,-B.valuation(q)) for j,row in enumerate(M) for i,q in enumerate(row) if q]
    flows=r['dual_flows'];need(len(edges)==len(flows),'Certificate size')
    bal=[0]*len(p);dual=primal=0
    for edge,row in zip(edges,flows):
        need(list(edge)==row[:4],'Authenticated dual edge');u,v,c,k=edge;f=row[4]
        need(type(f)==int and -c<=f<=c,'Capacity');bal[u]-=f;bal[v]+=f
        dual-=k*f;primal+=c*abs(p[v]-p[u]-k)
    need(not any(bal) and primal==dual==r['valuation_objective'],'Exact feasible primal-dual equality')
    offset=sum(B.add_cost(q)-2*abs(B.valuation(q)) for row in M for q in row if q)
    need(offset==r['constant'] and offset+primal==r['new'],'Complete scalar objective')

def verify():
    from itertools import product
    inputs=authenticated_sources();words=json.loads(gzip.decompress(next(v for k,v in inputs.items() if k.endswith('-NATIVE.json.gz'))))
    price=source_pricer(next(v for k,v in inputs.items() if k.endswith('/rebuild_native.py')))
    results=[];columns=0;intervals=[]
    for case in read('CASES.json'):
        entry={'ordinals':[case['first_ordinal'],case['last_ordinal']],'phase':case['phase'],'orientations':[]}
        for backward in (False,True):
            M,window,indices=source_matrix(words,case,backward);r=B.optimize(M);certificate(M,r)
            old=sum(price(e[1]) for e in window);need(old==case['old'],'Original source cost')
            need(plan_price(r['program'],price)==r['new'],'Source prices all gauge instructions')
            columns+=check_semantics(M,r['program'],False)
            one=B.rank_one(M);hybrid=one if one and one['new']<r['new'] else r
            need(plan_price(hybrid['program'],price)==hybrid['new'],'Complete hybrid source bill')
            columns+=check_semantics(M,hybrid['program'],bool(hybrid['owned_peak']))
            entry['orientations'].append({'backward':backward,'source_indices':indices,'matrix':M,'old':old,'gauge':r,'hybrid':hybrid})
            if any(e[0]=='scale' for e in r['program']):
                bad=[e[:] for e in r['program']];bad.pop();rejects(lambda:check_semantics(M,bad,False),'omit inverse scale')
            bad=B.encode(r);bad['dual_flows'][0][4]+=1;rejects(lambda:certificate(M,bad),'corrupt flow')
            if hybrid['owned_peak']:
                rejects(lambda:check_semantics(M,hybrid['program'][1:],True),'omit initial clear')
                rejects(lambda:check_semantics(M,hybrid['program'][:-1],True),'omit final clear')
            if not backward:
                for lo,hi in intervals:need(indices[1]<lo or hi<indices[0],'Disjoint source windows')
                intervals.append(indices)
        need(entry['orientations'][0]['gauge']['new']==entry['orientations'][1]['gauge']['new'],'Dual gauge price')
        need(entry['orientations'][0]['hybrid']['new']==entry['orientations'][1]['hybrid']['new'],'Dual hybrid price')
        results.append(entry)
    totals=[sum(r['orientations'][0][k]['new'] for r in results) for k in ('gauge','hybrid')]
    need(totals==[686,674],'Four-block totals')
    rng=random.Random(20261022)
    for _ in range(100):
        m,n=rng.randrange(1,6),rng.randrange(1,6)
        M=[[Q(rng.randrange(-5,6),2**rng.randrange(4)) for i in range(n)] for j in range(m)]
        r=B.optimize(M);certificate(M,r);check_semantics(M,r['program'],False);need(plan_price(r['program'],price)==r['new'],'Random source price')
    # A finite cross-check, not the proof of global optimality.
    for _ in range(10):
        M=[[B.power(rng.randrange(-1,2)) for i in range(3)] for j in range(2)];r=B.optimize(M)
        vals=[[B.valuation(q) for q in row] for row in M]
        best=min(4*sum(abs(x) for x in p)+2*sum(abs(vals[j][i]+p[3+j]-p[i]) for j in range(2) for i in range(3)) for p in product(range(-2,3),repeat=5))
        need(best==r['valuation_objective'],'Bounded exhaustive independent cross-check')
    rejects(lambda:B.optimize([[Q(1,3)]]),'illegal third')
    rejects(lambda:execute([['scale',['X',0],3,1]],1,1),'illegal scale')
    changed=dict(read('CASES.json')[0]);changed['first_ordinal']+=1
    rejects(lambda:source_matrix(words,changed,False),'shifted source selector')
    return B.encode({'status':'PASS_EXACT_UNIT_GAUGES','source_cases':results,'symbolic_columns_both_modes_and_orientations':columns,'random_exact_cases':100,'bounded_exhaustive_cases':10,'old_allowance_per_orientation':766,'previous_rank_factor_allowance':698,'zero_scratch_allowance':686,'one_scratch_hybrid_allowance':674,'new_recursive_calls':0,'productive_temporary_credit':0,'new_kappa':False})

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();result=verify()
    if args.write:(HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    else:need(result==read('RESULT.json'),'Deterministic semantic receipt')
    print(json.dumps({k:v for k,v in result.items() if k!='source_cases'},sort_keys=True))
