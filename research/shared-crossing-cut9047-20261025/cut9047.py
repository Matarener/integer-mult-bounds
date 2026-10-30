#!/usr/bin/env python3
"""One independent fixed-cut scalar-span qualification, no physical admission.

Reads frozen source as data; imports no predecessor/source evaluator. E alone
executes this scientific checker under the root-pinned guarded request.
Apache-2.0. Substantial OpenAI Codex assistance; native-word credit Cao Yifan,
literal semantics zxv and Cinna Davis; handoff credit GamingPuzzled/Joel Pulikkan.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path

SOURCE_SHA = "7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05"
DISCOVERY_SHA = "426a14360ea500b900bb4e13d6b292c781ffe0f1b54845d5776ce0b4b507f0cb"
CUT = 9047
FRAME = 21


def require(ok, message):
    if not ok:
        raise ValueError(message)


def ident(name):
    return {(name, ()): Q(1)}


def plus(row, source, coefficient=Q(1)):
    out = dict(row)
    for key, value in source.items():
        value = out.get(key, Q(0)) + coefficient * value
        if value:
            out[key] = value
        else:
            out.pop(key, None)
    return out


def scale(row, coefficient):
    require(coefficient != 0, "nonzero reversible scale")
    return {key: value * coefficient for key, value in row.items()}


def space(basis):
    points = {0}
    for vector in basis:
        points |= {x ^ vector for x in tuple(points)}
    require(len(points) == 2 ** len(basis), "independent ordered frame basis")
    return frozenset(points)


def serial(row):
    return [{"input": key[0], "warp_word": list(key[1]),
             "numerator": value.numerator, "denominator": value.denominator}
            for key, value in sorted(row.items())]


def rref_rows(rows):
    """Sparse rational echelon basis over (independent input, free word) keys."""
    basis = []
    for original in rows:
        row = dict(original)
        for pivot, vector in basis:
            if pivot in row:
                row = plus(row, vector, -row[pivot])
        if row:
            pivot = min(row)
            vector = scale(row, 1 / row[pivot])
            # Keep pivots ordered and eliminate new pivot from earlier vectors.
            basis = [(oldpivot, plus(oldvector, vector, -oldvector.get(pivot, Q(0))))
                     for oldpivot, oldvector in basis]
            basis.append((pivot, vector))
            basis.sort(key=lambda item: item[0])
    return basis


def membership(rows, target):
    basis = rref_rows(rows)
    residual = dict(target)
    for pivot, vector in basis:
        if pivot in residual:
            residual = plus(residual, vector, -residual[pivot])
    return {"member": not residual, "span_rank": len(basis),
            "augmented_rank": len(basis) + bool(residual),
            "pivots": [{"input": p[0], "warp_word": list(p[1])} for p, _ in basis],
            "exact_reduced_basis": [serial(vector) for _, vector in basis],
            "exact_residual": serial(residual)}


def event_apply(event, rows, current, spaces, dimensions, index):
    kind = event[0]
    if kind == "scalar":
        gate, frame = event[1:]
        action, target = gate[0], tuple(gate[1])
        if action == "clear":
            require(target[0] == "C", f"owned-only clear at {index}")
            rows[target], current[target] = {}, frame
            return
        require(current[target] == frame, f"target chart at {index}")
        if action in ("add", "copy"):
            source = tuple(gate[2])
            require(current[source] == frame, f"source chart at {index}")
            if action == "copy":
                require(target[0] == "C" and not rows[target], f"owned-zero COPY at {index}")
                rows[target] = dict(rows[source])
            else:
                require(source != target, f"distinct ADD owners at {index}")
                rows[target] = plus(rows[target], rows[source], Q(gate[3], gate[4]))
        else:
            require(action == "scale", f"known scalar at {index}")
            rows[target] = scale(rows[target], Q(gate[2], gate[3]))
    elif kind in ("climb", "center"):
        if kind == "climb":
            _, part, owner, old, new, rank = event
            role = ("L", owner)
            require(spaces[old] < spaces[new], f"ascending borrowed climb at {index}")
        else:
            _, owner, old, new, rank = event
            role = ("C", owner)
            require(spaces[old] < spaces[new] or spaces[new] < spaces[old], f"nested center at {index}")
        require(current[role] == old, f"paid source chart at {index}")
        require(rank == abs(dimensions[new] - dimensions[old]), f"paid rank at {index}")
        current[role] = new
    elif kind == "warp":
        _, owner, symbol, old, new = event
        role = tuple(owner)
        require(current[role] == old, f"warp source chart at {index}")
        out = {}
        for (variable, word), coefficient in rows[role].items():
            word2 = word[1:] if word and word[0] == -symbol else (symbol,) + word
            key = (variable, word2)
            out[key] = out.get(key, Q(0)) + coefficient
        rows[role] = {key: value for key, value in out.items() if value}
        current[role] = new
    else:
        require(kind in ("phase", "adapter", "residual_adapter"), f"known marker at {index}")


def controls():
    d, e1, e2, s1, s2, z, c = [ident(x) for x in ("D", "h1", "h2", "s1", "s2", "z", "c")]
    clean = [d, plus(e1, d), plus(e2, d), s1, s2]
    require(membership(clean, e1)["member"] and membership(clean, e2)["member"], "clean positive span control")
    # The successors' own arbitrary inputs are required positive columns.
    require(plus(clean[1], d, -1) == e1 and plus(clean[2], d, -1) == e2, "clean cancellation control")
    loaded1, loaded2 = plus(s1, d), plus(s2, d)
    require(plus(loaded1, d, -1) == s1 and plus(loaded2, d, -1) == s2, "independent successor positive endpoint")
    poisoned = [d, plus(e1, d), plus(plus(e2, d), z), s1, s2]
    require(not membership(poisoned, e2)["member"], "poison negative span control")
    require(plus(clean[2], plus(d, z), -1) != e2, "wrong-version residual control")
    correct_consumer = plus(plus(c, s2, -1), loaded2)
    require(correct_consumer == plus(c, d), "clean consumer positive control")
    require(plus(c, loaded2) != plus(c, d), "omitted presubtraction control")
    require(len(set(("s1", "s1"))) != 2 and len(set(("s1", "s2"))) == 2, "duplicate target inventory control")
    require(plus(plus(loaded2, z), d, -1) != s2, "dirty successor endpoint control")
    return {name: "PASS" for name in ("clean_positive_span", "independent_arbitrary_successors", "poison_negative_span", "wrong_version", "omitted_presubtraction", "duplicate_target_owner", "dirty_successor")}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    args = parser.parse_args()
    path = Path(args.source)
    raw = path.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == SOURCE_SHA, "frozen source compressed SHA256")
    decoded = gzip.decompress(raw)
    document = json.loads(decoded)
    require(document["discovery_word_sha256"] == DISCOVERY_SHA, "frozen source discovery metadata")
    canonical, program = document["canonical"], document["programs"]["forward"]
    require(canonical["h"] == 9 and canonical["v"] == 112 and len(canonical["start"]) == 632, "frozen domain")
    require(program[CUT] == ["scalar", ["add", ["L",301], ["L",19], 1,1], FRAME], "exact cut event")
    spaces = [space(basis) for basis in canonical["frames"]]
    dimensions = [len(basis) for basis in canonical["frames"]]
    rows = {("L", owner): ident(f"L{owner}") for owner in range(632)}
    current = {("L", owner): frame for owner, frame in enumerate(canonical["start"])}
    rows["C", 0], current["C", 0] = ident("C0"), None
    # Discover every owned entry touched by this prefix. Each begins arbitrary.
    for event in program[:CUT + 1]:
        if event[0] == "scalar":
            gate = event[1]
            for value in gate[1:]:
                if isinstance(value, list) and value[0] == "C":
                    role = tuple(value)
                    rows.setdefault(role, ident(f"C{role[1]}"))
                    current.setdefault(role, None)
        elif event[0] == "center":
            role = ("C", event[1])
            rows.setdefault(role, ident(f"C{role[1]}"))
            current.setdefault(role, None)
    entry_count = len(rows)
    kinds = Counter()
    for index, event in enumerate(program[:CUT + 1]):
        event_apply(event, rows, current, spaces, dimensions, index)
        kinds[event[0]] += 1
    selected = [rows["L", owner] for owner in (19, 300, 301)]
    require(all(current["L", owner] == FRAME for owner in (19, 300, 301)), "three selected cut frames")
    extended = selected + [ident("s300"), ident("s301")]
    span3 = {str(owner): membership(selected, ident(f"L{owner}")) for owner in (300, 301)}
    span5 = {str(owner): membership(extended, ident(f"L{owner}")) for owner in (300, 301)}
    require(all(span3[str(i)]["member"] == span5[str(i)]["member"] for i in (300, 301)), "independent successors cannot hide missing original column")
    coframed_roles = [role for role in sorted(rows) if current[role] == FRAME]
    coframed = [rows[role] for role in coframed_roles]
    span_all = {str(owner): membership(coframed, ident(f"L{owner}")) for owner in (300, 301)}
    span_all_successors = {str(owner): membership(coframed + [ident("s300"), ident("s301")], ident(f"L{owner}")) for owner in (300, 301)}
    require(all(span_all[str(i)]["member"] == span_all_successors[str(i)]["member"] for i in (300, 301)), "successor projection in all-coframed span")
    holders = {}
    for owner in (300, 301):
        variable = f"L{owner}"
        holders[str(owner)] = [{"owner": list(role), "frame": current[role],
                                "terms": serial({k: v for k, v in row.items() if k[0] == variable})}
                               for role, row in sorted(rows.items()) if any(k[0] == variable for k in row)]
    d_old = dict(rows["L", 19])
    # This fixed sixteen-event continuation only authenticates a distinct version.
    later_rows = {role: dict(row) for role, row in rows.items()}
    later_frames = dict(current)
    for index in range(CUT + 1, 9064):
        event_apply(program[index], later_rows, later_frames, spaces, dimensions, index)
    version_delta = plus(later_rows["L", 19], d_old, -1)
    require(bool(version_delta), "actual distinct historical version control")
    result = {
        "schema": "fixed-cut-scalar-span-qualification/v1",
        "scope": "necessary Q-linear recoverability at exact original forward cut9047/frame21; selected3+2 and every actually coframed owner+2; no changed cut, new operator coefficients, warp, transport, suffix, new word, inverse-transpose, phase, invoice or kappa admission",
        "source_compressed_sha256": SOURCE_SHA,
        "source_decompressed_sha256": hashlib.sha256(decoded).hexdigest(),
        "cut_index0_inclusive": CUT, "entry_independent_column_count": entry_count,
        "original_persistent_columns": 632, "new_successor_columns": ["s300", "s301"],
        "prefix_event_kinds": dict(sorted(kinds.items())),
        "all_coframed_owner_inventory": [list(role) for role in coframed_roles],
        "selected_rows": {str(i): serial(rows["L", i]) for i in (19, 300, 301)},
        "raw_four_edit_retiring_residues": {str(i): serial(plus(plus(rows["L", i], d_old, -1), ident(f"L{i}"), -1)) for i in (300, 301)},
        "span3": span3, "span5_with_independent_successors": span5,
        "span_all_coframed": span_all, "span_all_coframed_with_successors": span_all_successors,
        "successor_projection_lemma": "No existing row contains s300 or s301. In any rational combination yielding an old input column, coefficients of the distinct independent successor basis rows must vanish. Optional owned zero scratch adds the zero row and cannot enlarge either span.",
        "all_original_column_holders": holders,
        "actual_wrong_version_control": {"old_after_event": CUT, "new_after_event": 9063, "difference_new_minus_old": serial(version_delta), "rejects_substitution": bool(version_delta)},
        "controls": controls(),
        "qualification": "CUT_PREMISE_PASSES_NECESSARY_SPAN_ONLY" if all(x["member"] for x in span3.values()) else "REJECT_SCALAR_FIVE_OWNER_PURIFICATION_PREMISE",
        "all_coframed_qualification": "CUT_PREMISE_PASSES_NECESSARY_SPAN_ONLY" if all(x["member"] for x in span_all.values()) else "REJECT_ALL_ACTUALLY_COFRAMED_SCALAR_PURIFICATION_AT_THIS_CUT",
        "unestablished": ["arbitrary changed-cut ordinary-algebra designs", "legal realization/restoration even if span passes", "legal consumer presubtractions", "protected suffix outputs", "owned returns", "raw inverse transpose", "absolute phases", "complete profitable profile", "funded kappa"]
    }
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
