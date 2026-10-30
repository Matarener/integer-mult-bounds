"""Literal construction of the single-change controls and the composed word from selected #589.

E464 (PR #3647 ancestry R438, helper464 GL): delete A[224] = [56,464,[54]] and replace
A[1986..1988] (old D4 node at frame 506) by the ten-gate node read from the PR's R438 word.
E470 (#1043, Ali Romman): delete A[230] = [79,470,[77]] and replace A[1993] = [79,444,[470]]
by [186,444,[77]].  Indices are #589 A indices.  Deleted helpers are removed and higher ids
renumbered; D0 and C are rebuilt from the raw word (wordsem.rebuild_DC)."""
import copy
from wordsem import need, rebuild_DC

E464_DEL = 224
E464_DEL_GATE = [56, 464, [54]]
E464_NODE_AT = (1986, 1989)
E464_OLD_NODE = [[506, 349, [6, 56, 233, 319, 322, 340, 462, 463]],
                 [506, 340, [233, 241, 319, 349, 464]],
                 [506, 241, [6, 56, 233, 319, 322, 463, 464]]]
E470_DEL = 230
E470_DEL_GATE = [79, 470, [77]]
E470_READ = 1993
E470_OLD_READ = [79, 444, [470]]
E470_NEW_READ = [186, 444, [77]]


def apply(w589, new_node=None, do464=False, do470=False, read=None, read_at=None, rebuild=True):
    """Return (word, deleted helpers, renaming, origin keys of the A gates).  read/read_at
    override the E470 replacement gate and its position (mutants only)."""
    w = copy.deepcopy(w589)
    A = w['A']
    keys = []
    need(A[E464_DEL] == E464_DEL_GATE and A[E464_NODE_AT[0]:E464_NODE_AT[1]] == E464_OLD_NODE, 'E464 anchors changed')
    need(A[E470_DEL] == E470_DEL_GATE and A[E470_READ] == E470_OLD_READ, 'E470 anchors changed')
    out = []
    for i, g in enumerate(A):
        if do464 and i == E464_DEL:
            continue
        if do464 and E464_NODE_AT[0] <= i < E464_NODE_AT[1]:
            if i == E464_NODE_AT[0]:
                out.extend(copy.deepcopy(new_node))
                keys.extend(('A464', k) for k in range(len(new_node)))
            continue
        if do470 and i == E470_DEL:
            continue
        if do470 and i == E470_READ:
            if read_at is None and read != 'drop':
                out.append(list(read or E470_NEW_READ))
                keys.append(('A470', 0))
            continue
        out.append(g)
        keys.append(('A', i))
    if do470 and read_at is not None:
        out.insert(read_at, list(read or E470_NEW_READ))
        keys.insert(read_at, ('A470', 0))
    w['A'] = out
    dead = sorted(([464] if do464 else []) + ([470] if do470 else []))
    v = w['v']
    for q in dead:
        for sec in ('A', 'B'):
            for g in w[sec]:
                need(q != g[1] and q not in g[2], 'deleted helper %d still used in %s' % (q, sec))
        need(q not in w['ret'], 'deleted helper is retained')

    def ren(r):
        return r - sum(1 for q in dead if r > q)
    for sec in ('A', 'B'):
        w[sec] = [[f, ren(d), [ren(s) for s in srcs]] for f, d, srcs in w[sec]]
    w['ret'] = [ren(q) for q in w['ret']]
    w['start'] = [x for r, x in enumerate(w['start']) if r not in dead]
    w['final'] = [x for r, x in enumerate(w['final']) if r not in dead]
    w['R'] = w['R'] - len(dead)
    if rebuild:
        w['D'], w['C'] = rebuild_DC(w)
    else:
        w['D'], w['C'] = [], []
    return w, dead, ren, keys
