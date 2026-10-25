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
    data=(HERE/'compiler.py').read_bytes()
    mod=types.ModuleType('borrowed_rankone_authenticated');mod.__file__=str(HERE/'compiler.py')
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

def check_no_scratch(program):
    for e in program:
        need(e[0] in ('add','scale'),'No clear, copy or recursive opcode')
        roles=e[1:3] if e[0]=='add' else e[1:2]
        need(all(r[0] in ('X','Y') for r in roles),'Only original persistent fields')

def verify():
    inputs=authenticated_sources();words=json.loads(gzip.decompress(next(v for k,v in inputs.items() if k.endswith('-NATIVE.json.gz'))))
    price=source_pricer(next(v for k,v in inputs.items() if k.endswith('/rebuild_native.py')))
    results=[];columns=0;intervals=[];new_programs=0
    for case in read('CASES.json'):
        entry={'ordinals':[case['first_ordinal'],case['last_ordinal']],'phase':case['phase'],'orientations':[]}
        for backward in (False,True):
            M,window,indices=source_matrix(words,case,backward);gauge=B.optimize(M);certificate(M,gauge)
            borrowed=B.borrowed_candidates(M);plan=min([gauge]+borrowed,key=lambda x:x['new'])
            one=B.rank_one(M);previous=min([gauge]+([one] if one else []),key=lambda x:x['new'])
            old=sum(price(e[1]) for e in window);need(old==case['old'],'Original source bill')
            need(plan_price(plan['program'],price)==plan['new'],'Complete emitted scalar bill')
            need(plan['owned_peak']==0 and plan['new']<=previous['new'],'No extra field or allowance regression on source cases')
            check_no_scratch(plan['program']);columns+=check_semantics(M,plan['program'],False)
            if plan.get('mechanism','').startswith('borrow-'):
                new_programs+=1
                need(plan['preparation_count']>0,'Nontrivial borrowed adapter')
                if plan['mechanism']=='borrow-source':
                    rejects(lambda:check_semantics(M,plan['program'][:-1],False),'omit borrowed-input restoration')
                else:
                    rejects(lambda:check_semantics(M,plan['program'][1:],False),'omit dirty-target subtraction')
            entry['orientations'].append({'backward':backward,'source_indices':indices,'matrix':M,'old':old,'previous_one_field_allowance':previous['new'],'previous_zero_field_allowance':gauge['new'],'selected':plan,'gauge_certificate':gauge})
            if not backward:
                for lo,hi in intervals:need(indices[1]<lo or hi<indices[0],'Disjoint actual source windows')
                intervals.append(indices)
        need(entry['orientations'][0]['selected']['new']==entry['orientations'][1]['selected']['new'],'Dual source bills')
        results.append(entry)
    total=sum(r['orientations'][0]['selected']['new'] for r in results)
    need(total==666 and new_programs==4,'Constructive four-window allowance')
    need(sum(r['orientations'][0]['previous_one_field_allowance'] for r in results)==674,'Pinned predecessor comparison')
    rng=random.Random(20261022);candidates=0
    for _ in range(100):
        m,n=rng.randrange(1,6),rng.randrange(1,6)
        u=[Q(rng.randrange(-5,6),2**rng.randrange(3)) for j in range(m)]
        v=[Q(rng.randrange(-5,6),2**rng.randrange(3)) for i in range(n)]
        M=[[x*y for y in v] for x in u]
        for plan in B.borrowed_candidates(M):
            check_no_scratch(plan['program']);check_semantics(M,plan['program'],False)
            need(plan_price(plan['program'],price)==plan['new'],'Random exact source bill');candidates+=1
        plan=B.compile_borrowed(M);check_no_scratch(plan['program']);check_semantics(M,plan['program'],False)
    need(not B.borrowed_candidates([[1,0],[0,1]]),'No false rank-one rewrite')
    need(not B.borrowed_candidates([[0,0],[0,0]]),'Zero map uses direct identity')
    # Neither coefficient vector admits a dyadic normalization in this example.
    need(not B.borrowed_candidates([[9,15],[15,25]]),'Reject illegal odd-denominator pivots')
    rejects(lambda:B.compile_borrowed([[Q(1,3)]]),'non-dyadic source')
    changed=dict(read('CASES.json')[1]);changed['first_ordinal']+=1
    rejects(lambda:source_matrix(words,changed,False),'shifted source selector')
    return B.encode({'status':'PASS_BORROWED_RANKONE','source_cases':results,'symbolic_columns_both_orientations':columns,'random_rank_one_matrices':100,'random_borrowed_programs':candidates,'new_borrowed_source_programs':new_programs,'original_allowance_per_orientation':766,'previous_zero_scratch_allowance':686,'previous_one_scratch_allowance':674,'new_zero_scratch_allowance':666,'additional_owned_fields':0,'new_recursive_calls':0,'productive_temporary_credit':0,'new_kappa':False})

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();result=verify()
    if args.write:(HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    else:need(result==read('RESULT.json'),'Deterministic semantic receipt')
    print(json.dumps({k:v for k,v in result.items() if k!='source_cases'},sort_keys=True))
