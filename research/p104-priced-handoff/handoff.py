"""Derive WORD.json.gz from PR5561's headline word by one priced successor hand-off.  Apache-2.0.

Prepared for Joel Pulikkan (GamingPuzzled) with Claude Opus 5.5 (Anthropic), via Claude Code.

Helper 706 (initial dim 0, final dim 9) is last read at event 15443 (ADD 121 += -2*706, frame 549,
dim 7).  From then on its row is 706 + D, and the only use left is the uncompute
ADD 706 += -1/2*173 at frame 127 (dim 9, event 17252) after the climb 549 -> 127 (event 17251).
Main register 173 sits at frame 559 (dim 8, 549 < 559 < 127) from event 13089 to event 17248, and its
row is constant after event 13097, so -1/2*row(173) = -D already at event 15443.

Successor hand-off at F = 559 (PR5472 pattern, co-framed cancellation with one partner):
helper 706 climbs 549 -> 559, cancels D there, and ends at F.  The successor would start at F and
carry no data to the old final frame, so it is a rank-1 spectator (moment-neutral, like PR5553's
"Variant A") and is omitted.  The word therefore changes by:
  * insert after event 15443:  MOVE 706 549->559 ;  ADD 706 += -1/2*173 @559
  * delete events 17251 (MOVE 706 549->127) and 17252 (ADD 706 += -1/2*173 @127)
  * final[706]: 127 -> 559
Same event count (25,140), same scalar events (one ADD moved and relabelled), 735 public inputs.
Paid per call: one rank-2 climb -> one rank-1 climb; credited helper 706: rank 9 -> 8.
"""
import gzip,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
H,J,T,F=706,173,15443,559
OLD_MOVE=['MOVE',H,549,127,False]
OLD_ADD=['ADD',H,J,'-1/2',127]

def need(ok,why):
    if not ok: raise ValueError(why)

def source():
    return json.loads(gzip.decompress((HERE/'inputs'/'pr5561-WORD.json.gz').read_bytes()))

def positions(P):
    iM=[i for i,e in enumerate(P) if e==OLD_MOVE]; iA=[i for i,e in enumerate(P) if e==OLD_ADD]
    need(iM==[17251] and iA==[17252],'pinned uncompute events')
    need(P[T]==['ADD',121,H,'-2',549],'last read of helper 706')
    need(all(H not in e[1:3] for e in P[T+1:17251] if e[0] in('ADD','COPY')) and
         all(e[1]!=H for e in P[T+1:17251]),'helper 706 idle between its last read and the uncompute')
    return iM,iA

def handoff(w,frame=F,coef='-1/2',stop=True,lower_final=True):
    w=json.loads(json.dumps(w)); P=w['program']
    iM,iA=positions(P)
    ins=([['MOVE',H,549,frame,False]] if stop else [])+[['ADD',H,J,coef,frame]]
    w['program']=P[:T+1]+ins+[e for i,e in enumerate(P[T+1:],T+1) if i not in(iM[0],iA[0])]
    if lower_final: w['final'][H]=frame
    return w

def dump(w,path):
    Path(path).write_bytes(encoded(w))

def encoded(w):
    import io
    b=io.BytesIO()
    with gzip.GzipFile(fileobj=b,mode='wb',mtime=0) as g: g.write(json.dumps(w,sort_keys=True,separators=(',',':')).encode())
    return b.getvalue()

if __name__=='__main__':
    dump(handoff(source()),HERE/'WORD.json.gz'); print('wrote WORD.json.gz')
