#!/usr/bin/env python3
"""Fixed OQ4 hosting reconstruction; credits PR3647/3700 invoice audit."""
from collections import Counter,defaultdict
from fractions import Fraction as Q
from functools import lru_cache
import gzip,hashlib,json
from pathlib import Path
import sys
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P))
import verify as v
def candidate_template_bytes():
    manifest=json.loads((P/'CANDIDATE-TEMPLATE.json').read_text())
    v.need(manifest['format']=='exact-gzip-byte-chunks-v1' and manifest['logical_name']=='CANDIDATE-TEMPLATE.json.gz','candidate chunk format')
    pieces=[]
    for i,row in enumerate(manifest['parts']):
        v.need(row['path']=='candidate-template-chunks/part-'+str(i).zfill(3)+'.bin','ordered canonical candidate chunk path')
        data=(P/row['path']).read_bytes()
        v.need(len(data)==row['bytes'] and len(data)<=48*1024 and hashlib.sha256(data).hexdigest()==row['sha256'],'candidate chunk length/hash')
        pieces.append(data)
    data=b''.join(pieces)
    v.need(len(data)==manifest['bytes'] and hashlib.sha256(data).hexdigest()==manifest['sha256'],'joined candidate gzip identity')
    return data

def streams(w,dims):
    cur=w['start'][:];records=[];f=list(map(set,w['frames']))
    def move(r,new):
        old=cur[r]
        if old!=new:
            v.need(f[old]<=f[new],'host frame inclusion')
            records.append((0,r,old,new,dims[new]-dims[old],0));cur[r]=new
    for phase,sec in [(1,'D'),(2,'A'),(4,'B'),(5,'C')]:
        if sec=='B':
            for j,r in enumerate(w['ret']):
                records.append((2,r,659,cur[r],0,dims[cur[r]]))
                records.extend((1,111+t,659,1,0,3) for t,js in enumerate(w['scatter']) if j in js)
                records.append((3,r,659,cur[r],0,0))
        for frame,d,ss in w[sec]:
            for r in [d]+ss:move(r,frame)
            records.extend((1,d,s,1,frame,phase) for s in ss)
    for r,frame in enumerate(w['final']):move(r,frame)
    result={};details={}
    for rev in [False,True]:
        ev=[];vals=[1<<r for r in range(659)]+[0];norm=[1]*659+[0];opened=None;high=1;profile=Counter();adds=0
        for op,d,s,c,f,z in (reversed(records) if rev else records):
            if op==0:
                old,new=(c,s) if rev else (s,c);ev.append([0,d,old,new,f,int(rev)]);profile[f]+=1
            elif op==1:
                v.need(d!=opened and (s!=659 or opened is not None),'copy ownership')
                vals[d]^=vals[s];norm[d]+=norm[s];high=max(high,norm[d]);adds+=1
                ev.append([1,d,s,-c if rev else c,f,int(rev)])
            elif op==(3 if rev else 2):
                v.need(opened is None and vals[659]==0,'empty copy buffer')
                opened=d;vals[659]=vals[d];norm[659]=norm[d];r=abs(dims[c]-dims[f]);profile[r]+=1
                ev.append([2,d,659,c,f,r,int(rev)])
            else:
                v.need(opened==d and vals[659]==vals[d],'copy unchanged through scatter')
                vals[659]=0;norm[659]=0;opened=None;ev.append([3,d,659,c,f,z,int(rev)])
        v.need(vals[:659]==[(1<<r)^((1<<(r-111)) if 111<=r<222 else 0) for r in range(659)] and opened is None,'forward/reverse complete identity')
        key='reverse' if rev else 'forward';result[key]=ev
        details[key]={'records':len(records),'adds':adds,'l1':high,'profile':dict(sorted(profile.items())),'stream_sha256':hashlib.sha256(json.dumps(ev,separators=(',',':')).encode()).hexdigest(),'records_sha256':hashlib.sha256(b''.join(__import__('struct').pack('<6i',*r) for r in records)).hexdigest()}
    return result,details

@lru_cache(None)
def log_bounds(num,den=1):
    k=0;a=Q(num,den)
    while a>=2:a/=2;k+=1
    def series(z):
        total=Q(0);term=z
        for j in range(48):total+=2*term/(2*j+1);term*=z*z
        return total,total+2*term/(97*(1-z*z))
    lo,hi=series((a-1)/(a+1));l2,h2=series(Q(1,3));lo+=k*l2;hi+=k*h2;scale=10**64
    return Q(lo.numerator*scale//lo.denominator,scale),Q(-((-hi.numerator*scale)//hi.denominator),scale)
def exp_bounds(lo,hi):
    def series(x):
        total=term=Q(1)
        for j in range(1,23):term=term*x/j;total+=term
        return total,total+(term*x/23)/(1-x/24)
    return series(lo)[0],series(hi)[1]
def price(profile,c):
    pp=dict(profile);E=sum(pp.values());pp[1]=pp.get(1,0)+Q(32*64*64*E,10**16)
    low=high=Q(0)
    for r,n in pp.items():
        l,h=log_bounds(64,r);a,b=exp_bounds(c*l,c*h);factor=Q(n*r,64*28416)
        low+=factor*a;high+=factor*b
    scale=10**60
    return Q(low.numerator*scale//low.denominator,scale),Q(-((-high.numerator*scale)//high.denominator),scale)
def run():
    old=v.load();new=json.loads((P/'CANDIDATE.json').read_text());dims=v.geometry(old)
    baseline,bd=streams(old,dims);candidate,cd=streams(new,dims)
    t=json.loads(gzip.decompress((P/'inputs/OQ4-TEMPLATE.json.gz').read_bytes()))
    expected=json.loads((P/'inputs/OQ4-EXPECTED.json').read_text())
    v.need(t['local_programs']==baseline,'literal old local streams bind retained OQ4 template')
    windows={};last={};local=[]
    for pos,e in enumerate(t['schedule']):
        if e['kind']=='local_cover_sweep':local.append((pos,e['stage'],e['pair']));last[e['pair']]=pos
        elif e['kind']=='bridge':last[e['dst']]=pos;last[e['src']]=pos
        elif e['kind']=='idle':windows[e['idx']]=(e['pair'],e['rank'],{s for p,s,pair in local if last.get(e['pair'],-1)<p<pos and pair!=e['pair']})
        else:v.need(e['kind']=='exchange','known schedule event')
    assigned={};used=defaultdict(int)
    for i,cp,off,width,stage,helper in t['hosting']['slots']:
        pair,r,eligible=windows[i]
        v.need(stage in eligible and width==8 and off>=0 and off+8<=r and 0<=helper<437 and 0<=cp<222,'hosted lifetime and width')
        bits=((1<<8)-1)<<off
        v.need(not used[i,cp]&bits and (stage,helper) not in assigned,'hosted disjoint slots')
        used[i,cp]|=bits;assigned[stage,helper]=(i,cp,off,width)
    v.need(len(assigned)==9*437,'all full eight-coordinate helper slots')
    remainder=Counter()
    for i,(pair,r,eligible) in windows.items():
        if not r:continue
        for cp in range(222):
            rem=((1<<r)-1)^used[i,cp];n=rem.bit_count();start=(rem&-rem).bit_length()-1 if rem else 0
            v.need(not rem or rem==((1<<n)-1)<<start,'single contiguous unpooled remainder')
            if n:remainder[n]+=32
    profiles={}
    for name,detail in [('old',bd),('new',cd)]:
        paid=Counter({r:n*288 for r,n in detail['forward']['profile'].items()});paid.update(remainder);profiles[name]=dict(sorted(paid.items()))
    v.need(profiles['old']=={int(r):n for r,n in expected['profile'].items()},'source-bound old hosted profile')
    seen=set();owned=0;digests={};events={}
    for name,ss in [('old',baseline),('new',candidate)]:
        digest=hashlib.sha256();count=0;cache={}
        for key,es in ss.items():cache[key]=[(z[0],z[1],None if z[0]==0 else z[2],(','+','.join(str(x) for x in z[2 if z[0]==0 else 3:])+']\n').encode()) for z in es]
        for call in t['calls']:
            stage,rep,pair=call['stage'],call['replica'],call['pair'];owners=call['owners'];seen.add((stage,rep))
            v.need(len(owners)==659 and call['orientation']==('reverse' if stage%2 else 'forward'),'call dimensions/orientation')
            for r in range(222):
                side=r//111
                if call['orientation']=='reverse':side=1-side
                v.need(owners[r]==[rep*888+(2*pair+side)*111+r%111,['data',stage,r%111]],'data owner identity')
            for h in range(437):
                i,cp,off,width=assigned[stage,h];hostpair=windows[i][0];side,port=divmod(cp,111)
                v.need(hostpair!=pair and owners[222+h]==[rep*888+(2*hostpair+side)*111+port,['hosted',i,off,width]],'all literal helper owners')
            encoded=[json.dumps(o,separators=(',',':')).encode() for o in owners]+[b'[28416,["private",0]]']
            for op,d,s,suffix in cache[call['orientation']]:
                digest.update(b'['+str(op).encode()+b','+encoded[d]+(b','+encoded[s] if s is not None else b'')+suffix);count+=1
        digests[name]=digest.hexdigest();events[name]=count
    v.need(len(seen)==288 and digests['old']==expected['program_sha256'],'all source-bound hosted calls and old emitted digest')
    rebuilt=json.loads(json.dumps(t));rebuilt['local_programs']=candidate;rebuilt['source_record_sha256']=cd['forward']['records_sha256']
    for call in rebuilt['calls']:call['local_hash']=cd[call['orientation']]['stream_sha256']
    v.need(v.canon(rebuilt)==gzip.decompress(candidate_template_bytes()),'exact rebuilt candidate template')
    # Candidate rational grid point selected by a separate decimal estimate;
    # acceptance below uses rational intervals only.
    from decimal import Decimal,localcontext,ROUND_FLOOR
    with localcontext() as ctx:
        ctx.prec=65;lo_d=Decimal('0.0017');hi_d=Decimal('0.0018');E=sum(profiles['new'].values())
        pp={r:Decimal(n) for r,n in profiles['new'].items()};pp[1]+=Decimal(32*64*64*E)/Decimal(10**16)
        for _ in range(180):
            mid=(lo_d+hi_d)/2
            moment=sum(n*(Decimal(r)/64)**(1-mid)/28416 for r,n in pp.items())
            if moment<1:lo_d=mid
            else:hi_d=mid
        numerator=int((lo_d*Decimal(10**24)).to_integral_value(rounding=ROUND_FLOOR))
    c=Q(numerator,10**24);lo,hi=price(profiles['new'],c);next_lo,next_hi=price(profiles['new'],c+Q(1,10**24))
    v.need(hi<1<next_lo,'rational enclosed paid-moment root grid')
    old_c=Q(expected['BIT_c']);old_lo,old_hi=price(profiles['old'],old_c)
    v.need(old_hi<1 and c>old_c,'retained old charged grid and positive gain')
    return {'status':'PASS_FIXED_OQ4_HOST_REBUILD','calls':288,'replicas':32,'helpers_per_call':437,'hosted_owner_occurrences':288*437,
        'old':bd,'new':cd,'profiles':profiles,'emitted_sha256':digests,'events':events,
        'mass_old':sum(r*n for r,n in profiles['old'].items()),'mass_new':sum(r*n for r,n in profiles['new'].items()),
        'price_probe':{'c':str(c),'decimal':str(float(c)),'lower':str(lo),'upper':str(hi),'next_c':str(c+Q(1,10**24)),'next_lower':str(next_lo),'next_upper':str(next_hi),'old_c':str(old_c),'relative_gain':str((c-old_c)/old_c),'below_one':hi<1},
        'scope':'fixed unpooled OQ4 owner/idle schedule and primitive rank invoice; source/native compiler and complete physical/stock invoice remain conditional'}
if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--write');args=ap.parse_args();result=run()
    if args.write:Path(args.write).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:v.need(json.loads(json.dumps(result))==json.loads((P/'HOST-RESULT.json').read_text()),'host receipt')
    print(result['status'], 'calls=288 owners=125856 mass='+str(result['mass_new']), 'price_probe_below_one='+str(result['price_probe']['below_one']))
