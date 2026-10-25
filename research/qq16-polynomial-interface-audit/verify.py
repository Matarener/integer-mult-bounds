#!/usr/bin/env python3
"""Independent QQ16 component-format audit. Apache-2.0; OpenAI Codex assistance.

No predecessor executable, loader, event expander or envelope is imported.
Magnitudes are rational polynomials in z=2**(lambda-1). Grids are maxima
of affine functions of t=lambda-1, retaining their intercept/slope pairs.
"""

import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import io
import json
from pathlib import Path
import stat
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "20ecf2891d80b5acf18d980b2164fb44ea7faa90"
PREDECESSOR = "f9031ff1412c9a4e62a38306009ae9c334cfc34e"
CERT = "research/joint-query/certificate.json.gz"
ARCHIVE = "research/community-frontier1042-audit/selected-replay.tar.gz"
CLAIM = "research/qq16-all-depth-producer-grid/RESULT.json"
MEMBERS = {
    "slots/local/CLIFFORD-RECIPES.json":
        "d0768f2164d5f64a2fdbec422f1cfde4e400818792f1904ca541958377243731",
    "slots/local/RESIDUAL-ADAPTERS.json":
        "383f40aadd00a4ac700dfd0d4c22d6c6c0be9a9863116e4d69c7acd23bafae0c",
}
INPUT_PATHS = {
    CERT, ARCHIVE, CLAIM,
    "research/joint-query/evidence/CONSERVED-QQ16.md",
    "research/joint-query/evidence/NATIVE-REVIEW.md",
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def sha(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def unique_object(pairs):
    out = {}
    for key, value in pairs:
        need(key not in out, "duplicate JSON key")
        out[key] = value
    return out


def decode(raw):
    return json.loads(raw, object_pairs_hook=unique_object)


def read_file(path, limit=24_000_000):
    need(stat.S_ISREG(path.lstat().st_mode), "regular input file required")
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    need(len(raw) <= limit, "input capacity exceeded")
    return raw


def load(root=ROOT):
    manifest = decode(read_file(HERE / "SOURCES.json", 65536))
    need(manifest["base_commit"] == BASE, "scientific base")
    rows = manifest["files"]
    need(len({r["path"] for r in rows}) == len(rows), "unique pin paths")
    need({r["path"] for r in rows if r["usage"] == "input"} == INPUT_PATHS,
         "fixed scientific input inventory")
    inputs = {}
    for row in rows:
        need(row["usage"] in ("input", "provenance"), "pin usage")
        if row["usage"] == "input":
            raw = read_file(root / row["path"])
            need(hashlib.sha256(raw).hexdigest() == row["sha256"], "source SHA256")
            blob = hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()
            need(blob == row["git_blob"], "source Git blob")
            inputs[row["path"]] = raw
    with gzip.GzipFile(fileobj=io.BytesIO(inputs[CERT])) as stream:
        raw = stream.read(12_000_001)
    need(len(raw) <= 12_000_000, "decoded packet capacity")
    need(hashlib.sha256(raw).hexdigest() ==
         "2efe83c59978aa9c0db2c3e4eccc14cbfdcd3c9ce499432601b5dd34083472ef",
         "decoded packet SHA256")
    packet = decode(raw)
    need(packet["schema"] == "conserved-qq16-full-cover-native-words-v1", "packet schema")
    need(packet["field_namespace"] == {"C": [0, 7], "L": [0, 703],
                                       "formal_input_columns": 712}, "fixed field namespace")
    objects = {}
    with tarfile.open(fileobj=io.BytesIO(inputs[ARCHIVE]), mode="r:gz") as archive:
        records = archive.getmembers()
        need(len(records) <= 1000 and len({r.name for r in records}) == len(records),
             "bounded unique archive members")
        need(all(not (r.issym() or r.islnk()) for r in records), "archive links")
        for name, digest in MEMBERS.items():
            record = next(r for r in records if r.name == name)
            need(record.isfile() and record.size <= 12_000_000, "regular bounded member")
            with archive.extractfile(record) as stream:
                raw = stream.read(12_000_001)
            need(hashlib.sha256(raw).hexdigest() == digest, "native member SHA256")
            objects[name] = decode(raw)
    return (packet, objects["slots/local/CLIFFORD-RECIPES.json"],
            objects["slots/local/RESIDUAL-ADAPTERS.json"], decode(inputs[CLAIM]))


def index(token):
    need(type(token) is list and len(token) == 2, "port token")
    bank, number = token
    need(type(number) is int and bank in ("L", "C"), "port type")
    need(0 <= number < (704 if bank == "L" else 8), "port range")
    return number if bank == "L" else number + 704


def expand(packet, name):
    """Independently visit the literal program and retain each source address."""
    program = packet["programs"][name]
    need(type(program) is list and len(program) <= 1000, "program capacity")
    events, addresses = [], []
    for outer, item in enumerate(program):
        tag = item[0]
        if tag == "retained_core":
            need(item[1] in ("forward", "backward"), "core orientation")
            children = packet["core_words"][item[1]]
        elif tag in ("cover_sweep", "private_sweep"):
            need(type(item[2]) is list, "sweep program")
            children = item[2]
        else:
            children = [item]
        for inner, event in enumerate(children):
            need(event[0] in {"scalar", "climb", "adapter", "residual_adapter",
                              "phase", "native_line", "cover_map"}, "literal event kind")
            events.append(event)
            addresses.append([outer, inner, tag])
            need(len(events) <= 27019, "expanded event capacity")
    need(len(events) == {"F_0": 26099, "B_1_2": 27019}[name], "stage length")
    return events, addresses


def inverse_binary(columns):
    """Gauss-Jordan inverse, using rows reconstructed from source columns."""
    width = len(columns)
    need(width == 73 and all(type(x) is int and 0 <= x < 1 << width
                            for x in columns), "73-axis owner matrix")
    rows = [sum(((columns[j] >> i) & 1) << j for j in range(width)) |
            (1 << (width + i)) for i in range(width)]
    for j in range(width):
        candidates = [i for i in range(j, width) if rows[i] >> j & 1]
        need(candidates, "singular owner matrix")
        at = candidates[0]
        rows[j], rows[at] = rows[at], rows[j]
        for i in range(width):
            if i != j and rows[i] >> j & 1:
                rows[i] ^= rows[j]
    need(all(row & ((1 << width) - 1) == 1 << i for i, row in enumerate(rows)),
         "inverse left identity")
    inverse_rows = [row >> width for row in rows]
    for j, column in enumerate(columns):
        image = sum(((row & column).bit_count() % 2) << i
                    for i, row in enumerate(inverse_rows))
        need(image == 1 << j, "inverse right identity")
    return inverse_rows


def monomial_check(m):
    need(set(m) == {"matrix_rows", "quadratic_rows", "linear_Z4", "offset", "phase"},
         "monomial shape")
    matrix, quadratic, linear = (m[k] for k in
                                ("matrix_rows", "quadratic_rows", "linear_Z4"))
    need(len(matrix) == len(quadratic) == len(linear) == 9, "nine-axis monomial")
    need(all(type(x) is int and 0 <= x < 512 for x in matrix + quadratic),
         "binary monomial rows")
    need(all(type(x) is int and 0 <= x < 4 for x in linear), "quarter-turn phases")
    need(type(m["offset"]) is int and 0 <= m["offset"] < 512, "monomial offset")
    need(type(m["phase"]) is int and 0 <= m["phase"] < 4, "global phase")
    # Exhaustive image bijection, rather than the predecessor's rank routine.
    images = {sum(((row & x).bit_count() % 2) << i
                  for i, row in enumerate(matrix)) ^ m["offset"] for x in range(512)}
    need(len(images) == 512, "monomial is not a permutation")


def valuation(n):
    need(type(n) is int and n != 0, "nonzero integer valuation")
    exponent = 0
    n = abs(n)
    while n % 2 == 0:
        exponent += 1
        n //= 2
    return exponent


# A value is (nonnegative coefficient tuple, tuple of (slope, intercept)).
ZERO = ((), ())
UNIT = ((Q(1),), ((0, 0),))


def frontier(forms):
    by_slope = {}
    for slope, intercept in forms:
        by_slope[slope] = max(intercept, by_slope.get(slope, intercept))
    # Remove only pairwise dominance for t>=0; retaining extras is safe.
    return tuple((s, g) for s, g in sorted(by_slope.items())
                 if not any(s2 >= s and g2 >= g and (s2, g2) != (s, g)
                            for s2, g2 in by_slope.items()))


def add(left, right):
    if not left[0]:
        return right
    if not right[0]:
        return left
    a, b = left[0], right[0]
    polynomial = tuple((a[i] if i < len(a) else Q(0)) +
                       (b[i] if i < len(b) else Q(0))
                       for i in range(max(len(a), len(b))))
    return polynomial, frontier(left[1] + right[1])


def scale(value, coefficient):
    coefficient = Q(coefficient)
    need(coefficient.denominator & (coefficient.denominator - 1) == 0, "dyadic scalar")
    if not coefficient or not value[0]:
        return ZERO
    shift = coefficient.denominator.bit_length() - 1 - valuation(coefficient.numerator)
    return (tuple(c * abs(coefficient) for c in value[0]),
            tuple((s, g + shift) for s, g in value[1]))


def gaussian(value):
    """Envelope for lambda successive coordinate lines on one active axis.

    Pair/cross observations bound every intermediate layer. Final values use
    exactly the polynomial multiplier 2*z and grid shift lambda=1+t.
    """
    if not value[0]:
        return ZERO, ZERO, ZERO
    p, forms = value
    pair = ((Q(0),) + tuple(2 * c for c in p),
            tuple((s + 1, g) for s, g in forms))
    cross = ((Q(0),) + tuple(4 * c for c in p), pair[1])
    output = (pair[0], tuple((s + 1, g + 1) for s, g in forms))
    return pair, cross, output


def encoded(value):
    return [[str(c) for c in value[0]], value[1]]


class Audit:
    def __init__(self):
        self.trace = hashlib.sha256()
        self.count = 0
        self.max_sum, self.max_degree = Q(1), 0
        self.grid_forms = ()
        self.max_location = None
        self.position = None
        self.cost = Counter()
        self.monomials = set()

    def observe(self, value, label):
        polynomial, forms = value
        need(len(polynomial) <= 20 and len(forms) <= 20, "symbolic capacity")
        need(all(c >= 0 for c in polynomial), "nonnegative envelope coefficients")
        total = sum(polynomial, Q(0))
        if total > self.max_sum:
            self.max_sum, self.max_location = total, [self.position, label]
        if polynomial:
            self.max_degree = max(self.max_degree, len(polynomial) - 1)
            self.grid_forms = frontier(self.grid_forms + forms)
        self.trace.update(canonical([self.position, label, encoded(value)]) + b"\n")
        self.count += 1
        return value

    def multiply(self, value, coefficient):
        c = Q(coefficient)
        need(c != 0, "nonzero source multiplier")
        n, d = c.numerator, c.denominator
        # Densities per N complex-payload coordinates (two real components).
        self.cost["constant_product_calls"] += 1
        self.cost["constant_product_component_copies"] += 2 * abs(n).bit_count()
        self.cost["constant_product_additions"] += 2 * (abs(n).bit_count() - 1)
        self.cost["constant_product_left_shifts"] += 2 * (abs(n).bit_count() - (abs(n) & 1))
        self.cost["constant_product_negations"] += 2 * (n < 0)
        self.cost["constant_product_right_shifts"] += 2 * (d > 1)
        partial = (tuple(abs(n) * x for x in value[0]), value[1]) if value[0] else ZERO
        self.observe(partial, "integer-product-partials")
        numerator = self.observe(scale(value, n), "integer-numerator")
        return self.observe(scale(numerator, Q(1, d)), "dyadic-product")

    def mono(self, value, record):
        key = sha(record)
        if key not in self.monomials:
            monomial_check(record)
            self.monomials.add(key)
        self.cost["monomial_calls"] += 1
        self.cost["monomial_component_copies"] += 4
        self.cost["monomial_component_negations_upper_bound"] += 2
        return self.observe(value, "tensor-monomial")

    def recipe(self, value, recipe):
        r = recipe["rank"]
        need(type(r) is int and 0 <= r <= 9, "Gaussian rank")
        self.cost["native_recipe_calls"] += 1
        if r:
            value = self.mono(value, recipe["right"])
        else:
            need(recipe["right"] is None, "rank-zero recipe right factor")
        for _ in range(r):
            self.cost["native_gaussian_lines"] += 1
            self.cost["native_real_additions"] += 4
            self.cost["native_exact_halvings"] += 2
            self.cost["native_pair_component_copies"] += 4
            pair, cross, value = gaussian(value)
            self.observe(pair, "tensor-pair-interiors")
            self.observe(cross, "tensor-cross-interiors")
            self.observe(value, "tensor-line-output")
        return self.mono(value, recipe["left"])


def run(packet, recipes, residuals, reset_at_b1=False):
    children = {(r["old"], r["new"]): r for r in recipes["children"]}
    adapters = {(r["role"], r["port"]): r for r in recipes["endpoint_adapters"]}
    need(len(children) == len(recipes["children"]) and
         len(adapters) == len(recipes["endpoint_adapters"]), "unique native keys")
    state = [UNIT for _ in range(704)] + [ZERO for _ in range(8)]
    audit = Audit()
    stages, covers = {}, set()
    for name in ("F_0", "B_1_2"):
        if name == "B_1_2" and reset_at_b1:
            state = [UNIT for _ in range(704)] + [ZERO for _ in range(8)]
        events, addresses = expand(packet, name)
        start = sha([encoded(v) for v in state])
        complete = hashlib.sha256()
        kinds = Counter()
        for at, event in enumerate(events):
            audit.position = [name, at]
            kind = event[0]
            kinds[kind] += 1
            if kind == "phase":
                audit.cost["phase_labels"] += 1
                continue
            if kind == "scalar":
                gate = event[1]
                target = index(gate[1])
                if gate[0] == "clear":
                    need(target >= 704, "borrowed/data clear forbidden")
                    state[target] = ZERO
                    audit.cost["clear_component_writes"] += 2
                elif gate[0] == "scale":
                    state[target] = audit.multiply(state[target], Q(gate[2], gate[3]))
                else:
                    need(gate[0] == "add", "scalar opcode")
                    source = index(gate[2])
                    term = audit.multiply(state[source], Q(gate[3], gate[4]))
                    state[target] = audit.observe(add(state[target], term), "field-add")
                    audit.cost["scalar_real_additions"] += 2
            else:
                target = index(event[1]) if kind in ("native_line", "cover_map") else event[2]
                need(type(target) is int and 0 <= target < 712, "native target")
                if kind == "climb":
                    need(event[5] == children[event[3], event[4]]["rank"], "declared child rank")
                    state[target] = audit.recipe(state[target], children[event[3], event[4]])
                elif kind == "native_line":
                    state[target] = audit.recipe(
                        state[target], packet["native_line_recipes"][event[2]]["recipe"])
                elif kind == "adapter":
                    if event[1] == "old_to_new" and target < 112:
                        state[target] = audit.mono(state[target], adapters["source", target]["left"])
                    elif event[1] == "new_to_old" and 112 <= target < 224:
                        state[target] = audit.mono(state[target], adapters["target", target-112]["left"])
                    else:
                        need(event[1] in ("old_to_new", "new_to_old"), "adapter direction")
                        audit.cost["adapter_identity_labels"] += 1
                elif kind == "residual_adapter":
                    direction, _, a = event[1:4]
                    need(direction in ("pre", "post"), "residual direction")
                    b = event[4] if len(event) == 5 else 1
                    key = str(a) if b == 1 else f"{a}:{b}"
                    state[target] = audit.mono(state[target], residuals["recipes"][key][
                        "right" if direction == "pre" else "left"])
                else:
                    need(kind == "cover_map", "cover opcode")
                    covers.add(event[2])
                    audit.cost["full_cover_maps"] += 1
                    audit.cost["cover_component_transfers"] += 4
                    audit.observe(state[target], "cover-owner-uniform")
            audit.observe(state[target], "completed-source-event")
            complete.update(canonical([at, target, encoded(state[target])]) + b"\n")
        stages[name] = {"events": len(events), "event_sha256": sha(events),
                        "source_addresses_sha256": sha(addresses),
                        "event_kinds": dict(sorted(kinds.items())),
                        "entry_sha256": start, "completed_sha256": complete.hexdigest(),
                        "exit_sha256": sha([encoded(v) for v in state])}
    need(stages["F_0"]["exit_sha256"] == stages["B_1_2"]["entry_sha256"],
         "literal F0-to-B1 state carry")
    need(all(v == ZERO for v in state[704:]), "eight private fields clear")
    maps = []
    for key in sorted(covers):
        record = packet["map_registry"][key]
        inverse = inverse_binary(record["owner_right_matrix_columns"])
        delta = record["payload_translation_at_identity_owner"]
        need(type(delta) is int and 0 <= delta < 1 << 73, "73-axis cover translation")
        need(record["action"] == "out(d,z_1,...,z_lambda)=in(d*g,"
             "z_1 XOR d*delta,...,z_lambda XOR d*delta)", "cover action contract")
        maps.append([key, sha(inverse), delta])
    return audit, stages, maps


NUMERIC = (
    "clear_component_writes", "constant_product_additions",
    "constant_product_component_copies", "constant_product_left_shifts",
    "constant_product_negations", "constant_product_right_shifts",
    "monomial_component_copies", "monomial_component_negations_upper_bound",
    "native_exact_halvings", "native_pair_component_copies",
    "native_real_additions", "scalar_real_additions",
)


def certify(audit, stages, maps, claimed):
    need(audit.count == 270288, "complete primitive observation coverage")
    need(len(maps) == 512, "distinct cover maps")
    need(audit.max_degree == 19 and audit.grid_forms == ((19, 71),), "all-depth slopes/grid")
    need(audit.max_sum == Q(35714190970741142696015664337123072062513575, 4),
         "one-layer magnitude sum")
    need(audit.max_sum < 1 << 143, "strict component magnitude capacity")
    for name in stages:
        need(stages[name]["event_sha256"] == claimed["stages"][name]["event_sha256"],
             "independent event expansion versus published claim")
    costs = dict(sorted(audit.cost.items()))
    old_cost = claimed["direct_cost_at_one"]
    need(set(costs) | {"final_owned_scratch_clear_writes"} == set(old_cost),
         "complete published counter inventory")
    for key, number in costs.items():
        density = (1024 if key == "constant_product_calls" else
                   1 if key in {"adapter_identity_labels", "full_cover_maps", "monomial_calls",
                                "native_gaussian_lines", "native_recipe_calls", "phase_labels"}
                   else 512)
        need(number * density == old_cost[key], "independent primitive tariff: " + key)
    # One reusable cover buffer and twelve scalar words are finally cleared.
    numeric_at_one = 512 * (sum(costs[k] for k in NUMERIC) + 2) + 12
    line_density = 10 * costs["native_gaussian_lines"]
    fixed_density = sum(costs[k] for k in NUMERIC) + 2 - line_density
    need(numeric_at_one == 247337996, "summed numeric reference invoice")
    need((fixed_density, line_density, costs["cover_component_transfers"])
         == (372322, 110760, 2112), "symbolic cost coefficients")
    need(old_cost["final_owned_scratch_clear_writes"] == 2 * 512 + 12,
         "final reusable scratch clear")
    result = {
        "status": "PASS_QQ16_POLYNOMIAL_INTERFACE_AUDIT",
        "base_commit": BASE, "audited_pr_head": PREDECESSOR,
        "method": "positive rational polynomials and retained max-plus grid lines; independent raw source expansion",
        "events": sum(s["events"] for s in stages.values()), "stages": stages,
        "primitive_observations": audit.count, "polynomial_trace_sha256": audit.trace.hexdigest(),
        "maximum_polynomial_degree": audit.max_degree, "grid_affine_frontier": audit.grid_forms,
        "maximum_polynomial_at_one": str(audit.max_sum), "maximum_location": audit.max_location,
        "quantum_guard": "71+19*(lambda-1)", "signed_width": "P+215+38*(lambda-1)",
        "independent_counters": costs,
        "numeric_units_per_N": {k: costs[k] for k in NUMERIC},
        "counter_units": "numeric_units_per_N is calibrated at lambda=1: native_real_additions, native_exact_halvings and native_pair_component_copies scale with N*lambda; other numeric entries and cover_component_transfers scale with N; remaining counters count literal labels/calls",
        "wordops_fixed_per_N": fixed_density,
        "wordops_lambda_per_N": line_density, "wordops_constant": 12,
        "cover_transfers_per_N": costs["cover_component_transfers"],
        "numeric_storage_words_per_N": 2 * 712 + 2, "scalar_scratch_words": 12,
        "owner_inverse_inventory_sha256": sha(maps), "distinct_owner_maps": len(maps),
        "unique_nine_axis_monomials": len(audit.monomials),
        "full_native_functionality_reproved": False, "physical_tariff_priced": False,
        "literal_borrowed_restoration_claim": False, "new_supplier_or_kappa": False,
    }
    expected_fields = {
        "grid_intercept_at_one": 71, "grid_slope": 19, "range_bits_at_one": 143,
        "range_slope": 19, "signed_width_P_plus_at_one": 215, "signed_width_slope": 38,
        "tensor_linear_wordops_per_N": line_density, "tensor_constant_wordops_per_N": fixed_density,
        "cover_transfers_per_N": 2112, "storage_words_per_N": 1426, "scalar_scratch_words": 12,
    }
    need(all(type(claimed[k]) is int and claimed[k] == v for k, v in expected_fields.items()),
         "published numerical theorem coefficients")
    need(claimed["physical_routing_priced"] is False and claimed["supplier_admission"] is False,
         "published scope remains conditional")
    return result


def audit(root=ROOT):
    packet, recipes, residuals, claimed = load(root)
    envelope, stages, maps = run(packet, recipes, residuals)
    return certify(envelope, stages, maps, claimed)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="create an absent receipt")
    args = parser.parse_args()
    result = audit()
    if args.write:
        with args.write.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(result, indent=2) + "\n")
    else:
        need(canonical(result) == canonical(decode(read_file(HERE / "RESULT.json", 65536))),
             "independent receipt mismatch")
    print(result["status"], "events=53118 primitives=270288 all_lambda>=1 no_new_kappa")


if __name__ == "__main__":
    main()
