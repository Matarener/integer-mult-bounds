"""Compose the published P104 changes. Ali Romman with OpenAI Codex. Apache-2.0.

The paid A2 witness and frame reconstruction are from zxv PR5643.
The helper relations and coalescing are from Ali Romman PR5644.
"""
from collections import Counter
from copy import deepcopy


def rethread(word, L):
    """Rebuild every typed transport from the scalar contact sequence."""
    current = word['initial'] + [None]*word['owned_fields']
    spans = [L.span(b) for b in word['frames']]
    active, program = set(), []

    def move(role, frame):
        old = current[role]
        if old == frame:
            return
        private = role in active
        L.need(old is not None and (spans[frame] < spans[old] if private else spans[old] < spans[frame]),
               'Strict nested transport at every contact')
        program.append(['MOVE', role, old, frame, private])
        current[role] = frame

    for event in word['program']:
        if event[0] == 'MOVE':
            continue
        op, role = event[:2]
        if op == 'INIT':
            L.need(current[role] is None, 'Fresh owned slot')
            active.add(role)
            current[role] = event[2]
        elif op == 'CLEAR':
            move(role, event[2])
            active.remove(role)
            current[role] = None
        else:
            move(role, event[-1])
            if op != 'SCALE':
                move(event[2], event[-1])
        program.append(event[:])
    for role in range(word['public']):
        move(role, word['final'][role])
    out = deepcopy(word)
    out['program'] = program
    return out


def a2(word, L):
    first = ['ADD',388,715,'-4',825]
    second = ['ADD',340,388,'1',825]
    scalar = [e[:] for e in word['program'] if e[0] != 'MOVE']
    L.need(scalar.count(first) == scalar.count(second) == 1, 'Unique published A2 anchors')
    at = scalar.index(first)
    L.need(scalar[at+1] == second, 'Consecutive scalar A2 gates')
    L.need([word['frames'][f] for f in [598,396,825,127]] ==
           [[491],[13,70,416],[7,10,32,65,144,272],[1,2,4,8,16,32,64,128,256]], 'Published A2 chart chain')
    scalar[at:at+2] = [['ADD',340,715,'-4',396],second,['ADD',388,715,'-4',127]]
    out = deepcopy(word)
    out['program'] = scalar
    return rethread(out, L)


def delta(old, new, key):
    c = Counter(new[key])
    c.subtract(old[key])
    return {r:n for r,n in c.items() if n}


def compose(source, witness, cleanup, L):
    before = L.replay(source)
    neutral, changes, neutral_local = cleanup.construct(source, witness, L)
    combined = a2(neutral, L)
    after = L.replay(combined)
    L.need(delta(neutral_local,after,'paid') == {2:1,3:-1,5:-1,6:1}, 'Published A2 paid change survives cleanup')
    L.need(delta(before,after,'paid') == {1:-3,2:1,3:-1,5:-4,6:4}, 'Exact composed paid change')
    L.need(before['helpers'] == after['helpers'], 'All target ranks retained')
    L.need(cleanup.owned_events(source) == cleanup.owned_events(combined), 'All owned operations retained in order')
    # Rebuild in the other order. Cuts use exact anchors and recheck full rows.
    other = a2(source, L)
    alternate = []
    for old in witness:
        w = deepcopy(old)
        matches = [i for i,e in enumerate(other['program']) if e == w['anchor']]
        L.need(len(matches) == 1, 'Unique helper anchor after the A2 change')
        w['cut'] = matches[0]
        other, receipt = cleanup.relation(other, w, L)
        alternate.append(receipt)
    other = rethread(other, L)
    L.need(other['program'] == combined['program'], 'Both composition orders give the same literal word')
    L.need(L.replay(other) == after, 'Second composition endpoint')
    combined['schema'] = 'p104-a2-cleanup-composition/1'
    return combined, {'cleanup_then_A2':changes, 'A2_then_cleanup':alternate}, after, neutral, before
