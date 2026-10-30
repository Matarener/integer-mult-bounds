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
    mod=types.ModuleType('dyadic_block_authenticated');mod.__file__=str(HERE/'compiler.py')
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

def independent_rank(matrix):
    A=[[Q(x)for x in row]for row in matrix];m,n=len(A),len(A[0]);r=0
    for j in range(n):
        i=next((i for i in range(r,m)if A[i][j]),None)
        if i is None:continue
        A[r],A[i]=A[i],A[r];q=A[r][j];A[r]=[x/q for x in A[r]]
        for i in range(r+1,m):
            q=A[i][j];A[i]=[x-q*y for x,y in zip(A[i],A[r])]
        r+=1
        if r==m:break
    return r

def check_factor(M,U,V):
    m,n=len(M),len(M[0]);r=len(V)
    need(len(U)==m and all(len(row)==r for row in U),'Left dimensions')
    need(all(len(row)==n for row in V),'Right dimensions')
    need(r==independent_rank(M),'Independent rational rank')
    for row in U+V:
        for x in row:B.dyadic(x)
    need(all(Q(M[i][j])==sum((U[i][k]*V[k][j]for k in range(r)),Q(0))for i in range(m)for j in range(n)),'Factor product')

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
        else:
            need(e[0]=='add','Known opcode');a,b=tuple(e[1]),tuple(e[2])
            need(a!=b and a in rows and b in rows,'Distinct valid roles')
            q=B.dyadic(Q(e[3],e[4]));need(q!=0,'Nonzero ADD')
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

def verify():
    inputs=authenticated_sources()
    src=next(v for k,v in inputs.items()if k.endswith('-NATIVE.json.gz'));words=json.loads(gzip.decompress(src))
    price=source_pricer(next(v for k,v in inputs.items()if k.endswith('/rebuild_native.py')))
    results=[];columns=0;intervals=[]
    for case in read('CASES.json'):
        M,window,indices=source_matrix(words,case,False);f=B.compile_block(M,0);check_factor(M,f['left'],f['right'])
        need(all(x.denominator==1 for row in f['right']for x in row),'Integral right factor')
        need(f['rank']==case['rank'] and f['owned_peak']==1 and not f['conditional_paid'],'Complete local interface')
        forward=plan_price(f['program'],price);old=sum(price(e[1])for e in window);coalesced=sum(price(['add',['Y',i],['X',j],x.numerator,x.denominator])for i,row in enumerate(M)for j,x in enumerate(row)if x)
        need(old==coalesced==case['old'] and forward==case['new']<old,'Gain beyond repeated-edge coalescing, including all clears')
        columns+=check_semantics(M,f['program'],True)
        U,V=B.dual_factor(f['left'],f['right']);dual=B.emit_factor(U,V,0)
        DM,dwindow,dindices=source_matrix(words,case,True);check_factor(DM,U,V);columns+=check_semantics(DM,dual['program'],True)
        need(plan_price(dual['program'],price)==forward and sum(price(e[1])for e in dwindow)==old,'Both inverse-transpose allowance bills')
        for lo,hi in intervals:need(indices[1]<lo or hi<indices[0],'Disjoint source replacement windows')
        intervals.append(indices)
        results.append({'phase':case['phase'],'ordinals':[case['first_ordinal'],case['last_ordinal']],'forward_source_indices':indices,'backward_source_indices':dindices,'shape':[len(M),len(M[0])],'rank':f['rank'],'old_scalar_allowance':old,'new_scalar_allowance':forward,'saving':old-forward,'compiled_forward':f['program'],'compiled_backward':dual['program']})
        bad=[e[:]for e in f['program']];bad.pop(0);rejects(lambda:check_semantics(M,bad,True),'omit initial clear')
        bad=[e[:]for e in f['program']];bad.pop();rejects(lambda:check_semantics(M,bad,True),'omit final clear')
    need(sum(r['old_scalar_allowance']for r in results)==766 and sum(r['new_scalar_allowance']for r in results)==698,'Complete four-case scalar allowance')
    rng=random.Random(20261022)
    for _ in range(200):
        m,n=rng.randrange(1,7),rng.randrange(1,7);M=[[Q(rng.randrange(-5,6),2**rng.randrange(4))for _ in range(n)]for _ in range(m)]
        f=B.compile_block(M,0);check_factor(M,f['left'],f['right']);need(all(x.denominator==1 for row in f['right']for x in row),'Integral random right factor');check_semantics(M,f['program'],f['owned_peak'])
    odd=B.compile_block([[3,1],[6,2]],0);check_factor([[3,1],[6,2]],odd['left'],odd['right']);need(odd['rank']==1,'Odd-pivot rank')
    rejects(lambda:B.factor([[Q(1,3)]]),'illegal third')
    badU=[[x for x in row]for row in odd['left']];badU[0][0]+=1
    rejects(lambda:check_factor([[3,1],[6,2]],badU,odd['right']),'false factor')
    changed=dict(read('CASES.json')[0]);changed['first_ordinal']+=1
    rejects(lambda:source_matrix(words,changed,False),'shift source selector')
    return B.encode({'status':'PASS_DYADIC_SOURCE_BLOCK_COMPILER','source_cases':results,'local_columns_both_orientations':columns,'random_factor_and_program_cases':200,'old_allowance_per_orientation':766,'new_allowance_per_orientation':698,'saving_per_orientation':68,'additional_owned_fields':1,'new_recursive_calls':0,'productive_temporary_credit':0,'new_kappa':False})

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();result=verify()
    if args.write:(HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    else:need(result==read('RESULT.json'),'Deterministic semantic receipt')
    print(json.dumps({k:v for k,v in result.items()if k!='source_cases'},sort_keys=True))
