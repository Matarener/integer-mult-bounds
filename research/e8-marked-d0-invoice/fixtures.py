"""Exact intrinsic and actual-decoder controls, prepared by conorholds.

Substantial OpenAI Codex assistance; Apache-2.0. These are finite controls,
not a search over all characteristic-zero coefficients. The geometric model
and rational elimination are supplied by authenticated, frozen PR3166 code.
"""

from fractions import Fraction
from itertools import combinations


class FixtureError(ValueError):
    pass


def need(condition, message):
    if not condition:
        raise FixtureError(message)


def scalar_multiple(left, right):
    pivot = next((i for i, value in enumerate(right) if value), None)
    if pivot is None:
        return None
    ratio = Fraction(left[pivot], right[pivot])
    return ratio if ratio and all(a == ratio * b for a, b in zip(left, right)) else None


def run(model, algebra):
    labels, roots, gram = model.labels, model.roots, model.gram
    p = [i for i in range(120) if model.p112_mask >> i & 1]
    pos = {root: i for i, root in enumerate(p)}
    frame = model.frame
    rank = algebra.binary_rank

    def unit(root):
        return tuple(Fraction(i == root) for i in p)

    def code(normal):
        return tuple(Fraction(model.inner(roots[i], normal)) for i in p)

    def evaluate(normal):
        return tuple(Fraction(sum(model.cartan[i][j] * normal[j] for j in range(8)))
                     for i in range(8))

    def weight(word):
        return rank(labels[i] for i, value in zip(p, word) if value)

    def contains(word, label):
        values = [labels[i] for i, value in zip(p, word) if value]
        return rank(values + [label]) == rank(values)

    def pair_cost(left, right):
        columns = [i for i, value in zip(p, right) if value]
        rows = [i for i, value in zip(p, left) if value]
        return rank(sum(((1 + gram[i][j]) % 2) << k for k, j in enumerate(columns))
                    for i in rows)

    def combine(words, coefficients):
        return tuple(sum(c * word[i] for c, word in zip(coefficients, words))
                     for i in range(112))

    def validate_factorization(rows, columns):
        for i, r in enumerate(p):
            for j, s in enumerate(p):
                need(sum(a[i] * b[j] for a, b in zip(rows, columns)) == Fraction(gram[r][s], 2),
                     "actual decoder factorization fails")

    def rejects(operation, message):
        try:
            operation()
        except FixtureError as error:
            need(message in str(error), "mutation rejected for an unexpected reason")
            return True
        raise FixtureError("mutation was accepted: " + message)

    def make(low, xi_low, normals):
        inverse = algebra.inverse([[normal[i] for normal in normals] for i in range(8)])
        high = []
        for normal in normals:
            coefficients = [sum(a * b for a, b in zip(xi, normal)) for xi in xi_low]
            correction = combine(low, coefficients)
            high.append(tuple(a - b for a, b in zip(code(normal), correction)))
        words = low + high
        xis = xi_low + inverse
        need(algebra.rational_rank(words) == len(words), "actual column family is not a basis")
        need(all(any(xi) for xi in xis), "zero restricted dual functional")
        # Check the complete coordinate identity, not the constructor's ledger.
        for coordinate in range(8):
            h = tuple(int(i == coordinate) for i in range(8))
            need(combine(words, [xi[coordinate] for xi in xis]) == code(h),
                 "actual dual/code identity fails")
        support = {i for word in low for i, value in zip(p, word) if value}
        need(algebra.rational_rank(low) == len(low), "low family is dependent")
        # Distance49 and the weight7 support cap36 prove S_{<=7}=T for
        # these small-support fixtures, uniformly in their coefficients.
        need(all(weight(word) <= 7 for word in low), "fixture low generator exceeds seven")
        need(49 - len(support) > 36, "fixture does not have the distance/cap d=0 certificate")
        # Additional exact root-support checks are useful consistency controls;
        # they are not substituted for the preceding uniform d=0 argument.
        for r in range(120):
            need(rank(labels[i] for i in p if i not in support and gram[r][i]) >= 8,
                 "fixture surviving root support loses rank eight")
        corrections = []
        for word, xi in zip(words, xis):
            matching = [i for i in frame if scalar_multiple(xi, evaluate(roots[i]))]
            corrections.append(bool(matching and contains(word, labels[matching[0]])))
        weights = list(map(weight, words))
        need(all(w in (8, 9) for w in weights[len(low):]), "high weight outside eight/nine")
        invoice = sum(weights) - sum(corrections)
        return {"words": words, "xis": xis, "weights": weights,
                "corrected": corrections, "invoice": invoice,
                "support": support, "low_count": len(low)}

    def marking(fixture, v, k, coefficients=None):
        need(scalar_multiple(fixture["xis"][k], evaluate(roots[v])) is not None,
             "marked functional is not the root functional")
        orthogonal = [j for j in p if j == v or not gram[v][j]]
        need(len(orthogonal) == 60, "O_v does not have size sixty")
        equations = [[word[pos[j]] for word in fixture["words"]] for j in orthogonal]
        coordinate = [Fraction(i == k) for i in range(len(fixture["words"]))]
        witness_exists = algebra.rational_rank(equations + [coordinate]) > algebra.rational_rank(equations)
        if coefficients is not None:
            word = combine(fixture["words"], coefficients)
            need(coefficients[k] != 0, "marked coefficient is zero")
            need(all(word[pos[j]] == 0 for j in orthogonal), "marked witness does not vanish on O_v")
            need(witness_exists, "explicit witness disagrees with rank criterion")
        epsilon = int(contains(fixture["words"][k], labels[v]))
        return witness_exists, epsilon

    def actual_decoder(fixture, v, k, coefficients, require_mark=True):
        if require_mark:
            exists, epsilon = marking(fixture, v, k, coefficients)
            need(exists, "actual decoder has no marked witness")
            need(coefficients[k] == scalar_multiple(fixture["xis"][k], evaluate(roots[v])),
                 "witness coefficient does not give a v-losing row")
        actual_rows, projected_rows = [], []
        for xi, coefficient in zip(fixture["xis"], coefficients):
            normal = tuple(sum(model.inverse[i][j] * xi[j] for j in range(8))
                           for i in range(8))
            projected = tuple(value / 2 for value in code(normal))
            projected_rows.append(projected)
            actual_rows.append(tuple(value - coefficient * delta
                                     for value, delta in zip(projected, unit(v))))
        g = combine(fixture["words"], coefficients)
        rows = [unit(v)] + actual_rows
        columns = [g] + fixture["words"]
        need(all(any(row) for row in rows), "actual zero row")
        need(all(any(column) for column in columns), "actual zero column")
        need(all(scalar_multiple(a, b) is None for a, b in combinations(rows, 2)),
             "actual parallel rows")
        need(all(scalar_multiple(a, b) is None for a, b in combinations(columns, 2)),
             "actual parallel columns")
        validate_factorization(rows, columns)
        mutation_index = 0 if k is None else k
        wrong_rows = list(rows)
        wrong_rows[mutation_index + 1] = tuple(
            2 * value - coefficients[mutation_index] * delta
            for value, delta in zip(projected_rows[mutation_index], unit(v)))
        rejected_half = rejects(lambda: validate_factorization(wrong_rows, columns),
                                "actual decoder factorization fails")
        projected_cost = sum(pair_cost(a, b) for a, b in zip(projected_rows, fixture["words"]))
        cost = sum(pair_cost(a, b) for a, b in zip(rows, columns))
        need(projected_cost == fixture["invoice"], "one-sided invoice identity fails")
        pivot_cost = pair_cost(unit(v), g)
        losing_roots = [i for i, (xi, row) in enumerate(zip(fixture["xis"], actual_rows))
                        if scalar_multiple(xi, evaluate(roots[v])) is not None
                        and row[pos[v]] == 0]
        need(len(losing_roots) <= 1, "multiple v-losing root rows")
        possible_rebate = int(bool(losing_roots) and contains(
            fixture["words"][losing_roots[0]], labels[v]))
        if require_mark:
            need(pivot_cost == 0 and losing_roots == [k], "marked free-pivot control differs")
            need(possible_rebate == epsilon, "actual and marked rebate differ")
        if losing_roots and pivot_cost == 0:
            marking(fixture, v, losing_roots[0], coefficients)
        need(projected_cost >= 64, "unmarked invoice floor fails")
        need(cost >= projected_cost - possible_rebate + pivot_cost >= 64,
             "singleton-pivot decoder floor fails")
        omitted_pivot_rejected = rejects(
            lambda: validate_factorization(rows[1:], columns[1:]),
            "actual decoder factorization fails")
        losses = [i for i, (a, b) in enumerate(zip(actual_rows, projected_rows))
                  if pair_cost(a, fixture["words"][i]) < pair_cost(b, fixture["words"][i])]
        need(set(losses) <= set(losing_roots), "non-root edit reduces binary cost")
        rank_p = algebra.rational_rank(rows)
        need(rank_p == 9, "actual row rank differs from nine")
        return {"terms": len(rows), "rank_P": rank_p, "rank_Q": len(fixture["words"]),
                "weights": fixture["weights"], "corrected": fixture["corrected"],
                "invoice": projected_cost, "epsilon": possible_rebate,
                "pivot_cost": pivot_cost, "v_losing_root_rows": losing_roots,
                "actual_cost": cost, "rebate_rows": losses,
                "entries_checked": 112 * 112,
                "omitted_pivot_rejected_by_entrywise_identity": omitted_pivot_rejected,
                "wrong_half_rejected_by_entrywise_identity": rejected_half}

    # Genuine full-hypotheses fixtures, including both values of epsilon.
    v = p[0]
    u = next(i for i in p if i != v and gram[v][i])
    w = next(i for i in p if i not in (u, v) and gram[v][i])
    z = next(i for i in p if i not in (u, v, w))
    reports = {}
    for epsilon in (0, 1):
        for t in (2, 3):
            low = [unit(u), unit(w)]
            xi_low = [evaluate(roots[v]), evaluate(roots[z])]
            if epsilon:
                low = [tuple(a + b for a, b in zip(unit(u), unit(v))), unit(v)]
            coefficients = [Fraction(1), Fraction(-1 if epsilon else 1)]
            if t == 3:
                extra = next(i for i in p if i not in (u, v, w, z))
                low.append(unit(extra))
                xi_low.append(evaluate(roots[w]))
                coefficients.append(Fraction(0))
            fixture = make(low, xi_low, [roots[i] for i in frame])
            coefficients += [Fraction(0)] * 8
            exists, observed = marking(fixture, v, 0, coefficients)
            need(exists and observed == epsilon, "positive marked fixture fails")
            reports[f"marked_t{t}_epsilon{epsilon}"] = actual_decoder(fixture, v, 0, coefficients)

    # A sharp *unmarked* I=64,epsilon=1 fixture: deleting g from the theorem
    # would make its conclusion false. It retains literal coefficients,
    # d=0, all nonzero duals and the raw basis shape.
    incidence = {r: {j for j, axis in enumerate(frame) if gram[r][axis]} for r in p}
    v = next(r for r in p if len(incidence[r]) == 4)
    private = sorted(incidence[v])[:3]
    remaining = sorted(set(range(8)) - set(private))
    selected = [next(r for r in p
                     if incidence[r].intersection(private) == {j} and gram[r][v] == 0)
                for j in private]
    normals = [roots[r] for r in selected] + [roots[frame[j]] for j in remaining]
    inverse = algebra.inverse([[normal[i] for normal in normals] for i in range(8)])
    xi_low = [tuple(2 * value for value in inverse[i]) for i in range(3)]
    sharp = make([unit(r) for r in selected], xi_low, normals)
    marked_high = next(i for i in range(3, 11)
                       if scalar_multiple(sharp["xis"][i], evaluate(roots[v])))
    exists, epsilon = marking(sharp, v, marked_high)
    need(sharp["invoice"] == 64 and epsilon == 1 and not exists,
         "omitted-witness counterexample is not sharp")
    reports["omitting_g_is_false"] = {"invoice": 64, "epsilon": 1,
                                       "without_g_invoice_minus_epsilon": 63,
                                       "marked_witness_exists": False,
                                       "private_indices": private,
                                       "root_indices": selected, "pivot_index": v}
    paid_coefficients = [Fraction(1)] * 3 + [Fraction(0)] * 8
    paid_coefficients[marked_high] = scalar_multiple(sharp["xis"][marked_high], evaluate(roots[v]))
    paid = actual_decoder(sharp, v, None, paid_coefficients, require_mark=False)
    need(paid["invoice"] == paid["actual_cost"] == 64 and paid["pivot_cost"] == 1
         and paid["epsilon"] == 1 and paid["rebate_rows"] == [marked_high],
         "paid singleton pivot does not pay the sharp rebate")
    paid["actual_nonpivot_cost"] = paid["actual_cost"] - paid["pivot_cost"]
    reports["paid_pivot_sharp"] = paid
    # A sharp full-hypotheses family. Reflect each private root in its own
    # matched frame: low duals are genuine root functionals, while high
    # supports merely change nonzero signs. This also avoids actual parallel
    # rows/columns and keeps the free pivot nonzero.
    for t in (2, 3):
        private = tuple(range(t))
        candidates = [[r for r in p if incidence[r].intersection(private) == {j}]
                      for j in private]
        first = candidates[0][0]
        second = next(r for r in candidates[1] if gram[first][r])
        selected = [first, second] + ([candidates[2][0]] if t == 3 else [])
        reflected, gammas = [], []
        for r, j in zip(selected, private):
            axis = frame[j]
            image = tuple(a - gram[r][axis] * b for a, b in zip(roots[r], roots[axis]))
            image = next(i for i in range(120) if scalar_multiple(roots[i], image))
            reflected.append(image)
            gammas.append(Fraction(2, gram[r][image]))
        normals = [roots[r] for r in selected] + [roots[frame[j]] for j in range(8) if j not in private]
        low_xis = [tuple(gamma * value for value in evaluate(roots[r]))
                   for gamma, r in zip(gammas, reflected)]
        sharp = make([unit(r) for r in selected], low_xis, normals)
        coefficients = [gammas[0], gammas[1]] + [Fraction(0)] * (t + 6)
        report = actual_decoder(sharp, reflected[0], 0, coefficients)
        need(report["invoice"] == report["actual_cost"] == 64 and report["epsilon"] == 0,
             "sharp marked decoder does not attain sixty-four")
        report.update(private_axes=list(private),
                      root_normals_doubled=[model.to_doubled(roots[r]) for r in selected],
                      reflected_mark_roots_doubled=[model.to_doubled(roots[r]) for r in reflected],
                      gammas=[str(gamma) for gamma in gammas])
        reports[f"sharp_marked_t{t}"] = report
        free_coefficients = [coefficient / 3 for coefficient in coefficients]
        free = actual_decoder(sharp, reflected[0], None, free_coefficients, require_mark=False)
        need(free["pivot_cost"] == 0 and not free["v_losing_root_rows"]
             and free["actual_cost"] == 64, "free no-loss branch fails")
        reports[f"free_no_losing_row_t{t}"] = free
        paid_coefficients = [sum(a * b for a, b in zip(xi, roots[reflected[0]])) / 4
                             for xi in sharp["xis"]]
        paid = actual_decoder(sharp, reflected[0], None, paid_coefficients, require_mark=False)
        need(paid["pivot_cost"] == 1 and not paid["v_losing_root_rows"]
             and paid["actual_cost"] == 65, "paid no-loss branch fails")
        reports[f"paid_no_losing_row_t{t}"] = paid
    # Positive intrinsic control with coincident corrected LOW frame indices.
    # This is not an actual-normalized-decoder fixture: it tests the broader
    # basis/dual packet, whose proof must not silently impose distinct lows.
    label_index = {label: i for i, label in enumerate(labels)}
    triples = []
    for a, b in combinations(p, 2):
        c = label_index.get(labels[a] ^ labels[b] ^ labels[frame[0]])
        if c in pos and c > b:
            triples.append((a, b, c))
    first = triples[0]
    second = next(triple for triple in triples if not set(first).intersection(triple))
    used = set(first + second)
    u = next(r for r in p if r not in used)
    v = next(r for r in p if r != u and gram[r][u])
    carriers = [tuple(Fraction(r in triple) for r in p) for triple in (first, second)]
    repeated = make(carriers + [unit(u)],
                    [evaluate(roots[frame[0]]), evaluate(roots[frame[0]]), evaluate(roots[v])],
                    [roots[i] for i in frame])
    witness = [Fraction(0), Fraction(0), Fraction(1)] + [Fraction(0)] * 8
    exists, epsilon = marking(repeated, v, 2, witness)
    need(repeated["corrected"][:3] == [True, True, False] and exists and epsilon == 0,
         "coincident corrected low-frame positive control fails")
    need(repeated["invoice"] == 69, "coincident-low control invoice differs")
    reports["repeated_low_frame_intrinsic"] = {
        "actual_low_weights": repeated["weights"][:3], "corrected_low_indices": [0, 1],
        "same_frame_index": 0, "literal_marked_witness": True, "epsilon": epsilon,
        "invoice": repeated["invoice"], "scope": "intrinsic basis/dual packet only"}
    reports["controls"] = {"wrong_factor_half_rejected": all(
                                report["wrong_half_rejected_by_entrywise_identity"]
                                for report in reports.values() if "entries_checked" in report),
                            "dropped_marked_witness_has_counterexample": True,
                            "actual_decoders_checked": sum("entries_checked" in report
                                                           for report in reports.values()),
                            "paid_pivot_cost_is_necessary_at_equality": True}
    return reports
