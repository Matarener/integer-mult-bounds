"""BITADAPT tests: exact BIT price of the adopted packages, converter round trip, fast oracle on mutants.  run: python3 tests/bit_test.py   (~10 s; `--accept` adds the PR pipeline reproductions, ~35 s)"""
import sys,os,subprocess
HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,HERE)
import bitword
from fractions import Fraction as F
ok=True
def chk(c,m):
    global ok; print(('PASS ' if c else 'FAIL ')+m); ok&=bool(c)
for alias,want in (('bit5512',F(435496247,125*10**9)),('bit5708',F(3507719059749,10**15))):
    c=bitword.Ctx(alias); w=c.baseword; p=bitword.price(w,c)
    chk(p['admitted']==want,'%s price == %s'%(alias,want)); chk(not bitword.check(w,c,1),'%s published word legal (fast oracle)'%alias)
    if alias=='bit5708': chk(bitword.emit(w,bitword.scalars(w),c)['records']==w['records'],'bit5708 emit(scalars(word)) == word (derived Q round trip)')
    bad=dict(w,records=w['records'][:-1]); chk(bool(bitword.check(bad,c,1)),'%s truncated word rejected'%alias)
if '--accept' in sys.argv:
    import bitadapt
    for alias in ('bit5512','bit5708'):
        r=bitadapt.accept(alias,HERE+'/profiles/%s/pkg/WORD.json.gz'%alias,patched=False); chk(r.get('ok') and all(v for _,v in r.get('reproduces',[])),'%s PR pipeline reproduces published receipts'%alias)
sys.exit(0 if ok else 1)
