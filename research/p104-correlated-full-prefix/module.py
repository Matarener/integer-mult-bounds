"""Exact Z/4 row images, represented by two bounded bit planes. Apache-2.0."""

from engine import need


def add(left, right):
    low, high = left
    other_low, other_high = right
    return low ^ other_low, high ^ other_high ^ (low & other_low)


def negative(row):
    low, high = row
    return low, high ^ low


def subtract_multiple(row, pivot, coefficient):
    need(0 <= coefficient < 4, 'Z4 multiplier')
    if coefficient == 0:
        return row
    if coefficient == 2:
        return row[0], row[1] ^ pivot[0]
    return add(row, negative(pivot) if coefficient == 1 else pivot)


def binary_rank(rows):
    pivots = {}
    for source in rows:
        row = source
        for _ in range(1025):
            if not row:
                break
            bit = row.bit_length() - 1
            if bit not in pivots:
                pivots[bit] = row
                break
            row ^= pivots[bit]
        else:
            raise ValueError('binary elimination capacity')
    return len(pivots)


def image_index(rows, columns):
    """Return log2 image size, with independent unit and even ranks."""
    need(1 <= columns <= 1024 and len(rows) <= 40000, 'matrix capacity')
    pivots, even = [], []
    for source in rows:
        low, high = source
        need(low >= 0 and high >= 0 and
             low.bit_length() <= columns and high.bit_length() <= columns,
             'matrix row width')
        for bit, pivot in pivots:
            coefficient = ((low >> bit) & 1) + 2 * ((high >> bit) & 1)
            low, high = subtract_multiple((low, high), pivot, coefficient)
        if low:
            need(len(pivots) < columns, 'unit pivot capacity')
            bit = (low & -low).bit_length() - 1
            if (high >> bit) & 1:
                high ^= low
            pivots.append((bit, (low, high)))
        elif high:
            even.append(high)
    residual = []
    for source in even:
        high = source
        for bit, (low, _) in pivots:
            if (high >> bit) & 1:
                high ^= low
        residual.append(high)
    unit_rank, even_rank = len(pivots), binary_rank(residual)
    need(unit_rank + even_rank <= columns, 'independent matrix ranks')
    return {'unit_rank': unit_rank, 'even_rank': even_rank,
            'index_log2': 2 * unit_rank + even_rank}


def real_rows(planes, power):
    """Realify Gaussian rows, after multiplying their coefficients by pi^power."""
    need(0 <= power <= 3 and len(planes) <= 20000, 'Gaussian matrix capacity')
    rows = []
    for al, ah, bl, bh in planes:
        real = al | (bl << 512), ah | ((bh ^ bl) << 512)
        imag = bl | (al << 512), bh | (ah << 512)
        if power == 0:
            rows.extend((real, imag))
        elif power == 1:
            rows.extend((add(real, negative(imag)), add(real, imag)))
        elif power == 2:
            rows.extend(((0, imag[0]), (0, real[0])))
        else:
            rows.extend(((0, real[0] ^ imag[0]), (0, real[0] ^ imag[0])))
    return rows


def invariants(planes):
    ranks = [image_index(real_rows(planes, k), 1024) for k in range(4)]
    f0, f1, f2, f3 = (r['index_log2'] for r in ranks)
    counts = [0, f0 - 2 * f1 + f2, f1 - 2 * f2 + f3, f2 - 2 * f3, f3]
    counts[0] = 512 - sum(counts)
    need(all(n >= 0 for n in counts), 'Gaussian invariant multiplicities')
    need(sum(e * n for e, n in enumerate(counts)) == f0,
         'Gaussian index identity')
    return {'pi_power_images': ranks, 'pi_exponent_multiplicities': counts,
            'index_B9_log2': f0, 'index_over_four_B9_log2': 2048 - f0}
