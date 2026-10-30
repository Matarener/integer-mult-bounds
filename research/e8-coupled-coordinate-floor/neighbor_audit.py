"""Exact small-stratum neighbor deletion threshold.

Prepared by conorholds with substantial OpenAI Codex assistance. Apache-2.0.
Imports only the separately written independent E8 model.
No predecessor executable, float arithmetic, external solver, or file write.
Run standalone or through the sequential source-bound package replay.
"""

from collections import Counter
from fractions import Fraction
from functools import reduce
from math import gcd, lcm
import json

from independent_model import root_model, check_model, dot, require, binary_rank


# Exact doubled simple roots from PR3166 verify.py at the pinned source head
# 7c2a62363ad4945e8803fedea6ead78e1ad412b2. The inventory/base property is
# independently checked below; no predecessor executable is imported.
SIMPLE = (
    (1, -1, -1, -1, -1, -1, -1, 1),
    (2, 2, 0, 0, 0, 0, 0, 0),
    (-2, 2, 0, 0, 0, 0, 0, 0),
    (0, -2, 2, 0, 0, 0, 0, 0),
    (0, 0, -2, 2, 0, 0, 0, 0),
    (0, 0, 0, -2, 2, 0, 0, 0),
    (0, 0, 0, 0, -2, 2, 0, 0),
    (0, 0, 0, 0, 0, -2, 2, 0),
)


def primitive(vector):
    """Canonical integer representative of a nonzero rational ray."""
    vector = tuple(Fraction(x) for x in vector)
    require(any(vector), "zero ray")
    scale = lcm(*(x.denominator for x in vector))
    integers = tuple(int(x * scale) for x in vector)
    divisor = reduce(gcd, (abs(x) for x in integers))
    sign = 1 if next(x for x in integers if x) > 0 else -1
    return tuple(sign * x // divisor for x in integers)


def nullspace(rows, width=8):
    """Exact echelon elimination plus back-substitution over Q."""
    echelon = {}
    for original in rows:
        work = [Fraction(x) for x in original]
        for pivot, old in sorted(echelon.items()):
            coefficient = work[pivot]
            if coefficient:
                work = [x - coefficient * y for x, y in zip(work, old)]
        pivot = next((i for i, x in enumerate(work) if x), None)
        if pivot is not None:
            factor = work[pivot]
            echelon[pivot] = tuple(x / factor for x in work)
    result = []
    for free in range(width):
        if free in echelon:
            continue
        vector = [Fraction(0)] * width
        vector[free] = Fraction(1)
        for pivot, row in sorted(echelon.items(), reverse=True):
            vector[pivot] = -sum(row[j] * vector[j]
                                 for j in range(pivot + 1, width))
        integer = primitive(vector)
        require(all(dot(row, integer) == 0 for row in rows), "kernel witness")
        result.append(integer)
    require(len(result) + len(echelon) == width, "kernel rank-nullity")
    return tuple(result)


def combine(left, right, s, t):
    return primitive(tuple(s * x + t * y for x, y in zip(left, right)))


def parabolic_neighbor_certificate(rows, labels):
    """All proper standard parabolics versus all 120 neighbor stars.

    Every rational hyperplane root intersection is Weyl-conjugate to one
    of these parabolics. Exclude exactly the rank-seven E7 intersections,
    since their scalar perpendicular is a root ray. All remaining proper
    parabolics can occur as the exact zero set of a nonroot normal.
    """
    root_rays = {primitive(row): index for index, row in enumerate(rows)}
    require(not nullspace(SIMPLE), "simple roots form a scalar basis")
    require(all(primitive(row) in root_rays for row in SIMPLE), "simple root inventory")
    require(all(dot(row, row) == 8 for row in SIMPLE), "simple root norms")
    require(all(dot(a, b) in (0, -4) for i, a in enumerate(SIMPLE)
                for j, b in enumerate(SIMPLE) if i != j), "simple Cartan off-diagonal")
    dual_normals = []
    for omitted in range(8):
        kernel = nullspace([row for i, row in enumerate(SIMPLE) if i != omitted])
        require(len(kernel) == 1 and dot(SIMPLE[omitted], kernel[0]) != 0,
                "simple dual coordinate")
        dual_normals.append(kernel[0])
    coordinates = []
    for row in rows:
        coordinate = tuple(Fraction(dot(row, normal), dot(simple, normal))
                           for simple, normal in zip(SIMPLE, dual_normals))
        require(all(value.denominator == 1 for value in coordinate),
                "root has integral simple coordinates")
        require(all(value >= 0 for value in coordinate)
                or all(value <= 0 for value in coordinate), "simple positive-root base")
        require(all(sum(coordinate[i] * SIMPLE[i][j] for i in range(8)) == row[j]
                    for j in range(8)), "simple-coordinate reconstruction")
        coordinates.append(coordinate)
    neighbor_masks = [sum(1 << j for j, other in enumerate(rows)
                          if i != j and dot(row, other) != 0)
                      for i, row in enumerate(rows)]
    require(all(mask.bit_count() == 56 for mask in neighbor_masks), "all neighbor stars")
    reports = []
    excluded_e7 = []
    maximum = -1
    attaining = None
    size_histogram = Counter()
    for subset in range(255):
        selected_simple = [row for i, row in enumerate(SIMPLE) if subset >> i & 1]
        kernel = nullspace(selected_simple)
        rank = subset.bit_count()
        require(len(kernel) == 8 - rank, "parabolic scalar rank")
        selected = [i for i, row in enumerate(rows)
                    if all(dot(row, normal) == 0 for normal in kernel)]
        require(selected == [i for i, coordinate in enumerate(coordinates)
                             if all(not value or subset >> j & 1
                                    for j, value in enumerate(coordinate))],
                "independent parabolic membership formulations")
        root_normal = (root_rays.get(primitive(kernel[0])) if rank == 7 else None)
        if rank == 7 and len(selected) == 63:
            require(root_normal is not None, "E7 perpendicular is a root line")
            excluded_e7.append({"subset": subset, "normal_root": root_normal})
            continue
        require(root_normal is None, "unexpected root-normal proper parabolic")
        size_histogram[(rank, len(selected))] += 1
        mask = sum(1 << i for i in selected)
        intersections = [(mask & neighbors).bit_count() for neighbors in neighbor_masks]
        largest = max(intersections)
        arg_root = intersections.index(largest)
        reports.append({"subset": subset, "rank": rank, "root_lines": len(selected),
                        "maximum_neighbor_intersection": largest,
                        "arg_root": arg_root})
        if largest > maximum:
            maximum = largest
            attaining = (subset, arg_root, kernel, selected)
    require(len(reports) + len(excluded_e7) == 255, "all proper parabolics")
    require(excluded_e7, "rank-seven root-normal parabolic present")
    subset, arg_root, kernel, selected = attaining
    selected_set = set(selected)
    dimension = len(kernel)
    # A generic moment-curve normal avoids every root outside the subsystem:
    # each such row is a nonzero polynomial in t of degree <=dimension-1.
    # Thus at most (120-|selected|)*(dimension-1) rational t are forbidden.
    normal = None
    trial_bound = (120 - len(selected)) * (dimension - 1) + 1
    for t in range(trial_bound):
        candidate = primitive(tuple(sum((t ** i) * basis[j]
                                        for i, basis in enumerate(kernel))
                                    for j in range(8)))
        zero_roots = {i for i, row in enumerate(rows) if dot(row, candidate) == 0}
        if zero_roots == selected_set:
            normal = candidate
            break
    require(normal is not None and normal not in root_rays, "generic nonroot parabolic witness")
    deletion = [i for i, row in enumerate(rows)
                if neighbor_masks[arg_root] >> i & 1 and dot(row, normal)]
    require(len(deletion) == 56 - maximum, "attained complement-character distance")
    return {"proper_parabolics": 255, "included_parabolics": len(reports),
            "excluded_E7": excluded_e7, "all_root_positions": 120,
            "maximum_nonroot_zero_neighbor_intersection": maximum,
            "minimum_nonroot_neighbor_support": 56 - maximum,
            "attaining_witness": {"subset": subset, "fixed_root": arg_root,
                                   "normal": normal, "deletion_roots": deletion,
                                   "character": 511 ^ labels[arg_root]},
            "parabolic_size_histogram": [
                {"rank": rank, "root_lines": size, "multiplicity": count}
                for (rank, size), count in sorted(size_histogram.items())],
            "parabolic_neighbor_maxima": reports}


def transport_certificate(rows, labels, fixed):
    """Root-graph connectivity plus exact reflections proves all-v transport.

    An edge r,w with |(r,w)|=1 is transported by reflection in r-sign*w,
    another E8 root. Closure on all root rays is checked for each reflector
    used by a spanning tree. Orthogonal reflections preserve integer Gram,
    hence B_d. Since labels span a nondegenerate rank-nine pairing space,
    each such B_d-preserving permutation induces an invertible binary
    isometry on their span and therefore permutes all 511 characters.
    """
    rays = {primitive(row): i for i, row in enumerate(rows)}
    seen, queue, edges, reflectors = {fixed}, [fixed], [], {}
    for parent in queue:
        for child, other in enumerate(rows):
            gram = dot(rows[parent], other)
            if child in seen or abs(gram) != 4:
                continue
            sign = 1 if gram > 0 else -1
            alpha = tuple(x - sign * y for x, y in zip(rows[parent], other))
            require(dot(alpha, alpha) == 8 and primitive(alpha) in rays,
                    "connecting reflection is an E8 root")
            alpha = rows[rays[primitive(alpha)]]
            key = primitive(alpha)
            if key not in reflectors:
                permutation = []
                for row in rows:
                    product = dot(row, alpha)
                    require(product % 4 == 0, "integral root reflection")
                    reflected = tuple(x - (product // 4) * a
                                      for x, a in zip(row, alpha))
                    require(dot(reflected, reflected) == 8, "reflection norm")
                    require(primitive(reflected) in rays, "root-set reflection closure")
                    permutation.append(rays[primitive(reflected)])
                require(len(set(permutation)) == 120, "reflection permutation")
                reflectors[key] = permutation
            permutation = reflectors[key]
            require(permutation[parent] == child, "connecting reflection image")
            # The scalar reflection is an isometry by its norm-two formula;
            # check its label pairing with all roots at the transported edge.
            for x in range(120):
                before = (labels[parent] & labels[x]).bit_count() % 2
                after = (labels[child] & labels[permutation[x]]).bit_count() % 2
                require(before == after, "edge binary-pairing transport")
            seen.add(child)
            queue.append(child)
            edges.append([parent, child, rays[key]])
    require(len(seen) == 120 and len(edges) == 119, "root transitivity certificate")
    return {"root_tree_edges": edges, "distinct_reflections": len(reflectors),
            "reflection_root_image_checks": 120 * len(reflectors)}


def classification_boundary_control(rows, labels):
    """A 24-neighbor word refuting eligible-root-only classification there.

    This is a scalar word, not an all-pairs decoder or a COPY counterexample.
    Doubled standard rows R give E(r_v)(x)=dot(R_x,R_v)/4.
    """
    fixed, character = 0, 12
    negative = (1, 2, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53)
    positive = (8, 9, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74)
    expected = set(negative) | set(positive)
    require(rows[fixed] == (0, 2, -2, 0, 0, 0, 0, 0)
            and labels[fixed] == 508, "boundary model/orientation binding")
    oz = {i for i, label in enumerate(labels) if (label & character).bit_count() % 2}
    deleted = {i for i in oz if dot(rows[i], rows[fixed])}
    require(deleted == expected and len(deleted) == 24, "exact boundary deleted set")
    require(fixed not in deleted and fixed not in oz, "root's own site is uncorrected")
    require(all(i != fixed and dot(rows[i], rows[fixed]) != 0 for i in deleted),
            "all boundary correction sites are nonself neighbors")
    code = [Fraction(dot(row, rows[fixed]), 4) for row in rows]
    require(code[fixed] == 2, "norm-two self value / doubled-row scale")
    require(all(code[i] == 1 for i in negative)
            and all(code[i] == -1 for i in positive), "boundary correction signs")
    correction = [-1 if i in negative else 1 if i in positive else 0 for i in range(120)]
    word = [value + delta for value, delta in zip(code, correction)]
    require(all(word[i] == 0 for i in oz), "boundary character annihilates corrected word")
    require(word[fixed] == 2 and correction[fixed] == 0,
            "boundary word is not an eligible own-root hole")
    weight = binary_rank(label for value, label in zip(word, labels) if value)
    require(weight <= 8, "boundary word is binary-deficient")
    return {"fixed_root": fixed, "character": character, "negative_correction_indices": negative,
            "positive_correction_indices": positive, "deletion_count": 24,
            "own_root_value": 2, "own_root_correction": 0, "binary_weight": weight,
            "scope": "eligible-root classification boundary; not an exact decoder"}


def calculate(fixed=0, include_details=True):
    rows, labels = root_model()
    check_model(rows, labels)
    require(0 <= fixed < 120, "fixed root index")
    root_rays = {primitive(row): index for index, row in enumerate(rows)}
    ov = [i for i, label in enumerate(labels)
          if (label & labels[fixed]).bit_count() % 2]
    hv = set(range(120)) - set(ov)
    require(len(ov) == 64 and len(hv) == 56, "root character support/remainder")
    kernel_histogram = Counter()
    critical_histogram = Counter()
    generic_histogram = Counter()
    nonroot_minimum = None
    minimum_witnesses = []
    root_mismatch_minimum = None
    root_match_cases = 0
    characters = []
    complement_character = 511 ^ labels[fixed]
    complement_report = None

    def record_nonroot(count, witness):
        nonlocal nonroot_minimum, minimum_witnesses
        if nonroot_minimum is None or count < nonroot_minimum:
            nonroot_minimum, minimum_witnesses = count, [witness]
        elif count == nonroot_minimum:
            minimum_witnesses.append(witness)

    for z in range(1, 512):
        oz = [i for i, label in enumerate(labels) if (label & z).bit_count() % 2]
        forced = [i for i in ov if (labels[i] & z).bit_count() % 2]
        basis = nullspace([rows[i] for i in forced])
        dimension = len(basis)
        kernel_histogram[dimension] += 1
        report = {"character": z, "forced_zero_roots": len(forced),
                  "kernel_dimension": dimension, "kernel_basis": basis,
                  "critical_rays": []}
        if dimension > 2:
            require(dimension == 8 and z == complement_character
                    and not forced and set(oz) == hv,
                    "unclassified large kernel is not the verified complement character")
            require(complement_report is None, "multiple complement-character kernels")
            certificate = parabolic_neighbor_certificate(rows, labels)
            report["special_case"] = "complement character; all proper parabolic zero sets"
            report["minimum_nonroot_deletions"] = certificate["minimum_nonroot_neighbor_support"]
            report["parabolic_certificate"] = certificate
            complement_report = report
            witness = dict(certificate["attaining_witness"])
            witness["stratum"] = "complement_parabolic_all_root_positions"
            record_nonroot(certificate["minimum_nonroot_neighbor_support"], witness)
            characters.append(report)
            continue
        if not dimension:
            characters.append(report)
            continue

        if dimension == 1:
            critical_normals = [primitive(basis[0])]
            generic = None
        else:
            forms = [(dot(rows[i], basis[0]), dot(rows[i], basis[1])) for i in oz]
            distinct_forms = {primitive(form) for form in forms if any(form)}
            critical_normals = sorted({combine(basis[0], basis[1], form[1], -form[0])
                                       for form in distinct_forms})
            # A generic rational nonroot ray exists off the finitely many
            # critical and root rays. Testing (1,t) has at most one forbidden
            # t for each critical ray and each of the 120 root rays.
            generic = None
            for t in range(len(distinct_forms) + len(root_rays) + 1):
                normal = combine(basis[0], basis[1], 1, t)
                if normal in root_rays:
                    continue
                if any(s + t * u == 0 for s, u in forms if s or u):
                    continue
                generic = normal
                break
            require(generic is not None, "generic nonroot rational witness")
            generic_count = sum(any(form) for form in forms)
            generic_actual = [i for i in oz if dot(rows[i], generic)]
            require(len(generic_actual) == generic_count, "generic support stratum")
            require(set(generic_actual) <= hv, "generic deletion is neighbor-supported")
            generic_histogram[generic_count] += 1
            report["generic"] = {"normal": generic, "deletion_count": generic_count}
            record_nonroot(generic_count, {"character": z, "stratum": "generic",
                                          "normal": generic,
                                          "deletion_roots": generic_actual})

        for normal in critical_normals:
            deletion = [i for i in oz if dot(rows[i], normal)]
            require(set(deletion) <= hv, "critical deletion is neighbor-supported")
            root_index = root_rays.get(normal)
            critical_histogram[(dimension, root_index is not None, len(deletion))] += 1
            detail = {"normal": normal, "deletion_count": len(deletion),
                      "root_line": root_index}
            report["critical_rays"].append(detail)
            if root_index is None:
                record_nonroot(len(deletion), {"character": z, "stratum": "critical",
                                              "normal": normal,
                                              "deletion_roots": deletion})
            elif z == labels[root_index]:
                require(deletion == [root_index], "matching root single-hole cut")
                require(root_index in hv, "matching root is a nonself neighbor")
                root_match_cases += 1
            else:
                root_mismatch_minimum = (len(deletion) if root_mismatch_minimum is None
                                         else min(root_mismatch_minimum, len(deletion)))
        characters.append(report)

    require(sum(kernel_histogram.values()) == 511, "all nonzero characters covered")
    require(complement_report is not None, "verified complement character covered")
    result = {"fixed_root": fixed, "fixed_label": labels[fixed],
              "root_lines": 120, "characters": 511,
              "kernel_dimension_histogram": dict(sorted(kernel_histogram.items())),
              "critical_stratum_histogram": [
                  {"kernel_dimension": d, "is_root": root, "deletion_count": count,
                   "multiplicity": multiplicity}
                  for (d, root, count), multiplicity in sorted(critical_histogram.items())],
              "generic_nonroot_histogram": dict(sorted(generic_histogram.items())),
              "minimum_nonroot_neighbor_deletions": nonroot_minimum,
              "minimum_nonroot_witnesses": minimum_witnesses,
              "minimum_critical_root_mismatch_deletions": root_mismatch_minimum,
              "matching_root_cases": root_match_cases,
              "root_mismatch_uniform_source_lower_bound": 24,
              "special_complement_character": complement_character,
              "complement_nonroot_minimum": complement_report["minimum_nonroot_deletions"],
              "classification_boundary_control": classification_boundary_control(rows, labels),
              "transport": transport_certificate(rows, labels, fixed)}
    if include_details:
        result["character_strata"] = characters
    return result


if __name__ == "__main__":
    print(json.dumps(calculate(), indent=2, sort_keys=True))


def low_weight_calculate():
    """Complete full-support strata for every possible two-annihilator word."""
    rows, labels = root_model()
    check_model(rows, labels)
    v = 0
    ov = {i for i, u in enumerate(labels) if (u & labels[v]).bit_count() % 2}
    hv = set(range(120)) - ov
    oz = [0] + [sum((1 << i for i, u in enumerate(labels) if (u & z).bit_count() % 2)) for z in range(1, 512)]
    complement = 511 ^ labels[v]
    root_rays = {primitive(r): i for i, r in enumerate(rows)}
    candidates = {}
    kernels = Counter()
    for z in range(1, 512):
        if z == complement:
            continue
        forced = [rows[i] for i in ov if oz[z] >> i & 1]
        basis = nullspace(forced)
        kernels[len(basis)] += 1
        require(len(basis) <= 2, 'only complement may have large kernel')
        if not basis:
            continue
        if len(basis) == 1:
            normals = [primitive(basis[0])]
        else:
            forms = [(dot(row, basis[0]), dot(row, basis[1])) for row in rows]
            distinct = {primitive(form) for form in forms if any(form)}
            normals = [combine(basis[0], basis[1], f[1], -f[0]) for f in distinct]
            for t in range(len(distinct) + 121):
                n = combine(basis[0], basis[1], 1, t)
                if n not in root_rays and all((a + t * b for a, b in distinct)):
                    break
            else:
                raise ValueError('generic witness not found')
            normals.append(n)
        for normal in normals:
            off = sum((1 << i for i, r in enumerate(rows) if dot(r, normal)))
            candidates.setdefault(off, normal)
    minima = {'root': 121, 'nonroot': 121}
    witnesses = {}
    eligible = Counter()
    planes = 0
    for off, normal in candidates.items():
        forced = sum((1 << i for i in ov if off >> i & 1))
        allowed = [z for z in range(1, 512) if not forced & oz[z]]
        kind = 'root' if normal in root_rays else 'nonroot'
        eligible[kind, len(allowed)] += 1
        seen = set()
        for z in allowed:
            for t in allowed:
                if z >= t:
                    continue
                key = tuple(sorted((z, t, z ^ t)))
                if key in seen:
                    continue
                seen.add(key)
                planes += 1
                deleted = off & (oz[z] | oz[t])
                count = deleted.bit_count()
                if count < minima[kind]:
                    minima[kind] = count
                    witnesses[kind] = {'normal': normal, 'root': root_rays.get(normal), 'characters': key, 'deleted': [i for i in range(120) if deleted >> i & 1]}
    require(dict(kernels) == {0: 256, 1: 198, 2: 56}, 'all noncomplement character kernels covered')
    require(len(candidates) == 169 and planes == 10963, 'complete two-annihilator support strata')
    require(minima == {'root': 29, 'nonroot': 55}, 'sharp mixed low-weight thresholds')
    for kind, witness in witnesses.items():
        normal = witness['normal']
        deleted = set(witness['deleted'])
        support = [i for i, row in enumerate(rows) if dot(row, normal) and i not in deleted]
        require(binary_rank((labels[i] for i in support)) == 7, 'attaining low-word support rank')
    return {'candidates': len(candidates), 'kernels': dict(kernels), 'eligible_patterns': [{'kind': k, 'characters': n, 'patterns': m} for (k, n), m in sorted(eligible.items())], 'planes': planes, 'minima': minima, 'witnesses': witnesses}
