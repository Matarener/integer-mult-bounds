#!/usr/bin/env python3
"""Independent fixed-placement arithmetic audit; no producer module imports.

Apache-2.0. Prepared for Ross with substantial OpenAI Codex assistance.
The owner selection and source geometry remain credited to PR1043/2423/2653.
"""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction as Q
from hashlib import sha256
import gzip
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_REPO = Path("/Users/ross/git/math/integer-mult-bounds")
DEFAULT_SOURCE = Path("/Users/ross/git/math/.research-automation/runs/"
                      "kappa-3605-successor-20261018T0940Z/major-frontier/recursive")
PINS = {
    "source/BIT-OWNER-PRUNE.json": "8fdf672c9fbfd594991f2a59f9e586c6a0ae07ae55cadaf5e0cef73274cc1dc2",
    "source/BIT-PRUNE-AUDIT.json": "4efc043e71ba125bacfcdb1e2ed638dee685479846f70b2d863e889a5c075ec9",
    "source/BIT-NATIVE-CONTROLLER.json": "4d44059b0558c22d08f8d576dce8875cf1d725b759c57501b75b51cb8bcca603",
    "source/TWO-N-ALL-STAGES.md": "da4154af61bec16c0096e01c29fc29a5183a8ca02e9352d52f6e341b418ea85b",
    "repo/research/r438-rehost-projectors/SOURCES.json": "ce3b46e4f9fe278727e06c4166f7f3bfa423c30c5a54b538a8b0c7660a07549e",
    "repo/research/r438-rehost-projectors/verify.py": "30c4499d63d9cf8abd228ba4d0e6533f1aea244ec2e7e6bb57c086dc3dc0a82f",
    "repo/research/bit-r438-transport-rehost/verify_rehost.receipt.json": "06fa9322508aba3d8a5dc6469151cdfaa906b60559582b49c8b024428b158021",
    "repo/research/r438-native-rehost/CERTIFICATE.json": "6da8c593257c8440f0fe35488d941715d953d715e2e464ffdfffff7ed31eee9c",
    "repo/research/bit-r438-transport-rehost/words/r438-t154.json.gz": "a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022",
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def hist(obj):
    return Counter({int(r): n for r, n in obj.items()})


def mass(profile):
    return sum(r*n for r, n in profile.items())


def source_chronology():
    # Literal recipe in the pinned global_k.py, reconstructed here without exec.
    events = [("local", 0, 0)]
    for j in range(4):
        events.append(("local", 2*j+1, j))
        if j < 3:
            events.append(("bridge", j, j+1))
        events.append(("local", 2*j+2, j))
        if j < 3:
            events.append(("bridge", j, j+1))
    events.extend(("bridge", j+1, j) for j in (2, 1, 0))
    events.append(("exchange",))
    augmented, children = [], []
    levels = [-1]*4

    def advance(pair, target):
        level = levels[pair]
        axes = set(range(1 if level == -1 else 8+7*level, 8+7*target))
        child = {"idx": len(children), "pair": pair, "source_level": level,
                 "target_level": target, "rank": 7*(target-level),
                 "axes": sorted(axes), "deadline": len(augmented)}
        need(len(axes) == child["rank"], "pending rank")
        children.append(child)
        augmented.append(("idle", child["idx"], pair))
        levels[pair] = target

    for event in events:
        augmented.append(event)
        if event[0] == "local":
            _, stage, pair = event
            need(levels[pair] == stage-1, "source chronology")
            levels[pair] = stage
            if 1 <= stage <= 6:
                advance((stage+1)//2, stage)
            if stage == 8:
                for pair in range(4):
                    advance(pair, 8)
        elif event[0] == "bridge":
            need(levels[event[1]] == levels[event[2]], "bridge level")
        else:
            need(levels == [8]*4, "exchange level")
    need(len(augmented) == 29 and len(children) == 10, "chronology size")
    for child in children:
        eligible = []
        for begin, event in enumerate(augmented[:child["deadline"]]):
            if event[0] != "local" or event[2] == child["pair"]:
                continue
            touched = False
            for middle in augmented[begin+1:child["deadline"]]:
                if middle[0] == "local" and middle[2] == child["pair"]:
                    touched = True
                if middle[0] == "bridge" and child["pair"] in middle[1:]:
                    touched = True
            if not touched:
                eligible.append(event[1])
        child["eligible_stages"] = eligible
    return children


def expand_fixed_selection(selection, children):
    demands = defaultdict(list)
    seen = set()
    for child, width, stage, count in sorted(selection["stages"]):
        need((child, width, stage) not in seen, "duplicate demand")
        seen.add((child, width, stage))
        need(width == 8 and stage in children[child]["eligible_stages"]
             and type(count) is int and count > 0, "demand domain")
        demands[child].extend([stage]*count)
    counters = Counter()
    slots = []
    for child in children:
        identifier = child["idx"]
        patterns = sorted((widths, count) for c, widths, count in selection["patterns"]
                          if c == identifier)
        patterns.sort(key=lambda p: (-sum(p[0]), p[0]))
        copy = used = 0
        for widths, count in patterns:
            need(all(w == 8 for w in widths) and sum(widths) <= child["rank"],
                 "pattern domain")
            for _ in range(count):
                need(copy < 222, "copy count")
                for offset in range(0, sum(widths), 8):
                    stage = demands[identifier][used]
                    used += 1
                    slots.append((identifier, copy, offset, 8, stage, counters[stage]))
                    counters[stage] += 1
                copy += 1
        need(used == len(demands[identifier]), "unconsumed demand")
    need(counters == Counter({s: 438 for s in range(9)}), "all old helper roles")
    return slots


def audit_slots(slots, children, helpers, forced_rest=None):
    by_deadline = defaultdict(list)
    seen = set()
    for child, copy, offset, width, stage, helper in slots:
        need((stage, helper) not in seen, "duplicate helper role")
        seen.add((stage, helper))
        need(0 <= copy < 222 and width == 8
             and stage in children[child]["eligible_stages"], "owner domain")
        axes = set(children[child]["axes"][offset:offset+width])
        need(len(axes) == width, "slice extent")
        by_deadline[child, copy].append((axes, stage, helper))
    need(seen == {(s, h) for s in range(9) for h in range(helpers)}, "role coverage")
    remainders, signatures, rest_by_deadline = Counter(), set(), {}
    mask = lambda axes: sum(1 << x for x in axes)
    for child in children:
        target = set(child["axes"])
        for copy in range(222):
            parts = [axes for axes, _, _ in by_deadline[child["idx"], copy]]
            used = set()
            for axes in parts:
                need(axes <= target and not axes & used, "disjoint hosted factors")
                used |= axes
            rest = target-used
            if forced_rest and (child["idx"], copy) in forced_rest:
                rest = forced_rest[child["idx"], copy]
            need(not rest & used and rest | used == target, "complete pending partition")
            for part in parts+[rest]:
                need(part & set(range(1, 8)) in (set(), set(range(1, 8))),
                     "q-perp split")
            rest_by_deadline[child["idx"], copy] = rest
            remainders[len(rest)] += 1
            signatures.add((mask(target), tuple(mask(p) for p in parts+[rest])))
    rows = []
    occupied = {}
    for replica in range(32):
        for (child, copy), pieces in sorted(by_deadline.items()):
            side, port = divmod(copy, 111)
            family = replica*888+(2*children[child]["pair"]+side)*111+port
            for axes, stage, helper in pieces:
                need(not axes & occupied.get(family, set()), "physical cross-child overlap")
                occupied.setdefault(family, set()).update(axes)
                rows.append((replica, stage, helper, family, child, mask(axes)))
    need(len(rows) == 32*9*helpers, "physical role count")
    return {
        "idle": dict(sorted(remainders.items())),
        "owner_sha256": sha256(canonical(rows)).hexdigest(),
        "factorization_sha256": sha256(canonical(sorted(signatures))).hexdigest(),
        "physical_roles": len(rows),
    }, rest_by_deadline


def native_gauge_checks(lines):
    columns = 0
    witnesses = []
    for port, q in enumerate(lines):
        need(sum(x*x for x in q) == 4, "port norm")

        def address(vector):
            delta = sum(Q(q[i], 4)*(vector[8+i]-vector[i]) for i in range(8))
            shift = [q[i]*delta for i in range(8)]
            return tuple(vector[i]+shift[i] for i in range(8)) + \
                tuple(vector[8+i]-shift[i] for i in range(8))

        for j in range(16):
            vector = tuple(Q(i == j) for i in range(16))
            need(address(address(vector)) == vector, "two-gauge identity")
            columns += 1
        # E=I is a concrete invertible instance: N E^-1 N=I, while one N is not I.
        initial = tuple(Q(x, 2) for x in q)+(Q(0),)*8
        need(address(initial) != initial, "missing input gauge escaped")
        witnesses.append({"port": port, "q": q, "one_gauge_swaps_root_halves": True})
    need(len(lines) == 111, "actual punctured root count")
    return columns, witnesses


def run(repository, source):
    roots = {"repo": repository, "source": source}
    raw = {}
    for key, expected in PINS.items():
        prefix, name = key.split("/", 1)
        raw[key] = (roots[prefix]/name).read_bytes()
        need(sha256(raw[key]).hexdigest() == expected, "source pin: "+key)
    load = lambda key: json.loads(raw[key])
    old = load("source/BIT-OWNER-PRUNE.json")
    local = load("source/BIT-PRUNE-AUDIT.json")
    controller = load("source/BIT-NATIVE-CONTROLLER.json")
    upstream = load("repo/research/r438-rehost-projectors/SOURCES.json")
    for pin in upstream["files"]:
        if pin["usage"] == "input":
            need(sha256((repository/pin["path"]).read_bytes()).hexdigest() == pin["sha256"],
                 "upstream input pin: "+pin["path"])
    layout = load("repo/research/bit-r438-transport-rehost/verify_rehost.receipt.json")["placement"]
    certificate = load("repo/research/r438-native-rehost/CERTIFICATE.json")
    children = source_chronology()
    slots = expand_fixed_selection(layout["selection"], children)
    need(sha256(canonical(slots)).hexdigest() == layout["slot_list_sha256"], "old slot digest")
    before, old_rest = audit_slots(slots, children, 438)
    removed = [s for s in slots if 249 <= s[5] <= 257]
    retained = [s[:5]+(s[5]-(9 if s[5] > 257 else 0),)
                for s in slots if not 249 <= s[5] <= 257]
    after, new_rest = audit_slots(retained, children, 429)
    need(Counter(s[4] for s in removed) == Counter({s: 9 for s in range(9)}),
         "nine removed helpers at every stage")
    need([list(s) for s in removed] == old["deleted_slots_per_replica"], "deleted slot lineage")
    need(sha256(canonical(retained)).hexdigest() == old["retained_slots_sha256"],
         "retained slot digest")
    for data, name in ((before, "old_projector_audit"), (after, "new_projector_audit")):
        need(data["owner_sha256"] == old[name]["owner_projector_sha256"], "owner digest")
        need(data["factorization_sha256"] == old[name]["factorization_sha256"], "factor digest")
        need(hist(data["idle"]) == hist(old[name]["idle_per_replica_including_zero"]),
             "full idle histogram")
    freed = defaultdict(set)
    for child, copy, offset, width, _, _ in removed:
        freed[child, copy].update(children[child]["axes"][offset:offset+width])
    for key in old_rest:
        need(not old_rest[key] & freed[key] and new_rest[key] == old_rest[key] | freed[key],
             "returned physical complement")
    need(sum(len(x) for x in freed.values()) == 9*9*8 == 648, "returned idle rank")
    invoice = certificate["pipeline"]["candidate"]["hosted"]["invoice"]
    baseline = hist(invoice["bit_profile"])
    old_local = hist(certificate["local"]["candidate"]["profile"])
    new_local = hist(local["forward"]["profile"])
    need(new_local == hist(local["literal_inverse"]["profile"]), "local orientation profile")
    # Rebuild from the complete local and idle profiles, without subtracting a presumed total.
    complete = Counter({r: 288*n for r, n in new_local.items()})
    complete.update({r: 32*n for r, n in hist(after["idle"]).items() if r})
    baseline_rebuilt = Counter({r: 288*n for r, n in old_local.items()})
    baseline_rebuilt.update({r: 32*n for r, n in hist(before["idle"]).items() if r})
    need(baseline_rebuilt == baseline, "complete old profile")
    need(complete == hist(old["complete_pruned_local_and_idle_profile"]), "complete pruned profile")
    need(mass(old_local)-mass(new_local) == 132, "local saving")
    need(mass(baseline)-mass(complete) == 60*288, "net complete saving")
    need(controller["terminal_debt"]["conservative_rank_one_upper"] == 2*4*111 == 888,
         "fixed two-N terminal count")
    terminal = Counter(complete)
    terminal[1] += 888*32
    need(terminal == hist(old["pruned_plus_two_N_profile"]), "complete terminal profile")
    need(invoice["bit"]["live"] == 28416 and max(terminal) == 42, "stock and maximum child")
    m, stock = 64, 28416
    need(mass(terminal) == 1819488 and mass(terminal)-m*stock == 864, "terminal stock failure")
    need(all(type(r) is int and 0 < r <= m and n > 0 for r, n in terminal.items()),
         "all-alpha monotonicity domain")
    delta = Counter(complete)
    delta.subtract(baseline)
    need(all((r <= 7 and n <= 0) or n == 0 or (r >= 10 and n >= 0)
             for r, n in delta.items()), "rank-separated signed profile")
    need(mass(delta) == -17280, "uniform comparison mass")
    controls = []

    def rejects(name, action, required):
        try:
            action()
        except ValueError as error:
            need(required in str(error), "unrelated control failure: "+name)
            controls.append({"name": name, "reason": str(error)})
        else:
            raise ValueError("control accepted: "+name)

    changed = next(key for key in old_rest if new_rest[key] != old_rest[key])
    rejects("omit_returned_idle_axes",
            lambda: audit_slots(retained, children, 429, {changed: old_rest[changed]}),
            "complete pending partition")
    rejects("claim_132_net_saving",
            lambda: need(mass(baseline)-mass(complete) == 132*288, "returned idle rank omitted"),
            "returned idle rank omitted")
    rejects("omit_terminal_input_gauge_cost",
            lambda: need(mass(complete)+444*32 == mass(terminal), "one gauge cost omitted"),
            "one gauge cost omitted")
    rejects("allow_child_above_ambient",
            lambda: need(all(0 < r <= m for r in list(terminal)+[m+1]),
                         "moment domain violated"), "moment domain violated")
    word = json.loads(gzip.decompress(raw[
        "repo/research/bit-r438-transport-rehost/words/r438-t154.json.gz"]))
    gauge_columns, gauge_witnesses = native_gauge_checks(word["lines"])
    for banks in range(1, 1025):
        stages = 2*banks+1
        for ports in (1, 111):
            need((stages-1)*ports-3*stages-2*banks*ports == -3*stages,
                 "all-odd ledger identity")
    return {
        "status": "PASS_INDEPENDENT_B02_OWNER_RETURN_AND_TWO_N_MOMENT_BOUNDARY",
        "sources": PINS,
        "method": "No producer imports or function execution; independent chronology, set partitions, owner rows, complete histograms and exact address actions.",
        "source_children": children,
        "old_owner": before, "new_owner": after,
        "deleted_slots_per_replica": removed,
        "returned_idle_rank_per_replica": 648,
        "baseline_profile": dict(sorted(baseline.items())),
        "pruned_profile": dict(sorted(complete.items())),
        "pruned_plus_two_N_profile": dict(sorted(terminal.items())),
        "signed_pruned_minus_baseline_profile": dict(sorted(delta.items())),
        "local_mass_before_after": [mass(old_local), mass(new_local)],
        "complete_mass_before_after_terminal": [mass(baseline), mass(complete), mass(terminal)],
        "stock": stock, "ambient": m, "stock_rank_budget": m*stock,
        "terminal_excess_over_old_baseline": mass(terminal)-mass(baseline),
        "terminal_excess_over_stock_budget": mass(terminal)-m*stock,
        "zero_exponent_terminal_integer_budget_for_strict_pass": 860,
        "uniform_prefix_comparison": "For every alpha>=0, sum deltaH[r]*r*(64/r)^alpha <= -17280*8^alpha < 0.",
        "all_alpha_completion_obstruction": "For every alpha>=0, sum Hterminal[r]*r*(64/r)^alpha >= 1819488 > 64*28416.",
        "all_odd_identity_sanity_cases": 2048,
        "all_odd_written_proof": "(L-1)n-3L-2Bn=-3L for L=2B+1; a conditional ledger identity, not an emitted all-B construction.",
        "negative_controls": controls,
        "native_gauge_involution_basis_columns": gauge_columns,
        "native_one_gauge_omission_witnesses": gauge_witnesses,
        "limits": [
            "Native arbitrary-input projector factorization is justified by exact set partitions and the written orthogonal-projector law; no whole program is emitted.",
            "The 651-column integer/F2 local operator identity is inherited from published PR3645 and is not re-executed here; the pinned BIT-PRUNE-AUDIT receipt supplies the local paid profiles. The separate native_remainders.py binds the published word's frame events, ranks, COPY lifecycle and changed owner remainder operators, not its full integer/value identity.",
            "888 is the known construction's rank-one bill, not a universal terminal lower bound.",
            "444 is the fixed FULL-gather access bill, not a universal observer lower bound.",
            "No terminal recursive owner allocation, rounding, precision, physical tape or new kappa admission."
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=DEFAULT_REPO)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = run(args.repository, args.source)
    path = HERE/"OWNER-REVIEW.json"
    if args.write:
        need(not path.exists(), "refuse to overwrite review receipt")
        path.write_text(json.dumps(result, sort_keys=True, indent=2)+"\n")
    else:
        need(json.loads(path.read_bytes()) == json.loads(canonical(result)), "review receipt differs")
    print(result["status"])
    print("returned=648 mass=1791072 terminal=1819488 stock_excess=864 controls=4 gauge_witnesses=111")


if __name__ == "__main__":
    main()
