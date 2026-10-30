"""Paid two-source partial sums for the literal QQ16 future query.

Chris R / Clear1nsight with OpenAI assistance. Apache-2.0.
This module consumes authenticated P/R/source word supplied by its caller.
It imports no predecessor executable and has no hidden runtime inputs.
"""
from collections import defaultdict, Counter
from fractions import Fraction


def need(ok, message):
    if not ok:
        raise ValueError(message)


def choose_pairs(P, R):
    """Bounded deterministic matching inside each actual four-row support.

    Each support has at most eight ports. Exhaustive recursion chooses a
    perfect pairing maximizing equal coefficients, with lexical tie-breaking.
    This is optimal only within this one-pass, same-support pair template.
    """
    groups = defaultdict(list)
    for p in P.U + P.T:
        support = tuple(k for k in range(8) if R[k][p])
        need(len(support) == 4, 'four-entry source column')
        need(all(R[k][p] in (-1, 1) for k in support), 'signed source column')
        groups[support].append(p)
    records = []
    for support, ports in sorted(groups.items()):
        need(len(ports) in (4, 8), 'bounded source support group')
        def solve(rest):
            if not rest:
                return 0, ()
            p = rest[0]
            candidates = []
            for i, q in enumerate(rest[1:], 1):
                equal = sum(R[k][p] == R[k][q] for k in support)
                if equal < 2:
                    continue
                tail = solve(rest[1:i] + rest[i+1:])
                if tail is None:
                    continue
                score, pairs = tail
                candidates.append((score + equal - 1, ((p, q),) + pairs))
            if not candidates:
                return None
            return min(candidates, key=lambda item: (-item[0], item[1]))
        answer = solve(tuple(sorted(ports)))
        need(answer is not None, 'no legal pair decomposition')
        saving, pairs = answer
        for p, q in pairs:
            same = [k for k in support if R[k][p] == R[k][q]]
            different = [k for k in support if R[k][p] != R[k][q]]
            records.append({'ports': [p, q], 'support': list(support),
                            'same': same, 'different': different,
                            'coefficients': [[str(R[k][p]), str(R[k][q])] for k in range(8)],
                            'query_unit_adds_before': 8,
                            'query_unit_adds_after': 1 + len(same) + 2 * len(different),
                            'unit_add_saving': len(same) - 1})
        need(sum(len([k for k in support if R[k][p] == R[k][q]])-1 for p,q in pairs) == saving,
             'pair-score invoice')
    need(sorted(p for row in records for p in row['ports']) == sorted(P.U+P.T), 'exact query-port partition')
    return records


def paired_word(P, R, original):
    start = next(i for i,e in enumerate(original) if e[0] == 'map' and e[2] == 2)
    stop = max(i for i,e in enumerate(original) if e[0] == 'map' and e[2] == 2) + 1
    pairs = choose_pairs(P, R)
    block = []
    def emit(*e):
        block.append(list(e))
    for k in range(8):
        emit('clear', 'Q'+str(k), 'query2')
    intervals = []
    for row in pairs:
        first = len(block)
        p, q = row['ports']
        for name, port in (('D',p), ('E',q)):
            emit('clear', name, 'current')
            emit('add', name, 'W'+str(port), '1')
            emit('map', name, 2, port, False)
            emit('line', name, port, -1)
        # Consume unequal coefficients before overwriting D. Both payloads
        # are the actual current W values, normalized separately into F16.
        for k in row['different']:
            emit('add', 'Q'+str(k), 'D', str(R[k][p]))
            emit('add', 'Q'+str(k), 'E', str(R[k][q]))
        emit('add', 'D', 'E', '1')
        for k in row['same']:
            emit('add', 'Q'+str(k), 'D', str(R[k][p]))
        intervals.append({'ports': [p,q], 'block_start': first, 'block_stop_exclusive': len(block)})
    for p in P.A:
        emit('clear', 'D', 'query2')
        for k in range(8):
            if R[k][p]:
                emit('add', 'D', 'Q'+str(k), str(-R[k][p]/4))
        emit('line', 'D', p, 1)
        emit('map', 'D', 2, p, True)
        emit('add', 'W'+str(p), 'D', '1')
    for name in ['D','E']+['Q'+str(k) for k in range(8)]:
        emit('clear', name, 'identity')
    return original[:start] + block + original[stop:], {
        'source_window': [start,stop], 'pairs': pairs, 'pair_intervals': intervals,
        'unhosted_block': [start,start+len(block)],
        'query_unit_add_saving': sum(r['unit_add_saving'] for r in pairs)}


def host_outputs(P, word, ports=None):
    """Defer ten unused Z_U definitions; all returns are charged CLEAR/copy."""
    ports = list(P.U[:10]) if ports is None else list(ports)
    need(len(ports) == len(set(ports)) == 10 and all(p in P.U for p in ports), 'ten distinct U output hosts')
    roles = ['Q'+str(k) for k in range(8)] + ['D','E']
    aliases = dict(zip(roles, ['Z'+str(p) for p in ports]))
    start = next(i for i,e in enumerate(word) if e == ['clear','Q0','query2'])
    stop = next(i for i,e in enumerate(word) if e == ['clear','Q7','identity']) + 1
    definitions, skip = {}, set()
    for name in aliases.values():
        refs = [i for i,e in enumerate(word[:stop]) if name in e[1:3]]
        expected = [['clear',name,'current'],['add',name,'X'+name[1:],'1']]
        need([word[i] for i in refs] == expected and refs[-1] < start, 'deferred host def-use '+name)
        definitions[name] = {'source_events': refs, 'word': expected}
        skip.update(refs)
    out, restores = [], {}
    for i,e in enumerate(word):
        if i in skip:
            continue
        if e[0] == 'clear' and e[1] in aliases and e[2] == 'identity':
            continue
        if i == stop:
            for name in aliases.values():
                restores[name] = [len(out),len(out)+1]
                out.extend(definitions[name]['word'])
        out.append([aliases.get(x,x) if isinstance(x,str) else x for x in e])
    return out, {'aliases': aliases, 'deferred_definitions': definitions,
                 'restore_events': restores, 'source_window': [start,stop],
                 'removed_terminal_clears': 10}


def invoice(word):
    c = Counter(e[0] for e in word)
    for e in word:
        if e[0] == 'add':
            coefficient = abs(Fraction(e[3]))
            need(coefficient in (1, Fraction(1,4)), 'unpriced coefficient')
            c['unit_ADD' if coefficient == 1 else 'quarter_ADD'] += 1
    c['native_wrappers'] = 2*c['line']
    c['scalar_allowance'] = 8*c['unit_ADD'] + 12*c['quarter_ADD'] + 2*c['clear']
    return dict(sorted(c.items()))


def construct(P,R,original):
    unhosted, factoring = paired_word(P,R,original)
    word, hosting = host_outputs(P,unhosted)
    return word, {'factoring':factoring,'hosting':hosting,'invoice':invoice(word),
                  'word_events':len(word),'unhosted_invoice':invoice(unhosted)}
