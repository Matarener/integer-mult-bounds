"""Exact support certificates for immutable, fixed-chart rank-one controllers.

The frozen backward program is interpreted in its retained normalized logical
ABI, with physical_add omitted and all warp words specialized to a common fixed
vector.  This is a necessary quotient, not a new physical implementation.

Each added provider stays in one rank-one chart and may add arbitrary scalar
multiples of its immutable payload at every existing coframed contact.  The
native word is unchanged.  Helper restoration is granted optimistically; Y
must be restored by these contacts or initial ground preconditioning, without
a separate free final-Y cleanup.  Providers may not move/reframe, update their
payloads, or add native operations.  run() performs no writes.
"""

from collections import Counter
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path


WORD_SHA256 = "934fea11e51f674ce2031b7d3127b994a921a9d83317b00359292752563a1775"
R_SHA256 = "7b33b6dfb494c6eafe6d87a08d6a2c2e0681e56429495b2b27949040f0f63cd1"
PUBLIC = 632
PORTS = 112
MODES = 8
ZERO = Fraction(0)


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _owner(operand):
    _require(isinstance(operand, list) and len(operand) == 2,
             "invalid field operand")
    kind, index = operand
    _require(kind in ("L", "C") and isinstance(index, int) and index >= 0,
             "invalid field owner")
    _require(kind != "L" or index < PUBLIC, "public owner out of range")
    return index if kind == "L" else PUBLIC + index


def _add(destination, source, coefficient):
    # A copy also makes self-add semantics explicit.
    for key, value in list(source.items()):
        result = destination.get(key, ZERO) + coefficient * value
        if result:
            destination[key] = result
        else:
            destination.pop(key, None)


def _canonical_sha(value):
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def _chart_support(rows, controls, actual):
    support = {frame: set() for frame in actual}
    for port, row in enumerate(rows[:PORTS]):
        for control, coefficient in row.items():
            if coefficient:
                support[controls[control]["frame"]].add(port)
    return support


def _validate_weights(support, weights):
    _require(weights and all(weight > 0 for weight in weights.values()),
             "weights must be strictly positive on the target support")
    loads = {frame: sum((weights.get(port, ZERO) for port in ports), ZERO)
             for frame, ports in support.items()}
    _require(loads and max(loads.values()) <= 1,
             "a chart covers target weight greater than one")
    return sum(weights.values(), ZERO), max(loads.values())


def _cover_certificate(support, target):
    # The actual source has only one nonsingleton chart.  The construction is
    # still checked against every chart rather than assuming this shape.
    broad = set().union(*(ports & target for ports in support.values()
                          if len(ports) > 1))
    _require(broad, "missing nonsingleton support for the frozen certificate")
    weights = {port: Fraction(1, len(broad)) if port in broad else Fraction(1)
               for port in target}
    total, maximum = _validate_weights(support, weights)
    _require(total.denominator == 1, "nonintegral frozen cover bound")
    return {
        "target_ports": sorted(target),
        "target_weights": {str(port): str(weight)
                           for port, weight in sorted(weights.items())},
        "total_weight": str(total),
        "maximum_chart_weight": str(maximum),
        "minimum_distinct_fixed_chart_providers": int(total),
    }, weights


def _expect_invalid(support, weights, label):
    try:
        _validate_weights(support, weights)
    except ValueError as error:
        _require(str(error) == "a chart covers target weight greater than one",
                 label + ": unexpected failure")
        return {"rejected": True, "reason": str(error)}
    raise ValueError(label + ": invalid support certificate was accepted")


def run(word_path, R_path):
    """Return a compact, reproducible JSON certificate; do not write files."""
    word_bytes = Path(word_path).read_bytes()
    R_bytes = Path(R_path).read_bytes()
    word_sha = hashlib.sha256(word_bytes).hexdigest()
    R_sha = hashlib.sha256(R_bytes).hexdigest()
    _require(word_sha == WORD_SHA256, "wrong frozen backward word")
    _require(R_sha == R_SHA256, "wrong frozen mode matrix")
    source = json.loads(gzip.decompress(word_bytes))
    R = [[Fraction(value) for value in row] for row in json.loads(R_bytes)]
    _require(len(R) == MODES and all(len(row) == PORTS for row in R),
             "wrong mode matrix dimensions")
    gram = [[sum((R[i][j] * R[k][j] for j in range(PORTS)), ZERO)
             for k in range(MODES)] for i in range(MODES)]
    _require(all(gram[i][k] == (56 if i == k else 0)
                 for i in range(MODES) for k in range(MODES)),
             "the exact source normalization is RR^T=56I")
    _require(all(any(row[j] for row in R) for j in range(PORTS)),
             "a full-mode target row is zero")

    events = source["programs"]["backward"]
    canonical = source["canonical"]
    _require(len(canonical["start"]) == PUBLIC
             and len(canonical["final"]) == PUBLIC, "wrong public interface")
    frame_bases = canonical["frames"]
    _require(all(len(frame_bases[canonical["start"][PORTS+j]]) == 0
                 and len(frame_bases[canonical["final"][PORTS+j]]) == 8
                 for j in range(PORTS)), "Y boundary is not ground to rank eight")
    allowed = {"scalar", "warp", "climb", "center", "phase", "adapter",
               "residual_adapter", "physical_add"}
    _require(all(event[0] in allowed for event in events), "unknown source opcode")
    owners = [_owner(operand) for event in events if event[0] == "scalar"
              for operand in event[1] if isinstance(operand, list)]
    nroles = max(owners + [PUBLIC]) + 1
    frames = list(canonical["start"]) + [None] * (nroles - PUBLIC)
    rank_one = {i for i, basis in enumerate(frame_bases) if len(basis) == 1}

    # A unit impulse's suffix column changes at a read of its owner, scale,
    # overwrite, clear, or warp. ADD-to-owner alone has unit diagonal. Together
    # with rank-one arrivals these cuts cover every chronological contact;
    # duplicate response columns are harmless and no coefficient grid is used.
    sites = {(0, owner, frame) for owner, frame in enumerate(frames)
             if frame in rank_one}
    for i, event in enumerate(events):
        kind = event[0]
        if kind == "scalar":
            operation = event[1]
            opcode, destination = operation[0], _owner(operation[1])
            _require(opcode in ("clear", "copy", "add", "scale"),
                     "unknown scalar opcode")
            if opcode == "clear":
                frames[destination] = event[2]
            if opcode in ("copy", "add"):
                origin = _owner(operation[2])
                if frames[origin] in rank_one:
                    sites.add((i+1, origin, frames[origin]))
            if opcode in ("copy", "clear", "scale"):
                if frames[destination] in rank_one:
                    sites.add((i+1, destination, frames[destination]))
        elif kind in ("warp", "climb", "center"):
            if kind == "warp":
                destination, frame = _owner(event[1]), event[4]
            elif kind == "climb":
                destination, frame = event[2], event[4]
            else:
                destination, frame = PUBLIC + event[1], event[3]
            frames[destination] = frame
            if frame in rank_one:
                sites.add((i+1, destination, frame))

    controls = [{"boundary": boundary, "owner": owner, "frame": frame}
                for boundary, owner, frame in sorted(sites)]
    actual = {control["frame"] for control in controls}
    _require(len(actual) == 115 and len(controls) == 1090,
             "frozen rank-one contact census changed")
    by_boundary = {}
    for number, control in enumerate(controls):
        by_boundary.setdefault(control["boundary"], []).append(
            (control["owner"], number))

    rows = [{} for _ in range(nroles)]
    for i, event in enumerate(events):
        for owner, number in by_boundary.get(i, []):
            rows[owner][number] = rows[owner].get(number, ZERO) + 1
        if event[0] != "scalar":
            continue  # Fixed-vector, normalized ABI; omit physical_add.
        operation = event[1]
        opcode, destination = operation[0], _owner(operation[1])
        if opcode == "clear":
            rows[destination] = {}
        elif opcode == "copy":
            rows[destination] = dict(rows[_owner(operation[2])])
        elif opcode == "add":
            _add(rows[destination], rows[_owner(operation[2])],
                 Fraction(operation[3], operation[4]))
        elif opcode == "scale":
            coefficient = Fraction(operation[2], operation[3])
            rows[destination] = {key: value * coefficient
                                 for key, value in rows[destination].items()
                                 if value * coefficient}
    for owner, number in by_boundary.get(len(events), []):
        rows[owner][number] = rows[owner].get(number, ZERO) + 1
    raw_support = _chart_support(rows, controls, actual)

    # Source endpoint: X'=X-CY, Y'=Y, H'=H, C=I-R^T R/4.
    # Initial ground Y preconditioning can cancel total final Y, but then its
    # X response contributes C*deltaY. Thus Z is the necessary restored-Y
    # response, including cancellations jointly across different providers.
    for i in range(PORTS):
        for j in range(PORTS):
            coefficient = Fraction(i == j) - sum(
                (R[k][i] * R[k][j] / 4 for k in range(MODES)), ZERO)
            if coefficient:
                _add(rows[i], rows[PORTS+j], coefficient)
    support = _chart_support(rows, controls, actual)
    _require(Counter(map(len, support.values())) == {0: 2, 1: 112, 12: 1},
             "unexpected restored-Y support shape")
    _require(support[114] == support[115] == set()
             and support[137] == {31, 33, 49, 55, 68, 74, 80, 83, 85, 88, 98, 101},
             "exceptional chart supports changed")

    one_target = {i for i, value in enumerate(R[5]) if value}
    _require(len(one_target) == 56, "mode-five target support changed")
    one, one_weights = _cover_certificate(support, one_target)
    full, full_weights = _cover_certificate(support, set(range(PORTS)))
    _require(one["minimum_distinct_fixed_chart_providers"] == 50
             and full["minimum_distinct_fixed_chart_providers"] == 101,
             "unexpected fixed-chart cover bound")

    # These alter semantic boundary/coverage obligations, not numerical noise.
    dropped_Y = _expect_invalid(raw_support, one_weights,
                                "dropped final-Y restoration")
    dropped_Y["raw_chart_114_weight"] = str(sum(
        (one_weights.get(port, ZERO) for port in raw_support[114]), ZERO))
    artificial = dict(support)
    artificial[-1] = set(one_target)
    extra_chart = _expect_invalid(artificial, one_weights,
                                 "artificial all-target chart")
    extra_chart["artificial_chart_weight"] = str(sum(one_weights.values(), ZERO))

    return {
        "schema": "active-rank1-controller-v1",
        "source": {"word_sha256": word_sha, "R_sha256": R_sha,
                   "direction": "backward", "physical_add": "omitted"},
        "scope": {
            "quotient": "common fixed vector; retained normalized adapter ABI",
            "controller": "immutable payloads; one fixed rank-one chart per provider",
            "contacts": "all coframed chronological additive intervals; native word unchanged",
            "restoration": "final Y restored jointly; arbitrary helper cleanup granted",
            "excluded": ["provider movement or reframing", "payload updates",
                         "additional native operations", "free final-Y cleanup"],
            "claim": "necessary fixed-chart support bound, not a global feedback bound or new kappa",
        },
        "census": {"public_fields": PUBLIC, "scalar_and_owned_fields": nroles,
                   "events": len(events), "mode_matrix_shape": [MODES, PORTS],
                   "mode_gram_diagonal": 56, "all_mode_columns_nonzero": True,
                   "rank_one_frame_inventory": len(rank_one),
                   "actual_rank_one_charts": len(actual),
                   "contact_intervals": len(controls),
                   "omitted_physical_add_events": sum(e[0] == "physical_add" for e in events)},
        "controls_sha256": _canonical_sha(controls),
        "actual_rank_one_frame_bases": {str(frame): frame_bases[frame]
                                        for frame in sorted(actual)},
        "output_nulling_invariant": "Z=deltaX+(I-R^T R/4)*deltaY",
        "chart_Z_support": {str(frame): sorted(support[frame]) for frame in sorted(actual)},
        "one_mode_cover": one,
        "full_eight_mode_cover": full,
        "semantic_negative_controls": {
            "dropped_final_Y_restoration": dropped_Y,
            "artificial_all_target_chart": extra_chart,
        },
    }
