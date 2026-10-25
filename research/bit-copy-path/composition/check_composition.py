#!/usr/bin/env python3
"""R429 coded endpoint in the pinned nine-stage BIT recipe.

Finite exact scalar and rational witnesses only. No positive supplier tariff.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import argparse
import ast
import gzip
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PINS = {
    "composition/inputs/CODED-WORD.json.gz":
        "1a6841fccba51fa922993c77b4b296e659c2c538252e5e06113d0438c5edb870",
    "inputs/GEOMETRY.json.gz":
        "a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022",
    "inputs/global_k.py.txt":
        "6368196a393ac25bb2918880e4c4bd31ed733b762c27b6873ab391cbc0c5c3c8",
    "composition/inputs/FULL-E8-GEOMETRY.json.gz":
        "1fb726ea3818fe0837cceb0dd22a71a0814f064e5e781628104610d6468e0e55",
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def read(relative):
    path = ROOT / relative
    raw = path.read_bytes()
    need(sha256(raw).hexdigest() == PINS[relative], "Source bytes changed")
    return json.loads(gzip.decompress(raw)) if path.suffix == ".gz" else raw.decode()


def bits(value):
    while value:
        bit = value & -value
        yield bit.bit_length() - 1
        value ^= bit


def xor(values):
    result = 0
    for value in values:
        result ^= value
    return result


def product(left, right):
    return [xor(right[j] for j in bits(row)) for row in left]


def rank2(rows):
    pivots = {}
    for row in rows:
        while row:
            p = (row & -row).bit_length() - 1
            if p in pivots:
                row ^= pivots[p]
            else:
                pivots[p] = row
                break
    return len(pivots)


def inverse(rows):
    n = len(rows)
    rows = [row | (1 << (n + j)) for j, row in enumerate(rows)]
    for j in range(n):
        p = next((p for p in range(j, n) if rows[p] >> j & 1), None)
        need(p is not None, "Singular code")
        rows[j], rows[p] = rows[p], rows[j]
        for p in range(n):
            if p != j and rows[p] >> j & 1:
                rows[p] ^= rows[j]
    return [row >> n for row in rows]


def rankq(rows):
    basis = {}
    for row in rows:
        row = list(map(Fraction, row))
        for p, old in sorted(basis.items()):
            c = row[p]
            if c:
                row = [x - c*y for x, y in zip(row, old)]
        p = next((p for p, x in enumerate(row) if x), None)
        if p is not None:
            c = row[p]
            basis[p] = [x/c for x in row]
    return len(basis)


def literal_endpoint(word, reverse=False):
    n = word["public_registers"]
    rows = [1 << i for i in range(n)] + [0]
    live = None
    records = list(reversed(word["records"])) if reverse else word["records"]
    for op, dst, src, coefficient, _frame, _phase in records:
        if op == 1:
            if coefficient & 1:
                rows[dst] ^= rows[src]
        elif op == (3 if reverse else 2):
            need(live is None and rows[n] == 0, "Private field already live")
            rows[n] = rows[dst]
            live = dst
        elif op == (2 if reverse else 3):
            need(live == dst and rows[n] == rows[dst], "Snapshot changed")
            rows[n] = 0
            live = None
        else:
            need(op == 0, "Unknown literal opcode")
    need(live is None and rows[n] == 0, "Unclosed private field")
    return rows


def recipe(source):
    tree = ast.parse(source)
    selected = [node for node in tree.body
                if isinstance(node, ast.FunctionDef) and node.name == "recipe"]
    need(len(selected) == 1, "Unique source recipe")
    module = ast.Module(body=selected, type_ignores=[])
    namespace = {}
    exec(compile(module, "<pinned recipe>", "exec", dont_inherit=True, optimize=0),
         namespace)
    events = namespace["recipe"](4)
    need(sum(e["kind"] == "local" for e in events) == 9, "Nine local stages")
    return events


def controller(events, code, code_inverse, source_restored=False):
    v = len(code)
    rows = [1 << i for i in range(8*v)]
    snapshots = []
    for event in events:
        if event["kind"] == "local":
            p = event["pair"]
            x = rows[2*p*v:(2*p+1)*v]
            y = rows[(2*p+1)*v:(2*p+2)*v]
            if event["reverse"]:
                if source_restored:
                    x = [a ^ b for a, b in zip(x, product(code, y))]
                else:
                    x = [a ^ b for a, b in zip(x, y)]
                    y = product(code_inverse, y)
            else:
                ax = product(code, x)
                x = x if source_restored else ax
                y = [a ^ b for a, b in zip(y, ax)]
            rows[2*p*v:(2*p+1)*v] = x
            rows[(2*p+1)*v:(2*p+2)*v] = y
            snapshots.append({"stage": event["stage"], "pair": p,
                              "reverse": event["reverse"],
                              "endpoint_sha256": sha256(canonical(rows)).hexdigest()})
        elif event["kind"] == "bridge":
            d, s = event["dst"], event["src"]
            for p in range(v):
                rows[2*d*v+p] ^= rows[2*s*v+p]
                rows[(2*s+1)*v+p] ^= rows[(2*d+1)*v+p]
        else:
            need(event["kind"] == "exchange", "Unknown recipe event")
            for bank in range(4):
                for p in range(v):
                    a, b = 2*bank*v+p, (2*bank+1)*v+p
                    rows[a], rows[b] = rows[b], rows[a]
    return rows, snapshots


def laurent_controller(events):
    rows = [[{0} if i == j else set() for j in range(8)] for i in range(8)]

    def add(d, s):
        rows[d] = [a ^ b for a, b in zip(rows[d], rows[s])]

    def scale(d, power):
        rows[d] = [{x + power for x in row} for row in rows[d]]

    for event in events:
        if event["kind"] == "local":
            p = event["pair"]
            if event["reverse"]:
                add(2*p, 2*p+1)
                scale(2*p+1, -1)
            else:
                scale(2*p, 1)
                add(2*p+1, 2*p)
        elif event["kind"] == "bridge":
            d, s = event["dst"], event["src"]
            add(2*d, 2*s)
            add(2*s+1, 2*d+1)
        else:
            for p in range(4):
                rows[2*p], rows[2*p+1] = rows[2*p+1], rows[2*p]
    return rows


def actual_two_charts(geometry, full):
    """Reconstruct the upstream Weyl BFS routes at ports zero and three."""
    roots = full["lines"]
    need(len(roots) == 120, "Full E8 source geometry")
    parent = {0: None}
    queue = [0]
    for p in queue:
        for q in range(120):
            inner = sum(x*y for x, y in zip(roots[p], roots[q]))
            if q not in parent and abs(inner) == 2:
                parent[q] = (p, inner//2)
                queue.append(q)
    need(len(parent) == 120, "Complete actual Weyl graph")
    result = []
    for port in (0, 3):
        label = geometry["ports_geom"][port]
        need(roots[label] == geometry["lines"][port], "Actual retained port label")
        path = []
        at = label
        while parent[at] is not None:
            previous, sign = parent[at]
            path.append((previous, at, sign))
            at = previous
        g = [[Fraction(i == j) for j in range(8)] for i in range(8)]
        for previous, current, sign in reversed(path):
            v = [x-sign*y for x, y in zip(roots[previous], roots[current])]
            norm = sum(x*x for x in v)
            read = [sum(v[i]*g[i][j] for i in range(8)) for j in range(8)]
            g = [[g[i][j]-Fraction(2*v[i], norm)*read[j] for j in range(8)]
                 for i in range(8)]
        cap = [row[1:] for row in g]
        root = geometry["lines"][port]
        p = [[Fraction(x*y, 4) for y in root] for x in root]
        need(all(sum(cap[i][k]*cap[j][k] for k in range(7))
                 == int(i == j)-p[i][j] for i in range(8) for j in range(8)),
             "Actual cap columns span the root complement")
        rho = [p[i]+cap[i] for i in range(8)]
        rho += [[cap[j][i] for j in range(8)] + [Fraction(0)]*7 for i in range(7)]
        need(all(sum(rho[i][k]*rho[k][j] for k in range(15)) == int(i == j)
                 for i in range(15) for j in range(15)), "Actual rho squared")
        result.append(rho)
    return result


def rational_fresh_witness(geometry, code, charts):
    roots = geometry["lines"]
    need(roots[0] == [2,0,0,0,0,0,0,0], "Actual source root")
    need(roots[3] == [0,0,0,2,0,0,0,0], "Actual destination root")
    need(code[3] & 1, "Actual nonzero A[3,0]")
    head = [Fraction(i == 59) for i in range(64)]

    def apply_chart(rho, vector, stage):
        axes = list(range(8)) + list(range(7*stage+1, 7*stage+8))
        out = vector[:]
        for i, a in enumerate(axes):
            out[a] = sum(rho[i][j]*vector[b] for j, b in enumerate(axes))
        return out

    middle = apply_chart(charts[0], head, 8)
    need(middle == [Fraction(i == 3) for i in range(64)], "First actual route")
    routed = apply_chart(charts[1], middle, 8)
    need(routed == middle, "Actual destination route fixes its root")
    need(all(apply_chart(rho, head, 7) == head for rho in charts),
         "Actual stage7 routes fix fresh stage8 input")
    p = [[Fraction(x*y, 4) for y in roots[3]] for x in roots[3]]
    tail = [sum(p[i][j]*routed[j] for j in range(8))
            if i < 8 else Fraction(0) for i in range(64)]
    outhead = [x-y for x, y in zip(routed, tail)]
    need(outhead == [0]*64 and tail == [int(i == 3) for i in range(64)],
         "Actual uncancelled TAIL impulse")
    # Stage7 routes are identity on fresh stage8 coordinates; every inverse
    # coefficient therefore stays on HEAD=e59, which N also fixes.
    return {
        "input_bank": 7, "input_port": 0, "input_HEAD_axis": 59,
        "input_TAIL": 0,
        "output_banks_after_parent_full_factor": [0, 2, 4, 6],
        "output_port": 3, "output_HEAD": 0, "output_TAIL_axis": 3,
        "VALUE_coefficient": 1,
        "ADDRESS_domain": "Every odd field; the displayed coordinates are integral",
        "route_reason": "rho8,0 e59=e3; rho8,3 e3=e3; rho7,p e59=e59",
        "actual_two_rho15_sha256": [
            sha256(canonical([[str(x) for x in row] for row in rho])).hexdigest()
            for rho in charts],
    }


def supports(geometry, code):
    n = 2*geometry["v"] + geometry["R"]
    rows = [1 << i for i in range(n)]
    for phase in ("D", "A"):
        for _frame, dst, sources in geometry[phase]:
            rows[dst] ^= xor(rows[src] for src in sources)
    mask = (1 << 111) - 1
    r = [rows[i] & mask for i in geometry["ret"]]
    k = [sum(1 << i for i in indices) for indices in geometry["scatter"]]
    w = [0 if p < 3 else row for p, row in enumerate(k)]
    need(rank2(w) == rank2(r) == 9, "Full nine-channel defect")
    need(product(w, r) == [row ^ (1 << p) for p, row in enumerate(code)],
         "Literal source defect equals W' R")
    census = []
    histogram = Counter()
    for q in range(1, 512):
        support = [p for p, row in enumerate(w) if (row & q).bit_count() & 1]
        dimension = rankq(geometry["lines"][p] for p in support)
        census.append({"query_output_vector": q, "support": support,
                       "support_rank": dimension})
        histogram[dimension] += 1
    need(histogram == {7: 12, 8: 499}, "Complete rational direction census")
    chosen = product(r, k)
    need(rank2(chosen) == 9 and all(census[q-1]["support_rank"] == 7 for q in chosen),
         "Nine independent rank-seven directions")
    clean = [row ^ (1 << p) for p, row in enumerate(product(k, r))]
    commutator_edges = []
    for p, row in enumerate(clean):
        q = next((q for q in bits(row) if q != p), None)
        need(q is not None, "Every clean-map row has an off-diagonal identity")
        pp = [[Fraction(x*y, 4) for y in geometry["lines"][p]]
              for x in geometry["lines"][p]]
        pq = [[Fraction(x*y, 4) for y in geometry["lines"][q]]
              for x in geometry["lines"][q]]
        changed = next(((i, j) for i in range(8) for j in range(8)
                        if pp[i][j] != pq[i][j]), None)
        need(changed is not None, "Distinct root projectors in actual edge")
        i, j = changed
        commutator_edges.append({
            "row": p, "column": q, "projector_entry": [i, j],
            "destination_projector_value": str(pp[i][j]),
            "source_projector_value": str(pq[i][j]),
        })
    return {
        "R": r, "W_prime": w,
        "complete_output_direction_census": census,
        "support_rank_histogram": dict(sorted(histogram.items())),
        "rank7_basis": chosen,
        "basis_model_native_rank_lower_bound": 63,
        "N_commuting_code_unchanged_row_obstructions": commutator_edges,
        "N_commuting_code_required_changed_physical_rows": 111,
        "one_snapshot_per_changed_row_native_rank_lower_bound": 111,
        "scope": (
            "Nine independent scalar latent readers, each using one common-cap "
            "completion whose rank is at least the span of its output port roots. "
            "This is a necessary bound, not an emitted legal decoder or a bound "
            "for overcomplete or ADDRESS-dependent readers."
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path,
                        help="Write a recomputed receipt to this explicit path.")
    args = parser.parse_args()
    word = read("composition/inputs/CODED-WORD.json.gz")
    geometry = read("inputs/GEOMETRY.json.gz")
    full_geometry = read("composition/inputs/FULL-E8-GEOMETRY.json.gz")
    charts = actual_two_charts(geometry, full_geometry)
    events = recipe(read("inputs/global_k.py.txt"))
    forward, backward = literal_endpoint(word), literal_endpoint(word, True)
    code, code_inverse = forward[:111], inverse(forward[:111])
    identity = [1 << i for i in range(111)]
    need(backward[:111] == code_inverse, "Literal inverse source code")
    for p in range(111):
        need(forward[111+p] == (1 << (111+p)) ^ code[p], "Coded forward target")
        need(backward[111+p] == (1 << (111+p)) ^ (1 << p), "Literal inverse target")
    for p in range(222, 651):
        need(forward[p] == backward[p] == 1 << p, "Arbitrary dirty helper return")
    rows, snapshots = controller(events, code, code_inverse)
    scalar = laurent_controller(events)
    powers = {-1: code_inverse, 0: identity}
    for i in range(1, 5):
        powers[i] = product(code, powers[i-1])
    rebuilt = []
    for blockrow in scalar:
        for p in range(111):
            rebuilt.append(xor(xor(powers[e][p] for e in polynomial) << (111*j)
                               for j, polynomial in enumerate(blockrow)))
    need(rows == rebuilt, "Independent Laurent and bit-row caller products")
    last_mask = ((1 << 111)-1) << 777
    residual = [a ^ b for a, b in zip(code, code_inverse)]
    for bank in range(8):
        expected = residual if bank % 2 == 0 else code if bank == 7 else [0]*111
        need([(row & last_mask) >> 777 for row in rows[111*bank:111*(bank+1)]]
             == expected, "Exact untouched-last-target block")
    clean, _ = controller(events, identity, identity)
    need(clean == [1 << i for i in range(888)], "Identity-code positive control")
    wrong, _ = controller(events, code, code)
    need(wrong != rows, "Wrong inverse-code mutation changes the caller")
    rational = rational_fresh_witness(geometry, code, charts)
    mutant = code[:]
    mutant[3] ^= 1
    try:
        rational_fresh_witness(geometry, mutant, charts)
    except ValueError:
        pass
    else:
        raise ValueError("Deleted actual code edge was not rejected")
    output_support = supports(geometry, code)
    power = identity
    order = None
    for i in range(1, 29):
        power = product(code, power)
        if power == identity:
            order = i
            break
    need(order == 28, "Actual source-code order")
    output = {
        "status": "PASS_R429_NINE_STAGE_ENDPOINT_DEFECT_AND_BOUNDED_REPAIR_FLOOR",
        "no_new_kappa": True,
        "source_pins": PINS,
        "A": code, "A_inverse": code_inverse,
        "source_code_order": order,
        "rank_A_minus_I": rank2([a ^ b for a, b in zip(code, identity)]),
        "rank_A_squared_minus_I": rank2(
            [a ^ b for a, b in zip(product(code, code), identity)]),
        "identity_source_rows": [p for p, row in enumerate(code) if row == 1 << p],
        "caller_laurent_exponents": [[sorted(p) for p in row] for row in scalar],
        "caller_scalar_defect_rank": rank2([row ^ (1 << p) for p, row in enumerate(rows)]),
        "caller_endpoint_sha256": sha256(canonical(rows)).hexdigest(),
        "chronological_scalar_endpoints": snapshots,
        "last_pair_residual_rank": rank2(residual),
        "actual_native_last_pair_witness": rational,
        "local_terminal_basis_floor": output_support,
        "controls": ["identity code restores all 888 public scalar inputs",
                     "using A as its inverse changes the full caller",
                     "deleting actual A[3,0] invalidates the native impulse"],
        "limits": [
            "No all-parameter or formal-kernel verification is claimed.",
            "Native last-pair derivation retains the actual fresh-block route contract.",
            "No legal cheap routed decoder, whole-owner schedule, precision or outer transfer.",
            "The 63-unit floor covers only the stated minimum-basis common-cap model.",
        ],
    }
    receipt = json.dumps(output, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.write_text(receipt)
    else:
        need((HERE / "RESULT.json").read_text() == receipt,
             "Saved composition receipt differs from exact recomputation")
    print(json.dumps({k: output[k] for k in
                     ("status", "caller_scalar_defect_rank", "rank_A_minus_I",
                      "rank_A_squared_minus_I", "no_new_kappa")}, sort_keys=True))


if __name__ == "__main__":
    main()
