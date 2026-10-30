"""Exact finite corroboration and asymmetric frequency-order controls."""

from itertools import product as tuples
from reference import changed, geometry, original, permute, product, require, routing_saving


def packet(lengths, ell, rows, salt):
    count, degree = geometry(lengths, ell, rows)
    limit = 1 << ell
    return [((3*i+salt) % (2*limit+1)-limit,
             (5*i+2*salt) % (2*limit+1)-limit) for i in range(rows*count*degree)]


def finite_cases():
    cases = points = equivariance = 0
    invalid = {mask: False for mask in tuples((False, True), repeat=3)
               if mask not in ((False,)*3, (True,)*3)}
    for ell in (2, 3):
        for axes in (1, 2):
            for lengths in tuples((ell-1, ell), repeat=axes):
                for rows in (1, 2):
                    p = ell+1
                    first = packet(lengths, ell, rows, 1)
                    second = packet(lengths, ell, rows, 3)
                    # Add a common low-frequency component without leaving the disk.
                    first = [(a+(1 << (ell-1)), b) for a, b in first]
                    second = [(a+(1 << (ell-1)), b) for a, b in second]
                    require(all(a*a+b*b <= 1 << (2*p) for a, b in first+second), "finite disk inputs")
                    expected = original(first, second, lengths, ell, p, rows)
                    require(changed(first, second, lengths, ell, p, rows) == expected,
                            "all-three omission preserves complete rounded output")
                    a = permute(first, lengths, ell, rows)
                    b = permute(second, lengths, ell, rows)
                    require(product(a, b, lengths, ell, p, rows)
                            == permute(product(first, second, lengths, ell, p, rows), lengths, ell, rows),
                            "rounded record-local product equivariance")
                    require(permute(a, lengths, ell, rows) == first, "actual B is involutive")
                    for mask in invalid:
                        if not invalid[mask]:
                            invalid[mask] = changed(first, second, lengths, ell, p, rows, mask) != expected
                    cases += 1
                    points += len(expected)
                    equivariance += len(first)
    # A length-four character makes B exchange two different nonzero modes.
    first = character_packet()
    expected = original(first, first, (2,), 2, 3, 1)
    require(any(a or b for a, b in expected), "nonzero omission control")
    for mask in invalid:
        invalid[mask] = invalid[mask] or changed(first, first, (2,), 2, 3, 1, mask) != expected
    require(all(invalid.values()), "every asymmetric omission has a concrete counterexample")
    return {"rounded_cases": cases, "output_coefficients": points,
            "product_equivariance_coefficients": equivariance,
            "asymmetric_omission_counterexamples": len(invalid)}


def character_packet():
    result = []
    for address in range(4):
        record = [(0, 0)]*4
        for coefficient in range(4):
            wraps, target = divmod(coefficient+2*address, 4)
            record[target] = (-7 if wraps % 2 else 7, 0)
        result.extend(record)
    return result


def tariff_cases():
    tariffs = 0
    for widths in ((1,), (2,), (3, 2), (8,)*64, (256,)*64):
        for p in (2, 3, 8, 128, 65536):
            cap = 1 << (997*((p+sum(widths)).bit_length()-1)//1000)
            edges = sum(width//2 for width in widths)
            batches = sum(1 for _ in range(0, edges, cap))
            require(routing_saving(widths, p) == 3*batches, "enumerated bounded support batches")
            tariffs += 1
    require(routing_saving((2,), 3) == 3 and routing_saving((1,), 3) == 0,
            "strict and degenerate routing controls")
    rejected = 0
    for widths, p in (((), 3), ((0,), 3), ((257,), 3), ((2,), 1), ((2,), 65537)):
        try:
            routing_saving(widths, p)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid routing geometry accepted")
    return {"batch_cases": tariffs, "invalid_geometry_rejections": rejected}


def run():
    return {**finite_cases(), **tariff_cases()}
