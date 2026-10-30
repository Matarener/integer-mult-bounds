#!/usr/bin/env python3
"""Exact lazy progress scheduling on an already paid physical caller word.

Apache-2.0; substantial OpenAI Codex assistance. This changes the invoice
of a literal word, never its source contract or endpoint.
"""
from pathlib import Path
from fractions import Fraction
from collections import Counter
from math import isqrt
import argparse, hashlib, json, re
from chronology import Op, ident, need

HERE = Path(__file__).resolve().parent


def operator(data):
    return Op(data['sign'], sum(1 << i for i in data['native_blocks']),
              tuple(data['block_permutation']))


def schedule(events, banks, planes, ambient):
    """Invariant: old logical bank i = pending[i] * new physical bank i.

    A deferred progress is left-multiplied into pending. A unary query can
    cross pending only after an exact commutation check. An ADD can cross
    only equal pending operators on its two arbitrary dirty fields. A bank
    swap exchanges the pending labels. Otherwise pending is first flushed.
    These cases are a direct induction for arbitrary noncommuting inputs.
    """
    I = ident(planes)
    pending = [I] * banks
    out, decisions = [], []
    cap_planes = isqrt((ambient * ambient - 1) // 8)
    need(cap_planes > 0, 'a strictly contracting native plane fits')

    def flush(i, reason):
        g = pending[i]
        need(g.perm == I.perm, 'pending progress remains a native-plane product')
        indices = [j for j in range(planes) if g.mask >> j & 1]
        pieces = [indices[j:j + cap_planes] for j in range(0, len(indices), cap_planes)]
        if not pieces and g.sign != 1:
            pieces = [[]]
        product = I
        for j, piece in enumerate(pieces):
            h = Op(g.sign if j == 0 else 1, sum(1 << t for t in piece), I.perm)
            product = h @ product
            out.append(dict(kind='NATIVE' if piece else 'ADDRESS_OR_UNIT', bank=i,
                            operator=h.data(), label='paid grouped pending progress',
                            flush_reason=reason))
            need(not piece or 2 * (2 * len(piece)) ** 2 < ambient ** 2,
                 'every emitted grouped child strictly contracts')
        need(product == g, 'exact grouped phase and all pending planes')
        decisions.append(dict(bank=i, reason=reason, pending=g.data(),
                              emitted_arities=[2 * len(x) for x in pieces]))
        pending[i] = I

    for index, e in enumerate(events):
        kind = e['kind']
        is_progress = (kind == 'NATIVE' and
                       re.fullmatch(r'query\d+ (?:target fresh|inactive fresh progress)',
                                    e.get('label', '')) is not None)
        if is_progress:
            g = operator(e['operator'])
            need(g.perm == I.perm and g.mask.bit_count() == 1,
                 'only explicitly labelled single fresh progress can be delayed')
            pending[e['bank']] = g @ pending[e['bank']]
            continue
        if kind == 'ADD':
            i, j = e['dst'], e['src']
            if pending[i] != pending[j]:
                flush(i, f'ADD at input event {index}')
                flush(j, f'ADD at input event {index}')
        elif kind == 'BANK_SWAP':
            i, j = e['banks']
            pending[i], pending[j] = pending[j], pending[i]
        else:
            i = e['bank']
            g = operator(e['operator'])
            if g @ pending[i] != pending[i] @ g:
                flush(i, f'noncommuting unary at input event {index}')
        out.append(e)
    for i in range(banks):
        flush(i, 'complete endpoint')
    return out, decisions


def plus(a, b, coefficient=1):
    out = dict(a)
    for k, v in b.items():
        out[k] = out.get(k, 0) + coefficient * v
        if not out[k]:
            del out[k]
    return out


def left(g, a):
    out = {}
    for h, v in a.items():
        product = g @ h
        unsigned = Op(1, product.mask, product.perm)
        out = plus(out, {unsigned: product.sign * v})
    return out


def identity(banks, planes):
    return [[{ident(planes): Fraction(1)} if i == j else {}
             for j in range(banks)] for i in range(banks)]


def apply(rows, e, inverse=False):
    out = [[dict(x) for x in row] for row in rows]
    if e['kind'] == 'ADD':
        i, j = e['dst'], e['src']
        c = Fraction(e['coefficient']) * (-1 if inverse else 1)
        out[i] = [plus(a, b, c) for a, b in zip(out[i], out[j])]
    elif e['kind'] == 'BANK_SWAP':
        i, j = e['banks']
        out[i], out[j] = out[j], out[i]
    else:
        g = operator(e['operator'])
        if inverse:
            g = g.inverse()
        i = e['bank']
        out[i] = [left(g, x) for x in out[i]]
    return out


def replay(events, banks, planes):
    start = identity(banks, planes)
    out = start
    for e in events:
        out = apply(out, e)
    recovered = out
    for e in reversed(events):
        recovered = apply(recovered, e, True)
    need(recovered == start, 'literal inverse all arbitrary columns')
    recovered = start
    for e in reversed(events):
        recovered = apply(recovered, e, True)
    for e in events:
        recovered = apply(recovered, e)
    need(recovered == start, 'literal inverse opposite order')
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    source = HERE / 'INDEPENDENT-SHARED-CALLER.json'
    data = source.read_bytes()
    original = json.loads(data)
    events = original['events']
    new, decisions = schedule(events, 4, 6, 12)
    need(replay(events, 4, 6) == replay(new, 4, 6),
         'all four physical output columns preserved including native phases')
    H = Counter(e['operator']['native_arity'] for e in new if e['kind'] == 'NATIVE')
    old_H = Counter(e['operator']['native_arity'] for e in events if e['kind'] == 'NATIVE')
    need(sum(r * c for r, c in H.items()) == sum(r * c for r, c in old_H.items()),
         'batching does not claim any removed native rank mass')
    # A legal batch is not permission to drop its paid transform.
    mutant = [e for e in new if e.get('label') != 'paid grouped pending progress']
    need(replay(mutant, 4, 6) != replay(events, 4, 6), 'omitted grouped progress rejected')
    out = dict(status='PASS_EXACT_PAID_PROGRESS_BATCHING', no_new_kappa=True,
               producer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               source_path=str(source), source_sha256=hashlib.sha256(data).hexdigest(),
               plane_algebra_sha256=hashlib.sha256((HERE / 'chronology.py').read_bytes()).hexdigest(),
               original_histogram=dict(sorted(old_H.items())),
               batched_histogram=dict(sorted(H.items())), rank_mass=sum(r*c for r,c in H.items()),
               events=new, decisions=decisions,
               proof='Inductively old bank i equals pending[i] times new bank i. Equal pending products commute through ADD, commuting unary events preserve the invariant, BANK_SWAP exchanges pending products, and a flush realizes the exact pending product in strictly contracting pieces. Final pending products are identity.',
               domain='Every f>=1 in the exact signed native-plane and ADDRESS algebra; all four arbitrary dirty fields. All grouped queries remain explicitly paid.',
               controls=['Both literal inverse orders', 'All physical input columns', 'Dropped grouped progress rejected'],
               limits=['The n4 complete caller still has mass60 against stock48.',
                       'No unobserved bank interval or future scalable caller is assumed.',
                       'Native adapters, tape/controller realization, precision and compatible BIT are separate obligations.'])
    out = json.loads(json.dumps(out))
    target = HERE / 'PAID-PROGRESS-BATCHING.json'
    if args.write:
        target.write_text(json.dumps(out, indent=2, sort_keys=True) + '\n')
    else:
        need(json.loads(target.read_bytes()) == out, 'saved batching receipt differs')
    print(out['status'], out['original_histogram'], '->', out['batched_histogram'])


if __name__ == '__main__':
    main()
