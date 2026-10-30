#!/usr/bin/env python3
"""Source-bound address/ownership audit. No predecessor executable imports.
Chris R / Clear1nsight with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
from copy import deepcopy
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile

PKG = Path(__file__).resolve().parent
ROOT = PKG.parents[1]
ARCHIVE = 'research/community-frontier1042-audit/selected-replay.tar.gz'
MEMBERS = {
 'template': ('t16/global/hosted/GLOBAL-TEMPLATE.json.gz', '73f47a1e60b1e4ea66dbca9a497c411c8e6adc7984e276a437a10a9a7a13b47a'),
 'canonical': ('t16/global/base/providers/gauge44/CANONICAL-WORD.json.gz', '16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219'),
 'programs': ('t16/global/base/providers/gauge44/LOCAL-PROGRAMS.json.gz', '241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a'),
 'invoice': ('t16/global/audit/PREFIX-AND-INVOICE.json', '0b4ef2b9713da47a00ed6a948ceb6074ed0108cae78a32ddd0dc0996c5c3bb75'),
}
PENDING = {
 'WORD.json': ('272d8c1bd172c29044eb227ec6d67a882501250978234685e035158f4479aa58', '9a57a6f9c2fd8cdc4e5934408d78ef54e5f266b6'),
 'RESULT.json': ('b4af55d3db3212e79f8f31108e048c5c2d4c32d520fc980ebaa66f47933ad622', 'e9b6b8ea6f5a7dc47d8547cd7ed255e3d5864f7d'),
}

def need(ok, why):
    if not ok: raise ValueError(why)

def sha(b): return hashlib.sha256(b).hexdigest()
def blob(b): return hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest()
def serial(o): return json.dumps(o, sort_keys=True, separators=(',', ':'))

def sources():
    pins = json.loads((PKG/'SOURCES.json').read_bytes())
    raw = {}
    for p in pins['files']:
        if p['usage'] != 'input': continue
        b = (ROOT/p['path']).read_bytes()
        need(sha(b) == p['sha256'] and blob(b) == p['git_blob'], 'canonical source authentication: '+p['path'])
        raw[p['path']] = b
    out = {}
    with tarfile.open(fileobj=io.BytesIO(raw[ARCHIVE]), mode='r:gz') as t:
        for label, (name, h) in MEMBERS.items():
            matches = [m for m in t.getmembers() if m.name == name]
            need(len(matches) == 1 and matches[0].isfile(), 'unique archive member')
            b = t.extractfile(matches[0]).read()
            need(sha(b) == h, 'archive member authentication')
            out[label] = json.loads(gzip.decompress(b) if name.endswith('.gz') else b)
    for name, (h, g) in PENDING.items():
        b = (PKG/'vendor/pr4015'/name).read_bytes()
        need(sha(b) == h and blob(b) == g, 'pending data authentication: '+name)
        out[name] = json.loads(b)
    return out

def local_refs(e):
    if e[0] == 'scalar':
        q=e[1]; dst=tuple(q[1]); reads=[] if q[0] in ('clear','copy') else [dst]
        if q[0] in ('copy','add'): reads.append(tuple(q[2]))
        return reads, [dst]
    if e[0] in ('climb','adapter','residual_adapter'):
        return [('L',e[2])], [('L',e[2])]
    if e[0] == 'center': return [('C',e[1])], [('C',e[1])]
    need(e[0] == 'phase', 'unknown provider event')
    return [], []

def addresses(t, e):
    """Explicit family addresses; opaque child interiors deliberately excluded."""
    kind=e['kind']; live=t['live']; ns=t['private_namespace']; rep=e.get('replica')
    if kind == 'local_cover_sweep':
        c=next(c for c in t['calls'] if (c['stage'],c['replica']) == (e['stage'],rep))
        return {o[0] for o in c['owners']} | set(range(*ns['centers'])) | set(range(*ns['coefficient']))
    if kind == 'idle_cover_sweep':
        return {z['family'] for z in t['idle_children'] if z['replica']==rep and z['child'] in e['child_indices']}
    if kind == 'bridge': pairs=[e['src'],e['dst']]
    elif kind == 'terminal_Y_translations':
        return {rep*896+(2*p+1)*112+j for p in e['pairs'] for j in range(112)}
    elif kind == 'terminal': pairs=list(range(e['pairs']))
    elif kind in ('bank_padding_cover_sweep','translate_every_live_family'):
        return set(range(*e['families']))
    else: raise ValueError('unknown global event')
    return {rep*896+(2*p+s)*112+j for p in pairs for s in (0,1) for j in range(112)}

def allocate(word, outputs, scratch, current, clobber=None):
    """Linear capability checker for fixed word: no duplicate physical ownership."""
    out={s+str(p):outputs[(0 if s=='Z' else 112)+p] for s in ('Z','W') for p in range(112)}
    bor={s+str(p):current[(0 if s=='X' else 112)+p] for s in ('X','Y') for p in range(112)}
    priv={'F'+str(p):scratch[p] for p in range(8)} | {'G'+str(p):scratch[8+p] for p in range(8)}
    need(len(set(out.values()))==224, 'duplicate output ownership')
    need(len(set(out.values())|set(bor.values())|set(priv.values()))==464, 'physical ownership alias')
    active=set(); defined=set(bor); zero=set(); native=0; peak=0; lifetimes={n:[] for n in out}
    for i,e in enumerate(word):
        op=e[0]
        if op=='begin':
            need(not active, 'nested private window'); active=set(priv) if e[2]==16 else {'F'+str(p)for p in range(8)}
            need(e[2]==len(active), 'private size'); peak=max(peak,len(active))
        elif op=='end':
            need(len(active)==e[2] and active<=zero, 'private dirty return')
            defined-=active; zero-=active; active=set()
        elif op=='clear':
            n=e[1]; need(n in out or n in active, 'clear unowned role'); defined.add(n);zero.add(n)
            if n in out: lifetimes[n].append({'event':i,'kind':'initialize','frame':e[2]})
        elif op=='add':
            _,d,s,_=e;need(d in out or d in active,'write borrowed');need(d!=s and d in defined and s in defined,'read before initialization or self alias')
            zero.discard(d)
            for n,kind in ((s,'read'),(d,'write')):
                if n in out:lifetimes[n].append({'event':i,'kind':kind})
        elif op in ('line','map'):
            n=e[1];need(not active and n in out and n in defined,'native/map lifetime')
            if op=='line':
                native+=1
                need(not(set(clobber or ()) & {out[k]for k in out if k in defined and k not in zero and k!=n}), 'opaque native clobbers retained output')
            lifetimes[n].append({'event':i,'kind':op})
        elif op=='checkpoint':need(not active,'checkpoint private leak')
        else:raise ValueError('unknown decoder event')
    need(not active and set(out)<=defined and peak==16 and native==224,'complete decoder allocation')
    return {'roles':out,'scratch':priv,'borrowed':bor,'peak_private':peak,'native_events':native,
            'lifetimes':{n:{'family':out[n],'first_initialization':es[0], 'last_word_access':es[-1], 'return_frame':'F17 (inherited PR4015 theorem)'}for n,es in sorted(lifetimes.items())}}

def exclusive_candidates(candidates, protected, opaque_effects=()):
    """Free-bank intersection after contracting live productive obligations."""
    return sorted(set(candidates) - set(protected) - set(opaque_effects))

def rejected(f, label):
    try:f()
    except ValueError:return label
    raise ValueError('negative control accepted: '+label)

def run():
    s=sources();t,c,p,w=s['template'],s['canonical'],s['programs'],s['WORD.json']
    need(t['live']==14336 and t['physical']==14826 and c['R']==480,'source stock')
    ns=t['private_namespace'];need(ns=={'centers':[14336,14344],'reserved_tableau':[14344,14824],'coefficient':[14824,14826]},'actual reserve namespace')
    need(t['bank_padding']['families']==[] and t['bank_padding']['children']==[],'no dedicated helper bank stock')
    need(t['local_providers']['gauge44']['local_programs']==p,'literal provider dispatch')
    need(s['invoice']['physical_stock_identity']=={'data_and_owner_families':14336,'local_helpers':480,'private_centres':8,'coefficient_work':2},'charged reserve identity')
    events=t['execution_schedule']; cut=next(i for i,e in enumerate(events)if e.get('replica')==0 and e.get('stage')==1 and e['kind']=='local_cover_sweep')
    need([(e['kind'],e['source_event'])for e in events[cut:cut+3]]==[('local_cover_sweep',1),('idle_cover_sweep',2),('bridge',3)],'actual first B1 continuation')
    call=next(q for q in t['calls']if q['replica']==0 and q['stage']==1)
    need(call['provider_id']=='gauge44' and call['orientation']=='backward','actual provider is not QQ16')
    owners=[x[0]for x in call['owners']];need(len(set(owners))==704 and all(0<=x<14336 for x in owners),'distinct productive data/helper owners')
    reserve=set(range(*ns['reserved_tableau'])); refs=[addresses(t,e)for e in events]
    need(all(not(reserve & a)for a in refs),'reserve has explicit top-level use')
    need(all(set(r[0]for r in local_refs(e)[0]+local_refs(e)[1])<= {'L','C'} for es in p.values()for e in es),'literal provider namespace')
    ledger=[]
    for h,f in enumerate(owners[224:]):
        r=224+h
        reads=[i for i,e in enumerate(p['backward'])if ('L',r)in local_refs(e)[0]]
        writes=[i for i,e in enumerate(p['backward'])if ('L',r)in local_refs(e)[1]]
        next_use=next((j for j in range(cut+1,len(events))if f in refs[j]),None)
        need(reads and writes and next_use is not None,'helper continuation exists')
        ledger.append({'helper':h,'family':f,'route':call['owners'][r][1],
          'entry_frame':c['frames'][c['start'][r]],'core_exit_frame':c['frames'][c['final'][r]],
          'last_local_read':reads[-1],'last_local_write':writes[-1],
          'next_explicit_global_use':{'index':next_use,**events[next_use]},
          'return_obligation':'productive family content survives; helper endpoint is a paid invertible residual, not discarded',
          'eligible_as_exclusive_output_without_evacuation':False})
    protected={z['family'] for z in ledger if z['next_explicit_global_use']['index']>cut}
    candidate=owners[224:448];eligible=exclusive_candidates(candidate,protected)
    need(not eligible,'helper candidate unexpectedly disposable')
    need(len(exclusive_candidates(candidate,protected-{candidate[0]}))==1,'retirement eligibility control')
    outputs=list(range(14344,14568));scratch=list(range(14568,14584));current=owners[:224]
    a=allocate(w,outputs,scratch,current)
    need(len(w)==3813 and Counter(e[0]for e in w)['clear']==416,'pinned stream word census')
    need(not(set(outputs)&refs[cut+2]),'first bridge output interference')
    controls=[]
    controls.append(rejected(lambda:allocate(w,outputs[:-1]+[outputs[0]],scratch,current),'duplicate output family'))
    controls.append(rejected(lambda:allocate(w,[current[0]]+outputs[1:],scratch,current),'borrowed input alias'))
    controls.append(rejected(lambda:allocate(w,outputs,[outputs[0]]+scratch[1:],current),'private/output alias'))
    first_native=next(i for i,e in enumerate(w)if e[0]=='line')
    target=w[first_native][1]
    initialized={e[1] for e in w[:first_native] if e[0]=='clear'}
    written={e[1] for e in w[:first_native] if e[0]=='add'}
    victim=next(n for n in a['roles'] if n!=target and n in initialized and n in written)
    victim_family=a['roles'][victim]
    controls.append(rejected(lambda:allocate(w,outputs,scratch,current,[victim_family]),'native workspace may clear distinct retained output'))
    bad=deepcopy(w);bad[0]=['add','Z0','X0','1']
    controls.append(rejected(lambda:allocate(bad,outputs,scratch,current),'missing initial output clear'))
    bad=deepcopy(t);bad['execution_schedule'][cut+2]={'kind':'translate_every_live_family','families':[14344,14345]}
    need(bool(reserve & addresses(bad,bad['execution_schedule'][cut+2])),'continuation clobber control');controls.append('continuation reserve clobber detected')
    return {'status':'PASS_QQ16_OUTPUT_STOCK_CONTRACT_AUDIT','scope':'Exact literal family-address allocation and bounded ownership obstruction; not native-body exclusivity or physical supplier admission',
      'source_members':{k:{'path':v[0],'sha256':v[1]}for k,v in MEMBERS.items()},
      'actual_cut':{'execution_index':cut,'prefix':[e for e in events if e.get('replica')==0][:4], 'provider':'gauge44'},
      'stock':{'productive':14336,'physical':14826,'private_centres':8,'reserved_tableau':480,'coefficient':2,'dedicated_helper_banks':0},
      'helper_candidate':{'proposed_224_families':owners[224:448],'eligible_matching_size':len(eligible),'deficit':224-len(eligible),'model':'fixed literal owners, independent productive contents, no evacuation/recomputation or retirement of original outputs','all480_helper_lifetimes':ledger},
      'reserve_candidate':{'output_interval':[14344,14568],'private_interval':[14568,14584],'remaining_reserve':240,'explicit_top_level_conflicts':0,'first_bridge_conflicts':0,'allocation':a,
        'native_exclusive_lease':'UNPROVED: all native/map/wrapper bodies must exclude the leased 240 fields or have disjoint scoped work; macro absence alone is insufficient',
        'changed_QQ16_provider':'UNPROVED: selected gauge44 dispatch is not the QQ16 producer. This map is conditional on supplying the PR4015 input contract at the same cut.'},
      'return_ledger':{'outputs':224,'frame':'F17','lifetime':'from paid first initialization to declared decoder return; actual selected bridge reads none','private_scratch':16,'scratch_return':'zero/identity inherited from fixed PR4015 word','eventual_private_zero_return_if_outputs_are_discarded':{'additional_CLEAR':224,'additional_scalar_allowance':448,'native':0,'maps':0,'new_module_scalar_total':27392},'consumer_and_legal_discard':'not supplied by this address audit'},
      'native_clobber_countermodel':{'event':first_native,'declared_target':target,'target_family':a['roles'][target],'distinct_retained_victim':victim,'victim_family':victim_family},'negative_controls':controls,'retirement_sensitivity_control':'Retiring exactly one protected candidate restores exactly one eligible bank in the bounded model','scientific_replay_inherited':'PR4015 exact head0fff81d8997cef646538bcd4f60d7d455cf93b8e; no new algebra or native kernel replay claimed'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');a=ap.parse_args();path=PKG/'RESULT.json'
    if a.write:need(not path.exists(),'refuse overwrite RESULT')
    result=run()
    if a.write:
        with path.open('x') as f:f.write(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:need(serial(result)==serial(json.loads(path.read_bytes())),'typed complete receipt mismatch')
    print('PASS_QQ16_OUTPUT_STOCK_CONTRACT_AUDIT')
if __name__=='__main__':main()
