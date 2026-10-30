"""NATIVE PAIR CHECK: does a MOVE between nested frames a<b (bases as lists of ints<512) have a native Gaussian recipe of rank == dim gap
with exact global phase?  (local.native() check(), verifier-exact, uses the PR's vendored clifford_exact/native_verify.)  Cache by (a,b).
python -I native_pair.py ROOT   (self-test on random nested pairs)"""
import sys,importlib.util,random,time
from functools import lru_cache
ROOT=None;C=V=None
def init(root):
    global ROOT,C,V
    ROOT=root
    def load(path,name):
        spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
    C=load(root+'/research/p104-native-channel/vendor/clifford_exact.py','nv_clifford')
    V=load(root+'/research/p104-native-channel/vendor/native_verify.py','nv_gauss')
@lru_cache(None)
def chart(b): return C.canonical_frame(9,tuple(b))
@lru_cache(None)
def ok(a,b):
    """a,b tuples (bases). returns (True, rank) or (False, reason)"""
    try:
        recipe,_=C.lower_child(chart(a).adjoint().then(chart(b)))
        exp=V.adjoint(V.frame(list(a),9))+V.frame(list(b),9)
        V.equal(V.recipe(recipe),exp,'phase')
        if recipe['rank']!=abs(len(a)-len(b)): return (False,'rank %d != gap'%recipe['rank'])
        return (True,recipe['rank'])
    except Exception as e: return (False,str(e)[:80])
if __name__=='__main__':
    init(sys.argv[1]); rnd=random.Random(5)
    def rbasis(d):
        while True:
            b=[rnd.randrange(1,512) for _ in range(d)]; s={0}
            try:
                for v in b:
                    assert v not in s; s|={x^v for x in s}
                return b
            except AssertionError: pass
    t=time.time(); n=0;bad=0
    for _ in range(30):
        b=rbasis(rnd.randrange(2,10)); k=rnd.randrange(0,len(b)); a=tuple(rnd.sample(b,k)) if k else ()
        # a = subset of b's basis -> nested
        r=ok(a,tuple(b)); n+=1; bad+= (not r[0])
        if not r[0]: print('FAIL',a,b,r)
    print('pairs',n,'fail',bad,'%.1fs'%(time.time()-t))
