#!/usr/bin/env python3
"""Compensated restored shears preserve the R439 helper footprint.

The three words in the K-defect tally, and the pinned degree-1 pair control,
are the same parent D bracket with a helper-only prefix S and its reverse.
Each gate of S is h_a ^= h_b, and the middle support is the parent support
after columns[b] ^= columns[a]. That shape forces the executed helper mask E
to equal the parent's E. The synthetic restored edge applies the shear and
does not update the support, so its executed mask is not the named column.

This is a finite certificate plus the one-edge identity in README.md. It does
not adopt an H2/K contract and does not change a paid profile or kappa.
"""
import gzip
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
PARENT = "research/r439-target-compensation/candidate.json.gz"
WORDS = (
    ("star", "research/r439-helper-stars-seed19/candidate.json.gz", 221),
    ("composition", "research/r439-bsection-stars-seed01/composition.json.gz", 221),
    ("candidate", "research/r439-bsection-stars-seed01/candidate.json.gz", 236),
    ("pair_control", "research/r439-bsection-stars-seed01/pair_control.json.gz", 188),
)
BLOCKS = (306, 111, 306)


def fail(message):
    raise SystemExit("FAIL_R439_SHEAR_COMPENSATION " + message)


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pin_inputs():
    with open(os.path.join(HERE, "SOURCES.json"), encoding="utf-8") as handle:
        rows = json.load(handle)["files"]
    for row in rows:
        if row["usage"] != "input":
            continue
        path = os.path.join(ROOT, row["path"])
        if sha256(path) != row["sha256"]:
            fail("sha256 mismatch for " + row["path"])


def load_word(relative):
    with gzip.open(os.path.join(ROOT, relative), "rt", encoding="utf-8") as handle:
        word = json.load(handle)
    if word.get("v") != 111 or word.get("R") != 439 or "D" not in word:
        fail("unexpected word shape: " + relative)
    return word


def helper_mask(word):
    return ((1 << word["R"]) - 1) << (2 * word["v"])


def xor_sources(values, sources):
    acc = 0
    for src in sources:
        acc ^= values[src]
    return acc


def execute(word, gates):
    """Helper-column masks xored into targets, and whether helpers return."""
    width, helpers = word["v"], word["R"]
    columns = 2 * width + helpers
    mask = helper_mask(word)
    values = [1 << reg for reg in range(columns)]
    delivered = [0] * width
    for _frame, dest, sources in gates:
        acc = xor_sources(values, sources)
        if width <= dest < 2 * width:
            delivered[dest - width] ^= acc & mask
        values[dest] ^= acc
    restored = all(values[reg] == (1 << reg) for reg in range(2 * width, columns))
    return delivered, restored


def forward_k(word):
    """Helper columns on targets after A, scatter and B, frames off."""
    width = word["v"]
    mask = helper_mask(word)
    columns = 2 * width + word["R"]
    values = [1 << reg for reg in range(columns)]
    for name in ("A", "scatter", "B"):
        if name == "scatter":
            copies = [values[reg] for reg in word["ret"]]
            for target, row in enumerate(word["scatter"]):
                values[width + target] ^= xor_sources(copies, row)
        else:
            for _frame, dest, sources in word[name]:
                values[dest] ^= xor_sources(values, sources)
    return [values[width + target] & mask for target in range(width)]


def split_d(word):
    width = word["v"]
    gates = word["D"]
    prefix = 0
    while prefix < len(gates) and gates[prefix][1] >= 2 * width:
        prefix += 1
    left, middle, right = BLOCKS
    body = gates[prefix:prefix + left + middle + right]
    if len(body) != left + middle + right or len(gates) != prefix + len(body) + prefix:
        fail("D is not prefix + 306 + 111 + 306 + reverse-prefix")
    return (gates[:prefix], body[:left], body[left:left + middle],
            body[left + middle:], gates[-prefix:] if prefix else [])


def writes_targets_only(gates, width):
    return all(width <= dest < 2 * width and all(width <= src < 2 * width for src in sources)
               for _frame, dest, sources in gates)


def columns_from_middle(middle, width):
    columns = [0] * 439
    for index, (_frame, dest, sources) in enumerate(middle):
        if dest != width + index:
            fail("middle target %d is not in order" % index)
        for src in sources:
            if src < 2 * width:
                fail("middle gate names a non-helper")
            columns[src - 2 * width] ^= 1 << index
    return columns


def shear_columns(columns, edges):
    updated = list(columns)
    for center, leaf in edges:
        updated[leaf] ^= updated[center]
    return updated


def edges_of(prefix, width):
    edges = []
    for _frame, dest, sources in prefix:
        if len(sources) != 1 or dest < 2 * width or sources[0] < 2 * width:
            fail("helper prefix is not a single helper-to-helper gate")
        edges.append((dest - 2 * width, sources[0] - 2 * width))
    return edges


def middle_from_columns(columns, width):
    gates = []
    for target in range(width):
        sources = [2 * width + helper for helper, col in enumerate(columns) if col >> target & 1]
        gates.append([0, width + target, sources])
    return gates


def source_sets(middle):
    return [tuple(sorted(sources)) for _frame, _dest, sources in middle]


def one_edge_preserves(columns, values, center, leaf):
    """The README case split, evaluated on arbitrary helper-supported values."""
    width_bits = max((col.bit_length() for col in columns), default=0)
    before = [0] * width_bits
    for helper, col in enumerate(columns):
        bit = 0
        row = col
        while row:
            if row & 1:
                before[bit] ^= values[helper]
            row >>= 1
            bit += 1
    values[center] ^= values[leaf]
    columns[leaf] ^= columns[center]
    after = [0] * width_bits
    for helper, col in enumerate(columns):
        bit = 0
        row = col
        while row:
            if row & 1:
                after[bit] ^= values[helper]
            row >>= 1
            bit += 1
    return before == after


def probe_edges(columns):
    """Five shears whose centers actually carry support. Deterministic."""
    carriers = [helper for helper, col in enumerate(columns) if col]
    if len(carriers) < 5:
        fail("parent middle has fewer than five occupied helpers")
    edges = []
    for step, center in enumerate(carriers[:5]):
        leaf = (center + 1 + step) % len(columns)
        if leaf == center:
            leaf = (leaf + 1) % len(columns)
        edges.append((center, leaf))
    return edges


def assemble(parent_parts, edges, columns, compensated):
    prefix_gates, transport_before, _middle, transport_after = parent_parts
    updated = shear_columns(columns, edges) if compensated else list(columns)
    width = 111
    shears = [[0, 2 * width + center, [2 * width + leaf]] for center, leaf in edges]
    middle = middle_from_columns(updated, width)
    return shears + transport_before + middle + transport_after + shears[::-1]


def main():
    pin_inputs()
    parent = load_word(PARENT)
    width = parent["v"]
    prefix, before, middle, after, suffix = split_d(parent)
    if prefix or suffix:
        fail("parent D is not the bare 306+111+306 bracket")
    if not writes_targets_only(before, width) or not writes_targets_only(after, width):
        fail("parent transport blocks are not target-to-target")
    base_columns = columns_from_middle(middle, width)
    if source_sets(middle_from_columns(base_columns, width)) != source_sets(middle):
        fail("parent middle is not the column support it defines")
    parent_e, parent_restored = execute(parent, parent["D"])
    parent_k = forward_k(parent)
    if not parent_restored or parent_e != parent_k:
        fail("parent executed footprint is not its forward K")
    if execute(parent, middle + after)[0] != parent_e:
        fail("parent leading transport changes the helper footprint")

    # The one-edge identity on the parent's real supports, five times.
    probe = probe_edges(base_columns)
    running_columns = list(base_columns)
    running_values = [1 << (2 * width + helper) for helper in range(parent["R"])]
    for center, leaf in probe:
        if not one_edge_preserves(running_columns, running_values, center, leaf):
            fail("one-edge identity failed on the probe")
    parts = (prefix, before, middle, after)
    compensated = assemble(parts, probe, base_columns, True)
    bare = assemble(parts, probe, base_columns, False)
    if execute(parent, compensated)[0] != parent_e:
        fail("compensated probe changed E")
    if execute(parent, bare)[0] == parent_e:
        fail("uncompensated probe did not change E")
    if not execute(parent, compensated)[1]:
        fail("compensated probe did not restore helpers")

    edge_counts = []
    for name, relative, expect in WORDS:
        word = load_word(relative)
        word_prefix, word_before, word_middle, word_after, word_suffix = split_d(word)
        if len(word_prefix) != expect:
            fail(name + " prefix length is not " + str(expect))
        if word_suffix != word_prefix[::-1]:
            fail(name + " suffix is not the reversed helper prefix")
        if word_before != before or word_after != after:
            fail(name + " transport blocks are not the parent's")
        edges = edges_of(word_prefix, width)
        expected = shear_columns(base_columns, edges)
        if columns_from_middle(word_middle, width) != expected:
            fail(name + " middle is not the compensated parent support")
        if source_sets(middle_from_columns(expected, width)) != source_sets(word_middle):
            fail(name + " middle names a source twice or out of helper order")
        # Replay every real edge through the same identity, not only the total.
        columns = list(base_columns)
        values = [1 << (2 * width + helper) for helper in range(word["R"])]
        for center, leaf in edges:
            if not one_edge_preserves(columns, values, center, leaf):
                fail(name + " rejected the one-edge identity")
        delivered, restored = execute(word, word["D"])
        footprint = forward_k(word)
        if not restored or delivered != parent_e or footprint != parent_k:
            fail(name + " does not keep E = K = parent K")
        edge_counts.append(str(len(edges)))

    synthetic = {
        "v": 1,
        "R": 2,
        "D": [[0, 2, [3]], [0, 1, [2]], [0, 2, [3]]],
        "A": [],
        "B": [],
        "scatter": [[]],
        "ret": [2],
    }
    # h0 ^= h1 dirties h0. The read still names only h0, so the leaf support
    # was not toggled. Delivery is e0 XOR e1, not the named column e0.
    syn_e, syn_restored = execute(synthetic, synthetic["D"])
    named = 1 << 2
    if not syn_restored or syn_e != [named ^ (1 << 3)] or syn_e == [named]:
        fail("synthetic uncompensated edge did not separate delivery from the name")

    print(
        "PASS_R439_SHEAR_COMPENSATION words=4 edges=%s parent_E_equals_K=1 "
        "descendants_E_equals_K=4 shape=4 one_edge_steps=%d compensated_probe=1 "
        "uncompensated_probe=1 synthetic_rejects=1 no_new_kappa"
        % ("/".join(edge_counts), sum(int(item) for item in edge_counts) + len(probe)))


if __name__ == "__main__":
    main()
