#!/usr/bin/env python3
"""Source-bound fixed-boundary carrier cut. Apache-2.0; Chris R with Codex."""
import argparse, gzip, hashlib, json, math
from pathlib import Path

P = Path(__file__).resolve().parent
WORD_SHA = 'e432182d5b62c8bbefeb871fce30317234d707e5e18d4295e65ac21f7fd8365e'
RAW_SHA = 'da77deaf11368d016622348227657b98404b6afbc7e4f3d6fe9a246baae0dcce'
class Reject(Exception): pass
def need(ok, why):
    if not ok: raise Reject(why)
def xor_rows(xs):
    out=0
    for x in xs: out ^= x
    return out
def basis(xs):
    piv={}
    for v in xs:
        while v:
            j=v.bit_length()-1
            if j in piv: v ^= piv[j]
            else: piv[j]=v; break
    return piv
def rem(x, piv):
    for j in sorted(piv,reverse=True):
        if x>>j&1: x ^= piv[j]
    return x
def rank(xs): return len(basis(xs))
def obstruction(initial, final, external):
    piv=basis(external)
    a=[rem(x,piv) for x in initial]; b=[rem(x,piv) for x in final]
    need(rank(a)>rank(b), 'strict quotient rank loss required')
    return dict(initial=[hex(x) for x in a],final=[hex(x) for x in b],initial_rank=rank(a),final_rank=rank(b))
def norm(v):
    g=math.gcd(*v)
    if not g:return tuple(v)
    sign=1 if next(x for x in v if x)>0 else -1
    return tuple(sign*x//g for x in v)
def reduce_q(v,bs):
    v=tuple(v)
    for j,row in bs:
        if v[j]:v=norm([row[j]*x-v[j]*y for x,y in zip(v,row)])
    return v
def basis_q(rows):
    bs=[]
    for row in rows:
        v=reduce_q(row,bs)
        if any(v):bs.append((next(i for i,x in enumerate(v) if x),norm(v)));bs.sort()
    return bs

def audit(w):
    need(w['R']==437 and w['v']==111,'actual R437 dimensions')
    fr=list(map(set,w['frames'])); n=659
    dimensions=[]
    for f in fr:
        bs=basis_q([w['lines'][j] for j in sorted(f)])
        need({j for j,v in enumerate(w['lines']) if not any(reduce_q(v,bs))}==f,'closed rational frame')
        dimensions.append(len(bs))
    # Whole arbitrary-DIRTY linear identity; this does not assert physical realization.
    full=[1<<r for r in range(n)]
    for sec in ['D','A']:
        for _,d,ss in w[sec]:full[d]^=xor_rows(full[s] for s in ss)
    captured=[full[r] for r in w['ret']]
    for t,js in enumerate(w['scatter']):full[111+t]^=xor_rows(captured[j] for j in js)
    for sec in ['B','C']:
        for _,d,ss in w[sec]:full[d]^=xor_rows(full[s] for s in ss)
    need(full==[(1<<r)^((1<<(r-111)) if 111<=r<222 else 0) for r in range(n)],'659-column complete dirty identity')
    rows=[1<<r if r<111 else 0 for r in range(n)]; cur=w['start'][:]; states=[]
    for f,d,ss in w['A']:
        states.append((rows[:],cur[:]))
        for r in [d]+ss:
            need(fr[cur[r]]<=fr[f],'baseline monotone frame')
            cur[r]=f
        rows[d]^=xor_rows(rows[s] for s in ss)
    states.append((rows[:],cur[:])); endframes=cur[:]
    uses={h:[] for h in range(222,n)}
    for sec in ['A','B']:
        for i,(f,d,ss) in enumerate(w[sec]):
            for h in set([d]+ss)&uses.keys():uses[h].append((sec,i,f,d,ss))
    census=[]
    for h,u in uses.items():
        writes=[z for z in u if z[3]==h]
        if len(writes)!=1 or len(writes[0][4])!=1 or writes[0][4][0]>=111 or h in w['ret']:continue
        s=writes[0][4][0]; reads=[z for z in u if z[3]!=h]
        first=reads[0]; sec,i,f,d,ss=first
        need(sec=='A','census first observation in A')
        raw,frames=states[i]
        need(raw[s]==1<<s,'first observation SOURCE remains clean')
        census.append(dict(helper=h,source=s,first_read=i,receiver=d,receiver_frame=frames[d],source_frame=frames[s],direct_current_source_frame_eligible=fr[frames[d]]<=fr[frames[s]],source_read_count=len(reads)))
    need([c['helper'] for c in census]==[462,463,466,468,469],'complete single-load carrier census')
    need(not any(c['direct_current_source_frame_eligible'] for c in census),'all five immediate direct replacements blocked')
    # Actual current node: SOURCE77 read, then the two frame509 grouped gates.
    need(w['A'][1998:2001]==[[186,444,[77]],[509,444,[17,271,293,352,413,467,469]],[509,413,[17,271,293,352,371,469]]],'node binding')
    raw,cur=states[1998]; after=states[2001][0]
    need(raw[444]==0 and raw[413]==1<<87 and raw[469]==1<<92 and raw[92]==1<<92,'actual source rows')
    need(cur[444]==0 and cur[92]==184 and fr[184]<=fr[509],'favorable early92 injection')
    future={}
    for f,d,ss in w['A'][2001:]:
        for r in [d]+ss:future.setdefault(r,f)
    for r in w['ret']:future.setdefault(r,endframes[r])
    for f,d,ss in w['B']:
        for r in [d]+ss:future.setdefault(r,f)
    eligible=[r for r in range(n) if r not in [444,413,469] and fr[cur[r]]<=fr[509]<=fr[future.get(r,w['final'][r])]]
    need(eligible==[17,67,177,185,271,293,352,371,467,468],'all boundary-compatible external roles')
    need(raw[177]==raw[185]==0, 'two frame-compatible targets have zero SOURCE rows')
    # SOURCE77 is deliberately free even though its early original186 read is
    # incompatible with the hypothetical184 injection. Enlarging E only helps.
    external=[raw[r] for r in eligible]+[1<<77]
    cert=obstruction([1<<92,raw[413]],[after[444],after[413]],external)
    need(cert['initial_rank']==2 and cert['final_rank']==1,'rank2-to-rank1 cut')
    need(cert['final'][0]==cert['final'][1]==hex((1<<87)|(1<<92)),'actual common quotient')
    # Union of newly legal frame509 channels over every cut before413 leaves509.
    # This is an eligibility census; no all-window circuit theorem is inferred.
    cutrows=[];union=[]
    for cut in range(2001,2035):
        rws,cr=states[cut];fu={}
        for f,d,ss in w['A'][cut:]:
            for r in [d]+ss:fu.setdefault(r,f)
        for r in w['ret']:fu.setdefault(r,endframes[r])
        for f,d,ss in w['B']:
            for r in [d]+ss:fu.setdefault(r,f)
        av=[r for r in range(n) if r not in [444,413,469] and fr[cr[r]]<=fr[509]<=fr[fu.get(r,w['final'][r])]]
        union.extend(rws[r] for r in av);cutrows.append([cut,av])
    need(rank(external+union)==rank(external),'34 later eligibility cuts add no external source dimension')
    controls=[]
    for name,a,b,e in [
        ('source87_channel_breaks_cut',[1<<92,1<<87],[after[444],after[413]],external+[1<<87]),
        ('source92_channel_breaks_cut',[1<<92,1<<87],[after[444],after[413]],external+[1<<92]),
        ('borrowed_bank_keeps_missing_dimension',[1<<92,1<<87,0],[after[444],after[413],1<<87],external)]:
        try:obstruction(a,b,e)
        except Reject:controls.append(name)
        else:raise Reject('false obstruction accepted: '+name)
    return dict(status='PASS_R437_CARRIER_QUOTIENT_CUT',whole_dirty_columns=n,frames=len(fr),frame509_dimension=dimensions[509],census=census,eligible_external_roles=eligible,free_relaxation_source=77,quotient=cert,later_cut_count=len(cutrows),later_cuts=cutrows,controls=controls,scope='fixed node509 boundaries, invertible linear register gates, existing external channels plus free SOURCE77, borrowed writable banks returned modulo E; no uniform supplier or new kappa')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write');args=ap.parse_args()
    retained=json.loads((P/'RETAINED.json').read_text())
    for row in retained['files']:
        raw=(P/row['path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest()==row['sha256'],'retained source SHA256')
        need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob'],'retained Git blob')
    raw=(P/'inputs/R437-COMPOSED-WORD.json.gz').read_bytes();need(hashlib.sha256(raw).hexdigest()==WORD_SHA,'frozen word bytes')
    payload=gzip.decompress(raw);need(hashlib.sha256(payload).hexdigest()==RAW_SHA,'canonical word bytes')
    result=audit(json.loads(payload))
    if args.write:Path(args.write).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:need(result==json.loads((P/'RESULT.json').read_text()),'frozen certificate equality')
    print(result['status'], 'columns=659 frames=636 direct_candidates=5 quotient=2->1 later_cuts=34 controls=3')
if __name__=='__main__':
    try:main()
    except (Reject,OSError,ValueError,KeyError) as e:raise SystemExit('FAIL: '+str(e))
