#!/usr/bin/env python3
"""Exact corroboration of the arbitrary two-grid selector theorem.

Produced by Nick Petalas. Apache-2.0.
No predecessor implementation is imported or replayed.
"""

from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def periodic_case(h, copies, delta, mask):
    """Compare literal output multiplicities with the selector criterion."""
    require(2 <= h <= 8 and 1 <= copies <= 6, "period outside replay bounds")
    require(-2 * h <= delta <= 2 * h, "increment outside replay bounds")
    require(0 <= mask < (1 << copies), "invalid policy bit mask")
    period = h * copies
    selected = {h * j for j in range(copies) if mask & (1 << j)}
    offset = h - 3
    images = Counter(
        (q + offset + (delta if q in selected else 0)) % period
        for q in range(period)
    )
    injective = max(images.values()) == 1
    closed = all((q + delta) % period in selected for q in selected)
    require(injective == closed, "literal image disagrees with inclusion")
    require(injective == (len(images) == period), "periodic image is not a permutation")
    if selected and delta % h:
        require(not injective, "admission obstruction failed")
        q = min(selected)
        partner = q + delta
        require(partner % h != 0, "collision partner unexpectedly admits coarse input")
        require(q + offset + delta == partner + offset, "wrong collision witness")
    return injective, period, bool(selected and delta % h)


def check_periodic_policies():
    counts = Counter()
    for h in range(2, 9):
        for copies in range(1, 7):
            for delta in range(-2 * h, 2 * h + 1):
                for mask in range(1 << copies):
                    injective, period, obstructed = periodic_case(h, copies, delta, mask)
                    counts["parameter_policy_fixtures"] += 1
                    counts["literal_residue_images"] += period
                    counts["injective_fixtures"] += injective
                    counts["admission_obstructions"] += obstructed
    return dict(counts)


def finite_support_case(h, delta, selected):
    """An exact test on Z when S is finite, not a cyclic wraparound test."""
    require(2 <= h <= 6 and -6 <= delta <= 6, "finite support parameters out of bounds")
    require(all(-6 <= q <= 6 and q % h == 0 for q in selected), "invalid coarse support")
    closed = all(q + delta in selected for q in selected)
    # Every cross-branch collision involves q in S and q+delta. Both are here.
    radius = 6 + abs(delta)
    inputs = range(-radius, radius + 1)
    images = [q + (delta if q in selected else 0) for q in inputs]
    image_set = set(images)
    injective = len(image_set) == len(images)
    require(injective == closed, "nonperiodic image disagrees with inclusion")
    # Every y outside S has the fine preimage y. Only outputs in S need checking.
    surjective = all(q in image_set for q in selected)
    backwards_closed = all(q - delta in selected for q in selected)
    require(surjective == backwards_closed, "literal image disagrees with surjectivity")
    if selected and delta:
        require(not injective, "a nonempty finite set cannot be translation-closed")
    return len(images), injective


def check_finite_supports():
    counts = Counter()
    for h in range(2, 7):
        eligible = tuple(q for q in range(-6, 7) if q % h == 0)
        for size in range(len(eligible) + 1):
            for subset in combinations(eligible, size):
                for delta in range(-6, 7):
                    images, injective = finite_support_case(h, delta, frozenset(subset))
                    counts["finite_support_fixtures"] += 1
                    counts["literal_integer_images"] += images
                    counts["injective_fixtures"] += injective
    return dict(counts)


def check_cited_premise_application():
    """Use PR1845's stated increments as premises, without rechecking them."""
    coarse, fine, h = -10, -11, 2
    delta = coarse - fine
    require(delta % h != 0, "cited application does not meet the obstruction")
    count = 0
    for q in range(-1024, 1025, h):
        partner = q + delta
        require(q % h == 0 and partner % h != 0, "wrong admission classes")
        require(q + coarse == partner + fine, "cited-premise collision failed")
        count += 1
    return {"cited_premise_collision_witnesses": count, "coarse": coarse,
            "fine": fine, "refinement": h, "delta": delta}


def check_controls():
    """Distinguish injectivity, surjectivity, admission and shift orientation."""
    checks = []
    # A legal infinite ray is injective but misses zero. It is not periodic.
    values = [q + (2 if q % 2 == 0 and q >= 0 else 0) for q in range(-64, 65)]
    require(len(set(values)) == len(values) and 0 not in values, "ray control failed")
    checks.append("nonperiodic_injective_nonsurjective")
    # Reversing inclusion gives a collision at 0 and 2.
    values = [q + (2 if q % 2 == 0 and q <= 0 else 0) for q in range(3)]
    require(values[0] == values[2], "orientation control failed")
    checks.append("reversed_inclusion_rejected")
    # Divisible increment difference permits a nonempty, admission-safe policy.
    values = {(q + (2 if q % 2 == 0 else 0)) % 12 for q in range(12)}
    require(values == set(range(12)), "divisible-difference positive control failed")
    checks.append("divisible_difference_attainment")
    # Without coarse admission, S=Z is a translation even for odd delta.
    require(len({q + 1 for q in range(12)}) == 12, "admission-free control failed")
    checks.append("admission_is_essential")
    # Zero increment difference permits any selector, including finite S.
    require(finite_support_case(2, 0, frozenset({0}))[1], "zero difference control failed")
    checks.append("zero_difference")
    require(not periodic_case(2, 2, -1, 1)[0], "negative difference must also obstruct")
    checks.append("negative_difference")
    for args in ((1, 1, 0, 0), (2, 7, 0, 0), (2, 1, 5, 0), (2, 1, 0, 2)):
        try:
            periodic_case(*args)
        except ValueError:
            checks.append("invalid_parameters_" + str(len(checks)))
        else:
            raise ValueError("invalid replay parameter accepted")
    return checks


def file_hashes():
    package = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {}
    for name in names:
        path = package / name
        require(not path.is_symlink() and path.is_file(), "missing or aliased package file")
        require(path.stat().st_size <= 1048576, "package file exceeds replay size bound")
        hashes[name] = sha256(path.read_bytes()).hexdigest()
    return hashes


def main():
    result = {
        "status": "PASS_TWO_GRID_SELECTOR_OBSTRUCTION",
        "claim_type": "scoped written proof with exact finite corroboration",
        "periodic": check_periodic_policies(),
        "finite_support": check_finite_supports(),
        "cited_premise_application": check_cited_premise_application(),
        "controls": check_controls(),
        "files_sha256": file_hashes(),
        "new_kappa": False,
    }
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
