"""All flats (line sets of K-subspaces spanned by configuration lines) of a view, with dims. Exact."""
import sys, pickle; sys.path.insert(0,sys.path[0])
from lines import *
def flats(S):
    v=S.v; out={}
    def close(idx):
        d=S.arank(idx); return frozenset(T for T in range(v) if S.arank(list(idx)+[T])==d), d
    level=[ (frozenset([T]),1) for T in range(v)]
    for f,d in level: out[f]=d
    frontier=list(out.items())
    while frontier:
        new={}
        for f,d in frontier:
            if d>=S.w: continue
            for T in range(v):
                if T in f or any(T in g and f<g for g in new): continue
                g,dg=close(sorted(f)+[T])
                if g not in out and g not in new: new[g]=dg
        out.update(new); frontier=list(new.items())
    return out
if __name__=='__main__':
    nm=sys.argv[1]; S=views()[nm]
    F=flats(S)
    from collections import Counter
    print(nm, Counter((d,len(f)) for f,d in F.items()))
    pickle.dump({f:d for f,d in F.items()},open(f'flats_{nm}.pkl','wb'))
