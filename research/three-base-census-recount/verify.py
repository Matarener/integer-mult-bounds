#!/usr/bin/env python3
"""Independent recount of #4450: the THREE-base supplier's paid-event census, by separately written GF(2) code.

Reads the pinned native program (both orientations) and canonical frame table. Every frame basis is checked
independent; every paid `climb` and `center` event must move between nested frames, and its rank is recomputed as the
dimension gap (the declared rank is only compared). The 16 split center events are coalesced in adjacent pairs through
their shared middle frame. Expected (#4450): split {1:2487, 2:713, 3:232, 4:102, 5:28}; unsplit {1:2487, 2:713, 3:224,
4:102, 5:20, 8:8} = 3,554 calls, rank mass 5,157, identical in both orientations, with #4450's per-phase table; helper
increments for fields 224..631 {5:28, 6:18, 7:56, 8:93, 9:213}, mass 3,301.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXPECT_UNSPLIT = {1: 2487, 2: 713, 3: 224, 4: 102, 5: 20, 8: 8}
EXPECT_SPLIT = {1: 2487, 2: 713, 3: 232, 4: 102, 5: 28}
EXPECT_PHASE = {"A": {1: 950, 2: 12, 3: 20, 4: 38}, "B": {1: 1161, 2: 571, 3: 150, 4: 64, 5: 20},
                "cleanup_tail": {1: 72, 2: 53}, "final": {1: 304, 2: 77, 3: 54}}
EXPECT_HELPER = {5: 28, 6: 18, 7: 56, 8: 93, 9: 213}


def census():
    c=json.loads(gzip.decompress(open(ROOT / 'research/kappa-rebuild/complex/full-identity-certificates/THREE-base-FULL-IDENTITY-CANONICAL.json.gz', 'rb').read()))
    d=json.loads(gzip.decompress(open(ROOT / 'research/kappa-rebuild/complex/full-identity-certificates/THREE-base-FULL-IDENTITY-NATIVE.json.gz', 'rb').read()))
    def rank(vs):
        basis={}; r=0
        for v in vs:
            while v:
                h=v.bit_length()-1
                if h in basis: v^=basis[h]
                else: basis[h]=v; r+=1; break
        return r
    F=c['frames']; dim=[rank(f) for f in F]
    assert all(dim[i]==len(F[i]) for i in range(len(F)))
    def nested_gap(a,b):
        lo,hi=(a,b) if dim[a]<=dim[b] else (b,a)
        assert rank(F[lo]+F[hi])==dim[hi], "nested frames"
        return abs(dim[a]-dim[b])
    res={}
    for orient in ('forward','backward'):
        hist=Counter(); byphase={}; cen=[]
        for e in d[orient]:
            if e[0]=='climb':
                _,ph,field,a,b,r=e; rr=nested_gap(a,b); assert rr==r>0 and dim[b]>dim[a]
                hist[rr]+=1; byphase.setdefault(ph,Counter())[rr]+=1
            elif e[0]=='center':
                _,field,a,b,r=e; rr=nested_gap(a,b); assert rr==r>0; cen.append((a,b))
        split=hist+Counter(abs(dim[a]-dim[b]) for a,b in cen)
        pairs=[(cen[i],cen[i+1]) for i in range(0,len(cen),2)]
        assert len(cen)==16 and all(p[0][1]==p[1][0] for p in pairs)
        unsplit=hist+Counter(nested_gap(p[0][0],p[1][1]) for p in pairs)
        res[orient]={"split":dict(sorted(split.items())),"unsplit":dict(sorted(unsplit.items())),"calls":sum(unsplit.values()),
                     "rank_mass":sum(k*v for k,v in unsplit.items()),"events":len(d[orient]),
                     "by_phase":{k:dict(sorted(v.items())) for k,v in sorted(byphase.items())}}
    inc=Counter(nested_gap(c['start'][i],c['final'][i]) for i in range(224,632))
    res["helper_increments"]=dict(sorted(inc.items())); res["helper_mass"]=sum(k*v for k,v in inc.items())


    return res


def main():
    for row in json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))["files"]:
        assert hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"], row["path"]
    res = census()
    for orient in ("forward", "backward"):
        r = res[orient]
        assert r["split"] == EXPECT_SPLIT and r["unsplit"] == EXPECT_UNSPLIT, orient
        assert r["calls"] == 3554 and r["rank_mass"] == 5157 and r["events"] == 22633, orient
        assert r["by_phase"] == EXPECT_PHASE, orient
    assert res["helper_increments"] == EXPECT_HELPER and res["helper_mass"] == 3301
    print(json.dumps({"status": "PASS_THREE_BASE_CENSUS_RECOUNT", "calls": 3554, "rank_mass": 5157,
                      "unsplit": {str(k): v for k, v in EXPECT_UNSPLIT.items()}, "helper_mass": 3301,
                      "orientations": 2, "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
