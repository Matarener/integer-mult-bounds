#!/usr/bin/env python3
"""Source-bound COPY lifetime audit; exact sparse row/frame evaluator."""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import argparse, copy, hashlib, importlib.util, json
P=Path(__file__).resolve().parent
ROOT=P.parents[1]
WIT='research/p104-native-channel/inputs/LOWRANK-WITNESS.json'
WIT_HASH='0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e'

def need(ok,msg):
    if not ok: raise ValueError(msg)

def load(path):
    def pairs(items):
        out={}
        for k,v in items:
            need(k not in out,'duplicate JSON key: '+k)
            out[k]=v
        return out
    return json.loads(path.read_text(),object_pairs_hook=pairs)

def encoded(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'))

def span(vs):
    out={0}
    for v in vs: out |= {x^v for x in tuple(out)}
    return frozenset(out)

def add(a,b,c):
    out=dict(a)
    for k,v in b.items():
        out[k]=out.get(k,F(0))+c*v
        if not out[k]: del out[k]
    return out

def replay(word):
    rows={k:{k:F(1)} for k in word['initial_frames']}
    frames={k:span(v) for k,v in word['initial_frames'].items()}
    private=[]; paid=Counter(); counts=Counter(); snapshots={}
    for i,e in enumerate(word['program']):
        op,r=e[:2];counts[op]+=1
        if op=='transport':
            _,r,a,b,n=e;aa,bb=span(a),span(b)
            need(frames[r]==aa,'transport entrance')
            need(aa<=bb or bb<=aa,'non-nested transport')
            need(n==abs(len(a)-len(b)) and len(aa)==2**len(a) and len(bb)==2**len(b),'rank tariff')
            frames[r]=bb;paid[n]+=1
        elif op=='zero':
            need(r=='C' and r not in rows,'fresh owned private')
            rows[r]={};frames[r]=span(e[2]);private.append({'zero':i})
        elif op=='copy':
            _,r,s,f=e;need(r=='C' and not rows[r] and frames[r]==frames[s]==span(f),'copy ownership/zero/common chart')
            rows[r]=dict(rows[s]);private[-1].update(copy=i,source=s,copy_row=dict(rows[s]),frame=list(f))
        elif op=='erase':
            need(r=='C' and frames[r]==span(e[2]),'private erase owner/chart')
            private[-1].update(erase=i,erase_row=dict(rows[r]),end_frame=e[2]);del rows[r];del frames[r]
        elif op=='add':
            _,r,s,c,f=e;need(r!=s and frames[r]==frames[s]==span(f),'common-chart addition')
            rows[r]=add(rows[r],rows[s],F(c))
        else:raise ValueError('unknown event')
        if i in (2460,2524,3641,4057):snapshots[i]=copy.deepcopy(rows)
    need(set(rows)==set(word['initial_frames']),'private owner leaked')
    need(all(frames[k]==span(f) for k,f in word['final_frames'].items()),'final frame')
    return rows,dict(paid),dict(counts),private,snapshots

def intervals(word):
    starts=[i for i,e in enumerate(word['program']) if e[0]=='zero']
    ans=[]
    for i in starts:
        j=next(k for k in range(i,len(word['program'])) if word['program'][k][0]=='erase')
        block=word['program'][i:j+1]
        need([e[0] for e in block[:3]]==['zero','copy','transport'],'copy prefix')
        need(all(e[0]=='add' and e[2]=='C' and e[3]==1 for e in block[3:-1]),'private donor only')
        ans.append((i,j,block))
    need(len(ans)==8,'eight intervals')
    return ans

def rewrite(word,mode):
    out=copy.deepcopy(word);schedule=[];last=0
    for a,b,block in intervals(word):
        schedule.extend(word['program'][last:a]);last=b+1
        if mode=='remove':continue
        q=block[1][2];hi=block[2][2];lo=block[2][3]
        schedule.append(['transport',q,hi,lo,7])
        schedule.extend(['add',e[1],q,e[3],e[4]] for e in block[3:-1])
        if mode!='no_restore':schedule.append(['transport',q,lo,hi,7])
    schedule.extend(word['program'][last:]);out['program']=schedule
    return out

def rank(rows):
    a=[dict(r) for r in rows if r];piv={}
    for row in a:
        while row:
            k=min(row)
            if k in piv:row=add(row,piv[k],-row[k])
            else:
                c=row[k];piv[k]={j:v/c for j,v in row.items()};break
    return len(piv)

def tail_module():
    path=P/'inputs/pr3882_verify.py'
    pins=load(P/'SOURCES.json')['source_exports']
    need(hashlib.sha256(path.read_bytes()).hexdigest()==pins[0]['sha256'],'frozen tail builder')
    spec=importlib.util.spec_from_file_location('frozen3882',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    return m

def continue_tail(rows,mod):
    _,A,J,N,B=mod.geometry();ops=mod.program(J,N,B)
    names=[f'X{i}' for i in range(104)]+[f'Y{i}' for i in range(104)]+[f'Q{i}' for i in range(8)]+[f'G{i}' for i in range(32)]+[f'D{i}' for i in range(32)]
    out=[dict(rows[k]) for k in names];frames=[9]*104+[8]*104+[9]*72
    for e in ops:
        op,r=e[:2]
        if op in ('lift','drop'):
            need(frames[r]==(8 if op=='lift' else 9),'tail frame');frames[r]=9 if op=='lift' else 8
        elif op=='add':
            s,c=e[2:];need(frames[r]==frames[s]==9,'tail common full');out[r]=add(out[r],out[s],F(c))
        else:
            need(op in ('half','double') and frames[r]==9,'tail scalar');c=F(1,2) if op=='half' else F(2);out[r]={k:c*v for k,v in out[r].items()}
    return dict(zip(names,out)),J,N,B

def calculate():
    raw=(ROOT/WIT).read_bytes();need(hashlib.sha256(raw).hexdigest()==WIT_HASH,'frozen witness')
    w=json.loads(raw);base,p0,c0,lives,snaps=replay(w)
    new,p1,c1,lp,_=replay(rewrite(w,'direct'))
    need(new==base and not lp,'direct route restores every row')
    need(sum(k*v for k,v in p0.items())==2368,'original invoice')
    need(sum(k*v for k,v in p1.items())==2424,'replacement invoice')
    need(c1=={'add':2624,'transport':1418},'replacement event invoice')
    need(p1==dict(Counter(p0)+Counter({7:8})),'only extra eight rank7 returns')
    deleted,_,_,_,_=replay(rewrite(w,'remove'))
    delta={k:add(deleted[k],base[k],-1) for k in base}
    need(rank(delta.values())==8,'deletion defect rank eight')
    need(all(not delta[k] for k in base if k[0] in 'XQG'),'deletion preserves X/Q/G only')
    need(sum(bool(delta[k]) for k in base if k.startswith('D'))==32,'all32 delivery helpers retain defect')
    dirty=[[delta[f'Y{i}'].get(f'Q{j}',F(0)) for j in range(8)] for i in range(104)]
    need(rank([{str(j):v for j,v in enumerate(row) if v} for row in dirty])==8,'eight independent dirty counterexamples')
    m=tail_module();after,J,N,B=continue_tail(base,m);bad,_,_,_=continue_tail(deleted,m);fixed,_,_,_=continue_tail(new,m)
    need(after==fixed,'actual downstream continuation unchanged')
    A=m.geometry()[1]
    for i in range(104):
        need(base[f'X{i}']=={f'X{i}':F(1)},'baseline source restored')
        expected={f'Y{i}':F(1)}
        expected.update({f'X{j}':v for j,v in enumerate(A[i]) if v})
        need(base[f'Y{i}']==expected,'baseline Gram channel')
        slot=f'Y{i}' if i in J else f'X{i}'
        need(after[slot]=={f'X{i}':F(1),f'Y{i}':F(1)},'actual sum output')
    dpost={k:add(bad[k],after[k],-1) for k in after}
    need(rank(dpost.values())==8,'actual tail preserves deletion defect rank')
    sums=[f'Y{i}' if i in J else f'X{i}' for i in range(104)]
    need(rank([dpost[k] for k in sums])==8,'all sum outputs still expose rank8 defect')
    need(all(after[k]=={k:F(1)} for k in after if k[0] in 'QGD'),'72 dirty returns')
    need(sum(bad[k]!=after[k] for k in after if k[0] in 'QGD')==32,'deletion breaks32 dirty returns')
    records=[]
    for (a,b,block),life in zip(intervals(w),lives):
        q=life['source'];row=life['copy_row'];need(life['erase_row']==row and row.get(q)==1,'live dirty private is not zero')
        need(all(k==q or k.startswith('X') for k in row),'query has no other dirty inputs')
        need(all(row.get(f'Q{j}',0)==int(q==f'Q{j}') for j in range(8)),'independent dirty copy')
        need(all(e[1]!=q for e in w['program'][b+1:3570]),'query available untouched until full lift')
        donors=[e[1] for e in block[3:-1]]
        need(all(delta[d]=={k:-v for k,v in row.items()} for d in donors),'exact D deletion defect minus copied query')
        first_read={d:next(i for i in range(b+1,len(w['program'])) if w['program'][i][0]=='add' and w['program'][i][2]==d) for d in donors}
        records.append({'query':q,'zero':a,'copy':a+1,'drop':a+2,'last_read':b-1,'erase':b,'delivery_helpers':donors,'first_downstream_reads':first_read,'fixed_cleanup_events':{d:next(i for i in range(3578,len(w['program'])) if w['program'][i][0]=='add' and w['program'][i][1]==d) for d in donors},'query_source_coefficients':{k:str(v) for k,v in row.items() if k!=q},'nonzero_private_at_erase':True})
    need(sum(len(r['delivery_helpers']) for r in records)==32,'32 actual consumers')
    return {'schema_version':1,'scope':'literal private COPY retirement and direct-query replacement; no supplier','events_before':4058,'events_after':4042,'lifetime_records':records,'baseline_profile':p0,'replacement_profile':p1,'baseline_mass':2368,'replacement_mass':2424,'net_extra_mass':56,'private_allocations_after':0,'private_erases_after':0,'private_copies_after':0,'replacement_transports':1418,'replacement_adds':2624,'deletion_defect_rank':8,'deletion_sum_defect_rank_after_actual_3882_tail':8,'arbitrary_dirty_inputs':72,'broken_dirty_returns_on_deletion':32,'combined_3882_mass':2576,'direct_query_combined_mass':2632,'two_axis_calls':208,'two_axis_original_gap':44096,'two_axis_direct_query_gap':55744,'two_axis_all_correction_forgiven_original_gap':832,'two_axis_all_correction_forgiven_direct_query_gap':12480,'native_retirement_general_lower_bound_claimed':False}

def controls():
    w=json.loads((ROOT/WIT).read_text());n=0
    for kind in ('no_restore','dirty_erase','premature_erase','bad_rank'):
        x=rewrite(w,'no_restore') if kind=='no_restore' else copy.deepcopy(w)
        if kind=='dirty_erase':x['program'][2469]=['erase','Q0',x['program'][2469][2]]
        if kind=='premature_erase':x['program'][2464],x['program'][2469]=x['program'][2469],x['program'][2464]
        if kind=='bad_rank':x['program'][2463][4]=0
        try:replay(x)
        except (ValueError,KeyError):n+=1
        else:raise ValueError('control accepted '+kind)
    return n

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write-result',action='store_true');args=ap.parse_args()
    result=calculate();need(controls()==4,'controls')
    raw=json.dumps(result,sort_keys=True,indent=2)+'\n'
    if args.write_result:(P/'RESULT.json').write_text(raw)
    else:need(encoded(result)==encoded(load(P/'RESULT.json')),'typed result mismatch')
    print('PASS_P104_COPY_RETIREMENT rank_defect=8 replacement_mass=2424 dirty=72 controls=4')
if __name__=='__main__':main()
