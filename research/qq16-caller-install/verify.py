#!/usr/bin/env python3
"""Whole source-bound caller composition and typed read-only receipts.
Chris R / Clear1nsight, substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse,json,subprocess,sys,types
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
import runtime
A=runtime.module('qq16_auth',HERE/'auth.py');need=A.need
STATUS='PASS_QQ16_ACTUAL_CALLER_INSTALLATION_CONTRACT'
NAMES=('RESULT.json','COMPILATION.json','BILL.json','EXECUTION.json')

def physical(name,mode=None):
    cmd=[sys.executable,'-I']
    if sys.flags.optimize:cmd+=['-O']
    cmd+=['-Werror','-B',str(HERE/name)]
    if mode:cmd+=[mode]
    p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,timeout=180)
    need(p.returncode==0 and not p.stderr,'physical replay:'+name+':'+p.stdout+p.stderr)
    return A.parse(p.stdout)

def compute():
    pins=A.authenticate()
    runtime.cold()
    try:
        C=runtime.module('qq16_connection',HERE/'connection.py')
        data,packet,word,parent,service=C.bindings()
        S=runtime.module('qq16_continuation',HERE/'continuation.py')
        F=runtime.module('qq16_cost',HERE/'cost.py')
        L=runtime.module('qq16_lifecycle',HERE/'lifecycle.py')
        producer=parent.audit();decoder=service.audit()
        semantic=S.audit(packet,data['phases'],data['programs'],data['template'])
        logical=F.module_invoice(word);cost=F.physical_invoice(word)
        cost['whole_root_child_protocol']=F.root_protocol_invoice(producer['root_child_census'])
        actual=decoder['physical_per_cover'];expected=cost['decoder_service']
        for key in ('rank_one_children','physical_line_monomials','intrinsic_wrappers',
                    'owner_basis_monomials','nonmap_groups','all_gather_scatter_commit_groups',
                    'all_monomial_calls_including_map_translations',
                    'scalar_engine_calls_including_map_sign_corrections','private_zero_calls'):
            need(actual[key]==expected[key],'compiled decoder bill:'+key)
        ep=cost['producer_outer']
        need(producer['nonmap_groups_per_cover']==ep['nonmap_groups'] and
             producer['map_groups_per_cover']==ep['map_router']['gather_scatter_commit_groups_per_Gamma'] and
             producer['translated_map_calls_per_cover']==528 and
             producer['outer_macro_counts']=={'native_line':32,'scalar:add':2200,'scalar:clear':32,'scalar:scale':16},
             'actual producer outer bill')
        uniform=F.uniform_interval_domain(parent.height_programs())
        need(tuple(uniform[k] for k in ('programs','growth_constant','growth_lambda_slope','debt_constant','debt_lambda_slope','maximum_child_rank'))
             ==(46,230124,27834,84422,27834,8),'complete literal interval height')
        numeric=[]
        for lam in (1,2,8,73):
            numeric.append(F.fixed_grid_admission(lam,73*lam,230124+27834*lam,84422+27834*lam,8))
        need(all(r['admitted'] for r in numeric),'fixed admitted source width')
        B=1041408*F.gamma()+(1<<100000)
        need(4*B+(1<<24)<1<<210000,'all-parameter strict reserve inequality')
        source=ROOT/'research/physical-complex-controller'
        names=('machine.py','parking.py','bank_packets.py','selected_binding.py')
        compatibility=L.parent_source_audit({n:(source/n).read_bytes() for n in names},
                    {n:(HERE/'inputs'/('PR3464-'+n)).read_bytes() for n in names})
        native=A.parse((ROOT/'research/qq16-line-normalized-decoder/RESULT.json').read_bytes())
        dictionary={(r['port'],r['sign']):r for r in native['native']['signed_rank_one_recipes']}
        generated=[]
        from qq16_signed import signed_recipe
        installed_lines=[(i,e) for i,e in enumerate(word) if e[0]=='line']
        installed_lines += [(len(word)+224+p,('line','W'+str(p),p,-1)) for p in range(112)]
        for i,e in installed_lines:
            r=dictionary[e[2],e[3]];recipe=signed_recipe(r['q'],r['sign'],73)
            for side in ('right','left'):
                rows=recipe[side]['matrix_rows']
                cols=[sum(((rows[j]>>k)&1)<<j for j in range(73)) for k in range(73)]
                need(cols[:9]==r[side+'_columns'] and cols[9:]==[1<<k for k in range(9,73)],'actual signed73D recipe')
            need(recipe['left']['offset']==r['left_offset'],'signed affine offset')
            generated.append([i,A.sha(json.dumps(recipe,sort_keys=True).encode())])
        need(len(generated)==336,'all installed native recipes')
        compilation={'producer':producer,'decoder':decoder,'continuation':semantic,
                     'parent_return_byte_compatibility':compatibility,
                     'all336_signed73D_recipe_sha256':A.sha(json.dumps(generated).encode())}
        cost.update({'uniform_source_grid_proof':uniform,'numerical_controls':numeric,
                     'rejection_controls':F.rejection_controls(word),
                     'publication_controls':[F.publication_invoice(b) for b in (1,2,6,18,66,1000000)]})
    finally:runtime.cleanup()
    execution={name:physical(name) for name in ('producer-fixture.py','decoder-fixture.py','integrated-fixture.py')}
    execution.update({mode:physical('physical.py',mode) for mode in ('packet','lifecycle')})
    need(execution['integrated-fixture.py']['continuous']['completed_generations']==2,'composed repeat generation')
    result={'status':STATUS,'outcome_class':'B: source-bound caller installation with complete local contract and constructive symbolic bill; native-component charge comparison fails; total physical dominance unresolved',
        'scientific_base':'bb4bccbf42844d2801487450727c2f63e10d1d0f','source_inputs':pins,
        'connection':'RootLayer.fast_core first actual F0/B1 cut: source events0,4; whole-cover fence573; idle574; both bridge legs575',
        'scope':'One first-pair installation in the modified root Machine; all descendants use unchanged original C. The all-size connection is conditional on explicit native/source refinements and admission, not inferred from reduced fixtures.',
        'new_implication':'Actual producer bank to encoded448-family decoder bank to all224 current G outputs, immutable-port continuation and paid retirement; coarse prepared input/output lease/frame premises replaced by source-bound mechanisms.',
        'logical_D_allowance':26144,'D_plus_G_allowance':27936,
        'native_charge_screen':F.native_screen(),
        'whole_root_child_census':producer['root_child_census'],
        'physical_inventory':'3I+2**20 fixed roles total for controller stage; I=2q_*^2+100696823; root layer and earlier suspended inventories remain separately paid',
        'unchanged_kappa':'836330098538459/500000000000000000',
        'remaining':['Inherited exact original C/native/common-label/hosting, ordinary B1/C0, Compact and long-record hypotheses.','No production O73 numerical execution or full RootLayer.run claimed.','No affordable supplier established: isolated fullD224+producer32 native profile exceeds16H8; changed outer-call protocol credits/charges require complete physical comparison.','No all-node modified-recursion theorem; installed once in changed root Machine and original C handles all recursive descendants.','A sharper concrete runtime comparison still needs actual primitive tariffs; the operation-sum invoice treats no unknown cost as zero.'],
        'proof_inputs':{n:A.sha((HERE/n).read_bytes()) for n in ('PROOF.md','ADMISSION.json','REUSE.json')},
        'code_sha256':{p.name:A.sha(p.read_bytes()) for p in sorted(HERE.glob('*.py')) if p.name!='test_verify.py'}}
    return dict(zip(NAMES,(result,compilation,cost,execution)))

def check_receipt(name,obj,folder=HERE):
    expected=A.parse(json.dumps(obj,sort_keys=True,allow_nan=False))
    need(A.typed(A.parse((folder/name).read_bytes()))==A.typed(expected),'whole typed receipt mismatch:'+name)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args()
    if args.write:need(not any((HERE/n).exists() for n in NAMES),'refuse receipt overwrite')
    objects=compute()
    for name,obj in objects.items():
        if args.write:
            with (HERE/name).open('x') as f:f.write(json.dumps(obj,sort_keys=True,indent=2)+'\n')
        else:check_receipt(name,obj)
    print(STATUS)
if __name__=='__main__':main()
