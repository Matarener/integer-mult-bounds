"""Exact rational free-operator interpreter, including literal cleanup.

Ross Richardson, with substantial OpenAI Codex assistance. Apache-2.0.
Developed independently of the PR3133 auditor; source JSON is the sole input.
All initially dirty registers are independent columns. No finite matrix fixture
is substituted for a noncommutative warp symbol.
"""
from fractions import Fraction as Q

def plus(a, b, coefficient):
    for k, v in b.items():
        x = a.get(k, 0) + coefficient*v
        if x:
            a[k] = x
        elif k in a:
            del a[k]


def left_op(row, op):
    out = {}
    for (variable, word), value in row.items():
        nextword = word[1:] if word and word[0] == -op else (op,)+word
        out[variable, nextword] = value
    return out


def scalar_inverse(g):
    if g[0] == 'warp':
        return ['warp', g[1], -g[2]]
    if g[0] == 'add':
        return ['add', g[1], g[2], -g[3], g[4]]
    assert g[0] == 'scale'
    return ['scale', g[1], g[3], g[2]]


def programs(w):
    a = w['A'][w['prelude_events']:]
    fw = list(a)
    at = {}
    for i, (pos, reg, G, U, E) in enumerate(w['warps'], 1):
        at.setdefault(pos, []).append(['warp', reg, i])
    for i in range(len(w['B'])+1):
        fw.extend(at.get(i, []))
        if i < len(w['B']):
            fw.append(w['B'][i])
    fw += w['restore']
    restored = set(map(int, w['helper_final']))
    cleanup = []
    for g in reversed(fw):
        if g[0] != 'warp' and 112 <= g[1] < 224:
            continue
        g = scalar_inverse(g)
        g[1] += 704 if g[1] in restored else 0
        if g[0] == 'add':
            g[2] += 704 if g[2] in restored else 0
        cleanup.append(g)
    corrections = [['corr', c['target'], c['source'], c['operator_word'], Q(c['coefficient'])]
                   for c in w['initial_corrections']]
    forward = (corrections + w['precondition'] + w['compensation'] + w['A']
               + w['cut'] + fw[len(a):])
    return forward, cleanup


def apply(g, rows, dual):
    kind = g[0]
    if kind == 'corr':
        _, dst, src, ops, q = g
        if dual:
            dst, src, q = src, dst, -q
            ops = [-(1000+abs(o))*(1 if o > 0 else -1) for o in ops]
        else:
            ops = list(reversed(ops))
        v = rows[src]
        for op in ops:
            v = left_op(v, op)
        plus(rows[dst], v, q)
    elif kind == 'warp':
        op = g[2]
        if dual:
            op = (1000+abs(op))*(1 if op > 0 else -1)
        rows[g[1]] = left_op(rows[g[1]], op)
    elif kind == 'add':
        dst, src, q = g[1], g[2], Q(g[3], g[4])
        if dual:
            dst, src, q = src, dst, -q
        assert dst != src
        plus(rows[dst], rows[src], q)
    else:
        assert kind == 'scale'
        q = Q(g[2], g[3])
        if dual:
            q = 1/q
        rows[g[1]] = {k: q*v for k, v in rows[g[1]].items()}



def canonical_gate(g):
    if g[0]=='warp':
        return tuple(g[:3])
    if g[0]=='add':
        return g[0],g[1],g[2],Q(g[3],g[4])
    return g[0],g[1],Q(g[2],g[3])


def literal_replay(w,dual,aliases=None):
    """Execute the supplied cleanup itself; never replace it by derivation."""
    forward,derived=programs(w)
    aliases=aliases or {}
    def execute(g):
        if g[0]=='warp':
            g=list(g)
            op=g[2]
            g[2]=(1 if op>0 else -1)*aliases.get(abs(op),abs(op))
        elif g[0]=='corr' and aliases:
            g=list(g)
            g[3]=[(1 if op>0 else -1)*aliases.get(abs(op),abs(op)) for op in g[3]]
        apply(g,rows,dual)
    live=set(range(704))-set(w['removed'])
    restored=set(map(int,w['helper_final']))
    rows={r:{(r,()):Q(1)} for r in live}
    rows.update({r+704:{} for r in restored})
    cleanup=[g[:3] if g[0]=='warp' else g[:5] if g[0]=='add' else g[:4]
             for g in w['cleanup']]
    used={r for g in cleanup for r in (g[1:3] if g[0]=='add' else g[1:2])}
    undefined=sorted(used-set(rows))
    binding=list(map(canonical_gate,cleanup))==list(map(canonical_gate,derived))
    if undefined:
        return {'pass':False,'orientation':'dual' if dual else 'forward',
                'undefined_cleanup_registers':undefined,
                'cleanup_matches_independent_derivation':binding}
    for g in forward:
        execute(g)
    pre=True
    if not dual:
        pre=all(rows[h]=={(h,()):Q(1)} for h in restored)
        pre &= all(not any(v==h for v,word in rows[r])
                   for h in restored for r in live if r!=h)
    for g in cleanup:
        execute(g)
    bad=[]
    for r in live:
        want={(r,()):Q(1)}
        if dual and r<112:want[r+112,()]=Q(-1)
        if not dual and 112<=r<224:want[r-112,()]=Q(1)
        if rows[r]!=want:bad.append(r)
    buffers=[h for h in restored if rows[h+704]]
    return {'pass':pre and not bad and not buffers,
            'orientation':'dual' if dual else 'forward',
            'independent_inputs':len(live),'private_buffers':len(restored),
            'cleanup_matches_independent_derivation':binding,
            'precleanup_helper_rows_and_isolation':None if dual else pre,
            'bad_endpoint_rows':bad,'nonzero_private_buffers':buffers,
            'undefined_cleanup_registers':undefined}
