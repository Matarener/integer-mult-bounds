"""Source-bound height census and exact contract controls; Apache-2.0.

Jose Manuel (jmbarrancoml), with substantial OpenAI Codex assistance.
The emitted functions retain Cinna Davis / icekylinx / DreamingOfClouds credit.
This checker does not establish native endpoint or Gaussian caller correctness.
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter
import copy
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MIXED = "research/staged544-mixed-fourth-entry"
NATIVE = MIXED + "/native/vendor/native/new/code/borrow"
TEMPLATE = MIXED + "/owner/TEMPLATE.json.gz"
FUNCTIONS = ("basis", "reg", "dual", "scalar", "lregs", "expand", "emit")


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def authenticate(override=None):
    pins = json.loads((HERE / "SOURCES.json").read_text())
    result = {}
    for row in pins["files"]:
        if row["usage"] != "input":
            continue
        name = row["path"]
        data = override[name] if override and name in override else (ROOT / name).read_bytes()
        need(digest(data) == row["sha256"], "source bytes: " + name)
        result[name] = data
    return result


def read_json(sources, name):
    data = sources[name]
    return json.loads(gzip.decompress(data) if name.endswith(".gz") else data)


def emitter(source, word):
    """Execute exact selected definitions, without the source's CLI or writes."""
    tree = ast.parse(source)
    definitions = [node for node in tree.body
                   if isinstance(node, ast.FunctionDef) and node.name in FUNCTIONS]
    need(tuple(node.name for node in definitions) == FUNCTIONS, "exact emitter definitions")
    namespace = {"c": word, "frames": word["frames"],
                 "v": word["v"], "n": 2 * word["v"] + word["R"]}
    # Retain predecessor assertions even when this audit runs with -O.
    code = compile(ast.Module(body=definitions, type_ignores=[]),
                   NATIVE + "/bw_emit.py", "exec", optimize=0)
    exec(code, namespace)
    return namespace["emit"]


def bind_canonical(source, original, retained):
    """Run the transport's exact construction prefix, excluding later replay/I/O."""
    tree = ast.parse(source)
    basis = next(node for node in tree.body
                 if isinstance(node, ast.FunctionDef) and node.name == "basis")
    run = next(node for node in tree.body
               if isinstance(node, ast.FunctionDef) and node.name == "run")
    stops = [i for i, node in enumerate(run.body) if isinstance(node, ast.Assign)
             and any(isinstance(target, ast.Name) and target.id == "canonical"
                     for target in node.targets)]
    need(len(stops) == 1, "unique canonical construction boundary")
    run.body = run.body[:stops[0] + 1] + [ast.Return(value=ast.Name(id="canonical", ctx=ast.Load()))]
    selected = ast.fix_missing_locations(ast.Module(body=[basis, run], type_ignores=[]))
    namespace = {"read": lambda _: copy.deepcopy(original), "copy": copy, "Q": Q, "time": time}
    exec(compile(selected, NATIVE + "/bw_transport.py", "exec", optimize=0), namespace)
    rebuilt = namespace["run"](None, None)
    need(set(retained) - set(rebuilt) == {"local_profile", "edges", "warp_edges"},
         "canonical remainder fields")
    need(canonical(rebuilt) == canonical({key: retained[key] for key in rebuilt}),
         "original-to-canonical construction")
    need(retained["local_profile"] == original["report"]["local_profile"],
         "original local rank profile")
    return digest(canonical(rebuilt))


def scalar_charge(value):
    """Conservative numerator-temporary and denominator reserve for n/2**d."""
    denominator = value.denominator
    need(denominator > 0 and denominator & (denominator - 1) == 0,
         "reduced dyadic scalar")
    d = denominator.bit_length() - 1
    # ceil(log2(1+abs(n))) = bit_length(abs(n)), including n=0.
    return d + abs(value.numerator).bit_length(), d


def audit_events(events, receipt):
    need(digest(canonical(events)) == receipt["sha256"], "complete emitted digest")
    need(len(events) == receipt["events"], "complete emitted count")
    phases, kinds, scalars, denominators, child_profile = (
        Counter(), Counter(), Counter(), Counter(), Counter())
    phase = None
    charge = max_shift = 0
    values = set()
    for event in events:
        tag = event[0]
        kinds[tag] += 1
        if tag == "phase":
            phase = event[1]
        elif tag == "scalar":
            op = event[1]
            scalars[op[0]] += 1
            if op[0] in ("copy", "clear"):
                continue
            if op[0] == "add":
                value = Q(op[3], op[4])
            elif op[0] == "scale":
                value = Q(op[2], op[3])
            else:
                raise ValueError("unpriced scalar: " + op[0])
            cost, shift = scalar_charge(value)
            values.add(value)
            charge += cost
            phases[phase] += cost
            denominators[str(value.denominator)] += 1
            max_shift = max(max_shift, shift)
        elif tag == "climb":
            child_profile[str(event[5])] += 1
        elif tag == "center":
            child_profile[str(event[4])] += 1
        else:
            need(tag in ("warp", "adapter", "residual_adapter", "zero_buffer"),
                 "unpriced emitted event: " + tag)
    need(sum(scalars.values()) == receipt["scalar_macros"], "all scalar macros")
    need(dict(child_profile) == receipt["paid_profile"], "emitted child profile")
    need(phases["zero_frame_precondition"] > 0 and phases["full_frame_cleanup"] > 0,
         "both scalar boundaries")
    return {
        "sha256": receipt["sha256"], "events": len(events), "kinds": dict(kinds),
        "scalar_kinds": dict(scalars), "phase_height": dict(phases),
        "height_charge": charge, "max_shift": max_shift,
        "reduced_denominators": dict(denominators),
        "child_profile": dict(child_profile),
    }, values


def census(sources):
    result, coefficients = {}, set()
    first = None
    for kind in ("THREE", "FOUR"):
        prefix = "THREE" if kind == "THREE" else "NATIVE"
        for orientation in ("base", "extra"):
            word = read_json(sources, f"{MIXED}/evidence/{prefix}-CANONICAL-{orientation}.json.gz")
            original = read_json(sources, f"{MIXED}/inputs/{kind}-{orientation}.json.gz")
            binding = bind_canonical(sources[NATIVE + "/bw_transport.py"], original, word)
            receipts = read_json(sources, f"{MIXED}/evidence/{prefix}-LOCAL-{orientation}.json")
            emit = emitter(sources[NATIVE + "/bw_emit.py"], word)
            for name, back in (("forward", False), ("backward", True)):
                events = emit(back)
                record, values = audit_events(events, receipts[name])
                record["canonical_construction_sha256"] = binding
                result[f"{kind}-{orientation}/{name}"] = record
                coefficients.update(values)
                if first is None:
                    first = (events, receipts[name])
    need(len(result) == 8, "four providers in both emitted directions")
    return result, coefficients, first


def reject(call, message):
    try:
        call()
    except (ValueError, AssertionError):
        return
    raise ValueError("accepted negative control: " + message)


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def times(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def scale(a, q):
    return a[0] * q, a[1] * q


def fits(z, p, t):
    return all((x * (1 << (p + t))).denominator == 1 for x in z) and (
        z[0] * z[0] + z[1] * z[1] <= 1 << (2 * t))


def c_pair(a, b, opposite=False):
    u, v = ((1, -1), (1, 1)) if opposite else ((1, 1), (1, -1))
    numerators = (add(times(u, a), times(v, b)),
                  add(times(v, a), times(u, b)))
    return tuple(scale(z, Q(1, 2)) for z in numerators), numerators


def tensor_c(values, h, opposite=False):
    result = list(values)
    for axis in range(h):
        for i in range(1 << h):
            if not i & (1 << axis):
                j = i | (1 << axis)
                (result[i], result[j]), _ = c_pair(result[i], result[j], opposite)
    return result


def primitive_controls(coefficients):
    points = [(Q(a, 2), Q(b, 2)) for a in range(-2, 3) for b in range(-2, 3)
              if a * a + b * b <= 4]
    scalar_cases = c_cases = 0
    for value in sorted(coefficients):
        k, d = scalar_charge(value)
        for a in points:
            product = scale(a, value.numerator)
            need(fits(product, 2, k), "Horner numerator reserve")
            need(fits(scale(a, value), 2, k), "scalar endpoint reserve")
            for b in points:
                numerator = add(scale(b, 1 << d), product)
                endpoint = add(b, scale(a, value))
                need(fits(numerator, 2, k) and fits(endpoint, 2, k),
                     "ADD numerator and endpoint reserve")
                scalar_cases += 1
    for a in points:
        for b in points:
            for opposite in (False, True):
                outputs, numerators = c_pair(a, b, opposite)
                need(all(fits(z, 2, 2) for z in numerators), "C numerator reserve")
                need(all(fits(z, 2, 1) for z in outputs), "completed C reserve")
                c_cases += 1
    # A numerator can exceed endpoint-height headroom even on unit disk inputs.
    _, nums = c_pair((Q(5, 8), Q(-5, 8)), (Q(5, 8), Q(5, 8)))
    need(not fits(nums[0], 3, 1) and fits(nums[0], 3, 2), "endpoint-only control")
    reject(lambda: scalar_charge(Q(1, 3)), "nondyadic scalar")
    need(scalar_charge(Q(1, -2)) == scalar_charge(Q(-1, 2)), "negative stored denominator")
    return {"scalar_cases": scalar_cases, "C_cases": c_cases,
            "distinct_scalars": [str(q) for q in sorted(coefficients)]}


def contract_controls():
    cases = 0
    for p in (0, 3, 11):
        for h in range(1, 7):
            for c in (2, 3, 7):
                k = c * h
                t0 = k + 1
                value = (Q(1, 1 << (p + t0)), Q(0))
                incoming = [value] * (1 << h)
                need(fits(value, p, t0), "admitted incoming height")
                for opposite in (False, True):
                    need(tensor_c(incoming, h, opposite) == incoming, "constant eigenvector")
                need((value[0] * (1 << (p + k))).denominator == 2,
                     "old fractional grid loses one input bit")
                need((value[0] * (1 << (p + t0 + k))).denominator == 1,
                     "corrected common grid")
                big = 1 << t0
                old_integer_bits, corrected_integer_bits = k + 2, t0 + k + 2
                need(big >= (1 << (old_integer_bits - 1))
                     and big < (1 << (corrected_integer_bits - 1)),
                     "incoming integer headroom")
                cases += 1
    # Divisibility of zero cannot authorize a shift past the allocated word.
    def exact_shift(value, amount, width):
        need(0 <= amount < width, "shift extent")
        need(value % (1 << amount) == 0, "exact shift divisibility")
        return value >> amount
    reject(lambda: exact_shift(0, 9, 8), "zero and excessive shift")
    reject(lambda: exact_shift(0, 8, 8), "strict shift extent")
    reject(lambda: exact_shift(1, 1, 8), "discarded nonzero bit")
    need(exact_shift(8, 3, 8) == 1, "exact shift positive control")
    # Check H0=((1-i)/2) D C D and raw-H restoration on independent columns.
    for a, b in (((1, 0), (0, 0)), ((0, 0), (1, 0)),
                 ((Q(1, 2), Q(-1, 4)), (Q(-1, 2), Q(1, 8)))):
        transformed, _ = c_pair(a, times((0, 1), b))
        result = (scale(times((1, -1), transformed[0]), Q(1, 2)),
                  scale(times((1, -1), times((0, 1), transformed[1])), Q(1, 2)))
        expected = (scale(add(a, b), Q(1, 2)),
                    scale(add(a, scale(b, -1)), Q(1, 2)))
        need(result == expected, "H0 orientation and normalization")
        need(tuple(scale(z, 2) for z in result) == (add(a, b), add(a, scale(b, -1))),
             "raw H restoration")
    return {"incoming_height_cases": cases, "C_dimensions": [1, 2, 3, 4, 5, 6],
            "shift_controls": 4, "H0_columns_and_mixed_inputs": 3}


def reserve(sources, programs):
    retained = read_json(sources, MIXED + "/RESULT.json")
    profile = {int(k): v for k, v in retained["profile"].items()}
    need(max(profile) == 48 and retained["calls"] == 3240, "proper child and call count")
    rank_mass = sum(r * count for r, count in profile.items())
    template = read_json(sources, TEMPLATE)
    order = read_json(sources, MIXED + "/owner/ORDER.json")
    need(len(order) == 3240 and {tuple(row) for row in order}
         == {(stage, replica) for stage in range(9) for replica in range(360)},
         "complete source replica/stage inventory")
    port_lists = [read_json(sources, f"{MIXED}/inputs/{kind}-{orientation}.json.gz")["ports"]
                  for kind in ("THREE", "FOUR") for orientation in ("base", "extra")]
    need(len(port_lists[0]) == len(set(port_lists[0])) == 112
         and all(ports == port_lists[0] for ports in port_lists), "complete common port inventory")
    bridges = [event for event in template["execution_schedule"] if event["kind"] == "bridge"]
    need(all(type(event["coefficient"]) is int for event in bridges), "integer global bridges")
    # full_operator.normalize emits c and -c on the two sides.
    bridge_charge = 360 * 112 * sum(
        2 * scalar_charge(Q(event["coefficient"]))[0] for event in bridges)
    local = max(row["height_charge"] for row in programs.values())
    gamma = 1 << 1296
    for i in range(1, 37):
        gamma *= (1 << (2 * i)) - 1
    s = gamma * rank_mass
    e = gamma * (3240 * local + bridge_charge) + 73
    c = max(2, (s + e + 24) // 25)
    need(25 * c >= s + e, "uniform strong-induction coefficient")
    max_shift = max(row["max_shift"] for row in programs.values())
    need(max_shift <= c, "scalar descriptor shift extent")
    # Sample the proved recurrence with every proper rank, including seams.
    recurrence_cases = 0
    for width in (73, 74, 145, 146, 147, 1000, 1000001):
        f = width // 73
        for r in range(1, 49):
            need(r * f < width and c * r * f + s * f + e <= c * width,
                 "proper-child recurrence")
            recurrence_cases += 1
    return {
        "profile": retained["profile"], "rank_mass": rank_mass,
        "local_max_height": local, "scalar_max_shift": max_shift,
        "bridges_per_replica_port": len(bridges),
        "bridge_scalar_events_per_cover": 2 * len(bridges) * 360 * 112,
        "bridge_height_per_cover": bridge_charge,
        "remainder_height": 73, "Gamma": str(gamma),
        "S": str(s), "E": str(e), "C": str(c),
        "C_bits": c.bit_length(), "recurrence_cases": recurrence_cases,
        "fractional_bits": "P+t0+C*h", "integer_sign_bits": "t0+C*h+2",
        "raw_H_height": "(C+4)*h for h>=1; identity for h=0",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", type=Path, help="write a new receipt; refuse overwrite")
    args = parser.parse_args()
    sources = authenticate()
    programs, coefficients, (events, receipt) = census(sources)
    # Authenticate before compilation and bind the full emitted chronology.
    first_name = sorted(sources)[0]
    reject(lambda: authenticate({first_name: sources[first_name] + b"\n"}),
           "source corruption")
    removed = list(events)
    cleanup = next(i for i, event in enumerate(removed)
                   if event == ["phase", "full_frame_cleanup"])
    del removed[cleanup + 1]
    reject(lambda: audit_events(removed, receipt), "omitted cleanup event")
    changed = json.loads(canonical(events))
    for event in changed:
        if event[0] == "scalar" and event[1][0] == "add":
            event[1][3] *= -1
            break
    reject(lambda: audit_events(changed, receipt), "altered scalar direction")
    result = {
        "status": "PASS_GAUSSIAN_HEIGHT_CONTRACT",
        "programs": programs, "reserve": reserve(sources, programs),
        "primitives": primitive_controls(coefficients), "contract": contract_controls(),
        "controls": ["source corruption", "cleanup omission", "scalar sign",
                     "nondyadic scalar", "incoming fractional height",
                     "incoming integer height", "endpoint-only C prefix",
                     "shift extent", "shift divisibility"],
        "scope": "Exact emitted scalar census and finite controls accompanying a conditional height proof; no native endpoint, full Gaussian trace or multiplication-theorem acceptance.",
    }
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.emit:
        with args.emit.open("x") as handle:
            handle.write(encoded)
    else:
        need(json.loads((HERE / "RESULT.json").read_text()) == result, "complete retained receipt")
    print(json.dumps({"status": result["status"], "programs": len(programs),
                      "local_max_height": result["reserve"]["local_max_height"],
                      "receipt_sha256": digest(canonical(result)),
                      "scope": result["scope"]}, sort_keys=True))


if __name__ == "__main__":
    main()
