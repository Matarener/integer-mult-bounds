"""Compare encoded support extensions and persistent-field plans with finite oracles."""

from itertools import combinations
from composed_sources import active, require


def decode_pairs(tape, count, width):
    from check_support import inspect_count
    from router_metadata import Pairs, indices
    result = []
    table = Pairs(tape, count, width)
    for index in indices(count):
        with table.at(index) as (a, b):
            result.append((inspect_count(a), inspect_count(b)))
    return result


def extension_case(n, sources, targets):
    from cardinal_counts import Count
    from check_composed import selected_tape
    from check_support import inspect_count, no_decode
    from composed_plan import Positions, extend
    from router_metadata import Pairs
    from scratch_pool import ScratchPool
    from session import OuterScope, sealed_constructors
    counts = tuple(Count.literal(v) for v in (n, len(sources), max(1, (n-1).bit_length())))
    source, target = selected_tape(n, sources), selected_tape(n, targets)
    pool = ScratchPool(256)
    result = total = None
    try:
        with sealed_constructors(), OuterScope(pool).installed():
            try:
                result = pool.acquire()
                a, b = Positions(source, counts[1], counts[2]), Positions(target, counts[1], counts[2])
                with no_decode():
                    a.validate(counts[0])
                    b.validate(counts[0])
                    total = extend(a, b, counts[0], result)
                    Pairs(result, total, counts[2]).validate(counts[0])
                pairs = decode_pairs(result, total, counts[2])
                mapping = list(range(n))
                for old, new in pairs:
                    mapping[old] = new
                require(sorted(mapping) == list(range(n)) and all(mapping[s] == t for s, t in zip(sources, targets)),
                        "encoded extension realizes prescribed placement")
                require({s for s, _ in pairs} == set(sources) | set(targets)
                        and inspect_count(total) <= 2*len(sources), "complete support union, including fixed points")
                require(all(mapping[i] == i for i in set(range(n))-set(sources)-set(targets)),
                        "extension fixes complement")
            finally:
                if total is not None:
                    total.close()
                if result is not None:
                    result.clear()
            pool.empty()
        return pool.peak
    finally:
        source.clear()
        target.clear()
        for value in counts:
            value.close()


def plan_case(n, p, selected, policy="standard"):
    from cardinal_counts import Count
    from check_composed import selected_tape
    from check_support import inspect_count, no_decode
    from composed_plan import ExposurePlan
    from scratch_pool import ScratchPool
    from session import OuterScope, sealed_constructors
    positions = selected_tape(n, selected)
    inputs = tuple(Count.literal(v) for v in (n, p, len(selected), max(1, (n-1).bit_length())))
    pool = ScratchPool(256)
    plan = None
    try:
        with sealed_constructors(), OuterScope(pool).installed():
            try:
                with no_decode():
                    plan = ExposurePlan(*inputs, pool.acquire, policy)
                    plan.compile(positions)
                fields = {name: inspect_count(value) for name, value in plan.fields.items()}
                result = dict(mode=plan.mode, fields=fields)
                if plan.mode == "composed":
                    forward = decode_pairs(plan.forward, plan.count, plan.prefix_width)
                    inverse = decode_pairs(plan.inverse, plan.count, plan.prefix_width)
                    require(sorted((b, a) for a, b in forward) == inverse, "sorted inverse descriptor")
                    ell, U, K, N = (fields[key] for key in ("ell", "U", "K", "N"))
                    require(U >= ell and U+ell <= n
                            and not set(range(U, U+ell)) & (set(selected) | {ell+j*K for j in range(len(selected))}),
                            "actual untouched persistent record block")
                    current = list(range(n))
                    current[:ell], current[U:U+ell] = current[U:U+ell], current[:ell]
                    suffix, original_prefix = current[:ell], current[ell:]
                    prefix = original_prefix[:]
                    for old, new in forward:
                        prefix[new] = original_prefix[old]
                    require([prefix[j*K] for j in range(len(selected))] == list(selected),
                            "root selected coordinates hold the original support")
                    exposed = prefix[:]
                    for old, new in inverse:
                        prefix[new] = exposed[old]
                    require(prefix == original_prefix, "inverse restores complete prefix")
                    current = suffix+prefix
                    current[:ell], current[U:U+ell] = current[U:U+ell], current[:ell]
                    require(current == list(range(n)) and N == n-ell, "ungroup and restore original address interpretation")
                    result.update(forward=forward, inverse=inverse)
            finally:
                if plan is not None:
                    plan.close()
            pool.empty()
        result["peak"] = pool.peak
        return result
    finally:
        positions.clear()
        for value in inputs:
            value.close()


def run():
    count, peak = 0, 0
    for n in range(1, 5):
        for g in range(n+1):
            for sources in combinations(range(n), g):
                for targets in combinations(range(n), g):
                    peak = max(peak, extension_case(n, sources, targets))
                    count += 1
    cases = [plan_case(4, 2, (0,)), plan_case(3, 5, (0, 2)),
             plan_case(5, 5, (0, 1), "fixture-ell1")]
    require([case["mode"] for case in cases] == ["composed", "literal", "composed"],
            "production and fixture geometry decisions")
    require(cases[-1]["forward"] != cases[-1]["inverse"], "non-involutive exposure fixture")
    return dict(status="PASS_COMPOSED_ENCODED_METADATA", extensions=count, extension_peak=peak, cases=cases)
