"""Check one necessary mixed coefficient over F2.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
Matrices use integer bit rows. A pass does not prove the full word.
"""

def need(c, m):
    if not c:
        raise ValueError(m)

def add(a, b):
    return [x ^ y for x, y in zip(a, b)]

def outer(u, v, n):
    return [v if u >> i & 1 else 0 for i in range(n)]

def mul(a, b):
    out = []
    for x in a:
        z = 0
        while x:
            low = x & -x
            z ^= b[low.bit_length() - 1]
            x ^= low
        out.append(z)
    return out

def rank(a):
    p = {}
    for x in a:
        while x:
            i = x.bit_length() - 1
            if i not in p:
                p[i] = x
                break
            x ^= p[i]
    return len(p)

def family(g):
    need(g >= 3 and g % 2 == 1, 'odd g')
    n = 2 * (g + 1)
    us = []
    vs = []
    ps = []
    labels = []
    for j in range(1, g + 1):
        for a in range(2):
            core = 1 << a * (g + 1)
            leaf = core << j
            us.append(core | leaf)
            vs.append(core | leaf)
            ps.append(add(outer(core, core, n), outer(leaf, leaf, n)))
            labels.append(j - 1)
    for a in range(2):
        core = 1 << a * (g + 1)
        leaves = (1 << g + 1) - 2 << a * (g + 1)
        p = add(outer(core, core, n), outer(leaves, leaves, n))
        for u, v in [(core, leaves), (leaves, core)]:
            us.append(u)
            vs.append(v)
            ps.append(p)
            labels.append(g + a)
    axes = []
    for c in range(g + 2):
        group = [i for i, x in enumerate(labels) if x == c]
        e = add(ps[group[0]], ps[group[1]])
        need(mul(e, e) == e, 'target idempotent')
        outs = [j for j, x in enumerate(e) if x]
        need(all((not x or x == 1 << j for j, x in enumerate(e))), 'diagonal target')
        axes.append(dict(name=str(c), calls=group, outputs=outs))
    return (dict(n=n, u=us, v=vs, axes=axes), ps, labels)

def mixed(candidate, ps, labels):
    n = candidate['n']
    tail = [0] * n
    defects = {c: [0] * n for c in set(labels)}
    for i in reversed(range(len(ps))):
        c = labels[i]
        defects[c] = add(defects[c], add(mul(ps[i], tail), mul(tail, ps[i])))
        tail = add(tail, outer(candidate['u'][i], candidate['v'][i], n))
    need(tail == [1 << j for j in range(n)], 'identity frame')
    return {c: rank(a) for c, a in defects.items() if any(a)}
