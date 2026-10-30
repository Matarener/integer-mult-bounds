"""Finite address certificates for single-bit exposure, not a fast tape router."""

from fractions import Fraction as F
import itertools

from active_sources import require


def extension(size, sources, targets):
    require(type(size) is int and size >= 0, "address dimension")
    sources, targets = tuple(sources), tuple(targets)
    require(len(sources) == len(targets) and len(set(sources)) == len(sources)
            and len(set(targets)) == len(targets), "two equally sized distinct bit lists")
    require(all(type(i) is int and 0 <= i < size for i in (*sources, *targets)), "bit positions")
    mapping = list(range(size))
    for source, target in zip(sources, targets):
        mapping[source] = target
    for source, target in zip(sorted(set(targets)-set(sources)), sorted(set(sources)-set(targets))):
        mapping[source] = target
    require(sorted(mapping) == list(range(size)), "complete coordinate permutation")
    require(sum(i != j for i, j in enumerate(mapping)) <= 2*len(sources), "single-bit support bound")
    return tuple(mapping)


def address(index, mapping):
    return sum(((index >> bit) & 1) << target for bit, target in enumerate(mapping))


def place(values, mapping):
    output = [F(0)]*len(values)
    for index, value in enumerate(values):
        output[address(index, mapping)] = value
    return output


def hadamard(values, selected):
    result = list(values)
    for bit in selected:
        step = 1 << bit
        for index in range(len(result)):
            if index & step:
                continue
            a, b = result[index], result[index | step]
            result[index], result[index | step] = (a+b)/2, (a-b)/2
    return result


def run():
    permutations = 0
    for size in range(1, 7):
        for width in range(min(3, size)+1):
            for sources in itertools.combinations(range(size), width):
                for targets in itertools.permutations(range(size), width):
                    mapping = extension(size, sources, targets)
                    require(all(mapping[i] == j for i, j in zip(sources, targets)), "prescribed placement")
                    require(all(mapping[i] == i for i in set(range(size))-set(sources)-set(targets)),
                            "complement fixed")
                    permutations += 1
    cases = [(6, (0, 5), (0, 2)), (6, (1, 3, 5), (0, 2, 4)),
             (5, (0, 1, 2), (1, 2, 0)), (4, (), ())]
    columns = 0
    for size, sources, targets in cases:
        mapping = extension(size, sources, targets)
        inverse = tuple(mapping.index(i) for i in range(size))
        for column in range(1 << size):
            values = [F(int(i == column)) for i in range(1 << size)]
            actual = place(hadamard(place(values, mapping), targets), inverse)
            require(actual == hadamard(values, sources), "complete-tensor conjugation on each column")
            columns += 1
    # Fixing an external coarse bit loses closure under a permitted exposure.
    mapping = extension(6, (0, 1), (0, 2))
    fixed_coarse_slice = {i for i in range(64) if not (i >> 2) & 1}
    require({address(i, mapping) for i in fixed_coarse_slice} != fixed_coarse_slice,
            "fixed-label microbox is not an admitted complete tensor")
    rejected = 0
    for sources, targets in (((0, 0), (1, 2)), ((0,), (1, 2)), ((True,), (2,)), ((6,), (0,))):
        try:
            extension(6, sources, targets)
        except ValueError:
            rejected += 1
    require(rejected == 4, "invalid exposure descriptors reject")
    return {"status": "PASS_SINGLE_BIT_EXPOSURE_IDENTITY", "permutations": permutations,
            "exact_basis_columns": columns, "descriptor_rejections": rejected,
            "microbox_control": "not_closed", "scope": "Finite coordinate/linear algebra, not fast physical routing."}
