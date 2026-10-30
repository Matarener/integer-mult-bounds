#!/usr/bin/env python3
"""Bounded native-chart retiming of a fixed exact physical event word.

Apache-2.0; substantial OpenAI Codex assistance. Positive outputs are exact
replayed words; a failed beam search establishes no optimization lower bound.
"""
from pathlib import Path
from collections import Counter
from math import isqrt
from heapq import nsmallest
import argparse, hashlib, json
from chronology import Op, ident, need
from batch_paid_progress import operator, replay

HERE = Path(__file__).resolve().parent


def search(events, banks, planes, ambient, beam, exponent, all_masks):
    cap = isqrt((ambient * ambient - 1) // 8)
    # Ordering heuristic only. Mathematical admission never uses these floats.
    costs = [0.0]
    for k in range(1, planes + 1):
        costs.append(min(costs[k - j] + 2*j * (ambient/(2*j))**exponent
                         for j in range(1, min(k, cap) + 1)))
    states = {(0,) * banks: (0.0, ())}
    counts = []
    full = (1 << planes) - 1
    for index, e in enumerate(events):
        kind = e['kind']
        if kind == 'ADD':
            dst, src = e['dst'], e['src']
            candidates = {}
            for state, (cost, path) in states.items():
                a, b = state[dst], state[src]
                masks = range(full + 1) if all_masks else sorted({0, full, a, b, a & b, a | b})
                for mask in masks:
                    s = list(state)
                    s[dst] = s[src] = mask
                    s = tuple(s)
                    c = cost + costs[(a ^ mask).bit_count()] + costs[(b ^ mask).bit_count()]
                    old = candidates.get(s)
                    if old is None or c < old[0]:
                        candidates[s] = (c, path + (mask,))
            kept = nsmallest(beam, candidates.items(), key=lambda kv: (kv[1][0], kv[0]))
            states = dict(kept)
            counts.append(dict(event=index, expanded=len(candidates), retained=len(states)))
        elif kind == 'BANK_SWAP':
            i, j = e['banks']
            converted = {}
            for state, value in states.items():
                s = list(state)
                s[i], s[j] = s[j], s[i]
                converted[tuple(s)] = value
            states = converted
        else:
            g = operator(e['operator'])
            i = e['bank']
            converted = {}
            for state, value in states.items():
                moved = sum(1 << g.perm[j] for j in range(planes) if state[i] >> j & 1)
                s = list(state)
                s[i] = g.mask ^ moved
                converted[tuple(s)] = value
            states = converted
    best_state, (cost, path) = min(states.items(), key=lambda kv:
                                  (kv[1][0] + sum(costs[m.bit_count()] for m in kv[0]), kv[0]))
    return path, counts, cost + sum(costs[m.bit_count()] for m in best_state)


def compile_word(events, banks, planes, ambient, choices):
    I = ident(planes)
    pending = [I] * banks
    out = []
    choice = iter(choices)
    cap = isqrt((ambient * ambient - 1) // 8)

    def emit(i, g, label):
        need(g.perm == I.perm, 'alignment is a native tensor product')
        bits = [j for j in range(planes) if g.mask >> j & 1]
        pieces = [bits[j:j+cap] for j in range(0, len(bits), cap)]
        if not pieces and g.sign != 1:
            pieces = [[]]
        product = I
        for j, piece in enumerate(pieces):
            h = Op(g.sign if j == 0 else 1, sum(1 << t for t in piece), I.perm)
            product = h @ product
            need(not piece or 2*(2*len(piece))**2 < ambient**2, 'strictly contracting child')
            out.append(dict(kind='NATIVE' if piece else 'ADDRESS_OR_UNIT', bank=i,
                            operator=h.data(), label=label))
        need(product == g, 'literal alignment phase and support')

    for e in events:
        if e['kind'] == 'ADD':
            r = Op(1, next(choice), I.perm)
            for i in (e['dst'], e['src']):
                emit(i, r.inverse() @ pending[i], 'paid chart alignment before ADD')
                pending[i] = r
            out.append(e)
        elif e['kind'] == 'BANK_SWAP':
            i, j = e['banks']
            pending[i], pending[j] = pending[j], pending[i]
            out.append(e)
        else:
            i = e['bank']
            g = operator(e['operator'])
            address = Op(1, 0, g.perm)
            q = g @ pending[i] @ address.inverse()
            need(q.perm == I.perm, 'native pending chart after actual ADDRESS conjugation')
            if address != I:
                out.append(dict(kind='ADDRESS_OR_UNIT', bank=i, operator=address.data(),
                                label='retimed original ADDRESS'))
            if q.sign != 1:
                emit(i, Op(q.sign, 0, I.perm), 'exact chart phase')
            pending[i] = Op(1, q.mask, I.perm)
    need(next(choice, None) is None, 'one prescribed alignment per ADD')
    for i in range(banks):
        emit(i, pending[i], 'paid final chart restoration')
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', choices=('four', 'six', 'six_complete'), default='four')
    parser.add_argument('--beam', type=int, default=256)
    parser.add_argument('--all-masks', action='store_true')
    parser.add_argument('--exponent', type=float, default=.005)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    if args.source == 'four':
        source = HERE / 'INDEPENDENT-SHARED-CALLER.json'
        banks, planes, ambient = 4, 6, 12
    elif args.source == 'six':
        source = HERE.parent / 'caller/NESTED-SIX.json'
        banks, planes, ambient = 6, 8, 16
    else:
        source = HERE / 'INDEPENDENT-COMPLETE-SIX.json'
        banks, planes, ambient = 6, 8, 16
    raw = source.read_bytes()
    events = json.loads(raw)['events']
    choices, widths, screen = search(events, banks, planes, ambient, args.beam,
                                    args.exponent, args.all_masks)
    compiled = compile_word(events, banks, planes, ambient, choices)
    need(replay(compiled, banks, planes) == replay(events, banks, planes),
         'all physical columns and both literal inverse orders preserved')
    H = Counter(e['operator']['native_arity'] for e in compiled if e['kind'] == 'NATIVE')
    out = dict(status='PASS_EXACT_RETIMED_NATIVE_CHART_WORD', no_new_kappa=True,
               producer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               source_path=str(source), source_sha256=hashlib.sha256(raw).hexdigest(),
               mode=args.source, beam=args.beam, all_alignment_masks=args.all_masks,
               heuristic_exponent=args.exponent, heuristic_float_cost=screen,
               choices=list(choices), beam_widths=widths, events=compiled,
               histogram=dict(sorted(H.items())), rank_mass=sum(r*c for r,c in H.items()),
               total_input_stock=ambient*banks, scalar_and_address_event_count=sum(e['kind']!='NATIVE' for e in compiled),
               invariant='Old logical bank i equals the current native-plane product times the retimed physical bank. An ADD aligns both banks to a common paid chart; ADDRESS conjugates the chart exactly; final charts are paid and restored.',
               limits=['Beam search is bounded and not an optimality or impossibility proof.',
                       'Search floats only order candidates. Exact replay verifies the saved positive identity, not a strict moment.',
                       'The six-bank source is a prefix with two unfinished pivots; retiming does not close them.',
                       'All native monomial adapters, physical scans, precision and joint BIT obligations remain paid.'])
    out = json.loads(json.dumps(out))
    suffix = f'{args.source.upper()}-{args.beam}' + ('-ALL' if args.all_masks else '-CHOSEN')
    path = HERE / f'NATIVE-CHART-{suffix}.json'
    if args.write:
        path.write_text(json.dumps(out, indent=2, sort_keys=True) + '\n')
    else:
        need(json.loads(path.read_bytes()) == out, 'saved chart search differs')
    print(out['status'], args.source, out['histogram'], 'mass', out['rank_mass'],
          'stock', out['total_input_stock'], 'no completed supplier claim')


if __name__ == '__main__':
    main()
