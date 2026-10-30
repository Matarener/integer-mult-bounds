#!/usr/bin/env python3
"""Independent idle scan of PR #4088's mixed fourth-entry fill.

The ordinary admission rebind keeps one width vector per orientation and adds
the shipped idle remainder unchanged. This verifier scans the literal rows
itself, then shows that rule cannot carry the scanned invoice.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
The alternating log/exp enclosure is reimplemented here; no PR #4088 module
is imported.
"""
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path
import gzip
import hashlib
import json
import math

HERE = Path(__file__).resolve().parent
SHA256 = {
    "inputs/DISPATCH.json": "5d6fa711d704a1b498e5fe066ea821c4fa0217463702e82a7ce5be9da4023e8a",
    "inputs/FILL.json.gz": "45f5bce58f2251b784b0ab89ca4657e0920515209810cfabd7e32d9a126e2db1",
    "inputs/FOUR-base.json.gz": "aecaddba48fdff6353a6511c3623346b05aa607e30103fb016604a2b1025ce95",
    "inputs/FOUR-extra.json.gz": "615093190aa5479034bb8acdd8925d7a910e082b84dec7df84b459b62421235a",
    "inputs/MIXED-DISPATCH.json": "7f3b4a82e556300e5cfa5f873a5b1975f5d1a10b494316289f6662941b8e39f2",
    "inputs/NATIVE-base.json.gz": "bfe0cc0badac6c6d18461ceea0b299162c0f280c05f81b63f11fcc06cf9180e6",
    "inputs/NATIVE-extra.json.gz": "c5eec94a64cecfd6b83de05619628ad4868e889d62a55b49973f09705cc60448",
    "inputs/ORDER.json": "743e74b538432e2b2045e754b0de9c18f36fc5039fdb8eb542177a898ec78e44",
    "inputs/PLAN.json.gz": "d566cfb87b71639d4138e1f89b543e2dd6a7772070226a2a14c799a6835bf21e",
    "inputs/PR4085-PROFILE.json": "610cd49ed71e684481182ee3c7e5d1686f6a376ef8c6e74e3c3615bbb842d841",
    "inputs/TEMPLATE.json.gz": "21297b20f1f2dc76eb9dd8124416068c3cb096bab9df17fa4da19bc68dfe082e",
    "inputs/THREE-base.json.gz": "df31495cff95a1e512da398f52841c6b5ade29067869b3d68b89d756a5641112",
    "inputs/THREE-extra.json.gz": "9a28f7ef91938c0866e408eb06e03eb5f8e727a00b44eb936ddd5ed48704bd4c",
    "vendor/rebind.py": "faf283eb4edd2e6a1ccb40b3cb3ba30ae54338eaf5ea0a10d84d11d7939502af",
}
CLAIMED_PROFILE = {1: 8060060, 2: 2310120, 3: 751813, 4: 327210, 5: 66425, 8: 25920, 48: 138492}
CLAIMED_IDLE = {3: 22783, 5: 1625, 48: 138492}
PREDECESSOR_PROFILE = {1: 8057880, 2: 2310120, 3: 748602, 4: 330480, 5: 66690, 8: 25920, 48: 138438}
PREDECESSOR_IDLE = {3: 22842, 5: 1890, 48: 138438}
IDLE_DELTA = {3: -59, 5: -265, 48: 54}
LOCAL_THREE = {1: 2487, 2: 713, 3: 224, 4: 102, 5: 20, 8: 8}
LOCAL_FOUR = {1: 2489, 2: 713, 3: 227, 4: 99, 5: 20, 8: 8}
WIDTH_THREE = {5: 28, 6: 18, 7: 56, 8: 93, 9: 213}
WIDTH_FOUR = {5: 28, 6: 18, 7: 57, 8: 92, 9: 213}
CLAIMED_LOWER = Q("0.001730979115670792472760")
CLAIMED_UPPER = Q("0.001730979115670792472761")
PREDECESSOR_LOWER = Q("0.001730970419199163702738")
PREDECESSOR_UPPER = Q("0.001730970419199163702739")
PARENT_RANK = 73
REPLICAS = 360
LIVE_FAMILIES = 896
FULL = [1 << j for j in range(9)]


def need(ok, why):
    if not ok:
        raise ValueError(why)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    raw = path.read_bytes()
    if path.suffix == ".gz":
        raw = gzip.decompress(raw)
    return json.loads(raw)


def f2_rank(vectors):
    pivots = {}
    for value in vectors:
        need(type(value) is int and 0 <= value < 512, "frame vector")
        while value:
            bit = value.bit_length() - 1
            if bit in pivots:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                break
    return len(pivots)


def helper_widths(word, origin):
    widths = []
    for register in origin:
        final = word["helper_final"].get(str(register), FULL)
        start = word["start_extra"].get(str(register), [])
        widths.append(f2_rank(final) - f2_rank(start))
    return widths


def windows_for(order, template, plan):
    clock = {tuple(call): time for time, call in enumerate(order)}
    need(len(order) == 9 * REPLICAS, "call count")
    need(set(clock) == {(stage, replica) for stage in range(9) for replica in range(REPLICAS)}, "complete order")
    need(all(clock[stage, replica] < clock[stage + 1, replica] for replica in range(REPLICAS) for stage in range(8)),
         "stage order")
    ranks = {}
    for child in template["idle_children"]:
        previous = ranks.get(child["child"])
        need(previous in (None, child["rank"]), "stable child rank")
        ranks[child["child"]] = child["rank"]
    pair_of_stage = {row["stage"]: row["pair"] for row in template["recipe"] if row["kind"] == "local"}
    family = {child: 2 * plan["pairs"][str(child)] + plan["sides"][str(child)] for child in ranks}
    windows = {}
    for replica in range(REPLICAS):
        touched = {}
        tick = None
        for event in template["execution_schedule"]:
            kind = event["kind"]
            if kind == "local_cover_sweep":
                tick = clock[event["stage"], replica]
                touched[pair_of_stage[event["stage"]]] = tick
            elif kind == "bridge":
                touched[event["src"]] = tick
                touched[event["dst"]] = tick
            elif kind == "idle_cover_sweep":
                for child in event["child_indices"]:
                    if child in ranks:
                        need((replica, child) not in windows, "duplicate owner child")
                        windows[replica, child] = (ranks[child], touched.get(event["pair"], -1), tick)
            else:
                need(kind in ("bank_padding_cover_sweep", "translate_every_live_family",
                              "terminal_Y_translations", "terminal"), "schedule kind")
    shared = {}
    for (replica, child), (_, low, high) in windows.items():
        shared.setdefault((replica, family[child]), []).append((low, high))
    for intervals in shared.values():
        for index, (left_low, left_high) in enumerate(intervals):
            for right_low, right_high in intervals[index + 1:]:
                need(max(left_low, right_low) >= min(left_high, right_high), "same-family windows overlap")
    return clock, windows, family


def walk(rows, order, provider, windows, family, widths):
    need(len(rows) == 3240 * 408, "role coverage")
    used = {}
    for index, row in enumerate(rows):
        need(len(row) == 6 and all(type(value) is int for value in row), "integer row")
        time, helper, replica, child, port, offset = row
        need(time == index // 408 and helper == index % 408, "row identity")
        if helper == 0:
            families = set()
        need((replica, child) in windows and 0 <= port < 112, "owner bin")
        capacity, low, high = windows[replica, child]
        need(low < time <= high, "chronology")
        family_key = (replica, family[child], port)
        need(family_key not in families, "same-call family")
        families.add(family_key)
        bin_key = (replica, child, port)
        prefix = used.get(bin_key, 0)
        need(offset == prefix, "compact offset")
        width = widths[provider[tuple(order[time])]][helper]
        need(prefix + width <= capacity, "capacity")
        used[bin_key] = prefix + width
    idle = Counter()
    for (replica, child), (capacity, _low, _high) in windows.items():
        for port in range(112):
            leftover = capacity - used.get((replica, child, port), 0)
            if leftover:
                idle[leftover] += 1
    return used, dict(sorted(idle.items()))


def assemble(order, provider, local, idle):
    profile = Counter(idle)
    for call in order:
        profile.update(local[provider[tuple(call)]])
    return dict(sorted(profile.items()))


def outward(low, high, digits):
    scale = 10 ** digits
    lower = (low.numerator * scale) // low.denominator
    upper = -((-high.numerator * scale) // high.denominator)
    return Q(lower, scale), Q(upper, scale)


@lru_cache(None)
def log_bounds(rank):
    need(type(rank) is int and 1 <= rank <= PARENT_RANK, "rank")

    def series(value):
        z = (value - 1) / (value + 1)
        terms = 120
        partial = 2 * sum((z ** (2 * j + 1) / Q(2 * j + 1) for j in range(terms)), Q())
        tail = 2 * z ** (2 * terms + 1) / (Q(2 * terms + 1) * (1 - z * z))
        return partial, partial + tail

    exponent = rank.bit_length() - 1
    low_unit, high_unit = series(Q(rank, 1 << exponent))
    low_two, high_two = series(Q(2))
    return outward(low_unit + exponent * low_two, high_unit + exponent * high_two, 80)


def exp_minus_bounds(low, high):
    need(0 <= low <= high < 1, "exponent range")

    def partial(value, degree):
        return sum(((-value) ** j / Q(math.factorial(j)) for j in range(degree + 1)), Q())

    return partial(high, 25), partial(low, 24)


def moment_bounds(profile, exponent):
    need(0 < exponent < Q(1, 100), "moment exponent")
    low = high = Q()
    for rank, count in profile.items():
        need(type(count) is int, "integer count")
        log_low, log_high = log_bounds(rank)
        factor_low, factor_high = exp_minus_bounds(exponent * log_low, exponent * log_high)
        power_low, power_high = rank * factor_low, rank * factor_high
        low += count * (power_low if count >= 0 else power_high)
        high += count * (power_high if count >= 0 else power_low)
    return outward(low, high, 60)


def signed(profile):
    total = dict(profile)
    total[PARENT_RANK] = total.get(PARENT_RANK, 0) - LIVE_FAMILIES * REPLICAS
    return total


def certify(profile, lower, upper):
    low_moment = moment_bounds(signed(profile), lower)
    high_moment = moment_bounds(signed(profile), upper)
    need(low_moment[1] < 0 < high_moment[0], "moment signs")
    return low_moment, high_moment


def root_bracket(profile, low, high, steps):
    for _ in range(steps):
        mid = (low + high) / 2
        moment_low, moment_high = moment_bounds(signed(profile), mid)
        if moment_high < 0:
            low = mid
        elif moment_low > 0:
            high = mid
        else:
            raise ValueError("moment enclosure too wide to isolate the frozen-idle root")
    return low, high


def reject(label, function, controls):
    try:
        function()
    except ValueError:
        controls.append(label)
        return
    raise ValueError("mutation was accepted: " + label)


def main():
    for relative, digest in SHA256.items():
        need(sha256(HERE / relative) == digest, "pinned bytes " + relative)
    rebind = (HERE / "vendor/rebind.py").read_text(encoding="utf-8")
    need("locs = {'gauge44': loc_g, 'extra': loc_e}" in rebind, "two-provider rebind")
    need("unchanged idle remainder" in rebind, "rebind docstring")
    need("CONSTRUCTION.json')['idle']" in rebind, "shipped idle source")
    need("c['widths'] = widths" in rebind, "uniform width stamp")
    need("n * v" in rebind, "one local profile times the call count")

    order = read_json(HERE / "inputs/ORDER.json")
    template = read_json(HERE / "inputs/TEMPLATE.json.gz")
    plan = read_json(HERE / "inputs/PLAN.json.gz")
    clock, windows, family = windows_for(order, template, plan)
    need(len(windows) == 18 * REPLICAS, "owner windows")
    old_dispatch = read_json(HERE / "inputs/DISPATCH.json")
    published = read_json(HERE / "inputs/MIXED-DISPATCH.json")
    mixed = [[stage, replica, provider + ("-four" if (109 * clock[stage, replica]) % 324 < 109 else "")]
             for stage, replica, provider in old_dispatch]
    need(mixed == published, "published mixed dispatch")
    provider = {(stage, replica): tag for stage, replica, tag in mixed}
    counts = Counter(provider.values())
    need(counts == Counter({"extra": 1110, "gauge44": 1040, "extra-four": 562, "gauge44-four": 528}),
         "provider counts")
    need(sum(1 for tag in provider.values() if tag.endswith("-four")) == 1090, "fourth-call count")
    need(all(sum(1 for time in range(start, start + 324) if (109 * time) % 324 < 109) == 109
             for start in range(0, 3240, 324)), "ten exact periods")

    origin = read_json(HERE / "inputs/NATIVE-base.json.gz")["helper_origin"]
    need(origin == read_json(HERE / "inputs/NATIVE-extra.json.gz")["helper_origin"], "helper order")
    need(origin[367] == 601, "helper 601 index")
    local = {}
    widths = {}
    for kind, suffix, expected_local, expected_widths in (
            ("THREE", "", LOCAL_THREE, WIDTH_THREE),
            ("FOUR", "-four", LOCAL_FOUR, WIDTH_FOUR)):
        for tag, pid in (("base", "gauge44"), ("extra", "extra")):
            word = read_json(HERE / f"inputs/{kind}-{tag}.json.gz")
            removed = set(word["removed"])
            need(origin == sorted(set(range(224, 704)) - removed), "native helper domain")
            vector = helper_widths(word, origin)
            histogram = dict(sorted(Counter(vector).items()))
            report = {int(rank): count for rank, count in word["report"]["local_profile"].items()}
            need(histogram == expected_widths, "width inventory")
            need(report == expected_local, "declared local profile")
            need(sum(rank * count for rank, count in report.items()) == (5157 if kind == "THREE" else 5156),
                 "local rank mass")
            local[pid + suffix] = report
            widths[pid + suffix] = vector
    need(widths["gauge44"] == widths["extra"], "three-entry widths agree")
    need(widths["gauge44-four"] == widths["extra-four"], "four-entry widths agree")
    differences = [index for index, (left, right) in enumerate(zip(widths["gauge44"], widths["gauge44-four"]))
                   if left != right]
    need(differences == [367] and widths["gauge44"][367] == 8 and widths["gauge44-four"][367] == 7,
         "only helper 601 narrows")

    fill = read_json(HERE / "inputs/FILL.json.gz")
    need(fill["dispatch_overrides"] == [], "no hidden dispatch overrides")
    _used, idle = walk(fill["rows"], order, provider, windows, family, widths)
    profile = assemble(order, provider, local, idle)
    need(idle == CLAIMED_IDLE, "scanned idle")
    need(profile == CLAIMED_PROFILE, "scanned profile")
    need(sum(rank * count for rank, count in profile.items()) == 65088 * REPLICAS, "paid rank mass")
    predecessor = {int(rank): count for rank, count in read_json(HERE / "inputs/PR4085-PROFILE.json").items()}
    need(predecessor == PREDECESSOR_PROFILE, "predecessor profile pin")
    derived_idle = Counter()
    for rank, count in predecessor.items():
        derived_idle[rank] += count
    for rank, count in LOCAL_THREE.items():
        derived_idle[rank] -= 3240 * count
    need(dict(sorted((rank, count) for rank, count in derived_idle.items() if count)) == PREDECESSOR_IDLE,
         "predecessor idle")
    need({rank: CLAIMED_IDLE.get(rank, 0) - PREDECESSOR_IDLE.get(rank, 0) for rank in IDLE_DELTA} == IDLE_DELTA,
         "idle delta")
    need(sum(rank * count for rank, count in IDLE_DELTA.items()) == 1090, "idle rank-mass increase")
    need(1090 * (sum(rank * count for rank, count in LOCAL_FOUR.items())
                 - sum(rank * count for rank, count in LOCAL_THREE.items())) == -1090,
         "local rank-mass decrease")

    orientation_counts = Counter()
    rank_one_extra = Counter()
    width_split = Counter()
    for call, tag in provider.items():
        base = tag.removesuffix("-four")
        orientation_counts[base] += 1
        if tag.endswith("-four"):
            rank_one_extra[base] += 2
        width_split[base, widths[tag][367]] += 1
    need(orientation_counts == Counter({"gauge44": 1568, "extra": 1672}), "orientation calls")
    need(rank_one_extra["gauge44"] % orientation_counts["gauge44"] != 0, "gauge44 rank-1 indivisible")
    need(rank_one_extra["extra"] % orientation_counts["extra"] != 0, "extra rank-1 indivisible")
    need(width_split == Counter({("extra", 8): 1110, ("gauge44", 8): 1040,
                                 ("extra", 7): 562, ("gauge44", 7): 528}),
         "width split inside each orientation")

    local_sum = Counter()
    for call in order:
        local_sum.update(local[provider[tuple(call)]])
    frozen = Counter(local_sum)
    frozen.update(PREDECESSOR_IDLE)
    frozen_profile = dict(sorted(frozen.items()))
    need(frozen_profile != profile, "frozen idle misses the scan")
    gap = {rank: frozen_profile.get(rank, 0) - profile.get(rank, 0)
           for rank in set(frozen_profile) | set(profile)}
    need({rank: count for rank, count in gap.items() if count} == {3: 59, 5: 265, 48: -54},
         "frozen-idle gap is the negative idle delta")
    need(sum(rank * count for rank, count in profile.items())
         - sum(rank * count for rank, count in frozen_profile.items()) == 1090,
         "frozen invoice drops 1090 rank units")

    true_low, true_high = certify(profile, CLAIMED_LOWER, CLAIMED_UPPER)
    certify(predecessor, PREDECESSOR_LOWER, PREDECESSOR_UPPER)
    endpoint = CLAIMED_LOWER - Q(1, 10 ** 46) - Q(1, 10 ** 70)
    need(moment_bounds(signed(profile), endpoint)[1] < 0, "padded endpoint")
    need(endpoint - PREDECESSOR_UPPER > Q(869, 10 ** 11), "gain over the two-provider endpoint")
    frozen_low, frozen_high = root_bracket(frozen_profile, Q("0.001747"), Q("0.001748"), 24)
    need(frozen_low - CLAIMED_UPPER > Q(162, 10 ** 7), "frozen-idle root overstates the scan")
    need(frozen_high < Q("0.00174723"), "frozen-idle root upper")

    controls = []

    def wrong_threshold():
        other = [[stage, replica, tag + ("-four" if (108 * clock[stage, replica]) % 324 < 108 else "")]
                 for stage, replica, tag in old_dispatch]
        need(other == published, "wrong selector matched the published dispatch")

    def stamp_three_entry_width():
        altered = dict(provider)
        altered[tuple(order[0])] = altered[tuple(order[0])].removesuffix("-four")
        need(provider[tuple(order[0])].endswith("-four"), "control call is fourth-entry")
        walk(fill["rows"], order, altered, windows, family, widths)

    def frozen_at_claimed_bracket():
        certify(frozen_profile, CLAIMED_LOWER, CLAIMED_UPPER)

    def extra_rank_one():
        bad = dict(profile)
        bad[1] += 1
        certify(bad, CLAIMED_LOWER, CLAIMED_UPPER)

    def predecessor_at_claimed_bracket():
        certify(predecessor, CLAIMED_LOWER, CLAIMED_UPPER)

    reject("threshold-108-dispatch", wrong_threshold, controls)
    reject("three-entry-width-on-fourth-call", stamp_three_entry_width, controls)
    reject("frozen-idle-at-claimed-bracket", frozen_at_claimed_bracket, controls)
    reject("one-extra-rank-one", extra_rank_one, controls)
    reject("predecessor-profile-at-claimed-bracket", predecessor_at_claimed_bracket, controls)
    need(controls == ["threshold-108-dispatch", "three-entry-width-on-fourth-call",
                      "frozen-idle-at-claimed-bracket", "one-extra-rank-one",
                      "predecessor-profile-at-claimed-bracket"], "control list")

    print(json.dumps({
        "status": "PASS_MIXED_FOURTH_IDLE_REBIND_OBSTRUCTION",
        "scanned_profile": profile,
        "scanned_idle": idle,
        "idle_delta_from_predecessor": IDLE_DELTA,
        "helper_601_index": 367,
        "width_change": [8, 7],
        "claimed_root_bracket": [str(CLAIMED_LOWER), str(CLAIMED_UPPER)],
        "claimed_moment_signs": [str(true_low[1]), str(true_high[0])],
        "conditional_endpoint": str(endpoint),
        "frozen_idle_profile": frozen_profile,
        "frozen_idle_root_bracket": [str(frozen_low), str(frozen_high)],
        "frozen_idle_overstatement_above": str(frozen_low - CLAIMED_UPPER),
        "rejected_controls": controls,
        "selected_frontier_unchanged": True,
        "ordinary_release_rerun": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
