"""Full verification of delayed696 plus coupled frames and prepared573.

Prepared for flyingviper with substantial OpenAI Codex assistance and independent
agents. Retain Ali Romman, Pierre-Loic Doulcet, Scratch-net and all predecessor
native/caller/compiler notices. Apache-2.0. Not a proof-kernel verification.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import json,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from sources import sources,load,need,read
import delayed,coupled_frames,prepare,prepared573_local as R

def difference(a,b):return {r:a.get(r,0)-b.get(r,0) for r in a.keys()|b.keys() if a.get(r,0)!=b.get(r,0)}
def reject(action):
    try:action()
    except ValueError as error:return str(error)
    raise ValueError('Invalid control accepted')
def main():
    text=(HERE/'inputs/pr5606-pricing.py').read_text()
    for before,after in read(HERE/'PRICING-EDITS.json'):
        need(text.count(before)==1,'Unique declared pricing edit');text=text.replace(before,after)
    need(text==(HERE/'pricing.py').read_text(),'Only declared price edits')
    # Preserve the exact source checker except declared interface constants,
    # attribution, inlined need and an ownership-direction hardening.
    original=(HERE/'inputs/pr5606-prepared.py').read_text();adapted=(HERE/'prepared573_local.py').read_text()
    original=original[original.index('def add('):]
    for before,after in [('750','748'),('758','756'),('749','747'),('ascending = r < 748','ascending = not private')]:original=original.replace(before,after)
    need(original==adapted[adapted.index('def add('):],'Exact scoped prepared checker adaptation')
    with sources() as (prior,framework):
        L=load(prior/'inputs/pr5599-local.py','local');L.ROOT=framework
        S=load(prior/'inputs/pr5599-construct.py','retained_split_final')
        C0=load(prior/'construct.py','retained_composition_construct')
        base=read(prior/'inputs/pr5580-WORD.json.gz')
        parent=C0.construct_parent(base);first=delayed.construct(parent)
        before=L.replay(parent);after=L.replay(first)
        need(difference(after['paid'],before['paid'])=={4:1,5:-1,6:-1,7:1} and after['helpers']==before['helpers'],'Exact delayed shared-component saving')
        kept=read(HERE/'SPLITS.json');old=read(prior/'SPLITS.json')
        need(len(kept)==len(old)==13,'Thirteen same split channels')
        word=first;cuts=[]
        for h,p in zip(kept,old):
            need({k:v for k,v in h.items() if k!='cut_after'}=={k:v for k,v in p.items() if k!='cut_after'},'Only cut indices change')
            word=S.split(word,h);state=L.replay(word)
            need(state['paid']==after['paid'],'Each split preserves the paid profile')
            cuts.append({'pivot':h['pivot'],'cut_after':h['cut_after'],'public':word['public']})
        stage=L.replay(word)
        word=coupled_frames.construct(word,read(HERE/'inputs/pr5601-CHANGES.json'))
        frame_stage=L.replay(word)
        need(difference(frame_stage['paid'],stage['paid'])=={2:-2,3:2,4:-2,5:1} and difference(frame_stage['helpers'],stage['helpers'])=={4:1,5:-1},'Exact coupled-frame paid and target change')
        prepared,relations=prepare.construct(word)
        local=R.replay(prepared)
        need(prepared==read(HERE/'WORD.json.gz'),'Entire regenerated final payload')
        need(difference(local['paid'],frame_stage['paid'])=={1:-2} and difference(local['helpers'],frame_stage['helpers'])=={2:-1},'Prepared helper transport deletion and target debit')
        need((local['public_inputs'],local['owned_lifetimes'],local['peak_owned_fields'])==(747,11,2),'Independent interface and owned occupancy')
        print('PASS source pins, all construction stages, thirteen fresh cuts and747 independent inputs',flush=True)
        columns=R.reverse_columns(prepared)
        print('PASS all756 dense transpose columns',flush=True)
        native=L.native(prepared)
        need(native['helpers']==frame_stage['helpers'],'Historical endpoint census before explicit retirement')
        native['helpers'][2]-=1;native['helper_normalizers']-=2;native['retired_helper']=573
        print('PASS every signed native map and retired-target debit',native['distinct_maps'],flush=True)
        C=load(framework/'research/p104-productive-controller/caller.py','delayed_final_caller')
        caller=C.construct();need(caller==read(framework/'research/p104-productive-controller/CONTROLLER.json'),'Same complete caller')
        physical=C.physical(caller,prepared)
        print('PASS complete physical caller',flush=True)
        P=load(HERE/'pricing.py','delayed_final_price');price=P.run(local,native,caller,physical)
        print('PASS complete price, two interval engines, compiler and58 outer predicates',price['raw_root_interval'],flush=True)
        controls={}
        for label,event in [('missing_owned_initialization',['INIT',573,3]),('missing_owned_return',['CLEAR',573,603]),('missing_final_shared_cleanup',['ADD',696,133,'1/2',127])]:
            bad=deepcopy(prepared);need(bad['program'].count(event)==1,'Unique negative control site');bad['program'].remove(event)
            controls[label]=reject(lambda:R.replay(bad))
        bad=deepcopy(local);bad['helpers'][2]+=1
        controls['retired_target_credited']=reject(lambda:P.assemble(bad,native,caller,physical))
        bad=deepcopy(local);bad['paid'][1]-=1
        controls['unpaid_transport']=reject(lambda:P.assemble(bad,native,caller,physical))
        oldlocal=L.replay(read(prior/'WORD.json.gz'))
        pd=difference(local['paid'],oldlocal['paid']);td=difference(local['helpers'],oldlocal['helpers'])
        need(pd=={1:-2,2:-2,3:2,4:-1,6:-1,7:1} and td=={2:-1,4:1,5:-1},'Complete delta against PR5608')
    result=P.encode({'status':'PASS_P104_DELAYED_SHARED_RELAY_KAPPA_00310299','events':len(prepared['program']),
                     'splits':cuts,'prepared_relations':relations,'local_paid_delta_vs_pr5608':pd,'local_target_delta_vs_pr5608':td,
                     'local':local,'transpose':columns,'native':native,'physical':physical,'complete_cost':price,'controls':controls})
    if '--write' in sys.argv:(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    else:need(result==read(HERE/'RESULT.json'),'Exact saved complete receipt')
    print(result['status'],flush=True)
if __name__=='__main__':main()
