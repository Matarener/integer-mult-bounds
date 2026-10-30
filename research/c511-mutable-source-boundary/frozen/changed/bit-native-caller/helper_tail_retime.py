#!/usr/bin/env python3
"""Construct early BIT cleanup tails at actual common sub-FULL frames.

Moves only inverse-cleanup ADDs across exactly commuting ADDs; native frame
checks and complete arbitrary integer columns are replayed independently.
Apache-2.0. Prepared with substantial OpenAI Codex assistance.
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json
from cold_cosets import need,rankmod

HERE=Path(__file__).resolve().parent
BASE=Path('/Users/ross/git/math')
WORD=BASE/'.research-automation/runs/kappa-major-20261018T1330Z/bit-endpoint/BIT-FULL-COMPENSATION-WORD.json.gz'
RAW=BASE/'integer-mult-bounds/research/bit-r438-transport-rehost/words/r438-t154.json.gz'

def rankQ(rows):
    from fractions import Fraction as Q
    B={}
    for row in rows:
        v=list(map(Q,row))
        for j,b in sorted(B.items()):
            c=v[j]
            if c:v=[x-c*y for x,y in zip(v,b)]
        j=next((j for j,x in enumerate(v)if x),None)
        if j is not None:
            c=v[j];B[j]=[x/c for x in v]
    return len(B)

def plus(a,b,c):
    out=a.copy()
    for j,v in b.items():
        out[j]=out.get(j,0)+c*v
        if not out[j]:del out[j]
    return out

def replay(program,raw,initial=None,back=False):
    n=651;frames=(program['final']if back else program['start'])[:]
    rows=[{j:1}for j in range(n)]if initial is None else[r.copy()for r in initial]
    masks=[sum(1<<j for j in f)for f in raw['frames']]
    dims=[rankQ(raw['lines'][j]for j in f)for f in raw['frames']]
    H=Counter();prefix=1;adds=0
    for op,d,s,c,f,ph in reversed(program['records'])if back else program['records']:
        if op==0:
            old,new=(c,s)if back else(s,c)
            lo,hi=(new,old)if back else(old,new)
            need(frames[d]==old and not masks[lo]&~masks[hi]and dims[hi]-dims[lo]==f>0,'native MOVE exact frame/containment/rank')
            frames[d]=new;H[f]+=1
        else:
            need(op==1 and d!=s and frames[d]==frames[s]==f,'common-frame ADD')
            rows[d]=plus(rows[d],rows[s],-c if back else c);adds+=1
            prefix=max(prefix,sum(abs(x)for x in rows[d].values()))
    need(frames==(program['start']if back else program['final']),'all native endpoint frames')
    return rows,{'H':dict(sorted(H.items())),'mass':sum(k*v for k,v in H.items()),'ADDs':adds,'prefix_row_L1':prefix}

def build(base,raw):
    records=[r[:]for r in base['records']];dims=[rankQ(raw['lines'][j]for j in f)for f in raw['frames']]
    selected=[(i,r)for i,r in enumerate(records)if r[0]==1 and r[-1]==5]
    moved=[]
    for i,g in selected:
        need(records[i]is g,'earlier leftward moves preserve unprocessed positions')
        _,d,s,c,f,ph=g;fd=fs=f;best=None
        for j in range(i-1,-1,-1):
            r=records[j]
            if fd==fs and dims[fd]<=7:best=(j+1,fd)
            if r[0]==1:
                _,a,b,_,_,_=r
                if a==s or b==d:break
            else:
                need(r[0]==0,'no private opcode in input')
                if r[1]==d:need(fd==r[3],'reverse destination frame');fd=r[2]
                if r[1]==s:need(fs==r[3],'reverse source frame');fs=r[2]
            if j==0 and fd==fs and dims[fd]<=7:best=(0,fd)
        if best is not None:
            k,nf=best
            need(k<i and dims[nf]<8,'strictly earlier sub-FULL cleanup')
            g[4]=nf;records.pop(i);records.insert(k,g)
            moved.append({'old_index':i,'new_index':k,'dst':d,'src':s,'coefficient':c,'new_frame':nf,'new_rank':dims[nf]})
    removable=[];final=base['final'][:]
    for h in range(222,651):
        moves=[i for i,r in enumerate(records)if r[0]==0 and r[1]==h]
        i=moves[-1];r=records[i]
        need(r[3]==1,'old helper endsFULL')
        if any(z[0]==1 and h in(z[1],z[2])for z in records[i+1:]):continue
        final[h]=r[2];removable.append((i,h,r[2],r[4]))
    dead={i for i,_,_,_ in removable};records=[r for i,r in enumerate(records)if i not in dead]
    out=dict(base);out['records']=records;out['final']=final;out['format']='R429-retimed-commuting-cleanup-helper-endpoints-v1'
    return out,moved,removable

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');args=ap.parse_args()
    need(sha256(WORD.read_bytes()).hexdigest()=='0f461dbc7e82a02faedb4a5129103963507c9f063a0a3679ba5d20ad94df160e','frozen full box')
    need(sha256(RAW.read_bytes()).hexdigest()=='a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022','frozen geometry')
    base=json.loads(gzip.decompress(WORD.read_bytes()));raw=json.loads(gzip.decompress(RAW.read_bytes()))
    new,moved,removed=build(base,raw)
    oldrows,oldrec=replay(base,raw);rows,rec=replay(new,raw)
    need(rows==oldrows,'all651 arbitrary signed integer columns unchanged by cleanup retiming')
    need(all(rows[h]=={h:1}for h in list(range(111))+list(range(222,651))),'all non-target integer identities')
    closed,backrec=replay(new,raw,rows,True)
    need(closed==[{j:1}for j in range(651)],'literal integer inverse all651 columns')
    widths=Counter(rankQ(raw['lines'][j]for j in raw['frames'][f])for f in new['final'][222:])
    need(oldrec['mass']-rec['mass']==sum(d for _,_,_,d in removed),'all removed native mass accounted')
    canonical=json.dumps(new,sort_keys=True,separators=(',',':')).encode()
    out={'status':'PASS_LITERAL_R429_COMMUTING_CLEANUP_RETIME','no_new_kappa':True,
         'sources':{str(p):sha256(p.read_bytes()).hexdigest()for p in(WORD,RAW)},
         'moved_cleanup_ADDs':moved,'removed_helper_FULL_MOVEs':removed,'helper_terminal_width_histogram':dict(sorted(widths.items())),
         'old_profile':oldrec,'new_profile':rec,'literal_inverse_profile':backrec,
         'word_canonical_sha256':sha256(canonical).hexdigest(),
         'contract':'Every source and target boundary is inherited from the zero-private FULL compensation box. All429 helpers enter atZERO. A helper with its final FULL MOVE deleted instead exits at the explicitly listed old preceding frame U_h. The residual is native D_Uh, not full width8. Every integer source/helper row is identity; target map is exactly the same signed map as the frozen word.',
         'price':'Only exact commuting cleanup retiming and removal of unused terminal native MOVEs. No added COPY, ERASE, private field or scalar ADD. Lost helper native progress equals removed query mass, so the old uncovered deficit is unchanged. A changed owner stock/window and complete moment must be rebuilt.',
         'limits':['Greedy fixed-source/target construction; no optimal cleanup claim.','No chronological owner admission, rounded suffix-error proof or source/tape invoice.','A changed local helper histogram alone is not a new conditional exponent.']}
    out=json.loads(json.dumps(out));path=HERE/'HELPER-TAIL-RETIME.json';wp=HERE/'HELPER-TAIL-RETIME-WORD.json.gz'
    if args.write:
        path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');wp.write_bytes(gzip.compress(canonical,mtime=0))
    else:
        need(json.loads(path.read_bytes())==out,'saved helper-tail receipt differs')
        need(gzip.decompress(wp.read_bytes())==canonical,'saved helper-tail word differs')
    print(out['status']);print('moved',len(moved),'cleanup ADDs; narrowed',len(removed),'helpers;',dict(widths),'mass',rec['mass'])

if __name__=='__main__':main()
