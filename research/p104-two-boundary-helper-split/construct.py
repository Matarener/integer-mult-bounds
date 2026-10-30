"""One fixed input-main split on PR5713, using the existing cut carrier.

Source transformations retain their predecessor credit. New construction
prepared for flyingviper with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
import json

def need(condition, message):
    if not condition:
        raise ValueError(message)

def _construct_terminal(source):
    w = deepcopy(source)
    source_bytes = json.dumps(w, sort_keys=True, separators=(',', ':')).encode()
    need(sha256(source_bytes).hexdigest() == '32adce6656e49aa020d3e6317f1c45c11fccadeeb67a8d506172d101703d2138', 'Pinned PR5713 canonical source')
    n = w['public']
    total = n + w['owned_fields']
    pivot = 708
    fresh = n
    cut = 14330
    repair = 15733
    oldmove = 17000
    need(w['program'][cut] == ['MOVE', 119, 602, 684, False], "Exact constructor obligation: w['program'][cut] == ['MOVE', 119, 602, 684, False]")
    need(w['program'][repair] == ['ADD', 154, 217, '1', 696], "Exact constructor obligation: w['program'][repair] == ['ADD', 154, 217, '1', 696]")
    need(w['program'][oldmove] == ['MOVE', 708, 602, 127, False], "Exact constructor obligation: w['program'][oldmove] == ['MOVE', 708, 602, 127, False]")

    def add(a, b, q):
        for j, v in tuple(b.items()):
            z = a.get(j, Q(0)) + q * v
            if z:
                a[j] = z
            else:
                a.pop(j, None)

    def apply(rows, e):
        op, r = e[:2]
        if op == 'MOVE':
            return
        if op in ('INIT', 'CLEAR'):
            rows[r] = {}
        elif op == 'SCALE':
            rows[r] = {j: Q(e[-2]) * v for j, v in rows[r].items()}
        else:
            if op == 'COPY':
                rows[r] = {}
            add(rows[r], rows[e[2]], Q(e[-2]))
    rows = [{r: Q(1)} for r in range(total)]
    for e in w['program'][:cut + 1]:
        apply(rows, e)
    h = dict(rows[pivot])
    add(h, rows[154], Q(1, 2))
    k = dict(h)
    add(k, {pivot: Q(1)}, Q(-1))
    need(h[pivot] == 1 and all((w['initial'][r] == 3 for r in h)), "Exact constructor obligation: h[pivot] == 1 and all((w['initial'][r] == 3 for r in h))")
    main = set(w['live']) | {r + 112 for r in w['live']}
    need({r: q for r, q in h.items() if r in main} == {154: Q(1, 4), 217: Q(1, 4)}, 'Exact constructor obligation: {r: q for r, q in h.items() if r in main} == {154: Q(1, 4), 217: Q(1, 4)}')
    candidate = deepcopy(w)
    candidate['schema'] = 'p104-terminal-input-main-split/1'
    candidate['public'] = n + 1
    candidate['initial'] = w['initial'] + [602]
    candidate['final'] = w['final'] + [127]
    candidate['final'][pivot] = 602
    program = []
    for r, q in sorted(k.items()):
        program.append(['ADD', pivot, r, str(-q), 3])
    program.extend([['ADD', 126, pivot, '-2', 3], ['ADD', 188, pivot, '2', 3]])
    prefix_count = len(program)

    def rename(r, index):
        if index > cut and r == pivot:
            return fresh
        return r + 1 if r >= n else r
    for index, original in enumerate(w['program']):
        e = deepcopy(original)
        e[1] = rename(e[1], index)
        if e[0] in ('ADD', 'COPY'):
            e[2] = rename(e[2], index)
        program.append(e)
        if index == cut:
            program.append(['ADD', pivot, 154, '1/2', 602])
    program.extend([['ADD', 126, fresh, '2', 127], ['ADD', 188, fresh, '-2', 127]])
    replayed = [{r: Q(1)} for r in range(total + 1)]
    for e in program:
        apply(replayed, e)
    wrong = []
    for r, row in enumerate(replayed):
        expected = {r: Q(1)} if r < n + 1 else {}
        if r - 112 in w['live']:
            expected[r - 112] = Q(1)
        if row != expected:
            wrong.append(r)
    need(wrong == [fresh], wrong)
    correction = {fresh: Q(1)}
    add(correction, replayed[fresh], Q(-1))
    need(fresh not in correction and all((r < n + 1 and candidate['final'][r] == 127 for r in correction)), "Exact constructor obligation: fresh not in correction and all((r < n + 1 and candidate['final'][r] == 127 for r in correction))")
    need(not {154, 217, pivot} & set(correction), 'Exact constructor obligation: not {154, 217, pivot} & set(correction)')
    cleanup = [['ADD', fresh, r, str(q), 127] for r, q in sorted(correction.items())]
    program.extend(cleanup)
    candidate['program'] = program
    for e in cleanup:
        apply(replayed, e)
    for r, row in enumerate(replayed):
        expected = {r: Q(1)} if r < n + 1 else {}
        if r - 112 in w['live']:
            expected[r - 112] = Q(1)
        need(row == expected, (r, row, expected))

    def span(b):
        s = {0}
        for x in b:
            s |= {x ^ y for y in tuple(s)}
        return s
    frames = [span(b) for b in candidate['frames']]
    current = candidate['initial'] + [None] * candidate['owned_fields']
    active = set()
    paid = Counter()
    peak = 0
    lifetimes = 0
    scalar = 0
    for e in program:
        op, r = e[:2]
        if op == 'INIT':
            need(r >= n + 1 and current[r] is None, 'Exact constructor obligation: r >= n + 1 and current[r] is None')
            active.add(r)
            current[r] = e[2]
            peak = max(peak, len(active))
            lifetimes += 1
            scalar += 2
        elif op == 'CLEAR':
            need(r in active and current[r] == e[2], 'Exact constructor obligation: r in active and current[r] == e[2]')
            active.remove(r)
            current[r] = None
            scalar += 2
        elif op == 'MOVE':
            _, _, a, b, private = e
            need(current[r] == a and private == (r in active), 'Exact constructor obligation: current[r] == a and private == (r in active)')
            need(frames[b] < frames[a] if private else frames[a] < frames[b], 'Exact constructor obligation: frames[b] < frames[a] if private else frames[a] < frames[b]')
            paid[abs(len(candidate['frames'][a]) - len(candidate['frames'][b]))] += 1
            current[r] = b
        else:
            need(current[r] == e[-1], 'Exact constructor obligation: current[r] == e[-1]')
            if op in ('ADD', 'COPY'):
                need(current[e[2]] == e[-1] and e[2] != r, 'Exact constructor obligation: current[e[2]] == e[-1] and e[2] != r')
            q = Q(e[-2])
            a, b = (abs(q.numerator), q.denominator)
            need(q and b & b - 1 == 0 and (abs(q) + 1 < 2 ** 16), 'Exact constructor obligation: q and b & b - 1 == 0 and (abs(q) + 1 < 2 ** 16)')
            scalar += 2 * (abs(a.bit_length() - b.bit_length()) + (q < 0)) if op == 'SCALE' else 2 * (2 + a.bit_length() + a.bit_count() + b.bit_length() - 1)
    need(not active and current[:n + 1] == candidate['final'], "Exact constructor obligation: not active and current[:n + 1] == candidate['final']")
    oldpaid = Counter((abs(len(w['frames'][e[2]]) - len(w['frames'][e[3]])) for e in w['program'] if e[0] == 'MOVE'))
    targets = Counter((len(candidate['frames'][candidate['final'][r]]) - len(candidate['frames'][candidate['initial'][r]]) for r in range(n + 1) if r not in main))
    oldtargets = Counter((len(w['frames'][w['final'][r]]) - len(w['frames'][w['initial'][r]]) for r in range(n) if r not in main))

    def delta(a, b):
        return {str(r): a[r] - b[r] for r in sorted(a.keys() | b.keys()) if a[r] != b[r]}
    need(delta(paid, oldpaid) == {}, "Exact constructor obligation: delta(paid, oldpaid) == {}")
    need(delta(targets, oldtargets) == {'2': 1, '7': 1, '9': -1}, "Exact constructor obligation: delta(targets, oldtargets) == {'2': 1, '7': 1, '9': -1}")
    canonical = json.dumps(candidate, sort_keys=True, separators=(',', ':')).encode()
    receipt = dict(status='PASS_EXACT_SCALAR_CHART_OWNERSHIP', source_head='a5348f7143f95fe0046b92b96172e30763c7d731', source_canonical_sha256=sha256(source_bytes).hexdigest(), word_canonical_sha256=sha256(canonical).hexdigest(), public_inputs=n + 1, owned_fields=candidate['owned_fields'], owned_lifetimes=lifetimes, owned_peak=peak, events=len(program), initial_ordinary_adds=prefix_count, cleanup_adds=len(cleanup), scalar_allowance=scalar, local_paid=dict(paid), local_targets=dict(targets), paid_delta=delta(paid, oldpaid), target_delta=delta(targets, oldtargets), signed_target_minus_paid_delta={'2': 1, '7': 1, '9': -1}, h={str(r): str(q) for r, q in sorted(h.items())}, full9_cleanup={str(r): str(q) for r, q in sorted(correction.items())}, scope='All753 rational input columns/endpoints plus exact frame containment and owned intervals. Native maps, full caller, ordinary compiler and complete pricing remain unrun.')
    return (candidate, receipt)


def construct(source):
    """Reconstruct one pinned split and commute its normalization to an actual meeting."""
    word,witness=_construct_terminal(source)
    intermediate=sha256(json.dumps(word,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    need(intermediate=='892cfd5907ee1420b40cd511098c48eb3251501a7e6196367b3bfb4189e5d1a6','Exact terminal split witness')
    p=word['program'];fresh=word['public']-1
    restores=[['ADD',126,fresh,'2',127],['ADD',188,fresh,'-2',127]]
    need(p[-120:-118]==restores,'Actual terminal normalization order')
    need(all(e[0]=='ADD' and e[1]==fresh and e[-1]==127 for e in p[-118:]),'Actual118-term terminal cleanup')
    body=p[:-120]
    anchor=['ADD',fresh,146,'1/2',127]
    need(body.count(anchor)==1,'Unique actual146 correction version')
    at=body.index(anchor)
    need(at==17523,'Exact candidate correction event')
    for event in body[at+1:]:
        need(not (event[0] in ('ADD','COPY') and event[2] in (126,188,fresh)),'No later reads from normalized fields')
        need(event[1]!=fresh,'No later continuation write')
        if event[1] in (126,188):
            need(event[0]=='ADD' and event[-1]==127,'Normalization commutes with later destination ADDs')
    inserted=restores+[['ADD',fresh,146,'-1/2',127]]
    word['program']=body[:at+1]+inserted+body[at+1:]
    word['schema']='p104-terminal-main-split-short-cleanup/1'
    canonical=json.dumps(word,sort_keys=True,separators=(',',':')).encode()
    digest=sha256(canonical).hexdigest()
    need(digest=='a1c8277189a811546bdc7b147d72e6a594504ff9585c9bf59a5681aa873abb01','Frozen final candidate')
    def scalar_cost(e):
        op=e[0]
        if op=='MOVE':return 0
        if op in ('INIT','CLEAR'):return 2
        q=Q(e[-2]);a,b=abs(q.numerator),q.denominator
        if op=='SCALE':return 2*(abs(a.bit_length()-b.bit_length())+(q<0))
        return 2*(2+a.bit_length()+a.bit_count()+b.bit_length()-1)
    scalar=sum(scalar_cost(e) for e in word['program'])
    need(scalar==221474 and len(word['program'])==25546,'Literal final scalar/event counts')
    witness=dict(witness)
    witness['terminal_intermediate_canonical_sha256']=intermediate
    witness['terminal_full9_cleanup']=witness.pop('full9_cleanup')
    witness['terminal_cleanup_adds']=witness.pop('cleanup_adds')
    witness.update(word_canonical_sha256=digest,events=len(word['program']),scalar_allowance=scalar,
        after_candidate_event=at,cleanup_anchor=anchor,early_cleanup=inserted,
        removed_terminal_events=120,early_cleanup_adds=3,
        scope='Exact source-bound split, frame/ownership/invoice checks, then a validated three-operation temporal normalization. Independent full final scalar and native/caller/pricing checks are separate obligations.')
    return word,witness
