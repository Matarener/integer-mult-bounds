"""Count the tested four-gate scalar pattern before frame selection.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
This is a finite pattern census, not a test of all possible rewrites.
"""
from bisect import bisect_left, bisect_right
from collections import defaultdict
from fractions import Fraction as Q


def find(word):
    public = word['public']
    program = [e for e in word['program'] if e[0] != 'MOVE' or e[1] >= public]
    touches, reads, writes = (defaultdict(list) for _ in range(3))
    for i, event in enumerate(program):
        if event[0] not in ('ADD', 'COPY', 'SCALE'):
            continue
        roles = {event[1],event[2]} if event[0] != 'SCALE' else {event[1]}
        for role in roles:
            touches[role].append(i)
        writes[event[1]].append(i)
        reads[event[2] if event[0] != 'SCALE' else event[1]].append(i)

    def next_site(sites, i):
        k = bisect_right(sites, i)
        return sites[k] if k < len(sites) else len(program)

    def previous(roles, j, skip):
        candidates = []
        for role in roles:
            sites = touches[role]
            k = bisect_left(sites, j)-1
            while k >= 0 and sites[k] in skip:
                k -= 1
            if k >= 0:
                candidates.append(sites[k])
        return max(candidates, default=-1)

    matches = []
    for i, first in enumerate(program):
        if first[0] != 'ADD' or max(first[1:3]) >= public:
            continue
        a, b = first[1:3]
        j = min(next_site(writes[b], i), next_site(reads[a], i))
        if j >= len(program):
            continue
        second = program[j]
        if second[0] != 'ADD' or max(second[1:3]) >= public:
            continue
        x, y = second[1:3]
        if len({a,b,x,y}) != 3:
            continue
        if y == a:
            c, h, eta = x, b, Q(first[-2])*Q(second[-2])
        elif x == b:
            c, h, eta = a, y, -Q(first[-2])*Q(second[-2])
        else:
            continue
        t = previous({c,h}, j, {i})
        if (t < 0 or program[t][0] != 'ADD' or program[t][1] not in (c,h)
                or program[t][2] in (c,h)):
            continue
        s = program[t][2]
        if s >= public or previous({c,h,s}, j, {i}) != t:
            continue
        u = previous({c,h,s}, t, {i})
        if (u < 0 or program[u][0] != 'ADD' or program[u][2] != s
                or {program[u][1],program[t][1]} != {c,h}):
            continue
        alpha = Q(program[u][-2] if program[u][1] == h else program[t][-2])
        beta = Q(program[u][-2] if program[u][1] == c else program[t][-2])
        if beta + eta*alpha == 0:
            matches.append(dict(first=i, second=j, previous=[u,t], roles=[c,h,s]))
    return matches
