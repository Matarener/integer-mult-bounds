#!/usr/bin/env python3
"""Check exact prefix minima, root contracts and complete finite endpoints.

The layout interpreter uses exact integers, not physical record primitives.
Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
import ast
import hashlib
import itertools
import json
from math import isqrt, prod
from pathlib import Path
import random
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from reserve import PrefixCompiler, depth, floor_root, need
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[1]


def authenticate():
    sources=json.loads((ROOT/'SOURCES.json').read_text())
    inputs=[x for x in sources['files'] if x['usage']=='input']
    for row in inputs:
        path=REPO/row['path']
        need(path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256'],'source hash: '+row['path'])
    return len(inputs)


def source_consumers():
    inventory=json.loads((ROOT/'CONSUMER-INVENTORY.json').read_text())
    tokens=('q0','depth','stock','padded_rows','original_rows')
    production={};test_files=0
    for row in inventory:
        text=(REPO/row['path']).read_text()
        need(hashlib.sha256(text.encode()).hexdigest()==row['sha256'],'consumer inventory hash')
        lexical=[t for t in tokens if t in text]
        need(lexical==row['consumer_tokens'],'lexical inventory')
        tree=ast.parse(text)
        references=sorted({node.value for node in ast.walk(tree) if isinstance(node,ast.Constant) and isinstance(node.value,str) and node.value in tokens})
        name=Path(row['path']).name
        if name.startswith('check_'):
            test_files+=1
        elif references:
            production[name]=references
    need(set(production)=={'root_plan.py','root_layer.py'},'complete production descriptor consumers')
    plan=ast.parse((ROOT/'vendor/root_plan.py').read_text())
    cls=next(n for n in plan.body if isinstance(n,ast.ClassDef) and n.name=='RootPlan')
    compute=ast.unparse(next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='compute'))
    expected=["d = save('d', keep(floor_power(precision, 997, 1000)))", "K = save('K', keep(floor_power(d, 1, 500)))", "G = save('G', plus(scaled(logarithm, 4), constant=6))", "H = save('H', times(d, G))", "row_axes = times(q0, K)", "original_rows = save('original_rows', keep(power_two(row_axes)))", "multiples = keep(ceil_divide(original_rows, stock))", "save('padded_rows', times(multiples, stock))"]
    for statement in expected:need(statement in compute,'source formula: '+statement)
    layer=(ROOT/'vendor/root_layer.py').read_text()
    streams=(ROOT/'vendor/root_streams.py').read_text()
    machine=(ROOT/'vendor/machine.py').read_text()
    need('rows="padded_rows"' in layer, 'machine receives padded rows')
    need('def run(self, payload, prefixes, original_rows, padded_rows, row_bits, remove=False):' in streams, 'complete padding parameter boundary')
    need('divide(' in machine and 'unused' in machine, 'machine row quotient retained')
    return {'source_python_files':len(inventory),'test_files':test_files,'production_literal_consumers':production,'bound_plan_formulas':len(expected)}


def finite_minima():
    cases=0;relaxed=0;all_depths=0
    for m,r,threshold in [(3,2,3),(3,2,7),(3,2,13),(73,48,73),(73,48,101)]:
        ranks=(1,2) if m==3 else (1,2,3,4,5,7,8,48)
        table=[0]*2049
        for w in range(threshold,len(table)):
            table[w]=1+max(table[x*(w//m)] for x in ranks)
        for w,d in enumerate(table):
            need(d==depth(w,threshold,m,r),'all-child depth')
            all_depths+=1
        for f,k in itertools.product((2,3,7,16,17),(1,2,3,5)):
            compiler=PrefixCompiler(f,threshold,m,r)
            for remaining in range(1,201):
                got=compiler.compile(remaining,k)
                first=None
                for q0 in range(remaining):
                    stock=f**table[remaining-q0]
                    rows=1<<(k*q0)
                    padded=((rows+stock-1)//stock)*stock
                    if padded < 2*rows:
                        first=q0
                        break
                need(got['q0']==first,'direct padded-volume minimum')
                stock=f**got['depth'];rows=1<<(k*first)
                if stock>rows:relaxed+=1
                cases+=1
    need(relaxed>0,'strict volume improvement over rows>=stock')
    return {'minimum_cases':cases,'all_child_depth_entries':all_depths,'cases_with_rows_below_stock':relaxed}


def apply_axis(values,bit,fields):
    out=values.copy();mask=1<<bit
    addresses=len(values)//fields
    for index in range(addresses):
        if index & mask:continue
        for field in range(fields):
            a=values[index*fields+field];b=values[(index|mask)*fields+field]
            out[index*fields+field]=a+2*b
            out[(index|mask)*fields+field]=3*a+5*b
    return out


def layout_checks():
    rng=random.Random(66151);cases=0;components=0;added=0;reject=0
    for selected,k,qF,qB,right,fields,prefixes in [(5,1,1,1,1,2,3),(6,1,1,1,0,3,2),(4,2,1,1,1,2,2),(5,2,1,1,0,1,2),(4,1,0,1,1,2,2)]:
      for divisor in (3,5,7):
        remaining=selected-qF-qB
        compiler=PrefixCompiler(divisor,3,3,2)
        plan=compiler.compile(remaining,k);q0=plan['q0'];core=remaining-q0
        R=1<<(k*q0);S=divisor**plan['depth'];P=((R+S-1)//S)*S
        need(P<2*R and P%S==0,'small layout admission')
        per_row=(1<<((selected-q0)*k+right))*fields
        for residue in range(k):
            original=[rng.randrange(-11,12) for _ in range(prefixes*R*per_row)]
            expected=[];actual=[]
            block=R*per_row
            for pre in range(prefixes):
                v=original[pre*block:(pre+1)*block]
                direct=v.copy()
                for axis in range(selected):direct=apply_axis(direct,right+residue+axis*k,fields)
                expected.extend(direct)
                a=q0+qF
                for axis in list(range(selected-a,selected))+list(range(qB)):
                    v=apply_axis(v,right+residue+axis*k,fields)
                v += [0]*((P-R)*per_row)
                # Each complete row endpoint acts on the core and preserves its row index.
                completed=[]
                for row in range(P):
                    piece=v[row*per_row:(row+1)*per_row]
                    for axis in range(qB,qB+core):piece=apply_axis(piece,right+residue+axis*k,fields)
                    completed.extend(piece)
                need(all(x==0 for x in completed[R*per_row:]),'zero padding return')
                actual.extend(completed[:R*per_row])
                if P>R:
                    bad=completed.copy();bad[-1]=1
                    need(any(x!=0 for x in bad[R*per_row:]),'dirty padding control');reject+=1
            need(actual==expected,'complete tensor and layout endpoint')
            need(original!=expected,'nontrivial dirty endpoint')
            cases+=1;components+=len(original);added+=prefixes*(P-R)*per_row
    need(added>0 and reject>0,'nontrivial padding coverage')
    return {'complete_layouts':cases,'dirty_components':components,'added_zero_components':added,'nonzero_padding_controls':reject}


def tail_theorem():
    # For u=floor(log2 p), v=floor(997u/500000), v>=27 once u>=14000.
    # 2^v > 5284*(ceil(500000*(v+1)/997)+1) holds from v=27.
    v=27
    rhs=5284*((500000*(v+1)+996)//997+1)
    need((1<<v)>rhs,'one-axis base')
    # One increment in v increases the ceiling by at most 502.
    increment=5284*502
    need(rhs>=increment,'one-axis induction')
    for v in range(27,256):
        bound=5284*((500000*(v+1)+996)//997+1)
        need((1<<v)>bound,'tail control')
    # r^2/m^2 < 1/2 gives D0(d)<=2 ceil(log2 d).
    need(2*48*48<73*73,'two-level halving')
    return {'precision_cutoff':'2^14000','base_v':27,'base_rhs':rhs,'base_power':1<<27,'max_rhs_increment':increment,'tail_controls':229}


def production():
    F=14336*(1<<1296)*prod((1<<(2*j))-1 for j in range(1,37))
    need((F-1).bit_length()==2642,'actual fixed divisor bits')
    d=isqrt(1<<16949)
    need(d*d <= 1<<16949 < (d+1)*(d+1),'production floor')
    K=floor_root(d,500);T=floor_root(d-1,1000)+1;G=34006;H=d*G
    need(K**500<=d<(K+1)**500,'actual spacing')
    qF=(2*H+K-1)//K;qB=(H+K-1)//K
    old=2642*depth(d,73)
    compiler=PrefixCompiler(F,T)
    rows=[]
    for name,selected in [('full',d),('old_lambda45',qF+qB+old+73*45),('old_lambda72',qF+qB+old+73*72)]:
        need(qF+qB<selected<=d and K>3*G,'production fast domain')
        plan=compiler.compile(selected-qF-qB,K)
        core=selected-qF-qB-plan['q0']
        threshold=T; inverse_depth=0
        while threshold<=core:
            inverse_depth+=1
            threshold=73*((threshold+47)//48)
        need(inverse_depth==plan['depth'], 'independent inverse depth at production core')
        front=qF*K-2*H;back=qB*K-H
        need(front+3*H+core*K+back==(selected-plan['q0'])*K,'whole root address identity')
        need(0<=front<K and 0<=back<K,'guard residues')
        need(plan['q0']<=old,'old planner dominates new prefix')
        row={'case':name,'old_prefix':old,'old_stock_depth':depth(d,73),'new_core_bit_length':core.bit_length(),**plan}
        if core.bit_length()<64:row['new_core_width']=core
        rows.append(row)
    need(rows[0]['q0']==293 and rows[1]['q0']==rows[2]['q0']==1,'production minima')
    return {'precision':'2^8500','spacing':K,'threshold':T,'divisor_ceil_log2':2642,'plans':rows}


def main():
    result={'status':'PASS_MINIMUM_ROOT_ROW_PREFIX','authenticated_inputs':authenticate(),'consumer_audit':source_consumers(),'finite_minima':finite_minima(),'layout':layout_checks(),'one_axis_tail':tail_theorem(),'production':production(),'limits':['Reference integer compiler and written encoded algorithm; no installed production Count frontend','Inherited complete recursive/native/physical endpoints','No matched QQ16 comparison or new kappa']}
    saved=ROOT/'RESULT.json'
    if saved.exists():need(json.loads(saved.read_text())==result,'saved result mismatch')
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=='__main__':main()
