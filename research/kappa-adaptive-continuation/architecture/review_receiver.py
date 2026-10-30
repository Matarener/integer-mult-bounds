#!/usr/bin/env python3
"""Independent bounded review of the emitted helper544 receiver rewrite.

Imports neither the constructor nor its scalar, frame or cleanup helpers.
Rechecks literal edit preimages, all native frame paths, frame-rank billing,
dirty three-register identity, no intervening receiver observer, and exact
inverse cleanup syntax for both providers. The heavy native phase/operator
replay and complete global invoice are separate receipts.
Apache-2.0; substantial OpenAI assistance.
"""
from argparse import ArgumentParser
from collections import Counter,defaultdict
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import json

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
SOURCE=REPO/'research/kappa-global-continuation/inputs/kappa-consumer-followup/artifact/live-source/research/staged544-producer-return/words'
CANDIDATE=HERE.parent/'native-alternatives/candidate'
PINS={
 'base':'5ca4be99851f8878cbfe0fd6c454df926b11218f17feefa1664721cf03156699',
 'extra':'965268a9be73d3f62e7ef680d18f108cf064bfe1f44b82157baa61443232904e',
}
OLD=[['add',672,544,1,2,[414,51]],['add',676,544,-1,2,[414,51]]]
NEW=[['add',672,676,1,1,[51]],OLD[1],['add',672,676,-1,1,[413,72,48,3]]]


def need(ok,why):
    if not ok:raise ValueError(why)


def read(path):
    raw=path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)


def span(vectors):
    result={0}
    for vector in vectors:result|={x^vector for x in result.copy()}
    return frozenset(result)


def rank(subspace):
    need(len(subspace)&(len(subspace)-1)==0,'power-of-two span size')
    return len(subspace).bit_length()-1


def expanded(word):
    by=defaultdict(list)
    for number,(at,reg,operator,source,target) in enumerate(word['warps'],1):
        by[at].append(['warp',reg,number,source,target])
    events=[]
    for at,event in enumerate(word['B']):
        events.extend(by[at]);events.append(event)
    events.extend(by[len(word['B'])])
    return [('A',word['A']),('B',events),('restore',word['restore'])]


def frames(word):
    live=[r for r in range(704) if r not in set(word['removed'])]
    full=span([1<<j for j in range(9)])
    initial={r:span([word['ports'][r]]) if r<112 else span(word['start_extra'].get(str(r),[])) for r in live}
    final={r:(span([x for x in range(512) if (x&word['ports'][r-112]).bit_count()%2==0])
              if 112<=r<224 else full) for r in live}
    final.update({int(r):span(basis) for r,basis in word['helper_final'].items()})
    current=initial.copy();paid={r:Counter() for r in live};transitions={r:[] for r in live}
    def touch(reg,target,position):
        need(current[reg]<=target,'native frame path must be monotone')
        difference=rank(target)-rank(current[reg])
        if difference:
            paid[reg][difference]+=1
            transitions[reg].append([position,rank(current[reg]),rank(target)])
        current[reg]=target
    for name,events in expanded(word):
        for i,event in enumerate(events):
            if event[0]=='warp':
                reg=event[1];source=span(event[3]);target=span(event[4])
                need(current[reg]==source and rank(source)==rank(target),'exact frame at retained warp')
                current[reg]=target
            else:
                need(event[0] in ('add','scale'),'native scalar grammar')
                target=span(event[-1])
                for reg in event[1:3] if event[0]=='add' else event[1:2]:
                    touch(reg,target,[name,i])
        if name=='A':
            need(all(current[r]==span(f) for r,f in zip(word['centers'],word['center_frames'])),'actual centre frame boundary')
    for reg in live:touch(reg,final[reg],['terminal',0])
    return initial,final,paid,transitions


def scalar(events):
    ids=[544,672,676]
    M=[[Q(int(i==j)) for j in range(3)] for i in range(3)]
    for e in events:
        target,source=ids.index(e[1]),ids.index(e[2]);q=Q(e[3],e[4])
        M[target]=[x+q*y for x,y in zip(M[target],M[source])]
    return M


def cleanup(word):
    full=[256,128,64,32,16,8,4,2,1]
    hpe=set(map(int,word['helper_final']))
    role=lambda r:r+704 if r in hpe else r
    sections=expanded(word)
    events=sections[0][1][word['prelude_events']:]+sections[1][1]+sections[2][1]
    answer=[]
    for e in reversed(events):
        if 112<=e[1]<224 and e[0]!='warp':continue
        if e[0]=='warp':answer.append(['warp',role(e[1]),-e[2],full])
        elif e[0]=='add':answer.append(['add',role(e[1]),role(e[2]),-e[3],e[4],full])
        else:answer.append(['scale',role(e[1]),e[3],e[2],full])
    return answer


def run(source,candidate,out):
    results={}
    sources=[Path(__file__)]
    expected=[[Q(1),Q(0),Q(0)],[Q(1,2),Q(1),Q(0)],[Q(-1,2),Q(0),Q(1)]]
    need(scalar(OLD)==scalar(NEW)==expected,'exact three-register map on arbitrary dirty inputs')
    wrong=[list(e) for e in NEW];wrong[2]=list(wrong[2]);wrong[2][3]=1
    need(scalar(wrong)!=expected,'wrong final receiver sign rejected')
    P,Qf,R=span([51]),span([414,51]),span([413,72,48,3])
    need(P<Qf<R and [rank(P),rank(Qf),rank(R)]==[1,2,4],'actual nested receiver frames')
    for tag in ('base','extra'):
        oldpath=source/f'BORROW-WORD-43{tag}.json.gz'
        newpath=candidate/oldpath.name
        need(sha256(oldpath.read_bytes()).hexdigest()==PINS[tag],'authenticated complete provider source')
        old,new=read(oldpath),read(newpath)
        need(old['B'][692:694]==OLD and new['B'][692:695]==NEW,'actual emitted preimages and rewrite')
        need(old['B'][:692]==new['B'][:692] and old['B'][694:]==new['B'][695:],'all other B scalar events unchanged')
        expected_warps=[]
        for warp in old['warps']:
            item=list(warp);item[0]+=int(item[0]>=694);expected_warps.append(item)
        need(new['warps']==expected_warps,'literal warp positions adjusted once')
        need(all(old[k]==new[k] for k in old if k not in ('B','warps','cleanup','report')),'all other native payloads unchanged')
        need(old['cleanup']==cleanup(old) and new['cleanup']==cleanup(new),'complete owned-buffer inverse cleanup syntax')
        oi,of,op,ot=frames(old);ni,nf,np,nt=frames(new)
        need(oi==ni and of==nf,'every source and output frame unchanged')
        delta={}
        for reg in op:
            d=np[reg].copy();d.subtract(op[reg]);d={r:n for r,n in d.items() if n}
            if d:delta[reg]=d
        need(delta=={672:{1:-1,2:-1,3:1}},'complete independent native rank-path delta')
        widths=[rank(of[r])-rank(oi[r]) for r in oi if r>=224]
        need(Counter(widths)=={4:26,5:2,6:18,7:53,8:96,9:213},'literal helper stock unchanged')
        late_contacts={}
        for receiver,source_pos in ((672,692),(676,693)):
            hit=next((i,e) for i,e in enumerate(old['B']) if i>source_pos and
                     (e[1]==receiver or(e[0]=='add' and e[2]==receiver)))
            need(span(hit[1][-1])==R,'next actual receiver contact at common rank4 frame')
            need(not any(source_pos<warp[0]<=hit[0] and warp[1]==receiver for warp in old['warps']),
                 'no intervening receiver warp')
            late_contacts[receiver]=dict(next_B_index=hit[0],event=hit[1])
        need(not any(692<warp[0]<=694 for warp in old['warps']),'no intervening local warp in three-register identity')
        profile=Counter({int(r):n for r,n in old['report']['local_profile'].items()})
        profile.update({1:-1,2:-1,3:1})
        need(dict(profile)=={int(r):n for r,n in new['report']['local_profile'].items()},'reported complete local profile bound to changed paths')
        bad=json.loads(json.dumps(new));bad['B'][694][-1]=[51]
        try:frames(bad)
        except ValueError as error:need('monotone' in str(error),'correct frame rejection control')
        else:raise ValueError('illegal final rank1 contact accepted')
        results[tag]=dict(status='PASS_INDEPENDENT_RECEIVER_REWRITE_REVIEW',
                         source_payload_sha256=sha256(json.dumps(old,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
                         candidate_payload_sha256=sha256(json.dumps(new,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
                         native_delta_by_register=delta,helper_width_inventory=dict(sorted(Counter(widths).items())),
                         local_profile=dict(profile),next_original_receiver_contacts=late_contacts,
                         added_B_scalar_operations=1,added_cleanup_scalar_operations=1,
                         added_real_scalar_primitives=4,all_live_frame_paths=len(oi),
                         old_receiver672_positive_steps=ot[672],new_receiver672_positive_steps=nt[672],
                         rejection_controls=['wrong_final_receiver_sign','rank1_final_contact'])
        sources.extend([oldpath,newpath])
    result=dict(status='PASS_BOTH_PROVIDER_INDEPENDENT_RECEIVER_REWRITE_REVIEW',providers=results,
                input_sha256={str(path.relative_to(REPO)):sha256(path.read_bytes()).hexdigest() for path in sources},
                exact_three_register_matrix=[[str(x) for x in row] for row in expected],
                operator_argument='Let A be the canonical frame lift P->Q and B the lift Q->R. Old receivers atR are BAu+Bh/2 and BAv-Bh/2. New first adds v to u atP, subtracts h/2 fromv atQ, and subtracts v fromu atR; its outputs are the same for arbitraryu,v,h. The intervening receiver contacts startatR and have no receiver warps.',
                scope='Independent finite scalar identity, frame inclusion/chronology/rank bill, unchanged helper stock and inverse-cleanup syntax. Native Gaussian phases, every whole-word live input, both orientations and complete global pricing are checked by separate native/ordinary/invoice receipts; this review does not claim them independently.')
    out.mkdir(parents=True,exist_ok=True)
    (out/'RECEIVER-REVIEW.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(result['status'])


if __name__=='__main__':
    p=ArgumentParser(description=__doc__)
    p.add_argument('--source-dir',type=Path,default=SOURCE)
    p.add_argument('--candidate-dir',type=Path,default=CANDIDATE)
    p.add_argument('--out',type=Path,default=HERE/'evidence')
    a=p.parse_args();run(a.source_dir.resolve(),a.candidate_dir.resolve(),a.out.resolve())
