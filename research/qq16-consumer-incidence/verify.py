#!/usr/bin/env python3
"""Source-bound integer incidence and conditional QQ16 budget. Apache-2.0.
Chris R / Clear1nsight with substantial OpenAI assistance.
No predecessor executable is imported; numerical helper is package-local.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip,hashlib,io,json,tarfile,types
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
BASE='20ecf2891d80b5acf18d980b2164fb44ea7faa90'
MEMBER='t16/global/hosted/GLOBAL-TEMPLATE.json.gz'
MEMBER_SHA='73f47a1e60b1e4ea66dbca9a497c411c8e6adc7984e276a437a10a9a7a13b47a'
CASES=['F_0','B_1_2','F_2','B_3_4','F_4','B_5_6','F_6','B_7_8','F_8']
PAIRS=[0,0,0,1,1,2,2,3,3]
CORE={1:2412,2:418,3:432,4:142,5:82}

def need(ok,why):
    if not ok:raise ValueError(why)

def parse(raw):
    def pairs(items):
        d=dict(items);need(len(d)==len(items),'duplicate JSON key');return d
    return json.loads(raw,object_pairs_hook=pairs)

def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)

def sources():
    need(hashlib.sha256((HERE/'SOURCES.json').read_bytes()).hexdigest()=='958f1d29b31e8aa25d2f078ac0e8ac7ca53ce98029fd265446a2ce5900815e60','source manifest binding')
    need(hashlib.sha256((HERE/'PREDECESSORS.json').read_bytes()).hexdigest()=='eed9ddb0e7339b0fd75a8fa2f9ddb0c7556c43c1450185d16bfd3f6c3ca62599','predecessor manifest binding')
    manifest=parse((HERE/'SOURCES.json').read_bytes())
    need(manifest['base_commit']==BASE,'source base')
    data={}
    for pin in manifest['files']:
        if pin['usage']!='input':continue
        raw=(ROOT/pin['path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest()==pin['sha256'],'source hash '+pin['path'])
        need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==pin['git_blob'],'source Git blob')
        data[pin['path']]=raw
    for pin in parse((HERE/'PREDECESSORS.json').read_bytes())['retained_data']:
        raw=(HERE/pin['local_path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest()==pin['sha256'],'retained source hash')
        need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==pin['git_blob'],'retained Git blob')
    return data

def load_template(raw):
    with tarfile.open(fileobj=io.BytesIO(raw),mode='r:gz') as archive:
        members=[m for m in archive.getmembers() if m.name==MEMBER]
        need(len(members)==1 and members[0].isfile(),'unique source member')
        blob=archive.extractfile(members[0]).read()
        need(hashlib.sha256(blob).hexdigest()==MEMBER_SHA,'template member hash')
        return parse(gzip.decompress(blob))

def flatten(seq):
    for e in seq:
        if e[0] in ('private_sweep','cover_sweep'):yield from flatten(e[2])
        else:yield e

def producer(packet):
    for word in packet['core_words'].values():
        need(not any(e[0]=='center' for e in word),'already removed centre')
        need(dict(Counter(e[5] for e in word if e[0]=='climb'))==CORE,'literal core profile')
    rows=[]
    for stage,name in enumerate(CASES):
        ev=list(flatten(packet['programs'][name]));counts=Counter(e[0] for e in ev)
        retained=[e for e in ev if e[0]=='retained_core']
        need(len(retained)==1 and retained[0][1]==('backward' if stage%2 else 'forward'),'core orientation')
        lines=[e for e in ev if e[0]=='native_line']
        for e in lines:
            r=packet['native_line_recipes'][e[2]]
            need(r['rank']==r['recipe']['rank']==1,'native line rank')
        profile=dict(CORE);profile[1]+=len(lines)
        rows.append({'stage':stage,'pair':PAIRS[stage],'case':name,'orientation':retained[0][1],
                     'added_H1':len(lines),'profile':profile,'outside_core_events':dict(sorted(counts.items()))})
    need(sum(x['added_H1'] for x in rows)==136,'nine-stage line total')
    return rows

def schedule(template,packet):
    events=template['execution_schedule'];calls=template['calls'];order=template['async_schedule']['order']
    need(template['live']==14336 and template['replica_lift']['replicas']==16,'family/replica source')
    need(template['physical']==14826,'selected physical capacity')
    need(len(calls)==144 and len(events)==482,'complete schedule dimensions')
    need([[c['stage'],c['replica']] for c in calls]==order,'call order binding')
    need({(c['replica'],c['stage']) for c in calls}=={(r,s) for r in range(16) for s in range(9)},'unique replica-stage incidence')
    need([c['time'] for c in calls]==list(range(144)),'serial complete call times')
    need(all(c['provider_id']=='gauge44' for c in calls),'actual provider unchanged')
    local=[(i,e) for i,e in enumerate(events) if e['kind']=='local_cover_sweep']
    need([(e['replica'],e['stage'],e['time']) for i,e in local]==[(c['replica'],c['stage'],c['time']) for c in calls],'physical local inventory')
    need(dict(Counter(e['kind'] for e in events))=={'local_cover_sweep':144,'idle_cover_sweep':160,'bridge':144,'terminal_Y_translations':16,'terminal':16,'bank_padding_cover_sweep':1,'translate_every_live_family':1},'physical event grammar')
    need(template['cover_final_correction']['families']==[0,14336],'productive family boundary')
    stages=[]
    for s in range(9):
        subset=[c for c in calls if c['stage']==s]
        for c in subset:
            need(c['pair']==PAIRS[s] and c['orientation']==('backward' if s%2 else 'forward'),'actual local pair/orientation')
            need(c['window']=={'local_axes':list(range(9)),'prefix_axes':list(range(9,9+8*s))},'actual stage frame window')
            first=896*c['replica']+224*c['pair']
            need([x[0] for x in c['owners'][:224]]==list(range(first,first+224)),'actual active family map')
        stages.append({'stage':s,'case_under_QQ16_substitution':CASES[s], 'count':len(subset),'pair':PAIRS[s],
                       'completed_window_dimension':9+8*s,'source_provider':'gauge44'})
    cuts=[]
    for i,e in local:
        if e['stage']!=1:continue
        r=e['replica'];tail=[(j,x) for j,x in enumerate(events) if j>i and x.get('replica')==r]
        j,idle=tail[0];k,bridge=tail[1]
        need(idle['kind']=='idle_cover_sweep' and idle['pair']==1 and idle['source_event']==2,'first postcut idle')
        need(bridge['kind']=='bridge' and (bridge['src'],bridge['dst'],bridge['coefficient'])==(1,0,1),'first demanded current-bank read')
        f2=next(j for j,x in tail if x['kind']=='local_cover_sweep' and x['stage']==2)
        terminal=next(j for j,x in tail if x['kind']=='terminal')
        cuts.append({'replica':r,'call_time':e['time'],'after_schedule_index':i,'next_idle_index':j,
            'next_bridge_index':k,'next_F2_index':f2,'terminal_index':terminal,
            'borrowed_Y_family_interval':[896*r+112,896*r+224],
            'next_bridge_Ydst_ordinary_families':[896*r+112+p for p in packet['U_ports']],
            'literal_projected_output_consumer':None,
            'missing_binding':'provider gauge44 must first be replaced/connected to QQ16; bridge reads current Y2_U, not a fresh y1_U output bank'})
    need(len(cuts)==16,'stage1 cut count')
    def retention(endkey):
        changes=[]
        for c in cuts:changes.extend([(2*c['after_schedule_index']+1,96),(2*c[endkey],-96)])
        live=peak=0
        for _,d in sorted(changes):live+=d;peak=max(peak,live)
        need(live==0,'retention balance')
        return {'capture_instances':16,'output_bank_instances':1536,'peak_retained_output_fields':peak,
                'scope':'hypothetical logical retention only; no allocation/hosting or consumer admitted'}
    return {'physical_event_counts':dict(sorted(Counter(e['kind'] for e in events).items())),
        'stages':stages,'stage1_insertion_sites':cuts,'source_aligned_site_rate':'1/9',
        'literal_projection_invocations':0,'all_backward_sites':64,
        'retention_sensitivities':{'until_next_F2':retention('next_F2_index'),'until_replica_terminal':retention('terminal_index')},
        'actual_live_families':14336,'actual_physical_families':14826,'productive_families_per_replica':896,
        'first_missing_provider_event':{'schedule_index':0,'provider':'gauge44','proposed_case':'F_0'}}

def projection_invoice(word,U):
    counts=Counter(e[0] for e in word)
    reads={e[2] for e in word if e[0]=='add' and isinstance(e[2],str) and e[2].startswith(('X','Y'))}
    need(reads=={'Y'+str(p) for p in range(112)},'all112 current Y and no X reads')
    owned={'W'+str(p) for p in range(112)}
    first={}
    for i,e in enumerate(word):
        if e[0] in ('clear','add','line','map') and e[1] in owned:first.setdefault(e[1],(i,e))
    need(all(e[0]=='clear' for i,e in first.values()) and len(first)==112,'owned dirt erased before use')
    for name,(cut,_) in first.items():
        need(not any(e[0]=='add' and e[2]==name for e in word[:cut]),'owned dirt read before clear')
    need(counts['line']==112 and counts['map']==208 and counts['clear']==144,'projection local invoice')
    unit=sum(e[0]=='add' and abs(Q(e[3]))==1 for e in word)
    quarter=sum(e[0]=='add' and abs(Q(e[3]))==Q(1,4) for e in word)
    need((unit,quarter)==(560,384),'projection scalar counts')
    return {'per_invocation':{'H1':112,'native_wrappers':224,'maps':208,'unit_ADD':unit,'quarter_ADD':quarter,'CLEAR':144,'scalar_allowance':8*unit+12*quarter+288},
        '16_site_total':{'H1':1792,'native_wrappers':3584,'maps':3328,'scalar_allowance':150016},
        'owned_output_fields_per_site':96,'owned_temporary_fields_per_site':16,'private_scratch_per_site':8,
        'productive_extension_control':{'owned_dirt_basis_field':'W'+str(U[0]),'first_event_index':first['W'+str(U[0])][0],
        'initial_dirt_erased':True,'interpretation':'Appending these output slots does not satisfy the selected arbitrary productive-input family contract; a different zero-input supplier theorem would need new coverage.'}}

def calculate():
    data=sources();template=load_template(data['research/community-frontier1042-audit/selected-replay.tar.gz'])
    packet=parse(gzip.decompress(data['research/joint-query/certificate.json.gz']))
    rows=producer(packet);ledger=schedule(template,packet)
    word=parse((HERE/'vendor/pr3952/WORD.json').read_bytes());invoice=projection_invoice(word,packet['U_ports'])
    module=types.ModuleType('arithmetic');path=HERE/'arithmetic.py'
    exec(compile(path.read_bytes(),str(path),'exec'),module.__dict__)
    selected=parse(data['certificates/selected-result.json']);kappa=Q(selected['kappa'])
    a=kappa/(1-kappa)
    profile=Counter()
    for row in rows:
        for r,n in row['profile'].items():profile[r]+=16*n
    screens=module.screens(dict(profile),a,144,14336,16)
    ceiling=parse(data['research/complex-local-word-ceiling/RESULT.json'])
    need(ceiling['model']['centre_per_call']==64 and ceiling['model']['live_families_per_call']=='896/9','conditional coverage source')
    return {'status':'PASS_QQ16_INTEGER_CONSUMER_INCIDENCE no_new_kappa','canonical_main':BASE,
        'template_member':{'path':MEMBER,'sha256':MEMBER_SHA},'producer_stage_profiles':rows,
        'complete_producer_profile_144':dict(sorted(profile.items())),
        'producer_mean_H1':str(Q(profile[1],144)), 'schedule_ledger':ledger,'projection_invoice':invoice,
        'conditional_screens':screens,
        'decision':'The proposed once-per-stage1-cut placement has16sites/144calls, not72/144. It is not an actual admitted consumer schedule: selected provider and downstream read/type binding are missing. One-stage1-module full336 budget passes the conditional fixed-coverage relaxation; the older pair-rate rejection does not transport. No displaced idle credit or productive family extension is proved.'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--emit',action='store_true');args=p.parse_args()
    result=calculate()
    if args.emit:print(json.dumps(result,indent=2,sort_keys=True))
    else:
        need(canonical(result)==canonical(parse((HERE/'RESULT.json').read_bytes())),'complete typed RESULT mismatch')
        print(result['status'])
if __name__=='__main__':main()
