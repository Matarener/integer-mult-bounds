#!/usr/bin/env python3
"""Part B: the exact optimum of every owned helper-relation subspace on the #4610 word (both orientations).

Standard library only.  Reads Cao Yifan's #4610 word (research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz)
and #5383's eight relations (research/eight-owned-relations/RELATIONS.json), both pinned in SOURCES.json.

Model (#5377/#5383 owned-relation model, as generalised by #5433, widened here):
  * helpers whose start frame is the common input frame 0 (358: 326 rank-9, 26 rank-4, 6 rank-8 targets) are free
    inputs; a relation subspace V is a space of linear forms in them; each dimension owns one pivot helper, which
    loses its productive target (rank = final - start dimension);
  * a paid climb is free iff its logical row vanishes on the restricted domain.  Rows are tracked exactly over Q in the
    free group ring of warp words, so a row vanishes iff, for every warp word w, its coefficient vector over the
    helpers ("component") lies in V.  #5433 used only word-free rows of cold helpers;
  * a centre job (rank 8) is free iff row(centre) - row(Z) lies in V for an earlier same-frame snapshot Z.
Certificate:
  1. the distinct components of all helper-only climb rows are linearly independent over Q (225 backward, 358 forward);
  2. every centre option lies in their span, with support inside the components of a single pure climb pair;
  3. WLOG V = span(S) for a set S of components: an option outside span(S) adds a dimension whose pivot is a rank-9
     helper (option rows are pure cold), costing 9^t > 8^t;
  4. for independent S, any pivot set has a perfect matching to S inside supports (Laplace), so the lost target moment
     is >= sum_{c in S} min-target(c)^t;
  5. the climb/centre/component incidence splits into small connected pieces; each piece is enumerated exactly.
The optimum is 8 (8^t + 1 - 9^t) per backward local; #5383's eight relations attain it (an optimum, not
the unique one: replacing component 194 by 207, i.e. h288 - h294 - h296 - h297 + h300 + h303 = 0, gives a
different eight-dimensional optimal space; checked below as a regression, found in review by zxv).
Forward optimum 0.
Usage: python3 -I -B relations.py [--write]
"""
import argparse, collections, gzip, hashlib, itertools, json
from decimal import Decimal as D, getcontext
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
WORD = ROOT / 'research' / 'kappa-round3-warp-20261022' / 'ACTUAL-WORD.json.gz'
RELATIONS = ROOT / 'research' / 'eight-owned-relations' / 'RELATIONS.json'
PAID = {1: 2201, 2: 412, 3: 510, 4: 127, 5: 40, 8: 8}
C_SELECTED = D('0.003027288235')
NL = 632
getcontext().prec = 60


def require(ok, message):
    if not ok:
        raise SystemExit('FAIL: ' + message)


def pinned_inputs():
    for row in json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))['files']:
        if row['usage'] == 'input' and row['path'] in (str(WORD.relative_to(ROOT)), str(RELATIONS.relative_to(ROOT))):
            data = (ROOT / row['path']).read_bytes()
            require(hashlib.sha256(data).hexdigest() == row['sha256'], 'input drift: ' + row['path'])


def add_into(dst, src, q):
    for k, v in src.items():
        nv = dst.get(k, 0) + q * v
        if nv:
            dst[k] = nv
        else:
            dst.pop(k, None)


class Echelon:
    """Exact rational row echelon on sparse rows {column: Fraction}, tracking combinations of added rows."""

    def __init__(self):
        self.rows = {}

    def reduce(self, v, combo=None):
        v = dict(v); combo = dict(combo or {})
        while v:
            col = min(v)
            if col not in self.rows:
                break
            f = v[col]; pv, pc = self.rows[col]
            add_into(v, pv, -f); add_into(combo, pc, -f)
        return v, combo

    def add(self, v, tag):
        v, combo = self.reduce(v, {tag: Q(1)})
        if not v:
            return False
        col = min(v); f = v[col]
        self.rows[col] = ({k: x / f for k, x in v.items()}, {k: x / f for k, x in combo.items()})
        return True


def replay(word, orient, free):
    """Exact replay; returns paid profile, helper-only climbs [(t, rank, {word: component})] and centre options."""
    c = word['canonical']; prog = word['programs'][orient]
    rows = {('L', i): {(('L', i), ()): Q(1)} for i in range(NL)}; rows[('C', 0)] = {(('C', 0), ()): Q(1)}
    frames = {('L', i): c['start'][i] for i in range(NL)}; frames[('C', 0)] = None
    centre_frames = {e[3] for e in prog if e[0] == 'center'}
    snapshots = collections.defaultdict(list)
    paid = collections.Counter(); climbs, options = [], []

    def helper_only(row):
        return bool(row) and all(r[0] == 'L' and r[1] in free for (r, wd) in row)

    def split(row):
        out = {}
        for (r, wd), q in row.items():
            out.setdefault(wd, {})[r[1]] = q
        return out

    def snap(role):
        if frames[role] in centre_frames and rows[role]:
            snapshots[frames[role]].append(dict(rows[role]))
    for t, e in enumerate(prog):
        k = e[0]
        if k == 'climb':
            X = ('L', e[2]); paid[e[5]] += 1
            if helper_only(rows[X]):
                climbs.append((t, e[5], split(rows[X])))
            frames[X] = e[4]; snap(X)
        elif k == 'center':
            X = ('C', e[1]); paid[e[4]] += 1
            for rz in snapshots[e[3]]:
                d = dict(rows[X]); add_into(d, rz, Q(-1))
                require(bool(d), 'no centre equals an earlier snapshot exactly')
                if helper_only(d):
                    options.append((t, e[4], split(d)))
            frames[X] = e[3]
        elif k == 'warp':
            X = tuple(e[1]); op = e[2]
            sym = (1 if op > 0 else -1) * (abs(op) + 10 ** 6)
            rows[X] = {(r_, wd[1:] if wd and wd[0] == -sym else (sym,) + wd): q for (r_, wd), q in rows[X].items()}
            frames[X] = e[4]; snap(X)
        elif k == 'scalar':
            g, frame = e[1], e[2]; d_ = tuple(g[1])
            if g[0] == 'clear':
                rows[d_] = {}; frames[d_] = frame
            elif g[0] == 'copy':
                rows[d_] = dict(rows[tuple(g[2])])
            elif g[0] == 'add':
                add_into(rows[d_], rows[tuple(g[2])], Q(g[3], g[4]))
            elif g[0] == 'scale':
                rows[d_] = {kk: Q(g[2], g[3]) * v for kk, v in rows[d_].items()}
            snap(d_)
    require(dict(paid) == PAID, orient + ' paid profile of the #4610 word')
    return climbs, options


def norm(v):
    k = min(v); f = v[k]
    return tuple(sorted((i, q / f) for i, q in v.items()))


def optimum(climbs, options, trank, pw):
    keys, kid = [], {}
    for _, _, comp in climbs:
        for v in comp.values():
            n = norm(v)
            if n not in kid:
                kid[n] = len(keys); keys.append(n)
    E = Echelon()
    require(all(E.add(dict(k), i) for i, k in enumerate(keys)), 'distinct components are linearly independent over Q')
    need = [sorted({kid[norm(v)] for v in comp.values()}) for _, _, comp in climbs]
    cost = [pw(min(trank[h] for h, _ in k)) for k in keys]
    centres = collections.defaultdict(list)
    for t, r, comp in options:
        require(list(comp) == [()] and r == 8, 'centre options are word-free rank-8 rows')
        rest, combo = E.reduce(comp[()])
        require(not rest, 'every centre option lies in the span of the components')
        require(all(min(trank[h] for h in comp[()]) == 9 for _ in [0]), 'option rows are pure rank-9 (cold) forms')
        centres[t].append(sorted(combo))
    # connected pieces over components, joined by climbs and by the options of one centre
    par = list(range(len(keys)))

    def find(x):
        while par[x] != x:
            par[x] = par[par[x]]; x = par[x]
        return x

    def join(ids):
        for j in ids[1:]:
            par[find(j)] = find(ids[0])
    for ids in need:
        join(ids)
    for ol in centres.values():
        join(sorted({j for o in ol for j in o}))
    pieces = collections.defaultdict(list)
    for i in range(len(keys)):
        pieces[find(i)].append(i)
    total = D(0); best_sets = []; sizes = collections.Counter(); piece_data = {}
    for root, comps in pieces.items():
        sizes[len(comps)] += 1
        cl = [(pw(climbs[j][1]), set(need[j])) for j in range(len(climbs)) if find(need[j][0]) == root]
        ce = [[set(o) for o in ol] for ol in centres.values() if find(ol[0][0]) == root]
        piece_data[root] = (cl, ce)
        require(len(comps) <= 20, 'piece small enough for exact enumeration')
        best, arg = D(0), ()
        for k in range(1, len(comps) + 1):
            for S in itertools.combinations(comps, k):
                S_ = set(S)
                g = sum((w for w, nd in cl if nd <= S_), D(0)) - sum(cost[i] for i in S)
                g += sum(pw(8) for ol in ce if any(o <= S_ for o in ol))
                if g > best:
                    best, arg = g, S
        if arg:
            best_sets.append(sorted(arg))
        total += best

    def score(S):
        """Exact score of an arbitrary component set, summed piece by piece with the same formula."""
        S_ = set(S); g = D(0)
        for root, (cl, ce) in piece_data.items():
            Sp = {i for i in S_ if find(i) == root}
            if not Sp:
                continue
            g += sum((w for w, nd in cl if nd <= Sp), D(0)) - sum(cost[i] for i in Sp)
            g += sum(pw(8) for ol in ce if any(o <= Sp for o in ol))
        return g
    return dict(components=len(keys), climbs=len(climbs), options=len(options), centres=len(centres),
                piece_sizes=dict(sorted(sizes.items())), optimum=total, chosen=best_sets, keys=keys, score=score)


def build():
    pinned_inputs()
    word = json.loads(gzip.decompress(WORD.read_bytes()))
    c = word['canonical']; fr = c['frames']
    trank = {i: len(fr[c['final'][i]]) - len(fr[c['start'][i]]) for i in range(224, NL)}
    free = {i for i in range(224, NL) if c['start'][i] == 0}
    require(len(free) == 358 and collections.Counter(trank[i] for i in free) == {9: 326, 4: 26, 8: 6},
            '358 helpers start in the common input frame')
    t = 1 - C_SELECTED
    pw = lambda r: (t * D(r).ln()).exp()
    per_local = 8 * (pw(8) + 1 - pw(9))
    rel = json.loads(RELATIONS.read_text(encoding='utf-8'))
    V0 = [norm({int(k): Q(s) for k, s in row.items()}) for row in rel['rows']]
    out = {}
    for orient in ('backward', 'forward'):
        climbs, options = replay(word, orient, free)
        res = optimum(climbs, options, trank, pw)
        words = collections.Counter(len(comp) for _, _, comp in climbs)
        row = dict(helper_only_climbs=res['climbs'], climbs_by_word_count=dict(sorted(words.items())),
                   distinct_components=res['components'], components_independent=True,
                   centre_options=res['options'], centres_with_options=res['centres'],
                   piece_sizes=res['piece_sizes'], optimum_per_local=str(res['optimum'].quantize(D('1e-30'))))
        if orient == 'backward':
            require(abs(res['optimum'] - per_local) < D('1e-40'), 'backward optimum equals 8 (8^t + 1 - 9^t)')
            chosen = sorted(res['keys'][i] for s in res['chosen'] for i in s)
            span = Echelon()
            for i, k in enumerate(V0):
                require(span.add(dict(k), i), 'eight independent #5383 relations')
            require(len(chosen) == 8 and all(not span.reduce(dict(k))[0] for k in chosen),
                    'the span of the #5383 relations attains the optimum')
            row['optimum_attained_by'] = 'span of the eight #5383 relations (an optimum; not unique)'
            # Regression for the tie found in review (zxv): replace component 194 by 207.
            orig = sorted(i for s in res['chosen'] for i in s)
            require(orig == [56, 65, 66, 194, 200, 203, 205, 212], 'component numbering matches the reviewed head')
            tied = sorted([i for i in orig if i != 194] + [207])
            tE = Echelon()
            require(all(tE.add(dict(res['keys'][i]), i) for i in tied), 'tied set is independent (eight-dimensional)')
            require(span.reduce(dict(res['keys'][207]))[0], 'tied space differs from the #5383 span')
            require(abs(res['score'](tied) - res['score'](orig)) < D('1e-40')
                    and abs(res['score'](tied) - per_local) < D('1e-40'), 'tied space attains the same optimum')
            row['tied_optimum_regression'] = dict(original=orig, tied=tied, swapped='194 -> 207',
                                                  relation='h288 - h294 - h296 - h297 + h300 + h303 = 0')
        else:
            require(res['optimum'] == 0 and res['options'] == 0, 'forward: no centre option and optimum 0')
        out[orient] = row
    return dict(model='owned helper-relation subspaces over the 358 frame-0 helpers, any pivots, rows with warp words',
                C=str(C_SELECTED), V0_gain_per_backward_local=str(per_local.quantize(D('1e-30'))),
                frame0_helpers=358, frame0_target_ranks={'4': 26, '8': 6, '9': 326}, orientations=out,
                conclusion='No owned-relation subspace beats #5383; the 18 backward locals carry the maximum 144 exchanges.')


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--write', action='store_true'); args = ap.parse_args()
    result = build()
    path = HERE / 'RESULT-RELATIONS.json'
    text = json.dumps(result, indent=1, sort_keys=True) + '\n'
    if args.write:
        path.write_bytes(text.encode('utf-8'))
    require(path.exists() and json.loads(path.read_text(encoding='utf-8')) == json.loads(text), 'stored RESULT-RELATIONS.json equals the rebuild')
    print('PASS_OWNED_RELATION_EXACT_OPTIMUM_EQUALS_5383')


if __name__ == '__main__':
    main()
