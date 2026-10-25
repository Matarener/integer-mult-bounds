"""Source-bound rational FFT lowering to H/2 and rounded diagonal stages.

Jose Manuel (jmbarrancoml), with substantial OpenAI Codex assistance.
Apache-2.0. Fixed words, Beneš routing and FFT schedule: Vlado Vojdanovski.
Rational phases: Chafik Boukhalfa and the retained PR628 lineage.
"""
import ast
import copy
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREFIX = "research/rational-fft-fixed-h/"
EXACT = PREFIX + "vendor/rational_fft/exact.py"
ENGINE = PREFIX + "vendor/rational_fft/engine.py"
PROVENANCE = PREFIX + "vendor/PROVENANCE.json"
CIRCUIT = "research/capped-phase-fusion/evidence/inplace_algebra_ultra/check_circuits.py"
TENSOR = "research/capped-phase-fusion/evidence/inplace_algebra_ultra/check_tensor_compiler.py"
ORACLE = "research/cubic-cyclic-inverse/vendor/interval_kernel.py"
DENSE_PREFIX = PREFIX + "vendor/full_source/"
DENSE_CONTEXT = {"research/unconditional-batched-crt/vendor/GAUGEFREE-INTERIORS.md",
                 "research/unconditional-batched-crt/vendor/SHALLOW-TOEPLITZ.md"}
K = 1 << 14


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def norm2(vector):
    return sum((z.norm2() for z in vector), Q(0))


def authenticate(overrides=None):
    rows = json.loads((HERE / "SOURCES.json").read_text())["files"]
    raw, seals = {}, []
    for row in rows:
        if row["usage"] != "input":
            continue
        path = row["path"]
        value = (overrides or {}).get(path)
        if value is None:
            value = (ROOT / path).read_bytes()
        need(sha256(value).hexdigest() == row["sha256"], "source SHA256: " + path)
        raw[path] = value
        seals.append(dict(path=path, sha256=row["sha256"]))
    provenance = json.loads(raw[PROVENANCE])
    for row in provenance["files"]:
        need(sha256(raw[row["retained_path"]]).hexdigest() == row["sha256"],
             "unchanged published FFT producer")
    return raw, seals


class Sources:
    def __init__(self, overrides=None, include_dense=False):
        need(type(include_dense) is bool, "declared source inventory")
        self.raw, all_seals = authenticate(overrides)
        self.seals = [row for row in all_seals if include_dense
                      or not (row["path"].startswith(DENSE_PREFIX) or row["path"] in DENSE_CONTEXT)]
        self.e = ModuleType("_fixed_h_retained_exact")
        exec(compile(self.raw[EXACT], "<authenticated PR4205 exact arithmetic>", "exec", optimize=0),
             self.e.__dict__)
        self.engine = ModuleType("_fixed_h_retained_engine")
        previous = sys.modules.get("exact")
        sys.modules["exact"] = self.e
        try:
            exec(compile(self.raw[ENGINE], "<authenticated PR4205 FFT producer>", "exec", optimize=0),
                 self.engine.__dict__)
        finally:
            if previous is None:
                del sys.modules["exact"]
            else:
                sys.modules["exact"] = previous
        names = {"benes", "D", "u3", "id2", "id3", "canonical", "gateword",
                 "matching_permutation", "local_layer"}
        tree = ast.parse(self.raw[TENSOR])
        tree.body = [copy.deepcopy(node) for node in tree.body
                     if isinstance(node, ast.FunctionDef) and node.name in names]
        need({node.name for node in tree.body} == names, "complete fixed-word compiler closure")
        self.tensor_ast = sha256(ast.dump(tree).encode()).hexdigest()
        C = self.e.C
        scalar = SimpleNamespace(sympify=C.wrap, simplify=C.wrap, Integer=lambda n: C(n),
                                 Rational=lambda a, b=1: C(Q(a, b)), I=C(0, 1))
        self.ns = dict(s=scalar)
        exec(compile(tree, "<authenticated six-H and Benes compiler>", "exec", optimize=0), self.ns)

    def matrix_hash(self, matrix):
        return sha256((str((len(matrix), len(matrix[0]) if matrix else 0))
                       + self.e.vector_hash(x for row in matrix for x in row)).encode()).hexdigest()

    def word_endpoint(self, word):
        C, Mat = self.e.C, self.e.Mat
        matrix = Mat([[1, 0], [0, 1]])
        for operation in word:
            left = Mat([[1, 1], [1, -1]]) if operation == "H" else Mat(
                [[operation[0], 0], [0, operation[1]]])
            matrix = Mat([[sum((left[i][k] * matrix[k][j] for k in range(2)), C())
                           for j in range(2)] for i in range(2)])
        return matrix

    def butterfly_word(self, a, b, phase, adjoint=False):
        C = self.e.C
        need(type(a) is Q and type(b) is Q and a >= Q(1, 2) and b >= Q(1, 2)
             and a * a + b * b == 1 and phase.norm2() == 1, "bounded rational unit splitter")
        r, t = C(b / a), phase * (b / a)
        word = self.ns["canonical"](self.ns["u3"](t) + [self.ns["D"](a, -phase / a)]
                                    + list(reversed(self.ns["u3"](r))))
        if adjoint:
            word = [op if op == "H" else tuple(z.conjugate() for z in op)
                    for op in reversed(word)]
        return word

    def gate_word(self, gate):
        Mat = self.e.Mat
        if gate == Mat([[0, 1], [1, 0]]):
            kind, word = "swap", self.ns["gateword"]("swap")
        elif gate[0][0].im == gate[1][0].im == 0 and min(gate[0][0].re, gate[1][0].re) >= Q(1, 2):
            a, b = gate[0][0].re, gate[1][0].re
            phase = gate[0][1] / b
            kind, word = "butterfly", self.butterfly_word(a, b, phase)
        else:
            need(gate[0][0].im == gate[0][1].im == 0, "stored FFT adjoint orientation")
            a, b = gate[0][0].re, gate[0][1].re
            phase = (gate[1][0] / b).conjugate() if b != 0 else self.e.C()
            kind, word = "adjoint", self.butterfly_word(a, b, phase, True)
        need(len(word) == 13 and sum(op == "H" for op in word) == 6,
             "six-H seven-diagonal shape")
        need(self.word_endpoint(word) == gate, "exact endpoint equals the actual stored gate")
        return kind, word


def stage_hash(source, stages):
    rows = [(kind, value if kind == "H" else source.e.vector_hash(value)) for kind, value in stages]
    return sha256(canonical(rows)).hexdigest()


def plan_hash(source, plan):
    return sha256(canonical([[(list(ids), source.matrix_hash(gate)) for ids, gate in layer]
                             for layer in plan])).hexdigest()


class FFT:
    def __init__(self, source, size, indices, radius, target, incoming=0, *, adjoint=False,
                 phase_bits=None, data_bits=None):
        need(type(size) is int and size > 0 and size & (size - 1) == 0, "dyadic complete field")
        need(indices and all(type(i) is int and 0 <= i < size for i in indices)
             and len(set(indices)) == len(indices), "distinct oriented integer FFT wires")
        n = len(indices)
        need(n & (n - 1) == 0, "dyadic active FFT size")
        need(type(radius) in (int, Q) and radius >= 1 and type(target) is int and target >= 1
             and type(incoming) is int and incoming >= 0 and type(adjoint) is bool,
             "exact input radius, target, grid and direction")
        self.source, self.e = source, source.e
        self.size, self.indices, self.radius = size, tuple(indices), Q(radius)
        self.target, self.incoming, self.adjoint = target, incoming, adjoint
        d, field_d = n.bit_length() - 1, size.bit_length() - 1
        self.original_layers = d + 1 if d else 0
        self.stage_count = self.original_layers * (16 * field_d + 5)
        self.diagonal_count = self.original_layers * (8 * field_d + 3)
        self.h_count = self.original_layers * (8 * field_d + 2)
        required_phase = max(3, target + self.e.ceil_log2(8 * d * (radius + 1))) if d else 3
        self.phase_bits = required_phase if phase_bits is None else phase_bits
        need(type(self.phase_bits) is int and self.phase_bits >= required_phase,
             "funded phase precision and splitter chart")
        required_data = max(incoming, target + self.e.ceil_log2(16 * self.diagonal_count * K ** 2 * (radius + 1)),
                            target + self.e.ceil_log2(16 * K * self.stage_count * size)) if d else max(incoming, 1)
        self.bits = required_data if data_bits is None else data_bits
        need(type(self.bits) is int and self.bits >= required_data, "funded native coefficient/data grid")
        self.phases = source.engine.Phases(self.phase_bits, source.raw[ORACLE])
        self.builder = source.engine.Builder(self.phases, self.bits, source.raw[CIRCUIT])
        forward = self.builder.namespace["fft"](list(indices))
        self.plan = self.builder.namespace["inverse"](forward) if adjoint else forward
        need(len(self.plan) == self.original_layers, "retained FFT matching-layer count")
        self.reference_hash = plan_hash(source, self.plan)
        self.raw_stages, self.layers, self.words = [], [], []
        for layer in self.plan:
            pairs, words, kinds, used = [], [], [], set()
            for ids, gate in layer:
                need(len(ids) == 2 and len(set(ids)) == 2 and not used.intersection(ids)
                     and all(type(i) is int and 0 <= i < size for i in ids), "matching wire ownership")
                need(self.e.unitary(gate), "unitary completed FFT gate")
                kind, word = source.gate_word(gate)
                used.update(ids)
                pairs.append(tuple(ids))
                words.append(word)
                kinds.append(kind)
            free = [i for i in range(size) if i not in used]
            for j in range(0, len(free), 2):
                pairs.append(tuple(free[j:j + 2]))
                words.append(source.ns["gateword"]("diag", (1, 1)))
                kinds.append("idle")
            need(len(pairs) == len(words) == size // 2, "complete matching and inactive words")
            permutation = source.ns["matching_permutation"](size, pairs)
            network = source.ns["benes"](permutation)
            self.check_network(permutation, network)
            stages = source.ns["local_layer"](size, pairs, words)
            need(len(stages) == 16 * field_d + 5, "retained source local-stage count")
            begin = len(self.raw_stages)
            self.raw_stages.extend(stages)
            self.layers.append(dict(begin=begin, end=len(self.raw_stages), pairs=pairs, kinds=kinds,
                                    permutation=permutation, route_layers=len(network)))
            self.words.append(words)
        self.reference_stages = []
        for i, (kind, value) in enumerate(self.raw_stages):
            if kind == "H":
                need(type(value) is int and 0 <= value < field_d
                     and i + 1 < len(self.raw_stages) and self.raw_stages[i + 1][0] == "D",
                     "Hadamard bit and immediate compensation stage")
                self.reference_stages.append(("H", value))
            else:
                need(kind == "D" and len(value) == size and all(z != 0 for z in value),
                     "complete nonzero coefficient table")
                multiplier = 2 if i and self.raw_stages[i - 1][0] == "H" else 1
                page = self.e.Vec(multiplier * z for z in value)
                need(all(z.norm2() <= 36 for z in page), "bounded native coefficient modulus")
                need(all(self.e.qheight(part) <= 8 * self.phase_bits + 64
                         for z in page for part in (z.re, z.im)), "rational coefficient setup height")
                self.reference_stages.append(("D", page))
        self.stages = [(kind, value if kind == "H" else self.e.Vec(self.e.rounded(z, self.bits) for z in value))
                       for kind, value in self.reference_stages]
        self.coefficient_width = 0
        for kind, page in self.stages:
            if kind == "D":
                for z in page:
                    for part in (z.re, z.im):
                        integer = part * (1 << self.bits)
                        need(integer.denominator == 1, "stored coefficient grid")
                        self.coefficient_width = max(self.coefficient_width, abs(integer.numerator).bit_length() + 1)
        need(self.coefficient_width <= self.bits + 5, "signed coefficient record width")
        need(len(self.stages) == self.stage_count
             and sum(kind == "D" for kind, _ in self.stages) == self.diagonal_count
             and sum(kind == "H" for kind, _ in self.stages) == self.h_count, "complete native counts")
        u = Q(1, 1 << self.bits)
        self.phase_error = 2 * d * Q(1, 1 << self.phase_bits) * self.radius
        self.coefficient_error = 4 * self.diagonal_count * K ** 2 * u * self.radius
        self.rounding_error = 4 * K * self.stage_count * size * u
        self.native_error = self.coefficient_error + self.rounding_error
        self.total_error = self.phase_error + self.native_error
        need(self.diagonal_count * K ** 2 * 2 * u < Q(1, 2)
             and self.total_error < 3 * Q(1, 1 << target) / 4, "complete FFT precision budget")
        self.amplitude = 4 * K * (self.radius + 1)
        self.integer_bits = self.e.ceil_log2(self.amplitude) + 2
        self.temporary_bits = 2 * self.bits + self.integer_bits + 6
        self.stage_seal = stage_hash(source, self.stages)
        self.reference_stage_seal = stage_hash(source, self.reference_stages)
        for (kind, exact), (_, stored) in zip(self.reference_stages, self.stages):
            if kind == "D":
                need(all((a - b).norm2() <= (2 * u) ** 2 for a, b in zip(exact, stored)),
                     "quantized diagonal operator error")

    def check_network(self, permutation, network):
        data = list(range(self.size))
        for layer in network:
            used, bits = set(), set()
            for i, j, flip in layer:
                need(type(flip) is bool and i not in used and j not in used
                     and 0 <= i < self.size and 0 <= j < self.size, "source switch ownership")
                mask = i ^ j
                need(mask > 0 and mask & (mask - 1) == 0, "one-bit switch")
                bits.add(mask)
                used.update((i, j))
                if flip:
                    data[i], data[j] = data[j], data[i]
            need(len(bits) == 1 and len(used) == self.size, "complete common-bit routing layer")
        need(all(data[permutation[i]] == i for i in range(self.size)), "source routing orientation")

    def execute(self, vector, capture=False):
        E, scale = self.e, 1 << self.bits
        state = E.Vec(vector)
        need(len(state) == self.size and norm2(state) <= self.radius ** 2,
             "declared FFT input dimension and Euclidean radius")
        need(all((part * (1 << self.incoming)).denominator == 1
                 for z in state for part in (z.re, z.im)), "declared incoming data grid")
        need(plan_hash(self.source, self.plan) == self.reference_hash
             and stage_hash(self.source, self.reference_stages) == self.reference_stage_seal
             and stage_hash(self.source, self.stages) == self.stage_seal,
             "unchanged stored FFT and prepared stages")
        borrowed = E.vector_hash(state)
        stats = dict(real_products=0, complex_roundings=0, h_pair_calls=0,
                     maximum_data_numerator_bits=0, maximum_temporary_numerator_bits=0,
                     maximum_temporary_fractional_bits=0)
        traces = []

        def observe(value):
            integer = value * (1 << (2 * self.bits))
            need(integer.denominator == 1, "exact native arithmetic temporary grid")
            width = abs(integer.numerator).bit_length() + 1
            stats["maximum_temporary_numerator_bits"] = max(stats["maximum_temporary_numerator_bits"], width)
            stats["maximum_temporary_fractional_bits"] = max(
                stats["maximum_temporary_fractional_bits"], value.denominator.bit_length() - 1)
            need(width <= self.temporary_bits
                 and abs(value) <= 16 * getattr(self, "temporary_amplitude", self.amplitude),
                 "native arithmetic temporary allowance")
            return value

        def store(value):
            result = E.rounded(value, self.bits)
            stats["complex_roundings"] += 1
            for part in (result.re, result.im):
                integer = part * scale
                need(integer.denominator == 1, "stored native common grid")
                width = abs(integer.numerator).bit_length() + 1
                stats["maximum_data_numerator_bits"] = max(stats["maximum_data_numerator_bits"], width)
                need(width <= self.bits + self.integer_bits, "signed data record width")
            return result

        need(norm2(state) <= self.amplitude ** 2, "initial magnitude envelope")
        for number, (kind, value) in enumerate(self.stages):
            if kind == "D":
                output = []
                for a, x in zip(value, state):
                    ar, ai = observe(a.re * x.re), observe(a.re * x.im)
                    br, bi = observe(a.im * x.re), observe(a.im * x.im)
                    stats["real_products"] += 4
                    output.append(store(E.C(observe(ar - bi), observe(ai + br))))
                state = E.Vec(output)
            else:
                step = 1 << value
                for i in range(self.size):
                    if not i & step:
                        a, b = state[i], state[i + step]
                        sr, si = observe(a.re + b.re), observe(a.im + b.im)
                        dr, di = observe(a.re - b.re), observe(a.im - b.im)
                        state[i] = store(E.C(observe(sr / 2), observe(si / 2)))
                        state[i + step] = store(E.C(observe(dr / 2), observe(di / 2)))
                        stats["h_pair_calls"] += 1
            need(norm2(state) <= self.amplitude ** 2, "actual native prefix magnitude")
            if capture:
                traces.append(dict(stage=number, kind=kind, output_sha256=E.vector_hash(state)))
        need(borrowed == E.vector_hash(E.Vec(vector)), "borrowed input preserved")
        need(stats["complex_roundings"] == self.stage_count * self.size
             and stats["h_pair_calls"] == self.h_count * self.size // 2,
             "all active and inactive rounding sites charged")
        return state, stats, traces

    def record(self):
        return dict(field_size=self.size, active_indices=list(self.indices), adjoint=self.adjoint,
                    radius=str(self.radius), target_bits=self.target, incoming_bits=self.incoming,
                    phase_bits=self.phase_bits, data_bits=self.bits,
                    observed_coefficient_bits=self.coefficient_width,
                    counts=dict(logical_layers=self.original_layers, primitive_stages=self.stage_count,
                                diagonal_stages=self.diagonal_count, hadamard_stages=self.h_count),
                    layers=self.layers, logical_plan_sha256=self.reference_hash,
                    reference_stages_sha256=self.reference_stage_seal, stored_stages_sha256=self.stage_seal,
                    source_original_ast_sha256=self.builder.original_ast,
                    source_adapted_ast_sha256=self.builder.adapted_ast,
                    tensor_ast_sha256=self.source.tensor_ast, phases=self.phases.record(),
                    budget=dict(prefix_bound=K, phase_error=str(self.phase_error),
                                coefficient_error=str(self.coefficient_error), rounding_error=str(self.rounding_error),
                                total_error=str(self.total_error), amplitude_bound=str(self.amplitude),
                                coefficient_bits=self.bits + 5, data_bits=self.bits + self.integer_bits,
                                temporary_bits=self.temporary_bits))
