"""Check the exact price floor for fixed P104 scalar contacts.

Ali Romman with OpenAI Codex assistance. Apache-2.0.
The input modules retain their source notices.
"""
from collections import Counter
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import gzip
import importlib.util
import json
import sys

HERE = Path(__file__).resolve().parent


def need(ok, label):
    if not ok:
        raise ValueError(label)


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / 'inputs' / (name + '.py'))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def rank(vectors):
    pivots = {}
    for value in vectors:
        while value:
            bit = value.bit_length() - 1
            if bit in pivots:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                break
    return len(pivots)


def distance(a, b):
    return 2 * rank(tuple(a) + tuple(b)) - len(a) - len(b)


def spaces(n):
    out = {frozenset([0]): ()}
    for _ in range(n):
        for span, basis in tuple(out.items()):
            for x in range(1, 1 << n):
                if x not in span:
                    larger = span | frozenset(v ^ x for v in span)
                    out.setdefault(larger, basis + (x,))
    return out


def contact_floor(w):
    main = set(w['live']) | {r + 112 for r in w['live']}
    contacts = [[] for _ in range(743)]
    for r in main:
        contacts[r].append((-1, w['initial'][r]))
    for k, e in enumerate(w['program']):
        if e[0] in ('ADD', 'COPY'):
            for r in e[1:3]:
                contacts[r].append((k, e[-1]))
        elif e[0] in ('SCALE', 'INIT', 'CLEAR'):
            contacts[e[1]].append((k, e[-1]))
    for r in main:
        contacts[r].append((len(w['program']), w['final'][r]))
    paid, helpers, intervals = Counter(), Counter(), []
    for r, seq in enumerate(contacts):
        for (i, a), (j, b) in zip(seq, seq[1:]):
            d = distance(w['frames'][a], w['frames'][b])
            if d:
                paid[d] += 1
                intervals.append([r, i, j, a, b, d])
        if r < 735 and r not in main and seq:
            helpers[distance(w['frames'][seq[0][1]], w['frames'][seq[-1][1]])] += 1
    helpers.pop(0, None)
    unused = [r for r in range(735) if r not in main and not contacts[r]]
    return paid, helpers, intervals, unused


def main():
    for pin in json.loads((HERE / 'INPUTS.json').read_text()):
        need(sha256((HERE / pin['file']).read_bytes()).hexdigest() == pin['sha256'], 'Source pin')
    c, local, v = load('clifford_exact'), load('local'), load('native_verify')
    w = json.loads(gzip.decompress((HERE / 'inputs/WORD.json.gz').read_bytes()))
    replay = local.replay(w)
    small = {}
    for n in (2, 3, 4):
        all_spaces = spaces(n)
        ops = {s: c.canonical_frame(n, b) for s, b in all_spaces.items()}
        for a, ba in all_spaces.items():
            for b, bb in all_spaces.items():
                actual = ops[a].adjoint().then(ops[b])
                r = rank([x for x, z, phase in actual.tab[n:]])
                expected = len(ba) + len(bb) - 2 * ((len(a & b)).bit_length() - 1)
                need(r == expected == distance(ba, bb), 'All-frame rank law')
        small[str(n)] = len(all_spaces) ** 2

    @lru_cache(None)
    def chart(i):
        frame = w['frames'][i]
        op = c.canonical_frame(9, tuple(frame))
        span = {0}
        for x in frame:
            span |= {v ^ x for v in tuple(span)}
        need(all(x in span and all(((x ^ z) & u).bit_count() % 2 == 0 for u in frame)
                 for x, z, phase in op.tab[9:]), 'Source chart Lagrangian')
        return op

    paid, helpers, intervals, unused = contact_floor(w)
    pairs = {(a, b) for r, i, j, a, b, d in intervals}
    main_roles = set(w['live']) | {r + 112 for r in w['live']}
    pairs |= {(w['initial'][r], w['final'][r]) for r in range(735) if r not in main_roles}
    for a, b in pairs:
        actual = chart(a).adjoint().then(chart(b))
        need(rank([x for x, z, phase in actual.tab[9:]]) == distance(w['frames'][a], w['frames'][b]),
             'Source rank floor')
    # Bind nonnested examples to the retained compiler, including global phase.
    examples = [([1], [2]), ([3, 5], [9, 17]), ([1, 2, 4], [8, 16, 32])]
    for a, b in examples:
        target = c.canonical_frame(9, tuple(a)).adjoint().then(c.canonical_frame(9, tuple(b)))
        recipe, _ = c.lower_child(target)
        need(recipe['rank'] == distance(a, b), 'Nonnested recipe price')
        v.equal(v.recipe(recipe), v.adjoint(v.frame(a, 9)) + v.frame(b, 9), 'Nonnested phase')

    old_paid = Counter({int(k): n for k, n in replay['paid'].items()})
    old_helpers = Counter({int(k): n for k, n in replay['helpers'].items()})
    need(unused == [711], 'Complete unused-helper set')
    need(old_paid - paid == old_helpers - helpers == Counter({5: 1}), 'Neutral unused helper')
    need(not paid - old_paid and not helpers - old_helpers, 'No hidden floor cost')
    need({r: old_helpers[r] - old_paid[r] for r in old_paid.keys() | old_helpers.keys()} ==
         {r: helpers[r] - paid[r] for r in old_paid.keys() | old_helpers.keys()}, 'Exact signed profile optimum')

    need(distance([1], [2]) == 2 and len([1]) - len([2]) == 0, 'False rank control')
    wrong = json.loads(json.dumps(w))
    e = next(e for e in wrong['program'] if e[0] == 'ADD')
    e[-2] = '3/8'
    try:
        local.replay(wrong)
    except ValueError:
        pass
    else:
        raise ValueError('Changed scalar identity accepted')
    mutant = json.loads(json.dumps(w))
    e = next(e for e in mutant['program'] if e[0] == 'ADD')
    e[-1] = next(i for i in range(len(w['frames'])) if i != e[-1])
    try:
        local.replay(mutant)
    except ValueError:
        pass
    else:
        raise ValueError('Wrong scalar chart accepted')
    out = {'status': 'PASS_P104_FIXED_CONTACT_CEILING', 'source_pr': 5580,
           'small_pair_counts': small, 'source_pairs': len(pairs), 'nonzero_intervals': len(intervals),
           'interval_sha256': sha256(json.dumps(intervals, separators=(',', ':')).encode()).hexdigest(),
           'paid_floor': {str(k): v for k, v in sorted(paid.items())},
           'helper_core': {str(k): v for k, v in sorted(helpers.items())},
           'unused_helpers': unused, 'neutral_target_paid_pair': {'5': 1},
           'public_inputs': replay['public_inputs'], 'owned_lifetimes': replay['owned_lifetimes'],
           'scope': 'All nonnested paths and helper endpoints, fixed scalar contacts; every 0<t<1.',
           'controls': ['false_dimension_difference', 'changed_scalar', 'changed_contact']}
    path = HERE / 'RESULT.json'
    if '--write' in sys.argv:
        path.write_text(json.dumps(out, indent=2, sort_keys=True) + '\n')
    else:
        need(out == json.loads(path.read_text()), 'Complete receipt')
    print(json.dumps(out, sort_keys=True))


if __name__ == '__main__':
    main()
