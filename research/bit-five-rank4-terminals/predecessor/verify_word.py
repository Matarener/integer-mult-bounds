#!/usr/bin/env python3
"""Independent signed, F2 and rational-frame audit of the five-terminal word.

Imports no producer or predecessor checker. Apache-2.0; Codex assistance.
"""
from collections import Counter
from fractions import Fraction as F
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import argparse, gzip, json
HERE=Path(__file__).resolve().parent
LANE=HERE.parent/'bit-boundaries'
EXPECTED_WORD='3bca74a2a8427eb18e86566baa19de597f10d0bc40c30b7443febd499ee2189a'
EXPECTED_GEOMETRY='a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022'
N=660

def need(p,m):
    if not p:raise ValueError(m)

def plus(dst,src,c):
    out=dict(dst)
    for j,a in src.items():
        out[j]=out.get(j,0)+c*a
        if not out[j]:del out[j]
    return out

def dot(a,b):return sum((x*y for x,y in zip(a,b)),F(0))
def matvec(a,v):return tuple(dot(r,v)for r in a)

class Frames:
    def __init__(self,raw):
        self.lines=[tuple(map(F,l))for l in raw['lines']]
        self.frames=raw['frames'];self.data={};self.pairs=set()

    def get(self,f):
        if f in self.data:return self.data[f]
        ortho=[]
        for i in self.frames[f]:
            v=self.lines[i]
            for u in ortho:
                q=dot(v,u)/dot(u,u);v=tuple(x-q*y for x,y in zip(v,u))
            if any(v):ortho.append(v)
            if len(ortho)==8:break
        P=tuple(tuple(sum((u[i]*u[j]/dot(u,u)for u in ortho),F(0))for j in range(8))for i in range(8))
        need(all(P[i][j]==P[j][i]for i in range(8)for j in range(8)),'symmetric rational frame')
        need(all(matvec(P,u)==u for u in ortho),'projector fixes orthogonal basis')
        need(all(x.denominator&(x.denominator-1)==0 for row in P for x in row),'actual dyadic projector')
        need(sum(P[i][i]for i in range(8))==len(ortho),'exact rational rank')
        self.data[f]=(len(ortho),ortho,P);return self.data[f]

    def nested(self,a,b):
        if (a,b) in self.pairs:return
        ra,ua,pa=self.get(a);rb,ub,pb=self.get(b)
        need(ra<=rb and all(matvec(pb,u)==u for u in ua),'actual projector nesting')
        self.pairs.add((a,b))

def replay(word,frames,back=False,initial=None):
    current=list(word['final']if back else word['start'])+[None]
    rows=[{j:1}for j in range(N)]+[{}]if initial is None else [dict(r)for r in initial]
    opened=None;H=Counter();ADD=0;COPY=0;max_l1=1
    positive=[1]*N+[0];positive_max=1
    for z in reversed(word['records'])if back else word['records']:
        op,d,s,c,f,ph=z
        need(0<=d<N and 0<=s<=N,'in-range literal registers')
        if op==0:
            old,new=(c,s)if back else(s,c)
            need(current[d]==old,'MOVE current frame')
            frames.nested(s,c)
            need(frames.get(c)[0]-frames.get(s)[0]==f and f>0,'positive exact MOVE tariff')
            current[d]=new;H[f]+=1
        elif op==1:
            need(d!=s and current[d]==current[s]==f,'ADD common actual frame')
            need(d!=opened,'copied source is immutable')
            rows[d]=plus(rows[d],rows[s],-c if back else c);ADD+=1
            max_l1=max(max_l1,sum(map(abs,rows[d].values())))
            positive[d]+=abs(c)*positive[s];positive_max=max(positive_max,positive[d])
        elif op==(3 if back else 2):
            need(s==N and opened is None and not rows[N]and current[N]is None,'fresh PRIVATEZERO COPY')
            need(current[d]==c,'COPY actual source frame');frames.nested(f,c)
            tariff=frames.get(c)[0]-frames.get(f)[0];need(tariff>0,'paid COPY tariff')
            rows[N]=dict(rows[d]);current[N]=f;opened=d;H[tariff]+=1;COPY+=1
            positive[N]=positive[d]
        else:
            need(op==(2 if back else 3)and opened==d and s==N,'ERASE same source and private')
            need(current[d]==c and current[N]==f and rows[d]==rows[N],'ERASE original transported snapshot')
            rows[N]={};current[N]=None;opened=None;positive[N]=0
    need(current[:-1]==(word['start']if back else word['final'])and current[N]is None and opened is None,'all endpoints and PRIVATEZERO return')
    return rows,dict(H=dict(sorted(H.items())),mass=sum(r*c for r,c in H.items()),ADDs=ADD,COPYs=COPY,
                     prefix_row_L1=max_l1,positive_envelope=positive_max)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');a=ap.parse_args()
    receipt=json.loads((LANE/'FIVE-TERMINALS.json').read_text())
    blob=gzip.decompress((LANE/'FIVE-TERMINALS-WORD.json.gz').read_bytes())
    need(sha256(blob).hexdigest()==EXPECTED_WORD,'independent frozen candidate word')
    source=Path(next(iter(receipt['source'])));rawbytes=source.read_bytes()
    need(sha256(rawbytes).hexdigest()==EXPECTED_GEOMETRY,'independent frozen geometry')
    raw=json.loads(gzip.decompress(rawbytes));word=json.loads(blob);frames=Frames(raw)
    rows,forward=replay(word,frames)
    expected=[1<<j for j in range(N)]+[0]
    for p in range(111):expected[111+p]^=1<<p
    actual=[sum((a&1)<<j for j,a in r.items())for r in rows]
    need(actual==expected,'all660 independent persistent F2 input columns, private zero')
    need(all(rows[j]=={j:1}for j in list(range(111))+list(range(222,N)))and not rows[N],'integer source/helper restoration')
    restored,roundtrip=replay(word,frames,True,rows)
    need(restored==[{j:1}for j in range(N)]+[{}],'literal two-sided legal-state roundtrip')
    inverse_rows,inverse=replay(word,frames,True)
    restored2,_=replay(word,frames,False,inverse_rows)
    need(restored2==[{j:1}for j in range(N)]+[{}],'inverse-first all-column roundtrip')
    need(word['start']==raw['start']and word['final'][:222]==raw['final'][:222],'unchanged public entrances and exits')
    inventory=Counter(frames.get(word['final'][h])[0]for h in range(222,N))
    need(inventory=={4:5,8:433},'actual heterogeneous residual stock')
    need(forward['H']=={1:1322,2:1342,3:79,4:39,5:102,6:11,7:18}and forward['mass']==5101,'complete independent paid histogram')
    need(forward['COPYs']==9 and forward['ADDs']==36005,'complete COPY/ADD counts')
    need(forward['positive_envelope']==8402567 and inverse['positive_envelope']==630744,'both changed positive envelopes')
    Fwd=forward['positive_envelope'];Rev=inverse['positive_envelope']
    g104=64*Fwd**3*Rev**2;g192=2**18*Fwd**5*Rev**4
    need(g104>=2**104 and g192>=2**192,'inherited precision caps really fail')
    # Independent fail-closed endpoint and scalar controls.
    bad=dict(word);bad['final']=word['final'][:];bad['final'][462]=1
    try:replay(bad,frames)
    except ValueError:pass
    else:raise ValueError('false full terminal accepted')
    changed=[dict(r)for r in rows];changed[462]=plus(changed[462],{47:1},2)
    need([sum((v&1)<<j for j,v in r.items())for r in changed]==expected and changed[462]!={462:1},'F2 alone does not imply integer helper return')
    out=dict(status='PASS_INDEPENDENT_FIVE_TERMINAL_WORD_WITH_PRECISION_CAP_FAILURE',no_new_kappa=True,
             source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),word_sha256=EXPECTED_WORD,
             geometry_sha256=EXPECTED_GEOMETRY,persistent_columns=660,private_zero_slots=1,
             checked_frames=len(frames.data),checked_nested_pairs=len(frames.pairs),
             forward=forward,inverse=inverse,roundtrip=roundtrip,helper_inventory=dict(inventory),
             inherited_precision_diagnostics={'104_bit_expression':str(g104),'bit_length_104':g104.bit_length(),
                                             '192_bit_expression':str(g192),'bit_length_192':g192.bit_length(),
                                             'both_strict_caps_pass':False},
             controls=['Declaring the retired helper FULL fails actual endpoint check.',
                       'An even integer dirty error passes F2 and fails exact helper restoration.'],
             limits=['Independent finite word, dyadic projector and legal snapshot verification.',
                     'Generic exact-stream operator proof is separate from all-size physical owner/compiler admission.',
                     'Old H2/H4 syntax and 104/192-bit precision admission are not inherited; no outer exponent.'])
    out=json.loads(json.dumps(out));dest=HERE/'INDEPENDENT-FIVE-TERMINALS.json'
    if a.write:dest.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(dest.read_text())==out,'independent receipt differs')
    print(out['status'],len(frames.data),'frames',len(frames.pairs),'nested pairs')

if __name__=='__main__':main()
