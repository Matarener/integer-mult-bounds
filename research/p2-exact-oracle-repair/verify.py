"""Certify the exact 240-return minimum for the frozen p2 oracle model.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
Source and predecessor roles are recorded in SOURCES.json and PROOF.md.
"""
from fractions import Fraction as Q
from pathlib import Path
from hashlib import sha256
import gzip
import json
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SOURCE=ROOT/'research/p2-full-history-deficit/inputs'
N=17
IDENT=tuple(1<<i for i in range(N))


def need(ok,message):
    if not ok:raise ValueError(message)


def invert(a):
    n=len(a)
    rows=[list(map(Q,row))+[Q(i==j) for j in range(n)] for i,row in enumerate(a)]
    for j in range(n):
        k=next(i for i in range(j,n) if rows[i][j])
        rows[j],rows[k]=rows[k],rows[j]
        q=rows[j][j];rows[j]=[x/q for x in rows[j]]
        for i in range(n):
            if i!=j and rows[i][j]:
                q=rows[i][j];rows[i]=[x-q*y for x,y in zip(rows[i],rows[j])]
    return [r[n:] for r in rows]


def projector(code):
    m=[[2*(Q(i==j)-code[i][j]) for j in range(112)] for i in range(112)]
    need(all(x.denominator==1 for row in m for x in row),'Integral scaled defect')
    m=[[int(x) for x in row] for row in m]
    columns=[0,1,2,3,4,5,6,12]
    u=[[row[j] for j in columns] for row in m]
    gram=[[sum(row[i]*row[j] for row in u) for j in range(8)] for i in range(8)]
    gi=invert(gram)
    ug=[[sum(row[k]*gi[k][j] for k in range(8)) for j in range(8)] for row in u]
    p=[[sum(x*y for x,y in zip(row,v)) for v in u] for row in ug]
    need(all((28*x).denominator==1 for row in p for x in row),'Exact projector scale')
    s=[[int(28*x) for x in row] for row in p]
    selected=[i for i in range(112) if code[i][i]==12]
    need(len(selected)==8,'Eight selected source coordinates')
    w=[Q(-1,11) if i in selected else Q(1) for i in range(112)]
    b=[[w[i]*m[j][i] for j in range(112)] for i in range(112)]
    need(all(x.denominator==1 for row in b for x in row),'Exact row-space balancing')
    b=[[int(x) for x in row] for row in b]
    need(all(s[i][i]==2 for i in range(112)),'Uniform diagonal 1/14')
    need(all(s[i][j]==s[j][i] for i in range(112) for j in range(112)),'Symmetric projector')
    for i in range(112):
        for j in range(112):
            need(sum(s[i][k]*s[k][j] for k in range(112))==28*s[i][j],
                 'Independent integer idempotence')
            need(sum(s[i][k]*m[k][j] for k in range(112))==28*m[i][j],
                 'Entire defect column space')
            need(sum(s[i][k]*b[k][j] for k in range(112))==28*b[i][j],
                 'Entire balanced defect row space')
    return s,selected


def rm(x,g):
    out=0
    while x:
        low=x&-x;out^=g[low.bit_length()-1];x^=low
    return out


def mul(a,b):
    g,s=a;h,t=b
    return tuple(rm(row,h) for row in g),t^rm(s,h)


def inverse(a):
    g,s=a
    # The embedded source matrices are orthogonal over F2.
    h=tuple(sum(((g[j]>>i)&1)<<j for j in range(N)) for i in range(N))
    out=(h,rm(s,h))
    need(mul(a,out)==(IDENT,0) and mul(out,a)==(IDENT,0),'Exact signed inverse')
    return out


def embed(g,s,axes):
    rows=list(IDENT)
    for i,axis in enumerate(axes):
        rows[axis]=sum(((g[i]>>j)&1)<<other for j,other in enumerate(axes))
    return tuple(rows),sum(((s>>j)&1)<<axis for j,axis in enumerate(axes))


def action(a,x):
    g,s=a
    return sum(((row&x).bit_count()%2)<<i for i,row in enumerate(g)),(s&x).bit_count()%2


def normalizers(records):
    out=[]
    for record in records:
        word=record['K_word']
        need(len(word)==2 and word[0][0]=='P' and word[1][0]=='D','Source normalizer form')
        g=word[0][1];quad,alpha=word[1][1:]
        need(len(g)==9 and not any(quad) and len(alpha)==9 and all(x%2==0 for x in alpha),
             'Linear signed phase')
        need(all((x&y).bit_count()%2==(i==j) for i,x in enumerate(g) for j,y in enumerate(g)),
             'Source orthogonal binary map')
        s=rm(sum((x//2)<<i for i,x in enumerate(alpha)),g)
        out.append((embed(g,s,list(range(9))),embed(g,s,[0]+list(range(9,17)))))
    need(len(out)==112,'Every source normalizer')
    return out


def sidon(ks):
    ls=[mul(a,inverse(b)) for a,b in ks]
    groups={}
    checks=0
    for i,a in enumerate(ls):
        for j,b in enumerate(ls):
            word=[inverse(ks[j][0]),ks[j][1],inverse(ks[i][1]),ks[i][0]]
            z=mul(a,inverse(b))
            for bit in range(N):
                x,sign=1<<bit,0
                for op in word:
                    x,t=action(op,x);sign^=t
                need((x,sign)==action(z,1<<bit),'Independent chronological signed action')
                checks+=1
            groups.setdefault(z[0],[]).append((i,j))
    need(groups.get(IDENT)==[(i,i) for i in range(112)],'Only diagonal identity products')
    need(len(groups)==1+112*111 and all(len(v)==1 for k,v in groups.items() if k!=IDENT),
         'All ordered off-diagonal products have distinct linear parts')
    digest=sha256(json.dumps([(list(k),v) for k,v in sorted(groups.items())],separators=(',',':')).encode()).hexdigest()
    return groups,digest,checks


def main():
    for pin in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if pin['usage']=='input':
            need(sha256((ROOT/pin['path']).read_bytes()).hexdigest()==pin['sha256'],'Source bytes')
    raw=json.loads(gzip.decompress((SOURCE/'INVOLUTIVE-WORD.json.gz').read_bytes()))['F']
    code=[[Q(raw[j][i]) for j in range(112)] for i in range(112)]
    need(sum(code[i][i] for i in range(112))==96,'Source involution trace')
    scaled=[[int(2*x) for x in row] for row in code]
    need(all(2*code[i][j]==scaled[i][j] for i in range(112) for j in range(112)),
         'Source half-integral entries')
    need(all(sum(scaled[i][k]*scaled[k][j] for k in range(112))==4*(i==j)
             for i in range(112) for j in range(112)),'Source involution')
    s,selected=projector(code)
    records=json.loads((SOURCE/'NORMALIZERS.json').read_bytes())['ports']
    ks=normalizers(records)
    groups,digest,checks=sidon(ks)
    numerator=sum(s[i][j]*s[k][l]*s[i][k]*s[j][l]
                  for pairs in groups.values() for i,j in pairs for k,l in pairs)
    tau=Q(numerator,28**4)
    need(tau==2*8*Q(1,14)**2-112*Q(1,14)**4==Q(27,343),
         'Independent grouped and uniform-diagonal second moments')
    lower=16-2*tau
    need(lower>15 and 224+lower>239 and 224+16==240,'Sharp integer return count')
    controls=0
    bad_code=[row[:] for row in code];bad_code[0][0]=Q(11)
    bad_records=json.loads(json.dumps(records));bad_records[0]['K_word'][0][1][0]=0
    for fn in [lambda:sidon([ks[0]]*112),lambda:projector(bad_code),
               lambda:normalizers(bad_records),
               lambda:need(Q(239)>=224+lower,'False 239-return capacity')]:
        try:fn()
        except ValueError:controls+=1
        else:raise ValueError('Defective fixture accepted')
    need(Q(4,7)*2>1 and 2*tau<1,'Second moment closes what first moment cannot')
    result=dict(status='PASS_P2_EXACT_ORACLE_REPAIR_240',source_rank=8,selected=selected,
                projector_scale=28,projector_sha256=sha256(json.dumps(s,separators=(',',':')).encode()).hexdigest(),
                distinct_linear_products=len(groups),pair_partition_sha256=digest,
                signed_basis_actions=checks,second_moment=str(tau),rank_lower_over_h=str(lower),
                target_deficit_lower_over_h=str(224+lower),exact_oracle_returns=240,
                minimum_width=72,rejected_controls=controls,kappa_change=None)
    if '--write' in sys.argv:
        (HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    else:
        need(result==json.loads((HERE/'RESULT.json').read_text()),'Committed receipt')
    print(json.dumps(result,sort_keys=True))


if __name__=='__main__':main()
