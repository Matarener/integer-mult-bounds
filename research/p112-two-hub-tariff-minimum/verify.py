"""Exact minimum charge of the two-hub literal actual-reader factorization.

Model, stated once here and proved in PROOF.md.

The two-hub K3,2 support-transfer certificate of PR3583 consists of 21
premise rows over the nine queries ``gdthxykzw`` in Q^5 with marks E, F:
seven source exclusions and fourteen reader containments. A *literal
actual-reader factorization* assigns to every row p

  * an evaluator functional phi_p in Q^5,
  * a reader coefficient vector u^(p) in Q^9,

such that sum_i u_i^(p) Q_i = mark(p), and

  * a source row satisfies phi_p(mark(p)) = 1, phi_p(mark(other)) = 0 and
    phi_p(Q_i) = 0 for every query of its premise;
  * a reader row has phi_p equal to the mark's coordinate functional and
    supp(u^(p)) inside its premise's query set;
  * for a source row, supp(u^(p)) lies inside one of the seven reader
    premise sets of that mark.

Each row gets a zero companion port, giving 42 ports. With ``a`` and ``b``
the alternating-half binary indicators on the E-rows and F-rows, the nine
rectangular complete planes satisfy

    a a^T + b b^T = sum_i u_i q_i^T,

where u_i and q_i are zero at companions, (u_i)_p = u_i^(p) and
(q_i)_p = phi_p(Q_i). The measured charge of plane i is twice the number of
active rows p where both factors are nonzero, so the total charge is
2 * sum_p cost(p) with

    cost(p) = #{ i : u_i^(p) != 0 and phi_p(Q_i) != 0 }.

This module proves the lower bound by exhaustive enumeration of the finite
row model, and checks that the retained PR3583 witness attains it.
"""

import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ZERO = Fraction(0)
WIDTH = 5
NAMES = "gdthxykzw"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(name, bound=1_000_000):
    path = ROOT / name
    require(path.stat().st_size <= bound, "input exceeds byte bound")
    return json.loads(path.read_text())


def rref(matrix, rhs):
    """Reduced row echelon form over Q.

    Returns (particular solution or None, nullspace basis, consistent).
    """
    rows = [list(row) + [rhs[i]] for i, row in enumerate(matrix)]
    columns = len(matrix[0])
    pivots, r = [], 0
    for col in range(columns):
        chosen = next((i for i in range(r, len(rows)) if rows[i][col] != 0), None)
        if chosen is None:
            continue
        rows[r], rows[chosen] = rows[chosen], rows[r]
        pivot = rows[r][col]
        rows[r] = [x / pivot for x in rows[r]]
        for i in range(len(rows)):
            if i != r and rows[i][col] != 0:
                factor = rows[i][col]
                rows[i] = [x - factor * y for x, y in zip(rows[i], rows[r])]
        pivots.append(col)
        r += 1
        if r == len(rows):
            break
    ok = all(row[-1] == 0 for row in rows if all(v == 0 for v in row[:-1]))
    if not ok:
        return None, [], False
    particular = [ZERO] * columns
    for i, col in enumerate(pivots):
        particular[col] = rows[i][-1]
    basis = []
    for free in [c for c in range(columns) if c not in pivots]:
        vector = [ZERO] * columns
        vector[free] = Fraction(1)
        for i, col in enumerate(pivots):
            vector[col] = -rows[i][free]
        basis.append(vector)
    return particular, basis, True


class Model:
    def __init__(self, config):
        require(config["query_names"] == NAMES, "query naming")
        self.queries = [[Fraction(a) for a in q] for q in config["queries"]]
        self.marks = [[Fraction(a) for a in m] for m in config["marks"]]
        require(len(self.queries) == 9 and len(self.marks) == 2, "shape")
        self.index = {c: i for i, c in enumerate(NAMES)}
        self.source, self.reader = {}, {}
        for mark in (0, 1):
            self.source[mark] = [
                (m, [self.index[c] for c in spec])
                for (m, spec) in config["premises"]["source"]
                if m == mark
            ]
            self.reader[mark] = [
                (m, [self.index[c] for c in spec])
                for (m, spec) in config["premises"]["reader"]
                if m == mark
            ]

    def rows(self):
        out = []
        for mark in (0, 1):
            for _, spec in self.source[mark]:
                out.append(("source", mark, spec))
            for _, spec in self.reader[mark]:
                out.append(("reader", mark, spec))
        return out

    def in_span(self, vectors, target):
        if not vectors:
            return False
        matrix = [[v[j] for v in vectors] for j in range(WIDTH)]
        particular, _, ok = rref(matrix, target)
        return ok

    def admissible_supports(self, kind, mark, spec):
        """Every allowed set of query indices carrying the reader at this row."""
        pools = [spec] if kind == "reader" else [
            s for _, s in self.reader[mark]
        ]
        seen = set()
        for pool in pools:
            for size in range(1, len(pool) + 1):
                for pick in itertools.combinations(pool, size):
                    if pick in seen:
                        continue
                    seen.add(pick)
                    if self.in_span([self.queries[i] for i in pick], self.marks[mark]):
                        yield pick

    def evaluators(self, kind, mark, spec, killed):
        """Solve for an admissible phi killing the given query indices.

        For a reader row the proof forces phi to be the mark's coordinate
        functional. This routine deliberately admits the larger set of all
        phi with phi(mark) = 1 and phi(other mark) = 0, so the searched
        minimum is a lower bound for the real model, never an overestimate.
        """
        constraints = [self.marks[mark], self.marks[1 - mark]]
        targets = [Fraction(1), ZERO]
        if kind == "source":
            for i in list(spec) + list(killed):
                constraints.append(self.queries[i])
                targets.append(ZERO)
        else:
            for i in killed:
                constraints.append(self.queries[i])
                targets.append(ZERO)
        matrix = [[c[j] for j in range(WIDTH)] for c in constraints]
        particular, _, ok = rref(matrix, targets)
        return particular if ok else None

    def row_minimum(self, kind, mark, spec):
        """Smallest possible cost(p), searched over the whole row model."""
        best, witness = None, None
        for pool in self.admissible_supports(kind, mark, spec):
            for killed_size in range(len(pool), -1, -1):
                feasible = None
                for killed in itertools.combinations(pool, killed_size):
                    phi = self.evaluators(kind, mark, spec, killed)
                    if phi is not None:
                        feasible = (killed, phi)
                        break
                if feasible is None:
                    continue
                killed, phi = feasible
                cost = sum(
                    1
                    for i in pool
                    if sum(a * b for a, b in zip(phi, self.queries[i])) != 0
                )
                if best is None or cost < best:
                    best, witness = cost, (pool, killed, phi)
        require(best is not None, "no admissible row")
        return best, witness


def check_premises(model):
    """The 21 premises really are the stated exclusions and containments."""
    for mark in (0, 1):
        for _, spec in model.source[mark]:
            block = [model.marks[1 - mark]] + [model.queries[i] for i in spec]
            require(not model.in_span(block, model.marks[mark]), "source exclusion")
        for _, spec in model.reader[mark]:
            require(
                model.in_span([model.queries[i] for i in spec], model.marks[mark]),
                "reader containment",
            )
    return True


def check_witness(model, witness):
    """Check the retained PR3583 witness row by row against the row model."""
    rows = model.rows()
    require(len(witness["rows"]) == 21, "21 certificate rows")
    for p, (row, phi_values, reader) in enumerate(
        zip(witness["rows"], witness["functionals"], witness["readers"])
    ):
        kind, mark, spec = rows[p]
        require([kind, mark] == [row[0], row[1]], "row ordering")
        require("".join(NAMES[i] for i in spec) == row[2], "row premise")
        phi = [Fraction(a) for a in phi_values]
        require(len(phi) == WIDTH, "functional width")
        require(
            sum(a * b for a, b in zip(phi, model.marks[mark])) == 1, "phi at mark"
        )
        require(
            sum(a * b for a, b in zip(phi, model.marks[1 - mark])) == 0,
            "phi at other mark",
        )
        if kind == "source":
            require(
                all(
                    sum(a * b for a, b in zip(phi, model.queries[i])) == 0
                    for i in spec
                ),
                "phi vanishes on premise",
            )
        else:
            require(
                all(c == 0 for i, c in enumerate(phi) if i != mark),
                "reader functional is the coordinate functional",
            )
        coefficients = [Fraction(c) for c in reader]
        require(
            all(c.denominator in (1, 2) for c in coefficients), "reader denominator"
        )
        if kind == "reader":
            require(
                all(
                    c == 0 or NAMES[i] in row[2]
                    for i, c in enumerate(coefficients)
                ),
                "reader support inside premise",
            )
        else:
            require(
                all(
                    c == 0 or NAMES[i] in row[2]
                    for i, c in enumerate(coefficients)
                )
                or all(
                    c == 0 or NAMES[i] in ("ghx" if mark == 0 else "ghy")
                    for i, c in enumerate(coefficients)
                ),
                "source reader support is an admissible reader premise",
            )
        value = [
            sum(c * q[j] for c, q in zip(coefficients, model.queries))
            for j in range(WIDTH)
        ]
        require(value == model.marks[mark], "reader identity")
    return rows


def check_identity(model, witness):
    """All 42x42 entries of aa^T + bb^T = sum_i u_i q_i^T."""
    rows = model.rows()
    phis, readers = [], []
    for p in range(len(rows)):
        phis.append([Fraction(a) for a in witness["functionals"][p]])
        readers.append([Fraction(c) for c in witness["readers"][p]])
    a, b = [], []
    for p in range(len(rows)):
        a += [Fraction(1 if rows[p][1] == 0 else 0), Fraction(0)]
        b += [Fraction(1 if rows[p][1] == 1 else 0), Fraction(0)]
    for p in range(42):
        for q in range(42):
            left = a[p] * a[q] + b[p] * b[q]
            right = ZERO
            if p % 2 == 0 and q % 2 == 0:
                phi = phis[q // 2]
                for i in range(9):
                    right += readers[p // 2][i] * sum(
                        x * y for x, y in zip(phi, model.queries[i])
                    )
            require(left == right, "gram identity entry")
    return 42


def main():
    origins = load("ORIGINS.json")
    for row in origins["files"]:
        raw = (ROOT / row["retained_path"]).read_bytes()
        require(
            hashlib.sha256(raw).hexdigest() == row["sha256"],
            "retained source hash " + row["retained_path"],
        )
    config = load("predecessor/CONFIG.json")
    model = Model(config)
    require(check_premises(model), "premise replay")
    rows = model.rows()
    minima = [model.row_minimum(kind, mark, spec) for kind, mark, spec in rows]
    units = sum(c for (c, _) in minima)
    require(units == 27, "row-unit total " + str(units))
    witness = load("predecessor/WITNESS.json")
    check_witness(model, witness)
    ports = check_identity(model, witness)
    charges = []
    for i in range(9):
        active = 0
        for p, (kind, mark, spec) in enumerate(rows):
            phi = [Fraction(a) for a in witness["functionals"][p]]
            u = Fraction(witness["readers"][p][i])
            if u != 0 and sum(x * y for x, y in zip(phi, model.queries[i])) != 0:
                active += 1
        charges.append(2 * active)
    require(sum(charges) == 54, "retained witness charge " + str(sum(charges)))
    receipt = load("RESULT.json")
    require(charges == receipt["witness_charges"], "charge receipt mismatch")
    expected_rows = []
    for (kind, mark, spec), (cost, arg) in zip(rows, minima):
        pool, killed, _ = arg
        expected_rows.append(
            {
                "attained_evaluator_kills": "".join(NAMES[i] for i in killed),
                "attained_reader_support": "".join(NAMES[i] for i in pool),
                "kind": kind,
                "mark": mark,
                "minimum": cost,
                "premise": "".join(NAMES[i] for i in spec),
            }
        )
    require(receipt["row_minima"] == expected_rows, "row minimum receipt mismatch")
    require(receipt["rows"] == len(rows), "row count receipt mismatch")
    require(receipt["row_units"] == units, "row unit receipt mismatch")
    require(receipt["minimum_charge"] == 2 * units, "charge receipt mismatch")
    require(receipt["forced_excess"] == 2 * units - 42, "excess receipt mismatch")
    require(receipt["baseline_charge"] == 42, "baseline receipt mismatch")
    require(receipt["forced_reader_rows"] == [
        r["premise"] for r in expected_rows if r["minimum"] == 2
    ], "forced reader receipt mismatch")
    require(receipt["ports"] == ports, "port receipt mismatch")
    require(ports == 42, "port count")
    print(
        "PASS_TWO_HUB_TARIFF_MINIMUM "
        + json.dumps(
            {
                "rows": len(rows),
                "ports": ports,
                "row_units": units,
                "minimum_charge": 2 * units,
                "baseline_charge": 42,
                "attained_by_retained_witness": True,
                "no_new_kappa": True,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()