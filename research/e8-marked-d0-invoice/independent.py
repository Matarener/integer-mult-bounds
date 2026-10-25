#!/usr/bin/env python3
"""Independent finite E8 checks for the marked d=0 investigation.

Author: conorholds.  Standard library only; imports no candidate/predecessor code.
Roots use doubled D8+ coordinates.  Binary labels are restrictions of actual
Gram-pairing rows to independently selected columns, not lattice coordinates.

This checks finite geometric inputs.  It does not prove the marked invoice,
the continuous coefficient case analysis, or the original two-sided bridge.
The three-axis form inventory gives an identity for arbitrary coefficients;
the coefficient-grid controls are examples, not a universal-field proof.
"""

from __future__ import annotations

import argparse
from collections import Counter
from itertools import combinations, product
import json
from math import gcd
import sys
import time


class CheckFailure(RuntimeError):
    pass


class BudgetExceeded(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise CheckFailure(message)


def dot(left, right):
    return sum(a * b for a, b in zip(left, right))


def projective(vector):
    first = next((value for value in vector if value), 0)
    require(first != 0, "zero projective vector")
    return tuple(vector if first > 0 else (-value for value in vector))


def primitive(vector):
    divisor = 0
    for value in vector:
        divisor = gcd(divisor, abs(value))
    require(divisor != 0, "zero primitive vector")
    return projective(tuple(value // divisor for value in vector))


def binary_insert(value, basis):
    while value:
        pivot = value.bit_length() - 1
        if pivot not in basis:
            basis[pivot] = value
            return True
        value ^= basis[pivot]
    return False


def binary_rank(values):
    basis = {}
    for value in values:
        binary_insert(value, basis)
    return len(basis)


def bits(indices):
    value = 0
    for index in indices:
        value |= 1 << index
    return value


def indices(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


class Checks:
    def __init__(self, mode, budget):
        self.mode = mode
        self.started = time.monotonic()
        self.deadline = self.started + budget
        self.results = {}
        self.controls = {}
        self.build_model()

    def tick(self):
        if time.monotonic() > self.deadline:
            raise BudgetExceeded("requested wall-clock budget exhausted")

    def record(self, name, **data):
        self.results[name] = data
        self.tick()

    def build_model(self):
        oriented = set()
        for i, j in combinations(range(8), 2):
            for first, second in product((-2, 2), repeat=2):
                vector = [0] * 8
                vector[i], vector[j] = first, second
                oriented.add(tuple(vector))
        require(len(oriented) == 112, "D8 roots are incomplete")
        for signs in product((-1, 1), repeat=8):
            if sum(value < 0 for value in signs) % 2 == 0:
                oriented.add(signs)
        require(len(oriented) == 240, "D8+ roots are incomplete")
        self.roots = sorted({projective(vector) for vector in oriented})
        require(len(self.roots) == 120, "projective E8 root count")
        require(all(dot(root, root) == 8 for root in self.roots), "root norm")
        self.index = {root: i for i, root in enumerate(self.roots)}
        frame = []
        for i in range(0, 8, 2):
            for sign in (1, -1):
                vector = [0] * 8
                vector[i], vector[i + 1] = 2, 2 * sign
                frame.append(tuple(vector))
        self.frame = frame
        self.frame_ids = tuple(self.index[vector] for vector in frame)
        frame_set = set(self.frame_ids)
        self.pids = tuple(i for i in range(120) if i not in frame_set)
        self.pmask = bits(self.pids)
        require(len(self.pids) == 112, "P112 puncture count")
        require(all(dot(frame[i], frame[j]) == (8 if i == j else 0)
                    for i in range(8) for j in range(8)), "canonical frame")

        self.dots = [[dot(a, b) for b in self.roots] for a in self.roots]
        require(all(value % 4 == 0 for row in self.dots for value in row),
                "Gram entries not divisible by four")
        self.rows = [bits(j for j, value in enumerate(row)
                          if (1 + value // 4) % 2) for row in self.dots]
        require(binary_rank(self.rows) == 9, "Gram pairing rank is not nine")
        column_basis = {}
        selected = []
        for i, row in enumerate(self.rows):
            # Symmetry identifies row i with column i; selection is independent
            # binary elimination on the complete 120-entry columns.
            if binary_insert(row, column_basis):
                selected.append(i)
        require(len(selected) == 9, "nine selected Gram columns")
        self.labels = [sum(((row >> column) & 1) << i
                           for i, column in enumerate(selected))
                       for row in self.rows]
        require(binary_rank(self.labels) == 9, "restricted label rank")
        require(len(set(self.labels)) == 120 and 0 not in self.labels,
                "labels are not distinct nonzero vectors")
        self.label_index = {label: i for i, label in enumerate(self.labels)}
        self.z = [self.labels[i] for i in self.frame_ids]
        affine = [functional for functional in range(1, 1 << 9)
                  if all((functional & label).bit_count() % 2 for label in self.labels)]
        require(len(affine) == 1, "root labels do not have a unique affine-one functional")
        self.affine_functional = affine[0]
        # Equal ranks make the selected-column restriction injective on the
        # full row space.  Thus every checked XOR is an actual Gram-row XOR.
        require(binary_rank(self.rows) == binary_rank(self.labels),
                "label restriction loses row-space information")
        self.hyperplanes = []
        for functional in range(1, 1 << 9):
            mask = bits(i for i, label in enumerate(self.labels)
                        if (functional & label).bit_count() % 2 == 0)
            self.hyperplanes.append((functional, mask & self.pmask))
        self.carrying = [tuple((functional, mask)
                              for functional, mask in self.hyperplanes
                              if (functional & z).bit_count() % 2 == 0)
                         for z in self.z]
        self.incidence = {i: bits(j for j, axis in enumerate(self.frame)
                                 if dot(self.roots[i], axis)) for i in self.pids}
        require(all(mask.bit_count() == 4 for mask in self.incidence.values()),
                "nonframe root does not use four frame axes")
        self.blocks = Counter(self.incidence.values())
        require(len(self.blocks) == 14 and set(self.blocks.values()) == {8},
                "root incidence blocks/sign multiplicity")
        self.record("model", oriented_roots=len(oriented), root_lines=120,
                    frame_lines=8, p112_lines=112, pairing_rank=9,
                    label_columns=selected, affine_one_functional=self.affine_functional,
                    hyperplanes=len(self.hyperplanes))

    def off(self, normal):
        return bits(i for i in self.pids if dot(normal, self.roots[i]))

    @staticmethod
    def minimum_cut(off, hyperplanes):
        count, functional = min(((off & ~mask).bit_count(), functional)
                                for functional, mask in hyperplanes)
        return count, functional

    def design(self):
        require(all(sum((block & bits(triple)) == bits(triple)
                        for block in self.blocks) == 1
                    for triple in combinations(range(8), 3)),
                "incidence blocks are not S(3,4,8)")
        require(all((first & second).bit_count() in (0, 2)
                    for first, second in combinations(self.blocks, 2)),
                "distinct incidence block intersection")
        self.record("design", blocks=14, roots_per_block=8, triples=56)

    def carrier_triples(self):
        pset = set(self.pids)
        triples = 0
        eligible = 0
        triples_per_frame = Counter()
        eligible_per_frame = Counter()
        first_positive = None
        wrong_frame_control = None
        frame_lookup = {label: i for i, label in enumerate(self.z)}
        for a, b in combinations(self.pids, 2):
            for z, frame_index in frame_lookup.items():
                c = self.label_index.get(self.labels[a] ^ self.labels[b] ^ z)
                if c not in pset or c <= b:
                    continue
                triples += 1
                triples_per_frame[frame_index] += 1
                require(self.rows[a] ^ self.rows[b] ^ self.rows[c]
                        == self.rows[self.frame_ids[frame_index]],
                        "restricted XOR does not lift to Gram-row XOR")
                for root, other_a, other_b in ((a, b, c), (b, a, c), (c, a, b)):
                    if self.dots[root][other_a] and self.dots[root][other_b]:
                        eligible += 1
                        eligible_per_frame[frame_index] += 1
                        require(dot(self.frame[frame_index], self.roots[root]) == 0,
                                "pure carrier swap has nonzero own-row evaluation")
                        if first_positive is None:
                            first_positive = [frame_index, a, b, c, root]
                        if wrong_frame_control is None:
                            wrong = next(i for i, axis in enumerate(self.frame)
                                         if dot(axis, self.roots[root]))
                            wrong_frame_control = [wrong, a, b, c, root]
            if a % 8 == 0:
                self.tick()
        require(triples > 0 and eligible > 0, "carrier test is vacuous")
        require(len(triples_per_frame) == 8 and len(set(triples_per_frame.values())) == 1,
                "carrier triple counts are not uniform over the actual frame")
        require(wrong_frame_control is not None, "no wrong-frame carrier control")
        wrong, a, b, c, root = wrong_frame_control
        require(self.labels[a] ^ self.labels[b] ^ self.labels[c] != self.z[wrong],
                "wrong-frame control accidentally satisfies the XOR premise")
        others = [index for index in (a, b, c) if index != root]
        require(all(self.dots[root][index] for index in others)
                and dot(self.frame[wrong], self.roots[root]) != 0,
                "dropping the XOR premise did not create an actual counterexample")
        self.controls["carrier_without_xor_premise_rejected"] = True
        self.record("carrier_triples", triples=triples,
                    eligible_pure_swap_roots=eligible,
                    triples_per_frame=dict(triples_per_frame),
                    eligible_per_frame=dict(eligible_per_frame),
                    positive_witness=first_positive,
                    wrong_frame_counterexample=wrong_frame_control)

    def cuts(self):
        frame_values = []
        for i, normal in enumerate(self.frame):
            off = self.off(normal)
            require(off.bit_count() == 56, "frame support")
            cut, functional = self.minimum_cut(off, self.carrying[i])
            require(cut == 24, "matched-frame carrying remainder is not 24")
            unrestricted, _ = self.minimum_cut(off, self.hyperplanes)
            require(unrestricted == 0, "frame's own uncarrying flat control")
            frame_values.append([i, cut, functional])
        roots_to_check = self.pids if self.mode == "full" else self.pids[:4]
        root_values = []
        for i in roots_to_check:
            off = self.off(self.roots[i])
            require(off.bit_count() == 53, "nonframe root support")
            swap_flat = self.pmask & ~self.rows[i]
            distinguished = [(functional, mask) for functional, mask in self.hyperplanes
                             if mask == swap_flat]
            require(len(distinguished) == 1, "root-swap flat not uniquely represented")
            require((off & ~swap_flat) == 1 << i, "root-swap flat does not leave only self")
            restricted = off & ~(1 << i)
            require((restricted & ~swap_flat) == 0, "restricted root remainder leaves W_r")
            require(binary_rank(self.labels[j] for j in self.pids
                                if restricted >> j & 1) == 8,
                    "restricted root support does not span W_r")
            alternatives = [(functional, mask) for functional, mask in self.hyperplanes
                            if mask != swap_flat]
            restricted_cut, _ = self.minimum_cut(restricted, alternatives)
            require(restricted_cut == 20, "proper-hyperplane cut of restricted support is not 20")
            cut, functional = self.minimum_cut(off, alternatives)
            require(cut == 20, "restricted P112 root remainder is not 20")
            root_values.append([i, cut, functional, distinguished[0][0]])
        self.controls["frame_bound_25_rejected"] = frame_values[0][1] < 25
        self.controls["root_bound_21_rejected"] = root_values[0][1] < 21
        self.controls["unrestricted_root_bound_20_rejected"] = True
        self.record("remainder_cuts", frame_cases=len(frame_values),
                    root_cases=len(root_values), frame_witness=frame_values[0],
                    root_witness=root_values[0], complete=self.mode == "full",
                    root_restriction="exclude the distinguished root-swap flat; its cut is one")

    def axis_checks(self):
        distributions = {}
        normal_cuts = {1: [], 2: [], 3: []}
        all_frame_cuts = {1: [], 2: [], 3: []}
        grid = sorted({primitive(vector) for vector in product(range(-2, 3), repeat=3)
                       if any(vector)})
        grid_count = 0
        unrestricted_norm4 = None
        for size in (1, 2, 3):
            axis_sets = list(combinations(range(8), size))
            if self.mode == "smoke":
                axis_sets = axis_sets[:2]
            signature = None
            for axes in axis_sets:
                form_counts = Counter()
                zero = 0
                for root_index in self.pids:
                    form = tuple(dot(self.roots[root_index], self.frame[i]) // 4
                                 for i in axes)
                    if any(form):
                        form_counts[projective(form)] += 1
                    else:
                        zero += 1
                shape = Counter((sum(bool(x) for x in form), multiplicity)
                                for form, multiplicity in form_counts.items())
                current = (zero, tuple(sorted(shape.items())))
                if signature is None:
                    signature = current
                require(current == signature, "axis form multiplicity varies by axes")
                if size == 3:
                    require(len(form_counts) == 13, "three-axis restricted form count")
                    for coeffs in grid:
                        normal = tuple(sum(coeffs[a] * self.frame[i][coordinate]
                                           for a, i in enumerate(axes))
                                       for coordinate in range(8))
                        actual = self.off(normal).bit_count()
                        formula = sum(multiplicity for form, multiplicity in form_counts.items()
                                      if dot(coeffs, form))
                        require(actual == formula, "three-axis support formula")
                        nonzero = [abs(value) for value in coeffs if value]
                        special = len(set(nonzero)) == 1
                        require(special or actual >= 88,
                                "non-special three-axis normal below support 88")
                        grid_count += 1
                for signs in product((-1, 1), repeat=size - 1):
                    coeffs = (1,) + signs
                    normal = tuple(sum(coeffs[a] * self.frame[i][coordinate]
                                       for a, i in enumerate(axes)) for coordinate in range(8))
                    off = self.off(normal)
                    expected_support = {1: 56, 2: 76, 3: 80}[size]
                    require(off.bit_count() == expected_support, "equal-axis normal support")
                    for matched in range(8):
                        cut, functional = self.minimum_cut(off, self.carrying[matched])
                        threshold = 32 if size == 2 else 24
                        require(cut >= threshold, "matched-axis carrying cut below threshold")
                        all_frame_cuts[size].append(cut)
                        if matched in axes:
                            normal_cuts[size].append([list(axes), list(coeffs), matched,
                                                     cut, functional])
                    if size == 2 and unrestricted_norm4 is None:
                        cut, functional = self.minimum_cut(off, self.hyperplanes)
                        require(cut == 12, "norm4 uncarrying twelve-cut control")
                        require(all((functional & z).bit_count() % 2
                                    for z in self.z),
                                "norm4 exceptional cut carries a frame")
                        unrestricted_norm4 = [list(axes), list(coeffs), cut, functional]
                self.tick()
            distributions[size] = {"axis_sets": len(axis_sets), "zero_roots": signature[0],
                                    "form_shapes": signature[1]}
        self.controls["dropping_matched_frame_premise_rejected"] = (
            unrestricted_norm4 is not None and unrestricted_norm4[2] < 24)
        self.record("restricted_axes", distributions=distributions,
                    coefficient_grid_cases=grid_count,
                    matched_cut_cases={size: len(values) for size, values in normal_cuts.items()},
                    minimum_cuts={size: min(row[3] for row in values)
                                  for size, values in normal_cuts.items()},
                    all_frame_carrying_cut_cases={size: len(values)
                                                 for size, values in all_frame_cuts.items()},
                    all_frame_carrying_minimum={size: min(values)
                                               for size, values in all_frame_cuts.items()},
                    three_axis_support_formula=(
                        "16*sum_i[a_i!=0] + 8*sum_i<j([a_i+a_j!=0]+[a_i-a_j!=0])"
                        " + 2*sum_s,t=+/-1[a_0+s*a_1+t*a_2!=0]"),
                    exceptional_uncarrying_norm4=unrestricted_norm4,
                    complete=self.mode == "full",
                    field_limit="finite form identity; no universal coefficient theorem certified")

    def private_quartets(self):
        by_block = {}
        for root, block in self.incidence.items():
            by_block.setdefault(block, []).append(root)
        complements = 0
        impossible = 0
        raw_sign_choices = 0
        all_axes = (1 << 8) - 1
        for complement_tuple in combinations(range(8), 4):
            complement = bits(complement_tuple)
            private = all_axes ^ complement
            private_axes = [i for i in range(8) if private >> i & 1]
            groups = []
            for axis in private_axes:
                candidates = [block for block in self.blocks
                              if block & private == 1 << axis
                              and (block & complement).bit_count() == 3]
                groups.append(candidates)
            if complement in self.blocks:
                require(not any(groups), "a block complement admits a private quartet")
                impossible += 1
                continue
            require(all(len(group) == 1 for group in groups),
                    "nonblock complement lacks unique private extensions")
            blocks = [group[0] for group in groups]
            common_incidence = all_axes
            sign_choices = 1
            private_pairings = []
            for position, block in enumerate(blocks):
                group = by_block[block]
                sign_choices *= len(group)
                common_incidence &= block
                for root_index in group:
                    # A private diagonal minor certifies independence for
                    # every product choice, without enumerating its 8^4 signs.
                    values = [dot(self.roots[root_index], self.frame[j])
                              for j in private_axes]
                    require(abs(values[position]) == 4
                            and all(value == 0 for j, value in enumerate(values)
                                    if j != position), "private diagonal minor")
                    pairing_view = sum(((self.rows[root_index] >> self.frame_ids[j]) & 1)
                                       << a for a, j in enumerate(private_axes))
                    require(pairing_view == (15 ^ (1 << position)),
                            "private binary pairing is not the complement of a unit")
                private_pairings.append(15 ^ (1 << position))
                require(all(sum(not (candidate >> axis & 1) for candidate in blocks)
                            == (3 if private >> axis & 1 else 1)
                            for axis in range(8)), "private/complement perpendicular counts")
            require(common_incidence == 0, "private quartet has a common frame incidence")
            require(binary_rank(private_pairings) == 4, "private binary pairing minor")
            require(all(sum(((self.rows[frame_id] >> self.frame_ids[j]) & 1) << a
                            for a, j in enumerate(private_axes)) == 15
                        for frame_id in self.frame_ids), "frame private-pairing view")
            # The only subset of the private roots pairing as a frame with
            # these four columns is the full four-root subset.  Its affine
            # functional is zero, whereas every frame's is one.  Thus this
            # certifies frame exclusion from the binary span for all sign
            # products using checked finite inputs, without product sampling.
            matching_subsets = []
            for subset in range(16):
                value = 0
                for i, pairing in enumerate(private_pairings):
                    if subset >> i & 1:
                        value ^= pairing
                if value == 15:
                    matching_subsets.append(subset)
            require(matching_subsets == [15] and (15).bit_count() % 2 == 0,
                    "private frame-exclusion parity certificate")
            require(sign_choices == 8 ** 4, "quartet sign product")
            complements += 1
            raw_sign_choices += sign_choices
        require(complements == 56 and impossible == 14, "private complement split")
        require(raw_sign_choices == 229376, "private quartet raw family size")
        self.controls["block_complement_private_quartet_rejected"] = impossible == 14
        self.record("private_quartets", nonblock_complements=complements,
                    forbidden_block_complements=impossible,
                    sign_products_certified=raw_sign_choices,
                    perpendicular_counts={"private_frame": 3, "complement_frame": 1},
                    private_binary_minor_rank=4,
                    frame_label_in_quartet_span=False,
                    method="all group vectors checked; private diagonal minor certifies products")

    def frame_planes(self):
        # A point is a coloop iff a linear functional is one on that point
        # and zero on all other points.  Enumerating the whole 9-dimensional
        # dual space gives an exact no-coloop test independent of a primal
        # elimination/dependency-mask implementation.
        dual_ones = [(functional, self.pmask & ~mask)
                     for functional, mask in self.hyperplanes]

        def rank(mask):
            return binary_rank(self.labels[i] for i in indices(mask))

        def coloop_witness(mask):
            for functional, ones in dual_ones:
                only = mask & ones
                if only and only & (only - 1) == 0:
                    return functional, only.bit_length() - 1
            return None

        # An independent eight-point set has eight coloops.  This guard
        # catches an erroneously vacuous dual test.
        basis = {}
        independent = []
        for i in self.pids:
            if binary_insert(self.labels[i], basis):
                independent.append(i)
            if len(independent) == 8:
                break
        independent_mask = bits(independent)
        require(rank(independent_mask) == 8 and coloop_witness(independent_mask) is not None,
                "independent-point coloop control did not reject")
        self.controls["independent_eight_point_no_coloop_mutant_rejected"] = True

        pairs = [(j, k) for j in range(8) for k in range(8) if j != k]
        if self.mode == "smoke":
            pairs = pairs[:2]
        strata = (("plus", 1), ("minus", -1), ("generic", 2))
        cache = {}
        checked = 0
        direct_deletions = 0
        for j, k in pairs:
            for stratum, ratio in strata:
                normal = tuple(a + ratio * b for a, b in zip(self.frame[j], self.frame[k]))
                off = self.off(normal)
                for position, (functional, hyperplane) in enumerate(self.carrying[j]):
                    cancelled = off & ~hyperplane
                    if cancelled not in cache:
                        actual_rank = rank(cancelled)
                        witness = coloop_witness(cancelled)
                        require(actual_rank == 8,
                                "nonaxis plane cancellation set has rank other than eight")
                        require(witness is None, "nonaxis plane cancellation set has a coloop")
                        cache[cancelled] = (actual_rank, witness)
                    require(cache[cancelled] == (8, None), "plane-cache value")
                    # Direct one-point deletion is a second local check of
                    # the dual criterion, without making it the full algorithm.
                    if (j, k) == pairs[0] and position < 3:
                        for root_index in indices(cancelled):
                            require(rank(cancelled & ~(1 << root_index)) == 8,
                                    "direct one-point deletion disagrees with dual test")
                            direct_deletions += 1
                    checked += 1
                    if checked % 64 == 0:
                        self.tick()

        # Frame-axis cases genuinely survive the rank test.  Accidentally
        # treating the axis as a nonaxis stratum must therefore be rejected.
        frame_rank_counts = Counter()
        frame_positive = None
        for j, normal in enumerate(self.frame):
            off = self.off(normal)
            for functional, hyperplane in self.carrying[j]:
                cancelled = off & ~hyperplane
                actual_rank = rank(cancelled)
                frame_rank_counts[actual_rank] += 1
                if actual_rank < 8 and frame_positive is None:
                    frame_positive = [j, functional, actual_rank, cancelled.bit_count()]
        require(frame_positive is not None, "no surviving frame-axis positive control")
        self.controls["including_axis_in_nonaxis_strata_rejected"] = True
        expected = len(pairs) * len(strata) * len(self.carrying[0])
        require(checked == expected, "ordered-plane case aggregation")
        self.record("frame_planes", ordered_pairs=len(pairs), nonaxis_strata=3,
                    containing_hyperplanes=len(self.carrying[0]), cases=checked,
                    unique_cancellation_sets=len(cache), rank=8, no_coloops=True,
                    direct_deletion_crosschecks=direct_deletions,
                    frame_axis_rank_counts=dict(frame_rank_counts),
                    frame_axis_positive_control=frame_positive,
                    no_coloop_method="all511 dual functionals; no singleton nonzero evaluation",
                    complete=self.mode == "full")

    def mutation_controls(self):
        # These guards reject genuinely false variants, including removal of
        # a load-bearing hypothesis; they do not merely mirror expected totals.
        rank_losing_labels = [label & ((1 << 8) - 1) for label in self.labels]
        require(binary_rank(rank_losing_labels) == 8
                and binary_rank(rank_losing_labels) < binary_rank(self.rows),
                "column-deletion label control did not lose Gram-row injectivity")
        self.controls["rank_losing_label_map_rejected"] = True
        require(all(self.controls.values()), "a mathematical negative control failed")
        self.record("controls", passed=self.controls.copy())

    def run(self, section):
        selected = {
            "design": self.design,
            "carriers": self.carrier_triples,
            "cuts": self.cuts,
            "axes": self.axis_checks,
            "quartets": self.private_quartets,
            "planes": self.frame_planes,
        }
        if section == "all":
            for operation in selected.values():
                operation()
            self.mutation_controls()
        elif section != "model":
            selected[section]()
        return {"status": "pass", "author": "conorholds", "mode": self.mode,
                "section": section, "elapsed_seconds": round(time.monotonic() - self.started, 6),
                "full_finite_coverage": self.mode == "full" and section == "all",
                "results": self.results,
                "unproved": ["marked invoice and coefficient case analysis",
                             "universal characteristic-zero coefficient classification",
                             "original two-sided branch-reduction/coverage bridge"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("smoke", "full"), default="smoke")
    parser.add_argument("--section", choices=("all", "model", "design", "carriers", "cuts",
                                              "axes", "quartets", "planes"), default="all")
    parser.add_argument("--budget-seconds", type=float, default=8.0)
    args = parser.parse_args()
    if args.budget_seconds <= 0:
        parser.error("budget must be positive")
    try:
        result = Checks(args.mode, args.budget_seconds).run(args.section)
    except (CheckFailure, BudgetExceeded) as error:
        print(json.dumps({"status": "incomplete" if isinstance(error, BudgetExceeded) else "fail",
                          "error": str(error), "mode": args.mode, "section": args.section},
                         sort_keys=True))
        return 2 if isinstance(error, BudgetExceeded) else 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
