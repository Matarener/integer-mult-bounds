"""MARKETS: sink-grouping sweep -- all 5040 orders of the D3 edge directions (inst2 assigns each common port to the first edge in order),
model R0 after rt.build (b0 params) + edges.land.  usage: sweep.py OUT.jsonl"""
import sys,itertools,json
sys.path.insert(0,__import__('os').path.dirname(__import__('os').path.abspath(__file__)))
def main():
    import route_b as realB; realB.patch_geo()
    import rt, allh, edges
    f=open(sys.argv[1],'w')
    for p in itertools.permutations(realB.D3):
        D=list(p); I=realB.inst2(allh.hedges(D),True); N,_=rt.build(I,lam=4.0,seed=0,land=False,pairdirs=set(D))
        b=rt.r0(N)[1]; yt=edges.land(N,I)
        f.write(json.dumps(dict(D=D,R0=round(rt.r0(N)[1]+yt,1),bottom=round(b,1)))+'\n'); f.flush()
if __name__=='__main__': main()
