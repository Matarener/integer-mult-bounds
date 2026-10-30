#!/usr/bin/env python3
"""Independent literal-circuit and invoice checks of retained exact kernels."""
from pathlib import Path
import hashlib,json,sys
sys.dont_write_bytecode=True
import kernel_exact as p
HERE=Path(__file__).resolve().parent
def compile_actual(e,m):
    op=p.ce.ident(m)
    for gate in e['one_coordinate_literal_circuit']:
        k=gate[0]
        if k=='P':g=p.ce.perm(m,gate[1])
        elif k=='D':g=p.ce.diag(m,gate[1],gate[2])
        elif k=='X':g=p.ce.xgate(m,gate[1])
        elif k=='C':g=p.ce.cgate(m,gate[1],gate[2])
        elif k=='phase':g=p.phase(m,gate[1])
        else:raise ValueError(k)
        op=op.then(g)
    p.need(op.tab==tuple(tuple(t)for t in e['one_coordinate_tableau']),'serialized actual signed tableau')
    p.need(p.ce.rank(x for x,z,_ in op.tab[m:])==e['rank_per_f'],'serialized native rank')
    return op

def run():
    normal=(HERE/'EXACT-FIXTURES.json').read_bytes();p.need(normal==(HERE/'EXACT-FIXTURES-OPTIMIZED.json').read_bytes(),'normal/-O exact fixtures identical')
    data=json.loads(normal);unique={};rows=[]
    for case in data['fixtures']:
        for kind in('default','isolated'):
            f=case[kind];m=f['ambient_arity'];hist={}
            for e in f['events']:
                if e['kind']=='NATIVE':hist[str(e['rank_per_f'])]=hist.get(str(e['rank_per_f']),0)+1
                if 'one_coordinate_literal_circuit'in e:unique[(m,json.dumps(e['one_coordinate_literal_circuit']))]=e
            p.need(hist==f['histogram']and sum(int(r)*c for r,c in hist.items())==f['mass'],'actual complete event invoice')
            for e in f.get('inverse_events',[]):
                if 'one_coordinate_literal_circuit'in e:unique[(m,json.dumps(e['one_coordinate_literal_circuit']))]=e
        x=case['invoice'];q=x['q'];t,u=x['J_rank'],x['Jbar_rank'];p.need(x['mass']==case['isolated']['mass']and x['D_optimistic']<=0,'complete failed screen')
        p.need(x['L_rank']==4*q-4 and x['R_rank']<=(q-1)*u+2*(q-2),'actual transport rank inequalities')
        rows.append({'kernel':case['kernel'],'q':q,'J_rank':t,'Jbar_rank':u,'parent_arity':x['parent_arity'],'mass':x['mass'],'stock':x['optimistic_stock']})
    for(m,_),e in unique.items():
        op=compile_actual(e,m)
        for combined in(op.then(op.adjoint()),op.adjoint().then(op)):
            p.need(combined.tab==p.ce.identity(m),'actual circuit inverse signed tableau')
            col,den=p.b.sparse_column(combined);p.need(col=={0:(1,0)}and den==0,'actual circuit inverse Gaussian phase')
    return {'fixtures':rows,'distinct_literal_circuit_inverse_pairs':len(unique),'normal_optimized_fixture_bytes_identical':True,'all_full_default_original_columns_and_both_inverse_orders_checked_by_producer':True,'changed_all_input_proof':'complete current n-by-n isolated defect plus exact free word V=L U^-1 R','selected_changed_native_recipes':False,'no_new_kappa':True}

if __name__=='__main__':
    out=run();dest='VALIDATION.json'if __debug__ else'VALIDATION-OPTIMIZED.json';(HERE/dest).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,sort_keys=True))
