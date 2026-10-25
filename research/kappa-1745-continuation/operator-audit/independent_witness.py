#!/usr/bin/env python3
"""Independent dense-matrix witness against the previous claim's actual MOVES.

Data authentication/projection is reused from Nick Petalas's PR3187 source.py.
No imported operator, row-update, or replay implementation is used. Elementary
8x8 matrices over Z[i] are composed by ordinary dense matrix multiplication.
This is a counterexample in the g=I subcase, not a complete supplier verifier.
"""
import gzip
import hashlib
import importlib.util
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCOPE = HERE.parent
RESEARCH = SCOPE.parent
SOURCE = HERE / "checkout/research/rank7-idle-star-stream-obstruction/source.py"
MOVES = RESEARCH / "kappa-next-regime/sources/PR3959/research/rank7-idle-frame-select/MOVES.json.gz"
MOVES_SHA = "01e8417b90783f707cd18871be7c615eb9162f356460f07963b5198522aa692b"
ZERO, ONE = (0, 0), (1, 0)
UNITS = (ONE, (0, 1), (-1, 0), (0, -1))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def parity(x, y):
    return (int(x) & int(y)).bit_count() & 1


def identity():
    return [[ONE if r == c else ZERO for c in range(8)] for r in range(8)]


def multiply(left, right):
    result = [[ZERO for _ in range(8)] for _ in range(8)]
    for r in range(8):
        for c in range(8):
            re = im = 0
            for k in range(8):
                a, b = left[r][k]
                d, e = right[k][c]
                re += a * d - b * e
                im += a * e + b * d
            result[r][c] = (re, im)
    return result


def diagonal(stream, exponent):
    result = identity()
    result[stream][stream] = UNITS[exponent % 4]
    return result


def transvection(dst, src, coefficient):
    require(dst != src and type(coefficient) is int, "integer transvection")
    result = identity()
    result[dst][src] = (coefficient, 0)
    return result


def make_hosts(ctx):
    hosts, occupied = defaultdict(list), defaultdict(set)
    for time, helper, owner, child, port, offset in ctx["rows"]:
        require(owner == port == 0, "literal owner-0 port-0 projection")
        stage, replica = ctx["order"][time]
        provider = ctx["providers"][ctx["dispatch"][(stage, replica % 74)]]
        width = provider["widths"][helper]
        axes = [int(x) for x in ctx["recipe"]["idle_children"][child]["orthogonal_axes"]]
        slots = set(range(offset, offset + width))
        require(0 <= offset <= offset + width <= len(axes), "host range")
        require(not slots.intersection(occupied[child]), "disjoint host slices")
        occupied[child].update(slots)
        stream = 2 * ctx["plan"]["pairs"][str(child)] + ctx["plan"]["sides"][str(child)]
        hosts[time].append((stream, axes[offset:offset + width]))
    residual = {}
    for child, record in enumerate(ctx["recipe"]["idle_children"]):
        require(occupied[child] == set(range(len(occupied[child]))), "compact host prefix")
        residual[child] = [int(x) for pos, x in enumerate(record["orthogonal_axes"])
                           if pos not in occupied[child]]
    return hosts, residual


def apply_declared_moves(ctx, residual, moves):
    result = {child: list(axes) for child, axes in residual.items()}
    recipe = ctx["recipe"]
    translations = [int(stage[key]) for stage in recipe["stage_alignment"]
                    for key in ("entry_X", "exit_X", "entry_Y", "exit_Y")]
    translations.append(int(recipe["terminal_Y_translation"]))
    for donor, receiver, axis in moves:
        require(donor != receiver and axis in result[donor], "owned donor axis")
        guards = result[receiver] + translations + [
            int(recipe["idle_children"][child]["translation_after"])
            for child in (donor, receiver)]
        require(all(parity(axis, v) == 0 for v in guards), "declared orthogonality rule")
        result[donor].remove(axis)
        result[receiver].append(axis)
    require(all(len(axes) <= 51 for axes in result.values()), "rank cap")
    for axes in result.values():
        require(all(parity(x, y) == (i == j) for i, x in enumerate(axes)
                    for j, y in enumerate(axes)), "orthonormal final axes")
    require(Counter(x for a in residual.values() for x in a) ==
            Counter(x for a in result.values() for x in a), "axis multiset")
    return result


def event_matrices(event, ctx, residual, character):
    kind = event["kind"]
    qbit = parity(character, ctx["recipe"]["q"])
    if kind == "local_cover_sweep":
        stage = event["stage"]
        local = [e for e in ctx["template"]["recipe"]
                 if e["kind"] == "local" and e["stage"] == stage]
        require(len(local) == 1, "unique local stage")
        local = local[0]
        pair = local["pair"]
        for side in range(2):
            before = ((1 - side) * qbit if stage == 0 else
                      (character & ((1 << (9 + 8 * (stage - 1))) - 1)).bit_count()
                      - side * qbit)
            yield diagonal(2 * pair + side, -before)
        yield (transvection(2 * pair, 2 * pair + 1, -1) if local["reverse"]
               else transvection(2 * pair + 1, 2 * pair, 1))
        for side in range(2):
            after = (character & ((1 << (9 + 8 * stage)) - 1)).bit_count() - side * qbit
            yield diagonal(2 * pair + side, after)
    elif kind == "idle_cover_sweep":
        for side, child in enumerate(event["child_indices"]):
            phase = sum(parity(character, axis) for axis in residual[child])
            phase += 2 * parity(character, ctx["recipe"]["idle_children"][child]["translation_after"])
            yield diagonal(2 * event["pair"] + side, phase)
    elif kind == "bridge":
        d, s, c = event["dst"], event["src"], event["coefficient"]
        yield transvection(2 * d, 2 * s, c)
        yield transvection(2 * s + 1, 2 * d + 1, -c)
    elif kind == "terminal_Y_translations":
        for pair in event["pairs"]:
            yield diagonal(2 * pair + 1, 2 * qbit)
    elif kind == "terminal":
        require(event["pairs"] == 4, "four terminal pairs")
        result = [[ZERO for _ in range(8)] for _ in range(8)]
        for pair in range(4):
            result[2 * pair][2 * pair + 1] = ONE
            result[2 * pair + 1][2 * pair] = (-1, 0)
        yield result
    else:
        raise ValueError("unrecognized data event: " + kind)


def replay(ctx, hosts, residual, character):
    blocks, current = {}, None
    for event in ctx["template"]["execution_schedule"]:
        if event["kind"] in ("bank_padding_cover_sweep", "translate_every_live_family"):
            continue
        if event["kind"] == "local_cover_sweep":
            current = event["stage"]
            require(current not in blocks, "distinct stage blocks")
            blocks[current] = []
        require(current is not None, "event follows a local stage")
        blocks[current].append(event)
    require(set(blocks) == set(range(9)), "all nine stages")
    result = identity()
    for time, (stage, replica) in enumerate(ctx["order"]):
        for stream, axes in hosts.get(time, []):
            element = diagonal(stream, sum(parity(character, axis) for axis in axes))
            result = multiply(element, result)
        if replica == 0:
            for event in blocks[stage]:
                for element in event_matrices(event, ctx, residual, character):
                    result = multiply(element, result)
    return result


def main():
    raw = MOVES.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == MOVES_SHA, "actual prior claim MOVES pin")
    data = json.loads(gzip.decompress(raw))
    require(data["columns"] == ["replica", "port", "donor_child", "receiver_child", "axis"], "move schema")
    moves = [(d, r, int(a)) for owner, port, d, r, a in data["moves"] if owner == port == 0]
    require(len(moves) == 6, "six complete owner-0 port-0 moves")
    spec = importlib.util.spec_from_file_location("authenticated_data_only", SOURCE)
    source = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(source)
    ctx = source.load_context()
    hosts, residual = make_hosts(ctx)
    final = apply_declared_moves(ctx, residual, moves)
    require(replay(ctx, hosts, residual, 0) == replay(ctx, hosts, final, 0) == identity(), "zero-character control")
    rejected = False
    try:
        apply_declared_moves(ctx, residual, [(14, 8, 1 << 100)])
    except ValueError:
        rejected = True
    require(rejected, "foreign-axis control rejects")
    witnesses = []
    for character in sorted({a for _, _, a in moves}):
        before = replay(ctx, hosts, residual, character)
        after = replay(ctx, hosts, final, character)
        scalar = [[UNITS[character.bit_count() % 4] if r == c else ZERO
                   for c in range(8)] for r in range(8)]
        require(before == scalar, "baseline scalar operator")
        differences = [[r, c, before[r][c], after[r][c]] for r in range(8)
                       for c in range(8) if before[r][c] != after[r][c]]
        require(differences, "literal changed-operator witness")
        col = differences[0][1]
        witnesses.append({"character": str(character), "bit": character.bit_length() - 1,
                          "changed_entries": len(differences), "differences": differences,
                          "input_column": col, "input": [ONE if r == col else ZERO for r in range(8)],
                          "expected_output": [before[r][col] for r in range(8)],
                          "actual_output": [after[r][col] for r in range(8)]})
    require(next(w for w in witnesses if w["bit"] == 72)["changed_entries"] == 10,
            "independent agreement on ten-entry public witness")
    source.authenticate()
    require(hashlib.sha256(MOVES.read_bytes()).hexdigest() == MOVES_SHA, "source unchanged")
    report = {"status": "PASS_INDEPENDENT_COUNTEREXAMPLE", "new_kappa": False,
              "prior_complex_claim_supported": False,
              "scope": "Actual previous MOVES, owner=port=0, g=I; exact Gaussian integers and dense matrix composition. Data authentication is reused; operator implementation is independent.",
              "moves_path": str(MOVES.relative_to(RESEARCH.parent)), "moves_sha256": MOVES_SHA,
              "source_authenticator_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "checker_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "moves": moves, "host_rows": len(ctx["rows"]),
              "witnesses": witnesses,
              "controls": {"zero_character_equal": True, "foreign_axis_rejected": rejected},
              "credit": "Nick Petalas PR3187 data/event model; Clear1nsight PR3296/3311 operator obstruction; Erwan/ChaloupeMusic PR4046 continuation audit."}
    (HERE / "INDEPENDENT-WITNESS.json").write_text(json.dumps(report, indent=2) + "\n")
    print("PASS_INDEPENDENT_COUNTEREXAMPLE actual_prior_MOVES six_moves five_characters bit72_changed_entries=10")


if __name__ == "__main__":
    main()
