"""Reduced complete endpoints for the changed stopping rule and root."""

from collections import Counter
from hashlib import sha256
import sys
from types import SimpleNamespace
from unittest.mock import patch

from active_sources import active, load_check, require


def run():
    from active_plan import ActiveWidthPlan
    from active_root import ActiveWidthRoot
    from cardinal_counts import Count
    from macro_code import Code
    from ordinary import Ordinary
    from records import Tape
    from retuned_machine import RetunedMachine
    from retuned_native import retune
    from t74_machine import T74Machine
    from words import BLANK
    state = active()
    fixture = load_check(state.t74 / "check_runtime.py", "active_check_z_fixture")
    # The retained root checker names its sibling checker in an import. Keep
    # that test-only alias distinct from similarly named BIT check modules.
    with patch.dict(sys.modules, {"check_runtime": fixture}):
        root_check = load_check(state.t74 / "check_root_runtime.py", "active_check_root_fixture")

    def native():
        return retune(Ordinary(2, SimpleNamespace(codes=SimpleNamespace(q=2)),
                              SimpleNamespace(families=0), (Code((("unreachable",),), 0),), capacity=64))

    def one_case(machine_class, root_width, corrupt=False):
        binding = fixture.ZFixture(corrupt)
        visits = Counter()
        machine = machine_class(binding, native(), binding.catalogue,
                                lambda _machine, event: visits.update([event]))
        raw = dict(prefixes=2, rows=4, front=0, compact_bits=0, before=0,
                   width=2, after=0, back=0, spacing=1, guard=1, residue=0,
                   component_bits=16, coefficients=2, root_width=root_width)
        desc = {name: Count.literal(value) for name, value in raw.items()}
        before = {name: bytes(value.tape.cells) for name, value in desc.items()}
        values = [(64*((i*7) % 11-5), 64*((i*3) % 7-3)) for i in range(64)]
        payload = fixture.encode(values, 16)
        expected = fixture.encode(fixture.oracle(values, 2, 0, 8, 2), 16)
        source = Tape()
        for bit in payload:
            source.append(bit)
        source.rewind()
        saved = tuple(source.cells)
        rejected = None
        try:
            try:
                result = machine.run(source, desc)
            except ValueError as exc:
                require(corrupt and "zero" in str(exc).lower(), "specific private-release rejection")
                rejected = str(exc)
            else:
                require(not corrupt, "corrupt private release accepted")
                actual = bytes(result.cells[1:]).rstrip(bytes([BLANK]))
                require(actual == expected, "complete stopped/recursive endpoint")
                result.clear()
            require(tuple(source.cells) == saved and machine.closed
                    and all(bytes(value.tape.cells) == before[name] for name, value in desc.items()),
                    "borrowed packet and descriptors survive return")
            if not corrupt:
                require(visits["enter"] == visits["return"]
                        and all(t.read() == BLANK for t in machine.private), "balanced calls and private cleanup")
            return {"root_width_bits": root_width.bit_length(), "calls": visits["enter"],
                    "returns": visits["return"], "rejected": rejected,
                    "output_sha256": sha256(expected).hexdigest() if not corrupt else None}
        finally:
            source.clear()
            for value in desc.values():
                value.close()

    class ShortStop(RetunedMachine):
        STOP_POWER = 3  # Reduced fixed-control fixture, not the production rate.

    seams = [one_case(ShortStop, value) for value in (7, 8, 9)]
    require([row["calls"] for row in seams] == [10, 10, 0], "strict stopping seam including equality")
    huge = (1 << 1000)+1
    old, new = one_case(T74Machine, huge), one_case(RetunedMachine, huge)
    require(old["calls"] == 0 and new["calls"] == 10
            and old["output_sha256"] == new["output_sha256"], "actual production cutoff changes execution")
    bad = one_case(RetunedMachine, 2, True)
    require(bad["rejected"] is not None, "retained nonzero-release control")

    original_native = root_check.Ordinary

    def root_native(*args, **kwargs):
        return retune(original_native(*args, **kwargs))

    with patch.object(root_check, "T74RootLayer", ActiveWidthRoot), \
            patch.object(root_check, "Ordinary", root_native), \
            patch.object(root_check, "RootPlan", ActiveWidthPlan):
        direct = root_check.run(False)
        fast = root_check.run(True)
    require(direct["packets"] == 4 and fast["packets"] == 1 and fast["visits"]["enter"] > 0,
            "actual-width direct and reduced fast root coverage")
    require(direct["sha256"] == "4fced21f9e114bff265815a79dfe0b02e2989a195c87a6c5a16b7041193fd760"
            and fast["sha256"] == "75b19b9d75e245f1720eaccc048c366a7a68cf7741805e908b0a2222067d4b40",
            "retained normalized root endpoints")
    composed = physical_conjugation(fixture, root_check, native)
    return {"status": "PASS_ACTIVE_WIDTH_PHYSICAL_RETURNS", "stop_seams": seams,
            "production_stop_control": {"old": old, "new": new}, "private_release_control": bad,
            "direct_root": direct, "reduced_fast_root": fast, "physical_conjugation": composed,
            "scope": "Reduced packets and declared root/guard fixtures. Huge root descriptor does not certify its time-domain premise."}


def physical_conjugation(fixture, reference, native_factory):
    """Connect the actual root bit convention to a reference exposure/inverse."""
    from active_plan import ActiveWidthPlan
    from active_root import ActiveWidthRoot
    from cardinal_counts import Count
    from records import Tape
    from session import erase_marker
    from words import BLANK
    binding = fixture.ZFixture()
    layer = ActiveWidthRoot(binding, native_factory(), binding.catalogue,
                            ActiveWidthPlan(2, 1, 4, guard_exponent=2))
    # Swap address bits 1 and 3. This sends S=(0,3) to T=(0,1) and is its own inverse.
    def permutation(index):
        return (index & 5) | ((index & 2) << 2) | ((index & 8) >> 2)
    original = [(4*((i*3) % 7-3), 4*((i*5) % 5-2)) for i in range(16)]
    placed = [None]*16
    for index, pair in enumerate(original):
        placed[permutation(index)] = pair
    raw = reference.encode(placed, 7)
    source = Tape()
    for bit in raw:
        source.append(bit)
    source.rewind()
    descriptors = tuple(Count.literal(x) for x in (5, 2, 2, 0, 1, 1, 0))
    saved = tuple(bytes(x.tape.cells) for x in descriptors)
    try:
        output = layer.run(source, *descriptors)
        bits = reference.body(output)
        components = []
        for start in range(0, len(bits), 7):
            integer = sum(bit << j for j, bit in enumerate(bits[start:start+7]))
            components.append(integer-128 if integer & 64 else integer)
        returned = list(zip(components[::2], components[1::2]))
        restored = [returned[permutation(index)] for index in range(16)]
        expected = []
        for target in range(16):
            fixed, total = target & ~9, [0, 0]
            for a in (0, 1):
                for b in (0, 1):
                    sign = -1 if ((target & 1)*a + ((target >> 3) & 1)*b) % 2 else 1
                    pair = original[fixed | a | (b << 3)]
                    total = [x+sign*y for x, y in zip(total, pair)]
            require(all(x % 4 == 0 for x in total), "exact p-grid conjugation fixture")
            expected.append(tuple(x//4 for x in total))
        require(restored == expected and reference.body(source) == raw,
                "physical root and reference single-bit exposure compute H on the original selected bits")
        require(tuple(bytes(x.tape.cells) for x in descriptors) == saved and layer.closed
                and layer.current.read() == BLANK, "composed root borrowing and return")
        output.clear()
        erase_marker(output)
        return {"records": 16, "source_bits": [0, 3], "target_bits": [0, 1],
                "exposure_execution": "finite reference permutation; no fast-router execution",
                "status": "PASS_PHYSICAL_ROOT_CONJUGATION"}
    finally:
        source.clear()
        for value in descriptors:
            value.close()
