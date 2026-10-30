#!/usr/bin/env python3
"""Check canonical RIGHT-factor certificates independently of their generator.

ToikY with substantial OpenAI Codex assistance in a separate implementation
context. Ali Romman supplied the frozen G20 port matrices and caller data.
JoyboyBrian supplied the retained addressed P2 route interface. Apache-2.0;
NOTICE and PROOF retain the source and primitive authors' credit.
"""
import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha1, sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
PINS = {
    "PORTS.json": (311085,
        "a53a49c938a46c5a9da8c05ffdec4c2ef2dd906dd94c009d6fa451af4ed350e9",
        "aeffcdb444f564d247aff2265f9aebc424bce14f"),
    "CONTROLLER.json": (23753,
        "39ac84fb848b908f7ba051fae4556d507900c421dc5d23501a9c0cb1d61fd08d",
        "89c400d5970024b3debe870c36ce43889beed001"),
    "CALLS.json": (18903,
        "30dcc37cdade6b2dc05478837eca28b696894d1c4782bac6a1caab5e7f56c9e8",
        "9ee8c26f321ee3d420976fab69075c0c05db12ce"),
}
STAGES = [0, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 32]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticated(name):
    raw = (HERE / "inputs" / name).read_bytes()
    size, digest, blob = PINS[name]
    require(len(raw) == size and sha256(raw).hexdigest() == digest,
            "Oracle exact source bytes: " + name)
    require(sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == blob,
            "Oracle exact Git blob: " + name)
    return json.loads(raw)


def identity():
    return [[Fraction(i == j) for j in range(8)] for i in range(8)]


def product(left, right):
    # General matrix products, unlike the generator's elementary row updates.
    return [[sum((left[i][k] * right[k][j] for k in range(8)
                  if left[i][k] and right[k][j]), Fraction(0))
             for j in range(8)] for i in range(8)]


def power_of_two(value):
    return type(value) is int and value > 0 and value & (value - 1) == 0


def parse(event):
    require(type(event) is list and event and event[0] in ("ADD", "SCALE"),
            "Oracle only explicit ADD/SCALE operations")
    kind = event[0]
    require(len(event) == (4 if kind == "ADD" else 3), "Oracle opcode arity")
    indices = event[1:3] if kind == "ADD" else event[1:2]
    require(all(type(i) is int and 0 <= i < 8 for i in indices),
            "Oracle active coordinate range")
    require(type(event[-1]) is str, "Oracle exact coefficient string")
    q = Fraction(event[-1])
    require(q and str(q) == event[-1] and power_of_two(q.denominator),
            "Oracle nonzero canonical dyadic coefficient")
    if kind == "SCALE":
        require(power_of_two(abs(q.numerator)), "Oracle dyadic unit SCALE")
        return kind, indices[0], indices[0], q
    require(indices[0] != indices[1], "Oracle distinct ADD coordinates")
    return kind, indices[0], indices[1], q


def matrix_from_word(word):
    require(type(word) is list and len(word) <= 10000, "Oracle finite word")
    result = identity()
    for event in word:
        kind, i, j, q = parse(event)
        elementary = identity()
        elementary[i][j] = q
        result = product(result, elementary)
    return result


def row_basis_from_word(word):
    # A second interpretation: eight independent row vectors execute the
    # canonical RIGHT list directly. ADD[i,j,q] updates coordinate j from i.
    output = []
    for basis in range(8):
        row = [Fraction(basis == j) for j in range(8)]
        for event in word:
            kind, i, j, q = parse(event)
            if kind == "ADD":
                row[j] += q * row[i]
            else:
                row[i] *= q
        output.append(row)
    return output


def source_matrix(table):
    require(type(table) is list and len(table) == 8
            and all(type(row) is list and len(row) == 8 for row in table),
            "Oracle source matrix dimensions")
    return [[Fraction(value) for value in row] for row in table]


def inverse_word(word):
    result = []
    for event in reversed(word):
        kind, i, j, q = parse(event)
        result.append(["ADD", i, j, str(-q)] if kind == "ADD"
                      else ["SCALE", i, str(1 / q)])
    return result


def address_layouts(pairs):
    layouts = []
    templates = 0
    for ordinal, stage in enumerate(STAGES):
        active = [0] + list(range(1 + 7 * ordinal, 8 + 7 * ordinal))
        spectators = sorted(set(range(127)) - set(active))
        require(len(active) == len(set(active)) == 8 and len(spectators) == 119,
                "Oracle exact active/spectator split")
        for f in (1, 2):
            dimension = 127 * f
            touched = {coordinate * f + lane for coordinate in active
                       for lane in range(f)}
            require(len(touched) == 8 * f
                    and len(set(range(dimension)) - touched) == 119 * f,
                    "Oracle tensor spectators")
            for i, j in sorted(pairs):
                for row in range(dimension):
                    for lane in range(f):
                        src = row * dimension + active[i] * f + lane
                        dst = row * dimension + active[j] * f + lane
                        require(0 <= src < dimension**2 and 0 <= dst < dimension**2,
                                "Oracle flat address range")
                        require(src // dimension == dst // dimension == row
                                and src % dimension in touched
                                and dst % dimension in touched,
                                "Oracle same-row active-address law")
                        require(src % f == dst % f == lane,
                                "Oracle exact spectator-lane preservation")
                        templates += 1
        layouts.append({"stage": stage, "ordinal": ordinal,
                        "active": active, "spectators": spectators})
    return layouts, templates


def run():
    source = authenticated("PORTS.json")
    controller = authenticated("CONTROLLER.json")
    calls = authenticated("CALLS.json")
    require(controller["ambient_rank"] == 127
            and controller["invoice"]["thick_stages"] == STAGES,
            "Oracle exact caller stage inventory")
    require(len(calls) == 18 and [row["stage"] for row in calls] == STAGES,
            "Oracle every actual full call")
    raw = (HERE / "RESULT.json").read_bytes()
    candidate = json.loads(raw)
    records = candidate["ports"]
    ports = source["port_interfaces"]["ports"]
    require(len(records) == len(ports) == 111
            and [row["port"] for row in records] == list(range(111))
            and [row["port"] for row in ports] == list(range(111)),
            "Oracle exact 111-port inventory")
    histogram = Counter()
    pairs = set()
    lengths = []
    for record, original in zip(records, ports):
        forward, backward = record["forward_word"], record["inverse_word"]
        require(backward == inverse_word(forward), "Oracle literal inverse word")
        matrices = []
        for word, table in ((forward, original["normalizer"]),
                            (backward, original["inverse"])):
            expected = source_matrix(table)
            found = matrix_from_word(word)
            require(found == expected == row_basis_from_word(word),
                    "Oracle RIGHT product and eight basis rows")
            matrices.append(found)
            for event in word:
                kind, i, j, q = parse(event)
                histogram[(kind, str(q))] += 1
                pairs.add((i, j))
        require(product(matrices[0], matrices[1]) == identity()
                == product(matrices[1], matrices[0]), "Oracle both round trips")
        lengths.append({"port": record["port"], "forward": len(forward),
                        "inverse": len(backward)})
    layouts, templates = address_layouts(pairs)
    counts = []
    for f in (1, 2):
        dimension = 127 * f
        multiplier = 18 * 2 * dimension * f
        leaves = {"ordered_shift" if kind == "ADD" else "unit_scale": 0
                  for kind, coefficient in histogram}
        coefficients = []
        for (kind, coefficient), count in sorted(histogram.items()):
            leaf = "ordered_shift" if kind == "ADD" else "unit_scale"
            leaves[leaf] += count * multiplier
            coefficients.append({"primitive": leaf, "coefficient": coefficient,
                                 "count": count * multiplier})
        counts.append({"f": f, "N": dimension, "full_calls": 18,
                       "paired_halves": 2, "both_directions_in_base_histogram": True,
                       "all_matrix_rows_times_lanes_times_calls_times_halves": multiplier,
                       "coefficient_counts": coefficients, "primitive_counts": leaves})
    return {
        "status": "PASS_G20_NORMALIZER_DYADIC_WORD_ORACLE",
        "result_sha256": sha256(raw).hexdigest(),
        "source_sha256": {name: pin[1] for name, pin in PINS.items()},
        "convention": "I E1 ... Em = W; ADD[i,j,q] has matrix entry (i,j)=q "
                      "and updates row coordinate j from i; no word reversal.",
        "ports": 111, "right_products": 222, "row_basis_products": 222,
        "round_trips": 222, "layouts": layouts,
        "flat_address_templates_checked": templates,
        "word_lengths": lengths,
        "cross_product_catalogue_count": counts,
        "nominal_kernel_instances": 111 * 18 * 2 * 2,
        "incidence_limit": "7992 is the declared Cartesian catalogue count, not an "
                           "actual source paid-route count. A per-event mapping "
                           "is open; no event is presumed to equal one word.",
        "spectator_argument": "Every emitted address lies in one active column "
                              "and the same matrix row/lane; all119f inactive "
                              "columns remain fixed for every port word.",
        "scope": "Finite RIGHT-factor semantics and positive named P2 call counts. "
                 "These are not actual source route-use counts or a physical head "
                 "map. Full ROW borrow/cache/carry/return, coefficient preparation, "
                 "tape tariffs, native admission and compiler closure remain open.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true",
                        help="Print a candidate receipt without writing any file")
    args = parser.parse_args()
    receipt = run()
    if args.emit:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    else:
        expected = json.loads((HERE / "ORACLE.json").read_bytes())
        require(json.dumps(expected, sort_keys=True, separators=(",", ":"), allow_nan=False)
                == json.dumps(receipt, sort_keys=True, separators=(",", ":"), allow_nan=False),
                "Oracle complete retained receipt")
        print(json.dumps({"status": receipt["status"], "right_products": 222,
                          "row_basis_products": 222, "round_trips": 222},
                         sort_keys=True))


if __name__ == "__main__":
    main()
