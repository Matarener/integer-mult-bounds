"""K2BIT tests: BIT word encodes as a k2net rendezvous program with gap 0; moves keep legality + value.  run: python3 tests/k2bit_test.py (~15 s)"""
import sys,os,random
HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,HERE)
import bitword
from synth import k2bit
import k2bit_search as KS
ok=True
def chk(c,m):
    global ok; print(('PASS ' if c else 'FAIL ')+m); ok&=bool(c)
ctx=bitword.Ctx('bit5708'); w=ctx.baseword; net=k2bit.encode(w)
chk(k2bit.decode(net)['records']==w['records'],'encode/decode identity')
chk(k2bit.rendezvous(net,ctx)==0,'0 rendezvous violations')
v,_=k2bit.value(net,ctx); chk(v==bitword.price(w,ctx)['raw'],'net value == bitword.price (gap 0)')
chk(bitword.admitted_fine(v,ctx)==__import__('fractions').Fraction(ctx.prof['ordinary']['admitted']),'admitted reproduces the published value')
chk(k2bit.rederive(net,ctx)['events']==net['events'],'MOVE re-derivation is the identity')
st=KS.S('bit5708'); rng=random.Random(4); base=st.cost
for m in ('reloc','conj','merge'):
    n=0
    for _ in range(4000):
        if st.step(rng,0.0,(m,)) is not None: n+=1
        if n>=50: break
    w2,V=st.verify(); chk(not V and abs(st.cost-base)<1e-9 and w2 is not None and bitword.price(w2,ctx)['raw']==v,'%s: %d accepted moves, legal, exactly value-neutral'%(m,n))
sys.exit(0 if ok else 1)
