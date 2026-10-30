#!/usr/bin/env python3
"""Literal m=73 interstage admission for the Gaussian 128-port component.

This certifies local words, native phase alignments, the extra line invoice,
and the nine-stage data geometry. It does not certify a residual consumer or
a helper allocation. Apache-2.0; substantial OpenAI Codex assistance.
"""
from argparse import ArgumentParser
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
from types import ModuleType
import gzip
import json

PINS = {
    "artifact/recovered-involutory/modern_native_component.py": "f6769f1ecd6b2e582748805b3afcf4c65824ba108ce7f23a4d011c45f8b724de",
    "artifact/integer-mult-bounds/research/kappa-consumer-followup/baseline/symmetric_extended.py": "15f29c5a84e4b055668ff78bb6ec8c8e2d15aa8064b35832839a27a4ec205323",
}
SYMMETRIC_RESULT_SHA = "b870f449f883feb3ab65492d4fed55a08b996881a286f916b22b8b91728ed8a7"
SYMMETRIC_PROGRAM_PAYLOAD_SHA = "ca72b8ded2b12a842b3781cc6741084eb7136d20480d0a597e563eca776d85a3"
TEMPLATE_SHA = "21297b20f1f2dc76eb9dd8124416068c3cb096bab9df17fa4da19bc68dfe082e"
AXES = tuple(1 << i for i in range(73))


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def digest(p):
    return sha256(p.read_bytes()).hexdigest()


def read(p):
    data = p.read_bytes()
    return json.loads(gzip.decompress(data) if p.suffix == ".gz" else data)


def module(path, name, expected=None):
    raw = path.read_bytes()
    if expected is not None:
        need(sha256(raw).hexdigest() == expected, "source pin: " + str(path))
    out = ModuleType(name)
    out.__file__ = str(path)
    exec(compile(raw, str(path), "exec"), out.__dict__)
    return out


def bits(x):
    while x:
        b = x & -x
        yield b.bit_length() - 1
        x ^= b


def act(cols, x):
    out = 0
    for i in bits(x):
        out ^= cols[i]
    return out


def signature(lines, shift=0, global_phase=0):
    """Exact Z/4 quadratic polynomial on all 73 Boolean characters."""
    linear = [2 * ((shift >> i) & 1) for i in range(73)]
    cross = [0] * 73
    for axis, sign in lines:
        support = tuple(bits(axis))
        for i in support:
            linear[i] = (linear[i] + sign) % 4
            if sign % 2:
                for j in support:
                    if j > i:
                        cross[i] ^= 1 << j
    return global_phase % 4, tuple(linear), tuple(cross)


def routed(cols, lines):
    return [(act(cols, a), s) for a, s in lines]


def make_routes(phases, ports):
    routes = {}
    identities = 0
    for p in range(128):
        zero = p >= 112
        q = 1 if zero else ports[p]
        chart = AXES[1:9] if zero else tuple(phases["recipes"][p]["idle_children"][0]["orthogonal_axes"][:8])
        basis = (q,) + chart
        need(all((a & b).bit_count() % 2 == (i == j)
                 for i, a in enumerate(basis) for j, b in enumerate(basis)),
             "orthonormal stage chart")
        beta = sum(1 << i for i, v in enumerate(chart) if (v.bit_count() - 1) // 2 % 2)
        for stage in range(9):
            if stage == 0:
                cols, entry, exit_ = AXES, 0, 0
            else:
                swaps = [v ^ AXES[9 + 8 * (stage - 1) + i] for i, v in enumerate(chart)]
                cols = tuple(x ^ act(swaps, sum(((x & s).bit_count() % 2) << i
                                                for i, s in enumerate(swaps))) for x in AXES)
                entry = 0 if zero else q ^ act(chart, beta)
                exit_ = 0 if zero else act(chart, beta) ^ (beta << (9 + 8 * (stage - 1)))
            need(all(act(cols, act(cols, x)) == x for x in AXES), "involutory owner route")
            need(act(cols, q) == q, "fixed actual or virtual normal")
            need(all((a & b).bit_count() % 2 == (i == j)
                     for i, a in enumerate(cols) for j, b in enumerate(cols)), "orthogonal owner route")
            if not zero:
                need(phases["recipes"][p]["stage_alignment"][stage] == {
                    "entry_X": entry, "entry_Y": entry, "exit_X": exit_, "exit_Y": exit_},
                    "authenticated existing affine alignments")
            exterior = [(a, 1) for a in AXES[9:9 + 8 * stage]]
            if zero:
                old = [] if stage == 0 else [(a, 1) for a in AXES[:1 + 8 * stage]] + [(1, -1)]
                old_x = old_y = old
                local_x = local_y = exterior
                new_x = new_y = [(a, 1) for a in AXES[:9 + 8 * stage]]
                local_out_x = local_out_y = [(a, 1) for a in AXES[:9]] + exterior
            else:
                old_x = [(q, 1)] if stage == 0 else [(a, 1) for a in AXES[:1 + 8 * stage]]
                old_y = [] if stage == 0 else old_x + [(q, -1)]
                local_x, local_y = [(q, 1)] + exterior, exterior
                new_x = [(a, 1) for a in AXES[:9 + 8 * stage]]
                new_y = new_x + [(q, -1)]
                local_out_x = [(a, 1) for a in AXES[:9]] + exterior
                local_out_y = local_out_x + [(q, -1)]
            for old, loc, new, locout in ((old_x, local_x, new_x, local_out_x),
                                         (old_y, local_y, new_y, local_out_y)):
                need(signature(routed(cols, old), act(cols, entry)) == signature(loc),
                     "literal native entrance phase")
                need(signature(locout, act(cols, exit_)) == signature(routed(cols, new)),
                     "literal native exit phase")
                identities += 2
            routes[f"{stage}:{p}"] = dict(stage=stage, port=p, zero_label=zero,
                local_label=0 if zero else q, virtual_normal=q,
                owner_right_matrix_columns=list(cols), logical_payload_translation=0,
                entry_payload_translation=entry, exit_payload_translation=exit_,
                exterior_axis_indices=list(range(9, 9 + 8 * stage)),
                global_input_rank=[0, 0] if zero and stage == 0 else
                    [8 * stage, 8 * stage] if zero else [1 + 8 * stage, 8 * stage],
                global_output_rank=[9 + 8 * stage, 9 + 8 * stage - (not zero)])
    need(identities == 4608, "complete phase identity census")
    return routes, identities


def virtual_native(native):
    def monomial(offset=0):
        return dict(matrix_rows=list(1 << i for i in range(9)), quadratic_rows=[0] * 9,
                    linear_Z4=[0] * 9, offset=offset, phase=0)
    out = {}
    for sign in (1, -1):
        recipe = dict(rank=1, left=monomial(0 if sign == 1 else 1), right=monomial())
        actual, expected = native.recipe(recipe), (("C", 1, sign),)
        native.equal(actual, expected, "virtual normal native line including phase")
        for col in range(512):
            need(native.state(actual, col) == native.state(expected, col), "Gaussian line column")
        native.equal(native.fourier(9) + actual, actual + native.fourier(9), "virtual line FULL commutation")
        need(native.state(actual + (("phase", 1),)) != native.state(expected), "effective native phase control")
        need(native.state(actual) != native.state((("C", 1, -sign),)), "effective native direction control")
        out[str(sign)] = recipe
    native.equal(native.fourier(9) + native.recipe(out["-1"]),
                 tuple(("C", 1 << i, 1) for i in range(1, 9)),
                 "FULL9 to eight-axis exterior")
    return out


def frame_walk(program, word, c):
    current = word["start"].copy()
    query = None
    for e in program:
        tag = e[0]
        if tag == "climb":
            _, _, r, old, new, _ = e
            need(current[r] == old, "literal climb source gauge")
            current[r] = new
        elif tag == "warp" and e[1][0] == "L":
            _, reg, _, old, new = e
            need(current[reg[1]] == old, "literal warp source gauge")
            current[reg[1]] = new
        elif tag == "gaussian_scalar":
            _, op, t, s, packed, frame = e
            for v in (Fraction(packed[0], packed[1]), Fraction(packed[2], packed[3])):
                need(v.denominator & (v.denominator - 1) == 0, "Gaussian dyadic coefficient")
            if op == "clear":
                need(t == ["C", 0] and frame in (0, 1), "owned query clear")
                query = frame
                continue
            if op == "add":
                need(t != s, "nonaliasing Gaussian ADD")
            for reg in (t, s):
                if reg is None:
                    continue
                need(current[reg[1]] == frame if reg[0] == "L" else
                     reg == ["C", 0] and query == frame, "actual Gaussian common frame")
    need(current == word["final"], "literal local native endpoint")


def code_matrix(s, c, word, programs):
    R, _, _, _, _, _ = c.clean_reconstruction(word, programs)
    Q = [{**{j: s.G(v) for j, v in row.items()}, 112 + i: s.G(4), 120 + i: s.G(0, 8)}
         for i, row in enumerate(R)]
    QT = [{i: row[p] for i, row in enumerate(Q) if p in row} for p in range(128)]
    need(s.product(Q, QT) == [{i: s.G(8)} for i in range(8)], "actual augmented Gram")
    D = [{j: -a / s.G(4) for j, a in row.items()} for row in s.product(QT, Q)]
    for i, row in enumerate(D):
        s.add(row, {i: s.G(1)})
    need(s.product(D, D) == [{i: s.G(1)} for i in range(128)], "actual involution")
    return D


def local_checks(s, c, word, changed, D, info):
    X = tuple(range(112)) + tuple(info["source_helper_ports"])
    Y = tuple(range(112, 224)) + tuple(info["target_helper_ports"])
    helpers = tuple(i for i in range(632) if i not in set(X + Y))
    need(len(helpers) == 376 and len(set(X + Y)) == 256, "promoted data ownership")
    widths = Counter(len(word["frames"][word["final"][h]]) - len(word["frames"][word["start"][h]]) for h in helpers)
    # All promoted roles are literally I -> FULL9, not inferred from a count.
    need(all(word["start"][h] == 0 and word["final"][h] == 1 for h in X[112:] + Y[112:]), "promoted width9 roles")
    need(sum(widths.values()) == 376 and sum(k * v for k, v in widths.items()) == 2990, "remaining helper inventory")
    checks = {}
    for orientation, events in changed.items():
        frame_walk(events, word, c)
        native_profile = c.core_frame_check(word, [e for e in events if e[0] != "gaussian_scalar"])
        need(native_profile == Counter({1: 2440, 2: 725, 3: 224, 4: 102, 5: 20}), "recounted complete native core profile")
        state, bits_ = s.replay(events)
        for r in range(632):
            want = {(r, ()): s.G(1)}
            if r in X:
                p = X.index(r)
                if orientation == "forward":
                    want = {(X[j], ()): a for j, a in D[p].items()}
                else:
                    s.add(want, {(Y[p], ()): s.G(-1)})
            elif r in Y:
                p = Y.index(r)
                if orientation == "forward":
                    s.add(want, {(X[j], ()): a for j, a in D[p].items()})
                else:
                    want = {(Y[j], ()): a for j, a in D[p].items()}
            need(state["L", r] == want, "actual local endpoint column")
        need(all(not row for reg, row in state.items() if reg[0] in ("C", "Z")), "owned cleanup")
        checks[orientation] = dict(independent_input_columns=632, arbitrary_helpers=376,
            scalar_prefix_log2=bits_, scalar_invoice=s.gaussian_bill(events, c),
            recounted_native_rank_profile=dict(sorted(native_profile.items())))
    return X, Y, helpers, widths, checks


def compose_two(s, D, X, Y, helpers, programs, routes, first="forward", second="backward"):
    """Exact operator check over all independent inputs and formal cover words.

    Every local word is replayed independently above. This replay composes their
    resulting full operators on disjoint helper namespaces. The cover-word
    representation is exact for arbitrary field functions; it never assumes the
    different port routes commute or are equal.
    """
    state = [{(i, ()): s.G(1)} for i in range(1008)]
    def add(d, v, q=s.G(1)):
        s.add(d, v, q)
    def owner(row, p):
        if p is None:
            return row.copy()
        op = p + 1
        out = {}
        for (i, w), a in row.items():
            # All rho(1,p) are involutions. Identical zero-port routes share ID.
            op = 113 if p >= 112 else p + 1
            nw = w[1:] if w and w[0] == op else (op,) + w
            add(out, {(i, nw): a})
        return out
    def local(source, orientation, routed_call=False):
        pre = [owner(source[i], i % 128 if routed_call else None) for i in range(256)]
        out = [r.copy() for r in pre]
        if orientation == "forward":
            for p in range(128):
                z = {}
                for j, a in D[p].items():
                    add(z, pre[j], a)
                out[p] = z
                add(out[128 + p], z)
        else:
            for p in range(128):
                add(out[p], pre[128 + p], s.G(-1))
                out[128 + p] = {}
                for j, a in D[p].items():
                    add(out[128 + p], pre[128 + j], a)
        return [owner(out[i], i % 128 if routed_call else None) for i in range(256)] + source[256:]
    first_out = local(state, first)
    actual = local(first_out, second, True)
    # Independently assemble the two conjugated block operators by distributing
    # input columns. In the required F0, B1 case, X is exactly -Y for arbitrary
    # D0,D1; Y=D1 Y + D1 D0 X. D1 is rho^-1 D rho.
    need((first, second) == ("forward", "backward"), "required first two orientations")
    expected = [{(128 + p, ()): s.G(-1)} for p in range(128)]
    for p in range(128):
        row = {}
        for j, a in D[p].items():
            from_y = owner(owner({(128 + j, ()): s.G(1)}, j), p)
            add(row, from_y, a)
            for k, b in D[j].items():
                from_x = owner(owner({(k, ()): s.G(1)}, j), p)
                add(row, from_x, a * b)
        expected.append(row)
    expected += state[256:]
    need(actual == expected, "two-call operator on all1008 independent inputs")
    need(all(actual[i] == state[i] for i in range(256, 1008)), "two disjoint arbitrary helper banks restored")
    bad = local(first_out, "forward", True)
    need(bad != expected, "effective wrong bank-orientation control")
    return dict(input_columns=1008, data_columns=256, arbitrary_helper_columns=752,
                cover_action="Exact formal involutory owner words; distinct actual port maps not identified",
                endpoint="X_out=-Y_in; Y_out=D_1 Y_in + D_1 D_0 X_in",
                second_defect="D_1=rho_1^-1 D rho_1; port routes act separately",
                residual_not_decoded=True,
                nonzero_operator_terms=sum(len(row) for row in actual))


def nine_geometry(template):
    """Compile explicit data pending-axis intervals and every added inverse line."""
    levels = [-1] * 4
    recipe = []
    intervals = []
    lines = []
    for event in template["execution_schedule"]:
        kind = event["kind"]
        if kind == "local_cover_sweep":
            stage = event["stage"]
            local = next(e for e in template["recipe"] if e.get("kind") == "local" and e["stage"] == stage)
            pair = local["pair"]
            need(levels[pair] == stage - 1, "active data reaches exact local prefix")
            if stage:
                for bank in (2 * pair, 2 * pair + 1):
                    for p in range(112, 128):
                        line = dict(kind="native_line", before_stage=stage, bank=bank, port=p,
                                    family=128 * bank + p, label=1, sign=-1, rank=1,
                                    old_prefix_rank=1 + 8 * stage, new_prefix_rank=8 * stage,
                                    recipe="virtual:-1")
                        lines.append(line)
                        recipe.append(line)
            recipe.append(dict(kind="local", stage=stage, pair=pair, reverse=local["reverse"],
                per_call_rank_profile={1: 2440, 2: 725, 3: 224, 4: 102, 5: 20},
                remaining_helper_count=376, productive_ports_per_bank=128))
            levels[pair] = stage
        elif kind == "idle_cover_sweep":
            pair, low, high = event["pair"], event["from_level"], event["to_level"]
            need(levels[pair] == low, "idle interval chronological entrance")
            lo = 0 if low == -1 else 9 + 8 * low
            hi = 9 + 8 * high
            # First idle catchup adds virtual r to both formerly zero banks.
            # Later idle intervals contain only standard untouched axes.
            if hi > lo:
                for bank in (2 * pair, 2 * pair + 1):
                    interval = dict(bank=bank, from_level=low, to_level=high,
                        axis_indices=list(range(lo, hi)), rank=hi - lo,
                        zero_ports=list(range(112, 128)))
                    intervals.append(interval)
                    recipe.append(dict(kind="zero_port_idle_interval", **interval))
            levels[pair] = high
        elif kind == "bridge":
            need(levels[event["dst"]] == levels[event["src"]], "literal zero-bank bridge gauges match")
            recipe.append({**event, "ports": 128, "zero_port_frame": f"FULL_first_{9 + 8 * levels[event['dst']]}"})
        elif kind == "terminal_Y_translations":
            recipe.append(dict(kind="terminal_Y_translations", original_ports=list(range(112)),
                               zero_port_translation=0))
        elif kind == "terminal":
            need(levels == [8] * 4, "all bank outputs reached73")
            recipe.append(dict(kind="signed_exchange", pairs=4, ports=128))
    need(levels == [8] * 4 and len(lines) == 256, "eight literal32-line catches")
    need(sum(x["rank"] for x in intervals) == 438, "exact zero-port idle capacity perport")
    need(Counter(x["rank"] for x in intervals) == Counter({8: 6, 16: 2, 17: 2, 32: 2, 33: 2, 48: 2, 49: 2}),
         "complete idle-window rank distribution")
    return dict(status="PASS_NINE_STAGE_ZERO_PORT_DATA_GEOMETRY", m=73,
        productive_data_fields_per_replica=1024, zero_port_data_fields_per_replica=128,
        zero_port_final_gauges=["FULL73"] * 128,
        original_port_terminal_gauges="Inherited postexchange X=FULL73 C_q^-1, Y=FULL73",
        zero_port_idle_capacity_per_label=438, added_idle_capacity=7008,
        added_native_line_children=256,
        zero_port_idle_intervals=intervals, ordered_recipe=recipe,
        qualification="Productivity requires restoration of the ordered D residual; these are correct final native gauges only.")


def controls(routes, geometry):
    rejected = []
    def reject(name, fn):
        try:
            fn()
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("ineffective control: " + name)
    r = routes["1:112"]
    cols = tuple(r["owner_right_matrix_columns"])
    full9 = [(a, 1) for a in AXES[:9]]
    exterior8 = [(a, 1) for a in AXES[9:17]]
    reject("omit virtual inverse line", lambda: need(signature(routed(cols, full9)) == signature(exterior8), "missing line"))
    reject("wrong virtual line direction", lambda: need(signature(routed(cols, full9 + [(1, 1)])) == signature(exterior8), "wrong line sign"))
    reject("extra Gaussian global phase", lambda: need(signature(exterior8, global_phase=1) == signature(exterior8), "wrong global phase"))
    reject("use identity owner route at stage1", lambda: need(signature(full9 + [(1, -1)]) == signature(exterior8), "wrong stage route"))
    reject("apply final catchdown without restoration", lambda: need(signature([(a, 1) for a in AXES] + [(1, -1)]) == signature([(a, 1) for a in AXES]), "wrong terminal FULL claim"))
    reject("claim no zero-port idle r charge", lambda: need(geometry["added_idle_capacity"] == 16 * 432, "six omitted first-idle r axes"))
    return rejected


def dump_gzip(path, value):
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    path.write_bytes(gzip.compress(payload, mtime=0))
    return sha256(payload).hexdigest()


def main():
    need(__debug__, "Assertions must remain enabled in retained sources")
    ap = ArgumentParser(description=__doc__)
    ap.add_argument("--followup", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    src = a.followup.resolve()
    c = module(src / next(iter(PINS)), "bound_modern_component", next(iter(PINS.values())))
    producer_path = src / list(PINS)[1]
    s = module(producer_path, "bound_symmetric_producer", list(PINS.values())[1])
    inp = src / "artifact/recovered-involutory/modern-source/inputs"
    need(digest(inp / "NATIVE-RECEIPT.json") == c.NATIVE_RECEIPT_SHA, "native receipt pin")
    receipt = read(inp / "NATIVE-RECEIPT.json")
    symroot = src / "artifact/recovered-involutory/symmetric-extension-review/symmetric-extended-results"
    need(digest(symroot / "RESULT.json") == SYMMETRIC_RESULT_SHA, "frozen symmetric receipt pin")
    symresult = read(symroot / "RESULT.json")
    need(symresult["script_sha256"] == PINS[list(PINS)[1]], "retained symmetric source binding")
    legacy = src / "artifact/integer-mult-bounds/research/native-source-codes"
    # Import from authenticated source bytes rather than allowing stale pyc.
    for name, h in c.LEGACY_SHA.items():
        need(digest(legacy / name) == h, "native interpreter pin")
    native = module(legacy / "native_verify.py", "bound_gaussian_native", c.LEGACY_SHA["native_verify.py"])
    virtual = virtual_native(native)
    phase_paths = list((src / "artifact").rglob("DATA-PHASES.json"))
    phase_path = next(p for p in phase_paths if digest(p) == "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa")
    phases = read(phase_path)
    template_path = src / "artifact/live-source/research/staged544-producer-return/inputs/TEMPLATE.json.gz"
    need(digest(template_path) == TEMPLATE_SHA, "frozen complete controller template pin")
    template = read(template_path)
    need(template["exact_data_phase_recipe_sha256"] == digest(phase_path), "controller phase pin")
    result = dict(status="PASS_LITERAL_TWO_CALL_AND_NINE_STAGE_ZERO_PORT_GEOMETRY",
        source_pins={**PINS, str(phase_path.relative_to(src)): digest(phase_path),
                     str(template_path.relative_to(src)): digest(template_path),
                     str((symroot / "RESULT.json").relative_to(src)): SYMMETRIC_RESULT_SHA},
        verifier_sha256=digest(Path(__file__)),
        providers={}, native_virtual_line=dict(recipes=virtual, gaussian_basis_columns=1024,
            phase_controls_rejected=2, direction_controls_rejected=2),
        scope="Exact finite data transitions and local contracts. No residual consumer, chronological helper allocator, full invoice, or kappa increase.")
    first_routes = None
    for name, item in receipt["providers"].items():
        loc = inp / "native-cache" / item["word_sha256"] / "local"
        for basename in ("CANONICAL-WORD.json.gz", "LOCAL-PROGRAMS.json.gz", "CLIFFORD-RECIPES.json", "RESIDUAL-ADAPTERS.json"):
            need(digest(loc / basename) == item["complete_native_files"]["local/" + basename], "actual provider source")
        word, original = read(loc / "CANONICAL-WORD.json.gz"), read(loc / "LOCAL-PROGRAMS.json.gz")
        raw = gzip.decompress((symroot / f"PROGRAMS-{name}.json.gz").read_bytes())
        info = symresult["providers"][name]
        need(sha256(raw).hexdigest() == info["payload_sha256"] == SYMMETRIC_PROGRAM_PAYLOAD_SHA, "symmetric emitted word binding")
        changed = json.loads(raw)
        D = code_matrix(s, c, word, original)
        X, Y, helpers, widths, local = local_checks(s, c, word, changed, D, info)
        routes, identities = make_routes(phases, word["ports"])
        if first_routes is not None:
            need(routes == first_routes, "providers share exact global data routes")
        first_routes = routes
        two = compose_two(s, D, X, Y, helpers, changed, routes)
        calls = []
        for stage, orientation in enumerate(("forward", "backward")):
            if stage:
                for bank in range(2):
                    for p in range(112, 128):
                        calls.append(dict(kind="native_line", family=bank * 128 + p,
                            sign=-1, label=1, rank=1, old="FULL9", new="FULL9 C_1^-1", recipe=virtual["-1"]))
            mapping = {r: i for i, r in enumerate(X + Y)}
            mapping.update({r: 256 + 376 * stage + i for i, r in enumerate(helpers)})
            need(len(set(mapping.values())) == 632, "injective actual local role mapping")
            calls.append(dict(kind="literal_local_call", stage=stage, orientation=orientation,
                local_to_global=mapping, owner_routes=[routes[f"{stage}:{p}"] for p in range(128)],
                literal_program=changed[orientation], owned_zero_buffers=91))
        bill = dict(local_rank_profile={1: 4880, 2: 1450, 3: 448, 4: 204, 5: 40},
                    extra_rank1_children=32, combined_rank_mass=2 * 5070 + 32,
                    extra_scalar_primitives=0,
                    extra_rank_zero_entrance_exit_payload_translations=0,
                    extra_native_line_left_payload_translations=32,
                    extra_native_line_nonidentity_right_adapters=0,
                    zero_port_nonidentity_owner_route_applications=64,
                    owned_zero_buffers=91, independent_arbitrary_helpers=752,
                    routing_scope="The64 extra zero-port owner applications comprise16 ports times2 banks times entrance/exit at stage1. Each inverse line additionally uses one explicit left payload translation; its right monomial adapter is identity. Full tape/address and precision admission remains open.")
        result["providers"][name] = dict(local_checks=local, two_call_operator=two,
            actual_source_bank=list(X), actual_target_bank=list(Y), remaining_helper_inventory=dict(sorted(widths.items())),
            remaining_helper_width_sum=2990, phase_polynomial_identities=identities,
            two_call_bill=bill, emitted_two_call_payload_sha256=dump_gzip(a.out / f"TWO-CALL-{name}.json.gz", calls))
        print("PASS_TWO_CALL", name, "1008 independent columns;32 extra H1;4608 native phase identities", flush=True)
    geometry = nine_geometry(template)
    result["nine_stage_geometry"] = {k: v for k, v in geometry.items() if k not in ("ordered_recipe", "zero_port_idle_intervals")}
    result["rejection_controls"] = controls(first_routes, geometry) + ["wrong backward bank orientation"]
    result["routes_payload_sha256"] = dump_gzip(a.out / "ROUTES.json.gz", first_routes)
    result["geometry_payload_sha256"] = dump_gzip(a.out / "NINE-STAGE-DATA-GEOMETRY.json.gz", geometry)
    (a.out / "RESULT.json").write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(result["status"], flush=True)


if __name__ == "__main__":
    main()
