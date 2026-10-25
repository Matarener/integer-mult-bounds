"""Conditioned stored circuits on the retained fixed-H word and routing grammar.

Jose Manuel (jmbarrancoml), with substantial OpenAI Codex assistance.
Apache-2.0. Zero-safe words, routing and dense compiler: Vlado Vojdanovski.
Rational phases: Chafik Boukhalfa and the retained PR628 lineage.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import json
import sys
from types import MappingProxyType, ModuleType

from lowering import (DENSE_PREFIX, FFT, Sources, canonical, need, norm2,
                      plan_hash, stage_hash)


def budget_hash(source, budget):
    return sha256(canonical([(key, type(value).__name__, source.e.vector_hash([source.e.C(value)]))
                             for key, value in sorted(budget.items())])).hexdigest()


def reported(source, value, allowance=None):
    need(type(value) in (int, Q), "exact reported bound")
    bits = max(160, source.e.ceil_log2(1 / allowance) + 16) if allowance else 160
    result = source.e.upper(value, bits)
    if allowance is not None:
        need(0 <= value <= allowance, "proved reporting allowance")
        result = min(result, allowance)
    return str(result)


class DenseSources(Sources):
    def __init__(self, overrides=None):
        super().__init__(overrides, include_dense=True)
        provenance = json.loads(self.raw[DENSE_PREFIX + "PROVENANCE.json"])
        for row in provenance["files"]:
            content = self.raw[row["retained_path"]]
            need(sha256(content).hexdigest() == row["sha256"], "unchanged full-circuit archive")
            self.raw[row["original_path"]] = content
        names = ("exact", "engine", "triangular", "generator", "full")
        previous = {name: sys.modules.get(name) for name in names}
        sys.modules["exact"], sys.modules["engine"] = self.e, self.engine
        loaded = {}
        try:
            for name in names[2:]:
                module = ModuleType("_authenticated_dense_" + name)
                sys.modules[name] = module
                exec(compile(self.raw[DENSE_PREFIX + name + ".py"],
                             "<authenticated PR4205 " + name + ">", "exec", optimize=0), module.__dict__)
                loaded[name] = module
        finally:
            for name, old in previous.items():
                if old is None:
                    sys.modules.pop(name, None)
                else:
                    sys.modules[name] = old
        self.full = loaded["full"]
        self.raw = MappingProxyType(dict(self.raw))


class NativeProgram(FFT):
    """A prefix-bound compiler; callers must establish the declared logical bound."""
    CONTRACT_FIELDS = ("size", "radius", "target", "incoming", "prefix", "endpoint", "upstream_error",
                       "logical_layers", "stage_count", "diagonal_count", "h_count", "gamma_bits", "gamma",
                       "compiled_bound", "bits", "coefficient_bits", "coefficient_error", "rounding_error",
                       "native_error", "total_error", "amplitude", "temporary_amplitude", "integer_bits",
                       "temporary_bits")

    def __init__(self, source, size, plan, prefix, endpoint, radius, target, incoming=0, *,
                 upstream_error=0, context=None, data_bits=None):
        need(type(size) is int and size > 0 and size & (size - 1) == 0, "dyadic native field")
        need(all(type(x) in (int, Q) and x >= 1 for x in (prefix, endpoint, radius)),
             "exact positive circuit envelopes")
        need(type(target) is int and target >= 1 and type(incoming) is int and incoming >= 0,
             "native target and incoming grid")
        need(type(upstream_error) in (int, Q) and upstream_error >= 0, "upstream operator defect")
        self.source, self.e, self.context = source, source.e, context
        self.size, self.radius, self.target, self.incoming = size, Q(radius), target, incoming
        self.prefix, self.endpoint, self.upstream_error = Q(prefix), Q(endpoint), Q(upstream_error)
        self.plan = [list(layer) for layer in plan]
        self.reference_hash = plan_hash(source, self.plan)
        self.logical_layers = len(self.plan)
        m = size.bit_length() - 1
        self.stage_count = self.logical_layers * (16 * m + 5) if m else self.logical_layers
        self.diagonal_count = self.logical_layers * (8 * m + 3) if m else self.logical_layers
        self.h_count = self.logical_layers * (8 * m + 2) if m else 0
        self.gamma_bits = max(0, self.e.ceil_log2(self.prefix ** 2))
        self.gamma = 1 << self.gamma_bits
        self.compiled_bound = (1 << 14) * self.gamma * self.prefix
        c, e0, r = self.compiled_bound, self.endpoint, self.radius
        minimum = max(incoming, target + self.e.ceil_log2(16 * e0 * self.diagonal_count * c ** 2 * (r + 1)),
                      target + self.e.ceil_log2(16 * e0 * c * self.stage_count * size)) if self.logical_layers else max(incoming, 1)
        self.bits = minimum if data_bits is None else data_bits
        need(type(self.bits) is int and self.bits >= minimum, "funded nonunitary native grid")
        self.raw_stages, self.layers = [], []
        self.kinds = Counter()
        self.input_height = 1
        self.word_count = 0
        for layer in self.plan:
            used, pairs, words, singles, kinds = set(), [], [], {}, []
            for ids, gate in layer:
                need(len(ids) == len(gate) in (1, 2) and all(len(row) == len(ids) for row in gate),
                     "one- or two-wire source gate")
                need(len(set(ids)) == len(ids) and not used.intersection(ids)
                     and all(type(i) is int and 0 <= i < size for i in ids), "disjoint oriented source ownership")
                used.update(ids)
                self.input_height = max(self.input_height, *(self.e.qheight(p)
                    for row in gate for z in row for p in (z.re, z.im)))
                if len(ids) == 1:
                    self.scalar(gate[0][0])
                    singles[ids[0]] = gate[0][0]
                else:
                    kind, word = self.gate_word(gate)
                    pairs.append(tuple(ids))
                    words.append(word)
                    kinds.append(kind)
            if size == 1:
                value = singles.get(0, self.e.C(1))
                self.raw_stages.append(("D", self.e.Vec([value])))
                self.layers.append(dict(begin=len(self.raw_stages) - 1, end=len(self.raw_stages),
                                        pairs=[], kinds=["scalar" if singles else "idle"]))
                self.kinds.update(self.layers[-1]["kinds"])
                continue
            paired = {i for pair in pairs for i in pair}
            free = [i for i in range(size) if i not in paired]
            for j in range(0, len(free), 2):
                pair = tuple(free[j:j + 2])
                values = tuple(singles.get(i, self.e.C(1)) for i in pair)
                for value in values:
                    self.scalar(value)
                word = source.ns["gateword"]("diag", values)
                need(source.word_endpoint(word) == self.e.Mat([[values[0], 0], [0, values[1]]]),
                     "paired scalar endpoint")
                pairs.append(pair)
                words.append(word)
                kinds.append("scalar-pair" if any(i in singles for i in pair) else "idle")
            need(len(pairs) == len(words) == size // 2, "complete mixed matching")
            permutation = source.ns["matching_permutation"](size, pairs)
            self.check_network(permutation, source.ns["benes"](permutation))
            stages = source.ns["local_layer"](size, pairs, words)
            need(len(stages) == 16 * m + 5, "source matching-layer stage count")
            begin = len(self.raw_stages)
            self.raw_stages.extend(stages)
            self.layers.append(dict(begin=begin, end=len(self.raw_stages), pairs=pairs,
                                    kinds=kinds, permutation=permutation))
            self.kinds.update(kinds)
            self.word_count += len(words)
        self.reference_stages = []
        self.setup_height = 1
        for j, (kind, value) in enumerate(self.raw_stages):
            if kind == "H":
                need(type(value) is int and 0 <= value < m
                     and j + 1 < len(self.raw_stages) and self.raw_stages[j + 1][0] == "D",
                     "native bit and following compensation")
                self.reference_stages.append((kind, value))
            else:
                need(kind == "D" and len(value) == size and all(z != 0 for z in value),
                     "complete nonzero reference page")
                scale = 2 if j and self.raw_stages[j - 1][0] == "H" else 1
                page = self.e.Vec(scale * z for z in value)
                need(all(z.norm2() <= (6 * self.gamma) ** 2
                         and (1 / z).norm2() <= (200 * self.gamma) ** 2 for z in page),
                     "native direct/reciprocal coefficient envelope")
                self.setup_height = max(self.setup_height, *(self.e.qheight(p)
                    for z in page for p in (z.re, z.im)))
                self.reference_stages.append((kind, page))
        self.setup_allowance = 32 * (self.input_height + self.gamma_bits + 8)
        need(self.setup_height <= self.setup_allowance, "reduced rational setup height")
        self.stages = [(kind, value if kind == "H" else self.e.Vec(self.e.rounded(z, self.bits) for z in value))
                       for kind, value in self.reference_stages]
        need(len(self.stages) == self.stage_count
             and sum(kind == "D" for kind, _ in self.stages) == self.diagonal_count
             and sum(kind == "H" for kind, _ in self.stages) == self.h_count, "full native stage counts")
        self.coefficient_width = 0
        u = Q(1, 1 << self.bits)
        for (kind, exact), (_, page) in zip(self.reference_stages, self.stages):
            if kind == "D":
                for a, z in zip(exact, page):
                    need((a - z).norm2() <= (2 * u) ** 2, "native diagonal approximation")
                    for part in (z.re, z.im):
                        integer = part * (1 << self.bits)
                        need(integer.denominator == 1, "native coefficient grid")
                        self.coefficient_width = max(self.coefficient_width, abs(integer.numerator).bit_length() + 1)
        self.coefficient_bits = self.bits + self.gamma_bits + 5
        need(self.coefficient_width <= self.coefficient_bits, "signed nonunitary coefficient width")
        self.coefficient_error = 4 * e0 * self.diagonal_count * c ** 2 * u * r
        self.rounding_error = 4 * e0 * c * self.stage_count * size * u
        self.native_error = self.coefficient_error + self.rounding_error
        self.total_error = self.upstream_error * r + self.native_error
        need(self.diagonal_count * c ** 2 * 2 * u < Q(1, 2)
             and self.native_error < Q(1, 1 << (target + 1))
             and self.total_error <= Q(1, 1 << target), "complete conditioned target budget")
        self.amplitude = 4 * c * (r + 1)
        self.temporary_amplitude = self.gamma * self.amplitude
        self.integer_bits = self.e.ceil_log2(self.amplitude) + 2
        self.temporary_bits = 2 * self.bits + self.integer_bits + self.gamma_bits + 6
        self.stage_seal = stage_hash(source, self.stages)
        self.reference_stage_seal = stage_hash(source, self.reference_stages)
        self.contract_seal = self.contract_hash()

    def contract_hash(self):
        return budget_hash(self.source, {name: getattr(self, name) for name in self.CONTRACT_FIELDS})

    def scalar(self, value):
        need(value != 0 and value.norm2() <= self.gamma ** 2
             and (1 / value).norm2() <= self.gamma ** 2, "logical scalar and reciprocal admission")

    def gate_word(self, gate):
        E, source = self.e, self.source
        if gate[0][0] == gate[1][1] == 1 and gate[1][0] == 0:
            kind, value = "upper", gate[0][1]
            need(value.norm2() <= self.gamma ** 2, "upper shear coefficient admission")
            word = source.ns["gateword"](kind, value, self.gamma)
        elif gate[0][0] == gate[1][1] == 1 and gate[0][1] == 0:
            kind, value = "lower", gate[1][0]
            need(value.norm2() <= self.gamma ** 2, "lower shear coefficient admission")
            word = source.ns["gateword"](kind, value, self.gamma)
        elif gate[0][1] == gate[1][0] == 0:
            kind = "diagonal"
            values = gate[0][0], gate[1][1]
            for value in values:
                self.scalar(value)
            word = source.ns["gateword"]("diag", values)
        else:
            kind, word = source.gate_word(gate)
        need(len(word) == 13 and sum(op == "H" for op in word) == 6
             and source.word_endpoint(word) == E.Mat(gate), "actual six-H source gate endpoint")
        return kind, word

    def execute(self, vector, capture=False):
        need(self.contract_hash() == self.contract_seal, "unchanged native precision and magnitude contract")
        if self.context is not None:
            self.context.validate()
        return super().execute(vector, capture)

    def record(self):
        need(self.contract_hash() == self.contract_seal, "unchanged recorded native contract")
        if self.context is not None:
            self.context.validate()
        exact_values = dict(prefix=self.prefix, endpoint=self.endpoint, compiled=self.compiled_bound,
                            radius=self.radius, upstream=self.upstream_error,
                            coefficient=self.coefficient_error, rounding=self.rounding_error,
                            native=self.native_error, total=self.total_error, amplitude=self.amplitude)
        tau = Q(1, 1 << self.target)
        return dict(size=self.size, logical_layers=self.logical_layers, word_count=self.word_count,
                    kinds=dict(sorted(self.kinds.items())), layer_mapping_sha256=sha256(canonical(self.layers)).hexdigest(),
                    logical_plan_sha256=self.reference_hash, reference_stages_sha256=self.reference_stage_seal,
                    stored_stages_sha256=self.stage_seal, tensor_ast_sha256=self.source.tensor_ast,
                    counts=dict(primitive_stages=self.stage_count, diagonal_stages=self.diagonal_count,
                                hadamard_stages=self.h_count),
                    budget=dict(prefix_upper=reported(self.source, self.prefix),
                                endpoint_upper=reported(self.source, self.endpoint),
                                gamma_bits=self.gamma_bits, compiled_prefix_upper=reported(self.source, self.compiled_bound),
                                radius=str(self.radius), target_bits=self.target, incoming_bits=self.incoming,
                                data_grid_bits=self.bits, coefficient_bits=self.coefficient_bits,
                                data_bits=self.bits + self.integer_bits, temporary_bits=self.temporary_bits,
                                coefficient_error_upper=reported(self.source, self.coefficient_error, tau / 2),
                                rounding_error_upper=reported(self.source, self.rounding_error, tau / 2),
                                native_error_upper=reported(self.source, self.native_error, tau / 2),
                                total_error_upper=reported(self.source, self.total_error, tau),
                                amplitude_upper=reported(self.source, self.amplitude),
                                exact_budget_sha256=budget_hash(self.source, exact_values)),
                    setup=dict(input_component_height=self.input_height, reduced_coefficient_height=self.setup_height,
                               reduced_height_allowance=self.setup_allowance,
                               observed_stored_coefficient_bits=self.coefficient_width))


class FullRoot:
    def __init__(self, source, matrix, radius, target, indices=None):
        self.source, self.e = source, source.e
        self.matrix = self.e.Mat(matrix)
        self.matrix_seal = source.matrix_hash(self.matrix)
        self.lam, self.q, self.leading = source.full.admission(self.matrix)
        budget = source.full.allocation(len(matrix), self.lam, self.q, radius, target, 0)
        self.builder = source.full.Full(budget, source.raw)
        self.plan = self.builder.plan(self.matrix, indices)
        self.inverse_plan = self.builder.inverse(self.plan)
        self.bound = dict(self.builder.bound)
        self.budget_seal = budget_hash(source, self.bound)
        self.plan_seal, self.inverse_seal = plan_hash(source, self.plan), plan_hash(source, self.inverse_plan)
        self.radius, self.target = Q(radius), target
        self.indices = list(range(len(matrix))) if indices is None else list(indices)
        self.request_seal = self.request_state()
        need(source.matrix_hash(self.matrix) == self.matrix_seal, "borrowed exact root preserved during preparation")

    def request_state(self):
        return (self.lam, self.q, self.radius, self.target, tuple(self.indices), tuple(self.leading))

    def validate(self):
        need(self.request_state() == self.request_seal
             and self.lam == self.bound["lam"] and self.q == self.bound["inverse_bound"]
             and self.radius == self.bound["radius"] and self.target == self.bound["target_bits"]
             and self.source.matrix_hash(self.matrix) == self.matrix_seal
             and budget_hash(self.source, self.builder.bound) == self.budget_seal
             and budget_hash(self.source, self.bound) == self.budget_seal
             and plan_hash(self.source, self.plan) == self.plan_seal
             and plan_hash(self.source, self.inverse_plan) == self.inverse_seal,
             "same admitted root, stored plan and full prefix contract")

    def lower(self, inverse=False, incoming=0):
        need(type(inverse) is bool, "declared full direction")
        self.validate()
        defect = self.bound["coefficient_error"]
        endpoint = (self.q if inverse else self.lam) + defect
        need(endpoint <= self.bound["execution_bound"], "endpoint bound fits the retained full envelope")
        return NativeProgram(self.source, len(self.matrix), self.inverse_plan if inverse else self.plan,
                             self.bound["execution_bound"], endpoint, self.radius, self.target, incoming,
                             upstream_error=defect, context=self)

    def record(self):
        self.validate()
        return dict(n=len(self.matrix), indices=self.indices, root_sha256=self.matrix_seal,
                    full_source_ast_sha256=self.builder.source_ast,
                    full_budget_sha256=self.budget_seal,
                    lambda_upper=reported(self.source, self.lam), inverse_upper=reported(self.source, self.q),
                    leading=[dict(size=n, inverse_upper=reported(self.source, value)) for n, value in self.leading],
                    stored_prefix_upper=reported(self.source, self.bound["execution_bound"]),
                    upstream_operator_error_upper=reported(self.source, self.bound["coefficient_error"]),
                    target_bits=self.target, radius=str(self.radius),
                    forward_plan_sha256=self.plan_seal, inverse_plan_sha256=self.inverse_seal)
