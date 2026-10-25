"""Shared-reference finite-core Gaussian words and rounded boundary arithmetic.

Jose Manuel (jmbarrancoml), with substantial OpenAI Codex assistance.
Apache-2.0. Carve, factor order and block/Strassen program: Vlado's retained
lineage. Rounded boundary adapter: PR4186. Gaussian credits remain in README.
"""
import ast
import copy
from fractions import Fraction as Q
import hashlib
import json
from types import SimpleNamespace

from exact import C, Mat, Vec, apply, ceil_log2, need, qheight, upper, vector_hash
from gaussian import Gaussian, rational
from gaussian_reference import Exponentials, Reference, ceiling_sqrt
from raw_gaussian import RawGaussian

ADAPTER = "research/rational-unitary-fft/vendor/boundary_adapter.py"
PROVENANCE = "research/rational-unitary-fft/vendor/BOUNDARY-PROVENANCE.json"
SUBJECT = "research/capped-phase-fusion/evidence/radical_reduction_ultra/check_constructions.py"
CARVE = "research/capped-phase-fusion/evidence/gaussian_fast_ultra/check_capped_gauges.py"
WORD = "research/capped-phase-fusion/evidence/phase_layout_audit_ultra/check_union.py"


def matrix_hash(matrix):
    shape = (len(matrix), len(matrix[0]) if matrix else 0)
    values = (C.wrap(x) for row in matrix for x in row)
    return hashlib.sha256((str(shape) + vector_hash(values)).encode()).hexdigest()


def plan_hash(plan):
    digest = hashlib.sha256()
    for layer in plan:
        digest.update(str(len(layer)).encode() + b":")
        for wires, gate in layer:
            digest.update((str(tuple(wires)) + matrix_hash(gate)).encode())
    return digest.hexdigest()


def raw_core_record(program):
    """Bind exact child values without decimal-expanding checker fractions."""
    errors = [program.reference_error, program.diagonal_error, program.middle_error,
              program.raw_error, program.forward_error, program.inverse_error]
    bits = max(160, program.target + 32)
    return dict(kind=program.kind, start=program.start, n=program.n,
                radius=str(program.radius), target_bits=program.target,
                incoming_bits=program.incoming, data_bits=program.data_bits,
                reference_matrix_sha256=program.reference_hash,
                normalized_root_sha256=program.child.root_hash,
                source_ast_sha256=program.child.source_ast,
                callsite_ast_sha256=program.child.callsite_ast,
                plan_sha256=plan_hash(program.plan),
                inverse_plan_sha256=plan_hash(program.inverse_plan),
                exact_errors_sha256=vector_hash(C(x) for x in errors),
                error_upper=dict(zip(("reference", "diagonal", "middle", "raw",
                                      "forward", "inverse"),
                                     (str(upper(x, bits)) for x in errors))),
                budget={key: str(upper(value, bits)) if isinstance(value, Q) else value
                        for key, value in program.bound.items()})


def max_complex(matrix):
    return max((abs(x.re) + abs(x.im) for row in matrix for x in row), default=Q(0))


def real(matrix):
    need(all(x.im == 0 for row in matrix for x in row), "real reference pages")
    return [[x.re for x in row] for row in matrix]


def row_norm(matrix):
    return max((sum(abs(x) for x in row) for row in matrix), default=Q(0))


def row_gap(matrix):
    return min(abs(row[i]) - sum(abs(x) for j, x in enumerate(row) if i != j)
               for i, row in enumerate(matrix))


def bandwidth(matrix):
    return max((abs(i - j) for i, row in enumerate(matrix) for j, x in enumerate(row) if x), default=0)


def product(a, b):
    """Exact sparse setup/checker product, outside online arithmetic counts."""
    if not a:
        return []
    columns = len(b[0]) if b else 0
    nonzero = [[(j, x) for j, x in enumerate(row) if x] for row in b]
    result = [[Q(0) for _ in range(columns)] for _ in a]
    for i, row in enumerate(a):
        for k, x in enumerate(row):
            if x:
                for j, y in nonzero[k]:
                    result[i][j] += x * y
    return result


def block(matrix, rows, columns):
    return [[matrix[i][j] for j in columns] for i in rows]


def band_lu(matrix, band):
    """Exact natural-order LU; skip entries that ordinary band geometry makes zero."""
    n = len(matrix)
    need(bandwidth(matrix) <= band, "ordinary reference factorization band")
    lower = [[Q(i == j) for j in range(n)] for i in range(n)]
    upper = [[Q(0) for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(i, min(n, i + band + 1)):
            upper[i][j] = matrix[i][j] - sum(lower[i][k] * upper[k][j]
                                            for k in range(max(0, i - band), i))
        need(upper[i][i] > 0, "positive no-pivot narrow diagonal")
        for j in range(i + 1, min(n, i + band + 1)):
            lower[j][i] = (matrix[j][i] - sum(lower[j][k] * upper[k][i]
                            for k in range(max(0, j - band), i))) / upper[i][i]
    need(product(lower, upper) == matrix, "exact band LU identity")
    return lower, upper


def load_boundary(raw):
    provenance = json.loads(raw[PROVENANCE])
    need(provenance["retained_path"] == ADAPTER
         and hashlib.sha256(raw[ADAPTER]).hexdigest() == provenance["sha256"],
         "unchanged boundary adapter provenance")
    names = {"need", "sha", "encoded", "matrix_digest", "maximum", "norm", "identity",
             "multiply", "subtract", "solve", "lu", "reverse_both", "rounded", "on_grid",
             "RoundedSubject", "pass_constants", "check_pass"}
    tree = ast.parse(raw[ADAPTER])
    tree.body = [copy.deepcopy(node) for node in tree.body
                 if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in names]
    need({node.name for node in tree.body} == names, "complete boundary definition closure")
    seal = hashlib.sha256(ast.dump(tree).encode()).hexdigest()
    namespace = dict(Q=Q, hashlib=hashlib, json=json, SUBJECT=SUBJECT)
    exec(compile(tree, "<authenticated PR4186 boundary adapter>", "exec", optimize=0), namespace)
    # This diagnostic hashes exact values without Python's decimal-string limit.
    # Arithmetic, pages, rounding sites and source counters remain unchanged.
    namespace["matrix_digest"] = matrix_hash
    namespace["source_ast_sha256"] = seal
    return SimpleNamespace(**namespace)


def geometry_bounds(raw, source_size, excess, alpha, cap):
    theta, rho = Q(excess, source_size), Q(source_size + excess, source_size)
    lam, radius = 1 / rho, Q(cap - 1, 2)
    rate = lam * theta / alpha ** 2
    exponent = max(alpha ** 2 * theta * radius ** 2,
                   1 / (4 * alpha ** 2 * rho ** 2) + rate * (lam * radius ** 2 + radius / rho),
                   rate * (radius ** 2 + 2 * radius / rho))
    exp = Exponentials(raw)
    decay = exp.relative(exponent, exponent, 24)
    gauge = alpha / decay["value"]
    middle = Gaussian(raw, cap, lam / alpha ** 2, 0, 1, 1).qbar
    return gauge, middle, gauge ** 2 * middle


def allocated_reference(raw, source_size, excess, alpha, cap, y0, target):
    """Fund one reference for either finite-core direction before choosing windows."""
    need(all(type(x) is int for x in (source_size, excess, alpha, cap, target))
         and 0 < excess < source_size and alpha >= 1 and cap > 0
         and cap & (cap - 1) == 0 and 2 * cap <= source_size and target >= 1,
         "core reference geometry and target")
    y0 = rational(y0)
    need(y0 >= 1, "core reference input envelope")
    theta = Q(excess, source_size)
    bits = max(96, 2 * max(0, ceil_log2(1 / theta)) + 64)
    exp = Exponentials(raw)
    near, far = exp.decay_box(2 * alpha ** 2 * theta, bits), exp.decay_box(2 * alpha ** 2, bits)
    d0 = 1 - Q(near.hi, near.scale) - 5 * Q(far.hi, far.scale)
    need(d0 > 0, "certified ideal narrow gap before reference allocation")
    gauge, middle, inverse = geometry_bounds(raw, source_size, excess, alpha, cap)
    k = max(Q(3), 2 / d0, 4 + 32 * inverse)
    ystar = 6 * k ** 5 * y0
    radius = ceiling_sqrt(cap) * ystar
    dense_target = target + ceil_log2(20 * k ** 4)
    reference_target = max(dense_target, ceil_log2(2 / d0), ceil_log2(2 * inverse), 1)
    reference = Reference.for_cap(raw, source_size, excess, alpha, cap, radius, reference_target)
    need(reference.errors["narrow"] <= d0 / 2
         and reference.narrow_gap >= d0 / 2
         and reference.errors["broad"] * inverse <= Q(1, 2),
         "funded core gap and broad inverse perturbation")
    return reference, dict(ideal_gap_lower=str(d0), scalar_bits=bits, gauge_bound=str(gauge),
                           normalized_bound=str(middle), raw_inverse_bound=str(inverse),
                           factor_bound=str(k), stage_radius=str(ystar), dense_radius=str(radius),
                           dense_target_bits=dense_target, reference_target_bits=reference_target)


class Boundary:
    def __init__(self, raw, adapter, matrix, width, p, bits, ystar, gap):
        self.raw, self.adapter, self.matrix = raw, adapter, matrix
        self.width, self.p, self.bits, self.ystar, self.gap = width, p, bits, ystar, gap
        n, band = len(matrix), bandwidth(matrix)
        need(row_norm(matrix) <= 2 and row_gap(matrix) >= gap >= Q(1, 16 * p ** 2)
             and band <= 2 * p and max(1, band) <= width <= 4 * p, "actual boundary admission")
        self.lower, upper = band_lu(matrix, band)
        self.upper_reverse = adapter.reverse_both(upper)
        need(row_norm(self.lower) <= 65 * p ** 3 and row_norm(upper) <= 2, "reference factor norms")
        self.exact_inverses, self.pages = {}, []
        self.factor_pages, self.diagonal_pages, self.inverse_pages = {}, {}, {}
        prototype = adapter.RoundedSubject(raw[SUBJECT], bits, width, ystar, Q(32 * p ** 2),
                                            Q(65 * p ** 3))
        self.source_inverse = prototype.exact_inverse
        for label, factor, inverse_bound in (
                ("lower", self.lower, Q(32 * p ** 2)),
                ("upper", self.upper_reverse, Q(1040 * p ** 5))):
            self.factor_pages[label] = adapter.rounded(factor, bits)
            need(row_norm(adapter.subtract(self.factor_pages[label], factor))
                 <= width * Q(2, 1 << bits), "prepared factor-page error")
            self.diagonal_pages[label], self.inverse_pages[label] = [], []
            for start in range(0, n, width):
                page = [[factor[start + i][start + j] if start + i < n and start + j < n
                         else Q(i == j) for j in range(width)] for i in range(width)]
                key = tuple(map(tuple, page))
                if key not in self.exact_inverses:
                    inverse = self.source_inverse(page)
                    need(product(page, inverse) == adapter.identity(width), "exact consecutive inverse page")
                    self.exact_inverses[key] = tuple(map(tuple, inverse))
                exact = self.exact_inverses[key]
                need(row_norm(exact) <= inverse_bound, "reference inverse-page norm")
                rounded = adapter.rounded(exact, bits)
                need(row_norm(adapter.subtract(rounded, exact)) <= width * Q(2, 1 << bits),
                     "prepared inverse-page error")
                self.diagonal_pages[label].append(adapter.rounded(page, bits))
                self.inverse_pages[label].append(rounded)
                self.pages.append(dict(factor=label, start=start, input_sha256=matrix_hash(page),
                                       exact_inverse_sha256=matrix_hash(exact),
                                       rounded_inverse_sha256=matrix_hash(rounded)))
        self.temporary_bound = (1 << 46) * p ** 16 * ystar
        self.error_bound = (1 << 40) * p ** 16 * Q(2, 1 << bits) * ystar
        self.source_ast = adapter.source_ast_sha256

    def pass_run(self, rhs, upper=False):
        p, bits, width = self.p, self.bits, self.width
        a, sub, q = (Q(2), Q(2), Q(1040 * p ** 5)) if upper else (
            Q(65 * p ** 3), Q(65 * p ** 3), Q(32 * p ** 2))
        y = 128 * p ** 2 * self.ystar if upper else self.ystar
        eta = Q(2, 1 << bits)
        c0, c1, _ = self.adapter.pass_constants(a, sub, q, width)
        need(width * eta <= 1 and eta * c0 <= 1 and q * eta * c1 <= Q(1, 2),
             "boundary residual absorption")
        worker = self.adapter.RoundedSubject(self.raw[SUBJECT], bits, width, y, q, sub)
        label, cursor = ("upper" if upper else "lower"), [0]
        def prepared_inverse(diagonal):
            index = cursor[0]
            need(index < len(self.inverse_pages[label])
                 and diagonal == self.diagonal_pages[label][index], "sequential prepared diagonal page")
            page = [list(row) for row in self.inverse_pages[label][index]]
            cursor[0] += 1
            worker.inverse_pages += 1
            worker.inverse_ids.add(id(page))
            worker.observe(page)
            return page
        worker.ns["inverse"] = prepared_inverse
        answer = worker.run(self.factor_pages[label], rhs)
        need(cursor[0] == len(self.inverse_pages[label]), "complete prepared inverse-page stream")
        magnitude = self.adapter.maximum(answer)
        need(magnitude <= 4 * q * y and worker.max_value <= self.temporary_bound,
             "boundary pass magnitude and scratch")
        return answer, dict(root_products=worker.products, scalar_products=worker.ns["OPS"],
                            inverse_pages=worker.inverse_pages, rhs_roundings=worker.updates,
                            fractional_bits=worker.max_fractional,
                            maximum_upper=str(upper_bound(magnitude)),
                            temporary_maximum_upper=str(upper_bound(worker.max_value)),
                            batches=(len(rhs[0]) + width - 1) // width)

    def run(self, rhs):
        columns = len(rhs[0])
        packed = [[x.re for x in row] + [x.im for x in row] for row in rhs]
        forward, lower = self.pass_run(packed)
        reversed_answer, upper = self.pass_run(list(reversed(forward)), upper=True)
        answer = list(reversed(reversed_answer))
        result = Mat([[C(row[j], row[j + columns]) for j in range(columns)] for row in answer])
        need(max_complex(result) <= (1 << 20) * self.p ** 7 * self.ystar,
             "complex boundary output envelope")
        return result, dict(lower=lower, upper=upper, real_rhs_columns=2 * columns)

    def baseline(self, rhs):
        """Verifier-only comparison with the unchanged reference-factor adapter."""
        columns = len(rhs[0])
        packed = [[x.re for x in row] + [x.im for x in row] for row in rhs]
        for matrix, is_upper in ((self.lower, False), (self.upper_reverse, True)):
            p = self.p
            q, sub = (Q(1040 * p ** 5), Q(2)) if is_upper else (Q(32 * p ** 2), Q(65 * p ** 3))
            y = 128 * p ** 2 * self.ystar if is_upper else self.ystar
            worker = self.adapter.RoundedSubject(self.raw[SUBJECT], self.bits, self.width, y, q, sub)
            worker.exact_inverse = lambda page: self.exact_inverses[tuple(map(tuple, page))]
            if is_upper:
                packed = list(reversed(packed))
            packed = worker.run(matrix, packed)
        return Mat([[C(row[j], row[j + columns]) for j in range(columns)]
                    for row in reversed(packed)])

    def record(self):
        return dict(rows=len(self.matrix), band=bandwidth(self.matrix), width=self.width,
                    p=self.p, bits=self.bits, gap_lower=str(self.gap),
                    error_bound=str(self.error_bound), temporary_bound=str(self.temporary_bound),
                    source_ast_sha256=self.source_ast, lower_sha256=matrix_hash(self.lower),
                    upper_reverse_sha256=matrix_hash(self.upper_reverse),
                    unique_exact_inverse_pages=len(self.exact_inverses), pages=self.pages)


def upper_bound(value):
    return upper(value)


class Core:
    def __init__(self, raw, reference, kind, first, last, cap, y0, target, incoming=0,
                 physical_band=None):
        need(kind in ("narrow", "broad") and all(type(x) is int for x in
             (first, last, cap, target, incoming)) and cap > 0 and cap & (cap - 1) == 0
             and target >= 1 and incoming >= 0, "core kind, cap and precision")
        y0 = rational(y0)
        need(y0 >= 1 and 2 * cap <= reference.spec.source_size, "core radius and source cap")
        minimal = (2 * reference.spec.source_halfwidth + 2 if kind == "narrow"
                   else reference.spec.target_halfwidth)
        width = max(minimal, 1) if physical_band is None else physical_band
        need(type(width) is int and width >= max(1, minimal), "physical core band covers the reference")
        need(0 <= first < last <= reference.target_size
             and reference.target_size - (last - first) >= width, "ordinary core with complementary gap")
        self.raw, self.reference, self.kind = raw, reference, kind
        self.first, self.last, self.cap, self.width = first, last, cap, width
        self.y0, self.target, self.incoming = y0, target, incoming
        self.n = last - first
        self.coordinates = tuple(range(first, last))
        self.adapter = load_boundary(raw)
        self.carve, self.carve_ast = self.load_carve()
        self.pieces, self.cells = self.partition()
        self.interior = sorted(i for cell in self.cells for i in cell["indices"])
        interior_set = set(self.interior)
        self.boundary = [i for i in range(self.n) if i not in interior_set]
        need(self.boundary, "nonempty retained core boundary")
        self.gauge_bound, self.middle_bound, self.raw_inverse_bound = geometry_bounds(
            raw, reference.spec.source_size, reference.spec.excess, reference.spec.alpha, cap)
        if kind == "narrow":
            reference.require_narrow_gap()
            self.gap = reference.narrow_gap
            self.factor_bound = max(Q(3), 1 / self.gap)
        else:
            self.gap = None
            need(reference.errors["broad"] * self.raw_inverse_bound <= Q(1, 2),
                 "broad reference interior inverse margin")
            self.factor_bound = 3 + 18 * self.raw_inverse_bound
        k = self.factor_bound
        self.stage_radius = 6 * k ** 5 * y0
        self.stage_error = Q(1, 1 << target) / (10 * k ** 4)
        self.dense_radius = ceiling_sqrt(cap) * self.stage_radius
        self.dense_target = target + ceil_log2(20 * k ** 4)
        for cell in self.cells:
            cell["probe"] = RawGaussian(raw, reference, kind, cell["source_start"], len(cell["indices"]),
                                        self.dense_radius, self.dense_target, 0)
        self.matrix = real(reference.window(kind, self.coordinates))
        self.reference_hash = matrix_hash(self.matrix)
        need(bandwidth(self.matrix) <= width, "no unhandled cyclic core corner")
        need(row_norm(self.matrix) <= (2 if kind == "narrow" else 3), "core reference row norm")
        if kind == "narrow":
            need(row_gap(self.matrix) >= self.gap, "core inherits the common reference gap")
        self.prepare_schur()
        self.schur_band = bandwidth(self.schur)
        need(self.schur_band <= 2 * width - 1, "compressed ordinary Schur bandwidth")
        if kind == "narrow":
            need(row_norm(self.schur) <= 2 and row_gap(self.schur) >= self.gap,
                 "same-reference narrow Schur norm and gap")
        else:
            need(row_norm(self.schur) <= self.factor_bound, "applied broad Schur norm")
        self.p = max(width + 1, ceiling_sqrt(1 / (16 * self.gap))) if self.gap else width + 1
        self.block_width = 1 << max(0, (max(1, self.schur_band) - 1).bit_length())
        qe = target + ceil_log2(10 * k ** 4)
        boundary_bits = qe + 41 + 16 * ceil_log2(self.p) + ceil_log2(self.stage_radius)
        sparse_bits = 1 + ceil_log2(((2 * width + 1) * self.stage_radius + 1) / self.stage_error)
        apply_bits = 1 + ceil_log2(((2 * self.schur_band + 1) * self.stage_radius + 1) / self.stage_error)
        self.bits = max(incoming, sparse_bits, boundary_bits if kind == "narrow" else apply_bits,
                        *(cell["probe"].data_bits for cell in self.cells))
        self.upper_page = self.adapter.rounded(self.upper_coupling, self.bits)
        self.lower_page = self.adapter.rounded(self.lower_coupling, self.bits)
        self.schur_page = self.adapter.rounded(self.schur, self.bits) if kind == "broad" else None
        self.solver = (Boundary(raw, self.adapter, self.schur, self.block_width, self.p,
                                self.bits, self.stage_radius, self.gap) if kind == "narrow" else None)
        if self.solver:
            need(self.solver.error_bound <= self.stage_error, "funded complete boundary solve")
        for cell in self.cells:
            cell["program"] = RawGaussian(raw, reference, kind, cell["source_start"], len(cell["indices"]),
                                          self.dense_radius, self.dense_target, self.bits)
            cell["program"].compile()
            need(cell["program"].data_bits == self.bits, "one core and raw data grid")
        self.stages, self.word_ast = self.load_word()
        self.amplitude_bound = max(
            16 * (k + 1) * self.stage_radius,
            self.solver.temporary_bound if self.solver else Q(1),
            *(cell["program"].bound["amplitude_bound"] for cell in self.cells))
        self.integer_bits = max(1, ceil_log2(self.amplitude_bound)) + 2
        self.temporary_bits = max([2 * self.bits + self.integer_bits + 2,
                                  *(cell["program"].bound["temporary_bits"] for cell in self.cells)])
        self.total_error = 5 * k ** 4 * self.stage_error
        need(self.total_error <= Q(1, 1 << (target + 1)), "complete five-factor error allowance")

    def load_carve(self):
        tree = ast.parse(self.raw[CARVE])
        tree.body = [copy.deepcopy(node) for node in tree.body
                     if isinstance(node, ast.FunctionDef) and node.name == "carve"]
        need(len(tree.body) == 1, "one retained carve")
        namespace = {}
        exec(compile(tree, "<authenticated capped carve>", "exec", optimize=0), namespace)
        return namespace["carve"], hashlib.sha256(ast.dump(tree).encode()).hexdigest()

    def partition(self):
        ref, pieces, cells, cursor = self.reference, [], [], 0
        while cursor < self.n:
            source = ref.source_at.get(self.coordinates[cursor])
            if source is None:
                pieces.append(dict(kind="B", start=cursor, stop=cursor + 1, phase=None))
                cursor += 1
                continue
            phase, stop = ref.phases[source], cursor + 1
            while stop < self.n:
                j = ref.source_at.get(self.coordinates[stop])
                if j != source + stop - cursor or ref.phases[j] != phase:
                    break
                stop += 1
            for kind, a, b in self.carve(stop - cursor, self.width, self.cap):
                need(0 <= a < b <= stop - cursor, "positive retained carve piece")
                pieces.append(dict(kind=kind, start=cursor + a, stop=cursor + b, phase=phase))
                if kind == "I":
                    indices = list(range(cursor + a, cursor + b))
                    coordinates, _, _ = ref.interior(source + a, b - a)
                    need(coordinates == tuple(self.coordinates[i] for i in indices), "carved source binding")
                    cells.append(dict(indices=indices, source_start=source + a))
            cursor = stop
        need(pieces[0]["start"] == 0 and pieces[-1]["stop"] == self.n
             and all(a["stop"] == b["start"] for a, b in zip(pieces, pieces[1:])), "complete carve coverage")
        need(all(b["indices"][0] - a["indices"][-1] > self.width
                 for a, b in zip(cells, cells[1:])), "separated reference interiors")
        return pieces, cells

    def prepare_schur(self):
        self.upper_coupling = block(self.matrix, self.interior, self.boundary)
        self.lower_coupling = block(self.matrix, self.boundary, self.interior)
        self.schur = block(self.matrix, self.boundary, self.boundary)
        owner = {i: j for j, cell in enumerate(self.cells) for i in cell["indices"]}
        need(all(self.matrix[i][j] == 0 for i in self.interior for j in self.interior
                 if owner[i] != owner[j]), "actual reference interior direct sum")
        for cell in self.cells:
            indices = cell["indices"]
            matrix = block(self.matrix, indices, indices)
            inverse = self.adapter.solve(matrix, self.adapter.identity(len(indices)))
            limit = 1 / self.gap if self.gap else 2 * self.raw_inverse_bound
            need(row_norm(matrix) <= (2 if self.gap else 3)
                 and row_norm(inverse) <= limit, "reference interior factor bounds")
            cell["matrix"], cell["inverse"] = matrix, inverse
            left, right = block(self.matrix, self.boundary, indices), block(self.matrix, indices, self.boundary)
            correction = product(left, product(inverse, right))
            self.schur = [[x - y for x, y in zip(a, b)] for a, b in zip(self.schur, correction)]

    def load_word(self):
        tree = ast.parse(self.raw[WORD])
        assignments = [copy.deepcopy(node) for node in ast.walk(tree)
                       if isinstance(node, ast.Assign) and len(node.targets) == 1
                       and isinstance(node.targets[0], ast.Name) and node.targets[0].id == "seq"]
        need(len(assignments) == 1, "one retained six-stage factor word")
        module = ast.Module(body=assignments, type_ignores=[])
        a, ai, si = object(), object(), object()
        def embedded(value, indices, n):
            need(n == self.n, "source word dimension")
            if value is si:
                need(indices == self.boundary, "source boundary coordinates")
                return "boundary_inverse"
            need(indices == self.interior and value in (a, ai), "source interior coordinates")
            return "interior_forward" if value is a else "interior_inverse"
        namespace = dict(A=a, Ai=ai, Si=si, I=self.interior, J=self.boundary, n=self.n,
                         lower="lower_negative", upper="upper_negative", embedded=embedded)
        exec(compile(module, "<authenticated Gaussian factor word>", "exec", optimize=0), namespace)
        inverse_word = namespace["seq"]
        need(inverse_word == ["interior_inverse", "lower_negative", "boundary_inverse",
                              "interior_forward", "upper_negative", "interior_inverse"],
             "retained inverse chronology")
        if self.kind == "narrow":
            stages = inverse_word
        else:
            inverse_names = {"interior_inverse": "interior_forward", "interior_forward": "interior_inverse",
                             "boundary_inverse": "boundary_forward", "lower_negative": "lower_positive",
                             "upper_negative": "upper_positive"}
            stages = [inverse_names[name] for name in reversed(inverse_word)]
        return stages, hashlib.sha256(ast.dump(module).encode()).hexdigest()

    def execute(self, rhs, capture=False):
        state = Mat(rhs)
        columns = len(state[0]) if state else 0
        need(len(state) == self.n and columns > 0 and all(len(row) == columns for row in state),
             "complete core RHS shape")
        need(max_complex(state) <= self.y0 and all(
            (part * (1 << self.incoming)).denominator == 1
            for row in state for z in row for part in (z.re, z.im)), "declared core input grid and radius")
        need(matrix_hash(real(self.reference.window(self.kind, self.coordinates))) == self.reference_hash,
             "same immutable reference core at execution")
        need(self.stages == self.load_word()[0], "authenticated core chronology")
        records, traces = [], []
        stats = dict(dense_gate_applications=0, dense_rounded_outputs=0, dense_max_height=0,
                     boundary_scalar_products=0, sparse_real_products=0, sparse_complex_rounds=0,
                     sparse_fractional_bits=0, sparse_fixed_numerator_bits=0,
                     stored_grid_numerator_bits=0)

        def observe_state():
            need(max_complex(state) <= self.stage_radius, "actual stage input/output envelope")
            for row in state:
                for z in row:
                    for part in (z.re, z.im):
                        scaled = part * (1 << self.bits)
                        need(scaled.denominator == 1, "one completed core data grid")
                        stats["stored_grid_numerator_bits"] = max(
                            stats["stored_grid_numerator_bits"], abs(scaled.numerator).bit_length())
            need(stats["stored_grid_numerator_bits"] + 1 <= self.bits + self.integer_bits,
                 "signed core data words")

        def observe_temporary(value):
            denominator = value.denominator
            need(denominator & (denominator - 1) == 0
                 and denominator.bit_length() - 1 <= 2 * self.bits, "sparse dyadic temporary grid")
            stats["sparse_fractional_bits"] = max(stats["sparse_fractional_bits"],
                                                 denominator.bit_length() - 1)
            encoded = value * (1 << (2 * self.bits))
            need(encoded.denominator == 1, "fixed sparse temporary numerator")
            stats["sparse_fixed_numerator_bits"] = max(
                stats["sparse_fixed_numerator_bits"], abs(encoded.numerator).bit_length())
            need(stats["sparse_fixed_numerator_bits"] + 1 <= self.temporary_bits,
                 "signed sparse temporary width")

        def sparse(page, targets, sources, sign, add):
            output, scale = [], 1 << self.bits
            for i, row in zip(targets, page):
                new = []
                for col in range(columns):
                    re, im = (state[i][col].re, state[i][col].im) if add else (Q(0), Q(0))
                    for j, coefficient in zip(sources, row):
                        if coefficient:
                            x, y = coefficient * state[j][col].re, coefficient * state[j][col].im
                            stats["sparse_real_products"] += 2
                            observe_temporary(x)
                            observe_temporary(y)
                            re += sign * x
                            im += sign * y
                            observe_temporary(re)
                            observe_temporary(im)
                    new.append(C(Q(int(re * scale), scale), Q(int(im * scale), scale)))
                    stats["sparse_complex_rounds"] += 1
                output.append(new)
            for i, row in zip(targets, output):
                state[i] = row

        observe_state()
        for number, stage in enumerate(self.stages):
            before = Mat([list(row) for row in state]) if capture else None
            stage_stats = {}
            if stage.startswith("interior_"):
                for cell in self.cells:
                    program = cell["program"]
                    if stage == "interior_inverse":
                        plan = program.inverse_plan
                    else:
                        plan = program.plan
                    for col in range(columns):
                        vector = Vec(state[i][col] for i in cell["indices"])
                        need(sum((z.norm2() for z in vector), Q(0)) <= self.dense_radius ** 2,
                             "actual dense input radius")
                        output, measured = apply(plan, vector, self.bits)
                        for i, value in zip(cell["indices"], output):
                            state[i][col] = value
                        stats["dense_gate_applications"] += sum(map(len, plan))
                        stats["dense_rounded_outputs"] += measured["rounded_outputs"]
                        stats["dense_max_height"] = max(stats["dense_max_height"], measured["max_observed_height"])
                        need(measured["max_observed_height"] <= program.bound["temporary_bits"],
                             "dense arithmetic temporary width")
            elif stage == "boundary_inverse":
                boundary_rhs = Mat([state[i] for i in self.boundary])
                output, stage_stats = self.solver.run(boundary_rhs)
                for i, row in zip(self.boundary, output):
                    state[i] = row
                stats["boundary_scalar_products"] += (
                    stage_stats["lower"]["scalar_products"] + stage_stats["upper"]["scalar_products"])
                need(max(stage_stats["lower"]["fractional_bits"],
                         stage_stats["upper"]["fractional_bits"]) <= 2 * self.bits,
                     "boundary temporary fractional widths")
            elif stage == "boundary_forward":
                sparse(self.schur_page, self.boundary, self.boundary, 1, False)
            elif stage.startswith("lower_"):
                sparse(self.lower_page, self.boundary, self.interior,
                       -1 if stage.endswith("negative") else 1, True)
            elif stage.startswith("upper_"):
                sparse(self.upper_page, self.interior, self.boundary,
                       -1 if stage.endswith("negative") else 1, True)
            else:
                raise ValueError("unknown core factor")
            observe_state()
            records.append(dict(index=number, factor_index=(0, 1, 2, 2, 3, 4)[number],
                                stage=stage, output_sha256=matrix_hash(state),
                                maximum_upper=str(upper(max_complex(state))), boundary=stage_stats))
            if capture:
                traces.append((stage, before, Mat([list(row) for row in state])))
        return state, dict(stages=records, statistics=stats), traces

    def record(self):
        return dict(kind=self.kind, first=self.first, last=self.last, rows=self.n, cap=self.cap,
                    physical_band=self.width,
                    common_band=self.width >= max(2 * self.reference.spec.source_halfwidth + 2,
                                                  self.reference.spec.target_halfwidth),
                    cap_exceeds_band=self.cap > self.width,
                    reference_description_sha256=self.reference.description_hash,
                    reference_matrix_sha256=self.reference_hash,
                    carve_ast_sha256=self.carve_ast, word_ast_sha256=self.word_ast,
                    boundary_adapter_ast_sha256=self.adapter.source_ast_sha256,
                    pieces=self.pieces, interior=self.interior, boundary=self.boundary,
                    interior_blocks=[dict(source_start=cell["source_start"], indices=cell["indices"],
                                          reference_sha256=matrix_hash(cell["matrix"]),
                                          reference_inverse_sha256=matrix_hash(cell["inverse"]),
                                          program=raw_core_record(cell["program"])) for cell in self.cells],
                    schur_sha256=matrix_hash(self.schur), schur_band=self.schur_band,
                    upper_coupling_sha256=matrix_hash(self.upper_coupling),
                    lower_coupling_sha256=matrix_hash(self.lower_coupling),
                    upper_page_sha256=matrix_hash(self.upper_page), lower_page_sha256=matrix_hash(self.lower_page),
                    boundary_solver=self.solver.record() if self.solver else None,
                    stage_order=self.stages,
                    budget=dict(input_bound=str(self.y0), target_bits=self.target,
                                incoming_bits=self.incoming, data_bits=self.bits,
                                factor_bound=str(self.factor_bound), stage_radius=str(self.stage_radius),
                                stage_error=str(self.stage_error), dense_radius=str(self.dense_radius),
                                dense_target_bits=self.dense_target,
                                core_gap_lower=str(self.gap) if self.gap else None,
                                raw_inverse_bound=str(self.raw_inverse_bound),
                                total_error=str(self.total_error), amplitude_bound=str(self.amplitude_bound),
                                integer_bits=self.integer_bits, temporary_bits=self.temporary_bits))
