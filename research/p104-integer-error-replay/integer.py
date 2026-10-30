"""Exact integer inner loops for signed dyadic error transfer.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The literal scalar and reverse-cut oracles stay in the authenticated reference.
"""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256


def need(ok,message):
    if not ok: raise ValueError(message)


def dyadic(value):
    value=F(value);d=value.denominator
    need(d & (d-1)==0,'dyadic value required')
    return value.numerator,d.bit_length()-1


def scaled(value,scale):
    n,k=dyadic(value);need(scale%(1<<k)==0,'exact weight scale')
    return n*(scale>>k)


def multiply(value,n,k):
    value*=n
    need(not k or value%(1<<k)==0,'exact dyadic division')
    return value>>k


def coefficients(word):
    n=word['public']+word['owned_fields'];ops=[]
    for event in word['program']:
        op,r=event[:2];need(op in ('INIT','CLEAR','MOVE','ADD','COPY','SCALE'),'known operation')
        need(0<=r<n,'role range')
        if op in ('ADD','COPY','SCALE'):
            a,k=dyadic(event[-2]);need(a!=0,'nonzero scalar')
        else:a,k=1,0
        if op in ('ADD','COPY'):need(0<=event[2]<n and event[2]!=r,'distinct source')
        ops.append((op,r,a,k,event[2] if op in ('ADD','COPY') else None))
    bound=0
    for reverse in (False,True):
        degrees=[0]*n
        for op,r,a,k,s in reversed(ops) if reverse else ops:
            if op in ('INIT','CLEAR'):degrees[r]=0
            elif op=='SCALE':degrees[r]+=k
            elif op in ('ADD','COPY'):
                if reverse:degrees[s]=max(degrees[s],degrees[r]+k)
                else:degrees[r]=max(degrees[r],degrees[s]+k)
            bound=max(bound,degrees[r],degrees[s] if s is not None else 0)
    scale=1<<bound
    return n,ops,scale


def setup(word,weights):
    need(len(weights)==len(word['program']),'one weight per event')
    n,ops,scale=coefficients(word)
    aw=1<<max((dyadic(a)[1] for a,c in weights),default=0)
    cw=1<<max((dyadic(c)[1] for a,c in weights),default=0)
    values=[(scaled(a,aw),scaled(c,cw)) for a,c in weights]
    need(all(a>=0 and c>=0 for a,c in values),'nonnegative weights')
    return n,ops,scale,values,(scale*aw,scale*cw,scale)


def add_row(dst,src,n,k):
    for i,v in src.items():
        value=dst.get(i,0)+multiply(v,n,k)
        if value:dst[i]=value
        else:dst.pop(i,None)


def update_hash(h,event,value,scale):
    q=F(value,scale)
    h.update(f'{event}:{q.numerator}/{q.denominator};'.encode())


class Engine:
    def __init__(self,reference):
        self.binary_span=reference.binary_span
        self.digest=reference.digest
        self.encode=reference.encode
        self.execute=reference.execute
        self.reverse_cut=reference.reverse_cut

    def ideal(self,word):
        n,ops,S=coefficients(word);public=word['public']
        rows=[{i:S} for i in range(n)];norms=[S]*n
        frames=list(word['initial'])+[None]*(n-public)
        spaces=[self.binary_span(v) for v in word['frames']]
        live=set();peak_live=0;peak=dict(value=S,cut=0,role=0,row={0:S})
        weights=[];erasures=[];counts=Counter();stream=sha256()
        for j,(op,r,a,k,s) in enumerate(ops):
            event=word['program'][j];counts[op]+=1
            weight,feedback=F(norms[r],S),F(1)
            if op=='MOVE':
                _,_,start,end,private=event
                need(frames[r]==start and private==(r in live),'Native source and owner')
                need(spaces[end]<spaces[start] if private else spaces[start]<spaces[end],'Nested native path')
                frames[r]=end
            elif op=='INIT':
                need(r>=public and r not in live,'Owned INIT');live.add(r);peak_live=max(peak_live,len(live));rows[r]={};frames[r]=event[2]
            elif op=='CLEAR':
                need(r in live and frames[r]==event[2],'Owned CLEAR')
                erasures.append(dict(event=j,role=r,ideal_norm=F(norms[r],S),ideal_zero=not rows[r]))
                live.remove(r);rows[r]={};frames[r]=None
            else:
                q=F(a,1<<k);frame=event[-1]
                need(frames[r]==frame,'Dyadic scalar destination')
                if op=='SCALE':
                    weight,feedback=abs(q)*F(norms[r],S),abs(q)
                    rows[r]={i:multiply(v,a,k) for i,v in rows[r].items()}
                else:
                    need(frames[s]==frame,'Coframed scalar operands')
                    if op=='COPY':
                        need(r in live and not rows[r] and q==1,'Exact copy into cleared owned field')
                        weight,feedback=abs(q)*F(norms[s],S),1+abs(q);rows[r]=dict(rows[s])
                    else:
                        weight,feedback=F(norms[r],S)+abs(q)*F(norms[s],S),1+abs(q)
                        add_row(rows[r],rows[s],a,k)
            norms[r]=sum(map(abs,rows[r].values()));weights.append((weight,feedback))
            stream.update((str(j)+':'+str(F(norms[r],S))+';').encode())
            if norms[r]>peak['value']:peak=dict(value=norms[r],cut=j+1,role=r,row=dict(rows[r]))
        need(not live and frames[:public]==word['final'],'Public and owned exits')
        active=set(word['live'])
        for r,row in enumerate(rows):
            expected={r:S} if r<public else {}
            if r-112 in active:expected[r-112]=S
            need(row==expected,'Complete arbitrary-input endpoint')
        peak['value']=F(peak['value'],S);peak['row']={i:F(v,S) for i,v in peak['row'].items()}
        return dict(n=n,public=public,events=len(ops),counts=dict(counts),peak_owned=peak_live,
                    input_peak=peak,erasures=erasures,norm_stream_sha256=stream.hexdigest()),weights

    def error_trace(self,word,weights,rounded):
        n,ops,S,w,units=setup(word,weights);rows=[{} for _ in range(n)];scores=[[0]*3 for _ in range(n)]
        peaks=[dict(value=0,cut=0,role=0) for _ in range(3)];witness={};pairs=[];stream=sha256();sites=0
        for j,(op,r,a,k,s) in enumerate(ops):
            if op in ('INIT','CLEAR'):rows[r]={};scores[r]=[0]*3
            elif op=='SCALE':
                rows[r]={i:multiply(v,a,k) for i,v in rows[r].items()}
                scores[r]=[multiply(v,abs(a),k) for v in scores[r]]
            elif op in ('ADD','COPY'):
                for i,v in rows[s].items():
                    old=rows[r].get(i,0);value=old+multiply(v,a,k);change=abs(value)-abs(old)
                    scores[r][0]+=change*w[i][0];scores[r][1]+=change*w[i][1];scores[r][2]+=change
                    if value:rows[r][i]=value
                    else:rows[r].pop(i,None)
            if op in rounded:
                sites+=1;rows[r][j]=S;scores[r][0]+=S*w[j][0];scores[r][1]+=S*w[j][1];scores[r][2]+=S
            pairs.append((*scores[r][:2],j+1,r))
            stream.update((str(j)+':'+','.join(str(F(v,u)) for v,u in zip(scores[r],units))+';').encode())
            for c,value in enumerate(scores[r]):
                if value>peaks[c]['value']:
                    peaks[c]=dict(value=value,cut=j+1,role=r);witness[c]=dict(rows[r])
        pareto=[];maximum=-1
        for a,b,cut,r in sorted(pairs,reverse=True):
            if b>maximum:pareto.append([F(a,units[0]),F(b,units[1]),cut,r]);maximum=b
        final=[]
        for c in range(3):
            value,r=max((scores[r][c],r) for r in range(word['public']))
            final.append(dict(value=F(value,units[c]),cut=len(ops),role=r));witness['final'+str(c)]=dict(rows[r])
        hashes=[]
        for row in rows:
            h=sha256()
            for j in sorted(row,reverse=True):update_hash(h,j,row[j],S)
            hashes.append(h.hexdigest())
        for c,peak in enumerate(peaks):peak['value']=F(peak['value'],units[c])
        witness={key:{j:F(v,S) for j,v in row.items()} for key,row in witness.items()}
        return dict(rounded=sorted(rounded),sites=sites,peaks=peaks,pareto=pareto,final_peaks=final,
                    final_scores=[[F(v,u) for v,u in zip(row,units)] for row in scores],
                    final_coefficient_hashes=hashes,score_stream_sha256=stream.hexdigest()),witness

    def reverse_all(self,word,weights,rounded):
        n,ops,S,w,units=setup(word,weights);columns=[{i:S} for i in range(n)];scores=[[0]*3 for _ in range(n)];hashes=[sha256() for _ in range(n)]
        for j in reversed(range(len(ops))):
            op,r,a,k,s=ops[j]
            if op in rounded:
                for i,v in columns[r].items():
                    scores[i][0]+=abs(v)*w[j][0];scores[i][1]+=abs(v)*w[j][1];scores[i][2]+=abs(v)
                    update_hash(hashes[i],j,v,S)
            if op in ('INIT','CLEAR'):columns[r]={}
            elif op=='SCALE':columns[r]={i:multiply(v,a,k) for i,v in columns[r].items()}
            elif op in ('ADD','COPY'):add_row(columns[s],columns[r],a,k)
        return [[F(v,u) for v,u in zip(row,units)] for row in scores],[h.hexdigest() for h in hashes]
