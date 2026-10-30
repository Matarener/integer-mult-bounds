"""Bind the mixed fill to the unchanged exact all-character phase operator.

PR4085's unmodified Z4 normalizer and event-window helpers are imported.
The source-specific authenticate/main entrypoints are not used: this package
pins every input it uses, checks its own entire fill, and uses no axis overlay.
New binding: Cinna Davis with OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter,defaultdict
from copy import deepcopy
import json,sys,time
from verify import P,read,need,pins,reject,sha
from owner_verify import context
from vendor import full_operator as F
from vendor import t360_admission as T

def phase_checks(template,phases,ports):
    need(phases['m']==73 and len(phases['recipes'])==112,'phase dimensions')
    need([int(r['q']) for r in phases['recipes']]==ports,'all ordered ports')
    normals=[F.normalize(template,r) for r in phases['recipes']]
    original=F.normalize(read(P/'inputs/OPERATOR-TEMPLATE.json.gz'),phases['recipes'][0])
    need(all(n['events']==original['events'] for n in normals),'unchanged signed controller')
    need(F.exhaustive(normals[0],[],force_tensor=True)['admitted'],'all-character and tensor operator')
    return sum(n['phase_identities'] for n in normals)

def exact_windows(template,plan,order,phases):
    clock={tuple(v):t for t,v in enumerate(order)}
    blocks=T.blocks(template)
    pairs={e['stage']:e['pair'] for e in template['recipe'] if e['kind']=='local'}
    windows={}
    for o in range(360):
        last=[(-1,-1)]*8
        for s in range(9):
            tick=clock[s,o]
            for index,event in enumerate(blocks[s]):
                if event['kind']=='idle_cover_sweep':
                    for side,child in enumerate(event['child_indices']):
                        stream=2*event['pair']+side
                        if str(child) in plan['pairs']:
                            need(stream==2*plan['pairs'][str(child)]+plan['sides'][str(child)],'exact stream routing')
                        else:need(all(r['idle_children'][child]['rank']==0 for r in phases['recipes']),'only zero child may omit routing')
                        need((o,child) not in windows,'unique physical window')
                        windows[o,child]=last[stream],(tick,index),stream
                for stream in T.touches(event,pairs):last[stream]=tick,index
    shared=defaultdict(list)
    for (o,c),(lo,hi,stream) in windows.items():
        if str(c) in plan['pairs']:shared[o,stream].append((lo,hi))
    need(all(all(max(a,c)>=min(b,d) for j,(a,b) in enumerate(xs) for c,d in xs[j+1:]) for xs in shared.values()),'exact same-stream windows disjoint')
    return windows,pairs

def scan(rows,ctx,windows,pairs,phases):
    order,provider,_,_,widths,local=ctx
    used=defaultdict(int);occupied=defaultdict(int);families=set();mass=0
    need(len(rows)==1321920,'all roles')
    for j,row in enumerate(rows):
        need(len(row)==6 and all(type(v) is int for v in row),'integer physical record')
        tick,helper,o,c,p,offset=row
        need((tick,helper)==divmod(j,408),'complete call/helper identity')
        need((o,c) in windows and 0<=p<112,'physical bin')
        if helper==0:families=set()
        lo,hi,stream=windows[o,c]
        need(lo<(tick,-1)<hi,'strict exact observation window')
        physical=896*o+112*stream+p
        need(physical not in families,'same-call physical family');families.add(physical)
        stage,replica=order[tick]
        need(physical//224!=4*replica+pairs[stage],'productive data/helper nonaliasing')
        width=widths[provider[stage,replica]][helper]
        axes=phases['recipes'][p]['idle_children'][c]['orthogonal_axes'];key=o,c,p
        need(offset==used[key] and 0<=offset and offset+width<=len(axes),'exact native axis capacity')
        mask=((1<<width)-1)<<offset
        need(occupied[key]&mask==0,'disjoint original phase-axis cells')
        occupied[key]|=mask;used[key]+=width;mass+=width
    idle=Counter()
    for o in range(360):
        for p,recipe in enumerate(phases['recipes']):
            for c,child in enumerate(recipe['idle_children']):
                left=len(child['orthogonal_axes'])-occupied[o,c,p].bit_count()
                need(left>=0,'nonnegative phase residual')
                if left:idle[left]+=1
    need(mass+sum(r*n for r,n in idle.items())==360*sum(len(c['orthogonal_axes']) for r in phases['recipes'] for c in r['idle_children']),'all original axes accounted once')
    paid=Counter(idle)
    for call in order:paid.update(local[provider[tuple(call)]])
    result=read(P/'RESULT.json')
    need(dict(paid)=={int(k):v for k,v in result['profile'].items()},'exact phase invoice')
    need(dict(idle)=={int(k):v for k,v in result['idle'].items()},'exact phase residual')
    return dict(sorted(idle.items()))

def main():
    start=time.monotonic();pins();ctx=context()
    template=read(P/'owner/TEMPLATE.json.gz');phases=read(P/'inputs/DATA-PHASES.json')
    need(template['exact_data_phase_recipe_sha256']==sha(P/'inputs/DATA-PHASES.json'),'exact phase recipe pin')
    ports=read(P/'inputs/THREE-base.json.gz')['ports']
    identities=phase_checks(template,phases,ports)
    for tag in ('base','extra'):
        for kind in ('THREE','FOUR'):
            need(read(P/f'inputs/{kind}-{tag}.json.gz')['ports']==ports,'common all112 port interface')
    windows,pairs=exact_windows(template,read(P/'owner/PLAN.json.gz'),ctx[0],phases)
    rows=read(P/'owner/FILL.json.gz')['rows'];idle=scan(rows,ctx,windows,pairs,phases)
    controls=[]
    if '--controls' in sys.argv:
        bad=deepcopy(phases)
        child=next(c for c in bad['recipes'][0]['idle_children'] if c['rank']>0)
        child['translation_after']=int(child['translation_after'])^1
        controls.append(reject('wrong_global_phase',lambda:phase_checks(template,bad,ports)))
        bad=deepcopy(template);bridge=next(e for e in bad['execution_schedule'] if e['kind']=='bridge');bridge['coefficient']=-bridge['coefficient']
        controls.append(reject('wrong_signed_controller',lambda:phase_checks(bad,phases,ports)))
        original=rows[0][:];tick=rows[0][0]
        o,c=next(k for k,(lo,hi,stream) in windows.items() if lo>=(tick,-1))
        rows[0][2:4]=o,c
        try:controls.append(reject('cross_scalar_observation',lambda:scan(rows,ctx,windows,pairs,phases)))
        finally:rows[0][:]=original
    print(json.dumps({'status':'PASS_MIXED_EXACT_PHASE_OPERATOR','ports':112,'exact_Z4_identities':identities,'all_characters':True,'all_positive_tensor_multiplicities':True,'hosted_rows':len(rows),'idle':idle,'controls':controls,'seconds':time.monotonic()-start},sort_keys=True))
if __name__=='__main__':main()
