"""Census: stops X of register r (A->X->B) whose every partner at X could swap an ADJACENT stop of its own for B (next stop)
or A (previous stop) under strict nesting -- the PR5907 mechanism (helper 703: 593->859->127 became 593->712->127)."""
import json, collections, sys
import p104
from rung import timelines
w = p104.read(sys.argv[1]); prog = w['program']; S = p104.spans(w)
tl, moves = timelines(w)
n = w['public']
def stops_of(x):
    times, frames = tl[x]
    return [(frames[a], times[a]+1, times[a+1] if a+1 < len(times) else len(prog)) for a in range(len(times))]
touch = lambda p, x: prog[p][1] == x or (prog[p][0] in ('ADD', 'COPY') and prog[p][2] == x)
cnt = collections.Counter(); good = []
for r in sorted(moves):
    if r >= n: continue
    for mi in range(len(moves[r])-1):
        i, j = moves[r][mi], moves[r][mi+1]; A, X, B = prog[i][2], prog[i][3], prog[j][3]
        U = [p for p in range(i+1, j) if touch(p, r)]
        partners = {}
        for p in U:
            e = prog[p]
            if e[0] in ('ADD', 'COPY'):
                partners.setdefault(e[2] if e[1] == r else e[1], []).append(p)
        okall, kinds = True, []
        for o, ps in partners.items():
            if o >= n: okall = False; why = 'owned partner'; break
            st = stops_of(o)
            k = [a for a, (f, s0, e0) in enumerate(st) if f == X and s0 <= ps[0] < e0]
            if not k: okall = False; why = 'partner stop?'; break
            a = k[0]; opts = []
            if a+1 < len(st):
                Y = st[a+1][0]; Yn = st[a+2][0] if a+2 < len(st) else None
                if S[X] < S[B] and (Yn is None or S[B] < S[Yn]) and B != Y:
                    opts.append(('fwd', o, Y, len([p for p in range(st[a+1][1], st[a+1][2]) if touch(p, o)])))
            if a > 0:
                Y = st[a-1][0]; Yp = st[a-2][0] if a >= 2 else None
                if S[A] < S[X] and (Yp is None or S[Yp] < S[A]) and A != Y:
                    opts.append(('bwd', o, Y, len([p for p in range(st[a-1][1], st[a-1][2]) if touch(p, o)])))
            if not opts: okall = False; why = 'nesting'; break
            kinds.append(opts)
        if okall:
            cnt['ok'] += 1; good.append({'reg': r, 'stop': mi, 'U': len(U), 'A': A, 'X': X, 'B': B, 'partners': kinds})
        else:
            cnt[why] += 1
print(cnt)
json.dump(good, open(sys.argv[2], 'w'))
for g in good[:15]: print(g)
