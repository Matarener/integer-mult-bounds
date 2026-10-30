#!/usr/bin/env python3
"""Independent completion checks and a deterministic research receipt.
Prepared for SHIN09-git with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import permutations, product
import json
from pathlib import Path
from types import ModuleType

HERE = Path(__file__).resolve().parent
BOUND_FILES = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json",
               "bounds.py", "oracle.py", "verify.py", "benchmark.py", "test_mutations.py", "OVERLAP.json", "TIMINGS-FINAL.json",
               "compare_matching.py", "reference5001.py", "reference5001.md", "LICENSE")


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load_source(name):
    module = ModuleType(name)
    path = HERE / (name + ".py")
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


def digest(words):
    return sha256("".join("".join(map(str, word)) + "\n" for word in sorted(words)).encode()).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def prefix_nodes():
    def walk(word, points, highest):
        yield word, points, highest
        if len(word) == 11:
            return
        for label in range(min(highest + 1, 4) + 1):
            value = points[-1] ^ (1 << label)
            if value not in points:
                yield from walk(word + (label,), points + (value,), max(label, highest))
    yield from walk((), (0,), -1)


def independent_excess(points, mask):
    value = 0
    for bit in (0, 1):
        group = [x for x in points if sum((x >> j) & 1 for j in range(5) if mask >> j & 1) % 2 == bit]
        multiplicities = Counter(x ^ y for x in group for y in group if x != y)
        value += sum(count // 2 - 1 for count in multiplicities.values())
    return value


def literal_pair_envelope(points):
    """Separate ordered-route implementation of the original E2 formula."""
    remaining = 13 - len(points)
    last = points[-1]
    pool = {x for x in range(32) if x not in points
            and sum(v.bit_count() for v in (last ^ x, x)) <= remaining}
    supported = {a ^ b for a in points for b in points if a != b}
    supported.update(a ^ x for a in points for x in pool)
    checked = 0
    for x in pool:
        for y in pool:
            if x != y and sum(v.bit_count() for v in (last ^ x, x ^ y, y)) <= remaining:
                reflected = last ^ x ^ y
                need(reflected in points or reflected in pool, "reflected endpoint lemma")
                supported.add(x ^ y)
                checked += 1
    return tuple(sorted(pool)), sum(1 << z for z in supported), checked


def small_raw_controls(bounds, oracle):
    rows = []
    for n, length in ((3, 6), (4, 8)):
        simple = universal = checks = 0
        for word in product(range(n), repeat=length):
            state = 0
            for label in word:
                state ^= 1 << label
            if state:
                continue
            points, is_simple, is_universal = oracle.inspect(word, n)
            if not is_simple:
                continue
            simple += 1
            universal += is_universal
            actual = {a ^ b for a in points for b in points if a != b}
            for depth in range(length):
                prefix = points[:depth + 1]
                pool, mask = bounds.tail_envelope(prefix, n, length)
                need(set(points[depth + 1:]) <= set(pool), "small raw future containment")
                need(all(mask >> value & 1 for value in actual), "small raw pair containment")
                checks += 1
        rows.append({"n": n, "length": length, "raw_words": n ** length,
                     "simple_restored": simple, "universal": universal, "prefix_checks": checks})
    return rows


def semantic_controls(bounds, oracle):
    errors = 0
    for word, n, length, token in (
        ((0, 0), 5, 12, "simple"), ((True,), 5, 12, "label"),
        ((5,), 5, 12, "label"), ((-1,), 5, 12, "label"),
        ((), True, 12, "dimension"), ((), 6, 12, "dimension"),
        ((), 5, 11, "length"), (tuple(range(5)) * 3, 5, 12, "partial"),
    ):
        try:
            bounds.completion_bound(word, n, length)
        except ValueError as error:
            need(token in str(error), "wrong invalid-input rejection")
            errors += 1
        else:
            raise ValueError("invalid-input accepted")
    witness = tuple(map(int, "010201320"))
    one = bounds.completion_bound(witness, joint=False)
    two = bounds.completion_bound(witness, joint=True)
    need(not one["reject"] and two["reject"], "strict envelope improvement")
    need(two["future"] == (4, 10, 12, 16, 24) and two["missing"] == (20, 28), "literal missing-mask witness")
    words = []
    for tail in product(range(5), repeat=3):
        word = witness + tail
        if any(word.count(j) % 2 for j in range(5)):
            continue
        points, simple, universal = oracle.inspect(word)
        if simple:
            words.append({"word": "".join(map(str, word)), "universal": universal, "labels": len(set(word))})
    need([x["word"] for x in words] == ["010201320232", "010201320434"], "literal suffix enumeration")
    need(not any(x["universal"] for x in words), "witness universal suffix")
    permutations_checked = 0
    sharp = tuple(map(int, "012343234031"))
    for labels in permutations(range(5)):
        word = tuple(labels[i] for i in sharp)
        for depth in range(12):
            need(not bounds.completion_bound(word[:depth])["reject"], "coordinate-permuted positive witness")
            permutations_checked += 1
    p, simple, universal = oracle.inspect(tuple(map(int, "01021323")), 4)
    bit0 = sum(len(g) * (len(g) - 1) // 2 - len({a ^ b for a in g for b in g if a != b})
               for g in ([x for x in p if x & 1 == b] for b in (0, 1)))
    need(simple and universal and bit0 == 8 and 8 > 5, "credited bit-0 scope control")
    return {"invalid_inputs": errors, "strict_witness": {"prefix": "010201320", **two},
            "restored_simple_suffixes": words, "coordinate_permuted_prefixes": permutations_checked,
            "credited_low_weight_excess": bit0}


def calculate():
    sources = json.loads((HERE / "SOURCES.json").read_bytes())
    for row in sources["files"]:
        if "vendored_as" in row:
            need(sha256((HERE / row["vendored_as"]).read_bytes()).hexdigest() == row["sha256"], "frozen PR5001 bytes")
    bounds = load_source("bounds")
    oracle = load_source("oracle")
    matching = load_source("compare_matching")
    reference = load_source("reference5001")
    oracle_counts, reference_closed, reference_hits = oracle.census()
    modes = {}
    for mode in bounds.MODES:
        counts, closed, hits = bounds.search(mode)
        need(hits == reference_hits, "complete universal word set: " + mode)
        if mode == "none":
            need(closed == reference_closed, "independent simple closed word set")
        modes[mode] = {**counts, "universal_sha256": digest(hits)}
    need((len(reference_closed), len(reference_hits)) == (3695, 828), "credited census calibration")

    table = {}
    depths, rejections, extra_depths = Counter(), Counter(), Counter()
    additional, class_additional = [], []
    matching_comparisons = 0
    reflected_pairs = 0
    also_matching_rejected = []
    for word, points, highest in prefix_nodes():
        first, one = bounds.tail_envelope(points, joint=False)
        second, two = bounds.tail_envelope(points, joint=True)
        need(first == second and two & ~one == 0, "nested envelope")
        literal_pool, literal_support, pair_checks = literal_pair_envelope(points)
        need(second == literal_pool and two == literal_support, "simplified/literal pair envelope equality")
        reflected_pairs += pair_checks
        flags = {
            "remaining": bounds.remaining_reject(points, highest),
            "union": bounds.union_reject(points),
            "cap11": bounds.cap_reject(points),
            "one_vertex": len(first) < 12 - len(points) or one != (1 << 32) - 2,
            "two_vertex": len(second) < 12 - len(points) or two != (1 << 32) - 2,
        }
        lower = {mask: bounds.class_completion_lower(points, first, mask) for mask in bounds.MASKS}
        flags["class_lower"] = any(x is None or x > 11 for x in lower.values())
        matching_splits = []
        if word:
            for omitted in range(5):
                proposed = matching.splits(points, omitted)
                need(proposed == reference.feasible_splits(points, 5, 12, omitted), "literal PR5001 predicate equality")
                matching_splits.append(proposed)
                matching_comparisons += 1
        depths[len(word)] += 1
        for name, fired in flags.items():
            rejections[name] += fired
        if flags["two_vertex"] and not any(flags[name] for name in ("remaining", "union", "cap11", "one_vertex")):
            additional.append("".join(map(str, word)))
            extra_depths[len(word)] += 1
            if any(not values for values in matching_splits):
                also_matching_rejected.append("".join(map(str, word)))
        if flags["class_lower"] and not any(flags[name] for name in ("remaining", "union", "cap11", "one_vertex")):
            class_additional.append("".join(map(str, word)))
        table[word] = (first, two, flags, lower, matching_splits)

    completion_checks = universal_checks = 0
    matching_containment_checks = 0
    live = set()
    for word in reference_closed:
        points, simple, universal = oracle.inspect(word)
        need(simple, "oracle simple")
        actual = {a ^ b for a in points for b in points if a != b}
        final_excess = {mask: independent_excess(points, mask) for mask in bounds.MASKS}
        if universal:
            need(max(final_excess.values()) <= 11, "independent cap-11 domain check")
        for depth in range(12):
            key = word[:depth]
            future, possible, flags, lower, matching_splits = table[key]
            need(set(points[depth + 1:]) <= set(future), "actual future containment")
            need(all(possible >> value & 1 for value in actual), "actual pair containment")
            completion_checks += 1
            for omitted, splits in enumerate(matching_splits):
                mask = 31 ^ (1 << omitted)
                left = sum((x & mask).bit_count() % 2 == 0 for x in points)
                need((left, 12 - left) in splits, "matching actual split containment")
                matching_containment_checks += 1
            if universal:
                need(not any(flags.values()), "false prune of universal completion")
                need(all(lower[mask] is not None and lower[mask] <= final_excess[mask] for mask in bounds.MASKS), "excess completion lower bound")
                universal_checks += 1
                live.add(key)
    need(len(table) == 21640 and len(live) == 2427, "prefix coverage counts")
    need(len(additional) == 67 and not class_additional, "incremental bound classification")
    need(matching_comparisons == 108195 and not also_matching_rejected, "matching overlap classification")
    need(modes["one_vertex"]["entered"] == 7519 and modes["two_vertex"]["entered"] == 7326, "paired-envelope traversal counts")

    return {"schema": "five-label-prefix-completion/v1",
            "oracle": {**oracle_counts, "simple_closed_sha256": digest(reference_closed),
                       "universal_sha256": digest(reference_hits)},
            "prefixes": {"total": len(table), "by_depth": {str(k): v for k, v in depths.items()}, "live": len(live),
                         "literal_envelope_equalities": len(table), "reflected_ordered_pairs": reflected_pairs,
                         "closed_completion_checks": completion_checks,
                         "universal_completion_checks": universal_checks,
                         "predicate_rejections_on_full_domain": dict(rejections)},
            "modes": modes, "additional_joint_prefixes": additional,
            "matching_comparison": {"literal_predicate_comparisons": matching_comparisons,
                                    "actual_split_containment_checks": matching_containment_checks,
                                    "joint_strict_prefixes_also_matching_rejected": also_matching_rejected,
                                    "joint_strict_prefixes_passing_matching": len(additional)},
            "additional_by_depth": {str(k): v for k, v in extra_depths.items()}, "class_lower_additional": class_additional,
            "small_raw_controls": small_raw_controls(bounds, oracle),
            "controls": semantic_controls(bounds, oracle),
            "source_sha256": {name: sha256((HERE / name).read_bytes()).hexdigest() for name in BOUND_FILES}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-receipt", action="store_true", help="Explicit authoring output; no files are changed.")
    args = parser.parse_args()
    actual = calculate()
    if args.emit_receipt:
        print(json.dumps(actual, indent=2, sort_keys=True))
        return
    expected = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))
    need(canonical(actual) == canonical(expected), "complete deterministic receipt equality")
    for corrupt in (True, 827):
        changed = json.loads(canonical(actual))
        changed["oracle"]["simple_universal"] = corrupt
        need(canonical(changed) != canonical(expected), "typed receipt control")
    print("PASS_FIVE_LABEL_PREFIX_COMPLETION prefixes=21640 universal=828 joint_extra=67")


if __name__ == "__main__":
    main()

