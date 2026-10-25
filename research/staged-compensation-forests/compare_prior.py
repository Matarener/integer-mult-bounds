"""One fixed PR1080 recipe-transfer check; no optimization or search."""
import argparse
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def matrix(gates):
    result = {t: {} for t in range(112, 224)}
    for op, t, h, numerator, denominator, frame in gates:
        require(op == "add", "addition-only source")
        q = result[t].get(h, Q(0)) + Q(numerator, denominator)
        if q:
            result[t][h] = q
        else:
            result[t].pop(h, None)
    return result


def tariff(q):
    if not q:
        return 0
    d = q.denominator
    require(d & (d - 1) == 0, "dyadic coefficient")
    a = abs(q.numerator)
    return 3 + a.bit_length() - 1 + a.bit_count() + d.bit_length() - 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prior-word", type=Path, required=True)
    parser.add_argument("--prior-recipe", type=Path, required=True)
    parser.add_argument("--current-word", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(args.output.resolve() not in
            {args.prior_word.resolve(), args.prior_recipe.resolve(), args.current_word.resolve()},
            "output must not replace a frozen input")
    old_bytes = args.prior_word.read_bytes()
    old_payload = gzip.decompress(old_bytes)
    require(digest(old_payload) ==
            "24db880b7dab31e6af4eec8a1aba1bbbae29cd50d9a7b77cf0e9b571b3e5ae7c",
            "PR1080 original canonical word")
    current_bytes = args.current_word.read_bytes()
    require(digest(current_bytes) ==
            "735c540b1fe29d0ceeb4d2f304ec941e5f2bd3bc92bafc8cce2b4f9a67a3b653",
            "PR3605 source word")
    recipe_bytes = args.prior_recipe.read_bytes()
    require(digest(recipe_bytes) ==
            "d526804d9d627cbd850b0e54c3de9aadc74646e1a9b6befb577f42240720750a",
            "PR1080 frozen recipe")
    recipe = json.loads(recipe_bytes)
    old, current = json.loads(old_payload), json.loads(gzip.decompress(current_bytes))
    A, C = matrix(old["compensation"]), matrix(current["compensation"])
    old_support = set().union(*map(set, A.values()))
    new_support = set().union(*map(set, C.values()))
    require(len(old_support) == 216 and len(new_support) == 207, "support counts")
    require(all((4 * a).denominator == 1 for row in A.values() for a in row.values()),
            "prior quarter grid")
    eighths = [(t, h, str(q)) for t, row in C.items() for h, q in row.items()
               if (4 * q).denominator != 1]
    require(bool(eighths), "strict current eighth-grid witness")
    live = set(range(704)) - set(current["removed"])
    sources = set(recipe["sources"])
    helper_edges = recipe["helper_forest"]
    touched = {recipe["sources"][i] for c, p, s, depth in helper_edges for i in (c, p)}
    # This is deliberately the literal register-ID transfer. No mapping from
    # historical canonical identities to current raw helper roles is assumed.
    invalid = sorted(touched - live)
    nonzero = sorted(touched & set(map(int, current["start_extra"])))
    nonfull = sorted(touched & set(map(int, current["helper_final"])))
    require(invalid or nonzero or nonfull, "expected direct transfer obstruction")
    target_forest = recipe["target_forest"]
    D = {t: dict(row) for t, row in C.items()}
    for child, parent, sign, depth in target_forest:
        t, p = recipe["targets"][child], recipe["targets"][parent]
        for h in set(C[t]) | set(C[p]):
            q = C[t].get(h, Q(0)) - sign * C[p].get(h, Q(0))
            if q:
                D[t][h] = q
            else:
                D[t].pop(h, None)
    target_cost = 8 * len(target_forest) + sum(tariff(q) for row in D.values() for q in row.values())
    output = {
        "prior_pr": 1080,
        "prior_head": "803e080e181229a3af2196b7a13615c9d81ae10d",
        "prior_recipe_sha256": digest(recipe_bytes),
        "prior_word_compressed_sha256": digest(old_bytes),
        "prior_word_decoded_sha256": digest(old_payload),
        "prior_targets": 112, "prior_active_helpers": len(old_support),
        "prior_nonzeros": sum(map(len, A.values())),
        "prior_component_price": sum(tariff(q) for row in A.values() for q in row.values()),
        "current_targets": 112, "current_active_helpers": len(new_support),
        "current_nonzeros": sum(map(len, C.values())),
        "current_component_price": sum(tariff(q) for row in C.values() for q in row.values()),
        "prior_quarter_grid": True,
        "current_eighth_witnesses": sorted(eighths),
        "signed_permutation_equivalence_excluded_by_grid_and_support": True,
        "frozen_target_recipe_on_current_matrix_component_price": target_cost,
        "frozen_helper_recipe_literal_id_transfer": {
            "touched_helpers": sorted(touched),
            "unavailable_removed_helpers": invalid,
            "nonzero_entrance_helpers": nonzero,
            "nonfull_terminal_helpers": nonfull,
            "admitted_without_adapters_or_remapping": False,
        },
        "scope": "One frozen source/recipe comparison. No relabeling search, general basis-equivalence obstruction, paid wrapper transfer, or global circuit optimum.",
    }
    args.output.write_text(json.dumps(output, sort_keys=True, indent=2) + "\n")
    print("PASS_PR1080_FIXED_TRANSFER_CHECK", "target_recipe_price", target_cost,
          "unavailable", len(invalid), "nonzero", len(nonzero), "nonfull", len(nonfull))


if __name__ == "__main__":
    main()
