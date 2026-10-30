"""Exact fixed-word combination-carrier screens. Apache-2.0.

API: run(word, vendor_path) -> deterministic JSON-compatible dictionary.
vendor_path contains the pinned PR6045 leakfix.py and inputs/shapesplit.py.
The caller authenticates source bytes before calling this module. No files are
written, and no scratch-tree imports, optional packages, or subprocesses are used.
See CARRIER-PROOF.md for the mathematical scope and predecessor attribution.
"""

from collections import defaultdict
from fractions import Fraction as Q
from itertools import permutations
from pathlib import Path
import importlib.util
import sys


def need(condition, message):
    if not condition:
        raise ValueError(message)


def add(destination, source, coefficient):
    for role, value in source.items():
        new = destination.get(role, Q(0)) + coefficient * value
        if new:
            destination[role] = new
        else:
            destination.pop(role, None)


def dot(left, right):
    return sum(value * right.get(role, Q(0)) for role, value in left.items())


def serial(vector):
    return {str(role): str(value) for role, value in sorted(vector.items())}


class Span:
    """Sparse rational echelon basis, with an optional coordinate ordering."""

    def __init__(self, vectors=(), order=None):
        self.pivots = {}
        self.order = order
        for vector in vectors:
            self.insert(vector)

    def reduce(self, vector):
        vector = dict(vector)
        while vector:
            pivot = min(vector) if self.order is None else min(vector, key=self.order.__getitem__)
            if pivot not in self.pivots:
                return vector, pivot
            add(vector, self.pivots[pivot], -vector[pivot])
        return vector, None

    def insert(self, vector):
        vector, pivot = self.reduce(vector)
        if pivot is None:
            return False
        divisor = vector[pivot]
        self.pivots[pivot] = {role: value / divisor for role, value in vector.items()}
        return True


def load_vendor(directory):
    """Load exactly this vendor directory, without trusting a prior module cache."""
    directory = Path(directory)
    shapes_path = directory / "inputs" / "shapesplit.py"
    leak_path = directory / "leakfix.py"
    need(shapes_path.is_file() and leak_path.is_file(), "missing carrier vendor sources")
    shapes_spec = importlib.util.spec_from_file_location("_carrier_shapesplit", shapes_path)
    need(shapes_spec is not None and shapes_spec.loader is not None, "cannot load shapesplit")
    shapes = importlib.util.module_from_spec(shapes_spec)
    shapes_spec.loader.exec_module(shapes)
    # PR6045 looks up this historical name. Scope that cache entry to this load.
    cache_key = "pr6040_shapesplit"
    previous = sys.modules.get(cache_key)
    sys.modules[cache_key] = shapes
    try:
        leak_spec = importlib.util.spec_from_file_location("_carrier_leakfix", leak_path)
        need(leak_spec is not None and leak_spec.loader is not None, "cannot load leakfix")
        leak = importlib.util.module_from_spec(leak_spec)
        leak_spec.loader.exec_module(leak)
        need(leak.SS is shapes, "vendor module binding mismatch")
    finally:
        if previous is None:
            sys.modules.pop(cache_key, None)
        else:
            sys.modules[cache_key] = previous
    return leak


def transport(vector, event):
    """Primal transport, including optimistic deletion at existing owned CLEARs."""
    operation, role = event[:2]
    if operation in ("INIT", "CLEAR"):
        vector.pop(role, None)
    elif operation == "COPY":
        value = Q(event[-2]) * vector.get(event[2], Q(0))
        vector.pop(role, None)
        if value:
            vector[role] = value
    elif operation == "ADD":
        add(vector, {role: Q(1)}, Q(event[-2]) * vector.get(event[2], Q(0)))
    elif operation == "SCALE":
        if role in vector:
            vector[role] *= Q(event[-2])
    else:
        need(operation == "MOVE", "unknown primal operation")


class Baseline:
    """Original rows, their complete left kernel, and actual chart membership.

    The first pass tracks rows and explicitly validates baseline premises.
    Later passes reuse the same authenticated word and transport its kernel.
    """

    def __init__(self, word, frame_spans, track_rows=False):
        self.n = word["public"]
        self.total = self.n + word["owned_fields"]
        need(len(word["initial"]) == self.n == len(word["final"]), "boundary length mismatch")
        self.frames = frame_spans
        self.current = list(word["initial"]) + [None] * (self.total - self.n)
        self.at = defaultdict(set)
        for role, chart in enumerate(self.current):
            if chart is not None:
                need(0 <= chart < len(self.frames), "invalid initial chart")
                self.at[chart].add(role)
        self.rows = [{role: Q(1)} if role < self.n else {} for role in range(self.total)] if track_rows else None
        self.kernel = []
        self.owned = set()
        self.peak = 0
        self.checks = 0
        self.copies_checked = 0
        self.lifetimes = 0
        self.nonzero_clears = 0
        self.dirty = True
        self.pure_cache = []

    def check_kernel(self):
        need(len(Span(self.kernel).pivots) == len(self.kernel), "dependent kernel basis")
        if self.rows is not None:
            for covector in self.kernel:
                image = {}
                for role, coefficient in covector.items():
                    need(self.current[role] is not None, "kernel uses dead register")
                    add(image, self.rows[role], coefficient)
                need(not image, "kernel does not annihilate original rows")
        self.checks += 1

    def step(self, event):
        operation, role = event[:2]
        need(type(role) is int and 0 <= role < self.total, "invalid role")
        if operation == "INIT":
            need(len(event) == 3 and role >= self.n and self.current[role] is None, "invalid INIT")
            chart = event[2]
            need(type(chart) is int and 0 <= chart < len(self.frames), "invalid INIT chart")
            self.owned.add(role)
            self.current[role] = chart
            self.at[chart].add(role)
            self.kernel.append({role: Q(1)})
            if self.rows is not None:
                self.rows[role] = {}
            self.lifetimes += 1
            self.dirty = True
        elif operation == "CLEAR":
            need(len(event) == 3 and role in self.owned and self.current[role] == event[2], "invalid CLEAR")
            if self.rows is not None:
                self.check_kernel()
                self.nonzero_clears += bool(self.rows[role])
            choices = [j for j, vector in enumerate(self.kernel) if vector.get(role)]
            need(bool(choices), "CLEAR removes an independent original row")
            vector = self.kernel.pop(choices[0])
            divisor = vector[role]
            vector = {key: value / divisor for key, value in vector.items()}
            for other in self.kernel:
                if other.get(role):
                    add(other, vector, -other[role])
            self.at[self.current[role]].remove(role)
            self.current[role] = None
            self.owned.remove(role)
            if self.rows is not None:
                self.rows[role] = {}
            self.dirty = True
        elif operation in ("ADD", "COPY"):
            need(len(event) == 5, "invalid binary operation")
            source = event[2]
            need(type(source) is int and 0 <= source < self.total and source != role, "invalid source")
            need(self.current[role] is not None and self.current[role] == self.current[source] == event[-1], "binary operation lacks common chart")
            coefficient = Q(event[-2])
            if operation == "COPY":
                need(role in self.owned, "COPY destination is not owned")
                if self.rows is not None:
                    need(not self.rows[role], "COPY overwrites a nonzero original row")
                    self.copies_checked += 1
            if self.rows is not None:
                add(self.rows[role], self.rows[source], coefficient)
            for covector in self.kernel:
                if covector.get(role):
                    add(covector, {source: Q(1)}, -coefficient * covector[role])
                    self.dirty = True
        elif operation == "SCALE":
            need(len(event) == 4 and self.current[role] is not None and self.current[role] == event[-1], "invalid SCALE")
            coefficient = Q(event[-2])
            need(bool(coefficient), "zero SCALE")
            if self.rows is not None:
                self.rows[role] = {key: coefficient * value for key, value in self.rows[role].items()}
            for covector in self.kernel:
                if role in covector:
                    covector[role] /= coefficient
                    self.dirty = True
        else:
            need(operation == "MOVE" and len(event) == 5, "unknown operation")
            old, new = event[2:4]
            need(self.current[role] is not None and self.current[role] == old, "stale MOVE source")
            need(type(new) is int and 0 <= new < len(self.frames), "invalid MOVE destination")
            need(self.frames[old] <= self.frames[new] or self.frames[new] <= self.frames[old], "nonnested MOVE")
            self.at[old].remove(role)
            self.at[new].add(role)
            self.current[role] = new
            if any(role in covector for covector in self.kernel):
                self.dirty = True
        need(len(self.kernel) == len(self.owned), "kernel dimension differs from live owned count")
        self.peak = max(self.peak, len(self.kernel))
        if operation in ("INIT", "CLEAR"):
            self.check_kernel()

    def finish(self, word):
        need(not self.owned and not self.kernel, "unfinished owned lifetimes")
        need(self.current[:self.n] == word["final"], "final chart mismatch")

    def chart_kernel(self, shapes):
        if self.dirty:
            by_chart = defaultdict(set)
            for role in {role for vector in self.kernel for role in vector}:
                need(self.current[role] is not None, "dead role in kernel support")
                by_chart[self.current[role]].add(role)
            self.pure_cache = []
            for chart in sorted(by_chart):
                support = by_chart[chart]
                for _, image in shapes.pure_subspace(self.kernel, range(len(self.kernel)), support):
                    need(bool(image) and set(image) <= support, "invalid chart-kernel intersection")
                    self.pure_cache.append((chart, image))
            self.dirty = False
        return self.pure_cache


def case_id(case):
    return [case["cut_after"], case["frame"], case["pivot"]]


def brief(case):
    result = {key: case[key] for key in ("cut_after", "frame", "pivot", "group", "ranks", "leak")}
    result["group"] = list(case["group"])
    return result


def global_screen(word, cases, shapes):
    state = Baseline(word, shapes.spans(word), track_rows=True)
    at_cut = defaultdict(list)
    for case in cases:
        at_cut[case["cut_after"]].append(case)
    excluded, survived, witnesses = [], [], []
    for index, event in enumerate(word["program"]):
        state.step(event)
        check_cut = False
        for case in at_cut.get(index, ()):
            witness = next((v for v in state.kernel if v.get(case["pivot"])), None)
            if witness is None:
                excluded.append(case_id(case))
            else:
                survived.append(case)
                witnesses.append(dict(brief(case), dependency=serial(witness)))
                check_cut = True
        if check_cut:
            state.check_kernel()
    state.finish(word)
    need(len(excluded) + len(survived) == len(cases), "unvisited global-screen cut")
    return survived, dict(
        excluded_count=len(excluded), excluded_ids=excluded,
        surviving_count=len(survived), survivors=witnesses,
        peak_kernel_dimension=state.peak, kernel_snapshots_checked=state.checks,
        copy_zero_checks=state.copies_checked, owned_lifetimes=state.lifetimes,
        nonzero_owned_clears=state.nonzero_clears,
    )


def first_carrier_screen(word, cases, shapes):
    state = Baseline(word, shapes.spans(word))
    starts = defaultdict(list)
    for key, case in enumerate(cases):
        starts[case["cut_after"]].append(key)
    signals, found = {}, {}
    for index, event in enumerate(word["program"]):
        for signal in signals.values():
            transport(signal, event)
        state.step(event)
        for key in starts.get(index, ()):
            signals[key] = {cases[key]["pivot"]: Q(1)}
        if not signals:
            continue
        pure = state.chart_kernel(shapes)
        for key, signal in signals.items():
            if key in found:
                continue
            for chart, covector in pure:
                pairing = dot(covector, signal)
                if pairing:
                    found[key] = dict(case=brief(cases[key]), after_event=index, chart=chart,
                                      beta_pairing=str(pairing), combination=serial(covector))
                    break
    state.finish(word)
    need(len(signals) == len(cases), "unvisited first-carrier cut")
    return [cases[key] for key in sorted(found)], dict(
        tested=len(cases), excluded_count=len(cases)-len(found),
        excluded_ids=[case_id(case) for key, case in enumerate(cases) if key not in found],
        surviving_count=len(found), survivors=[found[key] for key in sorted(found)],
    )


def saturate(offset, directions, pure, membership):
    """Smallest affine enclosure invariant under relaxed current-chart controls."""
    span = Span(directions)
    activated, receivers = set(), set()
    changed, added = True, 0
    while changed:
        changed = False
        for chart, covector in pure:
            if chart in activated:
                continue
            if dot(covector, offset) or any(dot(covector, vector) for vector in span.pivots.values()):
                activated.add(chart)
                for role in sorted(membership[chart]):
                    receivers.add(role)
                    if span.insert({role: Q(1)}):
                        added += 1
                        changed = True
    for chart, covector in pure:
        if dot(covector, offset) or any(dot(covector, vector) for vector in span.pivots.values()):
            need(all(not span.reduce({role: Q(1)})[0] for role in membership[chart]), "unsaturated affine enclosure")
    return list(span.pivots.values()), activated, receivers, added


def determinant(matrix):
    """Independent Leibniz formula; used only for small terminal certificates."""
    size = len(matrix)
    need(size <= 8 and all(len(row) == size for row in matrix), "terminal minor is not small and square")
    result = Q(0)
    for permutation in permutations(range(size)):
        term = Q((-1) ** sum(permutation[i] > permutation[j] for i in range(size) for j in range(i+1, size)))
        for row, column in enumerate(permutation):
            term *= matrix[row][column]
        result += term
    return result


def dense_suffix(word, cut, pivot):
    """Separate dense primal implementation for the final-column certificate."""
    signal = [Q(0)] * (word["public"] + word["owned_fields"])
    signal[pivot] = Q(1)
    for event in word["program"][cut+1:]:
        operation, role = event[:2]
        if operation in ("INIT", "CLEAR"):
            signal[role] = Q(0)
        elif operation == "COPY":
            signal[role] = Q(event[-2]) * signal[event[2]]
        elif operation == "ADD":
            signal[role] += Q(event[-2]) * signal[event[2]]
        elif operation == "SCALE":
            signal[role] *= Q(event[-2])
        else:
            need(operation == "MOVE", "unknown dense suffix operation")
    need(not any(signal[word["public"]:]), "nonzero terminal owned signal")
    return signal[:word["public"]]


def solve_square(matrix, rhs):
    rows = [list(row)+[value] for row, value in zip(matrix, rhs)]
    for column in range(len(matrix)):
        candidates = [i for i in range(column, len(matrix)) if rows[i][column]]
        need(bool(candidates), "singular terminal minor")
        pivot = candidates[0]
        rows[column], rows[pivot] = rows[pivot], rows[column]
        divisor = rows[column][column]
        rows[column] = [value/divisor for value in rows[column]]
        for i in range(len(matrix)):
            if i != column:
                coefficient = rows[i][column]
                rows[i] = [x-coefficient*y for x, y in zip(rows[i], rows[column])]
    return [row[-1] for row in rows]


def terminal_certificate(word, case, basis, protected_roles, offset):
    matrix = [[vector.get(role, Q(0)) for vector in basis] for role in protected_roles]
    det = determinant(matrix)
    need(bool(det), "terminal protected projection is not injective")
    dense = dense_suffix(word, case["cut_after"], case["pivot"])
    need(all(dense[role] == offset.get(role, Q(0)) for role in range(word["public"])), "sparse/dense suffix mismatch")
    coefficients = solve_square(matrix, [dense[role] for role in protected_roles])
    need(all(sum(coefficient*vector.get(role, Q(0)) for coefficient, vector in zip(coefficients, basis)) == dense[role]
             for role in range(word["public"])), "offset is not in terminal correction span")
    return dict(protected_roles=protected_roles, determinant=str(det),
                baseline_coefficients=[str(value) for value in coefficients],
                checked_output_coordinates=word["public"])


def dynamic_screen(word, cases, shapes):
    state = Baseline(word, shapes.spans(word))
    starts = defaultdict(list)
    for key, case in enumerate(cases):
        starts[case["cut_after"]].append(key)
    active = {}
    for index, event in enumerate(word["program"]):
        for candidate in active.values():
            transport(candidate["offset"], event)
            for direction in candidate["directions"]:
                transport(direction, event)
        state.step(event)
        for key in starts.get(index, ()):
            active[key] = dict(offset={cases[key]["pivot"]: Q(1)}, directions=[], activations=[], maximum_rank=0)
        if not active:
            continue
        pure = state.chart_kernel(shapes)
        for candidate in active.values():
            before = len(candidate["directions"])
            directions, charts, receivers, added = saturate(candidate["offset"], candidate["directions"], pure, state.at)
            candidate["directions"] = directions
            candidate["maximum_rank"] = max(candidate["maximum_rank"], len(directions))
            if added:
                candidate["activations"].append(dict(after_event=index, charts=sorted(charts), receivers=sorted(receivers),
                                                       rank_before=before, rank_after=len(directions), added_directions=added))
    state.finish(word)
    need(len(active) == len(cases), "unvisited dynamic cut")
    results = []
    for key, case in enumerate(cases):
        candidate = active[key]
        outside = case["outside"]
        order = {role: index for index, role in enumerate(sorted(outside)+[r for r in range(word["public"]) if r not in outside])}
        need(all(role < word["public"] for vector in [candidate["offset"]]+candidate["directions"] for role in vector), "terminal owned support")
        span = Span(candidate["directions"], order)
        remainder, pivot = span.reduce(candidate["offset"])
        free = [vector for p, vector in span.pivots.items() if p not in outside]
        if pivot in outside:
            outcome = "outside_unreachable"
        elif not remainder and not free:
            outcome = "only_zero_signal"
        else:
            outcome = "productive_affine_relaxation_survives"
        need(candidate["offset"] == case["dall"], "vendor/primal suffix column mismatch")
        protected_roles = sorted(p for p in span.pivots if p in outside)
        basis = list(span.pivots.values())
        certificate = terminal_certificate(word, case, basis, protected_roles, candidate["offset"]) if outcome == "only_zero_signal" else None
        results.append(dict(case=brief(case), outcome=outcome, maximum_correction_rank=candidate["maximum_rank"],
                            final_correction_rank=len(basis), protected_projection_rank=len(protected_roles),
                            zero_protected_dimension=len(free), affine_remainder=serial(remainder),
                            activations=candidate["activations"], final_basis=[serial(v) for v in basis],
                            independent_terminal=certificate))
    return dict(tested=len(cases), results=results)


def expect_rejection(function, message):
    try:
        function()
    except ValueError:
        return
    raise ValueError(message)


def controls():
    """Discriminating algebra and baseline guards, all active under python -O."""
    toy = dict(public=2, owned_fields=1, initial=[0, 0], final=[0, 0])
    frames = [frozenset({0}), frozenset({0, 1})]
    state = Baseline(toy, frames, track_rows=True)
    state.step(["INIT", 2, 0])
    need(not any(v.get(0) for v in state.kernel), "independent pivot incorrectly dependent")
    state.step(["COPY", 2, 0, "1", 0])
    state.check_kernel()
    need(any(v.get(0) for v in state.kernel) and not any(v.get(1) for v in state.kernel), "snapshot dependency control failed")
    state.step(["ADD", 0, 1, "2", 0])
    state.step(["SCALE", 1, "-2", 0])
    state.check_kernel()
    need(any(v.get(1) for v in state.kernel), "inverse kernel transport control failed")
    expect_rejection(lambda: state.step(["COPY", 2, 0, "1", 0]), "nonzero COPY accepted")
    expect_rejection(lambda: state.step(["SCALE", 1, "0", 0]), "zero SCALE accepted")
    expect_rejection(lambda: state.step(["MOVE", 0, 1, 0, False]), "stale MOVE accepted")
    state.step(["CLEAR", 2, 0])
    state.finish(toy)
    expect_rejection(lambda: state.step(["CLEAR", 2, 0]), "duplicate CLEAR accepted")

    offset = {0: Q(1)}
    original_rows = [{0: Q(1)}, {0: Q(1)}, {1: Q(1)}, {1: Q(1)}, {2: Q(1)}]
    first = {1: Q(1), 0: Q(-1)}
    later = {3: Q(1), 2: Q(-1)}
    for covector in (first, later):
        image = {}
        for role, coefficient in covector.items():
            add(image, original_rows[role], coefficient)
        need(not image, "toy carrier has nonzero original value")
    directions, _, _, _ = saturate(offset, [], [(0, first)], {0: [0, 1, 2]})
    need(not dot(later, offset) and any(dot(later, vector) for vector in directions), "later carrier was not newly enabled")
    dynamic, activated, _, _ = saturate(offset, directions, [(1, later)], {1: [2, 3, 4]})
    need(1 in activated and not Span(dynamic).reduce({4: Q(1)})[0], "sequential carrier positive failed")
    static, activated, _, _ = saturate(offset, [], [(1, later)], {1: [2, 3, 4]})
    need(not static and not activated, "static carrier negative failed")
    concrete = dict(offset)
    add(concrete, {2: Q(1)}, dot(first, concrete))
    add(concrete, {4: Q(1)}, dot(later, concrete))
    need(concrete.get(4) == 1, "concrete sequential witness failed")
    remainder, pivot = Span([{1: Q(1)}], {0: 0, 1: 1}).reduce({0: Q(1)})
    need(remainder == {0: Q(1)} and pivot == 0, "affine offset control failed")
    need(determinant([[Q(1), Q(2)], [Q(3), Q(4)]]) == -2, "determinant control failed")
    expect_rejection(lambda: solve_square([[Q(1), Q(1)], [Q(1), Q(1)]], [Q(1), Q(1)]), "singular certificate accepted")
    return dict(snapshot_positive=True, independent_pivot_negative=True, inverse_add_scale=True,
                nonzero_copy_rejected=True, zero_scale_rejected=True, stale_move_rejected=True,
                duplicate_clear_rejected=True, sequential_new_carrier_positive=True,
                static_screen_misses_later_carrier=True, concrete_sequential_witness=True,
                affine_offset_negative=True, determinant_positive=True, singular_minor_rejected=True)


def run(word, vendor_path):
    """Return deterministic exact evidence; source authentication belongs to caller."""
    control_results = controls()
    vendor = load_vendor(vendor_path)
    classes, census = vendor.leak_classes(word)
    leaks = [case for case in classes if case["kind"] == "leak"]
    need(len({tuple(case_id(case)) for case in leaks}) == len(leaks), "duplicate leak class identity")
    survivors, global_result = global_screen(word, leaks, vendor.SS)
    dynamic_cases, first_result = first_carrier_screen(word, survivors, vendor.SS)
    dynamic_result = dynamic_screen(word, dynamic_cases, vendor.SS)
    all_excluded = all(result["outcome"] in ("outside_unreachable", "only_zero_signal") for result in dynamic_result["results"])
    return dict(schema="p104-fixed-word-carrier-screen/1", controls=control_results,
                census=dict(census), leak_classes=len(leaks), single_leak_classes=sum(case["leak"] == 1 for case in leaks),
                global_screen=global_result, first_carrier_screen=first_result, dynamic_screen=dynamic_result,
                all_tested_leak_classes_excluded=all_excluded,
                scope="Unit-injection leak classes of the pinned census; fixed original word, charts and owned lifetimes; arbitrary sequential rational chart-local corrections whose combined source has zero original value. The affine relaxation permits self/noninvertible controls. Nonzero-original correction programs, changed injections/events/MOVEs/storage and different words are excluded from this claim.")
