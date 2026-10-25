#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Source-bound finite two-edit replay; no network, Git, solver or native build."""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import time
import types

P=Path(__file__).resolve().parent

def need(ok,why):
    if not ok:raise ValueError(why)

def authentic(raw,row):
    need(len(raw)==row['bytes'],'source length: '+row['local'])
    need(hashlib.sha256(raw).hexdigest()==row['sha256'],'source SHA256: '+row['local'])
    need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob'],
         'source Git blob: '+row['local'])

sources=json.loads((P/'SOURCES.json').read_text())
for row in sources['snapshots']:authentic((P/row['local']).read_bytes(),row)
S=types.ModuleType('neutral_search');S.__file__=str(P/'search.py')
exec(compile((P/'search.py').read_bytes(),str(P/'search.py'),'exec'),S.__dict__)
R,C,A=S.R,S.C,S.A

def normal(x):return json.loads(json.dumps(x,sort_keys=True))

def object_hash(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def block_matrix(gates,registers=None):
    """Own rational scalar-block check, independent of retained interpreters.

    Every input row is an independent symbol, so equality is on all dirty states.
    Frames are checked separately; native gates are forbidden in this block.
    """
    if registers is None:registers=sorted({r for g in gates for r in (g[1:3] if g[0]=='add' else g[1:2])})
    rows={r:{r:Q(1)} for r in registers}
    for g in gates:
        if g[0]=='scale':
            q=Q(g[2],g[3]);need(q!=0,'zero scalar')
            rows[g[1]]={k:v*q for k,v in rows[g[1]].items()}
        else:
            need(g[0]=='add' and g[1]!=g[2],'non-scalar block or self ADD')
            q=Q(g[3],g[4]);need(q!=0,'zero ADD')
            for k,v in rows[g[2]].items():
                z=rows[g[1]].get(k,0)+q*v
                if z:rows[g[1]][k]=z
                else:rows[g[1]].pop(k,None)
    return [[str(rows[r].get(c,0)) for c in registers] for r in registers]

def block_equal(before,after):
    regs=sorted({r for g in before+after for r in (g[1:3] if g[0]=='add' else g[1:2])})
    b,a=block_matrix(before,regs),block_matrix(after,regs)
    need(a==b,'arbitrary-dirty scalar block differs')
    return {'registers':regs,'matrix_sha256':object_hash(a)}

def first_block(w,new,rec):
    lo=min(rec['index'],rec['cut']);hi=max(rec['index']+1,rec['cut'])
    return block_equal(w[rec['section']][lo:hi],new[rec['section']][lo:hi])

def summarize(report,keep_first=False):
    totals=Counter()
    for state in report['states']:
        for row in state['deltas']:
            d=tuple(row['delta']);need(R.all_power_nonnegative(d),'uncertified second delta')
            need(sum(k*n for k,n in enumerate(d))==0,'rank mass drift')
            totals[d]+=row['count']
    need(not report['gains'],'improving or uncertified literal candidate remains')
    need(report['counts'].get('uncertified_prices',0)==0,'unresolved relaxed price')
    rows=[{'delta':{str(k):n for k,n in enumerate(d) if n},'count':n,
           'caps':R.caps(d),'prefix_caps':[sum(R.caps(d)[:j]) for j in range(1,9)]}
          for d,n in sorted(totals.items())]
    result={'counts':dict(report['counts']),'delta_types':rows,
            'ordered_state_sha256':object_hash(report['states'])}
    if keep_first:result['first_edits']=[x['first'] for x in report['states']]
    return result

def rejects(fn,label):
    try:fn()
    except (ValueError,C.AuditFailure):return label
    raise ValueError('control accepted: '+label)

def ledger(w):
    bill,widths,chain,start,end=C.frame_bill(w)
    need(R.tracing(w)[2]==bill,'independent chronological bill')
    need(w['cleanup']==C.derive_cleanup(w),'source cleanup differs')
    C.hygiene(w)
    primitive={sec:dict(sorted(Counter(g[0] for g in w[sec]).items())) for sec in
               ('precondition','compensation','A','cut','B','restore','cleanup')}
    inherited=json.loads((P/'inputs/PROFILE.json').read_text())
    return {'local_profile':bill,'local_recursive_children':sum(bill.values()),
            'local_rank_mass':sum(r*n for r,n in bill.items()),'helper_width_inventory':widths,
            'helper_roles':sum(widths.values()),'live_inputs':C.N-len(w['removed']),
            'dirty_buffers':len(w['helper_final']),'primitive_inventory':primitive,
            'native_B_maps':len(w['warps']),'initial_operator_corrections':len(w['initial_corrections']),
            'extra_scalar_gates':0,'extra_helpers':0,'extra_dirty_buffers':0,
            'entrance_frame_sha256':object_hash({str(k):str(v) for k,v in start.items()}),
            'exit_frame_sha256':object_hash({str(k):str(v) for k,v in end.items()}),
            'inherited_outer_profile':inherited,
            'inherited_outer_profile_status':'Authenticated source only; not freshly reconstructed or admitted.',
            'proved_obligations':['Exact local chronological recursive invoice including centre descents and final climbs',
                'Fixed primitive counts, native maps/cuts, role and buffer counts',
                'Every admitted first-edit scalar block on arbitrary dirty inputs',
                'Full 723-input first-word and positive-control operator/cleanup checks'],
            'unknown_obligations':['Fresh native Gaussian/Clifford realization',
                'Fresh physical hosting and global allocation/owner chronology',
                'Uniform coefficient/precision/tape and bit-operation costs',
                'All-size/compiler and full outer/supplier admission','Analytic transfer and BIT H1-H5'],
            'unknown_costs_are_zero':False,'new_supplier_or_kappa':False}

def positive_control(w):
    old=deepcopy(w);g,h=old['A'][4043:4045]
    need(g[:5]==['add',81,40,1,1] and h[:5]==['add',81,17,1,1],'control source drift')
    old['A'][4043:4045]=[h[:-1]+[g[-1]],g]
    old['cleanup']=C.derive_cleanup(old)
    mid=R.apply_move(old,'A',4043,4045,g[-1]);mid['cleanup']=C.derive_cleanup(mid)
    new=R.apply_move(mid,'A',4044,4044,h[-1]);new['A'][4044][-1]=deepcopy(h[-1])
    new['cleanup']=C.derive_cleanup(new)
    before=C.frame_bill(old)[0];middle=C.frame_bill(mid)[0];after=C.frame_bill(new)[0]
    need(before==middle,'positive first edit not neutral')
    need(after==C.frame_bill(w)[0] and new==w,'positive recovery not literal source')
    delta=tuple([0]+[after.get(k,0)-before.get(k,0) for k in range(1,10)])
    need(delta==(0,1,-1,-1,1,0,0,0,0,0),'positive control invoice')
    need(not R.all_power_nonnegative(delta),'known profitable second edit excluded')
    matches=[r for r in S.placements(mid,gate_filter=lambda s,i,g:s=='A' and i==4044,
                    sections=('A',),target_cut=4044) if tuple(r['delta'])==delta]
    need(matches,'enumerator missed profitable frame-only second step')
    block_equal(old['A'][4043:4045],mid['A'][4043:4045])
    semantics={name:A.semantics(C,value) for name,value in [('rollback',old),('neutral_middle',mid),('recovered',new)]}
    return {'before_profile':before,'neutral_profile':middle,'after_profile':after,
            'delta':delta,'semantics':semantics,'credit':'Jeremy Kothe PR2957, recovered in PR3886; already in baseline'},mid

def controls(w):
    result=[];row=sources['snapshots'][0]
    result.append(rejects(lambda:authentic((P/row['local']).read_bytes()+b'x',row),'source byte drift'))
    bad=deepcopy(w);bad['A'][4044][3]*=-1;bad['cleanup']=C.derive_cleanup(bad)
    result.append(rejects(lambda:A.semantics(C,bad),'wrong scalar after refreshed cleanup'))
    bad=deepcopy(w);bad['A'][4044][-1]=[]
    result.append(rejects(lambda:C.frame_bill(bad),'illegal gate frame'))
    bad=deepcopy(w);bad['cleanup']=bad['cleanup'][1:]
    result.append(rejects(lambda:A.semantics(C,bad),'omitted cleanup on arbitrary dirt'))
    bad=deepcopy(w);bad['report']['local_profile']['1']+=1
    result.append(rejects(lambda:need(C.frame_bill(bad)[0]=={int(k):v for k,v in bad['report']['local_profile'].items()},'invoice differs'),'false declared invoice'))
    i=next(i for i in range(w['prelude_events'],len(w['A'])-1)
           if w['A'][i][0]=='add' and not R.crosses(w['A'][i],w['A'][i+1]))
    result.append(rejects(lambda:R.apply_move(w,'A',i,i+2,w['A'][i][-1]),'noncommuting scalar barrier'))
    pair=[['add',0,1,1,1,[]],['add',1,2,1,1,[]]]
    result.append(rejects(lambda:block_equal(pair,list(reversed(pair))),'own dirty-block checker rejects noncommuting swap'))
    need(not R.all_power_nonnegative((0,1,-2,1,0,0,0,0,0,0)),'profitable target has false sign certificate')
    result.append('profitable 2+2 to 1+3 rejected by non-improvement certificate')
    return result

def verify_provider(tag,full_dirty=True):
    w=S.load(tag);t=time.monotonic();base=R.census(w)
    need(base['candidates']==1776295 and len(base['deltas'])==19,'baseline census drift')
    need(all(x['certificate'] for x in base['deltas']),'baseline sign failure')
    own=Counter(tuple(x['delta']) for x in S.placements(w))
    expected=Counter({tuple([0]+[x['delta'].get(k,0) for k in range(1,10)]):x['count'] for x in base['deltas']})
    need(own==expected,'new enumerator does not reproduce full baseline census')
    print('BASELINE_BOUND',tag,base['candidates'],flush=True)
    zero=[x for x in S.placements(w,max_distance=2) if not any(x['delta'])]
    need(all(len(x['frame']) in (x['lower_dim'],x['upper_dim']) for x in zero),'unsampled interior neutral first subspace')
    frame=S.explore(tag,write=False,progress=False)
    print('FRAME_SECOND_PRICES',tag,frame['counts']['second_prices'],flush=True)
    pair=S.adjacent_pairs(tag,write=False,progress=False)
    print('SWAPPED_GATE_SECOND_PRICES',tag,pair['counts']['second_prices'],flush=True)
    novel=S.adjacent_novel_cuts(tag,write=False,progress=False)
    print('THIRD_GATE_MIDDLE_PRICES',tag,novel['counts']['second_prices'],flush=True)
    need(pair['counts']['legal_first']==novel['counts']['legal_first'],'adjacent start inventory differs')
    need([(s['section'],s['left_index']) for s in pair['states']]==[(s['section'],s['left_index']) for s in novel['states']],
         'adjacent start ordering differs')
    first_checks=[]
    for j,state in enumerate(frame['states']):
        rec=state['first'];new=S.apply(w,rec);new['cleanup']=C.derive_cleanup(new)
        block=first_block(w,new,rec)
        C.hygiene(new)
        need(C.frame_bill(new)[:2]==C.frame_bill(w)[:2],'first local invoice/inventory drift')
        need(new['report']['local_profile']==w['report']['local_profile'],'first declared invoice drift')
        semantic=A.semantics(C,new) if full_dirty else {'status':'compositional: exact local dirty-block equality plus full baseline replay'}
        first_checks.append({'first':rec,'literal_word_sha256':S.digest(new),'block':block,'semantics':semantic})
        if (j+1)%20==0:print('DIRTY_FIRST_WORDS',tag,j+1,len(frame['states']),flush=True)
    trace=R.tracing(w);pair_blocks=[];trace_controls=0;bounds=S.corridor_bounds(w)
    for serial,state in enumerate(pair['states']):
        sec,i=state['section'],state['left_index'];g,h=w[sec][i:i+2]
        block=block_equal([g,h],[h,g]);pair_blocks.append([sec,i,block])
        if serial%101==0 or serial==len(pair['states'])-1:
            new=w.copy();new[sec]=w[sec].copy();new[sec][i:i+2]=[h,g]
            need(S.adjacent_trace(w,trace,sec,i)==R.tracing(new),'incremental trace differs')
            need(C.frame_bill(new)[:2]==C.frame_bill(w)[:2],'retained adjacent auditor differs')
            # Check the optimized third-gate reach filter against the unrestricted
            # enumerator at precisely this middle cut, including all dimensions.
            lo,hi=next((lo,hi) for lo,hi in R.segments(w,sec) if lo<=i<i+1<hi)
            def allowed(s,j,k):
                if not lo<=j<hi or j in (i,i+1) or k[0]!='add':return False
                low,up=bounds[s,j]
                return (up>=i and R.crosses(k,h)) if j<i else (low<=i+2 and R.crosses(k,g))
            fast=list(S.placements(new,sections=(sec,),gate_filter=allowed,target_cut=i+1,trusted_reach=True))
            slow=list(S.placements(new,sections=(sec,),gate_filter=lambda s,j,k:j not in (i,i+1),target_cut=i+1))
            need(fast==slow,'new-middle reach reduction differs from full scan')
            trace_controls+=1
    rejected_trace_controls=[]
    for sec in ('A','B','restore'):
        found=False
        for lo,hi in R.segments(w,sec):
            for i in range(lo,hi-1):
                g,h=w[sec][i:i+2]
                if g[0]!='add' or h[0]!='add' or not R.crosses(g,h):continue
                if S.adjacent_trace(w,trace,sec,i) is not None:continue
                new=w.copy();new[sec]=w[sec].copy();new[sec][i:i+2]=[h,g]
                rejected_trace_controls.append(rejects(lambda:R.tracing(new),'fresh rejected '+sec+' trace'))
                rejected_trace_controls.append(rejects(lambda:C.frame_bill(new),'retained rejected '+sec+' frame bill'))
                found=True;break
            if found:break
    positive,mid=positive_control(w)
    result={'provider':tag,'baseline':{'candidates':base['candidates'],'delta_types':len(base['deltas']),
                'own_enumerator_matches_all_multiplicities':True},
            'radius_two_neutral_prices':len(zero),'frame_changing_first':summarize(frame,True),
            'adjacent_swapped_gate_seconds':summarize(pair),
            'adjacent_third_gate_new_middle':summarize(novel),
            'first_dirty_checks':first_checks,'adjacent_dirty_block_checks':len(pair_blocks),
            'adjacent_block_stream_sha256':object_hash(pair_blocks),
            'fresh_trace_and_full_middle_cut_crosschecks':trace_controls,
            'rejected_incremental_trace_controls':rejected_trace_controls,
            'positive_control':positive,'controls':controls(w),'ledger':ledger(w)}
    print('PROVIDER_CHECKED',tag,'seconds',round(time.monotonic()-t,3),flush=True)
    return normal(result)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--provider',choices=('base','extra'),required=True)
    ap.add_argument('--write',action='store_true');ap.add_argument('--compositional-dirty',action='store_true',
        help='prove each first word by exact local dirty-block equality and complete baseline replay; omit 122 redundant whole-word interpreter runs')
    args=ap.parse_args();result=verify_provider(args.provider,not args.compositional_dirty)
    path=P/('CERTIFICATE-'+args.provider+'.json')
    if args.write:
        need(not args.compositional_dirty,'--write requires the full per-first-word interpreter replay')
        path.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    else:
        expected=json.loads(path.read_text())
        if args.compositional_dirty:
            for row in expected['first_dirty_checks']:row['semantics']={'status':'compositional: exact local dirty-block equality plus full baseline replay'}
        need(result==expected,'committed certificate differs')
    print(json.dumps({'status':'PASS_STAGED544_NEUTRAL_TWO_EDIT','provider':args.provider,
        'full_dirty_first_words':not args.compositional_dirty,'exact_local_dirty_blocks':len(result['first_dirty_checks']),
        'new_current_supplier':False},sort_keys=True))
