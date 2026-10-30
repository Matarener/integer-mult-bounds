#!/usr/bin/env python3
"""Exact R437 chronological carrier exchange. Chris R / Codex, Apache-2.0."""
import argparse
from collections import Counter
from copy import deepcopy
import gzip
import hashlib
import json
import math
from pathlib import Path

P = Path(__file__).resolve().parent
class Reject(Exception): pass
def need(test, message):
    if not test: raise Reject(message)
def canon(obj): return json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()
def xor(values):
    z = 0
    for x in values: z ^= x
    return z
def raw(w):
    rows = [1 << r for r in range(659)]
    for f,d,ss in w['A']: rows[d] ^= xor(rows[s] for s in ss)
    caps = [rows[r] for r in w['ret']]
    for t,js in enumerate(w['scatter']): rows[111+t] ^= xor(caps[j] for j in js)
    for f,d,ss in w['B']: rows[d] ^= xor(rows[s] for s in ss)
    return rows, caps
def build_control(w):
    c = deepcopy(w); gates = []
    need(w['A'][229] == [94,469,[92]], 'old source92 carrier birth')
    need(w['A'][1998:2001] == [[186,444,[77]],[509,444,[17,271,293,352,413,467,469]],[509,413,[17,271,293,352,371,469]]], 'old node509')
    for i,g in enumerate(w['A']):
        if i == 229: gates.extend([[79,469,[77]],[94,444,[92]]])
        elif i == 1998: pass
        elif i == 1999:
            gates.extend([[509,468,[413]],[509,444,[413,469,17,271,293,352,467]],[509,413,[444,469,467,371]]])
        elif i == 2000: pass
        else: gates.append(g)
    c['A'] = gates
    c['C'] = [[1,d,ss] for f,d,ss in reversed(c['A']+c['B']) if not 111 <= d < 222]
    rr,_ = raw(c)
    need(all(rr[111+t]&((1<<222)-1) == (1<<t)^(1<<(111+t)) for t in range(111)), 'raw SOURCE and TARGET blocks')
    c['D'] = [[0,111+t,[s for s in range(222,659) if rr[111+t]>>s&1]] for t in range(111)]
    return c
def normalize(v):
    g = math.gcd(*v)
    if not g: return tuple(v)
    s = 1 if next(x for x in v if x)>0 else -1
    return tuple(s*x//g for x in v)
def reduce_q(v, bs):
    v = tuple(v)
    for j,row in bs:
        if v[j]: v = normalize([row[j]*a-v[j]*b for a,b in zip(v,row)])
    return v
def geometry(w):
    dims=[]
    for f in w['frames']:
        bs=[]
        for i in f:
            row=reduce_q(w['lines'][i],bs)
            if any(row): bs.append((next(j for j,x in enumerate(row) if x),normalize(row))); bs.sort()
        need([i for i,row in enumerate(w['lines']) if not any(reduce_q(row,bs))] == f, 'exact rational closed frame')
        dims.append(len(bs))
    return dims
def ledger(w, dims):
    frames = list(map(set,w['frames'])); cur=w['start'][:]
    rows=[1<<r for r in range(659)]; paths=[[f] for f in cur]
    profile=Counter(); adds=0; snapshots={}; caps=[]; source_writes=[]
    def move(r,f):
        need(frames[cur[r]]<=frames[f], 'frame descent role '+str(r))
        if cur[r]!=f:
            k=dims[f]-dims[cur[r]]; need(k>0,'strict positive frame step')
            profile[k]+=1; paths[r].append(f); cur[r]=f
    for sec in ['D','A','B','C']:
        if sec=='B':
            need(all(cur[r]==0 for r in range(111,222)), 'targets stay zero-frame until scatter')
            caps=[rows[r] for r in w['ret']]
            for r in w['ret']: profile[dims[cur[r]]]+=1
            for t,js in enumerate(w['scatter']): rows[111+t]^=xor(caps[j] for j in js); adds+=len(js)
        for i,(f,d,ss) in enumerate(w[sec]):
            for r in [d]+ss: move(r,f)
            rows[d]^=xor(rows[s] for s in ss); adds+=len(ss)
            if d<111: source_writes.append([sec,f,d,rows[d]])
            if sec=='A' and ((f==509 and d in [413,444,468]) or (d==413 and f==517)):
                snapshots[str(i)]=[hex(rows[r]&((1<<111)-1)) for r in [444,413,468]]
    for r,f in enumerate(w['final']): move(r,f)
    expected=[(1<<r)^((1<<(r-111)) if 111<=r<222 else 0) for r in range(659)]
    need(rows==expected,'full arbitrary-DIRTY 659-column identity')
    rr,_=raw(w); is_y=lambda r:111<=r<222
    h=[all(not is_y(s) for sec in ['D','A','B','C'] for f,d,ss in w[sec] if not is_y(d) for s in ss),
       all(f==0 and is_y(d) and all(s>=222 for s in ss) for f,d,ss in w['D']),
       all(not is_y(d) for f,d,ss in w['A']) and all(r>=222 for r in w['ret']),
       w['C']==[[1,d,ss] for f,d,ss in reversed(w['A']+w['B']) if not is_y(d)],
       all(rr[111+t]&(((1<<111)-1)<<111)==1<<(111+t) for t in range(111))]
    need(all(h),'H1-H5')
    return {'profile':dict(sorted(profile.items())), 'rank_mass':sum(r*n for r,n in profile.items()),
            'children':sum(profile.values()),'adds':adds,'paths':paths,
            'capture_source_rows':[hex(x&((1<<111)-1)) for x in caps],
            'source_writes':source_writes,'snapshots':snapshots,'hypotheses':h}
def audit_control(w,c):
    need(c==build_control(w),'exact declared transformation')
    dims=geometry(w); old=ledger(w,dims); new=ledger(c,dims)
    delta=Counter(new['profile']);delta.subtract(old['profile']);delta={k:v for k,v in delta.items() if v}
    need(delta=={1:1,2:-2,3:3,6:-1},'paid rank split')
    need(old['rank_mass']==new['rank_mass']==5113,'same paid rank mass')
    need(new['adds']==old['adds']-2==24206,'two fewer complete-word scalar ADDs')
    changed=[r for r in range(659) if old['paths'][r]!=new['paths'][r]]
    need(changed==[444,468,469],'three changed role frame paths')
    need(old['source_writes']==new['source_writes'],'all full SOURCE write states unchanged')
    need(old['capture_source_rows']==new['capture_source_rows'],'nine COPY source rows unchanged')
    need(sum(a!=b for a,b in zip(w['D'],c['D']))==55,'55 recomputed dirty compensation rows')
    uses=[(s,i,f,d,ss) for s in ['A','B'] for i,(f,d,ss) in enumerate(w[s]) if 468 in [d]+ss]
    need(uses==[('A',228,52,468,[50]),('A',2035,517,413,[468])],'sole later observation of debt bank')
    # Actual obstruction to deleting the replacement SOURCE77 relay in this word.
    f=list(map(set,w['frames']))
    need(not f[94]<=f[186] and not f[184]<=f[186], 'early92 then original77 is not monotone')
    need(w['B'][35]==[186,149,[77]] and not f[509]<=f[186], 'late direct77 spoils pinned B35')
    return {'status':'PASS_R437_ACTUAL_TWO_WINDOW_EXCHANGE_NO_KAPPA_GAIN',
            'source_word_sha256':hashlib.sha256(canon(w)).hexdigest(),
            'candidate_sha256':hashlib.sha256(canon(c)).hexdigest(),
            'columns':659,'closed_frames':len(dims),'helpers':437,
            'old_profile':old['profile'],'new_profile':new['profile'],'profile_delta':delta,
            'rank_mass':new['rank_mass'],'old_children':old['children'],'new_children':new['children'],
            'old_adds':old['adds'],'new_adds':new['adds'],
            'changed_paths':{r:{'old':old['paths'][r],'new':new['paths'][r]} for r in changed},
            'all_SOURCE_write_states_unchanged':True,'nine_COPY_source_rows_unchanged':True,
            'old_snapshots':old['snapshots'],'new_snapshots':new['snapshots'],
            'debt_bank_old_observations':uses,'H1_H5':new['hypotheses'],
            'moment_delta_per_288_calls':'288*(1+3*3**(1-a)-2*2**(1-a)-6**(1-a))/(W*64**(1-a)) > 0 for W>0 and 0<a<1',
            'scope':'actual complete scalar/frame word; conditional local primitive interface, no compiled pooled supplier or new kappa'}
def build(w):
    c=deepcopy(w); gates=[]
    for i,g in enumerate(w['A']):
        if i==229:gates.extend([[79,469,[77]],[94,444,[92]]])
        elif i==1998:pass
        elif i==1999:gates.extend([[509,467,[413]],[509,413,[444,17,271,293,352,371]],[509,444,[467,469,17,271,293,352]]])
        elif i==2000:pass
        else:gates.append(g)
    c['A']=gates;c['B']=w['B'][:69]+[[509,467,[87]]]+w['B'][69:]
    c['C']=[[1,d,ss] for f,d,ss in reversed(c['A']+c['B']) if not 111<=d<222]
    rr,_=raw(c)
    need(all(rr[111+t]&((1<<222)-1)==(1<<t)^(1<<(111+t)) for t in range(111)),'new raw SOURCE and TARGET blocks')
    c['D']=[[0,111+t,[s for s in range(222,659) if rr[111+t]>>s&1]] for t in range(111)]
    return c

def audit(w,c):
    need(c==build(w),'exact constructive467 rewrite')
    dims=geometry(w);old=ledger(w,dims);new=ledger(c,dims)
    delta=Counter(new['profile']);delta.subtract(old['profile']);delta={k:n for k,n in delta.items() if n}
    need(delta=={1:1,2:-2,3:1},'strictly favorable complete local rank delta')
    need(old['rank_mass']==new['rank_mass']==5113 and old['children']==new['children']==2915,'same rank mass and number of children')
    need(new['adds']==old['adds']+3==24211,'complete scalar ADD charge')
    need(old['capture_source_rows']==new['capture_source_rows'],'all nine SOURCE capture rows')
    need(old['source_writes']==new['source_writes'],'all full SOURCE write states')
    changed=[r for r in range(659) if old['paths'][r]!=new['paths'][r]]
    need(changed==[444,469],'only receiver444 and repurposed469 paths change')
    need(sum(a!=b for a,b in zip(w['D'],c['D']))==55,'55 changed dirty rows')
    uses=[i for i,(f,d,ss) in enumerate(w['B']) if 87 in [d]+ss]
    need(uses[:2]==[68,283] and w['B'][68]==[189,188,[87]] and w['B'][283]==[509,87,[92]],'actual cleanup window endpoints')
    need(c['B'][69]==[509,467,[87]],'cleanup exactly after B68')
    return {'status':'PASS_R437_467_TWO_WINDOW_STRICT_LOCAL_MOMENT_GAIN',
        'candidate_sha256':hashlib.sha256(canon(c)).hexdigest(),'columns':659,'closed_frames':636,'helpers':437,
        'old_profile':old['profile'],'new_profile':new['profile'],'profile_delta':delta,'rank_mass':5113,'children':2915,
        'old_adds':24208,'new_adds':24211,'D_changed_rows':55,
        'changed_paths':{r:{'old':old['paths'][r],'new':new['paths'][r]} for r in changed},
        'all_SOURCE_write_states_unchanged':True,'nine_COPY_source_rows_unchanged':True,'H1_H5':new['hypotheses'],
        'cleanup_after_old_B':68,'next_SOURCE87_use_old_B':283,
        'moment_delta_per_288_calls':'288*(1+3**(1-a)-2*2**(1-a))/(W*64**(1-a)) < 0 for W>0 and 0<a<1',
        'scope':'exact local scalar/frame word; complete physical/native/stock/pooled caller obligations remain open; selected kappa unchanged'}

def load():
    for row in json.loads((P/'RETAINED.json').read_text())['files']:
        b=(P/row['path']).read_bytes()
        need(hashlib.sha256(b).hexdigest()==row['sha256'],'retained source hash')
        need(hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==row['git_blob'],'retained Git blob')
    return json.loads(gzip.decompress((P/'inputs/R437-COMPOSED-WORD.json.gz').read_bytes()))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write');args=ap.parse_args()
    w=load();result=audit(w,json.loads((P/'CANDIDATE.json').read_text()))
    control=audit_control(w,json.loads((P/'LOSING-CONTROL.json').read_text()))
    need(canon(control)==canon(json.loads((P/'LOSING-CONTROL-RESULT.json').read_text())),'preserved losing control')
    if args.write: Path(args.write).write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    else: need(canon(result)==canon(json.loads((P/'RESULT.json').read_text())),'immutable receipt equality')
    print(result['status'], 'columns=659 frames=636 ADD_delta=+3 children_delta=0 rank_mass_delta=0 strict_local_moment_gain' )
if __name__=='__main__':
    try:main()
    except (Reject,OSError,ValueError,KeyError) as e: raise SystemExit('FAIL: '+str(e))
