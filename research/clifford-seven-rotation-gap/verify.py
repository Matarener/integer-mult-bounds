"""Exact finite corroboration of the seven-rotation spectral argument.

No predecessor executable is imported or run. The all-dimension theorem is
the written proof; these fixed finite checks test its new local ingredients.
"""

from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import sys


PACKAGE = Path(__file__).resolve().parent
REAL = (1, 0, -1, 0)
PACKAGE_FILES = (
    "README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def symplectic(u: int, v: int) -> int:
    return (((u & 7) & (v >> 3)) ^ ((u >> 3) & (v & 7))).bit_count() % 2


def span(basis: tuple[int, int, int]) -> tuple[int, ...]:
    a, b, c = basis
    return tuple(sorted((a, b, c, a ^ b, a ^ c, b ^ c, a ^ b ^ c)))


def isotropic_spaces() -> dict[tuple[int, ...], tuple[int, int, int]]:
    spaces = {}
    # Exactly C(63,3)=39711 candidate triples; no larger domain is accepted.
    for basis in combinations(range(1, 64), 3):
        points = span(basis)
        if len(set(points)) != 7 or 0 in points:
            continue
        if any(symplectic(u, v) for u, v in combinations(basis, 2)):
            continue
        spaces.setdefault(points, basis)
        require(len(spaces) <= 135, "space capacity exceeded")
    incidences = Counter(v for points in spaces for v in points)
    require(len(spaces) == 135, "isotropic-space census")
    require(incidences == Counter({v: 15 for v in range(1, 64)}), "nonuniform incidence")
    return spaces


def pauli(label: int) -> tuple[int, int, int]:
    x, z = label & 7, label >> 3
    return x, z, (x & z).bit_count() % 4


def multiply(a: tuple[int, int, int], b: tuple[int, int, int]) -> tuple[int, int, int]:
    x, z, phase = a
    xx, zz, pp = b
    return x ^ xx, z ^ zz, (phase + pp + 2 * (z & xx).bit_count()) % 4


def signed_axes(basis: tuple[int, int, int]) -> tuple[tuple[int, int, int], ...]:
    axes = []
    for mask in range(1, 8):
        value = (0, 0, 0)
        for j in range(3):
            if mask & (1 << j):
                value = multiply(value, pauli(basis[j]))
        require(multiply(value, value) == (0, 0, 0), "non-Hermitian axis")
        axes.append(value)
    return tuple(axes)


def rotate(value: tuple[int, int], phase: int) -> tuple[int, int]:
    a, b = value
    return ((a, b), (-b, a), (-a, -b), (b, -a))[phase % 4]


def turn(vector: list[tuple[int, int]], axis: tuple[int, int, int]) -> list[tuple[int, int]]:
    """Apply 2 C_P with Gaussian integers, so denominators stay explicit."""
    x, z, phase = axis
    result = [(a - b, a + b) for a, b in vector]
    for column in range(8):
        a, b = rotate(vector[column], phase + 2 * (z & column).bit_count())
        c, d = result[column ^ x]
        result[column ^ x] = c + a + b, d + b - a
    return result


def is_identity_word(axes: tuple[tuple[int, int, int], ...]) -> bool:
    require(len(axes) <= 7, "word exceeds seven rotations")
    for column in range(8):
        vector = [(int(row == column), 0) for row in range(8)]
        for axis in axes:
            vector = turn(vector, axis)
        expected = [(int(row == column) * 2 ** len(axes), 0) for row in range(8)]
        if vector != expected:
            return False
    return True


def literal_relations(spaces: dict) -> tuple[int, int]:
    columns = 0
    for basis in spaces.values():
        require(is_identity_word(signed_axes(basis)), "literal seven-turn endpoint")
        columns += 8
    axes = signed_axes((8, 16, 32))
    rejected = 0
    for omitted in range(7):
        mutant = axes[:omitted] + axes[omitted + 1:]
        require(not is_identity_word(mutant), "omitted rotation survived")
        rejected += 1
        for replacement in range(7):
            if replacement == omitted:
                continue
            mutant = axes[:omitted] + (axes[replacement],) + axes[omitted + 1:]
            require(not is_identity_word(mutant), "replaced rotation survived")
            rejected += 1
    return columns, rejected


def abstract_spectrum() -> Counter:
    spectrum = Counter()
    for exponents in product(range(4), repeat=7):
        if sum(exponents) % 4 == 0:
            spectrum[2 * sum(REAL[a] for a in exponents)] += 1
    require(sum(spectrum.values()) == 4096, "incomplete root domain")
    require(min(spectrum) == -10, "seven-root lower constant")
    require(spectrum == Counter({-10: 49, -6: 490, -2: 1519,
                                 2: 1484, 6: 511, 10: 42, 14: 1}), "root spectrum")
    require(2 * sum(REAL[2] for _ in range(7)) < -10, "missing-product control")
    return spectrum


def diagonal_group_spectrum() -> Counter:
    """Characters of Z4^3 x Z2^3, separately from the abstract root scan."""
    spectrum = Counter()
    functions = set()
    for linear in product(range(4), repeat=3):
        for quadratic in product(range(2), repeat=3):
            phases = []
            for mask in range(8):
                x = tuple((mask >> j) & 1 for j in range(3))
                pairs = (x[0] * x[1], x[0] * x[2], x[1] * x[2])
                phase = sum(linear[j] * x[j] for j in range(3))
                phase += 2 * sum(quadratic[j] * pairs[j] for j in range(3))
                phases.append(phase % 4)
            functions.add(tuple(phases))
            require(sum(phases[1:]) % 4 == 0, "character violates product relation")
            spectrum[2 * sum(REAL[a] for a in phases[1:])] += 1
    require(len(functions) == 512, "diagonal character parametrization")
    require(spectrum == Counter({-10: 7, -6: 56, -2: 203, 2: 168, 6: 77, 14: 1}),
            "diagonal regular-action spectrum")
    # At the excluded f=4 mod 8, the rank-one coefficient has the opposite sign.
    require(-max(spectrum) == -14 < -10, "wrong-width-sign control")
    return spectrum


def scope(n: int, f: int) -> None:
    if n < 3 or n % 2 == 0 or f < 4 * n + 4:
        raise ValueError("requires odd n>=3 and f>=4n+4")


def constants() -> dict:
    partial = sum((Fraction(1, 2 ** (k * (k + 1) // 2)) for k in range(1, 6)), Fraction())
    tail = Fraction(1, 2**21) / (1 - Fraction(1, 2**7))
    inherited_upper = partial + tail
    gamma = 1 - Fraction(5, 14) - (inherited_upper - Fraction(1, 2))
    require(gamma == Fraction(14601049, 29130752) > Fraction(1, 2), "new constant")
    checks = 0
    for n in range(3, 32, 2):
        for offset in range(8):
            scope(n, 4 * n + 4 + offset)
            checks += 1
        f = 4 * n + 4
        require(f % 8 == 0, "starting phase residue")
        mass = Fraction(2 * (2 ** (2 * n) - 1), 2 ** (f // 2))
        require(Fraction(5, 7) * mass < Fraction(5, 14), "rank-one normalization")
    invalid = ((1, 8), (2, 16), (4, 24), (3, 15), (9, 39))
    for n, f in invalid:
        try:
            scope(n, f)
        except ValueError:
            continue
        raise ValueError("out-of-scope fixture accepted")
    return {"lower_constant": str(gamma), "gap_above_half": str(gamma - Fraction(1, 2)),
            "width_fixtures": checks, "scope_rejections": len(invalid)}


def source_hashes() -> dict[str, str]:
    root = PACKAGE.parent.parent
    require((PACKAGE / "SOURCES.json").stat().st_size <= 65536, "manifest capacity")
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    require(len(manifest["files"]) <= 8, "source inventory capacity")
    hashes = {}
    for row in manifest["files"]:
        if row["usage"] == "input":
            path = root / row["path"]
            require(path.stat().st_size <= 1048576, "source file capacity")
            data = path.read_bytes()
            digest = sha256(data).hexdigest()
            require(digest == row["sha256"], "source hash: " + row["path"])
            hashes[row["path"]] = digest
    require(len(hashes) == 3, "scientific source inventory")
    for name in PACKAGE_FILES:
        require((PACKAGE / name).stat().st_size <= 1048576, "package file capacity")
        hashes["research/" + PACKAGE.name + "/" + name] = sha256((PACKAGE / name).read_bytes()).hexdigest()
    return hashes


def main() -> None:
    require(len(sys.argv) == 1, "verifier accepts no arguments")
    hashes = source_hashes()
    spaces = isotropic_spaces()
    columns, rejected = literal_relations(spaces)
    abstract = abstract_spectrum()
    diagonal = diagonal_group_spectrum()
    receipt = {"status": "PASS_CLIFFORD_SEVEN_ROTATION_GAP", "constants": constants(),
               "isotropic_spaces": len(spaces), "point_incidence": 15,
               "literal_endpoint_columns": columns, "word_rejections": rejected,
               "abstract_root_spectrum": dict(sorted(abstract.items())),
               "diagonal_group_spectrum": dict(sorted(diagonal.items())),
               "semantic_controls": 2, "sha256": hashes}
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
