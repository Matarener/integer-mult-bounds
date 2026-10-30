"""Nonempty marked actual-d2 controls, with complete low-space certificates.

conorholds, substantial OpenAI Codex assistance. Apache-2.0.
The modulo-three minors certify characteristic-zero ranks; payloads and
the Gram factorization are checked over the rationals. These examples lie
above the invoice floor and do not replace its written proof.
"""

from fractions import Fraction


def rank_mod3(rows):
    basis = {}
    for original in rows:
        row = list(original)
        for j in range(6):
            if not row[j]:
                continue
            if j in basis:
                factor = row[j]
                row = [(x - factor*y) % 3 for x, y in zip(row, basis[j])]
            else:
                factor = row[j]  # Both nonzero elements of F3 are self-inverse.
                basis[j] = [(factor*x) % 3 for x in row]
                break
        if len(basis) == 6:
            return 6
    return len(basis)


def run(model):
    g = model.Geometry()
    live, frame = list(model.indices(g.live)), list(model.indices(g.frame))
    a, b = frame[:2]
    axes = frame[2:]
    parts = [g.neighbors[a] & ~g.neighbors[b] & g.live,
             g.neighbors[b] & ~g.neighbors[a] & g.live,
             sum(1 << s for s in live if g.dots[a][s]*g.dots[b][s] > 0),
             sum(1 << s for s in live if g.dots[a][s]*g.dots[b][s] < 0)]
    model.need([p.bit_count() for p in parts] == [32, 32, 12, 12], "d2 piece partition")
    root = next(s for s in live if not (g.neighbors[a] | g.neighbors[b]) >> s & 1)
    active = [f for f in axes if g.dots[root][f]]
    model.need(len(active) == 4, "d2 marked root outside plane")
    selected = active[0]
    epsilon = Fraction(g.dots[root][selected], 4)
    pivot = next(s for s in model.indices(parts[0]) if g.dots[a][s] == 4)
    pivot_pos = live.index(pivot)

    def word(f):
        return [Fraction(g.dots[f][s], 4) for s in live]

    def normal(f, scale=Fraction(1)):
        return [scale*Fraction(x, 2) for x in g.roots[f]]

    def support(q):
        return [g.labels[s] for s, value in zip(live, q) if value]

    def weight(q):
        return model.rank(support(q))

    def nonparallel(rows):
        normalized = []
        for row in rows:
            lead = next((x for x in row if x), None)
            if lead is None:
                return False
            normalized.append(tuple(x/lead for x in row))
        return len(normalized) == len(set(normalized))

    def term_cost(p, q):
        def basis(labels):
            result = []
            for label in labels:
                if model.rank(result + [label]) > len(result):
                    result.append(label)
            return result
        left, right = basis(support(p)), basis(support(q))
        return model.rank(sum((((x & 1)*(y & 1)) ^ g.b(x >> 1, y >> 1)) << j
                              for j, y in enumerate(right)) for x in left)

    code = [word(f) for f in frame]
    raw = {s: tuple((g.dots[f][s]//4) % 3 for f in axes) for s in live}
    results = []
    for t in (2, 3):
        masks = parts.copy()
        if t == 3:
            masks[0] ^= 1 << pivot
            masks.append(1 << pivot)
        ids = [list(model.indices(mask)) for mask in masks]
        low = [[Fraction(g.dots[b if j == 1 else a][s], 4) if mask >> s & 1 else Fraction(0)
                for s in live] for j, mask in enumerate(masks)]
        high = [word(f) for f in axes]
        if t == 3:
            for row in high:
                row[pivot_pos] = Fraction(0)
        chosen = axes.index(selected)
        for j, f in enumerate(axes):
            if j != chosen:
                scalar = Fraction(g.dots[root][f], 4) / epsilon
                high[j] = [x - scalar*y for x, y in zip(high[j], high[chosen])]
        columns = low + high
        normals = [normal(a, Fraction(1, 2)), normal(b, Fraction(1, 2)),
                   [(x+y)/2 for x, y in zip(normal(a), normal(b))],
                   [(x-y)/2 for x, y in zip(normal(a), normal(b))]]
        if t == 3:
            normals.append(normal(pivot))
        normals += [normal(root, 1/epsilon) if f == selected else normal(f, Fraction(1, 2))
                    for f in axes]
        model.need(model.rational_rank(low) == t+2
                   and model.rational_rank(columns) == 8+t
                   and model.rational_rank(code+low) == 8+t, "actual d2 ranks/intersection")
        model.need(all(any(x for x in row) for row in normals), "actual d2 zero restricted dual")
        for f in frame:
            coefficients = [sum(x*y for x, y in zip(row, normal(f))) for row in normals]
            model.need(all(sum(c*q[i] for c, q in zip(coefficients, columns)) == value
                           for i, value in enumerate(word(f))), "actual d2 restricted dual expansion")

        # Certify S_(<=7)=T. Every support-rank<=7 word lies in an affine-six
        # label flat. Eliminate the disjoint T coordinates outside each flat.
        # Full rank six of the remaining C/T evaluation matrix modulo3 gives
        # a nonzero integer minor, and thus the same full rank in every char0 field.
        used = 0
        for mask in masks:
            used |= mask
        outside = list(model.indices(g.live ^ used))
        normalized = [{s: tuple((x*(g.dots[b if j == 1 else a][s]//4)) % 3 for x in raw[s])
                       for s in part} for j, part in enumerate(ids)]
        differences = [{(u, v): tuple((x-y) % 3 for x, y in zip(vectors[u], vectors[v]))
                        for u in vectors for v in vectors} for vectors in normalized]
        flat_count = 0
        for _, _, flat in g.affine_sections():
            def residuals():
                for s in outside:
                    if not flat >> s & 1:
                        yield raw[s]
                for part, delta in zip(ids, differences):
                    complement = [s for s in part if not flat >> s & 1]
                    if complement:
                        anchor = complement[0]
                        for s in complement[1:]:
                            yield delta[s, anchor]
            model.need(rank_mod3(residuals()) == 6, "actual d2 low-space minor rank")
            flat_count += 1
        model.need(flat_count == 43180, "actual d2 low-space flat coverage")

        weights, corrected = [weight(q) for q in columns], []
        for j, (q, row) in enumerate(zip(columns, normals)):
            for f in frame:
                fr = normal(f)
                first = next(k for k, x in enumerate(fr) if x)
                scalar = row[first]/fr[first]
                if scalar and row == [scalar*x for x in fr]:
                    if model.rank(support(q)+[g.labels[f]]) == weights[j]:
                        corrected.append(j)
        model.need(len(corrected) == 3 and weights.count(9) == 3
                   and all(weights[j] == 9 for j in corrected),
                   "actual d2 corrected weight-nine controls")
        model.need(normals[len(low)+chosen] == normal(root, 1/epsilon), "actual d2 live-root mark")

        eu = [Fraction(s == pivot) for s in live]
        eta = [Fraction(j in (0, 2) or (t == 3 and j == 4)) for j in range(len(columns))]
        qp = [sum(c*q[i] for c, q in zip(eta, columns)) for i in range(112)]
        dual_words = [[sum(x*y for x, y in zip(row, normal(s))) for s in live] for row in normals]
        left = [[x/2-c*eu[i] for i, x in enumerate(row)] for c, row in zip(eta, dual_words)]
        all_left, all_right = [eu]+left, [qp]+columns
        model.need(model.rational_rank(all_left) == 9 and model.rational_rank(all_right) == 8+t,
                   "actual d2 consumer ranks")
        model.need(nonparallel(all_left) and nonparallel(all_right), "actual d2 parallel factor")
        for i, ri in enumerate(live):
            for j, rj in enumerate(live):
                model.need(sum(p[i]*q[j] for p, q in zip(all_left, all_right))
                           == Fraction(g.dots[ri][rj], 8), "actual d2 Gram factorization")
        costs = [term_cost(p, q) for p, q in zip(all_left, all_right)]
        model.need(sum(costs) >= 64, "actual d2 control consumer floor")
        results.append({"t": t, "d": 2, "dimension_T": t+2, "weights": weights,
                        "n_c": len(corrected), "corrected_weight9": len(corrected),
                        "invoice": sum(weights)-len(corrected), "low_space_flats": flat_count,
                        "quotient_minor_rank_mod3": 6, "rank_P": 9, "rank_Q": 8+t,
                        "nonparallel_factors": True, "exact_Gram_entries": 12544,
                        "term_costs": costs, "actual_cost": sum(costs)})
    return {"scope": "nonempty-marked-actual-d2-controls-not-sharpness", "cases": results}
