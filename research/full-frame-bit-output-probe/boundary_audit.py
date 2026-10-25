"""Exact endpoint and complete-mass audits omitted by the scalar column tests.

The rotating-normal experiment is a separate changed-endpoint construction.
Its literal two-coordinate closure is priced; no unrestricted barrier follows.
"""
from __future__ import annotations

import ast
from collections import Counter
from fractions import Fraction as Q


def need(ok, label):
    if not ok:
        raise RuntimeError(label)


def eye(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def transpose(a):
    return list(map(list, zip(*a)))


def multiply(a, b):
    bt = transpose(b)
    return [[sum((x * y for x, y in zip(row, col) if x and y), Q(0))
             for col in bt] for row in a]


def port_boundary(q):
    """Reconstruct the pinned rho's block identities over Q for one E8 port."""
    n = len(q)
    unit = [Q(x, 2) for x in q]
    need(sum(x * x for x in unit) == 1, "unit E8 normal")
    P = [[x * y for y in unit] for x in unit]
    I = eye(n)
    K = [[I[i][j] - P[i][j] for j in range(n)] for i in range(n)]
    v = [Q(i == 0) - unit[i] for i in range(n)]
    norm = sum(x * x for x in v)
    g = I if not norm else [[I[i][j] - 2 * v[i] * v[j] / norm
                             for j in range(n)] for i in range(n)]
    need(multiply(g, transpose(g)) == I, "Householder port chart isometry")
    need([row[0] for row in g] == unit, "Householder maps e0 to the port")
    A = [row[1:] for row in g]
    need(multiply(A, transpose(A)) == K, "A A^T=K")
    need(multiply(transpose(A), A) == eye(n - 1), "A^T A=I7")
    need(not any(x for row in multiply(P, A) for x in row), "P A=0")
    need(multiply(P, P) == P and sum(P[i][i] for i in range(n)) == 1,
         "rank-one nonzero endpoint discrepancy")
    # rho=[[P,A],[A^T,0]]. These checked block identities give
    # rho diag(0,I7) rho = diag(K,0), and
    # rho diag(P,I7) rho = diag(I8,0).
    # Selected ends (Fx,Fy)=(I,K) match the next reflected call.
    # Changed ends (I,I) require K on both incoming physical banks,
    # while the preceding call leaves I on both: two rank-one discrepancies.
    return {"selected_boundary_matches": True,
            "full_full_boundary_matches": False,
            "full_full_discrepancy_ranks": [1, 1]}


def source_recipe(source):
    tree = ast.parse(source)
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "recipe"]
    need(len(nodes) == 1, "one pinned pure recipe function")
    namespace = {}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), "pinned_recipe", "exec"), namespace)
    return namespace["recipe"]


def complete_profile(recipe, pairs, ports, replicas, local):
    stages = 2 * pairs + 1
    levels = [-1] * pairs
    idle = []
    local_calls = 0
    for event in recipe(pairs):
        if event["kind"] == "local":
            s, p = event["stage"], event["pair"]
            need(levels[p] == s - 1, "pinned stage entrance level")
            levels[p] = s
            local_calls += 1
            if s % 2 and s <= 2 * pairs - 3:
                j = (s + 1) // 2
                need(levels[j] == -1, "first idle entrance")
                levels[j] = s
                idle.append(7 * (s + 1))
            elif not s % 2 and 2 <= s <= 2 * pairs - 2:
                j = s // 2
                need(levels[j] == s - 1, "second idle entrance")
                levels[j] = s
                idle.append(7)
            elif s == 2 * pairs:
                for j in range(pairs):
                    need(levels[j] == 2 * j + 2, "terminal idle entrance")
                    idle.append(7 * (2 * pairs - levels[j]))
                    levels[j] = 2 * pairs
        elif event["kind"] == "bridge":
            need(levels[event["dst"]] == levels[event["src"]], "bridge levels")
        else:
            need(levels == [2 * pairs] * pairs, "terminal exchange levels")
    need(local_calls == stages, "complete local stage count")
    hist = Counter({r: stages * replicas * count for r, count in local.items()})
    for rank in idle:
        if rank:
            hist[rank] += 2 * ports * replicas
    m = 1 + 7 * stages
    live = 2 * pairs * ports * replicas
    mass = sum(r * count for r, count in hist.items())
    return {"stages": stages, "m": m, "live": live, "rank_mass": mass,
            "capacity": m * live, "deficit": m * live - mass,
            "bill_at_zero": str(Q(mass, m * live)),
            "idle_ranks": idle,
            "histogram": {str(r): count for r, count in sorted(hist.items())}}


def full_frame_audit(word, global_source, levers):
    ports = word["v"]
    boundaries = [port_boundary(q) for q in word["lines"]]
    recipe = source_recipe(global_source)
    budgets = []
    for pairs in (2, 4, 5):
        audit = complete_profile(recipe, pairs, ports, 32, {7: ports, 8: ports})
        need(audit["deficit"] == -ports * 32, "full targets destroy the positive deficit")
        need(Q(audit["bill_at_zero"]) > 1, "no positive saving in the retained schedule")
        control = complete_profile(recipe, pairs, ports, 32, {7: 2 * ports})
        need(control["deficit"] == control["live"], "rank-seven endpoint accounting control")
        audit["rank7_endpoint_accounting_control_deficit"] = control["deficit"]
        budgets.append(audit)
    actual = budgets[1]
    actual_hist = {int(r): count for r, count in actual["histogram"].items()}
    need(levers.bill(actual_hist, actual["m"], actual["live"], Q(1, 499))[0] > 1,
         "complete nine-stage bill rejects the requested threshold")
    # Formerly the extra target rank was subtracted from idle mass. The
    # pinned schedule has no such deletion: it is exactly L*T*v unpaid work.
    missing = 9 * 32 * ports
    former = levers.relaxed({7: ports, 8: ports}, 64, Q(8 * ports, 9), 0, 45)
    need(levers.bill(former, 64, Q(8 * ports, 9), Q(0))[1] < 1,
         "retain the former false-positive model as a scope control")
    return {
        "status": "REJECT_FIXED_FULL_TARGET_TEMPLATE",
        "ports_checked": len(boundaries),
        "selected_interstage_boundary_matches": 2 * len(boundaries),
        "changed_interstage_rank_one_mismatches": 2 * len(boundaries),
        "address_witness": {
            "port": 0, "normal": word["lines"][0],
            "incoming_frame": "I8", "required_next_frame": "K=I8-P",
            "full_on_head_q_tail_zero": "head=0, tail=q",
            "K_on_head_q_tail_zero": "head=q, tail=0",
        },
        "complete_rank_budgets": budgets,
        "former_screen_withdrawn": {
            "reason": "extra FULL target rank was incorrectly removed from idle mass",
            "missing_nine_stage_rank_mass": missing,
            "incorrect_bit_kappa_cap": "0.018456786532",
            "complex_screen_applicability": "withdrawn; no replacement coverage law was proved",
        },
    }


def complex_structure(q):
    return tuple(z for i in range(0, 8, 2) for z in (-q[i + 1], q[i]))


def canonical(q):
    return max(tuple(q), tuple(-x for x in q))


def rational_rank(rows):
    basis = []
    for row in rows:
        row = [Q(x) for x in row]
        for pivot, prior in basis:
            if row[pivot]:
                factor = row[pivot] / prior[pivot]
                row = [x - factor * y for x, y in zip(row, prior)]
        pivot = next((j for j, x in enumerate(row) if x), None)
        if pivot is not None:
            basis.append((pivot, row))
    return len(basis)


def rotating_normal_probe(lines, levers):
    """One exact E8-normal rotation and its literal six-step closure invoice."""
    roots = {canonical(q) for q in lines}
    need(len(roots) == 120, "complete E8 root-line inventory")
    for q in roots:
        jq = complex_structure(q)
        need(canonical(jq) in roots, "J preserves E8 root lines")
        need(sum(x * y for x, y in zip(q, jq)) == 0, "p perpendicular to Jp")
        need(complex_structure(jq) == tuple(-x for x in q), "J squared is minus identity")
        need(canonical(jq) != q, "no projective fixed point")
        frame = [r for r in roots if sum(x * y for x, y in zip(r, jq)) == 0]
        need(len(frame) == 63 and rational_rank(frame) == 7, "root-spanned Jp hyperplane")
    # A local word reads x at (Jp)^perp, leaves x there, and advances y to
    # FULL. Its frame increments are 6,7,1. Reassigning high/low roles gives
    # (x,y)->(x+y,x), with order three over F2; J has projective order two.
    steps = 6
    frames = [1, 0]
    expressions = [{(0, 0)}, {(1, 0)}]
    active = list(range(8))
    exterior = 0
    high, low = 0, 1
    next_axis = 8
    profile = Counter()
    def move(role, new):
        old = frames[role]
        need(old & ~new == 0, "rotating word uses only nested moves")
        difference = new ^ old
        if difference:
            profile[difference.bit_count()] += 1
            expressions[role] = {(bank, mask ^ difference) for bank, mask in expressions[role]}
            frames[role] = new
    normals = []
    for stage in range(steps):
        p, n = stage % 2, 1 - stage % 2
        full = exterior | sum(1 << axis for axis in active)
        normal = active[n]
        H = full ^ (1 << normal)
        need(frames[high] == exterior | (1 << active[p]), "source entrance line")
        need(frames[low] == exterior, "target entrance zero in the active core")
        move(high, H)
        move(low, H)
        expressions[low] ^= expressions[high]
        move(low, full)
        high, low = low, high
        normals.append(normal)
        if stage != steps - 1:
            exterior = H
            active = [normal if i == n else -1 for i in range(8)]
            for i in range(8):
                if active[i] == -1:
                    active[i] = next_axis
                    next_axis += 1
    m = next_axis
    all_axes = (1 << m) - 1
    final_normal = normals[-1]
    need(m == 43 and high == 0 and low == 1, "six-stage owner and dimension closure")
    need(profile == Counter({1: 6, 6: 6, 7: 6}), "rotating local rank histogram")
    need(expressions[0] == {(0, all_axes ^ 1)}, "first bank exact address endpoint")
    need(expressions[1] == {(1, all_axes ^ (1 << final_normal))},
         "second bank exact drifting-spectator endpoint")
    need(final_normal != 0, "spectator has not returned to the input line")
    # Ignoring address masks gives the identity, so scalar-only checks pass.
    need([{b for b, _ in e} for e in expressions] == [{0}, {1}], "scalar identity control")
    correction = 1 | (1 << final_normal)
    fixed_low = {(b, mask ^ correction) for b, mask in expressions[1]}
    need(fixed_low == {(1, all_axes ^ 1)}, "literal rank-two correction closes the endpoint")
    paid = dict(profile)
    paid[2] = 1
    need(sum(r * count for r, count in profile.items()) == 84, "uncorrected rank mass")
    need(sum(r * count for r, count in paid.items()) == 2 * m, "correction consumes the deficit")
    need(levers.bill(paid, m, 2, Q(1, 499))[0] > 1, "literal closure has no positive saving")
    one_rank1 = dict(profile)
    one_rank1[1] += 1
    need(levers.bill(one_rank1, m, 2, Q(1, 499))[1] < 1,
         "one-rank optimistic repair allowance at the requested target")
    return {
        "status": "REJECT_LITERAL_ROTATING_NORMAL_CLOSURE",
        "J_root_lines_checked": 120, "J_projective_two_cycles": 60,
        "J_hyperplane_root_spans_checked": 120,
        "local_profile_per_port": {"1": 1, "6": 1, "7": 1},
        "local_input_normal": "p", "local_output_normal": "Jp",
        "local_source_end": "(Jp)^perp", "local_target_end": "FULL",
        "six_stage_scalar_endpoint": "identity over F2",
        "ambient_dimension": m, "normal_axis_path": normals,
        "initial_spectator_axis": 0, "final_spectator_axis": final_normal,
        "uncorrected_rank_mass_per_pair": 84,
        "nominal_capacity_per_pair": 86,
        "literal_address_correction_rank": 2,
        "corrected_zero_saving_bill": "1",
        "one_rank1_extra_fits_a_1_over_499_but_not_an_endpoint_construction": True,
        "scope": "exact coordinate-core walk and separate rank-two terminal correction; joint consumer/cover changes remain outside scope",
    }
