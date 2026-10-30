"""Evaluate the feasible constructions of pass 7/8: best bill (repair or minimal), local B-frame
optimisation, ideal packing ceiling compared with the starting word."""
import sys,json,copy
from fractions import Fraction as Q
from collections import defaultdict
from timeline import *
from construct2 import assemble
from repair import repair
from minimal_all import minimal_all
from frameopt import Frames,total
from ideal import ideal
tag=sys.argv[1]; files=sys.argv[2:]
w=load(tag); ev=events(w); b0,w0,*_=C.frame_bill(w); a0=ideal(b0,w0)
print('ideal of starting word',f'{a0:.15f}')
rows=[]
for f in files:
    for r in json.load(open(f))['results']:
        if r['status']!='ok': continue
        rows.append(r)
best=defaultdict(lambda:None)
for r in rows:
    h=r['h']; P=C.span(tuple(r['P'])); a={int(k):Q(v) for k,v in r['a'].items()}
    place={int(k):p for k,p in r['best']['place'].items()}
    ins=[(place[k],['add',k,h,q.numerator,q.denominator]) for k,q in sorted(a.items())]
    for mode in ('repair','minimalB','minimal_all'):
        try:
            x,mark=assemble(w,ev,h,P,r['cut'],ins)
            if mode=='repair': x,_=repair(x,mark,cleanup=False)
            elif mode=='minimalB': x,_=repair(x,mark,minimal_B=True,cleanup=False)
            else: x,_=minimal_all(x,mark)
            C.frame_bill(x)
        except Exception: continue
        fr=Frames(x); fr.optimize(); x=fr.write()
        try: b,wd,*_=C.frame_bill(x)
        except Exception: continue
        an=ideal(b,wd)
        if best[h] is None or an>best[h][0]:
            d={k:b.get(k,0)-b0.get(k,0) for k in set(b)|set(b0) if b.get(k,0)!=b0.get(k,0)}
            best[h]=(an,dict(sorted(d.items())),{k:wd.get(k) for k in (7,8,9)},mode,r['P'],r['cut'],r['a'])
for h,v in sorted(best.items()):
    an,d,wd,mode,P,cut,a=v
    print(h,'d_ideal',f'{an-a0:+.3e}','d_bill',d,'widths',wd,mode,'P',P,'cut',cut,'releases',a)
