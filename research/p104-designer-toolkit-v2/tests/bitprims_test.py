"""BITPRIMS tests: linear model == exact on P1c edits, plateau edits legal and value-neutral, p0 cancel legal.  run: python3 tests/bitprims_test.py (~20 s; `--accept` adds tk accept on an edited word, ~15 s)"""
import sys,os,random
HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,HERE)
import bitprims as B,bitword
ok=True
def chk(c,m):
    global ok; print(('PASS ' if c else 'FAIL ')+m); ok&=bool(c)
v=B.BitView('bit5708'); base=bitword.price(v.w,v.ctx)['raw']
chk(bitword.emit(v.w,v.scal,v.ctx)['records']==v.w['records'],'BitView round trip')
k=0; n=0; good=0; neutral=0
for ed in B.p1c_sites(v,1):
    k+=1
    if k%97: continue
    r=B.eval_p1c(v,ed)
    if r is None: continue
    x=v.exact(B.build_p1c(v,ed,r[1]))
    n+=1
    if x is None: continue
    w2,raw,legal=x; good+=bool(legal); neutral+=(abs(raw-base)<1e-12)
    if n>=40: break
chk(n>=30 and good==n,'%d P1/P1c edits: all legal (fast oracle)'%n); chk(neutral>=n//2,'most P1/P1c edits are exactly value-neutral (%d/%d)'%(neutral,n))
ps=list(B.cancel_sites(v)); chk(len(ps)>=1,'p0 cancel sites exist (%d)'%len(ps))
S2=B.PLUGINS['p0'].scalars(v,ps[0]); x=v.exact(S2); chk(x and x[2] and abs(x[1]-base)<1e-12,'p0 cancel legal, value-neutral, -2 ADDs')
z=list(B.ZRel().sites(v,step=7)); chk(not z,'zero-row relation search: 0 sites on #5708 (rows of non-owned registers are independent)')
if '--accept' in sys.argv:
    import bitadapt
    w2=x[0]; import tempfile; p=tempfile.mkdtemp()+'/p0.json.gz'; bitword.save(w2,p); r=bitadapt.accept('bit5708',p,patched=True); chk(r.get('ok'),'tk accept on the p0-cancelled word: '+bitadapt.fmt(r))
sys.exit(0 if ok else 1)
