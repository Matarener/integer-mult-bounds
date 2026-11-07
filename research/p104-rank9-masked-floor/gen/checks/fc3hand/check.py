# Cross-check for the hand FC3 route (NOTE 13.27 restated with weights mod 4):
# (1) every nonzero z in F2^9 with wt(z) % 4 in {0,1} has a P-frame inside O(z) = {t : lab(t).z = 1};
# (2) no 3-dim U has all 7 nonzero points with wt % 4 in {2,3} (the hand lemma; brute-force sanity check);
# (3) the witness table FW (first frame index inside O(z), or 0) for the Lean check fwOK.
import os, re, sys, itertools
L = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lean')
s = open(L + '/BForm/E8/Data.lean').read(); s = s[s.index('def portBits'):]; s = s[s.index('[') + 1:s.index(']')]
PB = list(map(int, re.findall(r'\d+', s))); assert len(PB) == 104
s = open(L + '/RankNine/Data.lean').read(); s = s[s.index('def frameData'):]; s = s[s.index(':= [') + 4:]; s = s[:s.index(']]') + 1]
FD = [list(map(int, re.findall(r'\d+', b))) for b in re.findall(r'\[([^\[\]]*)\]', s)]; assert len(FD) == 759
wt = lambda n: bin(n).count('1')
O = [sum(1 << t for t in range(104) if wt(PB[t] & z) % 2) for z in range(512)]
frm = [sum(1 << x for x in f) for f in FD]
FW = []; bad = 0
for z in range(512):
    w = next((i for i, f in enumerate(frm) if f & O[z] == f), None)
    if z and wt(z) % 4 in (0, 1) and w is None: bad += 1; print('NO FRAME', z)
    FW.append(w if w is not None else 0)
print('(1) z with wt%4 in {0,1} and no frame in O(z):', bad)
Phi = [z for z in range(1, 512) if wt(z) % 4 in (2, 3)]
PS = set(Phi); cnt = 0
for a in Phi:
    for b in Phi:
        if b <= a or a ^ b not in PS: continue
        for c in Phi:
            if c in (a, b, a ^ b): continue
            if all(x in PS for x in (c, a ^ c, b ^ c, a ^ b ^ c)): cnt += 1
print('(2) |Phi\'| =', len(Phi), ' ordered (a<b, c) triples spanning a 3-space inside Phi\':', cnt)
print('frameless O(z) count (any z):', sum(1 for z in range(1, 512) if not any(f & O[z] == f for f in frm)))
open(sys.argv[1], 'w').write(' '.join(map(str, FW)) + '\n') if len(sys.argv) > 1 else None
print('ALL OK' if bad == 0 and cnt == 0 else 'FAIL')
