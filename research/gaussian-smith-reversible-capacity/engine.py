"""Finite logical reversible Gaussian overwrite interface. Apache-2.0."""

from math import comb


def dimensions(n: int, precision: int) -> tuple[int, int]:
    """Bound this executable model; the written theorem has no such bounds."""
    if type(n) is not int or type(precision) is not int:
        raise ValueError("depth and precision must be integers")
    if not 0 <= n <= 8 or not 0 <= precision <= 16:
        raise ValueError("executable bounds are 0 <= n <= 8, 0 <= P <= 16")
    clean = sum(comb(n, j) * min(2 * j, precision) for j in range(n + 1))
    return 1 << n, clean


def gaussian(label: int, precision: int) -> tuple[int, int]:
    """Evaluate the P binary pi-adic digits, pi=1+i."""
    real, imag, power_real, power_imag = 0, 0, 1, 0
    for j in range(precision):
        if (label >> j) & 1:
            real += power_real
            imag += power_imag
        power_real, power_imag = power_real - power_imag, power_real + power_imag
    return real, imag


def residue(real: int, imag: int, precision: int) -> int:
    """Extract P digits using exact division by pi after subtracting parity."""
    label = 0
    for j in range(precision):
        digit = (real + imag) & 1
        label |= digit << j
        real, imag = (real - digit + imag) // 2, (imag - real + digit) // 2
    return label


def chart(bank: tuple[int, ...], n: int, precision: int, kind: str) -> tuple[int, ...]:
    """Apply cited unimodular tensor factors, without any truncation."""
    result = list(bank)
    axes = range(n - 1, -1, -1) if kind.endswith("inv") else range(n)
    for axis in axes:
        for low in range(1 << n):
            high = low | (1 << axis)
            if low != high:
                ar, ai = gaussian(result[low], precision)
                br, bi = gaussian(result[high], precision)
                if kind == "T":
                    first, second = (ar + bi, ai - br), (br, bi)
                elif kind == "Tinv":
                    first, second = (ar - bi, ai + br), (br, bi)
                elif kind == "S":
                    first, second = (-ai, ar), (ar + br, ai + bi)
                elif kind == "Sinv":
                    first, second = (ai, -ar), (br - ai, bi + ar)
                else:
                    raise ValueError("unknown chart")
                result[low] = residue(*first, precision)
                result[high] = residue(*second, precision)
    return tuple(result)


def rotate(bank: tuple[int, ...], auxiliary: int, precision: int,
           inverse: bool = False) -> tuple[tuple[int, ...], int]:
    """Rotate (live, lost, clean) to (clean, live, lost) at every label."""
    output = [0] * len(bank)
    recovered = 0
    offset = 0
    for u, value in enumerate(bank):
        lost = min(2 * u.bit_count(), precision)
        live = precision - lost
        auxiliary_part = (auxiliary >> offset) & ((1 << lost) - 1)
        if inverse:
            output[u] = (value >> lost) | (auxiliary_part << live)
            recovered |= (value & ((1 << lost) - 1)) << offset
        else:
            output[u] = ((value & ((1 << live) - 1)) << lost) | auxiliary_part
            recovered |= (value >> live) << offset
        offset += lost
    return tuple(output), recovered


def overwrite(bank: tuple[int, ...], auxiliary: int, n: int, precision: int,
              inverse: bool = False) -> tuple[tuple[int, ...], int]:
    """Permutation on NP+K bits; auxiliary zero gives the required response."""
    size, clean = dimensions(n, precision)
    if len(bank) != size or any(type(x) is not int or not 0 <= x < (1 << precision)
                                for x in bank):
        raise ValueError("bank must contain 2^n canonical P-digit labels")
    if type(auxiliary) is not int or not 0 <= auxiliary < (1 << clean):
        raise ValueError("auxiliary state must fit exactly K bits")
    if type(inverse) is not bool:
        raise ValueError("inverse must be Boolean")
    before, after = ("Sinv", "Tinv") if inverse else ("T", "S")
    middle = chart(bank, n, precision, before)
    middle, garbage = rotate(middle, auxiliary, precision, inverse)
    return chart(middle, n, precision, after), garbage
