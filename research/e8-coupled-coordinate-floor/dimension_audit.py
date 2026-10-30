"""Private independent prefix-capacity DP; no E8 geometry is generated here.

Source: PR2962 Lemma S, f6e68c9838e21b263223ae61273e381d2c0b92c7,
research/decoder-certificate-ceilings/README.md section 3.
The formulation below minimizes basis weight directly, rather than maximizing
the predecessor's deficiency sum. Prepared for conorholds; local-only.
"""

from functools import lru_cache

SUPPORT_CAP = (0, 1, 2, 4, 8, 12, 20, 36, 64, 120)
ROOT_CAP = (0, 1, 3, 6, 12, 20, 36, 63)


def minimum_relaxation_bill(dimension):
    """Return the exact minimum over sorted positive weights in 1..9.

    For every prefix of dimension-r vectors, r=0..7, its support union
    leaves roots spanning at most r dimensions. Thus the sum of its support
    caps must be at least 120-ROOT_CAP[r]. Larger residual ranks give no
    additional constraint. Capping a prefix sum at 120 loses no information.
    """

    @lru_cache(None)
    def visit(position, previous, covered):
        if position == dimension:
            return 0
        answer = None
        for weight in range(previous, 10):
            next_covered = min(120, covered + SUPPORT_CAP[weight])
            remaining = dimension - position - 1
            if remaining <= 7 and next_covered < 120 - ROOT_CAP[remaining]:
                continue
            suffix = visit(position + 1, weight, next_covered)
            if suffix is None:
                continue
            bill = weight + suffix
            answer = bill if answer is None else min(answer, bill)
        return answer

    result = visit(0, 1, 0)
    profile = []
    position, previous, covered = 0, 1, 0
    while position < dimension:
        current = visit(position, previous, covered)
        for weight in range(previous, 10):
            next_covered = min(120, covered + SUPPORT_CAP[weight])
            remaining = dimension - position - 1
            if remaining <= 7 and next_covered < 120 - ROOT_CAP[remaining]:
                continue
            suffix = visit(position + 1, weight, next_covered)
            if suffix is not None and weight + suffix == current:
                profile.append(weight)
                position, previous, covered = position + 1, weight, next_covered
                break
        else:
            raise RuntimeError("No optimal reconstruction transition")
    return result, tuple(profile), visit.cache_info().currsize


def main():
    results = {}
    for dimension in range(23, 73):
        bill, profile, states = minimum_relaxation_bill(dimension)
        results[dimension] = bill
        if dimension >= 24 and bill < 73:
            raise AssertionError((dimension, bill, profile))
        print(dimension, bill, profile, "states", states)
    if results[23] != 72 or results[24] != 73:
        raise AssertionError(results)
    print("PASS_PRIVATE_STRICT_DIMENSION_SCREEN dimensions24..72")


if __name__ == "__main__":
    main()
