#!/usr/bin/env python3
"""Fresh reconstruction: deferred original functions and nested dirty pools.

The October 21 pre-reset sources did not survive.  This is a newly specified
construction, not a reconstruction of those source bytes or historical counts.
Frozen October 20 implementations are imported read only.  Apache-2.0;
substantial OpenAI assistance, with predecessor attribution retained in README.
"""
from collections import Counter, defaultdict
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import argparse
import json
import platform
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FROZEN = ROOT / "research/kappa-function-composition/bit"
sys.path.insert(0, str(FROZEN))
import native_functions as N
import staged_continuation as S
C = N.C


def minimum_chains(patterns):
    """Exact minimum path cover of the strict reverse-inclusion DAG."""
    ps = sorted(patterns, key=lambda p: (-p.bit_count(), p))
    matched_right = {}

    def augment(i, seen):
        for j in range(i + 1, len(ps)):
            if j in seen or ps[i] & ps[j] != ps[j]:
                continue
            seen.add(j)
            if j not in matched_right or augment(matched_right[j], seen):
                matched_right[j] = i
                return True
        return False

    for i in range(len(ps)):
        augment(i, set())
    successor = {i: j for j, i in matched_right.items()}
    chains = []
    for i in range(len(ps)):
        if i in matched_right:
            continue
        chain = [ps[i]]
        while i in successor:
            i = successor[i]
            chain.append(ps[i])
        chains.append(chain)
    C.require(sorted(p for chain in chains for p in chain) == sorted(ps),
              "Chain cover dropped or duplicated a function")
    C.require(len(chains) == len(ps) - len(matched_right), "Wrong matching bound")
    return chains


def fresh_instance(q):
    targets = N.grid_targets()
    targets += [C.mask((0, 1, 2, *edge)) for edge in combinations(range(3, 9), 2)
                if C.mask((0, 1, 2, *edge)) not in targets]
    if q == 16:
        targets.append(C.mask((0, 1, 3, 5, 6)))
    C.require(q in (15, 16) and len(targets) == q, "Unsupported fresh fixture")
    forest = [N.old_grid_tree(), C.tree(range(8, 15))]
    if q == 16:
        forest.append((1 << 15, ()))
    g = N.instance(19, targets, forest, f"fresh_{q}_static")
    stages = {node: stage for stage, root in enumerate(forest)
              for node, _ in C.walk(root)}
    # Make the static comparison's original assignment compatible with the
    # frozen restored-original cut contract; this changes no helper count.
    helpers, queries = [], defaultdict(list)
    for item in g["patterns"]:
        nodes, pattern, pivot = item["nodes"], item["pattern"], item["pivot"]
        original = min(nodes, key=lambda node: (stages[node], -node.bit_count(), node))
        copies = []
        for node in nodes:
            if node == original:
                role = pivot
            else:
                role = g["V"] + q + len(helpers)
                helper = (role, pivot, node, pattern)
                helpers.append(helper)
                copies.append(helper)
            queries[node].append((role, pivot, pattern))
        item["copies"] = copies
        item["original_node"] = original
    g.update(helpers=helpers, queries=dict(queries), A=len(helpers),
             W=g["V"] + q + len(helpers))
    return g, stages


def pooled_instance(base):
    by_node = defaultdict(list)
    for _, _, node, pattern in base["helpers"]:
        by_node[node].append(pattern)
    pools = []
    for node, patterns in sorted(by_node.items()):
        for chain in minimum_chains(patterns):
            pools.append(dict(role=base["V"] + base["q"] + len(pools),
                              node=node, patterns=chain))
    g = dict(base, A=len(pools), W=base["V"] + base["q"] + len(pools),
             design=f"fresh_{base['q']}_deferred_nested_pools", pools=pools)
    return g


def events(g, sign, omit_cleanup=False, early_original_cleanup=False):
    V = g["V"]
    items = {item["pattern"]: item for item in g["patterns"]}
    for pool in g["pools"]:
        for target in C.bits(pool["node"]):
            yield "ADD", V + target, pool["role"], sign, "old_pool_compensation"
    # Original pivots remain aggregate functions until every pool is clean.
    for item in g["patterns"]:
        if len(item["nodes"]) == 1:
            continue
        pattern, pivot = item["pattern"], item["pivot"]
        for source in item["members"]:
            yield "MOVE", source, ("E", pattern)
        for source in item["members"][1:]:
            yield "ADD", pivot, source, 1, "original_function_gather"
            yield "MOVE", source, "I"
    for pool in g["pools"]:
        for pattern in pool["patterns"]:
            yield "MOVE", pool["role"], ("E", pattern)
            yield "ADD", pool["role"], items[pattern]["pivot"], 1, "nested_pool_acquire"
    node_pools = defaultdict(list)
    node_originals = defaultdict(list)
    for pool in g["pools"]:
        node_pools[pool["node"]].append(pool)
    for item in g["patterns"]:
        node_originals[item["original_node"]].append(item)

    def process(node):
        group, children = node
        leaves = C.bits(group)
        pivot = V + leaves[0]
        if node_pools[group] or node_originals[group]:
            for target in leaves[1:]:
                yield "ADD", V + target, pivot, -1, "output_precode"
            for target in leaves:
                yield "MOVE", V + target, ("E", group)
            for item in node_originals[group]:
                if len(item["nodes"]) == 1:
                    for source in item["members"]:
                        yield "MOVE", source, ("E", group)
                        yield "ADD", pivot, source, -sign, "single_use_original_read"
                        yield "MOVE", source, "I"
                else:
                    yield "MOVE", item["pivot"], ("E", group)
                    yield "ADD", pivot, item["pivot"], -sign, "original_function_read"
                    yield "MOVE", item["pivot"], "I"
            for pool in node_pools[group]:
                yield "MOVE", pool["role"], ("E", group)
                yield "ADD", pivot, pool["role"], -sign, "pooled_function_read"
                yield "MOVE", pool["role"], "I"
            for target in leaves[1:]:
                yield "ADD", V + target, pivot, 1, "output_decode"
        if children:
            for child in children:
                yield from process(child)
        else:
            yield "MOVE", pivot, ("E", group)
    for stage, root in enumerate(g["forest"]):
        yield from process(root)
        yield "CUT", stage
    for source in range(V):
        if source not in g["used"]:
            yield "MOVE", source, "I"

    def restore_originals():
        for item in reversed(g["patterns"]):
            if len(item["nodes"]) > 1:
                for source in reversed(item["members"][1:]):
                    yield "ADD", item["pivot"], source, -1, "original_function_restore"
    if early_original_cleanup:
        yield from restore_originals()
    if not omit_cleanup:
        for pool in reversed(g["pools"]):
            for pattern in reversed(pool["patterns"]):
                yield "ADD", pool["role"], items[pattern]["pivot"], -1, "nested_pool_restore"
    if not early_original_cleanup:
        yield from restore_originals()


def cut_audit(g, stages, sign):
    V, q, W = g["V"], g["q"], g["W"]
    rows = [{i: 1} for i in range(W)]
    frames = [("P", i) for i in range(V)] + ["zero"] * (W - V)
    output_stage = {t: stage for stage, root in enumerate(g["forest"])
                    for t in C.bits(root[0])}
    cuts = []
    for event in events(g, sign):
        if event[0] == "MOVE":
            frames[event[1]] = event[2]
        elif event[0] == "ADD":
            _, dst, src, coefficient, _ = event
            C.require(frames[dst] == frames[src], "Cut audit sees unequal-frame ADD")
            rows[dst] = C.add(rows[dst], rows[src], coefficient)
        else:
            stage = event[1]
            expected = [{i: 1} for i in range(W)]
            expected_frames = [("P", i) for i in range(V)] + ["zero"] * (W - V)
            for item in g["patterns"]:
                consumed = stages[item["original_node"]] <= stage
                if len(item["nodes"]) == 1:
                    if consumed:
                        for source in item["members"]:
                            expected_frames[source] = "I"
                else:
                    expected[item["pivot"]] = {r: 1 for r in item["members"]}
                    for source in item["members"]:
                        expected_frames[source] = "I"
                    if not consumed:
                        expected_frames[item["pivot"]] = ("E", item["pattern"])
            for target in range(q):
                if output_stage[target] <= stage:
                    for source, mask in enumerate(g["labels"]):
                        if (mask & g["targets"][target]).bit_count() == 2:
                            expected[V + target][source] = -sign
                    expected_frames[V + target] = ("E", 1 << target)
                else:
                    for pool in g["pools"]:
                        if pool["node"] >> target & 1:
                            expected[V + target][pool["role"]] = sign
            for pool in g["pools"]:
                for pattern in pool["patterns"]:
                    item = next(x for x in g["patterns"] if x["pattern"] == pattern)
                    for source in item["members"]:
                        expected[pool["role"]][source] = 1
                expected_frames[pool["role"]] = ("I" if stages[pool["node"]] <= stage
                                                  else ("E", pool["patterns"][-1]))
            C.require(rows == expected and frames == expected_frames,
                      "Fresh deferred original cut contract failed")
            cuts.append(dict(stage=stage, sign=sign,
                             completed_outputs=[t for t in range(q) if output_stage[t] <= stage],
                             complete_independent_input_columns=W,
                             original_aggregate_pivots=sum(len(x["nodes"]) > 1 for x in g["patterns"]),
                             ordinary_pool_states_retained=g["A"],
                             future_outputs_have_only_old_pool_compensation=True,
                             matrix_sha256=sha256(json.dumps([sorted(r.items()) for r in rows],
                                                           separators=(",", ":")).encode()).hexdigest(),
                             frame_sha256=sha256(json.dumps(frames, separators=(",", ":")).encode()).hexdigest(),
                             mismatching_coefficients=0))
    return cuts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path, default=HERE / "DEFERRED-RECONSTRUCTION.json")
    args = parser.parse_args()
    started = time.monotonic()
    checks, cuts, comparisons, fixtures, negatives = [], [], [], [], []
    for q in (15, 16):
        base, stages = fresh_instance(q)
        g = pooled_instance(base)
        baseline = N.replay_word(base, (e for e in S.staged_events(base, 1) if e[0] != "CUT"), 1)
        checks.append(baseline)
        for sign in (1, -1):
            result = N.replay_word(g, (e for e in events(g, sign) if e[0] != "CUT"), sign)
            checks.append(result)
            cuts.extend(cut_audit(g, stages, sign))
        for a in (Q(349, 200000), Q(1, 250)):
            comparisons.append(dict(outputs=q, **N.cost_difference(baseline["local_profile"],
                result["local_profile"], base["A"], g["A"], 19, a)))
        for control in ("omit_pool_cleanup", "original_cleanup_too_early"):
            opts = {"omit_cleanup": control == "omit_pool_cleanup",
                    "early_original_cleanup": control == "original_cleanup_too_early"}
            r = N.replay_word(g, (e for e in events(g, 1, **opts) if e[0] != "CUT"),
                              1, expect_failure=True)
            negatives.append(dict(control=control, outputs=q,
                                  wrong_coefficients=r["mismatching_coefficients"]))
        fixtures.append(dict(outputs=q, target_masks=g["targets"], forest=g["forest"],
                             patterns=[dict(pattern=x["pattern"], original_node=x["original_node"],
                                            members=x["members"], pivot=x["pivot"])
                                       for x in g["patterns"]],
                             pools=g["pools"], geometry=g["geometric_checks"]))
        print(json.dumps(dict(outputs=q, baseline_helpers=base["A"], helpers=g["A"],
                              baseline_ADDs=baseline["ADDs"], ADDs=result["ADDs"],
                              status="PASS")), flush=True)
    pins = N.pins(Path(__file__), Path(S.__file__))
    receipt = dict(schema="fresh-bit-deferred-original-nested-pools/1", status="PASS",
                   provenance="New post-reset construction; historical lost target/forest bytes were not recovered.",
                   coefficient_ring="Z", geometry_field="Q", checks=checks, cut_audits=cuts,
                   comparisons=comparisons, fixtures=fixtures, negative_controls=negatives,
                   source_sha256=pins, new_multiplication_kappa=False,
                   global_supplier_completed=False,
                   environment=dict(python=sys.version, platform=platform.platform()),
                   elapsed_seconds=time.monotonic() - started)
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n")


if __name__ == "__main__":
    main()
