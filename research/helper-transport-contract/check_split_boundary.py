"""One nominated 21-field boundary, not a search over helpers or windows."""

import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import json
from pathlib import Path


W = (
    "research/coupled-helper-neutral-completion/capsule/workspace/"
    "swarm-provider-audit-sol-high-20261024/repository/research/"
    "native-rank8-helper-provider/WORD.json.gz"
)
C = "research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz"
PINS = {
    W: "7dc356001ed597ad6fc9fd3e0bc6ff7e3ec3a580a579a956827aa17fccfdd2dc",
    C: "7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05",
}
FIELDS = [18, 19, 39, 40, *range(288, 304)]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def span(vs):
    answer = {0}
    for v in vs:
        answer |= {x ^ v for x in answer}
    return frozenset(answer)


def clean(row):
    return {k: v for k, v in row.items() if v}


def row_add(rows, t, s, q):
    for j, v in rows[s].items():
        rows[t][j] = rows[t].get(j, Q(0)) + q * v
    rows[t] = clean(rows[t])


def local_event_roles(event):
    """Admit only the scalar/climb language used by this bounded contract."""
    need(isinstance(event, list) and event, "candidate event shape")
    if event[0] == "climb":
        need(
            len(event) == 6 and event[1] == "warp_retimed",
            "candidate climb representation",
        )
        roles = [event[2]]
    elif event[0] == "scalar":
        need(len(event) == 3, "candidate scalar representation")
        op = event[1]
        need(isinstance(op, list) and op, "candidate scalar opcode")
        if op[0] == "add":
            need(len(op) == 5, "candidate ADD representation")
            references = op[1:3]
        elif op[0] == "scale":
            need(len(op) == 4, "candidate SCALE representation")
            references = op[1:2]
        else:
            raise ValueError("unsupported candidate scalar opcode: " + str(op[0]))
        for ref in references:
            need(
                isinstance(ref, list) and len(ref) == 2 and ref[0] == "L",
                "candidate scalar requires local-field references",
            )
        roles = [ref[1] for ref in references]
    else:
        raise ValueError("unsupported candidate event: " + str(event[0]))
    need(
        all(type(role) is int or role == "S" for role in roles),
        "candidate field identifier",
    )
    return set(roles)


def entry_row(word, stop):
    # Reverse slice only the nominated output row, then replay its dependency
    # instructions; no global row census and no imported native interpreter.
    required = {300}
    selected = []
    for i in range(stop - 1, -1, -1):
        event = word[i]
        if (
            event[0] == "scalar"
            and event[1][1][0] == "L"
            and event[1][1][1] in required
        ):
            selected.append(i)
            if event[1][0] == "add":
                required.add(event[1][2][1])
        elif event[0] == "warp" and event[1][1] in required:
            raise ValueError("nominated entry row has an operator warp")
    rows = {i: {i: Q(1)} for i in required}
    for i in reversed(selected):
        op = word[i][1]
        t = op[1][1]
        if op[0] == "add":
            row_add(rows, t, op[2][1], Q(op[3], op[4]))
        elif op[0] == "scale":
            rows[t] = clean({j: Q(op[2], op[3]) * v for j, v in rows[t].items()})
        else:
            raise ValueError("unexpected entry-slice operation")
    return rows[300], sorted(selected), sorted(required)


def original_column(word, canonical, stop):
    column = [Q(i == 300) for i in range(len(canonical["start"]))]
    frames = canonical["start"].copy()
    for i, event in enumerate(word[:stop]):
        if event[0] == "scalar":
            op = event[1]
            t = op[1][1]
            if op[0] == "add":
                column[t] += Q(op[3], op[4]) * column[op[2][1]]
            elif op[0] == "scale":
                column[t] *= Q(op[2], op[3])
            else:
                raise ValueError("noninvertible prefix column event")
        elif event[0] == "climb":
            frames[event[2]] = event[4]
        elif event[0] == "warp":
            need(
                not column[event[1][1]],
                "original-h300 column touched by nontrivial warp",
            )
            frames[event[1][1]] = event[4]
    return [
        {
            "role": i,
            "coefficient": str(v),
            "frame": frames[i],
            "frame_basis": canonical["frames"][frames[i]],
        }
        for i, v in enumerate(column)
        if v
    ]


def execute_candidate(events, initial, final, expected, spaces, disjoint_events):
    current = dict(initial)
    rows = {f: {f: Q(1)} for f in initial}
    paid = Counter()
    skipped = []
    for event in events:
        roles = local_event_roles(event)
        if roles.isdisjoint(rows):
            skipped.append(event)
            continue
        need(roles <= rows.keys(), "candidate event crosses field closure")
        if event[0] == "climb":
            _, _, f, before, after, rank = event
            need(
                current[f] == before and spaces[before] < spaces[after],
                "candidate climb contact",
            )
            need(
                rank
                == len(spaces[after]).bit_length()
                - len(spaces[before]).bit_length(),
                "candidate paid rank",
            )
            current[f] = after
            paid[rank] += 1
        else:
            op = event[1]
            t = op[1][1]
            need(current[t] == event[2], "candidate receiver frame")
            if op[0] == "add":
                s = op[2][1]
                need(current[s] == event[2], "candidate sender frame")
                row_add(rows, t, s, Q(op[3], op[4]))
            else:
                q = Q(op[2], op[3])
                need(q, "candidate nonzero scale")
                rows[t] = clean({j: q * v for j, v in rows[t].items()})
    # Every skipped event must be one of the eight pinned, disjoint events in
    # its original order. A new disjoint event is not an admitted free action.
    need(skipped == disjoint_events, "candidate unchanged disjoint events")
    need(current == final, "candidate retirement/output frames")
    need(rows == expected, "candidate exact arbitrary-input endpoint")
    return paid


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo", type=Path, default=Path(__file__).resolve().parents[2]
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    docs = {}
    for path, digest in PINS.items():
        raw = (args.repo / path).read_bytes()
        need(sha256(raw).hexdigest() == digest, "source hash")
        docs[path] = json.loads(gzip.decompress(raw))
    need(docs[W]["direction"] == "backward", "direction")
    need(
        docs[W]["source_sha256"]
        == sha256(gzip.decompress((args.repo / C).read_bytes())).hexdigest(),
        "source payload binding",
    )
    canonical = docs[C]["canonical"]
    word = docs[W]["word"]
    spaces = [span(basis) for basis in canonical["frames"]]
    current = canonical["start"].copy()
    for event in word[:9044]:
        if event[0] == "climb":
            need(current[event[2]] == event[3], "prefix climb")
            current[event[2]] = event[4]
        elif event[0] == "warp":
            need(current[event[1][1]] == event[3], "prefix warp")
            current[event[1][1]] = event[4]

    rows = {f: {g: Q(f == g) for g in FIELDS} for f in FIELDS}
    entry_frames = {f: current[f] for f in FIELDS}
    paths = {f: [current[f]] for f in FIELDS}
    paid = Counter()
    disjoint_events = []
    disjoint_indices = []
    for index, event in enumerate(word[9044:9137], 9044):
        roles = local_event_roles(event)
        if roles.isdisjoint(rows):
            disjoint_events.append(event)
            disjoint_indices.append(index)
            continue
        need(roles <= rows.keys(), "source event crosses field closure")
        if event[0] == "climb":
            _, _, f, before, after, rank = event
            need(current[f] == before, "local climb")
            need(spaces[before] < spaces[after], "monotone path")
            current[f] = after
            paths[f].append(after)
            paid[rank] += 1
        else:
            op = event[1]
            f = op[1][1]
            need(current[f] == event[2], "receiver frame")
            if op[0] == "add":
                g = op[2][1]
                need(current[g] == event[2], "sender frame")
                q = Q(op[3], op[4])
                rows[f] = {j: x + q * rows[g][j] for j, x in rows[f].items()}
            else:
                q = Q(op[2], op[3])
                need(q != 0, "scale invertibility")
                rows[f] = {j: q * x for j, x in rows[f].items()}
    need(
        disjoint_indices == [9068, 9069, 9070, 9071, 9080, 9081, 9082, 9083]
        and set().union(*(local_event_roles(e) for e in disjoint_events))
        == {54, 55, 101, 102},
        "retained eight disjoint source events",
    )
    need(
        paths[300] == [0, 21, 430, 437] and paid == {1: 38},
        "retained nominated path and invoice",
    )
    # The nominated relabel-and-retire interface substitutes S for cut input x300
    # in every continuing row; old H300 is returned as its independent cut value.
    target = {
        str(f): {str(j): str(q) for j, q in row.items() if q and j != 300}
        for f, row in rows.items()
        if f != 300
    }
    for f, row in rows.items():
        if f != 300 and row[300]:
            target[str(f)]["S"] = str(row[300])
    target["S"] = {
        ("S" if j == 300 else str(j)): str(q)
        for j, q in rows[300].items()
        if q
    }
    target["300"] = {"300": "1"}
    modified = {str(f): path.copy() for f, path in paths.items()}
    modified["300"] = [0, 21, 430]
    modified["S"] = [430, 437]
    candidate_paid = Counter(
        len(canonical["frames"][v]) - len(canonical["frames"][u])
        for path in modified.values()
        for u, v in zip(path, path[1:])
    )
    need(candidate_paid == paid, "same paid invoice")
    bad = []
    for f, row in target.items():
        coefficient = Q(row.get("S", "0"))
        final = modified[f][-1]
        if coefficient and not spaces[430] <= spaces[final]:
            bad.append(
                {
                    "output": f,
                    "successor_coefficient": str(coefficient),
                    "exit_frame": final,
                    "exit_basis": canonical["frames"][final],
                    "missing_successor_direction": min(spaces[430] - spaces[final]),
                }
            )
    need(
        {item["output"] for item in bad} == {"299", "301"},
        "exact two blocked successors",
    )
    need(
        rows[301][300] == -1 and rows[299][300] == Q(-1, 2),
        "source witness coefficients",
    )
    # Optimistic graph test: shared-space stations, all chronological restrictions removed.
    edges = {
        (spaces[u], spaces[v])
        for path in modified.values()
        for u, v in zip(path, path[1:])
    }
    seen = {spaces[430]}
    while True:
        next_seen = seen | {v for u, v in edges if u in seen}
        if next_seen == seen:
            break
        seen = next_seen
    need(
        all(spaces[item["exit_frame"]] not in seen for item in bad),
        "reachability obstruction",
    )
    # Moving the birth to the old line removes this endpoint obstruction.
    # The literal local construction below verifies feasibility; original-target
    # and caller admission remain separate obligations.
    need(
        all(spaces[21] <= spaces[item["exit_frame"]] for item in bad),
        "line-birth contrast",
    )
    preloads = [
        [i, event]
        for i, event in enumerate(word[:9044])
        if event[0] == "scalar"
        and event[1][0] == "add"
        and event[1][1] == ["L", 300]
    ]
    spread = [
        [i, event]
        for i, event in enumerate(word[:9044])
        if event[0] == "scalar"
        and event[1][0] == "add"
        and event[1][2] == ["L", 300]
    ]
    need(len(preloads) == 32 and len(spread) == 7, "precondition and spread inventory")
    # Named line21 escape: retire old H300 immediately after its first climb,
    # then replace every subsequent reference to H300 by S born at line21.
    line_program = deepcopy(word[9044:9137])
    for event in line_program[1:]:
        if event[0] == "climb" and event[2] == 300:
            event[2] = "S"
        elif event[0] == "scalar":
            for ref in event[1]:
                if isinstance(ref, list) and ref == ["L", 300]:
                    ref[1] = "S"
    typed_target = {
        ("S" if f == "S" else int(f)): {
            ("S" if j == "S" else int(j)): Q(q) for j, q in row.items()
        }
        for f, row in target.items()
    }
    line_initial = {**entry_frames, "S": 21}
    line_final = {**{f: current[f] for f in FIELDS}, 300: 21, "S": 437}
    line_paid = execute_candidate(
        line_program, line_initial, line_final, typed_target, spaces, disjoint_events
    )
    need(line_paid == {1: 38}, "line21 unchanged invoice")
    # Retiring old H300 at430 instead duplicates the21->430 ascent. The same
    # exact row identity remains attainable, now at39 H1.
    duplicate_program = deepcopy(line_program)
    duplicate_program.insert(1, ["climb", "warp_retimed", 300, 21, 430, 1])
    duplicate_final = {**line_final, 300: 430}
    duplicate_paid = execute_candidate(
        duplicate_program,
        line_initial,
        duplicate_final,
        typed_target,
        spaces,
        disjoint_events,
    )
    need(duplicate_paid == {1: 39}, "duplicated ascent invoice")
    actual_row, slice_events, slice_fields = entry_row(word, 9044)
    expected_row = {
        300: Q(1), 113: Q(1, 2), 174: Q(-1, 2), 123: Q(-1, 2),
        163: Q(1, 2), 128: Q(1, 2), 221: Q(-1, 2), 135: Q(-1, 2),
        140: Q(-1, 2), 145: Q(-1, 2), 162: Q(-1, 2), 216: Q(1, 2),
        190: Q(1, 2), 203: Q(-1, 2), 183: Q(-1, 2), 194: Q(1, 2),
        205: Q(-1, 2),
    }
    need(
        actual_row == expected_row
        and len(slice_events) == 98
        and len(slice_fields) == 41,
        "actual original-input entry row",
    )
    support = original_column(word, canonical, 9044)
    expected_support = {
        18: Q(-1, 2), 40: Q(-1, 2), 288: Q(1, 2), 289: Q(-1, 2),
        290: Q(-1, 2), 291: Q(1, 2), 297: Q(1, 2), 299: Q(1, 2),
        300: Q(1), 301: Q(-1, 2), 303: Q(1, 2), 505: Q(-1, 4),
    }
    need(
        {item["role"]: Q(item["coefficient"]) for item in support}
        == expected_support,
        "original h300 coefficient support",
    )
    external = next(item for item in support if item["role"] == 505)
    need(
        external["frame"] == 0
        and 505 not in FIELDS
        and not spaces[21] <= spaces[0],
        "outside-field line-birth obstruction",
    )
    controls = []

    def rejected(name, fn):
        try:
            fn()
        except ValueError as exc:
            controls.append({"name": name, "rejected": True, "reason": str(exc)})
        else:
            raise ValueError("accepted semantic mutation: " + name)

    wrong_target = deepcopy(typed_target)
    wrong_target[301].pop("S")
    rejected(
        "drop required successor coefficient at output301",
        lambda: execute_candidate(
            line_program, line_initial, line_final, wrong_target, spaces, disjoint_events
        ),
    )
    leak = deepcopy(line_program)
    leak[1][1][2] = ["L", 300]
    rejected(
        "leave original h300 in first consumer subtraction",
        lambda: execute_candidate(
            leak, line_initial, line_final, typed_target, spaces, disjoint_events
        ),
    )
    rejected(
        "claim plane430 retirement for unmodified line21 program",
        lambda: execute_candidate(
            line_program,
            line_initial,
            duplicate_final,
            typed_target,
            spaces,
            disjoint_events,
        ),
    )
    rejected(
        "omit original helper paid first climb",
        lambda: execute_candidate(
            line_program[1:],
            line_initial,
            line_final,
            typed_target,
            spaces,
            disjoint_events,
        ),
    )
    rejected(
        "claim duplicated ascent has38 H1",
        lambda: need(duplicate_paid == {1: 38}, "actual invoice is39 H1"),
    )
    unsupported_warp = deepcopy(line_program)
    unsupported_warp.insert(1, ["warp", ["L", 300], 59, 21, 21])
    rejected(
        "insert unsupported warp on original helper",
        lambda: execute_candidate(
            unsupported_warp,
            line_initial,
            line_final,
            typed_target,
            spaces,
            disjoint_events,
        ),
    )
    result = {
        "status": "PASS_NOMINATED_HELPER300_SPLIT_BOUNDARIES",
        "interval": [9044, 9137],
        "source_pins": PINS,
        "fields": FIELDS,
        "new_field": "S",
        "successor_birth_frame": 430,
        "successor_birth_basis": canonical["frames"][430],
        "fixed_target_rows": target,
        "modified_paths": modified,
        "paid_profile": dict(candidate_paid),
        "blocked_outputs": bad,
        "retained_disjoint_event_indices": disjoint_indices,
        "prefix_helper300_preloads": preloads,
        "prefix_helper300_spread": spread,
        "line21_positive_control": {
            "old_helper_retirement": 21,
            "successor_birth": 21,
            "successor_exit": 437,
            "paid_profile": dict(line_paid),
            "program": line_program,
            "meaning": (
                "Exact local cut-variable relabeling; the entrance-pure pattern already "
                "identified by PR5472. Not original-helper target admission."
            ),
        },
        "line21_with_plane430_retirement": {
            "paid_profile": dict(duplicate_paid),
            "extra_ascent": [300, 21, 430, 1],
        },
        "actual_original_input_entry_row": {
            str(i): str(q) for i, q in actual_row.items()
        },
        "entry_row_slice_indices": slice_events,
        "entry_row_slice_roles": slice_fields,
        "original_h300_column_at_cut": support,
        "external_zero_frame_obstruction": external,
        "semantic_controls": controls,
        "scope": (
            "Only the explicit 21-field relabel-and-retire contract at event9137. "
            "Not a whole-word obstruction, not every successor handoff, and not a proof "
            "that retiring cut variable x300 earns original helper target credit."
        ),
        "argument": (
            "Every coefficient of S stays in frames containing its birth subspace. "
            "The required nonzero S coefficients at outputs299 and301 in frame419 "
            "cannot be created by any coframed scalar program and monotone ascents."
        ),
        "contrast": (
            "Birth at frame21 removes this endpoint obstruction, but is a changed "
            "earlier producer interface with its own paid/target bill."
        ),
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(
            result["status"]
            + " plane430=excluded line21=38H1 duplicate_ascent=39H1 controls="
            + str(len(controls))
        )


if __name__ == "__main__":
    main()
