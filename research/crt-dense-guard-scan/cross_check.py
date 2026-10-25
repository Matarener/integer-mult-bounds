"""Independent pinned machine/source cross-check; host oracle has no tariff claim.

Usage: python3 -I -B cross_check.py PACKAGE REPOSITORY
All publishable output uses logical role names, never local input paths.
"""
import hashlib
import json
from pathlib import Path
import sys
import types

PINS = {
    "machine.py": "1cb27312932914eb631078bd56e85feb1dc6c4191e9d1962b2cc3a7e1cfb8df7",
    "verify.py": "40794cd2e2936f0f5e42fac1bb51b65c951a2ab56b7e88824e8c2d09a3dbf40e",
    "SOURCE-PINS.json": "e8e5c7320fb0bd1494e063eaa5aaf5f2f08562b80b72750081ea5a409eea5b1e",
}
ORACLE_SHA = "5863cd978de7f81c0627ba6ade29912ea2de99fbd149db8575302f3f10e97a3e"
SOURCE_PINS = {
    "research/unconditional-batched-crt/CRT.md": ("02c3a1e38cbee25aefe2640cc72676da62ba10eb7519fbcb9adb9d48b74eff2b", "d98dd8e368431cac33d5fc1c8c336696663641d6"),
    "research/unconditional-batched-crt/check_batched_crt.py": ("681e2e3d71fa74c8b9b326f3860104fd9d89590a222e26ae6ee718d1fd40ff2e", "1cf78abccd5e06beecc3ed21ba55f7c03b65fdbc"),
    "research/unconditional-batched-crt/NOTICE.md": ("924109837e71c52392191710d49c9deb42780878d1094f0b01e8690dbe799461", "886a8fdee275f01b459cbd68ae2815dc9269502f"),
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load(name, path, expected):
    data = path.read_bytes()
    need(digest(data) == expected, "changed input: " + path.name)
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(data, str(path), "exec"), module.__dict__)
    return module


def literal(cells, machine, adapter):
    adapter.admit_stencil(cells, machine)  # Host admission is explicitly unpriced.
    original = [machine.LEFT] + list(cells) + [machine.END]
    stencil = machine.Tape(original)
    counter, output = machine.transduce(stencil)
    need(stencil.cells == original, "protected input changed")
    need(stencil.head == counter.head == output.head == 0, "head return")
    need(counter.cells[0] == machine.LEFT and all(x == machine.BLANK for x in counter.cells[1:]),
         "private cells/right marker not blank")
    need(output.cells[0] == machine.LEFT and output.cells[-1] == machine.END, "owned output marker")
    mask = "".join(output.cells[1:-1]).encode("ascii")
    length, records = len(cells), 2 ** len(cells)
    need(len(mask) == records and set(mask) <= {48, 49}, "complete binary output length")
    roles = (stencil, counter, output)
    actions = sum(t.reads + t.writes + t.moves for t in roles)
    need(actions == 8 * records * length + 15 * records + 13 * length + 18, "action formula observer")
    need(sum(len(t.cells) for t in roles) == records + 2 * length + 6, "visited cell formula")
    return mask, actions


def source_cases(machine, adapter, oracle, source):
    rows = []
    cases = [(shape, 0) for shape in oracle.SHAPES]
    cases.append((oracle.Shape("one_target_with_back_spectator", 1, 5, 1, 5, (0,)), 1))
    for shape, back in cases:
        # This frozen quotient/remainder oracle predates reading the machine.
        # Repeat each base-address decision for every omitted back-bit suffix.
        base = oracle.good_mask(shape, source)
        expected = bytes(49 - bit for bit in base for _ in range(2 ** back))
        cells = adapter.geometry_stencil(shape.G, shape.H, shape.Y, shape.positions,
                                         shape.K, back, machine)
        actual, actions = literal(cells, machine, adapter)
        need(actual == expected, "literal output differs from preimplementation interval oracle")
        rows.append({"name": shape.name, "addresses": len(expected), "good": expected.count(b"0"),
                     "bad": expected.count(b"1"), "mask_ascii_sha256": digest(actual),
                     "observed_actions": actions, "back_skip_bits": back})
    return rows


def stencil(length, groups, machine):
    cells = [machine.SKIP] * length
    for start, width, kind, low, high in groups:
        lower = format(low, "0%db" % width)
        upper = format(high, "0%db" % width)
        for offset in range(width):
            need(cells[start + offset] == machine.SKIP, "test descriptor overlap")
            cells[start + offset] = (kind, offset == 0, offset == width - 1,
                                    lower[offset], upper[offset])
    return cells


def interval_mask(length, groups):
    result = bytearray()
    for address in range(2 ** length):
        accepted = True
        for start, width, kind, low, high in groups:
            # Independent direct numeric interval extraction, not streaming flags.
            value = (address // (2 ** (length - start - width))) % (2 ** width)
            accepted = accepted and (value != 2 ** width - 1 if kind == "D" else low <= value < high)
        result.append(48 if accepted else 49)
    return bytes(result)


def generic_cases(machine, adapter):
    cases = []
    for length in (1, 2, 3):
        cases.append((length, ()))
        for width in range(1, length + 1):
            for start in range(length - width + 1):
                cases.append((length, ((start, width, "D", 0, 0),)))
                for low in range(2 ** width):
                    for high in range(2 ** width):
                        cases.append((length, ((start, width, "G", low, high),)))
    # Adjacent intervals test conjunctive latching, including singleton intervals.
    for kind1, kind2 in (("D", "G"), ("G", "D")):
        for low in range(4):
            for high in range(4):
                groups = ((0, 1, "D", 0, 0), (1, 2, "G", low, high)) if kind1 == "D" else (
                    (0, 2, "G", low, high), (2, 1, "D", 0, 0))
                cases.append((3, groups))
    combined = hashlib.sha256()
    addresses = actions = 0
    for length, groups in cases:
        actual, count = literal(stencil(length, groups, machine), machine, adapter)
        expected = interval_mask(length, groups)
        need(actual == expected, "admitted generic interval semantics mismatch")
        combined.update(actual)
        addresses += len(actual)
        actions += count
    return {"cases": len(cases), "addresses": addresses, "combined_mask_ascii_sha256": combined.hexdigest(),
            "observed_actions": actions,
            "coverage": "L=1..3 all-SKIP; every single D placement; every single G placement/all threshold pairs; adjacent D/G orders"}


def main():
    need(len(sys.argv) == 3, "usage: cross_check.py PACKAGE REPOSITORY")
    package, repository = map(Path, sys.argv[1:])
    for name, sha in PINS.items():
        need(digest((package / name).read_bytes()) == sha, "changed primary input: " + name)
    for path, (sha, blob) in SOURCE_PINS.items():
        data = (repository / path).read_bytes()
        need(digest(data) == sha, "changed retained source: " + path)
        need(hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest() == blob, "source Git blob mismatch")
    oracle = load("_independent_before_machine_guard_oracle", Path(__file__).with_name("independent_guard_oracle.py"), ORACLE_SHA)
    source = oracle.load_source(repository / "research/unconditional-batched-crt/check_batched_crt.py")
    machine = load("_cross_literal_guard_machine", package / "machine.py", PINS["machine.py"])
    adapter = load("_cross_literal_guard_adapter", package / "verify.py", PINS["verify.py"])
    rows = source_cases(machine, adapter, oracle, source)
    generic = generic_cases(machine, adapter)
    print(json.dumps({"status": "PASS_INDEPENDENT_LITERAL_GUARD_CROSS_CHECK", "primary_hashes": PINS,
                      "preimplementation_oracle_sha256": ORACLE_SHA, "source_files_checked": len(SOURCE_PINS),
                      "source_fixture_addresses": sum(r["addresses"] for r in rows), "source_fixtures": rows,
                      "generic_stencils": generic,
                      "scope": "Complete Boolean output/ownership cross-check; source predicate projections, not production placement; geometry/admission and oracle are unpriced host work."}, sort_keys=True))


if __name__ == "__main__":
    main()
