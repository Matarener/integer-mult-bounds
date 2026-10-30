#!/usr/bin/env python3
"""Exact certificate for the declared Fano coordinate-cut cone.

Produced by Nick Petalas. Apache-2.0.
No solver, predecessor executable, network, Git or output file is needed.
"""

import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path


IDENTITY = (1, 2, 4)
TARGET = (7, 1, 3)
LABELS = tuple((i, j) for i in range(3) for j in range(3) if i != j)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def apply(matrix, vector):
    value = 0
    for i in range(3):
        if vector >> i & 1:
            value ^= matrix[i]
    return value


def multiply(left, right):
    return tuple(apply(left, column) for column in right)


def generators():
    result = []
    for i, j in LABELS:
        columns = list(IDENTITY)
        columns[j] ^= 1 << i
        result.append(tuple(columns))
    return tuple(result)


def point_action(matrix):
    return tuple(apply(matrix, x) - 1 for x in range(1, 8))


def inverse(matrix):
    action = point_action(matrix)
    need(sorted(action) == list(range(7)), "matrix is singular")
    return tuple(action.index(x - 1) + 1 for x in IDENTITY)


def line_action(matrix):
    inv = inverse(matrix)
    return tuple(sum(((inv[k] & x).bit_count() % 2) << k
                     for k in range(3)) - 1 for x in range(1, 8))


def crossing(action, mask):
    need(0 <= mask < 128, "cut mask out of range")
    return sum((mask >> x & 1) and not (mask >> action[x] & 1)
               for x in range(7))


def all_group_elements(gens):
    group = tuple(a for a in itertools.product(range(1, 8), repeat=3)
                  if len({apply(a, x) for x in range(1, 8)}) == 7)
    need(len(group) == 168, "wrong GL3 order")
    words = {IDENTITY: ()}
    frontier = [IDENTITY]
    for _ in range(7):
        following = []
        for matrix in frontier:
            for label, gen in enumerate(gens):
                product = multiply(gen, matrix)
                if product not in words:
                    words[product] = words[matrix] + (label,)
                    following.append(product)
        frontier = following
    need(set(words) == set(group), "incomplete Cayley traversal")
    need(len(words[TARGET]) == 4, "target distance changed")
    power = IDENTITY
    for _ in range(7):
        power = multiply(TARGET, power)
    need(power == IDENTITY and TARGET != IDENTITY, "target order is not seven")
    return group, words[TARGET]


def check_actions(group):
    """Compare columns to an independently evaluated row/dot-product action."""
    points = {}
    lines = {}
    for matrix in group:
        rows = tuple(sum(((matrix[j] >> i) & 1) << j for j in range(3))
                     for i in range(3))
        alternate = tuple(sum(((row & x).bit_count() % 2) << i
                              for i, row in enumerate(rows)) - 1
                          for x in range(1, 8))
        points[matrix] = point_action(matrix)
        lines[matrix] = line_action(matrix)
        need(points[matrix] == alternate, "row/column action disagreement")
        # Orthogonality identifies each line without a transpose convention.
        for normal in range(1, 8):
            members = {x - 1 for x in range(1, 8)
                       if (normal & x).bit_count() % 2 == 0}
            image = {points[matrix][x] for x in members}
            new_normal = lines[matrix][normal - 1] + 1
            expected = {x - 1 for x in range(1, 8)
                        if (new_normal & x).bit_count() % 2 == 0}
            need(image == expected, "point/line incidence disagreement")
    for left, right in itertools.product(group, repeat=2):
        product = multiply(left, right)
        for actions in (points, lines):
            need(actions[product] == tuple(actions[left][x]
                                          for x in actions[right]),
                 "action is not a homomorphism")
    return points, lines


def cut_certificate(gens, actions):
    profiles = []
    histograms = []
    for action in actions:
        histogram = Counter()
        for mask in range(128):
            paid = tuple(crossing(action[g], mask) for g in gens)
            target = crossing(action[TARGET], mask)
            slack = sum(paid) - 2 * target
            need(slack >= 0, "dual certificate violated")
            need(crossing(action[inverse(TARGET)], mask) == target,
                 "inverse target changes the cut")
            complement = mask ^ 127
            need(crossing(action[TARGET], complement) == target,
                 "complement symmetry violated")
            profiles.append([mask, list(paid), target, slack])
            histogram[slack] += 1
        histograms.append(dict(sorted(histogram.items())))
    point = profiles[42]
    line = profiles[128 + 10]
    need(point[1:] == [[2, 2, 0, 0, 0, 0], 2, 0], "point primal changed")
    need(line[1:] == [[0, 0, 1, 1, 1, 1], 2, 0], "line primal changed")
    need(all(point[1][i] + 2 * line[1][i] == 2 for i in range(6)),
         "primal exceeds a paid budget")
    need(point[2] + 2 * line[2] == 6, "primal value is not three")
    return profiles, histograms


def binary_rank(rows):
    pivots = {}
    for row in rows:
        for _ in range(21):
            if not row:
                break
            pivot = row.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = row
                break
            row ^= pivots[pivot]
        else:
            raise ValueError("rank elimination exceeded capacity")
    return len(pivots)


def paid_block(action, mask, u, v, width):
    rows = []
    for role in range(width):
        for address in range(7):
            if mask >> address & 1:
                continue
            row = 0
            for source in range(7):
                if (mask >> source & 1 and action[source] == address
                        and u >> role & 1):
                    for donor in range(width):
                        if v >> donor & 1:
                            row |= 1 << (7 * donor + source)
            rows.append(row)
    return rows


def check_paid_blocks(gens, actions):
    """Test actual crossing matrices, rather than only the rank formula."""
    count = 0
    projectors = 0
    for width in range(1, 4):
        for u, v in itertools.product(range(1, 1 << width), repeat=2):
            if (u & v).bit_count() % 2 != 1:
                continue
            projectors += 1
            for action in actions:
                for gen in gens:
                    for mask in (0, 10, 42, 85, 117, 127):
                        rows = paid_block(action[gen], mask, u, v, width)
                        need(binary_rank(rows) == crossing(action[gen], mask),
                             "paid tensor crossing rank mismatch")
                        count += 1
    need(projectors == 35, "projector domain incomplete")
    return count


def scalar_multiply(left, right, width):
    rows = []
    for row in left:
        output = 0
        for j in range(width):
            if row >> j & 1:
                output ^= right[j]
        rows.append(output)
    return tuple(rows)


def formal_multiply(left, right, width):
    result = {}
    for a, b in itertools.product(left, right):
        product = multiply(a, b)
        value = scalar_multiply(left[a], right[b], width)
        previous = result.get(product, (0,) * width)
        result[product] = tuple(x ^ y for x, y in zip(previous, value))
    return {a: rows for a, rows in result.items() if any(rows)}


def formal_word(word, width):
    unit = tuple(1 << i for i in range(width))
    value = {IDENTITY: unit}
    for gen, projector in word:
        at_identity = tuple(x ^ y for x, y in zip(unit, projector))
        factor = {IDENTITY: at_identity, gen: projector}
        value = formal_multiply(factor, value, width)
    return value


def check_formal_endpoints(gens, word):
    omissions = 0
    for targets in range(1, 4):
        width = targets + 1
        circuit = []
        for role in range(targets):
            projector = tuple(1 << role if i == role else 0 for i in range(width))
            circuit.extend((gens[label], projector) for label in word)
        expected = {TARGET: tuple(1 << i if i < targets else 0
                                  for i in range(width)),
                    IDENTITY: tuple(1 << i if i == targets else 0
                                    for i in range(width))}
        need(formal_word(circuit, width) == expected, "direct endpoint failed")
        for omitted in range(len(circuit)):
            altered = circuit[:omitted] + circuit[omitted + 1:]
            need(formal_word(altered, width) != expected, "missing call accepted")
            omissions += 1
        # This projector writes an arbitrary source into a dirty spectator.
        dirty = tuple(1 if i in (0, targets) else 0 for i in range(width))
        detour = [(gens[0], dirty)] * 2
        need(formal_word(detour + circuit, width) == expected,
             "dirty spectator not restored")
        need(formal_word(detour[:1] + circuit, width) != expected,
             "dirty leakage accepted")
    return omissions


def boundary_controls():
    for mask in (-1, 128, 256):
        try:
            crossing(tuple(range(7)), mask)
        except ValueError:
            continue
        raise ValueError("invalid mask accepted")
    try:
        inverse((1, 1, 4))
    except ValueError:
        pass
    else:
        raise ValueError("singular inverse accepted")
    return 4


def source_and_package_hashes():
    package = Path(__file__).resolve().parent
    root = package.parents[1]
    sources = json.loads((package / "SOURCES.json").read_text())
    source_hashes = {}
    for entry in sources["files"]:
        if entry["usage"] != "input":
            continue
        digest = hashlib.sha256((root / entry["path"]).read_bytes()).hexdigest()
        need(digest == entry["sha256"], "changed source: " + entry["path"])
        source_hashes[entry["path"]] = digest
    package_hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in sorted(package.iterdir()) if p.is_file()}
    return source_hashes, package_hashes


def main():
    sources, package = source_and_package_hashes()
    gens = generators()
    group, word = all_group_elements(gens)
    actions = check_actions(group)
    profiles, histograms = cut_certificate(gens, actions)
    blocks = check_paid_blocks(gens, actions)
    omissions = check_formal_endpoints(gens, word)
    payload = {
        "status": "PASS_GL3_SINGER_CUT_GAP",
        "claim_type": "scoped proof with finite cut certificate",
        "target_columns": TARGET,
        "group_order": len(group),
        "cut_count": len(profiles),
        "cut_slack_histograms": histograms,
        "cut_profiles_sha256": hashlib.sha256(json.dumps(profiles).encode()).hexdigest(),
        "action_composition_checks": 2 * len(group) ** 2,
        "point_line_incidence_checks": 7 * len(group),
        "paid_crossing_blocks": blocks,
        "direct_word": [LABELS[i] for i in word],
        "direct_distance": len(word),
        "cone_value_per_target": 3,
        "omitted_call_controls": omissions,
        "boundary_controls": boundary_controls(),
        "source_sha256": sources,
        "package_sha256": package,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
