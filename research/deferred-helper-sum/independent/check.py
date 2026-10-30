#!/usr/bin/env python3
"""Independent local consumer and monotone-frame witnesses, standard library only.

SPDX-License-Identifier: Apache-2.0
Prepared with substantial OpenAI Codex GPT-6.1 Sol assistance. This is a new
finite exact checker and written-proof witness, not independent human review.
The BORROW-WORD format and frame contract are credited to the retained PR4076
NOTICE.md and Sagar Thakrar's audit_core.py, which is read but never executed.
No primary or design checker is imported, executed, or read by this program.
"""
from __future__ import annotations

from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import gzip
import hashlib
import json


EXPORT_SHA256 = "323edf5ff6415abbb60253f64c548c24d63cee499519787a6ffa334acd74861b"
PR4096_HEAD = "8d1e3b9399a2a7914f1ab538242cf2e6e6c4cd9f"
CANONICAL_BASE = "bb4bccbf42844d2801487450727c2f63e10d1d0f"
PR4076_HEAD = "9744f9df268590295a9872b1952c695a678192b9"
PAIR = (608, 609)
LOC = (608, 609, 610, 612, 410, 417, 419, 421)
TRACK = frozenset((*LOC, 278, 276))
ENTRANCE = (97, 45)
FRAME = (144, 75, 42, 7)


class Failure(ValueError):
    def __init__(self, code, message):
        super().__init__(code + ": " + message)
        self.code = code


def need(ok, code, message):
    if not ok:
        raise Failure(code, message)


def reject(label, code, check):
    try:
        check()
    except Failure as error:
        need(error.code == code, "control_wrong_guard", label + " rejected by " + error.code)
        return label
    raise Failure("control_accepted", label)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def unique_object(pairs):
    out = {}
    for key, value in pairs:
        need(key not in out, "json_duplicate", str(key))
        out[key] = value
    return out


def decode(raw):
    return json.loads(raw, object_pairs_hook=unique_object)


def bind_bytes(raw, sha, label):
    need(digest(raw) == sha, "source_sha256", label)


def authenticate(package):
    raw = (package / "SOURCE-EXPORT.json").read_bytes()
    bind_bytes(raw, EXPORT_SHA256, "outer SOURCE-EXPORT.json")
    export = decode(raw)
    need(export["source_commit"] == PR4096_HEAD and export["canonical_base"] == CANONICAL_BASE,
         "source_commit", "PR4096 export pins")
    paths = {}
    for item in export["files"]:
        rel = Path(item["path"])
        need(not rel.is_absolute() and ".." not in rel.parts and str(rel) not in paths,
             "source_path", str(rel))
        data = (package / rel).read_bytes()
        bind_bytes(data, item["sha256"], str(rel))
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        need(blob == item["git_blob"] and item["mode"] == "100644",
             "source_blob", str(rel))
        need(item["source_commit"] == PR4096_HEAD, "source_commit", str(rel))
        paths[str(rel)] = {"bytes": len(data), "sha256": digest(data), "git_blob": blob}
    nested = decode((package / "source4096/SOURCE-EXPORT.json").read_bytes())
    need(nested["source_pr"] == 4076 and nested["source_head"] == PR4076_HEAD,
         "source_commit", "nested PR4076 provenance")
    for item in nested["files"]:
        rel = "source4096/source4076/" + item["local_path"]
        need(paths[rel] == {"bytes": item["bytes"], "sha256": item["sha256"],
                            "git_blob": item["git_blob"]}, "source_manifest", rel)
    return paths


# Independent frame representation: reduced XOR bases, not point-set masks.
def basis(vectors):
    pivots = {}
    for vector in vectors:
        need(type(vector) is int and 0 <= vector < 512, "frame_vector", str(vector))
        for bit in sorted(pivots, reverse=True):
            if vector >> bit & 1:
                vector ^= pivots[bit]
        if vector:
            bit = vector.bit_length() - 1
            for old in tuple(pivots):
                if pivots[old] >> bit & 1:
                    pivots[old] ^= vector
            pivots[bit] = vector
    return tuple(pivots[k] for k in sorted(pivots, reverse=True))


def contained(small, large):
    return basis((*small, *large)) == basis(large)


def image(columns, vector):
    out = 0
    for bit, column in enumerate(columns):
        if vector >> bit & 1:
            out ^= column
    return out


def warped(columns, frame, inverse=False):
    need(len(columns) == 9 and len(basis(columns)) == 9, "native_invertible", str(columns))
    if inverse:
        # Enumerating the 512 binary vectors is only inversion of this fixed
        # nine-dimensional frame map, not a sampled scalar-operator test.
        reverse = {image(columns, x): x for x in range(512)}
        need(len(reverse) == 512, "native_invertible", "binary inverse map")
        return basis(reverse[x] for x in frame)
    return basis(image(columns, x) for x in frame)


def scalar_touched(gate):
    return gate[1:3] if gate[0] == "add" else gate[1:2]


def frame_witness(word):
    need(not (TRACK & set(word["centers"])), "frame_domain", "tracked register is a descending centre")
    need(not any(TRACK & set(g[1:3]) for g in word["cut"]),
         "frame_domain", "unannotated cut touches tracked registers")
    need(not any(set(PAIR) & set(scalar_touched(g))
                 for name in ("precondition", "compensation", "A", "cut", "restore")
                 for g in word[name]), "pair_sites", "pair access outside B")
    early = [(i, g) for i, g in enumerate(word["B"][:948]) if set(PAIR) & set(scalar_touched(g))]
    need([(i, g[:5]) for i, g in early] ==
         [(388, ["add", 121, 609, 1, 2]), (410, ["add", 137, 608, -1, 2])],
         "pair_sites", "exact two early target reads")
    current = {r: basis(word["start_extra"].get(str(r), ())) for r in TRACK}
    changes = {r: [] for r in TRACK}

    def climb(g, where):
        fr = basis(g[-1])
        for register in TRACK & set(scalar_touched(g)):
            old = current[register]
            need(contained(old, fr), "frame_monotone", str((where, register, old, fr)))
            if old != fr:
                changes[register].append({"where": where, "from": list(old), "to": list(fr)})
            current[register] = fr

    for name in ("precondition", "compensation"):
        for i, g in enumerate(word[name]):
            climb(g, [name, i])
    for i, g in enumerate(word["A"]):
        if g[0] != "warp":
            climb(g, ["A", i])
            continue
        _, r, op, before, after = g
        if r in TRACK:
            rec = word["warps"][abs(op) - 1]
            need(current[r] == basis(before), "native_entry", str(("A", i)))
            need(warped(rec[2], basis(before), op < 0) == basis(after),
                 "native_frame", str(("A", i)))
            current[r] = basis(after)
    at = {}
    for k, rec in enumerate(word["warps"], 1):
        need(warped(rec[2], basis(rec[3])) == basis(rec[4]), "native_frame", str(k))
        at.setdefault(rec[0], []).append((k, rec))
    captures = {}
    for p in range(len(word["B"]) + 1):
        if p == 948:
            captures["before_native_948"] = dict(current)
        for k, (_, r, _, before, after) in at.get(p, ()):
            if r in TRACK:
                need(current[r] == basis(before), "native_entry", str(k))
                current[r] = basis(after)
        if p in (948, 962):
            captures["before_B" + str(p)] = dict(current)
        if p < len(word["B"]):
            climb(word["B"][p], ["B", p])
    need(not any(rec[1] in PAIR for rec in word["warps"]),
         "pair_native", "a pair cell has a native warp")
    need(not any(g[0] == "warp" and g[1] in PAIR for g in word["A"]),
         "pair_native", "a pair cell has a prelude native warp")
    e, f = basis(ENTRANCE), basis(FRAME)
    need(len(e) == 2 and len(f) == 4 and contained(e, f), "frame_geometry", "E is a rank-two subspace of F")
    need(e == basis((76, 45)), "frame_geometry", "equivalent entrance basis")
    need(all(captures["before_B948"][h] == e for h in PAIR), "pair_entry", "pair at E")
    need(all(captures["before_B948"][s] == f for s in (410, 417, 419, 421)),
         "source_frame", "external sources at F after native warps")
    need(all(captures["before_B962"][h] == f for h in PAIR), "pair_exit", "source pair after B961")
    native = [(k, rec[1]) for k, rec in at[948]]
    need(native == [(33, 410), (34, 417), (35, 419), (36, 421)],
         "native_sites", "four external native warps before B948")
    return captures, {"entrance_basis": list(e), "source_basis": list(f),
                      "native_at_948": native,
                      "early_pair_accesses": [[i, g] for i, g in early],
                      "pair_positive_frame_changes": {str(h): changes[h] for h in PAIR}}


def chronological(word):
    for i, g in enumerate(word["initial_corrections"]):
        yield ["corr", g["target"], g["source"], g["operator_word"], Q(g["coefficient"])], ["initial_corrections", i]
    for name in ("precondition", "compensation", "A", "cut"):
        for i, g in enumerate(word[name]):
            yield g, [name, i]
    at = {}
    for k, rec in enumerate(word["warps"], 1):
        at.setdefault(rec[0], []).append(["warp", rec[1], k])
    for p in range(len(word["B"]) + 1):
        for g in at.get(p, ()):
            yield g, ["native_before_B", p, g[2]]
        if p < len(word["B"]):
            yield word["B"][p], ["B", p]


def arbitrary_current_state(word, cut=948):
    live = set(range(704)) - set(word["removed"])
    buffers = {704 + int(r) for r in word["helper_final"]}
    need(len(live) == 632 and len(buffers) == 91 and not (live & buffers),
         "input_domain", "632 independent live cells and 91 separate dirty buffers")
    kinds = Counter()
    count = 0
    for g, where in chronological(word):
        if where == ["B", cut]:
            break
        op = g[0]
        need(op in ("add", "scale", "warp", "corr"), "opcode", str(where))
        rs = g[1:3] if op in ("add", "corr") else g[1:2]
        need(set(rs) <= live, "input_domain", str(where))
        if op in ("add", "corr"):
            need(g[1] != g[2], "prefix_invertible", "self shear at " + str(where))
            coefficient = Q(g[3], g[4]) if op == "add" else Q(g[4])
            need(coefficient.denominator & (coefficient.denominator - 1) == 0,
                 "prefix_coefficient", "non-dyadic shear at " + str(where))
        if op == "scale":
            coefficient = Q(g[2], g[3])
            need(coefficient != 0, "prefix_invertible", "zero scale at " + str(where))
            need(coefficient.denominator & (coefficient.denominator - 1) == 0,
                 "prefix_coefficient", "non-dyadic scale at " + str(where))
        if op == "warp":
            need(g[2] != 0 and abs(g[2]) <= len(word["warps"]), "prefix_invertible", str(where))
        if op == "corr":
            need(all(type(k) is int and k != 0 and abs(k) <= len(word["warps"]) for k in g[3]),
                 "prefix_invertible", "invalid correction symbol")
        kinds[op] += 1
        count += 1
    # Every listed operation has the explicit inverse: negate the shear,
    # reciprocate a nonzero scale, or invert its free native symbol. Buffers
    # are untouched. Their reverse word proves bijectivity for all states.
    return {"dimension": len(live | buffers), "B_cut": cut, "prefix_events_before_cut": count,
            "prefix_opcode_counts": dict(sorted(kinds.items())),
            "argument": "product of invertible shears, nonzero scales and invertible native symbols; dirty buffers are identity"}


def eye(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def product(a, b):
    need(len(a[0]) == len(b), "matrix_shape", "product")
    return [[sum((a[i][k] * b[k][j] for k in range(len(b))), Q(0))
             for j in range(len(b[0]))] for i in range(len(a))]


def matrix(gates, coordinates=LOC):
    # Column-wise execution differs from the row-form derivation below.
    pos = {r: j for j, r in enumerate(coordinates)}
    columns = []
    for j in range(len(coordinates)):
        state = [Q(i == j) for i in range(len(coordinates))]
        for g in gates:
            if g[0] == "add":
                state[pos[g[1]]] += Q(g[3], g[4]) * state[pos[g[2]]]
            elif g[0] == "scale":
                state[pos[g[1]]] *= Q(g[2], g[3])
            else:
                raise Failure("local_opcode", str(g))
        columns.append(state)
    return [list(row) for row in zip(*columns)]


def inverse(gates):
    return [["add", g[1], g[2], -g[3], g[4], *g[5:]] if g[0] == "add"
            else ["scale", g[1], g[3], g[2], *g[4:]] for g in reversed(gates)]


def equal_matrix(actual, expected, rows=None):
    indices = range(len(expected)) if rows is None else rows
    need(all(actual[i] == expected[i] for i in indices), "operator_coefficients", "complete selected output rows")


def det2(a):
    return a[0][0] * a[1][1] - a[0][1] * a[1][0]


def rank_two(a):
    need(det2(a) != 0, "external_rank_two", "source410/source417 minor is singular")


def framed(gates, initial, enforce=True):
    current = {r: basis(fr) for r, fr in initial.items()}
    visited = {r: [current[r]] for r in current}
    for i, g in enumerate(gates):
        common = basis(g[-1])
        for r in scalar_touched(g):
            if enforce:
                need(contained(current[r], common), "frame_monotone", str((i, r)))
            current[r] = common
            visited[r].append(common)
    return current, visited


def add(d, s, q, frame=FRAME):
    q = Q(q)
    return ["add", d, s, q.numerator, q.denominator, list(frame)]


def encode(a):
    return [[str(q) for q in row] for row in a]


def next_frame_witness(word, captures):
    g, h = word["B"][962:964]
    need(g[:5] == ["add", 608, 278, 1, 1] and h[:5] == ["add", 609, 276, 1, 1],
         "next_source_sites", "literal B962 and B963")
    u, v = basis(g[-1]), basis(h[-1])
    join = basis((*u, *v))
    need(len(u) == len(v) == 6 and len(join) == 7,
         "next_frame_dimensions", "rank-six source labels with rank-seven join")
    need(contained(FRAME, u) and contained(FRAME, v),
         "next_frame_dimensions", "both source labels contain F")
    need(contained((26,), u) and not contained((26,), v) and
         contained((3,), v) and not contained((3,), u),
         "incomparable_witness", "26 in U minus V and 3 in V minus U")
    persistent_shear = [add(608, 278, 1, u), add(608, 276, 1, v), add(609, 276, 1, v)]
    failure = reject("persistent sum chart at B963 on physical608", "frame_monotone",
                     lambda: framed(persistent_shear, captures["before_B962"]))
    # A scaled permutation is an admitted positive example of the necessary
    # support pattern. This checks just these two source events, not a suffix.
    monomial = [add(609, 278, Q(1, 2), u), add(608, 276, 2, v)]
    framed(monomial, captures["before_B962"])
    return {"source_sites": [[962, 608, 278], [963, 609, 276]],
            "U_basis": list(u), "V_basis": list(v), "U_V_join_basis": list(join),
            "U_dimension": 6, "V_dimension": 6, "join_dimension": 7,
            "intersection_dimension": len(u) + len(v) - len(join),
            "U_not_V_witness": 26, "V_not_U_witness": 3,
            "persistent_shear_failure": failure,
            "scaled_permutation_two_event_positive_control": [["0", "2"], ["1/2", "0"]]}


def run_provider(word, provider):
    current_domain = arbitrary_current_state(word)
    captures, frame_certificate = frame_witness(word)
    next_frames = next_frame_witness(word, captures)
    raw = word["B"][948:962]
    expected = [
        add(610, 608, -1), add(608, 410, -1), add(610, 609, -1),
        add(609, 410, -1), add(610, 410, 1), add(608, 417, 1),
        add(609, 417, -1), add(612, 417, -1), add(608, 419, 1),
        add(610, 419, -1), add(612, 419, -1), add(609, 421, -1),
        add(610, 421, 1), add(612, 421, -1),
    ]
    need(raw == expected, "local_slice", provider + " literal B948:962")
    # Hand-derived rows in order x,y,z,w,s,t,u,v = LOC.
    closed = eye(8)
    closed[0] = list(map(Q, (1, 0, 0, 0, -1, 1, 1, 0)))
    closed[1] = list(map(Q, (0, 1, 0, 0, -1, -1, 0, -1)))
    closed[2] = list(map(Q, (-1, -1, 1, 0, 1, 0, -1, 1)))
    closed[3] = list(map(Q, (0, 0, 0, 1, 0, -1, -1, -1)))
    equal_matrix(matrix(raw), closed)
    a = [[closed[i][j] for j in (4, 5)] for i in (0, 1)]
    rank_two(a)
    need(det2(a) == 2, "minor_value", "raw determinant")
    shear, unshear = eye(8), eye(8)
    shear[0][1], unshear[0][1] = Q(1), Q(-1)
    conjugated = product(product(shear, closed), unshear)
    consumer = [
        add(610, 608, -1), add(608, 410, -2), add(609, 410, -1),
        add(610, 410, 1), add(609, 417, -1), add(612, 417, -1),
        add(608, 419, 1), add(610, 419, -1), add(612, 419, -1),
        add(608, 421, -1), add(609, 421, -1),
        add(610, 421, 1), add(612, 421, -1),
    ]
    equal_matrix(matrix(consumer), conjugated)
    equal_matrix(matrix(consumer + inverse(consumer)), eye(8))
    equal_matrix(matrix(inverse(consumer) + consumer), eye(8))
    chart_a = [[conjugated[i][j] for j in (4, 5)] for i in (0, 1)]
    need(chart_a == [[Q(-2), Q(0)], [Q(-1), Q(-1)]] and det2(chart_a) == 2,
         "minor_value", "single-shear source minor")
    initial = captures["before_B948"]
    _, visits = framed(consumer, initial)
    need(all(basis(FRAME) in visits[h] for h in PAIR), "pair_F_visit", "both single-shear rows reach F")
    delayed = [add(608, 609, 1, ENTRANCE), *consumer, add(608, 609, -1)]
    equal_matrix(matrix(delayed), closed)
    _, raw_visits = framed(raw, initial)
    _, delayed_visits = framed(delayed, initial)
    def paid_visits(trace):
        out = {}
        for r, frames in trace.items():
            previous, positive = frames[0], []
            for new in frames[1:]:
                if previous != new:
                    positive.append([len(new) - len(previous), list(new)])
                previous = new
            out[str(r)] = positive
        return out
    need(paid_visits(raw_visits) == paid_visits(delayed_visits),
         "local_paid_chain", "legal delayed word retains every local paid frame change")

    controls = [next_frames["persistent_shear_failure"]]
    bad = [list(g) for g in consumer]
    bad[4] = add(609, 417, 1)
    controls.append(reject("wrong source417 sign in conjugated row609", "operator_coefficients",
                           lambda: equal_matrix(matrix(bad), conjugated)))
    equal_matrix(matrix(bad), conjugated, rows=[2, 3, 4, 5, 6, 7])
    ablations = ["consumer-only row comparison accepts the wrong row609 sign"]
    controls.append(reject("dependent minor presented as rank two", "external_rank_two",
                           lambda: rank_two([[Q(-1), Q(1)], [Q(-1), Q(1)]])))
    illegal = [add(608, 410, -1), add(609, 608, 1, ENTRANCE)]
    controls.append(reject("unpaid return from F to E for pair mixing", "frame_monotone",
                           lambda: framed(illegal, initial)))
    framed(illegal, initial, enforce=False)
    ablations.append("removing monotone containment admits the illegal F-to-E pair gate")
    controls.append(reject("off-by-one source slice", "local_slice",
                           lambda: need(word["B"][949:963] == expected, "local_slice", "wrong cut")))

    # A rank-one two-source map admits a genuine protected row. Its entrance
    # chart is (x,x-y), and the consumer writes only its first physical row.
    dependent_raw = [add(608, 410, -1), add(609, 410, -1),
                     add(608, 417, 1), add(609, 417, 1)]
    dependent_chart = eye(8)
    dependent_chart[1][0], dependent_chart[1][1] = Q(1), Q(-1)
    dependent = [add(608, 410, -1), add(608, 417, 1)]
    equal_matrix(matrix(dependent), product(product(dependent_chart, matrix(dependent_raw)), dependent_chart))
    _, dep_visits = framed(dependent, initial)
    need(basis(FRAME) in dep_visits[608] and basis(FRAME) not in dep_visits[609],
         "positive_control", "dependent columns can keep row609 low")

    # If the logical pair delivery is dropped, the shared consumer is correct
    # on every outside row while the protected pair row remains low. The full
    # endpoint comparison must reject this weaker terminal contract.
    projection_only = [g for g in consumer if g[1] not in PAIR]
    equal_matrix(matrix(projection_only), conjugated, rows=[2, 3, 4, 5, 6, 7])
    controls.append(reject("consumer projection mistaken for complete pair delivery", "operator_coefficients",
                           lambda: equal_matrix(matrix(projection_only), conjugated)))
    _, projection_visits = framed(projection_only, initial)
    need(basis(FRAME) not in projection_visits[609], "positive_control", "projected terminal can keep row609 low")

    # Allowing outside source gates at a larger common frame invalidates exact
    # F necessity, although it changes the paid source/interface boundary.
    higher = basis((*FRAME, 256))
    need(len(higher) == 5 and contained(FRAME, higher), "positive_control", "strict overframe")
    overframe_consumer = [g[:-1] + [list(higher)] for g in consumer]
    equal_matrix(matrix(overframe_consumer), conjugated)
    _, high_visits = framed(overframe_consumer, initial)
    need(all(basis(FRAME) not in high_visits[h] and higher in high_visits[h] for h in PAIR),
         "positive_control", "changed source frame bypasses the exact rank-four level")

    # With a third dirty helper, a permutation chart can move logical y to it.
    # Both independent channels still visit F, but physical row609 stays low.
    more = (*LOC, 2048)  # Toy new helper, outside all 723 frozen coordinates.
    swap = eye(9)
    swap[1][1] = swap[8][8] = Q(0)
    swap[1][8] = swap[8][1] = Q(1)
    extra_raw = matrix(raw, more)
    moved = [[g[0], 2048 if g[1] == 609 else g[1],
              2048 if g[2] == 609 else g[2], *g[3:]] for g in raw]
    equal_matrix(matrix(moved, more), product(product(swap, extra_raw), swap))
    extra_initial = dict(initial)
    extra_initial[2048] = basis(ENTRANCE)
    _, extra_visits = framed(moved, extra_initial)
    need(basis(FRAME) not in extra_visits[609] and
         all(basis(FRAME) in extra_visits[r] for r in (608, 2048)),
         "positive_control", "extra helper relocates, without eliminating, the second F channel")

    return {
        "provider": provider, "current_state": current_domain,
        "current_state_before_next_sources": arbitrary_current_state(word, 962),
        "source_decompressed_sha256": digest(json.dumps(word, sort_keys=True, separators=(",", ":")).encode()),
        "frame_certificate": frame_certificate,
        "local_coordinates": list(LOC), "local_raw_operator": encode(closed),
        "source410_source417_minor": encode(a), "minor_determinant": "2",
        "single_shear_consumer": consumer, "single_shear_operator": encode(conjugated),
        "single_shear_minor": encode(chart_a),
        "incomparable_next_source_frames": next_frames,
        "legal_delayed_word": delayed,
        "identical_local_paid_chains": paid_visits(raw_visits),
        "legal_delayed_word_adds": len(delayed),
        "raw_local_adds": len(raw), "single_shear_local_adds": len(consumer),
        "entry_chart_and_eventual_unmix_not_included_in_local_add_count": True,
        "rejected_controls": controls, "guard_ablations_detected": ablations,
        "positive_controls": [
            "dependent columns permit one pair cell below F",
            "outside consumer projection permits one pair cell below F, while full pair delivery fails",
            "changed external-gate overframe bypasses exact F and changes the source boundary",
            "third dirty helper relocates the second F channel and changes helper support",
            "scaled permutation satisfies the two fixed rank-six source events",
        ],
    }


def main():
    ap = ArgumentParser()
    ap.add_argument("--package", type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    pins = authenticate(args.package)
    controls = [reject("changed semantic source bytes", "source_sha256",
                       lambda: bind_bytes(b"not the frozen word", pins["source4096/source4076/inputs/NEW-base.json.gz"]["sha256"], "control"))]
    providers = {}
    for name in ("base", "extra"):
        rel = "source4096/source4076/inputs/NEW-" + name + ".json.gz"
        raw = (args.package / rel).read_bytes()
        bind_bytes(raw, pins[rel]["sha256"], rel)
        providers[name] = run_provider(decode(gzip.decompress(raw)), name)
    result = {
        "status": "PASS_INDEPENDENT_LOCAL_CHART_AND_FRAME_WITNESSES",
        "PR4096_head": PR4096_HEAD, "PR4076_head": PR4076_HEAD,
        "canonical_base": CANONICAL_BASE, "outer_export_sha256": EXPORT_SHA256,
        "authenticated_files": pins, "source_binding_controls": controls,
        "providers": providers,
        "theorem_level": "finite exact matrix/frame witnesses plus written all-chart argument in REVIEW.md; no formal-kernel proof",
        "limits": "No complete paid-cost optimum, full changed-word admission, native phase, owner, physical supplier, outer recurrence or kappa claim.",
    }
    if args.out:
        args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "providers": list(providers),
                      "source_minor_determinant": "2", "local_matrix_dimension": 8,
                      "arbitrary_current_state_dimension": 723,
                      "rejecting_controls": len(controls) + sum(len(p["rejected_controls"]) for p in providers.values()),
                      "positive_controls": sum(len(p["positive_controls"]) for p in providers.values())}, sort_keys=True))


if __name__ == "__main__":
    main()
