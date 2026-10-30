"""Pin primary caller and earlier independent oracle for a bounded cross-check."""
import hashlib
from itertools import product
import json
from pathlib import Path
from random import Random
import sys
import types


PRIMARY_SHA256 = "5e62787f3c4a8f1175ca7dea6c6b8ceff7863a3f879abd6245faf6aeb272fd45"
ORACLE_SHA256 = "8cdaedebd991fc0f73e74dd7b53e1c42f1e50d7b61e5b2e52d74134e2dafbdc4"
SOURCE_SHA256 = "681e2e3d71fa74c8b9b326f3860104fd9d89590a222e26ae6ee718d1fd40ff2e"


def load(path, name, expected):
    path = Path(path)
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError("reviewed source bytes changed")
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(data, str(path), "exec"), module.__dict__)
    return module


def independent_row(oracle, state, moduli, widths, ell, level, global_row):
    result = []
    for axis, shift in oracle.offsets(state, moduli, level).items():
        embedding = oracle.global_rows(widths[axis], ell)
        if global_row not in embedding:
            result.append((axis, None, None, 0))
        else:
            row = embedding.index(global_row)
            target, table = oracle.network(widths[axis], moduli[axis], shift)[row]
            result.append((axis, row, target, table[state[axis]]))
    return tuple(result)


def main():
    primary = load(sys.argv[1], "_pinned_mixed_primary", PRIMARY_SHA256)
    oracle = load(sys.argv[2], "_before_primary_mixed_oracle", ORACLE_SHA256)
    source = load(sys.argv[3], "_retained_mixed_source", SOURCE_SHA256)
    decoder_checks = 0
    for ell in range(2, 17):
        for height in (ell - 1, ell):
            embedding = oracle.global_rows(height, ell)
            for g in range(2 * ell - 1):
                expected = embedding.index(g) if g in embedding else None
                if primary.local_row(height, ell, g) != expected:
                    raise ValueError("literal decoder differs from independent embedding")
                decoder_checks += 1
    rng = Random(4174)
    mixed = set()
    for packed in rng.sample(range(1 << 14), 64):
        mixed.add((packed & 7, (packed >> 3) & 7, (packed >> 6) & 15, (packed >> 10) & 15))
    mixed.update(((5, 0, 1, 0), (0, 1, 0, 13)))
    fixtures = [((5, 7, 11, 13), (3, 3, 4, 4), 4, sorted(mixed)),
                ((5, 3), (3, 3), 4, product(range(8), repeat=2)),
                ((7, 3), (3, 2), 3, product(range(8), range(4))),
                ((3,), (2,), 3, ((x,) for x in range(4)))]
    states = rows_checked = idle_specs = 0
    digest = hashlib.sha256()
    for moduli, widths, ell, inputs in fixtures:
        caller = primary.Caller(moduli, widths, ell, source)
        for original in inputs:
            original = tuple(original)
            for reverse in (False, True):
                state = original
                levels = tuple(range(1, len(state).bit_length()))
                for level in reversed(levels) if reverse else levels:
                    rows = tuple(range(2 * ell - 1))
                    for g in reversed(rows) if reverse else rows:
                        expected = independent_row(oracle, state, moduli, widths, ell, level, g)
                        if caller.row(state, level, g) != expected:
                            raise ValueError("actual-row specification differs from independent oracle")
                        updated = list(state)
                        for axis, row, target, control in expected:
                            if row is None:
                                idle_specs += 1
                            else:
                                updated[axis] ^= control << target
                        state = tuple(updated)
                        rows_checked += 1
                if state != caller.run(original, reverse=reverse):
                    raise ValueError("literal caller endpoint differs from independent program")
                if state != oracle.atomic_endpoint(original, moduli, reverse=reverse):
                    raise ValueError("literal caller endpoint differs from atomic CRT oracle")
                digest.update(oracle.encode(state, widths).to_bytes((sum(widths) + 7) // 8, "big"))
            states += 1
    print(json.dumps({"status": "PASS_PINNED_MIXED_CALLER_CROSSCHECK",
                      "states": states, "forward_inverse_rows": rows_checked,
                      "row_decoder_comparisons": decoder_checks,
                      "literal_idle_specifications": idle_specs,
                      "endpoint_sha256": digest.hexdigest(),
                      "primary_sha256": PRIMARY_SHA256, "oracle_sha256": ORACLE_SHA256,
                      "retained_source_sha256": SOURCE_SHA256,
                      "scope": "separate pre-code oracle against actual rows, including external ell/all-short and singleton cases; no E/tape theorem"},
                     sort_keys=True))


if __name__ == "__main__":
    main()
