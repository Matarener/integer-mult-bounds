# SPDX-License-Identifier: Apache-2.0
"""Independent kernel census and full-group replay; produced by Nick Petalas."""

from itertools import permutations, product

PROFILES = ((3, 1, 1, 1, 1), (2, 2, 1, 1, 1), (2, 1, 2, 1, 1))


def check(condition, message):
    if not condition:
        raise ValueError(message)


def direct_census(widths):
    """Enumerate row choices directly and intersect all annihilator sets."""
    owners = [vertex for vertex in range(5) for _ in range(widths[vertex])]
    row_options = []
    for i in range(7):
        allowed = sum(1 << j for j in range(7)
                      if (owners[i] - owners[j]) % 5 in (1, 4))
        row_options.append(tuple((1 << i) | x for x in range(128) if x & ~allowed == 0))
    annihilators = tuple(sum(1 << x for x in range(128)
                            if (x & row).bit_count() % 2 == 0) for row in range(128))
    histogram = [0] * 8
    optima = set()
    for rows in product(*row_options):
        kernel = (1 << 128) - 1
        for row in rows:
            kernel &= annihilators[row]
        cardinality = kernel.bit_count()
        check(cardinality > 0 and cardinality & (cardinality - 1) == 0,
              "kernel cardinality is not a power of two")
        rank = 7 - (cardinality.bit_length() - 1)
        histogram[rank] += 1
        if rank == 4:
            optima.add(sum(row << (7 * i) for i, row in enumerate(rows)))
    return histogram, optima


def general_linear(d):
    """List all invertible local matrices by the determinant formula."""
    choices = []
    for rows in product(range(1 << d), repeat=d):
        determinant = 0
        for perm in permutations(range(d)):
            term = 1
            for i in range(d):
                term &= (rows[i] >> perm[i]) & 1
            determinant ^= term
        if determinant:
            choices.append(rows)
    return choices


def full_group(widths):
    """Return the complete vector permutations L and L^-1."""
    elements = []
    for blocks in product(*(general_linear(d) for d in widths)):
        rows = []
        offset = 0
        for block in blocks:
            rows.extend(row << offset for row in block)
            offset += len(block)
        forward = tuple(sum(((row & x).bit_count() % 2) << i
                            for i, row in enumerate(rows)) for x in range(128))
        check(len(set(forward)) == 128, "singular local group element")
        inverse = [0] * 128
        for x, y in enumerate(forward):
            inverse[y] = x
        elements.append((forward, tuple(inverse)))
    return elements


def transform(word, element):
    forward, inverse = element
    columns = tuple(sum(((word >> (7 * i + j)) & 1) << i for i in range(7))
                    for j in range(7))
    answer = 0
    for j in range(7):
        image = 0
        for k in range(7):
            if inverse[1 << j] & (1 << k):
                image ^= columns[k]
        column = forward[image]
        for i in range(7):
            answer |= ((column >> i) & 1) << (7 * i + j)
    return answer


def independent_channels(widths):
    """Build every optimal edge/private word with separate port allocation."""
    offsets = [sum(widths[:i]) for i in range(5)]
    forms = {}
    for x in product(*(range(min(widths[i], widths[(i + 1) % 5]) + 1)
                       for i in range(5))):
        private = [widths[i] - x[i - 1] - x[i] for i in range(5)]
        if sum(x) != 3 or min(private) < 0:
            continue
        next_port = offsets[:]
        rows = [1 << i for i in range(7)]
        for i in range(5):
            j = (i + 1) % 5
            for _ in range(x[i]):
                a, b = next_port[i], next_port[j]
                next_port[i] += 1
                next_port[j] += 1
                rows[a] |= 1 << b
                rows[b] |= 1 << a
        word = sum(row << (7 * i) for i, row in enumerate(rows))
        forms[word] = {"shared": list(x), "private": private}
    return forms


def verify_profile(record):
    widths = tuple(record["widths"])
    check(widths in PROFILES, "unexpected profile")
    histogram, optima = direct_census(widths)
    check(histogram == record["rank_histogram"], "independent rank histogram")
    check(len(optima) == record["optimal_matrices"], "independent optimum count")
    elements = full_group(widths)
    check(len(elements) == record["local_group_order"], "independent group order")
    channels = independent_channels(widths)
    covered = set()
    sizes = {}
    for orbit in record["orbits"]:
        word = sum(row << (7 * i) for i, row in enumerate(orbit["representative_rows"]))
        check(word in optima, "invalid orbit representative")
        members = {transform(word, element) for element in elements}
        check(min(members) == word, "noncanonical orbit representative")
        check(members <= optima and not members & covered, "overlapping or invalid orbit")
        check(len(members) == orbit["orbit_size"], "independent orbit size")
        check(len(elements) == len(members) * orbit["stabilizer_size"], "stabilizer count")
        forms = [value for key, value in channels.items() if key in members]
        check(forms == ([] if orbit["edge_private_form"] is None else
                        [orbit["edge_private_form"]]), "independent channel classification")
        covered.update(members)
        size = str(len(members))
        sizes[size] = sizes.get(size, 0) + 1
    check(covered == optima, "orbit partition omits an optimum")
    check(len(record["orbits"]) == record["orbit_count"], "orbit count")
    check(sizes == record["orbit_size_histogram"], "orbit-size histogram")
    check(sum(x["edge_private_form"] is not None for x in record["orbits"]) ==
          record["edge_private_orbits"], "edge/private count")
    check(sum(histogram) == record["matrix_count"] == 1 << record["free_entries"],
          "complete matrix count")
    check(record["minimum_rank"] == next(i for i, count in enumerate(histogram) if count),
          "minimum rank")


def verify_certificate(certificate):
    check(certificate["field"] == "F2", "field")
    check(certificate["equivalence"] == "block-diagonal similarity; labeled vertices",
          "equivalence")
    check([tuple(x["widths"]) for x in certificate["profiles"]] == list(PROFILES),
          "profile domain")
    for record in certificate["profiles"]:
        verify_profile(record)


if __name__ == "__main__":
    import json
    from pathlib import Path

    verify_certificate(json.loads((Path(__file__).parent / "RESULT.json").read_text()))
    print("PASS_BINARY_C5_INDEPENDENT_KERNEL_AND_FULL_GROUP")
