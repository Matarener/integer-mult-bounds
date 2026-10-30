"""Exact full verification of PR5602's boundary relation composed with PR5612.

Prepared for flyingviper with substantial OpenAI Codex assistance. Apache-2.0.
Ali Romman's identity and original native/caller/price notices remain credited.
"""
from copy import deepcopy
from pathlib import Path
import json,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from sources import sources,load,need,read
import construct

def diff(a,b):return {k:a.get(k,0)-b.get(k,0) for k in a.keys()|b.keys() if a.get(k,0)!=b.get(k,0)}
def reject(action):
    try:action()
    except ValueError as error:return str(error)
    raise ValueError('Invalid control accepted')

def main():
    with sources() as (parent,prior,framework):
        L=load(prior/'inputs/pr5599-local.py','local');L.ROOT=framework
        R=load(parent/'prepared573_local.py','basis_prepared_checker')
        # Use the published checker unchanged, including its owned573 contract.
        parent_text=(parent/'inputs/pr5606-prepared.py').read_text()
        body=parent_text[parent_text.index('def add('):]
        for a,b in [('750','748'),('758','756'),('749','747'),('ascending = r < 748','ascending = not private')]:body=body.replace(a,b)
        adapted=(parent/'prepared573_local.py').read_text()
        need(body==adapted[adapted.index('def add('):],'Exact inherited checker adaptation')
        source=read(parent/'WORD.json.gz');old=R.replay(source)
        witness=read(HERE/'WITNESS.json')
        originals=[s for s in read(HERE/'inputs/pr5602-WITNESS.json')['steps'] if s.get('kind')=='boundary_basis' and s['helper']==341]
        need(originals==[witness['source_witness']],'Exact published basis witness')
        need(dict(witness['source_witness'],cut=11285)==witness['adapted_witness'],'Only the causal cut index changes')
        B=load(HERE/'inputs/pr5602-construct.py','published_boundary_constructor')
        candidate=B.boundary_basis(source,witness['adapted_witness'])
        need(candidate==construct.construct(source)==read(HERE/'WORD.json.gz'),'Published and specialized constructors agree on entire payload')
        local=R.replay(candidate)
        pd,td=diff(local['paid'],old['paid']),diff(local['helpers'],old['helpers'])
        need(pd=={5:-1} and td=={4:1,9:-1},'Exact paid and productive target change')
        need((local['public_inputs'],local['owned_lifetimes'],local['peak_owned_fields'])==(747,11,2),'Unchanged independent and owned interface')
        need([e for e in candidate['program'] if e[0] in ('INIT','CLEAR','COPY')]==[e for e in source['program'] if e[0] in ('INIT','CLEAR','COPY')],'Ownership sequence unchanged')
        print('PASS source pins, exact original witness, two constructors and all756 endpoint rows',flush=True)
        transpose=R.reverse_columns(candidate)
        print('PASS all756 dense transpose columns',flush=True)
        native=L.native(candidate)
        native['helpers'][2]-=1;native['helper_normalizers']-=2;native['retired_helper']=573
        need(native['helpers']==local['helpers'],'Native census includes both target changes')
        print('PASS every signed native map',native['distinct_maps'],flush=True)
        C=load(framework/'research/p104-productive-controller/caller.py','basis_caller')
        caller=C.construct();need(caller==read(framework/'research/p104-productive-controller/CONTROLLER.json'),'Unchanged full caller')
        physical=C.physical(caller,candidate)
        print('PASS full physical caller',flush=True)
        text=(parent/'pricing.py').read_text()
        for a,b in read(HERE/'PRICING-EDITS.json'):
            need(text.count(a)==1,'Unique pricing declaration');text=text.replace(a,b)
        need(text==(HERE/'pricing.py').read_text(),'Only five declared pricing changes')
        P=load(HERE/'pricing.py','basis_price');price=P.run(local,native,caller,physical)
        print('PASS full price, two interval engines, compiler and58 outer predicates',price['raw_root_interval'],flush=True)
        controls={}
        for label,event in [('missing_initial_basis',['ADD',341,93,'2',3]),('missing_cut_correction',['ADD',341,337,'-2',240]),('missing_owned_initialization',['INIT',573,3])]:
            bad=deepcopy(candidate);need(bad['program'].count(event)==1,'Unique corruption site');bad['program'].remove(event)
            controls[label]=reject(lambda:R.replay(bad))
        bad=deepcopy(local);bad['helpers'][4]-=1;bad['helpers'][9]+=1
        controls['old_target_credit']=reject(lambda:P.assemble(bad,native,caller,physical))
        bad=deepcopy(local);bad['paid'][5]-=1
        controls['extra_unpaid_transport']=reject(lambda:P.assemble(bad,native,caller,physical))
        result=P.encode({'status':'PASS_P104_DELAYED_BASIS_KAPPA_00310440','events':len(candidate['program']),'witness':witness['adapted_witness'],'local_paid_delta':pd,'local_target_delta':td,'local':local,'transpose':transpose,'native':native,'physical':physical,'complete_cost':price,'controls':controls})
    if '--write' in sys.argv:(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    else:need(result==read(HERE/'RESULT.json'),'Exact complete saved receipt')
    print(result['status'],flush=True)
if __name__=='__main__':main()
