"""Verify the complete P104 shared-relay/cascade/helper-split composition.

Prepared for flyingviper with substantial OpenAI Codex assistance and independent
agents. Ali Romman supplied the split and pricing framework; Pierre-Loic Doulcet
supplied the commuting cascade. All retained source notices remain. Apache-2.0.
"""
from collections import Counter
from copy import deepcopy
from difflib import SequenceMatcher
from fractions import Fraction as Q
from hashlib import sha1,sha256
from pathlib import Path
import json,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from common import closure,load,need,read
from construct import construct,construct_parent


def independent_parent(base,relay,cascade):
    """Merge disjoint literal edits from the two retained predecessor generators."""
    old=base['program'];edits=[]
    for word in (relay,cascade):
        matcher=SequenceMatcher(None,list(map(tuple,old)),list(map(tuple,word['program'])),autojunk=False)
        edits += [(i,j,word['program'][a:b]) for kind,i,j,a,b in matcher.get_opcodes() if kind!='equal']
    edits.sort(key=lambda e:(e[0],e[1]));cursor=0;program=[]
    for i,j,part in edits:
        need(i>=cursor,'Disjoint source edit intervals')
        program+=deepcopy(old[cursor:i])+deepcopy(part);cursor=j
    program+=deepcopy(old[cursor:])
    result=deepcopy(cascade);result['program']=program
    return result


def delta(new,old):
    return {r:new.get(r,0)-old.get(r,0) for r in new.keys()|old.keys() if new.get(r,0)!=old.get(r,0)}


def reject(action):
    try:action()
    except ValueError as e:return str(e)
    raise ValueError('Invalid control accepted')


def main():
    pins=read(HERE/'SOURCES.json')
    for p in pins['external_inputs']:
        raw=(HERE/p['local_path']).read_bytes()
        need(sha256(raw).hexdigest()==p['sha256'],'Immutable input SHA256: '+p['local_path'])
        need(sha1(('blob '+str(len(raw))+'\0').encode()+raw).hexdigest()==p['git_blob'],'Immutable input blob: '+p['local_path'])
    source_price=(HERE/'inputs/pr5599-pricing.py').read_text()
    for before,after in [
        ("KAPPA, TESTED = Q('.00309839'), Q('.0030983905')","KAPPA, TESTED = Q('.00310184'), Q('.0031018405')"),
        ("PREVIOUS = Q('.00308189')","PREVIOUS = Q('.00309839')"),
        ("sum(targets.values()) == 13084 and sum(paid.values()) == 66852","sum(targets.values()) == 13048 and sum(paid.values()) == 66690"),
        ("'kappa_decimal':'.00309839'","'kappa_decimal':'.00310184'"),
        ("'previous_open_pr5580':PREVIOUS","'previous_open_pr5599':PREVIOUS")]:
        need(source_price.count(before)==1,'Unique pricing declaration')
        source_price=source_price.replace(before,after)
    need(source_price==(HERE/'pricing.py').read_text(),'Only five declared pricing edits')
    base=read(HERE/'inputs/pr5580-WORD.json.gz')
    relay_module=load(HERE/'inputs/pr5605-construct.py','retained_relay')
    cascade_module=load(HERE/'inputs/pr5565-construct.py','retained_cascade')
    relay,cascade=relay_module.construct(base),cascade_module.construct(base)
    need(relay==read(HERE/'inputs/pr5605-WORD.json.gz'),'Exact published relay reconstruction')
    need(cascade==read(HERE/'inputs/pr5565-WORD.json.gz'),'Exact published cascade reconstruction')
    parent=construct_parent(base)
    need(parent==independent_parent(base,relay,cascade),'Independent disjoint-edit parent construction')
    witnesses=read(HERE/'SPLITS.json');original=read(HERE/'inputs/pr5599-SPLITS.json')
    kept=[h for i,h in enumerate(original,1) if i not in (12,15)]
    need(len(original)==15 and len(witnesses)==len(kept)==13,'Exact retained split inventory')
    for h,prior in zip(witnesses,kept):
        need({k:v for k,v in h.items() if k!='cut_after'}=={k:v for k,v in prior.items() if k!='cut_after'},'Only split cut offsets change')
    with closure() as root:
        L=load(HERE/'inputs/pr5599-local.py','local');L.ROOT=root
        S=load(HERE/'inputs/pr5599-construct.py','retained_split')
        split_base=L.replay(read(HERE/'inputs/pr5599-WORD.json.gz'))
        word=parent;cuts=[];paid=L.replay(parent)['paid']
        for h in witnesses:
            word=S.split(word,h)
            stage=L.replay(word)
            need(stage['paid']==paid,'Every split preserves exact paid histogram')
            cuts.append({'pivot':h['pivot'],'cut_after':h['cut_after'],'ranks':h['ranks'],'public':word['public'],'events':len(word['program'])})
        need(word==read(HERE/'WORD.json.gz'),'Entire regenerated final word payload')
        local=L.replay(word)
        need((local['public_inputs'],local['owned_lifetimes'],local['peak_owned_fields'])==(748,8,1),'Public and owned inventory')
        pd=delta(local['paid'],split_base['paid']);td=delta(local['helpers'],split_base['helpers'])
        need(pd=={1:-9,2:-1,3:-2,4:-2,5:4,6:1},'Complete local paid delta versus PR5599')
        need(td=={1:-2,4:-1,5:1,8:-2,9:2},'Complete local target delta versus PR5599')
        print('PASS immutable inputs, independent construction, all13 exact cuts and748 arbitrary inputs',flush=True)
        reverse=L.reverse_columns(word)
        print('PASS dense exact transpose',flush=True)
        native=L.native(word)
        print('PASS all signed native maps',native['distinct_maps'],flush=True)
        C=load(root/'research/p104-productive-controller/caller.py','composed_caller')
        caller=C.construct();need(caller==read(root/'research/p104-productive-controller/CONTROLLER.json'),'Exact unchanged physical caller')
        physical=C.physical(caller,word)
        print('PASS physical caller',flush=True)
        P=load(HERE/'pricing.py','composed_price')
        price=P.run(local,native,caller,physical)
        print('PASS complete invoice, two interval engines, compiler and58 outer predicates',price['raw_root_interval'],flush=True)
        controls={}
        bad=deepcopy(witnesses[0]);key=next(iter(bad['a']));bad['a'][key]=str(Q(bad['a'][key])+1)
        controls['false_prefix']=reject(lambda:S.check_cut(parent,bad))
        bad=deepcopy(word);bad['program'].pop(0)
        controls['missing_input_basis']=reject(lambda:L.replay(bad))
        bad=deepcopy(word);bad['program'].pop()
        controls['missing_output_basis']=reject(lambda:L.replay(bad))
        bad=deepcopy(local);bad['helpers'][1]+=1
        controls['unearned_target']=reject(lambda:P.assemble(bad,native,caller,physical))
        bad=deepcopy(local);bad['paid'][1]-=1
        controls['unpaid_transport']=reject(lambda:P.assemble(bad,native,caller,physical))
        # At the two omitted old cuts there is no remaining line597 visit of
        # the pivot. Reinserting them would require a new charged itinerary.
        omitted=[original[11],original[14]]
        missing=[]
        for h in omitted:
            r,f=h['pivot'],h['frame']
            need(not any(e[0]=='MOVE' and e[1]==r and e[3]==f for e in parent['program']),'Omitted split pivot never visits old chart')
            missing.append({'pivot':r,'frame':f,'reason':'The cascade removes this intermediate chart visit.'})
    result=P.encode({'status':'PASS_P104_RELAY_SPLIT_COMPOSITION_KAPPA_00310184','cuts':cuts,
                     'omitted_original_splits':missing,'events':len(word['program']),
                     'local_paid_delta_vs_pr5599':pd,'local_target_delta_vs_pr5599':td,
                     'local':local,'transpose':reverse,'native':native,'physical':physical,
                     'complete_cost':price,'negative_controls':controls})
    if '--write' in sys.argv:(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    else:need(result==read(HERE/'RESULT.json'),'Exact complete committed receipt')
    print(result['status'],flush=True)


if __name__=='__main__':main()
