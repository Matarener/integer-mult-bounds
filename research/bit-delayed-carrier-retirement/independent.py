#!/usr/bin/env python3
"""Independent native frame/invoice audit of the helper469 retirement.

Consumes only the two pinned input archives. It reconstructs both edits from
literal record identities, uses dense integer columns, and constructs rational
projectors through inverse Gram matrices. No producer/checker is imported.
"""
from collections import Counter
from decimal import Decimal, localcontext
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import json

PACKAGE = Path(__file__).resolve().parent
N, DIM = 660, 8


def require(condition, message):
    if not condition:
        raise ValueError(message)


def matrix_product(a, b):
    columns = list(zip(*b))
    return [[sum(x*y for x, y in zip(row, column)) for column in columns]
            for row in a]


def identity(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def inverse(a):
    n = len(a)
    out = [list(row) + eye for row, eye in zip(a, identity(n))]
    for j in range(n):
        k = next(k for k in range(j, n) if out[k][j])
        out[j], out[k] = out[k], out[j]
        z = out[j][j]
        out[j] = [v/z for v in out[j]]
        for k in range(n):
            if k != j and out[k][j]:
                z = out[k][j]
                out[k] = [v-z*w for v, w in zip(out[k], out[j])]
    return [row[n:] for row in out]


def basis(rows):
    pivots = {}
    result = []
    for original in rows:
        row = list(map(Q, original))
        for j, pivot in sorted(pivots.items()):
            z = row[j]
            row = [v-z*w for v, w in zip(row, pivot)]
        if not any(row):
            continue
        j = next(j for j, x in enumerate(row) if x)
        z = row[j]
        pivots[j] = [v/z for v in row]
        result.append(list(map(Q, original)))
    return result


def projection(lines):
    b = basis(lines)
    if not b:
        return [[Q(0) for _ in range(DIM)] for _ in range(DIM)], 0
    bt = list(map(list, zip(*b)))
    p = matrix_product(matrix_product(bt, inverse(matrix_product(b, bt))), b)
    require(matrix_product(p, p) == p, "projector idempotence")
    require(p == list(map(list, zip(*p))), "projector symmetry")
    require(all(x.denominator & (x.denominator-1) == 0 for row in p for x in row),
            "dyadic projector")
    return p, len(b)


def swap(p):
    return [[Q(i == j)-p[i][j] for j in range(DIM)] + p[i] for i in range(DIM)] + [
        p[i] + [Q(i == j)-p[i][j] for j in range(DIM)] for i in range(DIM)]


def minus(a, b):
    return [[x-y for x, y in zip(r, s)] for r, s in zip(a, b)]


def geometry_audit(geometry, records):
    cache = {}
    def frame(f):
        if f not in cache:
            cache[f] = projection(geometry["lines"][i] for i in geometry["frames"][f])
        return cache[f]
    pairs = set()
    for _, (op, _, before, after, rank, _) in records:
        if op == 0:
            pair = before, after, rank
        elif op in (2, 3):
            pair = rank, after, 7
        else:
            continue
        if pair in pairs:
            continue
        pairs.add(pair)
        p, pr = frame(pair[0])
        q, qr = frame(pair[1])
        require(qr-pr == pair[2], "derived MOVE/COPY rank")
        require(matrix_product(p, q) == p, "frame nesting")
        delta = minus(q, p)
        require(matrix_product(delta, delta) == delta, "delta idempotence")
        require(matrix_product(swap(p), swap(q)) == swap(delta), "native relative address operation")
    p0, r0 = frame(0)
    p1, r1 = frame(1)
    require(p0 == [[Q(0)]*DIM for _ in range(DIM)], "ZERO projector")
    require(p1 == identity(DIM), "FULL projector")
    p517, r517 = frame(517)
    require(r517 == 7, "closure intermediate rank")
    require((0,517,7) in pairs and (517,1,1) in pairs, "two-step closure queries")
    require(all(rank < DIM for _,_,rank in pairs), "strict local recursive child")
    return {"unique_frame_pairs": len(pairs), "frame_projectors": len(cache),
            "closure_projector_frame": 517, "closure_rank": r517,
            "terminal_return_rank": r1-r517, "zero_to_full_rank": r1-r0,
            "maximum_child_rank": max(rank for _,_,rank in pairs),
            "local_dimension": DIM, "all_children_strictly_smaller": True,
            "all_projectors_dyadic": True,
            "relative_address_identities": True}


def literal_inverse(records):
    out = []
    for tag, record in reversed(records):
        op, d, s, c, f, section = record
        if op == 0:
            record = [op, d, c, s, f, section]
        elif op == 1:
            record = [op, d, s, -c, f, section]
        else:
            record = [5-op, d, s, c, f, section]
        out.append((tag, record))
    return out


def dense_replay(records, initial_frames, final_frames, initial=None, snapshots=()):
    rows = ([[int(i == j) for j in range(N)] for i in range(N)] + [[0]*N]
            if initial is None else [list(row) for row in initial])
    frames = list(initial_frames) + [None]
    majorants = [sum(map(abs, row)) for row in rows]
    peak_l1 = max(majorants)
    peak_majorant = peak_l1
    peak_coefficient = max(max(map(abs, row)) for row in rows)
    active = None
    hist = Counter()
    adds = copies = erases = 0
    captures = {}
    for index, (tag, record) in enumerate(records):
        op, d, s, c, f, section = record
        if tag in snapshots:
            captures[str(tag)] = {
                "index": index, "frames": {str(k): frames[k] for k in (50,178,413,444,469,478,605)},
                "private_source": active,
                "rows": {str(k): {str(j):x for j,x in enumerate(rows[k]) if x}
                         for k in (50,413,444,469,478)}}
        if op == 0:
            require(frames[d] == s, "MOVE frame entrance")
            require(active is None, "MOVE inside active COPY")
            require(d != active, "active COPY source MOVE")
            frames[d] = c
            hist[f] += 1
        elif op == 1:
            require(c in (-1, 1), "unit ADD alphabet")
            require(d != s and frames[d] == frames[s] == f, "common ADD frame")
            require(d != active, "active COPY source ADD")
            rows[d] = [x+c*y for x, y in zip(rows[d], rows[s])]
            majorants[d] += majorants[s]
            peak_coefficient = max(peak_coefficient, max(map(abs, rows[d])))
            peak_l1 = max(peak_l1, sum(map(abs, rows[d])))
            peak_majorant = max(peak_majorant, majorants[d])
            adds += 1
        elif op == 2:
            require(s == N and active is None and not any(rows[N]), "fresh zero COPY")
            require(frames[d] == c and frames[N] is None, "COPY frame guard")
            rows[N] = list(rows[d])
            majorants[N] = majorants[d]
            frames[N] = f
            active = d
            hist[7] += 1
            copies += 1
        elif op == 3:
            require(s == N and active == d and frames[d] == c and frames[N] == f,
                    "ERASE frame guard")
            require(rows[N] == rows[d], "ERASE transported snapshot equality")
            rows[N] = [0]*N
            majorants[N] = 0
            frames[N] = None
            active = None
            erases += 1
        else:
            raise ValueError("unknown opcode")
    require(frames == list(final_frames) + [None], "final frame boundary")
    require(active is None and not any(rows[N]), "final private zero")
    return rows, {
        "records": len(records), "unit_ADDs": adds, "COPY": copies, "ERASE": erases,
        "paid_queries": sum(hist.values()), "histogram": dict(sorted(hist.items())),
        "rank_mass": sum(r*n for r,n in hist.items()), "row_l1_peak": peak_l1,
        "positive_majorant_peak": peak_majorant, "coefficient_peak": peak_coefficient,
        "no_MOVE_inside_active_COPY": True}, captures


def build(records, strict_integer):
    retired = {53, 20255, 20256, 23408, 23409, 33620}
    retimed = {23405, 23406, 23407, 23515, 24189, 24190, 24515}
    identities = {
        53: [1,413,469,-1,0,30], 20255:[0,469,0,52,1,0], 20256:[1,469,50,1,52,2],
        23408:[0,469,52,517,6,0], 23409:[1,413,469,1,517,2],
        33619:[0,469,517,1,1,32], 33620:[1,469,50,-1,1,32],
        23865:[1,178,660,1,0,3], 23889:[3,476,660,515,0,3],
        24189:[0,178,0,52,1,0],
        24190:[1,178,50,1,52,4], 24515:[0,50,52,509,3,0]}
    for i, expected in identities.items():
        require(records[i] == expected, "literal source identity " + str(i))
    d = {h: Counter() for h in (391,413,444,469)}
    cut = max(i for i,r in enumerate(records) if r[5] == 10)
    for op, dest, source, coefficient, _, section in records:
        if op == 1 and section == 10 and source in d:
            d[source][dest] += coefficient
    correction = d[469].copy()
    for h, sign in ((413,-1),(444,1),(391,1)):
        for dest, coefficient in d[h].items():
            correction[dest] += sign*coefficient
    correction = {dest:c for dest,c in sorted(correction.items()) if c}
    require(set(correction.values()) == {2} and len(correction) == 51,
            "integer zero-frame compensation formula")
    result = []
    deleted_comp = 0
    for i, r in enumerate(records):
        if i == 33619:
            result.append(("idle_469_to517",[0,469,0,517,7,32]))
        remove_comp = r[0] == 1 and r[2] == 469 and r[5] == 10
        deleted_comp += int(remove_comp)
        if i not in retired | retimed and not remove_comp:
            result.append((i, r))
        if i == cut and strict_integer:
            for dest,c in correction.items():
                result.extend((f"integer_comp_{dest}_{j}",[1,dest,469,1,0,10]) for j in range(c))
        if i == 23889:
            result.extend((j,records[j]) for j in (24189,24190,24515))
            result.append(("direct_x50",[1,413,50,1,509,2]))
            result.extend((j,records[j]) for j in (23405,23406,23407,23515))
    require(deleted_comp == 55, "deleted old compensation count")
    return result, correction


def itinerary_audit(baseline, candidate, geometry):
    def extract(records):
        paths = {i: [] for i in range(N)}
        for _, (op, d, before, after, rank, _) in records:
            if op == 0:
                paths[d].append([before, after, rank])
        return paths
    old, new = extract(baseline), extract(candidate)
    require(old[469] == [[0,52,1],[52,517,6],[517,1,1]], "original leaf itinerary")
    require(new[469] == [[0,517,7],[517,1,1]], "retired leaf itinerary")
    require(all(old[i] == new[i] for i in range(N) if i != 469),
            "every other ordered MOVE itinerary")
    require(geometry["start"][469] == 0 and geometry["final"][469] == 1,
            "same width-eight helper contract")
    return {"changed_MOVE_itineraries": [469], "old_helper469": old[469],
            "new_helper469": new[469], "helper469_width": 8,
            "ordinary_registers": N, "private_COPY_registers": 1,
            "new_registers": 0, "all_other_ordered_MOVE_itineraries_unchanged": True}


def main():
    authenticated = {}
    for name, digest in (("WORD","c46ccd7d3eedabc6a7efbb1a91ec13f2928bad8ee0bac57c6e593a092d13d96c"),
                         ("GEOMETRY","a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022")):
        data = (PACKAGE/"inputs"/(name+".json.gz")).read_bytes()
        require(sha256(data).hexdigest() == digest, name+" archive hash")
        authenticated[name] = json.loads(gzip.decompress(data))
    word, geometry = authenticated["WORD"], authenticated["GEOMETRY"]
    baseline = list(enumerate(word["records"]))
    start, finish = word["start"], word["final"]
    origin, baseline_invoice, _ = dense_replay(baseline,start,finish)
    zero = [[int(i == j) for j in range(N)] for i in range(N)] + [[0]*N]
    result = {
        "scope": "exact finite local stream operator, complete native partial-swap query invoice; no physical compiler or outer moment admission",
        "baseline": baseline_invoice, "variants": {}}
    for name, strict in (("Boolean",False),("integer",True)):
        candidate, correction = build(word["records"],strict)
        rows, invoice, captures = dense_replay(candidate,start,finish,snapshots=("direct_x50",23947))
        require(captures["direct_x50"]["private_source"] is None,
                "private COPY blank at retimed direct read")
        require(captures["direct_x50"]["rows"]["50"] == {"50":1},
                "original x50 at retimed direct read")
        require(captures["direct_x50"]["frames"]["50"] ==
                captures["direct_x50"]["frames"]["413"] == 509,
                "retimed direct read frame509")
        require(all(rows[i] == zero[i] for i in list(range(111))+list(range(222,N))),
                "exact integer source/helper restoration")
        require(all(all((x-y)%2 == 0 for x,y in zip(row, old)) for row,old in zip(rows,origin)),
                "complete Boolean endpoint")
        differences = {str(i):{str(j):x-y for j,(x,y) in enumerate(zip(row,old)) if x != y}
                       for i,(row,old) in enumerate(zip(rows,origin)) if row != old}
        if strict:
            require(rows == origin, "complete integer endpoint")
        else:
            require(differences == {str(i):{"469":-2} for i in correction},
                    "precise permitted even public lift change")
        undo = literal_inverse(candidate)
        inverse_rows, inverse_invoice, _ = dense_replay(undo,finish,start)
        require(dense_replay(undo,finish,start,rows)[0] == zero, "forward-inverse identity")
        require(dense_replay(candidate,start,finish,inverse_rows)[0] == zero, "inverse-forward identity")
        geometry_result = geometry_audit(geometry,candidate)
        result["variants"][name] = {
            "invoice": invoice, "inverse_invoice": inverse_invoice,
            "geometry": geometry_result, "integer_endpoint_equal": rows == origin,
            "itineraries": itinerary_audit(baseline,candidate,geometry),
            "integer_endpoint_differences": differences,
            "Boolean_endpoint_equal": True, "source_helper_integer_restoration": True,
            "inverse_both_orders": True, "captures": captures,
            "canonical_records_sha256": sha256(json.dumps([r for _,r in candidate],
                sort_keys=True,separators=(",",":")).encode()).hexdigest()}
    with localcontext() as ctx:
        ctx.prec = 60
        b = Decimal(1)/500
        gain = Decimal(64)**b * (1+Decimal(6)**(1-b)-Decimal(7)**(1-b))
        result["saving_at_m64_b_1_over_500_decimal_diagnostic"] = str(gain)
    result["all_parameter_saving"] = "m^b*(1+6^(1-b)-7^(1-b)) > 0 for m>0, 0<b<1"
    result["native_helper_469_endpoint"] = "decoded h469 restored; physical payload composed with D_I8"
    result["status"] = "PASS_NATIVE_FRAME_INVOICE_AUDIT"
    result["no_new_kappa"] = True
    print(json.dumps(result,sort_keys=True,separators=(",",":")))


if __name__ == "__main__":
    main()
