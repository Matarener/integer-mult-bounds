"""Exact nonempty d=1 invoice/actual-consumer controls.

conorholds, with substantial OpenAI Codex assistance. Apache-2.0.
The finite support strata certify the low space using the written <70
root-direction rigidity argument; they do not enumerate arbitrary fields.
"""

from fractions import Fraction


def run(model):
    g = model.Geometry()
    live = list(model.indices(g.live))
    position = {root: i for i, root in enumerate(live)}
    frame = list(model.indices(g.frame))
    f0, w0 = frame[:2]
    model.need(g.dots[f0][w0] == 0, "actual control frame pair changed")
    xmask = g.neighbors[f0] & ~g.neighbors[w0] & g.live
    cmask = g.neighbors[f0] & g.neighbors[w0] & g.live
    model.need(xmask.bit_count() == 32 and cmask.bit_count() == 24,
               "actual control quarter sizes")

    def word(normal):
        return [Fraction(g.dots[normal][root], 4) for root in live]

    def unit(root):
        return [Fraction(root == site) for site in live]

    def support(values):
        return [g.labels[root] for root, value in zip(live, values) if value]

    def weight(values):
        return model.rank(support(values))

    def independent_rows(rows):
        basis = {}
        for value in rows:
            while value:
                pivot = value.bit_length() - 1
                if pivot in basis:
                    value ^= basis[pivot]
                else:
                    basis[pivot] = value
                    break
        return list(basis.values())

    def term_cost(left, right):
        rb = independent_rows(support(left))
        cb = independent_rows(support(right))
        matrix = [sum((((a & 1) * (b & 1)) ^ g.b(a >> 1, b >> 1)) << j
                      for j, b in enumerate(cb)) for a in rb]
        return model.rank(matrix)

    def nonparallel(rows):
        keys = []
        for row in rows:
            first = next((value for value in row if value), None)
            if first is None:
                return False
            keys.append(tuple(value / first for value in row))
        return len(keys) == len(set(keys))

    cf0 = word(f0)
    gx = [value if xmask >> root & 1 else Fraction(0)
          for root, value in zip(live, cf0)]
    bc = [value if cmask >> root & 1 else Fraction(0)
          for root, value in zip(live, cf0)]
    candidates = [root for root in model.indices(xmask) if g.dots[f0][root] == 4]
    model.need(len(candidates) >= 2, "actual control lacks positive unit sites")
    code = [word(normal) for normal in frame]
    outside = [[Fraction(value, 2) for value in g.roots[root]]
               for root in live if not (g.neighbors[f0] >> root & 1)]
    model.need(model.rational_rank(outside) == 7, "actual control code intersection")
    results = []

    for t in (2, 3):
        units = candidates[:t - 1]
        uu = [unit(root) for root in units]
        bx = [value - sum(u[i] for u in uu) for i, value in enumerate(gx)]
        high = []
        high_normals = [normal for normal in frame if normal != f0]
        for normal in high_normals:
            original = word(normal)
            high.append([value - sum(Fraction(g.dots[root][normal], 4) * u[i]
                                     for root, u in zip(units, uu))
                         for i, value in enumerate(original)])
        columns = [bx, bc] + uu + high
        low = [bx, bc] + uu
        expected_weights = [7, 7] + [1] * (t - 1) + [8] * 7
        weights = [weight(q) for q in columns]
        model.need(weights == expected_weights, "actual d1 basis weights changed")
        model.need(model.rational_rank(columns) == 8 + t,
                   "actual d1 columns are not a basis")
        model.need(model.rational_rank(low) == t + 1
                   and model.rational_rank(code + low) == 8 + t,
                   "actual d1 low/code intersection rank")

        # Restricted duals are x_bX=x_bC=f0/2, x_unit=u, x_high=fi/2.
        # Store their root index and scalar, preserving the literal normalization.
        duals = [(f0, Fraction(1, 2)), (f0, Fraction(1, 2))]
        duals += [(root, Fraction(1)) for root in units]
        duals += [(root, Fraction(1, 2)) for root in high_normals]
        for axis in frame:
            coefficients = [scale * Fraction(g.dots[root][axis], 4)
                            for root, scale in duals]
            target = word(axis)
            model.need(all(sum(coefficient * q[i] for coefficient, q
                               in zip(coefficients, columns)) == value
                           for i, value in enumerate(target)),
                       "actual d1 restricted dual expansion")
        corrections = []
        for j, ((normal, _), q) in enumerate(zip(duals, columns)):
            if normal in frame:
                carried = model.rank(support(q) + [g.labels[normal]]) == weight(q)
                if carried:
                    corrections.append(j)
        model.need(not corrections, "actual d1 control unexpectedly corrected")
        invoice = sum(weights)

        # Every low word is Ch + alpha*gx + unit edits. Its support cap36
        # forces |Off(h)|<=36+32=68<70, hence h=0 or a root/frame direction.
        # At nonunit X sites the only support-changing alpha ratios are
        # 0,+/-1,+/-2. Alpha=3 represents every other characteristic-zero
        # ratio. At each unit site both zero/nonzero support states are tested.
        qualifying = []
        for normal in range(120):
            base = word(normal)
            for alpha in (-2, -1, 0, 1, 2, 3):
                for state in range(1 << len(units)):
                    q = [value + alpha * edit for value, edit in zip(base, gx)]
                    for j, root in enumerate(units):
                        q[position[root]] = Fraction((state >> j) & 1)
                    if weight(q) <= 7:
                        model.need(normal == f0,
                                   "actual d1 low-space certification found another normal")
                        qualifying.append((normal, alpha, state))
        model.need(qualifying, "actual d1 low-space certification is vacuous")
        # h=0 words are supported in X, whose label rank is seven; h=f0
        # words lie in span(Cf0,gx,units)=T. Thus these complete support
        # strata prove S_(<=7)=T, not merely that selected lows lie in T.
        model.need(model.rank(g.labels[root] for root in model.indices(xmask)) == 7,
                   "actual d1 zero-normal low space")

        pivot = units[0]
        pivot_unit = uu[0]
        eta = [1, 0] + [1] * len(units) + [0] * 7
        model.need(all(sum(coefficient * q[i] for coefficient, q in zip(eta, columns))
                       == value for i, value in enumerate(gx)), "actual d1 pivot word")
        left = []
        for (normal, scale), coefficient in zip(duals, eta):
            original = word(normal)
            left.append([scale * value / 2 - coefficient * pivot_unit[i]
                         for i, value in enumerate(original)])
        all_left, all_right = [pivot_unit] + left, [gx] + columns
        model.need(model.rational_rank(all_left) == 9
                   and model.rational_rank(all_right) == 8 + t,
                   "actual d1 consumer ranks")
        model.need(nonparallel(all_left) and nonparallel(all_right),
                   "actual d1 consumer zero/parallel factors")
        for i, root_i in enumerate(live):
            for j, root_j in enumerate(live):
                actual = sum(p[i] * q[j] for p, q in zip(all_left, all_right))
                model.need(actual == Fraction(g.dots[root_i][root_j], 8),
                           "actual d1 consumer is not the exact Gram factorization")
        costs = [term_cost(p, q) for p, q in zip(all_left, all_right)]
        expected_costs = [1, 7, 7] + [0] + [1] * (len(units) - 1) + [8] * 7
        model.need(costs == expected_costs and sum(costs) == invoice,
                   "actual d1 consumer term costs")
        losing = [j for j, ((normal, scale), p) in enumerate(zip(duals, left))
                  if scale * Fraction(g.dots[normal][pivot], 8) != 0
                  and p[position[pivot]] == 0]
        model.need(losing == [2], "actual d1 consumer losing root row")
        results.append({"t": t, "basis_weights": weights, "n_c": 0,
                        "invoice": invoice, "low_space_dimension": t + 1,
                        "code_intersection_dimension": 1,
                        "low_root_strata": 120 * 6 * (1 << len(units)),
                        "low_qualifying_digest": model.digest(qualifying),
                        "rank_P": 9, "rank_Q": 8 + t,
                        "factor_nonparallel": True, "exact_Gram_entries": 112 * 112,
                        "pivot_cost": costs[0], "losing_indices": losing,
                        "term_costs": costs, "actual_cost": sum(costs),
                        "unit_roots": units})
    return {"scope": "nonempty-actual-d1-consumer-controls-not-sharpness",
            "root_direction_rigidity_premise": "support-at-most68-is-below70",
            "cases": results}
