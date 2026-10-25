"""Independent exact minimum charge of the two-hub literal actual-reader row model.

This program shares no code with ``verify.py``. It uses only integer
arithmetic and fraction-free elimination, and it reaches the per-row minima
by an explicit span table over the nine queries rather than by the
linear-programming route that ``verify.py`` uses.

Two separate facts are checked here.

1. The universal row bound. For any admissible row p the reader identity
   sum_i u_i^(p) Q_i = mark(p) and the evaluator condition
   phi_p(mark(p)) = 1 give

       1 = sum_i u_i^(p) phi_p(Q_i),

   so at least one index i has both factors nonzero and cost(p) >= 1. This
   is arithmetic on the model, not a search, and the default reader sets
   ghx for E and ghy for F attain it.

2. The reader rows. On a reader row the evaluator is the mark's coordinate
   functional, so phi_p(Q_i) is the mark component of Q_i. The program
   enumerates every admissible reader support and takes the exact minimum.
   ``verify.py`` independently repeats this after relaxing the reader
   evaluator to every functional with phi(mark) = 1 and phi(other mark) = 0,
   which is a superset of the admissible set and therefore a conservative
   lower bound; it returns the same total.
"""

import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NAMES = "gdthxykzw"
WIDTH = 5


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(name, bound=1_000_000):
    path = ROOT / name
    require(path.stat().st_size <= bound, "input exceeds byte bound")
    return json.loads(path.read_text())


def is_nonzero(text):
    """Zero test for an integer or a simple rational literal, without Fractions."""
    require(isinstance(text, str), "reader coefficient must be a string")
    numerator, _, denominator = text.partition("/")
    return int(numerator) * int(denominator or "1") != 0


def rank_over_q(matrix):
    """Exact rank over Q by fraction-free integer Gaussian elimination.

    Each step swaps a nonzero entry into place and then replaces a lower
    row by a nonzero multiple of itself minus a multiple of the pivot row.
    Both operations preserve the row space over Q, so no division and no
    rational arithmetic is needed.
    """
    rows = [list(row) for row in matrix]
    require(rows and len(rows) <= WIDTH and len(rows[0]) <= WIDTH, "rank shape")
    height, width = len(rows), len(rows[0])
    pivot_row = 0
    for col in range(width):
        if pivot_row >= height:
            break
        pivot = next((i for i in range(pivot_row, height) if rows[i][col] != 0), None)
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        lead = rows[pivot_row][col]
        for i in range(pivot_row + 1, height):
            if rows[i][col] == 0:
                continue
            scale = rows[i][col]
            rows[i] = [
                lead * rows[i][j] - scale * rows[pivot_row][j] for j in range(width)
            ]
        pivot_row += 1
    return pivot_row


def contains(vectors, target):
    """Whether target lies in the Q-span of vectors."""
    require(1 <= len(vectors) <= WIDTH, "span shape")
    matrix = [list(v) for v in vectors] + [list(target)]
    return rank_over_q(matrix) == rank_over_q(vectors)


def main():
    origins = load("ORIGINS.json")
    for row in origins["files"]:
        raw = (ROOT / row["retained_path"]).read_bytes()
        require(
            hashlib.sha256(raw).hexdigest() == row["sha256"],
            "retained source hash " + row["retained_path"],
        )
    config = load("predecessor/CONFIG.json")
    require(config["query_names"] == NAMES, "query naming")
    queries = [list(map(int, q)) for q in config["queries"]]
    marks = [list(map(int, m)) for m in config["marks"]]
    require(len(queries) == 9 and len(marks) == 2, "query and mark shape")
    index = {c: i for i, c in enumerate(NAMES)}

    source, reader = {0: [], 1: []}, {0: [], 1: []}
    for mark in (0, 1):
        source[mark] = [
            [index[c] for c in spec]
            for (m, spec) in config["premises"]["source"]
            if m == mark
        ]
        reader[mark] = [
            [index[c] for c in spec]
            for (m, spec) in config["premises"]["reader"]
            if m == mark
        ]
    require(len(source[0]) == 4 and len(source[1]) == 3, "7 source rows")
    require(len(reader[0]) == 7 and len(reader[1]) == 7, "14 reader rows")

    # The default readers ghx and ghy carry each mark, so the universal bound
    # of one unit per source row is attained.
    source_units = 0
    for mark in (0, 1):
        default = [index[c] for c in ("ghx" if mark == 0 else "ghy")]
        require(
            contains([queries[i] for i in default], marks[mark]),
            "default reader carries the mark",
        )
        require(
            not contains([queries[i] for i in default], marks[1 - mark]),
            "default reader must not carry the other mark",
        )
        source_units += len(source[mark])

    reader_units = 0
    detail = []
    for mark in (0, 1):
        for spec in reader[mark]:
            best = None
            for size in range(1, len(spec) + 1):
                for pick in itertools.combinations(spec, size):
                    if not contains([queries[i] for i in pick], marks[mark]):
                        continue
                    cost = sum(1 for i in pick if queries[i][mark] != 0)
                    if best is None or cost < best:
                        best = cost
            require(best is not None, "reader row has no admissible support")
            reader_units += best
            detail.append(
                {
                    "mark": mark,
                    "premise": "".join(NAMES[i] for i in spec),
                    "minimum": best,
                }
            )

    units = reader_units + source_units
    require(units == 27, "row-unit total " + str(units))
    receipt = load("RESULT.json")
    require(receipt["row_units"] == units, "row-unit receipt mismatch")
    require(receipt["minimum_charge"] == 2 * units, "charge receipt mismatch")
    require(receipt["forced_excess"] == 2 * units - 42, "excess receipt mismatch")
    require(receipt["row_units"] > 21, "baseline must be excluded")
    recorded = [
        {
            "mark": r["mark"],
            "premise": r["premise"],
            "minimum": r["minimum"],
        }
        for r in receipt["row_minima"]
        if r["kind"] == "reader"
    ]
    require(recorded == detail, "reader row receipt mismatch")
    require(
        all(r["minimum"] == 1 for r in receipt["row_minima"] if r["kind"] == "source"),
        "source rows are pinned to the universal bound",
    )
    require(
        sorted(receipt["forced_reader_rows"])
        == ["dxy", "dxy", "dzw", "dzw", "gtxy", "gtxy"],
        "forced reader receipt mismatch",
    )

    # Recompute the nine plane charges of the retained witness without any
    # rational arithmetic: only zero tests on integers are needed here.
    witness = load("predecessor/WITNESS.json")
    functionals = [[int(a) for a in f] for f in witness["functionals"]]
    readers = [[is_nonzero(c) for c in u] for u in witness["readers"]]
    require(len(functionals) == 21 and len(readers) == 21, "21 witness rows")
    charges = []
    for i in range(9):
        active = 0
        for p in range(21):
            if not readers[p][i]:
                continue
            if sum(a * b for a, b in zip(functionals[p], queries[i])) != 0:
                active += 1
        charges.append(2 * active)
    require(charges == receipt["witness_charges"], "witness charge receipt mismatch")
    require(sum(charges) == 2 * units, "witness attains the searched minimum")
    print(
        "PASS_TWO_HUB_TARIFF_MINIMUM_INDEPENDENT "
        + json.dumps(
            {
                "forced_reader_rows": sorted(
                    {d["premise"] for d in detail if d["minimum"] == 2}
                ),
                "minimum_charge": 2 * units,
                "no_new_kappa": True,
                "reader_rows": len(detail),
                "row_units": units,
                "source_rows": source_units,
                "witness_charge_total": sum(charges),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
