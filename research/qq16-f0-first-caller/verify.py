"""Source-bound first F0 Gaussian caller inspection.

Clear1nsight, with substantial OpenAI ChatGPT assistance. Apache-2.0.
No full physical caller or multiplication supplier is admitted here.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import io
from itertools import product
import json
import tarfile
import types
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "20ecf2891d80b5acf18d980b2164fb44ea7faa90"
PINS = {
    "research/joint-query/certificate.json.gz":
        "a5ed85fac5ebf3c091482a113ab0d351eb5a7892fe2841a35e16017ec1ff49f7",
    "research/community-frontier1042-audit/selected-replay.tar.gz":
        "22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754",
}
MEMBERS = {
    "slots/local/CANONICAL-WORD.json.gz":
        "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219",
    "slots/local/CLIFFORD-RECIPES.json":
        "d0768f2164d5f64a2fdbec422f1cfde4e400818792f1904ca541958377243731",
    "slots/local/RESIDUAL-ADAPTERS.json":
        "383f40aadd00a4ac700dfd0d4c22d6c6c0be9a9863116e4d69c7acd23bafae0c",
}
NATIVE_PATH = "research/qq16-native-rounded-components/vendor/native.py"
NATIVE_SHA = "999eb1230798b25821de7771ecfa86381e137124059b30ccef167169d176ee8e"
TAPES_SHA = "a3ad668b94d44ff1b9d7093e95c5af3ea0d80cdb798365ea7631c0e2a3dcae10"
SEMANTICS_PATH = "research/qq16-native-rounded-components/verify.py"
SEMANTICS_SHA = "16a6cf984f37adb2d98f5180312dc8637c3f653dd41db9252961c3ca1f3ffdba"
FORMAT_PATH = "research/qq16-all-depth-producer-grid/RESULT.json"
FORMAT_SHA = "b954ab5c5a720b21a9ab49bda2e1a0824ab184a482243d6263dab3c4bddb91bb"
EVENT = ["climb", "A", 546, 0, 4, 1]
PREFIX_SHA = "15115954461f2cb93e2266822d82bfac1ab8de7d460ff78fcf594d21c61d2b53"
RECIPE_SHA = "2f3fd69e1096a44b35b9298c2af9096ace5c4f52b9401e7e3e5187063636b0b3"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def digest(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()


def source_bytes(root, name, sha, cap=128 * 1024**2):
    path = Path(root)
    for part in Path(name).parts:
        need(part not in ("..", "/"), "relative source path")
        path /= part
        need(not path.is_symlink(), "source symlink: " + name)
    need(path.is_file() and path.stat().st_size <= cap, "source file/size: " + name)
    raw = path.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == sha, "source SHA256: " + name)
    return raw


def source_module(root, name, sha):
    raw = source_bytes(root, name, sha)
    module = types.ModuleType(name)
    exec(compile(raw, str(Path(root) / name), "exec"), module.__dict__)
    return module


def load(root=ROOT):
    raw = {}
    for name, sha in PINS.items():
        raw[name] = source_bytes(root, name, sha)
    packet = json.loads(gzip.decompress(raw[next(iter(PINS))]))
    objects = []
    with tarfile.open(fileobj=io.BytesIO(raw[list(PINS)[1]]), mode="r:gz") as archive:
        for name, sha in MEMBERS.items():
            records = [m for m in archive.getmembers() if m.name == name]
            need(len(records) == 1 and records[0].isfile(), "unique regular member")
            need(records[0].size <= 64 * 1024**2, "member size cap")
            value = archive.extractfile(records[0]).read()
            need(hashlib.sha256(value).hexdigest() == sha, "member SHA256")
            objects.append(json.loads(gzip.decompress(value) if name.endswith(".gz") else value))
    return packet, *objects


def reg(token):
    kind, index = token
    need(kind in ("L", "C") and type(index) is int, "register token")
    need(0 <= index < (704 if kind == "L" else 8), "register range")
    return index + (704 if kind == "C" else 0)


def ceil_log2_fraction(value):
    need(value > 0, "positive envelope")
    n, d = value.numerator, value.denominator
    result = n.bit_length() - d.bit_length()
    power = Fraction(2**result) if result >= 0 else Fraction(1, 2**(-result))
    return result + (value > power)


def scaled(bound, coefficient):
    magnitude, denominator = bound
    if coefficient == 0 or magnitude == 0:
        return Fraction(0), 0
    d = coefficient.denominator
    need(d > 0 and d & (d-1) == 0, "dyadic scalar")
    return magnitude * abs(coefficient), denominator + d.bit_length() - 1


def added(left, right):
    if left[0] == 0:
        return right
    if right[0] == 0:
        return left
    return left[0] + right[0], max(left[1], right[1])


def inspect(packet, word, recipes, residuals):
    need(packet["programs"]["F_0"][0][:3] == ["retained_core", "forward", 0],
         "F0 retained-core binding")
    children = {(r["old"], r["new"]): r for r in recipes["children"]}
    need(len(children) == len(recipes["children"]), "unique child frames")
    states = [(Fraction(1), 0)] * 704 + [(Fraction(0), 0)] * 8
    events = packet["core_words"]["forward"]
    for index, event in enumerate(events):
        kind = event[0]
        if kind == "climb":
            _, direction, dst, old, new, claimed_rank = event
            child = children[old, new]
            rank = child["rank"]
            need(type(rank) is int and 0 <= rank <= 9, "native rank")
            if rank > 0:
                magnitude, grid = states[dst]
                need(magnitude > 0, "nonzero input envelope")
                return {
                    "source_base": BASE,
                    "event_index": index,
                    "event": event,
                    "prefix_events": events[:index],
                    "prefix_sha256": digest(events[:index]),
                    "recipe": child,
                    "recipe_sha256": digest(child),
                    "target_entry_magnitude_factor": str(magnitude),
                    "target_entry_grid_exponent": grid,
                    "target_initial_frame": word["start"][dst],
                    "first_axis_signed_width_intercept": grid + 4 + ceil_log2_fraction(magnitude),
                    "whole_recipe_width_intercept_at_lambda1": grid + 2*rank + 2 + ceil_log2_fraction(magnitude),
                    "private_fields_proved_zero_at_cut": [i-704 for i in range(704, 712) if states[i][0] == 0],
                    "physical_window_assignment_in_source": "not established by these numerical records",
                }
            need(child["right"] is None, "rank-zero right factor")
        elif kind == "scalar":
            gate = event[1]
            dst = reg(gate[1])
            if gate[0] == "clear":
                need(dst >= 704, "owned private CLEAR")
                states[dst] = Fraction(0), 0
            elif gate[0] == "scale":
                states[dst] = scaled(states[dst], Fraction(gate[2], gate[3]))
            else:
                need(gate[0] == "add", "scalar instruction")
                states[dst] = added(states[dst], scaled(states[reg(gate[2])], Fraction(gate[3], gate[4])))
        else:
            need(kind in ("adapter", "residual_adapter", "phase"), "pre-Gaussian event kind")
    raise ValueError("no positive-rank F0 child")


def bind_first(data):
    packet, word, recipes, residuals = data
    found = inspect(*data)
    need(found["event_index"] == 9894 and found["event"] == EVENT,
         "literal first caller changed")
    need(found["prefix_sha256"] == PREFIX_SHA, "literal prefix changed")
    need(found["recipe_sha256"] == RECIPE_SHA, "literal native recipe changed")
    need(word["start"][546] == 0 and word["frames"][0] == []
         and word["frames"][4] == [459], "first caller frame binding")
    reads, adapters, writes = [], [], []
    for index, event in enumerate(found["prefix_events"]):
        if event[0] == "scalar":
            gate = event[1]
            if reg(gate[1]) == 546:
                writes.append(index)
            if gate[0] == "add" and reg(gate[2]) == 546:
                reads.append(index)
        elif event[0] != "phase" and event[2] == 546:
            adapters.append([index, event])
    need(not writes, "target is modified before first child")
    need(adapters == [[7948, ["adapter", "old_to_new", 546, 0]]],
         "target endpoint adapter changed")
    # The pinned native interpreter applies endpoint monomials only to data
    # ports (0..223); this helper adapter records the existing I frame.
    need(reads == [262, 335, 408, 482, 555, 628, 701, 774], "target reads changed")
    need(found["target_entry_magnitude_factor"] == "1"
         and found["target_entry_grid_exponent"] == 0, "target entry envelope")
    need(packet["core_words"]["forward"][9895] ==
         ["scalar", ["add", ["L", 546], ["L", 561], -1, 1], 4],
         "adjacent scalar event changed")
    last_clears = [8185, 8259, 8337, 8412, 8484, 8557, 8628, 8702]
    events = packet["core_words"]["forward"]
    for c, last in enumerate(last_clears):
        token = ["C", c]
        writes = [i for i, e in enumerate(events[:9894])
                  if e[0] == "scalar" and e[1][1] == token]
        need(writes and writes[-1] == last
             and events[last] == ["scalar", ["clear", token], 0],
             "private last-write CLEAR binding")
        need(not any(e[0] == "scalar" and token in e[1][1:3]
                     for e in events[9894:]), "private field reused in retained-core suffix")
    return found, reads


def sparse(value):
    return [[x, str(Fraction(a, 2**value[2])), str(Fraction(b, 2**value[2]))]
            for x, (a, b) in enumerate(zip(*value[:2])) if a or b]


def numerators(real, imag, axis=1):
    return ([real[x] - imag[x] + real[x ^ axis] + imag[x ^ axis]
             for x in range(len(real))],
            [imag[x] + real[x] + imag[x ^ axis] - real[x ^ axis]
             for x in range(len(real))])


def preconditions(real, imag, width):
    rr, ii = numerators(real, imag)
    values = rr + ii
    return {"even": all(x % 2 == 0 for x in values),
            "signed_range": all(-(1 << (width - 1)) <= x < (1 << (width - 1))
                                for x in values)}


def tariff(tapes):
    return {k: sum(t.count[k] for t in tapes) for k in ("read", "write", "move")}


def replay_prefix(N, data, initial):
    """Exact witness replay of the entire literal prelude, no numeric bounds.

    Event semantics follow Sricharan Vagvala/Tekalign's pinned native evaluator;
    this small interpreter accepts an explicit arbitrary-helper input instead
    of that evaluator's fixed rounding fixture. No physical cost is inferred.
    """
    packet, word, recipes, residuals = data
    endpoints = {(r["role"], r["port"]): r for r in recipes["endpoint_adapters"]}
    state = [N.ZERO] * 712
    state[546] = initial
    for event in packet["core_words"]["forward"][:9894]:
        kind = event[0]
        if kind == "scalar":
            gate = event[1]
            at = reg(gate[1])
            if gate[0] == "clear":
                state[at] = N.ZERO
            elif gate[0] == "scale":
                if state[at] != N.ZERO:
                    state[at] = N.scaled(state[at], Fraction(gate[2], gate[3]))
            else:
                need(gate[0] == "add", "prefix scalar kind")
                value = state[reg(gate[2])]
                if value != N.ZERO:
                    term = N.scaled(value, Fraction(gate[3], gate[4]))
                    state[at] = N.plus(state[at], term)
        elif kind == "adapter":
            _, direction, at, _ = event
            if direction == "old_to_new" and at < 112:
                state[at] = N.mono(state[at], N.monomial_key(endpoints["source", at]["left"]))
            elif direction == "new_to_old" and 112 <= at < 224:
                state[at] = N.mono(state[at], N.monomial_key(endpoints["target", at-112]["left"]), True)
        elif kind == "residual_adapter":
            direction, at, a = event[1:4]
            b = event[4] if len(event) == 5 else 1
            key = str(a) if b == 1 else f"{a}:{b}"
            part = "right" if direction == "pre" else "left"
            state[at] = N.mono(state[at], N.monomial_key(residuals["recipes"][key][part]), True)
        else:
            need(kind == "phase", "unexpected positive-rank event in prefix")
    need(state[546] == initial, "literal prefix did not preserve witness helper")
    return state


def check_tape_case(T, real, imag, width, expected):
    need(preconditions(real, imag, width) == {"even": True, "signed_range": True},
         "fixture must meet the arithmetic contract")
    tapes = T.fixture(real, imag, width, origins=[-17, 31, 109, -203, 419, 1009])
    exterior = [dict(t.exterior) for t in tapes]
    T.axis_kernel(tapes, 9, width, 0)
    actual = (T.decode(tapes[0], width), T.decode(tapes[1], width))
    need(actual == expected, "tape/native value mismatch")
    need(all(t.head == t.origin for t in tapes), "head return")
    need(all(not any(t.cells) for t in tapes[2:]), "scratch cleanup")
    need([t.exterior for t in tapes] == exterior, "exterior changed")
    want = {"read": 6 * 512 * width, "write": 6 * 512 * width,
            "move": 20 * 512 * width}
    need(tariff(tapes) == want, "exact axis tariff")
    return want


def audit(data=None, root=ROOT, package=HERE):
    data = load(root) if data is None else data
    found, reads = bind_first(data)
    source_bytes(root, SEMANTICS_PATH, SEMANTICS_SHA)
    format_receipt = json.loads(source_bytes(root, FORMAT_PATH, FORMAT_SHA))
    need(format_receipt["grid_intercept_at_one"] == 71
         and format_receipt["signed_width_P_plus_at_one"] == 215,
         "existing all-depth format parameters changed")
    N = source_module(root, NATIVE_PATH, NATIVE_SHA)
    T = source_module(package, "vendor/tapes.py", TAPES_SHA)
    record = found["recipe"]
    right = N.monomial_key(record["right"])
    left = N.monomial_key(record["left"])
    need(N.table(right)[0] == (0, 0) and N.table(left)[0] == (0, 0)
         and N.table(left)[1] == (459, 3), "witness monomial binding")

    # An arbitrary nonconstant dirty helper, with all other input fields zero.
    # No prefix event writes L546; its source reads do not restrict that value.
    re = [0] * 512
    re[0] = 1
    initial = N.vector(re)
    prelude = replay_prefix(N, data, initial)
    entry = N.mono(initial, right)
    axis_output = N.line(entry, 1)
    child_output = N.recipe(initial, record)
    need(sparse(axis_output) == [[0, "1/2", "1/2"], [1, "1/2", "-1/2"]],
         "axis witness output")
    need(sparse(child_output) == [[0, "1/2", "1/2"], [459, "-1/2", "-1/2"]],
         "complete child witness output")
    need(preconditions(*entry[:2], 5) == {"even": False, "signed_range": True},
         "unchanged-grid divisibility obstruction")
    failing = T.fixture(*entry[:2], 5)
    try:
        T.axis_kernel(failing, 9, 5, 0)
    except ValueError as error:
        need(str(error) == "nonexact half", "wrong rejection reason")
    else:
        raise ValueError("unchanged grid unexpectedly admitted")

    # The changed-grid control doubles the mantissas, while the represented
    # physical value is unchanged because the grid exponent increases by one.
    # Its preparation and the monomials are unmetered fixture work, not a bill.
    rr, ii = ([2*x for x in component] for component in entry[:2])
    ar, ai = numerators(rr, ii)
    cost = check_tape_case(T, rr, ii, 5, ([x//2 for x in ar], [x//2 for x in ai]))
    repaired = N.vector([x//2 for x in ar], [x//2 for x in ai], 1)
    need(repaired == axis_output, "changed-grid physical value")
    need(N.mono(repaired, left) == child_output, "left monomial endpoint")

    # PR3303 already reserves 71 fractional bits at lambda=1. The unchanged
    # helper's h-grid input is a multiple of 2**71 in that proposed format.
    # P=1 admits this unit witness; the actual stored component width is 216.
    reserved_real = [x << 71 for x in entry[0]]
    reserved_imag = [x << 71 for x in entry[1]]
    nr, ni = numerators(reserved_real, reserved_imag)
    format_cost = check_tape_case(T, reserved_real, reserved_imag, 216,
                                 ([x//2 for x in nr], [x//2 for x in ni]))
    reserved_output = N.vector([x//2 for x in nr], [x//2 for x in ni], 71)
    need(reserved_output == axis_output, "existing finer format physical value")
    need(73 < 214, "first-child numerator range fits existing format for all P")

    # All 1024 Gaussian basis columns are checked against the actual pinned
    # native recipe. Each has a half-integral output on the unchanged grid.
    # This is finite evidence for lambda=1; PROOF.md states the lattice lemma.
    columns = 0
    for component in (0, 1):
        for address in range(512):
            pair = [[0] * 512, [0] * 512]
            pair[component][address] = 1
            value = N.vector(*pair)
            before = N.mono(value, right)
            p = preconditions(*before[:2], 5)
            need(p == {"even": False, "signed_range": True}, "basis parity obstruction")
            nr, ni = numerators(*before[:2])
            separate = N.vector(nr, ni, 1)
            need(N.mono(separate, left) == N.recipe(value, record), "basis native binding")
            need(N.recipe(value, record)[2] == 1, "unchanged-grid output obstruction")
            columns += 1

    parity_patterns = []
    for a, b, c, d in product((0, 1), repeat=4):
        nr, ni = numerators([a, c], [b, d])
        even = all(x % 2 == 0 for x in nr + ni)
        need(even == ((a+b+c+d) % 2 == 0), "exact pair admission lattice")
        parity_patterns.append(even)
    need(sum(parity_patterns) == 8, "index-two pair sublattice")

    # Dense signed data exercise the full four-term numerator, not only sparse
    # columns. Each original component lies in [-M,M]; W=bit_length(M)+4.
    routed = 0
    widths = []
    for magnitude in (1, 3, 7, 255, (1 << 64) - 1):
        width = magnitude.bit_length() + 4
        widths.append(width)
        for variant in range(4):
            a = [magnitude if ((x * 13 + variant) % 7) < 3 else -magnitude
                 for x in range(512)]
            b = [magnitude if ((x * 17 + 3 * variant) % 11) < 5 else -magnitude
                 for x in range(512)]
            before = N.mono(N.vector(a, b), right)
            r2, i2 = ([2*x for x in component] for component in before[:2])
            nr, ni = numerators(r2, i2)
            check_tape_case(T, r2, i2, width, ([x//2 for x in nr], [x//2 for x in ni]))
            got = N.mono(N.vector([x//2 for x in nr], [x//2 for x in ni], 1), left)
            need(got == N.recipe(N.vector(a, b), record), "dense complete-child comparison")
            routed += 1

    # A sharp width failure remains possible even after parity is repaired.
    # At pair 0/1: (a,b,c,d)=(2,-2,2,2), so the real numerator is +8.
    a, b = [0] * 512, [0] * 512
    a[0], b[0], a[1], b[1] = 2, -2, 2, 2
    need(preconditions(a, b, 4) == {"even": True, "signed_range": False},
         "insufficient width control")
    narrow = T.fixture(a, b, 4)
    T.axis_kernel(narrow, 9, 4, 0)
    need(T.decode(narrow[0], 4)[0] == -4, "unchecked overflow control")
    check_tape_case(T, a, b, 5, ([x//2 for x in numerators(a, b)[0]],
                                [x//2 for x in numerators(a, b)[1]]))
    return {
        "schema_version": 1,
        "source_base": BASE,
        "scope": "first F0 rank-one child, lambda=1 nine-axis slice with identity spectators; unchanged-grid obstruction",
        "source_implementations_sha256": {"native": NATIVE_SHA, "event_semantics": SEMANTICS_SHA,
                                          "tapes": TAPES_SHA, "existing_format_receipt": FORMAT_SHA},
        "caller": {"event_index_zero_based": 9894, "event": EVENT,
                   "next_event": data[0]["core_words"]["forward"][9895],
                   "prefix_sha256": PREFIX_SHA, "recipe_sha256": RECIPE_SHA,
                   "prefix_target_writes": [], "prefix_target_scalar_reads": reads,
                   "identity_helper_adapter_index": 7948,
                   "initial_frame_axes": [], "exit_frame_axes": [459],
                   "private_fields_zero_at_cut": found["private_fields_proved_zero_at_cut"],
                   "private_last_write_clear_indices": [8185, 8259, 8337, 8412, 8484, 8557, 8628, 8702],
                   "private_scalar_accesses_in_remaining_retained_core": 0},
        "witness": {"input": "L546 real delta at address 0; all other input fields zero",
                    "literal_prefix_events_replayed": 9894,
                    "prefix_target_value": sparse(prelude[546]),
                    "unchanged_grid_preconditions": preconditions(*entry[:2], 5),
                    "axis_output": sparse(axis_output), "child_output": sparse(child_output),
                    "tape_rejection": "nonexact half",
                    "rejection_is_not_a_nondestructive_admission_scan": True},
        "conditional_arithmetic_repair": {
            "input_grid_exponent": "q", "output_grid_exponent": "q+1",
            "stored_input_mantissas": "twice the original input mantissas",
            "minimum_extra_fractional_bits_for_arbitrary_integer_mantissas": 1,
            "sufficient_width_for_component_bound_M_ge_1": "bit_length(M)+4",
            "witness_width": 5, "witness_axis_cell_actions": cost,
            "witness_axis_total": sum(cost.values()),
            "fixture_preparation_and_monomials_metered": False},
        "existing_PR3303_format": {
            "grid_fractional_reserve_at_lambda1": 71,
            "width_at_lambda1": "P+215",
            "entry_premise": "original components in h Z with magnitude strictly below 2^P h",
            "first_child_numerator_strict_bound_in_stored_units": "2^(P+73)",
            "signed_range_positive_threshold": "2^(P+214)",
            "parity_and_range_compatible_conditionally": True,
            "physical_entry_protocol_admitted": False,
            "unit_witness_P": 1, "unit_witness_width": 216,
            "unit_witness_axis_cell_actions": format_cost,
            "unit_witness_axis_total": sum(format_cost.values()),
            "slice_is_full_payload_execution": False},
        "finite_checks": {"native_gaussian_basis_columns": columns,
                          "pair_parity_classes": 16, "admitted_pair_parity_classes": 8,
                          "independent_pair_constraints_at_N512": 256,
                          "same_grid_admission_lattice_index": str(1 << 256),
                          "dense_complete_child_tape_cases": routed,
                          "dense_widths": widths,
                          "narrow_width_even_numerator": 8,
                          "narrow_width": 4, "wrong_real_output": -4,
                          "correct_real_output": 4},
        "physical_obligations": {
            "two_data_windows": "logical mutable helper is named; physical intervals and encoding unknown",
            "four_scratch_windows": "C0/C1 component half-slices give a legal abstract scratch candidate; six separate physical tapes/origins and paid access remain unbound",
            "grid_refinement": "necessary for this direct same-grid proposal; implementation cost unknown",
            "right_and_left_monomials": "source-pinned arithmetic only; physical routing cost unknown",
            "adjacent_scalar_event": "named, but alignment/addressing/arithmetic cost unknown",
            "helper_restoration": "whole-caller obligation; not discharged by a single child",
            "F17_consumer_and_recursive_bill": "unknown; not priced by the axis tariff"},
        "abstract_scratch_candidate": {
            "binding": ["Re C0[0:N/2]", "Im C0[0:N/2]", "Re C1[0:N/2]", "Im C1[0:N/2]"],
            "each_length_bits": "N*W/2", "additional_logical_fields": 0,
            "entry": "C0 and C1 are zero after their last CLEARs",
            "exit": "kernel restores four used half-slices to zero; unused halves untouched",
            "scope": "an abstract allocation compatible with the source private-field contract, not a supplied six-tape physical embedding"},
        "decision": "unchanged-grid substitution obstructed; existing PR3303 finer format passes local arithmetic conditionally; physical connection uncosted",
        "supplier_admitted": False, "new_kappa_claimed": False,
    }


def compare_result(result, path=HERE / "RESULT.json"):
    def unique(pairs):
        value = {}
        for key, item in pairs:
            need(key not in value, "duplicate RESULT.json key")
            value[key] = item
        return value
    path = Path(path)
    need(path.stat().st_size <= 128 * 1024, "RESULT.json size cap")
    saved = json.loads(path.read_text(), object_pairs_hook=unique)
    need(canonical(saved) == canonical(result), "complete RESULT.json mismatch")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-result", action="store_true",
                        help="explicitly regenerate this package's result, never frozen inputs")
    args = parser.parse_args()
    result = audit()
    if args.write_result:
        (HERE / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    compare_result(result)
    print("PASS_QQ16_FIRST_F0_CALLER_AUDIT event=9894 helper=L546 "
          "same_grid=REJECTED minimum_extra_fractional_bits=1 "
          "basis_columns=1024 dense_tape_cases=20 no_physical_caller_admission")


if __name__ == "__main__":
    main()
