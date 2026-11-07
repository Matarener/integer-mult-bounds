# Cross-check for the hand Cap6 / Cap4 route (CENSUS-PLAN §6): labels = weight-3/7 vectors of F2^9 minus 16 (RL).
# (1) RL = the 16 weight-3/7 vectors that are not port labels; (2) for z != 0: N(z) = n_P(z) + n_RL(z) is 56 with
# wt z = 1, 2 (mod 4), or >= 64; (3) no 3-dim W with all 7 weights = 1, 2 (mod 4); (4) port labels distinct, odd.
import os, re, itertools
L = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lean')
s = open(L + '/BForm/E8/Data.lean').read(); s = s[s.index('def portBits'):]; s = s[s.index('[') + 1:s.index(']')]
PB = list(map(int, re.findall(r'\d+', s))); assert len(PB) == 104
wt = lambda n: bin(n).count('1')
S = [n for n in range(512) if wt(n) in (3, 7)]; RL = [n for n in S if n not in PB]
print('|S| =', len(S), '|RL| =', len(RL), 'RL =', RL, ' ports in S:', all(p in S for p in PB), ' distinct:', len(set(PB)) == 104)
bad = 0; vals = {}
for z in range(1, 512):
    N = sum(wt(p & z) % 2 for p in PB) + sum(wt(r & z) % 2 for r in RL)
    vals[N] = vals.get(N, 0) + 1
    if not ((N == 56 and wt(z) % 4 in (1, 2)) or N >= 64): bad += 1
print('(2) values of N:', sorted(vals.items()), ' bad:', bad)
G = set(z for z in range(1, 512) if wt(z) % 4 in (1, 2)); cnt = 0
for a, b, c in itertools.combinations(sorted(G), 3):
    if all(x in G for x in (a ^ b, a ^ c, b ^ c, a ^ b ^ c)) and c != a ^ b: cnt += 1
print('(3) 3-spaces inside wt = 1,2 mod 4:', cnt)
print('ALL OK' if bad == 0 and cnt == 0 and len(RL) == 16 else 'FAIL')
