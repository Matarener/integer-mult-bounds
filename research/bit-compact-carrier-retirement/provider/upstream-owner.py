#!/usr/bin/env python3
"""Finite mixed-terminal owner admission; source constructions retain credit.

PR2423 supplies the R438 allocation; PR2653 supplies its pending-axis census;
PR589-five-helper-hosting supplies the full-cover owner convention. This script
changes only ordered widths, bin offsets and explicit terminal charts.
"""
import argparse
import ast
from collections import Counter, defaultdict
from copy import deepcopy
from fractions import Fraction as Q
import gzip
import hashlib
from itertools import combinations
import json
from math import gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent
INPUT = HERE/"inputs"
V, R, M, T = 111, 438, 64, 32
PARTIAL = {462: 506, 463: 506, 464: 506, 467: 508, 470: 509}
PINS = {
    "WORD.json.gz": "c46ccd7d3eedabc6a7efbb1a91ec13f2928bad8ee0bac57c6e593a092d13d96c",
    "GEOMETRY.json.gz": "a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022",
    "ALLOCATION.json": "06fa9322508aba3d8a5dc6469151cdfaa906b60559582b49c8b024428b158021",
    "TERMINAL-CHARTS.json": "489216ea25f47f061675ab7b7e4a17289a531bce6fe77cca166a13265bfcbb17",
    "CONTROLLER.py": "6368196a393ac25bb2918880e4c4bd31ed733b762c27b6873ab391cbc0c5c3c8",
}


def need(x, why):
    if not x:
        raise ValueError(why)


def canon(x):
    # JSON object keys become strings on disk; normalize before sorting so a
    # reconstructed integer-key histogram compares with its loaded receipt.
    x = json.loads(json.dumps(x))
    return json.dumps(x, sort_keys=True, separators=(",", ":")).encode()


def sha(x):
    return hashlib.sha256(x).hexdigest()


def authenticated_inputs():
    out = {name: (INPUT/name).read_bytes() for name in PINS}
    for name, raw in out.items():
        need(sha(raw) == PINS[name], "source SHA256: "+name)
    return out


def matmul(a, b):
    return [[sum((x*y for x, y in zip(row, col)), Q(0))
             for col in zip(*b)] for row in a]


def transpose(a):
    return list(map(list, zip(*a)))


def eye(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def projector(vectors):
    basis = []
    for vector in vectors:
        v = list(map(Q, vector))
        for u in basis:
            d = sum(x*y for x, y in zip(v, u))/sum(x*x for x in u)
            v = [x-d*y for x, y in zip(v, u)]
        if any(v):
            basis.append(v)
    p = [[sum((u[i]*u[j]/sum(x*x for x in u) for u in basis), Q(0))
          for j in range(8)] for i in range(8)]
    return p, len(basis)


def apply_gate(a, gate):
    op, i, j = gate[:3]
    if op == "swap":
        a[i], a[j] = a[j], a[i]
    elif op == "scale":
        need(Q(j) in (Q(-1), Q(2), Q(1, 2)), "coordinate scale alphabet")
        a[i] = [Q(j)*x for x in a[i]]
    else:
        need(op == "add" and Q(gate[3]) in (Q(-1), Q(1)), "coordinate ADD alphabet")
        a[i] = [x+Q(gate[3])*y for x, y in zip(a[i], a[j])]


def inverse_program(program):
    return ([g[:] if g[0] == "swap" else
             ["scale", g[1], str(1/Q(g[2]))] if g[0] == "scale" else
             ["add", g[1], g[2], str(-Q(g[3]))] for g in reversed(program)])


def replay_program(program, n):
    a, norm, denominator = eye(n), Q(1), 1
    for gate in program:
        apply_gate(a, gate)
        norm = max(norm, max(sum(map(abs, row)) for row in a))
        denominator = max(denominator, max(x.denominator for row in a for x in row))
    return a, norm, denominator


def terminal_program(chart):
    """Frozen five-terminal supplement's nomination and primitive expansion.

    No producer checker is imported. Every nominated word and its inverse are
    independently replayed below, with all exact prefix matrices retained.
    """
    a, reductions = deepcopy(chart), []
    for j in range(8):
        i = next(i for i in range(j, 8) if a[i][j])
        if i != j:
            a[i], a[j] = a[j], a[i]
            reductions.append(["swap", i, j])
        if a[j][j] != 1:
            c = 1/a[j][j]
            a[j] = [c*x for x in a[j]]
            reductions.append(["scale", j, str(c)])
        for i in range(8):
            if i != j and a[i][j]:
                c = -a[i][j]
                a[i] = [x+c*y for x, y in zip(a[i], a[j])]
                reductions.append(["add", i, j, str(c)])
    need(a == eye(8), "terminal Gaussian reduction")
    program = []
    for g in inverse_program(reductions):
        if g[0] == "swap":
            program.append(g)
        elif g[0] == "scale":
            c = Q(g[2])
            need(abs(c) in (Q(1), Q(2), Q(1, 2)), "terminal nominated scale")
            if c < 0:
                program.append(["scale", g[1], "-1"])
            if abs(c) != 1:
                program.append(["scale", g[1], str(abs(c))])
        else:
            c = Q(g[3])
            need(abs(c) in (Q(1), Q(2), Q(1, 2)), "terminal nominated shear")
            unit = "1" if c > 0 else "-1"
            if abs(c) == Q(1, 2):
                program.extend([["scale", g[2], "1/2"], ["add", g[1], g[2], unit],
                                ["scale", g[2], "2"]])
            else:
                program.extend([["add", g[1], g[2], unit]]*int(abs(c)))
    inverse = inverse_program(program)
    m, norm, den = replay_program(program, 8)
    mi, inorm, iden = replay_program(inverse, 8)
    need(m == chart and mi == transpose(chart), "terminal forward/inverse all-input replay")
    need(matmul(mi, m) == eye(8), "terminal exact restoration")
    return dict(program=program, inverse=inverse, primitive_count=len(program),
                forward_max_prefix_row_l1=str(norm), inverse_max_prefix_row_l1=str(inorm),
                forward_max_prefix_denominator=den, inverse_max_prefix_denominator=iden)


def permutation_program(perm):
    current = list(range(len(perm)))
    wanted = [perm.index(i) for i in range(len(perm))]
    out = []
    for i in range(len(perm)):
        if current[i] != wanted[i]:
            j = current.index(wanted[i])
            current[i], current[j] = current[j], current[i]
            out.append(["swap", i, j])
    need(current == wanted, "permutation lowering")
    return out


def family_chart(q):
    """Explicit signed H4/2 chart; no division by an odd field characteristic."""
    axes = [i for i, x in enumerate(q) if x]
    program = []
    if len(axes) == 1:
        need(abs(q[axes[0]]) == 2, "unit root")
        if q[axes[0]] < 0:
            program.append(["scale", 0, "-1"])
    else:
        need(len(axes) == 4 and all(abs(q[i]) == 1 for i in axes), "four-coordinate root")
        for i, j in ((0, 1), (2, 3), (0, 2), (1, 3)):
            program += [["add", i, j, "1"], ["scale", j, "-1"],
                        ["scale", j, "2"], ["add", j, i, "1"]]
        program += [["scale", i, "1/2"] for i in range(4)]
        program += [["scale", i, "-1"] for i, axis in enumerate(axes) if q[axis] < 0]
    perm = axes+[i for i in range(8) if i not in axes]
    program += permutation_program(perm)
    a, norm, denominator = replay_program(program, 8)
    ai, inorm, iden = replay_program(inverse_program(program), 8)
    u = [Q(x, 2) for x in q]
    need([row[0] for row in a] == u, "family first axis")
    need(matmul(transpose(a), a) == eye(8), "family orthogonality")
    need(all(x.denominator & (x.denominator-1) == 0 for row in a for x in row),
         "family chart not dyadic")
    need(ai == transpose(a), "family inverse routing")
    return a, dict(program=program, inverse=inverse_program(program),
                   primitive_count=len(program), max_forward_prefix_row_l1=str(norm),
                   max_inverse_prefix_row_l1=str(inorm),
                   max_forward_prefix_denominator=denominator, max_inverse_prefix_denominator=iden)


def recipe():
    """Literal PR442/PR589 K=4 recipe; equality with pinned source is checked."""
    out = [dict(kind="local", stage=0, pair=0, reverse=False)]
    stage = 1
    for j in range(4):
        out.append(dict(kind="local", stage=stage, pair=j, reverse=True))
        stage += 1
        if j < 3:
            out.append(dict(kind="bridge", dst=j, src=j+1, coefficient=1))
        out.append(dict(kind="local", stage=stage, pair=j, reverse=False))
        stage += 1
        if j < 3:
            out.append(dict(kind="bridge", dst=j, src=j+1, coefficient=-1))
    for j in reversed(range(3)):
        out.append(dict(kind="bridge", dst=j+1, src=j, coefficient=1))
    out.append(dict(kind="exchange"))
    return out


def chronology():
    levels = [-1]*4
    events, children = [], []
    def advance(pair, target):
        before = levels[pair]
        axes = list(range(1 if before == -1 else 8+7*before, 8+7*target))
        child = dict(kind="idle", idx=len(children), pair=pair,
                     source_level=before, target_level=target, axes=axes, rank=len(axes))
        events.append(child)
        children.append(child)
        levels[pair] = target
    for e in recipe():
        events.append(e)
        if e["kind"] == "local":
            s, p = e["stage"], e["pair"]
            need(levels[p] == s-1, "local source level")
            levels[p] = s
            if 1 <= s <= 6:
                advance((s+1)//2, s)
            if s == 8:
                for p in range(4):
                    advance(p, 8)
        elif e["kind"] == "bridge":
            need(levels[e["src"]] == levels[e["dst"]], "bridge levels")
        else:
            need(levels == [8]*4, "final levels")
    calls = {e["stage"]: (i, e["pair"]) for i, e in enumerate(events) if e["kind"] == "local"}
    windows = {}
    for c in children:
        end = events.index(c)
        touched = [i for i, e in enumerate(events[:end])
                   if (e["kind"] == "local" and e["pair"] == c["pair"]) or
                   (e["kind"] == "bridge" and c["pair"] in (e["src"], e["dst"]))]
        lo = max(touched, default=-1)
        stages = [s for s, (begin, pair) in calls.items()
                  if lo < begin < end and pair != c["pair"]]
        windows[c["idx"]] = dict(lower_open_event=lo, upper_open_event=end, stages=stages)
    need(len(events) == 29 and len(children) == 10 and len(calls) == 9, "controller size")
    return events, children, calls, windows


def baseline_slots(selection, children, windows):
    queues, patterns = defaultdict(list), defaultdict(list)
    for child, width, stage, count in sorted(selection["stages"]):
        need(width == 8 and stage in windows[child]["stages"], "source demand window")
        queues[child].extend([stage]*count)
    for child, widths, count in selection["patterns"]:
        patterns[child].append((widths, count))
    next_helper = Counter()
    slots = []
    for c in children:
        child, cp, used = c["idx"], 0, 0
        for widths, count in sorted(patterns[child], key=lambda p: (-sum(p[0]), p[0])):
            need(all(w == 8 for w in widths), "source widths")
            for _ in range(count):
                for offset in range(0, sum(widths), 8):
                    stage = queues[child][used]
                    used += 1
                    helper = next_helper[stage]
                    next_helper[stage] += 1
                    slots.append([child, cp, offset, 8, stage, helper])
                cp += 1
        need(used == len(queues[child]) and cp <= 222, "source demand coverage")
    need(dict(next_helper) == {s: R for s in range(9)}, "source helper coverage")
    return slots


def adapt(slots, ordered_widths):
    offsets = Counter()
    out = []
    for child, cp, oldoff, oldwidth, stage, helper in slots:
        width = ordered_widths[helper]
        out.append([child, cp, offsets[child, cp], width, stage, helper])
        offsets[child, cp] += width
    return out


def relative_chart(axes, b):
    """Sparse rows of pi_axes diag(B^T,I56); common A_q cancels for owners."""
    perm = list(axes)+[i for i in range(64) if i not in axes]
    rows = [None]*64
    bt = transpose(b)
    for i in range(64):
        rows[perm[i]] = ([str(x) for x in bt[i]]+["0"]*56 if i < 8
                         else ["1" if j == i else "0" for j in range(64)])
    return rows


def difference_unit(a, b):
    """All odd-characteristic specializations distinguish these two charts."""
    nums = [abs((Q(x)-Q(y)).numerator)
            for ar, br in zip(a, b) for x, y in zip(ar, br) if x != y]
    need(nums, "physical chart collision")
    g = 0
    for n in nums:
        g = gcd(g, n)
    need(g & (g-1) == 0, "owner collision at an odd characteristic")
    return g


def audit(slots, children, windows, ordered_widths, terminal_frames, bases):
    used, by_stage, helpers = defaultdict(set), defaultdict(list), set()
    routes, chart_by_key, charts = {}, {}, []
    for child, cp, offset, width, stage, helper in slots:
        need(stage in windows[child]["stages"], "slot outside open source window")
        need(0 <= cp < 222 and 0 <= helper < R, "slot domain")
        need(width == ordered_widths[helper], "ordered terminal width")
        need((stage, helper) not in helpers, "duplicate helper")
        helpers.add((stage, helper))
        axes = children[child]["axes"][offset:offset+width]
        need(len(axes) == width and offset >= 0, "slot extent")
        need(not used[child, cp].intersection(axes), "overlapping slot")
        used[child, cp].update(axes)
        frame = terminal_frames[helper]
        chart_key = (tuple(axes), frame)
        if chart_key not in chart_by_key:
            cid = len(charts)
            chart_by_key[chart_key] = cid
            perm = list(axes)+[i for i in range(64) if i not in axes]
            charts.append(dict(id=cid, axes=axes, terminal_frame=frame,
                               permutation=perm, permutation_program=permutation_program(perm),
                               relative_matrix=relative_chart(axes, bases[frame])))
        cid = chart_by_key[chart_key]
        routes[stage, helper] = (child, cp, offset, width, cid)
        by_stage[stage].append((helper, child, cp, cid))
    need(helpers == {(s, h) for s in range(9) for h in range(R)}, "missing helper")
    remainder, factors = Counter(), []
    for c in children:
        for cp in range(222):
            original = set(c["axes"])
            need(used[c["idx"], cp] <= original, "factor outside pending")
            rest = sorted(original-used[c["idx"], cp])
            # Compact-prefix promise used by the source child dispatch.
            need(rest == c["axes"][len(used[c["idx"], cp]):], "noncompact pending prefix")
            remainder[len(rest)] += 1
            factors.append([c["idx"], cp, rest])
    family_masks = defaultdict(set)
    fill, dispatch, max_roles = [], [], {}
    compared_pairs, difference_gcds = 0, Counter()
    pair_for_stage = {e["stage"]: e["pair"] for e in recipe() if e["kind"] == "local"}
    reverse_for_stage = {e["stage"]: e["reverse"] for e in recipe() if e["kind"] == "local"}
    for stage in range(9):
        by_family = defaultdict(list)
        active = pair_for_stage[stage]
        for helper, child, cp, cid in by_stage[stage]:
            pair = children[child]["pair"]
            need(pair != active, "host on active pair")
            by_family[2*pair*V+cp].append(cid)
        max_roles[stage] = max(map(len, by_family.values()))
        for cids in by_family.values():
            for a, b in combinations(cids, 2):
                unit_gcd = difference_unit(charts[a]["relative_matrix"], charts[b]["relative_matrix"])
                difference_gcds[unit_gcd] += 1
                compared_pairs += 1
        for rep in range(T):
            owners = []
            for role in range(222):
                side, port = divmod(role, V)
                if reverse_for_stage[stage]:
                    side = 1-side
                family = rep*888+(2*active+side)*V+port
                owners.append([family, ["data", stage, port]])
            for helper in range(R):
                child, cp, offset, width, cid = routes[stage, helper]
                family = rep*888+2*children[child]["pair"]*V+cp
                axes = charts[cid]["axes"]
                need(not family_masks[family].intersection(axes), "cross-child physical overlap")
                family_masks[family].update(axes)
                fill.append([stage, rep, helper, family, child, offset, width, cid])
                owners.append([family, ["hosted", child, offset, width, cid]])
            dispatch.append(dict(stage=stage, replica=rep, pair=active,
                                 orientation="reverse" if reverse_for_stage[stage] else "forward",
                                 owners=owners, private_owner=[28416+stage, ["private", "d"]]))
    need(len(fill) == 126144 and len(dispatch) == 288, "full owner coverage")
    return dict(remainders=dict(sorted(remainder.items())), factors=factors,
                fill=fill, dispatch=dispatch, charts=charts,
                max_helpers_per_family=max_roles, physical_families=len(family_masks),
                compared_pairs_per_replica=compared_pairs,
                owner_difference_numerator_gcds=dict(sorted(difference_gcds.items())))


def check_controller(raw):
    nodes = [n for n in ast.parse(raw).body if isinstance(n, ast.FunctionDef) and n.name == "recipe"]
    need(len(nodes) == 1, "unique source recipe")
    namespace = {}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), "authenticated CONTROLLER.py recipe", "exec"),
         namespace)
    need(namespace["recipe"](4) == recipe(), "literal controller source binding")


def audit_emitted(fill, dispatch, slots, children, calls, charts):
    """Read emitted descriptors independently of their construction loops."""
    source = {(s, h): (child, cp, offset, width)
              for child, cp, offset, width, s, h in slots}
    seen = set()
    for stage, rep, helper, family, child, offset, width, cid in fill:
        need(0 <= rep < 32 and (stage, helper) in source, "emitted owner role domain")
        need((stage, rep, helper) not in seen, "duplicate emitted owner")
        seen.add((stage, rep, helper))
        c, cp, off, w = source[stage, helper]
        need((child, offset, width) == (c, off, w), "emitted slot binding")
        need(family == rep*888+2*children[child]["pair"]*V+cp, "emitted physical family")
        need(charts[cid]["axes"] == children[child]["axes"][offset:offset+width], "emitted chart binding")
    need(seen == {(s, r, h) for s in range(9) for r in range(32) for h in range(R)},
         "omitted emitted owner")
    by_call = defaultdict(dict)
    for stage, rep, helper, family, child, offset, width, cid in fill:
        by_call[stage, rep][helper] = [family, ["hosted", child, offset, width, cid]]
    seen_calls = set()
    orientations = {e["stage"]: ("reverse" if e["reverse"] else "forward")
                    for e in recipe() if e["kind"] == "local"}
    for d in dispatch:
        s, r, p = d["stage"], d["replica"], d["pair"]
        need((s, r) not in seen_calls and 0 <= r < 32 and s in calls, "emitted dispatch domain")
        seen_calls.add((s, r))
        need(p == calls[s][1], "emitted active pair")
        need(d["orientation"] == orientations[s], "emitted controller orientation")
        need(d["private_owner"] == [28416+s, ["private", "d"]], "emitted private family")
        need(len(d["owners"]) == 660, "emitted owner arity")
        for role, actual in enumerate(d["owners"]):
            if role >= 222:
                need(actual == by_call[s, r][role-222], "emitted helper dispatch binding")
            else:
                side, port = divmod(role, V)
                if d["orientation"] == "reverse":
                    side = 1-side
                need(actual == [r*888+(2*p+side)*V+port, ["data", s, port]],
                     "emitted data dispatch binding")
    need(seen_calls == {(s, r) for s in range(9) for r in range(32)}, "omitted emitted dispatch")


def defects(slots, children, windows, widths, frames, bases, result, calls):
    rejected = []
    def reject(name, action, message):
        try:
            action()
        except ValueError as e:
            need(message in str(e), name+" wrong rejection: "+str(e))
            rejected.append(dict(name=name, rejection=str(e)))
            return
        raise ValueError("malformed control accepted: "+name)
    def check_slots(x):
        return audit(x, children, windows, widths, frames, bases)
    reject("missing helper", lambda: check_slots(slots[:-1]), "missing helper")
    reject("duplicate helper", lambda: check_slots(slots+[slots[-1]]), "duplicate helper")
    bad = deepcopy(slots)
    bad[0][4] = 8
    reject("stage outside open window", lambda: check_slots(bad), "slot outside open source window")
    bad = deepcopy(slots)
    index = next(i for i, z in enumerate(bad) if z[3] == 4)
    bad[index][3] = 8
    reject("partial terminal charged as full", lambda: check_slots(bad), "ordered terminal width")
    bad = deepcopy(slots)
    index = next(i for i, z in enumerate(bad) if z[2] > 0)
    bad[index][2] = 0
    reject("overlapping same-deadline slices", lambda: check_slots(bad), "overlapping slot")
    reject("same-family duplicate cover chart",
           lambda: difference_unit(result["charts"][0]["relative_matrix"],
                                   result["charts"][0]["relative_matrix"]),
           "physical chart collision")
    bad_fill = [x[:] for x in result["fill"]]
    bad_fill[0][3] += 888
    reject("wrong replica with unchanged support",
           lambda: audit_emitted(bad_fill, result["dispatch"], slots, children, calls, result["charts"]),
           "emitted physical family")
    bad_dispatch = deepcopy(result["dispatch"])
    bad_dispatch[0]["private_owner"][0] = 0
    reject("private aliases live family",
           lambda: audit_emitted(result["fill"], bad_dispatch, slots, children, calls, result["charts"]),
           "emitted private family")
    bad_dispatch = deepcopy(result["dispatch"])
    bad_dispatch[0]["orientation"] = "reverse"
    owners = bad_dispatch[0]["owners"]
    owners[:222] = owners[111:222]+owners[:111]
    reject("wrong orientation with consistently swapped data owners",
           lambda: audit_emitted(result["fill"], bad_dispatch, slots, children, calls, result["charts"]),
           "emitted controller orientation")
    p, _ = projector([[bases[506][i][j] for i in range(8)] for j in range(4)])
    bad_b = deepcopy(bases[506])
    for row in bad_b:
        row[0], row[4] = row[4], row[0]
    d = [[Q(i == j and i < 4) for j in range(8)] for i in range(8)]
    reject("equal-rank wrong terminal projector",
           lambda: need(matmul(matmul(bad_b, d), transpose(bad_b)) == p, "wrong terminal image"),
           "wrong terminal image")
    return rejected


def construct():
    raw = authenticated_inputs()
    wraw, graw = raw["WORD.json.gz"], raw["GEOMETRY.json.gz"]
    word = json.loads(gzip.decompress(wraw))
    geom = json.loads(gzip.decompress(graw))
    receipt_raw = raw["ALLOCATION.json"]
    selection = json.loads(receipt_raw)["placement"]["selection"]
    frames = word["final"][222:]
    need(word["start"][222:] == [0]*R, "nonzero helper entrance")
    need({222+h:f for h,f in enumerate(frames) if f != 1} == PARTIAL, "partial terminal registry")
    terminal_raw = raw["TERMINAL-CHARTS.json"]
    predecessor_charts = {c["terminal_frame"]: c for c in json.loads(terminal_raw)["charts"]}
    bases, dims, projectors = {1:eye(8)}, {1:8}, {1:eye(8)}
    terminal_programs = {1: dict(program=[], inverse=[], primitive_count=0,
                                 forward_max_prefix_row_l1="1", inverse_max_prefix_row_l1="1",
                                 forward_max_prefix_denominator=1, inverse_max_prefix_denominator=1)}
    for f in sorted(set(frames)-{1}):
        p, k = projector([geom["lines"][i] for i in geom["frames"][f]])
        need(k == 4, "partial terminal rank")
        b = transpose([[Q(x) for x in col] for col in predecessor_charts[f]["Q_columns"]])
        need(matmul(transpose(b), b) == eye(8), "predecessor terminal chart isometry")
        d = [[Q(i == j and i < k) for j in range(8)] for i in range(8)]
        need(matmul(matmul(b, d), transpose(b)) == p, "predecessor terminal chart actual projector")
        prog = terminal_program(b)
        for inverse in (False, True):
            key = "inverse" if inverse else "program"
            matrix, norm, denominator = replay_program(prog[key], 8)
            need(matrix == (transpose(b) if inverse else b), "terminal primitive replay")
            name = "inverse" if inverse else "forward"
            need(str(norm) == prog[name+"_max_prefix_row_l1"] and
                 denominator == prog[name+"_max_prefix_denominator"], "terminal prefix receipt")
        need(prog["inverse"] == inverse_program(prog["program"]), "terminal exact primitive inverse")
        bases[f], dims[f], projectors[f], terminal_programs[f] = b, k, p, prog
    widths = [dims[f] for f in frames]
    family_data = [family_chart(q) for q in geom["lines"]]
    family_charts = [a for a, _ in family_data]
    check_controller(raw["CONTROLLER.py"])
    events, children, calls, windows = chronology()
    source = baseline_slots(selection, children, windows)
    need(sha(json.dumps(source, separators=(",", ":")).encode()) ==
         json.loads(receipt_raw)["placement"]["slot_list_sha256"], "source slot digest")
    slots = adapt(source, widths)
    result = audit(slots, children, windows, widths, frames, bases)
    audit_emitted(result["fill"], result["dispatch"], slots, children, calls, result["charts"])
    controls = defects(slots, children, windows, widths, frames, bases, result, calls)
    old_idle = Counter()
    oldused = Counter()
    for child, cp, offset, width, stage, helper in source:
        oldused[child, cp] += width
    for c in children:
        for cp in range(222):
            old_idle[c["rank"]-oldused[c["idx"], cp]] += 1
    new_idle = Counter(result["remainders"])
    need(sum(k*v for k,v in new_idle.items())-sum(k*v for k,v in old_idle.items()) == 180,
         "returned terminal mass")
    order = dict(controller=events, calls=[dict(stage=s, replica=r, event=calls[s][0])
                                         for s in range(9) for r in range(32)],
                 windows=windows)
    charts = dict(terminal_bases={str(f): [[str(x) for x in row] for row in b]
                                 for f,b in bases.items()},
                  terminal_programs=terminal_programs,
                  family_charts=[[[str(x) for x in row] for row in a] for a in family_charts],
                  family_programs=[p for _, p in family_data],
                  relative_charts=result["charts"])
    route_max = max(len(terminal_programs[c["terminal_frame"]]["program"]) +
                    len(c["permutation_program"]) + p["primitive_count"]
                    for c in result["charts"] for _, p in family_data)
    af = max(Q(p["max_forward_prefix_row_l1"]) for _, p in family_data)
    ar = max(Q(p["max_inverse_prefix_row_l1"]) for _, p in family_data)
    qf = max(Q(p["forward_max_prefix_row_l1"]) for p in terminal_programs.values())
    qr = max(Q(p["inverse_max_prefix_row_l1"]) for p in terminal_programs.values())
    need(all(p["max_forward_prefix_denominator"] <= 2 and
             p["max_inverse_prefix_denominator"] <= 2 for _, p in family_data), "family dyadic prefix")
    need(all(p["forward_max_prefix_denominator"] <= 2 and
             p["inverse_max_prefix_denominator"] <= 2 for p in terminal_programs.values()), "terminal dyadic prefix")
    route_bound = dict(max_64_coordinate_forward_primitives=route_max,
                       max_64_coordinate_inverse_primitives=route_max,
                       max_128_coordinate_chart_primitives=2*route_max,
                       max_128_coordinate_chart_and_inverse_primitives=4*route_max,
                       max_family_primitives=max(p["primitive_count"] for _, p in family_data),
                       max_permutation_primitives=max(len(c["permutation_program"]) for c in result["charts"]),
                       max_terminal_primitives=max(p["primitive_count"] for p in terminal_programs.values()),
                       max_forward_prefix_row_l1_bound=str(max(qr, 2*af)),
                       max_inverse_prefix_row_l1_bound=str(max(ar, 2*qf)),
                       max_prefix_denominator_bound=4, scratch_field_elements=0,
                       alphabet=["unit signed ADD", "NEGATE", "DOUBLE", "HALF", "SWAP"],
                       caveat="Coordinate primitives are not physical payload/tape tariffs.")
    summary = dict(scope="finite exact stream owner/controller admission; no physical compiler claim",
                   local_input_word_sha256=sha(wraw), geometry_sha256=sha(graw),
                   allocation_receipt_sha256=sha(receipt_raw),
                   predecessor_terminal_charts_sha256=sha(terminal_raw),
                   controller_sha256=sha(raw["CONTROLLER.py"]),
                   ordered_widths=widths, partial_terminals=PARTIAL,
                   slots_per_replica=len(slots), full_helper_occurrences=len(result["fill"]),
                   calls=len(result["dispatch"]), controller_events=len(events),
                   idle_per_replica_including_zero=result["remainders"],
                   old_idle_per_replica_including_zero=dict(sorted(old_idle.items())),
                   returned_idle_rank_per_replica=180, returned_idle_rank_global=5760,
                   distinct_relative_charts=len(result["charts"]),
                   max_helpers_per_family=result["max_helpers_per_family"],
                   occupied_physical_families=result["physical_families"],
                   same_family_pairs_per_replica=result["compared_pairs_per_replica"],
                   same_family_pairs_all_replicas=32*result["compared_pairs_per_replica"],
                   owner_difference_numerator_gcds=result["owner_difference_numerator_gcds"],
                   physical_child_deadlines_including_zero=32*10*222,
                   fill_sha256=sha(canon(result["fill"])), dispatch_sha256=sha(canon(result["dispatch"])),
                   order_sha256=sha(canon(order)), charts_sha256=sha(canon(charts)),
                   slots_sha256=sha(canon(slots)), remainder_factors_sha256=sha(canon(result["factors"])),
                   live_families=28416, private_family_reserve=9, banks=0)
    summary["coordinate_route_bound"] = route_bound
    terms = dict(rho15=240, legacy_chart=144, new_complete_chart=4*route_max,
                 legacy_basis=2, permutation=63, tail=64)
    summary["routing_invoice"] = dict(
        selector_G_terms=terms, selector_G=sum(terms.values()), max_sigma_primitives=route_max,
        max_both_halves_primitives=2*route_max, max_complete_route_primitives=4*route_max,
        premise="Inherited selector-coordinate invoice; physical payload and tape implementation remain conditional.",
        interpretation="Keep all legacy terms and additionally charge both halves and both chart directions.")
    summary["controls"] = controls
    return summary, dict(ORDER=order, CHARTS=charts, SLOTS=slots, REMAINDERS=result["factors"],
                         FILL=result["fill"], DISPATCH=result["dispatch"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="intentionally replace OWNERS.json")
    parser.add_argument("--emit", type=Path, help="new directory for complete literal certificates")
    args = parser.parse_args()
    summary, artifacts = construct()
    if args.write:
        (HERE/"OWNERS.json").write_text(json.dumps(summary, sort_keys=True, indent=2)+"\n")
    else:
        expected = json.loads((HERE/"OWNERS.json").read_text())
        need(canon(summary) == canon(expected), "OWNERS.json deterministic receipt mismatch")
    if args.emit is not None:
        args.emit.mkdir(parents=False, exist_ok=False)
        for name, obj in artifacts.items():
            data = canon(obj)
            if name in ("FILL", "DISPATCH"):
                (args.emit/(name+".json.gz")).write_bytes(gzip.compress(data, mtime=0))
            else:
                (args.emit/(name+".json")).write_bytes(data+b"\n")
    print("PASS_CARRIER_OWNERS helpers=126144 calls=288 G=%d controls=%d no_new_kappa" %
          (summary["routing_invoice"]["selector_G"], len(summary["controls"])))
    return summary


if __name__ == "__main__":
    main()
