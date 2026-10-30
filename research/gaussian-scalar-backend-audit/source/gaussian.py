"""Certified normalized Gaussian coefficients at the retained full-plan caller.

Jose Manuel (jmbarrancoml), with substantial OpenAI Codex assistance.
Apache-2.0. Interval arithmetic: Mason Hale; Tsec: Jeremy Kothe/IdeaOuter;
full circuit and q-LDU identities: Vlado Vojdanovski.
"""
import ast
import copy
from dataclasses import dataclass
from fractions import Fraction as Q
from hashlib import sha256
import sys
from types import ModuleType, SimpleNamespace

from exact import C, ceil_log2, need, vector_hash
from full import Full, Matrix, allocation

INTERVALS = "research/certified-gaussian-recovery/intervals.py"
EVALUATOR = "research/capped-fusion-t74-k554/outer/check_gaugefree.py"


def rational(value):
    need(type(value) in (int, Q), "exact Gaussian parameter")
    return Q(value)


def load_intervals(content):
    name = "_retained_gaussian_intervals_" + sha256(content).hexdigest()
    if name not in sys.modules:
        module = ModuleType(name)
        sys.modules[name] = module
        try:
            exec(compile(content, "<authenticated Mason interval arithmetic>", "exec",
                         optimize=0), module.__dict__)
        except BaseException:
            del sys.modules[name]
            raise
    return sys.modules[name]


@dataclass(frozen=True)
class PiMultiple:
    coefficient: Q

    def __neg__(self):
        return PiMultiple(-self.coefficient)

    def __add__(self, other):
        if isinstance(other, Grid):
            return other + self
        need(isinstance(other, PiMultiple), "one symbolic pi factor")
        return PiMultiple(self.coefficient + other.coefficient)

    def __mul__(self, other):
        if isinstance(other, Grid):
            return other * self
        return PiMultiple(self.coefficient * rational(other))

    __rmul__ = __mul__


class Grid:
    """Only exact scalar arithmetic and the two source broadcast axes."""
    def __init__(self, rows):
        self.rows = tuple(tuple(row) for row in rows)
        need(self.rows and self.rows[0]
             and all(len(row) == len(self.rows[0]) for row in self.rows), "grid shape")
        self.shape = len(self.rows), len(self.rows[0])

    def binary(self, other, operation):
        if not isinstance(other, Grid):
            return Grid([[operation(x, other) for x in row] for row in self.rows])
        m, n = max(self.shape[0], other.shape[0]), max(self.shape[1], other.shape[1])
        need(all(a in (1, b) for a, b in zip(self.shape, (m, n)))
             and all(a in (1, b) for a, b in zip(other.shape, (m, n))), "source broadcasting")
        return Grid([[operation(self.rows[i % self.shape[0]][j % self.shape[1]],
                                other.rows[i % other.shape[0]][j % other.shape[1]])
                      for j in range(n)] for i in range(m)])

    def __sub__(self, other):
        return self.binary(other, lambda a, b: a - b)

    def __add__(self, other):
        return self.binary(other, lambda a, b: a + b)

    def __mul__(self, other):
        return self.binary(other, lambda a, b: a * b)

    def __pow__(self, exponent):
        need(exponent == 2, "source square only")
        return Grid([[x * x for x in row] for row in self.rows])


class Range:
    def __init__(self, n):
        self.n = n

    def __getitem__(self, key):
        if key == (None, slice(None)):
            return Grid([range(self.n)])
        need(key == (slice(None), None), "source arange axes")
        return Grid([[i] for i in range(self.n)])


class GaussianMatrix(Matrix):
    def astype(self, tag):
        need(tag is complex, "retained complex tag without floating conversion")
        return GaussianMatrix(self)


@dataclass(frozen=True)
class Specification:
    n: int
    c: Q
    shift: Q
    radius: Q
    target: int
    incoming: int


class Gaussian:
    def __init__(self, raw, n, c, shift, radius, target, incoming=0, window=None):
        c, shift, radius = rational(c), rational(shift), rational(radius)
        need(type(n) is int and n > 0 and n & (n - 1) == 0, "dyadic Gaussian dimension")
        need(c > 0 and abs(shift) <= Q(1, 2) and radius >= 1, "Gaussian domain")
        need(type(target) is int and target >= 1 and type(incoming) is int and incoming >= 0,
             "Gaussian target and incoming grid")
        need(window is None or (type(window) is int and 0 <= window < n), "Gaussian cutoff")
        self.spec = Specification(n, c, shift, radius, target, incoming)
        self.raw, self.oracle = raw, load_intervals(raw[INTERVALS])
        a = -(-(2 / c).numerator // (2 / c).denominator)
        self.conditioning_bits = 2 * a + 36
        box = self.exponential(1 / (4 * c), self.conditioning_bits)
        lower = Q(box.lo, box.scale)
        need(lower > 0 and Q(box.hi - box.lo, box.scale) <= Q(1, 1 << (a + 2)),
             "positive conditioning enclosure with certified width")
        self.conditioning_box = box
        self.qbar = n / lower
        self.error_bits = target + ceil_log2(8 * (radius + 1) * self.qbar ** 2)
        self.epsilon = Q(1, 1 << self.error_bits)
        self.coefficient_error_bits = self.error_bits + ceil_log2(4 * (2 * n - 1))
        self.coefficient_bits = self.coefficient_error_bits + 1
        self.working_bits = 2 * self.coefficient_bits + 32
        if window is None:
            for window in range(n):
                tail = self.tail(window)
                if tail is not None and tail <= self.epsilon / 2:
                    break
        self.window, self.tail_bound = window, self.tail(window)
        need(self.tail_bound is not None and self.tail_bound <= self.epsilon / 2,
             "requested cutoff has a paid Gaussian tail")
        self.offsets, self.builder, self.root, self.plan = {}, None, None, None
        tree = ast.parse(raw[EVALUATOR])
        definitions = [copy.deepcopy(node) for node in tree.body
                       if isinstance(node, ast.FunctionDef) and node.name == "Tsec"]
        need(len(definitions) == 1, "one retained Tsec definition")
        function = ast.Module(body=definitions, type_ignores=[])
        pairs = []
        for parent in ast.walk(tree):
            body = getattr(parent, "body", None)
            if not isinstance(body, list):
                continue
            for left, right in zip(body, body[1:]):
                if (isinstance(left, ast.Assign) and isinstance(right, ast.Assign)
                        and ast.unparse(left) == "A = Tsec(n, g, s).astype(complex)"
                        and ast.unparse(right) == "plan = M.full_plan(list(range(n)), A)"):
                    pairs.append([copy.deepcopy(left), copy.deepcopy(right)])
        need(len(pairs) == 1, "one retained adjacent Tsec/full_plan call")
        self.callsite = ast.Module(body=pairs[0], type_ignores=[])
        self.source_ast = sha256(ast.dump(function).encode()).hexdigest()
        self.callsite_ast = sha256(ast.dump(self.callsite).encode()).hexdigest()
        self.namespace = dict(np=SimpleNamespace(arange=Range, exp=self.prepare_exponent_grid),
                              n=n, g=PiMultiple(c), s=shift,
                              M=SimpleNamespace(full_plan=self.compile_root))
        exec(compile(function, "<authenticated Tsec>", "exec", optimize=0), self.namespace)

    def exponential(self, factor, bits):
        factor = rational(factor)
        need(factor >= 0 and bits >= 16, "nonnegative exponent and working precision")
        if factor == 0:
            return self.oracle.Interval.rational(1, bits)
        result = self.oracle.exp_negative(self.oracle.pi_interval(bits) * factor)
        need(Q(result.hi - result.lo, result.scale) <= 512 * bits ** 2 * Q(1, 1 << bits),
             "retained exponential width allowance")
        return result

    def tail(self, window):
        if window == self.spec.n - 1:
            return Q(0)
        numerator = self.exponential(self.spec.c * window * (window + 1), self.working_bits)
        ratio = self.exponential(2 * self.spec.c * (window + 1), self.working_bits)
        denominator = 1 - Q(ratio.hi, ratio.scale)
        return 2 * Q(numerator.hi, numerator.scale) / denominator if denominator > 0 else None

    def coefficient(self, offset):
        if offset not in self.offsets:
            factor = self.spec.c * (offset * offset - 2 * self.spec.shift * offset)
            box = self.exponential(factor, self.working_bits)
            zero = self.oracle.Interval.rational(0, self.working_bits)
            numerators, error = self.oracle.inward_quantize((box, zero), self.coefficient_bits)
            value = Q(numerators[0], 1 << self.coefficient_bits)
            need(numerators[1] == 0 and 0 <= value <= 1
                 and error <= Q(1, 1 << self.coefficient_error_bits), "Gaussian coefficient receipt")
            need(factor != 0 or value == 1, "exact zero-exponent coefficient")
            self.offsets[offset] = dict(factor=factor, value=value, error=error,
                                       lower=Q(box.lo, box.scale), upper=Q(box.hi, box.scale))
        return self.offsets[offset]["value"]

    def prepare_exponent_grid(self, grid):
        n, c, shift = self.spec.n, self.spec.c, self.spec.shift
        need(isinstance(grid, Grid) and grid.shape == (n, n), "Tsec exponent shape")
        rows = []
        for i, row in enumerate(grid.rows):
            output = []
            for j, exponent in enumerate(row):
                u = j - i
                need(isinstance(exponent, PiMultiple)
                     and exponent.coefficient == -c * (u * u - 2 * shift * u),
                     "retained normalized Tsec orientation")
                output.append(self.coefficient(u) if abs(u) <= self.window else Q(0))
            rows.append(output)
        return GaussianMatrix(rows)

    def compile_root(self, indices, matrix):
        n = self.spec.n
        need(self.builder is None and indices == list(range(n)), "one exact Gaussian caller")
        need(set(self.offsets) == set(range(-self.window, self.window + 1)),
             "shared complete retained offset table")
        expected = GaussianMatrix([[self.offsets[j - i]["value"] if abs(j - i) <= self.window else 0
                                    for j in range(n)] for i in range(n)])
        need(matrix == expected, "same prepared root at full-plan boundary")
        self.root = Matrix(matrix)
        self.coefficient_error = sum((row["error"] for row in self.offsets.values()), Q(0))
        self.kernel_error = self.tail_bound + self.coefficient_error
        need(self.coefficient_error <= self.epsilon / 2 and self.kernel_error <= self.epsilon
             and self.epsilon * self.qbar <= Q(1, 2), "Gaussian perturbation admission")
        bound = allocation(n, n, 2 * self.qbar, self.spec.radius, self.spec.target + 1,
                           self.spec.incoming)
        self.builder = Full(bound, self.raw)
        self.plan = self.builder.plan(matrix, indices)
        self.forward_error = bound["total_error"] + self.spec.radius * self.kernel_error
        self.inverse_error = bound["total_error"] + 2 * self.qbar ** 2 * self.spec.radius * self.kernel_error
        need(max(self.forward_error, self.inverse_error) < Q(1, 1 << self.spec.target),
             "complete ideal Gaussian budget")
        self.root_hash = vector_hash([z for row in self.root for z in row])
        return self.plan

    def compile(self):
        need(self.builder is None, "Gaussian caller executes once")
        need(self.namespace["n"] == self.spec.n and self.namespace["g"] == PiMultiple(self.spec.c)
             and self.namespace["s"] == self.spec.shift, "same prepared caller parameters")
        exec(compile(self.callsite, "<authenticated Gaussian full-plan call>", "exec", optimize=0),
             self.namespace)
        need(self.namespace["plan"] is self.plan and self.namespace["A"] == self.root,
             "retained caller returns the certified root and plan")
        return self.plan

    def record(self):
        need(self.builder is not None and self.plan is not None, "compiled Gaussian receipt")
        return dict(n=self.spec.n, c=str(self.spec.c), shift=str(self.spec.shift),
                    radius=str(self.spec.radius), target_bits=self.spec.target,
                    incoming_bits=self.spec.incoming, window=self.window,
                    conditioning_bits=self.conditioning_bits,
                    conditioning_interval=[str(Q(self.conditioning_box.lo, self.conditioning_box.scale)),
                                           str(Q(self.conditioning_box.hi, self.conditioning_box.scale))],
                    ideal_inverse_bound=str(self.qbar), error_bits=self.error_bits,
                    coefficient_bits=self.coefficient_bits, working_bits=self.working_bits,
                    epsilon=str(self.epsilon), tail_bound=str(self.tail_bound),
                    coefficient_error=str(self.coefficient_error), kernel_error=str(self.kernel_error),
                    forward_error=str(self.forward_error), inverse_error=str(self.inverse_error),
                    root_sha256=self.root_hash, source_ast_sha256=self.source_ast,
                    callsite_ast_sha256=self.callsite_ast,
                    offsets=[dict(offset=u, **{key: str(value) for key, value in self.offsets[u].items()})
                             for u in sorted(self.offsets)])
