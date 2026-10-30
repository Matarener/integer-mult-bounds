"""Exact two-occupied-bin swaps on the fixed selected T16 geometry.

The geometry and full-map auditor retain Josie Elliston's PR1091 credit.
This module constructs a new map; it does not admit a supplier.
"""

from collections import Counter, defaultdict
from copy import deepcopy

ROWS = 69_120
MAX_PAIR_CHECKS = 1_000_000
ROLE_KEYS = frozenset(("stage", "replica", "time", "helper", "width"))
PLACE_KEYS = ("owner_replica", "child", "port", "copy", "family")


def need(condition, message):
    if not condition:
        raise ValueError(message)


def bin_key(row):
    return row["owner_replica"], row["child"], row["port"]


def validate_rows(rows):
    need(isinstance(rows, list) and len(rows) == ROWS, "wrong role count")
    keys = ROLE_KEYS | set(PLACE_KEYS) | {"offset"}
    for row in rows:
        need(isinstance(row, dict) and row.keys() == keys, "wrong role fields")
        need(
            all(type(value) is int and 0 <= value < 100_000 for value in row.values()),
            "invalid role integer",
        )
        need(row["width"] in (4, 5, 7, 8, 9), "invalid helper width")


def exchange(rows, first, second):
    """Exchange two whole roles, then compact only their destination bins."""
    validate_rows(rows)
    need(
        0 <= first < ROWS and 0 <= second < ROWS and first != second, "bad role indices"
    )
    a, b = rows[first], rows[second]
    need(bin_key(a) != bin_key(b), "same-bin exchange")
    out = [dict(row) for row in rows]
    for index, target in ((first, b), (second, a)):
        out[index].update({key: target[key] for key in PLACE_KEYS})
    affected = {bin_key(a), bin_key(b)}
    groups = defaultdict(list)
    for index, row in enumerate(out):
        if bin_key(row) in affected:
            groups[bin_key(row)].append(index)
    for indices in groups.values():
        offset = 0
        for index in sorted(indices, key=lambda i: (out[i]["offset"], i)):
            out[index]["offset"] = offset
            offset += out[index]["width"]
    need(
        all(
            all(old[key] == new[key] for key in ROLE_KEYS)
            for old, new in zip(rows, out)
        ),
        "logical role changed",
    )
    return out


def state(rows, geometry, plan, auditor):
    validate_rows(rows)
    order = [tuple(item) for item in plan["order"]]
    spans, positions = auditor.windows(geometry, order)
    members, occupied = defaultdict(list), defaultdict(set)
    for index, row in enumerate(rows):
        members[bin_key(row)].append(index)
        occupied[row["time"]].add(row["family"])
    free = {
        key: geometry["rank"][key[1]] - sum(rows[i]["width"] for i in indices)
        for key, indices in members.items()
    }
    need(all(value >= 0 for value in free.values()), "overfilled source bin")
    return spans, positions, members, occupied, free


def legal_swap(a, b, geometry, spans, positions, occupied):
    for source, target in ((a, b), (b, a)):
        stage, replica = source["stage"], source["replica"]
        owner, child = target["owner_replica"], target["child"]
        lo, hi = spans[owner, child]
        if not lo < positions[stage, replica] < hi:
            return False, "window"
        pair = geometry["place"][child][0]
        if (owner, pair) == (replica, geometry["stage_pair"][stage]):
            return False, "active_pair"
        released = {source["family"]}
        if a["time"] == b["time"]:
            released.add(target["family"])
        if target["family"] in occupied[source["time"]] - released:
            return False, "family"
    return True, "legal"


def census(rows, geometry, plan, auditor):
    """Exhaust different-capacity two-role swaps that strictly improve every concave moment."""
    spans, positions, members, occupied, free = state(rows, geometry, plan, auditor)
    index = defaultdict(list)
    for key, indices in members.items():
        if 0 < free[key] < geometry["rank"][key[1]]:
            for i in indices:
                index[rows[i]["width"], free[key]].append(i)
    counts, winners = Counter(), []
    for (wa, fa), left in sorted(index.items()):
        for (wb, fb), right in sorted(index.items()):
            delta = wa - wb
            if delta <= 0 or fb < delta or fa + delta <= fb:
                continue
            counts["type_pairs"] += 1
            for i in left:
                for j in right:
                    a, b = rows[i], rows[j]
                    if geometry["rank"][a["child"]] == geometry["rank"][b["child"]]:
                        continue
                    counts["moment_improving_pairs"] += 1
                    need(
                        counts["moment_improving_pairs"] <= MAX_PAIR_CHECKS,
                        "pair budget exhausted",
                    )
                    legal, reason = legal_swap(
                        a, b, geometry, spans, positions, occupied
                    )
                    counts[reason] += 1
                    if legal:
                        winners.append([i, j])
    return {"counts": dict(sorted(counts.items())), "winners": sorted(winners)}


def idle_profile(rows, geometry, plan, auditor):
    spans, _, _, _, free = state(rows, geometry, plan, auditor)
    result = Counter()
    for owner, child in spans:
        for port in range(auditor.V):
            remainder = free.get((owner, child, port), geometry["rank"][child])
            if remainder:
                result[remainder] += 1
    return result


def derive_data(
    rows, plan, spec, audit, native_price, conservative_price, container_hash, charts
):
    """Regenerate the selected PLAN/SPEC shapes without changing their contract."""
    from decimal import Decimal, localcontext
    from fractions import Fraction

    plan, spec = deepcopy(plan), deepcopy(spec)
    profile = {str(k): v for k, v in sorted(audit["profile"].items())}
    plan.update(profile=profile, assignment_sha256=container_hash)
    plan["replica_lift"]["owners_file_sha256"] = container_hash
    import hashlib
    import json

    canonical = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
    plan["assignment_content_sha256"] = hashlib.sha256(canonical).hexdigest()

    def decimal(value):
        rational = Fraction(value)
        with localcontext() as context:
            context.prec = 70
            return str(Decimal(rational.numerator) / Decimal(rational.denominator))

    expected = spec["expected"]
    expected.update(
        complex_lower=native_price["endpoint"],
        conservative_complex_lower=conservative_price["endpoint"],
        kappa=native_price["kappa"],
        kappa_decimal=decimal(native_price["kappa"]),
        conservative_kappa_decimal=decimal(conservative_price["kappa"]),
        cross_replica_helper_roles=audit["cross_replica_roles"],
        idle_remainders=sum(audit["idle"].values()),
        idle_remainder_profile={str(k): v for k, v in sorted(audit["idle"].items())},
        global_profile=profile,
        actual_73column_sigmas=charts,
    )
    return plan, spec
