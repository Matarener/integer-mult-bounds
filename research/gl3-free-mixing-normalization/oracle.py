#!/usr/bin/env python3
"""Independent lossless free-mixing normalization oracle (standard library only).

All commands write JSON to stdout only. No command writes files. Matrices over
F2 use row masks: bit j of row i is entry (i,j), with zero-based indices.
Symbolic coefficients are finite F2 sums of noncommuting positive words.
"""
import argparse
import hashlib
import itertools
import json
import sys

SCHEMA = "independent-free-mixing-normalization-v1"


class ContractError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ContractError(message)


def identity(r):
    require(type(r) is int and r >= 1, "r must be a positive integer")
    return tuple(1 << i for i in range(r))


def binary_matrix(rows, r=None):
    require(isinstance(rows, (list, tuple)) and len(rows) > 0, "matrix must have rows")
    if r is None:
        r = len(rows)
    require(len(rows) == r, "matrix dimension mismatch")
    require(all(type(x) is int and 0 <= x < (1 << r) for x in rows), "invalid binary row mask")
    return tuple(rows)


def bmul(a, b):
    r = len(a)
    require(len(b) == r, "matrix product dimension mismatch")
    out = []
    for row in a:
        value = 0
        for j in range(r):
            if (row >> j) & 1:
                value ^= b[j]
        out.append(value)
    return tuple(out)


def inverse(a):
    r = len(a)
    left = list(binary_matrix(a))
    right = list(identity(r))
    for col in range(r):
        pivot = next((j for j in range(col, r) if (left[j] >> col) & 1), None)
        require(pivot is not None, "singular register frame")
        left[col], left[pivot] = left[pivot], left[col]
        right[col], right[pivot] = right[pivot], right[col]
        for row in range(r):
            if row != col and ((left[row] >> col) & 1):
                left[row] ^= left[col]
                right[row] ^= right[col]
    require(tuple(left) == identity(r), "inverse elimination failed")
    return tuple(right)


def gl_frames(r=3):
    require(type(r) is int and 1 <= r <= 3, "finite frame enumeration supports r=1,2,3")
    frames = []
    for rows in itertools.product(range(1 << r), repeat=r):
        try:
            inverse(rows)
        except ContractError:
            continue
        frames.append(rows)
    return frames


def dot(u, v):
    return bin(u & v).count("1") & 1


def outer(u, v, r):
    require(type(u) is int and type(v) is int and 0 < u < (1 << r) and 0 < v < (1 << r),
            "u and v must be nonzero r-bit vectors")
    require(dot(u, v) == 1, "rank-one idempotent requires v^T u = 1")
    return tuple(v if (u >> i) & 1 else 0 for i in range(r))


def column(a, j):
    return sum(((row >> j) & 1) << i for i, row in enumerate(a))


def from_columns(columns):
    r = len(columns)
    return tuple(sum(((columns[j] >> i) & 1) << j for j in range(r)) for i in range(r))


def span_extend(basis, vector):
    value = vector
    for pivot in sorted(basis, reverse=True):
        if (value >> pivot) & 1:
            value ^= basis[pivot]
    if value == 0:
        return False
    basis[value.bit_length() - 1] = value
    return True


def converse_basis(u, v, r):
    n = outer(u, v, r)
    columns = [u]
    basis = {}
    require(span_extend(basis, u), "u must be independent")
    for candidate in range(1, 1 << r):
        if dot(candidate, v) == 0 and span_extend(basis, candidate):
            columns.append(candidate)
    require(len(columns) == r, "kernel basis construction failed")
    q = from_columns(columns)
    p = inverse(q)
    ei = tuple(1 if i == 0 else 0 for i in range(r))
    require(bmul(bmul(q, ei), p) == n, "converse conjugacy failed")
    return {"basis_columns": columns, "basis": list(q), "frame": list(p), "coordinate": 0}


def factor_projector(n):
    r = len(n)
    n = binary_matrix(n)
    nonzero = next((i for i in range(r) if column(n, i)), None)
    require(nonzero is not None, "zero matrix is not rank one")
    u = column(n, nonzero)
    u_row = (u & -u).bit_length() - 1
    v = n[u_row]
    require(outer(u, v, r) == n, "projector must have rank one and be idempotent")
    return u, v


def conjugacy_table(r=3):
    rows = []
    projectors = {}
    for p in gl_frames(r):
        pinv = inverse(p)
        for coordinate in range(r):
            u, v = column(pinv, coordinate), p[coordinate]
            n = outer(u, v, r)
            ei = tuple((1 << coordinate) if i == coordinate else 0 for i in range(r))
            require(bmul(bmul(pinv, ei), p) == n, "conjugacy construction failed")
            converse = converse_basis(u, v, r)
            rows.append({"frame": list(p), "coordinate": coordinate,
                         "inverse": list(pinv), "projector": list(n), "u": u, "v": v,
                         "converse": converse})
            projectors[n] = {"projector": list(n), "u": u, "v": v, "converse": converse}
    all_rank_one = {outer(u, v, r) for u in range(1, 1 << r)
                    for v in range(1, 1 << r) if dot(u, v) == 1}
    require(set(projectors) == all_rank_one, "finite converse coverage failed")
    digest_input = [{"frame": x["frame"], "coordinate": x["coordinate"],
                     "projector": x["projector"]} for x in rows]
    digest = hashlib.sha256(json.dumps(digest_input, sort_keys=True,
                                      separators=(",", ":")).encode()).hexdigest()
    return {"schema": SCHEMA, "r": r,
            "encoding": "row masks; bit j of row i = entry (i,j); zero-based coordinate",
            "frame_count": len(gl_frames(r)), "conjugacy_count": len(rows),
            "projector_count": len(projectors), "binary_table_sha256": digest,
            "conjugacies": rows,
            "projectors": [projectors[n] for n in sorted(projectors)]}


ZERO = frozenset()
ONE = frozenset({()})


def padd(a, b):
    return a ^ b


def pmul(a, b):
    out = set()
    for x in a:
        for y in b:
            z = x + y
            if z in out:
                out.remove(z)
            else:
                out.add(z)
    return frozenset(out)


def address_word(value):
    require(isinstance(value, (list, tuple)) and all(isinstance(x, str) and x for x in value),
            "address must be a list of nonempty symbolic tokens")
    return tuple(value)


def smatrix(a):
    r = len(a)
    return tuple(tuple(ONE if (a[i] >> j) & 1 else ZERO for j in range(r)) for i in range(r))


def smul(a, b):
    r = len(a)
    require(len(b) == r, "symbolic matrix dimension mismatch")
    return tuple(tuple(sum_poly(pmul(a[i][k], b[k][j]) for k in range(r))
                       for j in range(r)) for i in range(r))


def sum_poly(values):
    out = ZERO
    for value in values:
        out = padd(out, value)
    return out


def paid_operator(n, address):
    r = len(n)
    delta = padd(frozenset({address_word(address)}), ONE)
    return tuple(tuple(padd(ONE if i == j else ZERO,
                            delta if ((n[i] >> j) & 1) else ZERO)
                       for j in range(r)) for i in range(r))


def augmentation(a):
    return tuple(sum((len(a[i][j]) & 1) << j for j in range(len(a))) for i in range(len(a)))


def polynomial_json(a):
    return [[[list(word) for word in sorted(poly)] for poly in row] for row in a]


def validate_paid_count(data, n):
    if "paid_count" in data:
        require(type(data["paid_count"]) is int and data["paid_count"] == n,
                "paid_count mismatch")


def normalize_raw(raw):
    require(isinstance(raw, dict), "raw word must be an object")
    r = raw.get("r")
    identity(r)
    paid = raw.get("paid")
    require(isinstance(paid, list), "paid must be a list")
    free = raw.get("free")
    require(isinstance(free, list) and len(free) == len(paid) + 1,
            "raw word requires n+1 free frames")
    validate_paid_count(raw, len(paid))
    free = [binary_matrix(w, r) for w in free]
    for w in free:
        inverse(w)
    cumulative = identity(r)
    factors = []
    for j, item in enumerate(paid):
        require(isinstance(item, dict), "paid operation must be an object")
        cumulative = bmul(free[j], cumulative)
        coordinate = item.get("coordinate")
        require(type(coordinate) is int and 0 <= coordinate < r, "invalid paid coordinate")
        addr = address_word(item.get("address"))
        u, v = column(inverse(cumulative), coordinate), cumulative[coordinate]
        factors.append({"projector": list(outer(u, v, r)), "u": u, "v": v,
                        "address": list(addr)})
    cumulative = bmul(free[-1], cumulative)
    return {"schema": SCHEMA, "r": r, "residual": list(cumulative),
            "factors": factors, "paid_count": len(paid)}


def normalized_factors(data):
    require(isinstance(data, dict), "normalized word must be an object")
    r = data.get("r")
    identity(r)
    factors = data.get("factors")
    require(isinstance(factors, list), "factors must be a list")
    validate_paid_count(data, len(factors))
    out = []
    for factor in factors:
        require(isinstance(factor, dict), "factor must be an object")
        n = binary_matrix(factor.get("projector"), r)
        u, v = factor_projector(n)
        if "u" in factor:
            require(type(factor["u"]) is int and factor["u"] == u, "u factor mismatch")
        if "v" in factor:
            require(type(factor["v"]) is int and factor["v"] == v, "v factor mismatch")
        out.append((n, u, v, address_word(factor.get("address"))))
    return r, out


def compile_normalized(data):
    r, factors = normalized_factors(data)
    residual = binary_matrix(data.get("residual", identity(r)), r)
    require(residual == identity(r), "net-free-I compilation requires identity residual")
    if not factors:
        return {"schema": SCHEMA, "r": r, "free": [list(identity(r))], "paid": [], "paid_count": 0}
    frames = [tuple(converse_basis(u, v, r)["frame"]) for _, u, v, _ in factors]
    free = [frames[0]]
    for previous, following in zip(frames, frames[1:]):
        free.append(bmul(following, inverse(previous)))
    free.append(inverse(frames[-1]))
    paid = [{"coordinate": 0, "address": list(addr)} for _, _, _, addr in factors]
    return {"schema": SCHEMA, "r": r, "free": [list(w) for w in free],
            "paid": paid, "paid_count": len(factors)}


def evaluate_raw(raw):
    normalized = normalize_raw(raw)  # validation only; evaluation below follows raw chronology
    r = raw["r"]
    value = smatrix(binary_matrix(raw["free"][0], r))
    for j, item in enumerate(raw["paid"]):
        ei = tuple((1 << item["coordinate"]) if i == item["coordinate"] else 0 for i in range(r))
        value = smul(paid_operator(ei, item["address"]), value)
        value = smul(smatrix(binary_matrix(raw["free"][j + 1], r)), value)
    require(augmentation(value) == tuple(normalized["residual"]), "raw augmentation identity failed")
    return value


def evaluate_normalized(data, include_residual=True):
    r, factors = normalized_factors(data)
    value = smatrix(identity(r))
    for n, _, _, addr in factors:
        value = smul(paid_operator(n, addr), value)
    residual = binary_matrix(data.get("residual", identity(r)), r)
    inverse(residual)
    if include_residual:
        value = smul(smatrix(residual), value)
    return value


def selftest():
    checks = []
    controls = []

    def check(name, condition):
        require(condition, "selftest failed: " + name)
        checks.append(name)

    def reject(name, operation):
        try:
            operation()
        except ContractError:
            controls.append({"name": name, "status": "rejected"})
            return
        raise ContractError("negative control was accepted: " + name)

    table = conjugacy_table(3)
    check("all_168_GL3_frames_and_504_conjugacies", table["frame_count"] == 168 and table["conjugacy_count"] == 504)
    check("all_28_rank_one_idempotents", table["projector_count"] == 28)
    check("all_frame_inverses_are_two_sided", all(bmul(p, inverse(p)) == identity(3) and bmul(inverse(p), p) == identity(3) for p in gl_frames(3)))
    check("all_projectors_are_nonzero_idempotents", all(any(p["projector"]) and bmul(tuple(p["projector"]), tuple(p["projector"])) == tuple(p["projector"]) for p in table["projectors"]))
    check("each_projector_has_18_conjugacies", all(sum(x["projector"] == p["projector"] for x in table["conjugacies"]) == 18 for p in table["projectors"]))
    raw_cases = []
    frames = gl_frames(3)
    for p in frames:
        for coordinate in range(3):
            raw_cases.append({"r": 3, "free": [list(p), list(inverse(p))],
                              "paid": [{"coordinate": coordinate, "address": ["a"]}]})
    # Independent deterministic bounded words; each free matrix is selected directly.
    for length in range(0, 7):
        for seed in range(24):
            free = [list(frames[(seed * 37 + j * 53 + length * 11) % len(frames)]) for j in range(length + 1)]
            paid = [{"coordinate": (seed + j) % 3, "address": ["a", "b", "c"][j % 3:j % 3 + 1]}
                    for j in range(length)]
            raw_cases.append({"r": 3, "free": free, "paid": paid, "paid_count": length})
    for raw in raw_cases:
        normal = normalize_raw(raw)
        require(evaluate_raw(raw) == evaluate_normalized(normal), "bounded raw conversion mismatch")
        require(len(raw["paid"]) == normal["paid_count"], "raw paid cost changed")
        require([x["address"] for x in raw["paid"]] == [x["address"] for x in normal["factors"]], "raw address order changed")
    check("672_full_symbolic_raw_conversions", len(raw_cases) == 672)
    normalized_cases = []
    ps = table["projectors"]
    for length in range(0, 7):
        for seed in range(28):
            factors = [{"projector": ps[(seed + 9 * j) % len(ps)]["projector"], "address": ["a", "b", "c"][j % 3:j % 3 + 1]}
                       for j in range(length)]
            normalized_cases.append({"r": 3, "factors": factors, "paid_count": length})
    for normal in normalized_cases:
        raw = compile_normalized(normal)
        require(evaluate_raw(raw) == evaluate_normalized(normal), "bounded converse mismatch")
        require(normalize_raw(raw)["residual"] == list(identity(3)), "converse net free matrix not I")
        require([x["address"] for x in normal["factors"]] == [x["address"] for x in raw["paid"]], "converse address order changed")
        require(len(raw["paid"]) == len(normal["factors"]), "converse paid cost changed")
    check("196_full_symbolic_converse_compilations", len(normalized_cases) == 196)
    zero = {"r": 3, "free": [list(identity(3))], "paid": []}
    check("n_zero_identity", normalize_raw(zero)["factors"] == [] and evaluate_raw(zero) == smatrix(identity(3)))
    zero_residual = {"r": 3, "free": [[3, 2, 4]], "paid": []}
    check("n_zero_nonidentity_residual_retained", evaluate_raw(zero_residual) == evaluate_normalized(normalize_raw(zero_residual)) and normalize_raw(zero_residual)["residual"] == [3, 2, 4])
    for length in range(5):
        raw = {"r": 1, "free": [[1]] * (length + 1),
               "paid": [{"coordinate": 0, "address": ["a" if j % 2 == 0 else "b"]} for j in range(length)]}
        check("r_one_length_" + str(length), evaluate_raw(raw) == evaluate_raw(compile_normalized(normalize_raw(raw))))
    # Direct diagonal target and a mixed intermediate state restored to a diagonal target.
    direct = {"r": 3, "free": [[1, 2, 4], [1, 2, 4]], "paid": [{"coordinate": 0, "address": ["a"]}]}
    shear = (3, 2, 4)
    dirty = {"r": 3, "free": [list(shear), list(identity(3)), list(shear)],
             "paid": [{"coordinate": 0, "address": ["a"]}, {"coordinate": 1, "address": ["a"]}]}
    dirty_target = ((frozenset({("a",)}), ZERO, ZERO),
                    (ZERO, frozenset({("a",)}), ZERO), (ZERO, ZERO, ONE))
    check("direct_positive", evaluate_raw(direct) == evaluate_normalized(normalize_raw(direct)))
    direct_target = ((frozenset({("a",)}), ZERO, ZERO), (ZERO, ONE, ZERO), (ZERO, ZERO, ONE))
    check("direct_hits_diagonal_augmentation_I_target", evaluate_raw(direct) == direct_target and augmentation(direct_target) == identity(3))
    check("dirty_restore_positive", evaluate_raw(dirty) == evaluate_normalized(normalize_raw(dirty)) and normalize_raw(dirty)["residual"] == list(identity(3)))
    check("dirty_restore_hits_diagonal_augmentation_I_target", evaluate_raw(dirty) == dirty_target and augmentation(dirty_target) == identity(3))
    identity_address = {"r": 3, "free": [list(shear), list(shear)],
                        "paid": [{"coordinate": 2, "address": []}]}
    check("identity_address_preserves_literal_paid_count", evaluate_raw(identity_address) == smatrix(identity(3)) and normalize_raw(identity_address)["paid_count"] == 1)
    witness = None
    for p in frames:
        if bmul(p, p) == identity(3):
            continue
        for coordinate in range(3):
            raw = {"r": 3, "free": [list(p), list(inverse(p))], "paid": [{"coordinate": coordinate, "address": ["a"]}]}
            normal = normalize_raw(raw)
            ei = tuple((1 << coordinate) if i == coordinate else 0 for i in range(3))
            wrong = bmul(bmul(p, ei), inverse(p))
            if wrong != tuple(normal["factors"][0]["projector"]):
                witness = {"raw": raw, "normalized": normal, "wrong_projector": list(wrong)}
                break
        if witness is not None:
            break
    require(witness is not None, "noninvolutory witness not found")
    wrong_data = dict(witness["normalized"])
    wrong_data["factors"] = [{"projector": witness["wrong_projector"], "address": ["a"]}]
    check("noninvolutory_register_frame_positive", evaluate_raw(witness["raw"]) == evaluate_normalized(witness["normalized"]))
    check("wrong_conjugate_inverse_detected", evaluate_raw(witness["raw"]) != evaluate_normalized(wrong_data))
    # Search a demonstrably noncommuting pair; absence would fail explicitly.
    order_witness = None
    for left in ps:
        for right in ps:
            candidate = {"r": 3, "factors": [{"projector": left["projector"], "address": ["a"]},
                                                {"projector": right["projector"], "address": ["b"]}]}
            reverse = {"r": 3, "factors": list(reversed(candidate["factors"]))}
            reorder = {"r": 3, "factors": [{"projector": left["projector"], "address": ["b"]},
                                              {"projector": right["projector"], "address": ["a"]}]}
            if evaluate_normalized(candidate) != evaluate_normalized(reverse) and evaluate_normalized(candidate) != evaluate_normalized(reorder):
                order_witness = {"normal": candidate, "reversed_factors": reverse, "reordered_addresses": reorder}
                break
        if order_witness is not None:
            break
    require(order_witness is not None, "order witness missing")
    check("wrong_factor_product_order_detected", evaluate_normalized(order_witness["normal"]) != evaluate_normalized(order_witness["reversed_factors"]))
    check("address_reorder_detected", evaluate_normalized(order_witness["normal"]) != evaluate_normalized(order_witness["reordered_addresses"]))
    residual_raw = {"r": 3, "free": [list(shear), list(identity(3))], "paid": [{"coordinate": 0, "address": ["a"]}]}
    residual_normal = normalize_raw(residual_raw)
    check("nonidentity_augmentation_residual_retained", augmentation(evaluate_raw(residual_raw)) == shear and evaluate_raw(residual_raw) != evaluate_normalized(residual_normal, False))
    reject("singular_frame", lambda: normalize_raw({"r": 3, "free": [[0, 2, 4]], "paid": []}))
    reject("vTu_zero", lambda: outer(1, 2, 3))
    reject("paid_count_mismatch", lambda: normalize_raw({"r": 3, "free": [[1, 2, 4]], "paid": [], "paid_count": 1}))
    reject("converse_nonidentity_residual", lambda: compile_normalized(residual_normal))
    reject("normalized_paid_count_mismatch", lambda: compile_normalized({"r": 3, "factors": [], "paid_count": 1}))
    reject("non_rank_one_projector", lambda: compile_normalized({"r": 3, "factors": [{"projector": [1, 2, 4], "address": ["a"]}]}))
    check("all_converse_bases_are_invertible", all(inverse(tuple(x["converse"]["basis"])) == tuple(x["converse"]["frame"]) for x in table["conjugacies"]))
    symbolic_controls = [{"name": name, "status": "detected_by_unequal_full_symbolic_operators"}
                         for name in ("wrong_conjugate_inverse", "wrong_factor_product_order",
                                      "omitted_nonidentity_residual", "address_reorder")]
    return {"schema": SCHEMA, "status": "PASS", "checks": checks, "negative_controls": controls + symbolic_controls,
            "raw_symbolic_cases": len(raw_cases), "converse_symbolic_cases": len(normalized_cases),
            "frame_count": table["frame_count"], "conjugacy_count": table["conjugacy_count"],
            "projector_count": table["projector_count"], "binary_table_sha256": table["binary_table_sha256"],
            "noninvolutory_witness": witness, "order_witness": order_witness,
            "residual_witness": {"raw": residual_raw, "normalized": residual_normal},
            "positive_examples": {"direct": direct, "dirty_restore": dirty,
                                  "dirty_restore_target": polynomial_json(dirty_target),
                                  "identity_address": identity_address},
            "scope": "one algebraic model reduction; finite tests corroborate the all-n proof"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("table", "selftest", "normalize", "compile", "evaluate-raw", "evaluate-normalized"))
    parser.add_argument("--r", type=int, default=3, help="finite table dimension (default: 3)")
    parser.add_argument("--input", default="-", help="JSON input file, or - for stdin; no file output")
    args = parser.parse_args(argv)
    try:
        if args.command == "table":
            result = conjugacy_table(args.r)
        elif args.command == "selftest":
            result = selftest()
        else:
            if args.input == "-":
                data = json.load(sys.stdin)
            else:
                with open(args.input, encoding="utf-8") as handle:
                    data = json.load(handle)
            if args.command == "normalize":
                result = normalize_raw(data)
            elif args.command == "compile":
                result = compile_normalized(data)
            elif args.command == "evaluate-raw":
                result = {"operator": polynomial_json(evaluate_raw(data))}
            else:
                result = {"operator": polynomial_json(evaluate_normalized(data))}
        json.dump(result, sys.stdout, sort_keys=True, indent=2)
        sys.stdout.write("\n")
        return 0
    except (ContractError, TypeError, KeyError, json.JSONDecodeError) as exc:
        json.dump({"schema": SCHEMA, "status": "ERROR", "message": str(exc)}, sys.stdout, sort_keys=True)
        sys.stdout.write("\n")
        return 2


if __name__ == "__main__":
    sys.exit(main())
