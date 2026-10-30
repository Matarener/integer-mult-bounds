"""Bounded exact reference for the changed rounded convolution boundary."""

from fractions import Fraction


def require(condition, message):
    if not condition:
        raise ValueError(message)


def geometry(lengths, ell, rows):
    require(type(ell) is int and 2 <= ell <= 4, "reference ell in 2..4")
    require(type(rows) is int and 1 <= rows <= 2, "reference rows in 1..2")
    require(1 <= len(lengths) <= 3 and all(v in (ell-1, ell) for v in lengths),
            "reference long/short axes")
    require(sum(lengths) <= 6, "reference at most 64 addresses")
    return 1 << sum(lengths), 1 << ell


def coordinates(value, lengths):
    result = [0] * len(lengths)
    for index in range(len(lengths)-1, -1, -1):
        result[index] = value % (1 << lengths[index])
        value >>= lengths[index]
    return result


def reverse_index(value, lengths):
    result = 0
    for coordinate, width in zip(coordinates(value, lengths), lengths):
        reversed_value = 0
        for bit in range(width):
            reversed_value = (reversed_value << 1) | ((coordinate >> bit) & 1)
        result = (result << width) | reversed_value
    return result


def permute(values, lengths, ell, rows):
    count, degree = geometry(lengths, ell, rows)
    require(len(values) == rows*count*degree, "complete permutation reference packet")
    return [values[(row*count+reverse_index(index, lengths))*degree+coefficient]
            for row in range(rows) for index in range(count) for coefficient in range(degree)]


def transform(values, lengths, ell, rows, opposite=False):
    count, degree = geometry(lengths, ell, rows)
    require(len(values) == rows*count*degree, "complete transform reference packet")
    result = []
    for row in range(rows):
        for target in range(count):
            total = [[0, 0] for _ in range(degree)]
            outgoing = coordinates(target, lengths)
            for source in range(count):
                incoming = coordinates(source, lengths)
                phase = sum((2*degree >> width)*a*b
                            for width, a, b in zip(lengths, outgoing, incoming))
                phase = phase if opposite else -phase
                for coefficient in range(degree):
                    wraps, destination = divmod(coefficient+phase, degree)
                    sign = -1 if wraps % 2 else 1
                    a, b = values[(row*count+source)*degree+coefficient]
                    total[destination][0] += sign*a
                    total[destination][1] += sign*b
            result.extend((int(Fraction(a, count)), int(Fraction(b, count)))
                          for a, b in total)
    return result


def product(first, second, lengths, ell, p, rows):
    count, degree = geometry(lengths, ell, rows)
    require(type(p) is int and ell < p <= 16, "reference precision")
    require(len(first) == len(second) == rows*count*degree, "complete product packet")
    result = []
    for record in range(rows*count):
        total = [[0, 0] for _ in range(degree)]
        for left in range(degree):
            a, b = first[record*degree+left]
            for right in range(degree):
                c, d = second[record*degree+right]
                wrap, target = divmod(left+right, degree)
                sign = -1 if wrap else 1
                total[target][0] += sign*(a*c-b*d)
                total[target][1] += sign*(a*d+b*c)
        result.extend((int(Fraction(a, (1 << p)*degree)),
                       int(Fraction(b, (1 << p)*degree))) for a, b in total)
    return result


def original(first, second, lengths, ell, p, rows):
    a = transform(first, lengths, ell, rows)
    b = transform(second, lengths, ell, rows)
    return transform(product(a, b, lengths, ell, p, rows), lengths, ell, rows, True)


def changed(first, second, lengths, ell, p, rows, omissions=(True, True, True)):
    a = transform(first, lengths, ell, rows)
    b = transform(second, lengths, ell, rows)
    if omissions[0]:
        a = permute(a, lengths, ell, rows)
    if omissions[1]:
        b = permute(b, lengths, ell, rows)
    multiplied = product(a, b, lengths, ell, p, rows)
    if omissions[2]:
        multiplied = permute(multiplied, lengths, ell, rows)
    return transform(multiplied, lengths, ell, rows, True)


def routing_saving(lengths, p):
    require(1 <= len(lengths) <= 64 and all(type(v) is int and 1 <= v <= 256 for v in lengths),
            "bounded routing geometry")
    require(type(p) is int and 2 <= p <= 65536, "bounded routing precision")
    exponent = 997*((p+sum(lengths)).bit_length()-1)//1000
    cap = 1 << exponent
    edges = sum(width//2 for width in lengths)
    return 3*((edges+cap-1)//cap)
