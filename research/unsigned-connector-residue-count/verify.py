#!/usr/bin/env python3
"""Replay the closed counting law; print a source-bound receipt without writes."""

import hashlib
import itertools
import json
from math import comb
from pathlib import Path

from counts import (MAX_MODULUS, chronological_counts, formula_counts, require,
                    signature, witness)

PACKAGE = Path(__file__).resolve().parent
ENUMERATION_MAX = 10


def subset_counts(modulus: int, centered: bool = True) -> tuple[int, ...]:
    """Choose readout positions, independently of chronological DP states."""
    require(2 <= modulus <= ENUMERATION_MAX, "subset enumeration out of range")
    counts = [0] * modulus
    offset = modulus * (modulus - 1) // 2 if centered else 0
    for positions in itertools.combinations(range(2 * modulus), modulus):
        counts[(sum(positions) - offset) % modulus] += 1
    require(sum(counts) == comb(2 * modulus, modulus), "subset mass mismatch")
    return tuple(counts)


def exact_count_checks() -> dict:
    spectra = {}
    enumerated = 0
    residues = 0
    for modulus in range(2, MAX_MODULUS + 1):
        counts = formula_counts(modulus)
        require(counts == chronological_counts(modulus), "formula/DP disagreement")
        prime = all(modulus % d != 0 for d in range(2, modulus))
        require((len(set(counts[1:])) == 1) == prime,
                "nonzero equidistribution/primality disagreement")
        require(all(counts[c] == counts[-c] for c in range(modulus)),
                "reverse-word symmetry failed")
        if modulus <= ENUMERATION_MAX:
            require(counts == subset_counts(modulus), "formula/subset disagreement")
            enumerated += comb(2 * modulus, modulus)
        residues += modulus
        spectra[str(modulus)] = counts
    require(spectra["3"] == (8, 6, 6), "F3 specialization changed")
    require(spectra["4"] == (20, 16, 18, 16), "composite specialization changed")
    return {"spectra": spectra, "residues": residues,
            "enumerated_words": enumerated}


def positional_action_checks() -> int:
    """Run every small word through the generic dirty coefficient action."""
    checked = 0
    for modulus in range(2, 9):
        counts = [0] * modulus
        for positions in itertools.combinations(range(2 * modulus), modulus):
            selected = frozenset(positions)
            word = "".join("A" if i in selected else "B"
                           for i in range(2 * modulus))
            source, dirt, product = signature(word, modulus)
            require(source == dirt == 0, "unrestored balanced word")
            counts[product] += 1
            checked += 1
        require(tuple(counts) == formula_counts(modulus), "word action count mismatch")
    return checked


def complete_length_checks() -> dict:
    """Include the two pure words in the zero-target, length-2m class."""
    checked, restored = 0, 0
    for modulus in range(2, 8):
        counts = [0] * modulus
        for events in itertools.product("AB", repeat=2 * modulus):
            source, dirt, product = signature("".join(events), modulus)
            if source == dirt == 0:
                counts[product] += 1
                restored += 1
            checked += 1
        expected = list(formula_counts(modulus))
        expected[0] += 2
        require(counts == expected, "full restored word count mismatch")
    return {"words": checked, "restored_words": restored}


def matvec(matrix: tuple, vector: tuple, modulus: int) -> tuple:
    require(len(matrix) == len(vector) == 2 and all(len(r) == 2 for r in matrix),
            "dense replay expects two coordinates")
    return tuple(sum(matrix[i][j] * vector[j] for j in range(2)) % modulus
                 for i in range(2))


def add(left: tuple, right: tuple, modulus: int) -> tuple:
    return tuple((left[i] + right[i]) % modulus for i in range(2))


def dense_replay(word: str, modulus: int, a: tuple, b: tuple,
                 x: tuple, y: tuple, z: tuple) -> tuple:
    require(2 <= modulus <= MAX_MODULUS and len(word) <= 2 * MAX_MODULUS,
            "dense replay bound exceeded")
    for event in word:
        require(event in "AB", "unknown dense event")
        if event == "B":
            z = add(z, matvec(b, x, modulus), modulus)
        else:
            y = add(y, matvec(a, z, modulus), modulus)
    return x, y, z


def dense_checks() -> dict:
    """Literal noncommuting maps; coordinate bases plus arbitrary dirty inputs."""
    a, b = ((0, 1), (1, 1)), ((1, 1), (0, 1))
    checked, roundtrips, witnesses = 0, 0, 0
    for modulus in range(2, MAX_MODULUS + 1):
        for coefficient in range(1, modulus):
            word = witness(modulus, coefficient)
            require(signature(word[::-1], modulus) == (0, 0, -coefficient % modulus),
                    "reverse word is not the inverse")
            witnesses += 1
            for index in range(8):
                values = [int(i == index) for i in range(6)]
                if index >= 6:
                    values = [(i * (index + 1) + index) % modulus for i in range(6)]
                x, y, z = tuple(values[:2]), tuple(values[2:4]), tuple(values[4:])
                abx = matvec(a, matvec(b, x, modulus), modulus)
                target = add(y, tuple(coefficient * v for v in abx), modulus)
                result = dense_replay(word, modulus, a, b, x, y, z)
                require(result == (x, target, z), "dense dirty endpoint failed")
                back = dense_replay(word[::-1], modulus, a, b, *result)
                require(back == (x, y, z), "dense inverse failed")
                checked += 1
                roundtrips += 1
    return {"witnesses": witnesses, "dense_inputs": checked, "roundtrips": roundtrips}


def reject_controls() -> list[str]:
    controls = []
    require(subset_counts(2, centered=False) != formula_counts(2),
            "missing positional shift was undetected")
    controls.append("missing subset-position shift")
    fake_prime = ((comb(8, 4) + 2 * 3) // 4,) + ((comb(8, 4) - 2) // 4,) * 3
    require(fake_prime != formula_counts(4), "composite treated as prime")
    controls.append("prime formula used at composite characteristic")
    word = witness(4, 1)
    for mutant, label in ((word.replace("B", "", 1), "omitted source restoration"),
                          (word[:-1], "omitted dirty readout cancellation"),
                          (witness(4, 2), "wrong product coefficient")):
        require(signature(mutant, 4) != (0, 0, 1), f"undetected fault: {label}")
        controls.append(label)
    a, b = ((0, 1), (0, 0)), ((0, 0), (1, 0))
    x, zero = (1, 0), (0, 0)
    actual = dense_replay(word, 4, a, b, x, zero, zero)[1]
    require(actual != matvec(b, matvec(a, x, 4), 4), "AB/BA swap undetected")
    controls.append("noncommuting factor order reversed")
    require(signature("BABBB", 4)[1] != 0, "clean-only shortcut accepted")
    controls.append("one readout leaves arbitrary connector dirt")
    for invalid in (1, 33, True, 2.0):
        try:
            formula_counts(invalid)
        except ValueError:
            continue
        raise ValueError("invalid characteristic accepted")
    controls.append("finite verifier domain enforced")
    return controls


def source_hashes() -> dict:
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    require(len(sources["files"]) <= 8, "source list exceeds finite bound")
    result = {}
    for row in sources["files"]:
        if row["usage"] == "input":
            path = PACKAGE.parent.parent / row["path"]
            require(path.stat().st_size <= 1_048_576, "input exceeds byte bound")
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            require(actual == row["sha256"], f"input hash mismatch: {row['path']}")
            result[row["path"]] = actual
    files = sorted(PACKAGE.iterdir())
    require(len(files) <= 12, "unexpected package file count")
    for path in files:
        require(path.is_file() and not path.is_symlink(), "unexpected package entry")
        require(path.stat().st_size <= 1_048_576, "package file exceeds byte bound")
        result[f"package/{path.name}"] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def main() -> None:
    counts = exact_count_checks()
    receipt = {"claim_type": "scoped proof with finite corroboration",
               "counting": counts, "literal_words": positional_action_checks(),
               "complete_length": complete_length_checks(),
               "dense": dense_checks(), "controls": reject_controls(),
               "sha256": source_hashes()}
    encoded = json.dumps(receipt, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(encoded.encode()).hexdigest()
    print(encoded)
    print(f"PASS_UNSIGNED_CONNECTOR_RESIDUE_COUNT moduli=31 "
          f"residues={counts['residues']} receipt_sha256={digest}")


if __name__ == "__main__":
    main()
