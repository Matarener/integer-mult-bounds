"""Check the source-bound return floor, approximation examples and invoice.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
The general proof is in REPAIR.md. This is not a proof kernel.
"""
import argparse
import contextlib
from fractions import Fraction as Q
import io
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
import source
import bounds
import census
import certify as exact
import verify_application
sys.path.insert(0, str(HERE.parent / "passive-saved-query-ceiling"))
import portable
sys.path.insert(0, str(ROOT / "scripts"))
import compare_recursive_invoices as invoices

G, need = exact.G, census.require


def source_contract():
    application = verify_application.run()
    with portable.private_stage() as (stage, requests, _work):
        loader = portable.Loader(stage, requests)
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            bank = loader.run(loader.author / "bank_span.py")
        need(stream.getvalue().encode() == (loader.author / "BANK-SPAN.json").read_bytes(),
             "Exact bank source replay")
        a = bank["a"]
        target = a.mul(bank["d"], bank["qi"])
        need(bank["targetrows"][0] == [target, {}, {}, {}], "Original first target bank")
        mixed = bank["env"]
        need(mixed["standard"][0] == [target, {}, {}, {}], "Original mixed target bank")
        gate = json.loads((loader.author / "GRADE-GATE.json").read_text())
        ports = gate["actual_source_zero_diagonal_ports"]
        need(len(set(ports)) == 104 and ports == sorted(ports), "104 distinct source ports")
        independent = json.loads((stage / "INDEPENDENT.json").read_text())
        need(independent["earlier_grades"] == [0, 1] and independent["target_grade"] == 9,
             "Disjoint initial and target grades")
        need(independent["post_FULL_unselected_grade_census"] == {"7": 5408},
             "Complete late source grades")
        need(independent["ownership"]["independent_native_helpers"] == 816,
             "Independent helper inputs")
        paid, targets = dict(mixed["P"]), dict(mixed["Tar"])
        selected = json.loads((ROOT / "certificates/selected-result.json").read_text())
        saving = Q(selected["kappa"])
        low_t, high_t = mixed["iv"].moment(targets, 1-saving)
        low_p, high_p = mixed["iv"].moment(paid, 1-saving)
        margin = low_t-high_p, high_t-low_p
        need(Q(36) < margin[0] <= margin[1] < Q(37), "Exact reference-tariff budget")
        budget = {"reference_saving": str(saving), "tariff_exponent": str(1-saving),
                  "source": "Pinned selected value used only as a reference tariff",
                  "margin_interval": list(map(str, margin)),
                  "margin_decimal_enclosure": mixed["iv"].display(margin),
                  "max_rank_one_returns_with_positive_margin": 36}
    return application, ports, paid, targets, budget


def invoice(paid, targets):
    return {"schema": invoices.SCHEMA,
            "contract": {"model": "PR4948 frozen mixed word with extra same-capacity paid returns",
                         "rank_semantics": "One positive-rank recursive job returns one field",
                         "ambient_rank": 17,
                         "boundary": "Original 448 main targets and 816 autonomous helper credits; unchanged frozen paid inputs"},
            "paid": {str(k): v for k, v in sorted(paid.items())},
            "targets": {str(k): v for k, v in sorted(targets.items())}}


def cost_certificate(paid, targets, count):
    paid = dict(paid)
    paid[1] = paid.get(1, 0) + count
    actual = invoice(paid, targets)
    result = invoices.compare_invoices(invoice({}, {}), actual)
    direct = [{"rank": k, "value": sum(v*min(r, k) for r, v in paid.items())
               - sum(v*min(r, k) for r, v in targets.items())}
              for k in [0]+sorted(set(paid) | set(targets))]
    need(result["hinges"] == direct, "Independent direct hinge calculation")
    return actual, result


def small_group():
    matrices = []
    for state in census.clifford_choi(1):
        denominator = G("1+i") if sum(bool(x) for x in state[:2]) == 2 else G(1)
        matrices.append(tuple(tuple(G.pair(*map(Q, census.UNITS[state[i+2*j]]))/denominator
                                    for j in range(2)) for i in range(2)))

    def projective(matrix):
        first = next(z for row in matrix for z in row if z)
        return exact.key(tuple(tuple(z/first for z in row) for row in matrix))

    index = {projective(a): j for j, a in enumerate(matrices)}
    need(len(index) == 24, "Complete one-axis projective group")
    products = {}
    for i, a in enumerate(matrices):
        need(exact.multiply(exact.adjoint(a), a) == exact.identity(2), "Unitary representative")
        for j, b in enumerate(matrices):
            product = exact.multiply(a, b)
            k = index[projective(product)]
            phase = next(product[x][y]/matrices[k][x][y] for x in range(2)
                         for y in range(2) if matrices[k][x][y])
            need(phase in [G(1), G(-1), G("i"), G("-i")], "Exact central phase")
            need(product == tuple(tuple(phase*z for z in row) for row in matrices[k]),
                 "Literal product including phase")
            products[i, j] = k, phase
    ordinary = [i for i, a in enumerate(matrices) if sum(bool(z) for row in a for z in row) == 2]
    identity = index[projective(exact.identity(2))]
    target = next(i for i in range(24) if i not in ordinary)
    need(len(ordinary) == 8, "Complete one-axis monomial subgroup")
    need(all(products[i, j][0] in ordinary for i in ordinary for j in ordinary),
         "Ordinary group closure")
    return matrices, products, ordinary, identity, target


def add(x, y, scale=G(1)):
    result = dict(x)
    for k, value in y.items():
        result[k] = result.get(k, G(0)) + scale*value
        if not result[k]:
            del result[k]
    return result


def basis(rows):
    pivots = {}
    for row in rows:
        row = dict(row)
        while row:
            k = min(row)
            if k in pivots:
                row = add(row, pivots[k], -row[k])
            else:
                pivots[k] = {j: v/row[k] for j, v in row.items()}
                break
    return list(pivots.values())


def action(g, row, products, width):
    result = {}
    for (column, word), value in row.items():
        new_word, phase = products[g, word]
        result[column, new_word] = value*exact.power(phase, width)
    return result


def orbit(rows, ordinary, products, width):
    return [action(g, row, products, width) for row in rows for g in ordinary]


def gram(matrices, width):
    return [[exact.power(sum((exact.conjugate(a[i][j])*b[i][j]
                              for i in range(2) for j in range(2)), G(0))/2, width)
             for b in matrices] for a in matrices]


def inner(x, y, kernel):
    return sum((exact.conjugate(a)*b*kernel[i][j]
                for (c, i), a in x.items() for (d, j), b in y.items() if c == d), G(0))


def projection_error(history, targets, kernel):
    """Eliminate the history block from the physical Gram matrix."""
    rows = basis(history) + targets
    size = len(rows)-len(targets)
    matrix = [[inner(x, y, kernel) for y in rows] for x in rows]
    for k in range(size):
        pivot = matrix[k][k]
        need(pivot.imag == 0 and pivot.real > 0, "Physical history Gram pivot")
        for i in range(k+1, len(rows)):
            for j in range(k+1, len(rows)):
                matrix[i][j] -= matrix[i][k]*matrix[k][j]/pivot
    result = sum((matrix[k][k] for k in range(size, len(rows))), G(0))
    need(result.imag == 0 and result.real >= 0, "Physical least-squares error")
    return result.real


def finite_checks():
    matrices, products, ordinary, identity, target = small_group()
    sources = [{(j, identity): G(1)} for j in range(3)]
    targets = [{(j, target): G(1)} for j in range(3)]
    counts = {"group_products": len(products), "phase_covariances": 0,
              "history_prefixes": 0, "physical_approximation_cases": 0}
    errors = []
    for width in range(8, 12):
        kernel = gram(matrices, width)
        for h in ordinary:
            for i in range(24):
                for j in range(24):
                    image_i = action(h, {(0, i): G(1)}, products, width)
                    image_j = action(h, {(0, j): G(1)}, products, width)
                    need(inner(image_i, image_j, kernel) == kernel[i][j], "Tensor phase covariance")
                    counts["phase_covariances"] += 1
        initial = orbit(sources, ordinary, products, width)
        desired = orbit(targets, ordinary, products, width)
        need(len(basis(initial)) == 24 and len(basis(initial+desired)) == 48,
             "Full target quotient dimension")
        for cached in range(4):
            old = initial+desired[:8*cached]
            need(len(basis(old+desired))-len(basis(old)) == 8*(3-cached),
                 "Correctly cached targets remove charges")
        stale = initial+orbit([{(3, target): G(1)}], ordinary, products, width)
        need(len(basis(stale+desired))-len(basis(stale)) == 24, "Wrong input version gives no credit")
        for mode in ("direct", "mixed", "feedback"):
            history, previous = list(initial), {}
            for q in range(4):
                dim = len(basis(history))
                need(dim <= 24+8*q, "One return adds at most one ordinary module")
                if q < 3:
                    need(len(basis(history+desired)) > dim, "Too few returns cannot complete targets")
                if mode == "direct" and q == 3:
                    need(len(basis(history+desired)) == dim, "Direct oracle attains isolated count")
                counts["history_prefixes"] += 1
                if mode == "mixed" and q < 3:
                    error = projection_error(history, targets, kernel)
                    need(error >= bounds.pointwise_bound(1, width, clifford=True)*(3-q),
                         "Projected-frame approximation bound")
                    errors.append({"width": width, "returns": q, "squared_error": str(error)})
                    counts["physical_approximation_cases"] += 1
                if q == 3:
                    continue
                if mode == "direct":
                    new = targets[q]
                elif mode == "mixed":
                    new = {}
                    for j, row in enumerate(targets):
                        new = add(new, row, G((j+1)**q))
                else:
                    new = add(targets[q], action(target, previous, products, width))
                    new = add(new, sources[(q+1) % 3], G("i"))
                previous = new
                history += orbit([new], ordinary, products, width)

    # Two singular target rows need only one paid return. Row count alone fails.
    width = 8
    z_matrix = ((G(1), G(0)), (G(0), G(-1)))
    z = next(i for i, a in enumerate(matrices) if a == z_matrix)
    positive = add({(0, identity): G(Q(1, 2))}, {(0, z): G(Q(1, 2))})
    negative = add({(1, identity): G(Q(1, 2))}, {(1, z): G(-Q(1, 2))})
    one_return = orbit([add(positive, negative)], ordinary, products, width)
    singular = orbit([positive, negative], ordinary, products, width)
    need(len(basis(one_return)) == len(basis(one_return+singular)) == 8,
         "Complementary idempotents share one return")
    need(len(basis(orbit([positive], ordinary, products, width))) == 4,
         "A singular target need not generate the full algebra")

    # At width one, monomial matrices span every two-by-two matrix.
    literal = [{(0, k): z for k, z in enumerate(sum((list(row) for row in a), [])) if z}
               for a in matrices]
    low = [literal[i] for i in ordinary]
    need(len(basis(low)) == len(basis(low+[literal[target]])) == 4,
         "Width-one physical counterexample to formal independence")
    counts["controls"] = ["cached targets", "wrong input version", "complementary idempotents",
                          "small-width physical dependence", "arbitrary feedback rows"]
    return counts, errors


def run(write=False):
    application, ports, paid, targets, budget = source_contract()
    actual, cost = cost_certificate(paid, targets, len(ports))
    need([row["value"] for row in cost["hinges"]] ==
         [0, 5996, 7134, 7448, 6742, 5838, 3870, 2900, 1800, 8], "Complete repair invoice hinges")
    need(cost["classification"] == "uniformly_worse", "All concave tariffs are adverse")
    need(sum(k*v for k, v in targets.items())-sum(k*v for k, v in paid.items()) == 96,
         "Original rank-mass allowance")
    for q in (0, 95, 96, 97, 103, 104):
        _, control = cost_certificate(paid, targets, q)
        need(control["hinges"][-1]["value"] == q-96, "Rank-mass price threshold")
        if q < 96:
            need(control["classification"] == "inconclusive", "Missing repair charge is not uniform failure")
        else:
            need(control["classification"] == "uniformly_worse", "No positive margin with 96 returns")
    missing = len(ports)-budget["max_rank_one_returns_with_positive_margin"]
    budget["operator_error_squared_from_width_72"] = str(Q(missing, 9*len(ports)))
    budget["operator_error_squared_from_width_84"] = str(Q(125*missing, 126*len(ports)))
    counts, errors = finite_checks()
    result = {"status": "PASS_104_RETURN_FLOOR_ERROR_TRADEOFF_AND_ADVERSE_REPAIR_INVOICE",
              "proof": "REPAIR.md; finite tests are not a proof kernel",
              "source_replay": application["source_replay"],
              "source_ports": ports, "new_returns_required": len(ports),
              "first_width": 72, "squared_error_per_missing_return": "1/9",
              "later_width": 84, "later_squared_error_per_missing_return": "125/126",
              "operator_error_squared_at_103_returns_and_width_84": "125/13104",
              "max_returns_for_any_positive_concave_power_margin": 95,
              "any_profitable_repair_operator_error_squared_from_width_72": "1/104",
              "any_profitable_repair_operator_error_squared_from_width_84": "125/1456",
              "reference_tariff_budget": budget,
              "optimistic_invoice_comparison": cost, "finite_checks": counts,
              "physical_approximation_errors": errors, "new_kappa": None}
    for name, value in (("REPAIR-INVOICE.json", actual), ("REPAIR-RESULT.json", result)):
        path = HERE / name
        if write:
            path.write_text(json.dumps(value, indent=2, sort_keys=True)+"\n")
        else:
            need(value == json.loads(path.read_text()), "Complete repair receipt: "+name)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args()
    print(run(args.write_result)["status"])


if __name__ == "__main__":
    main()
