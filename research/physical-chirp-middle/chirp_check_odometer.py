"""Exact streamed residues, local head travel and complete rollover controls."""
from hashlib import sha256
import importlib.util
from pathlib import Path
import sys
from chirp_sources import require


def reference():
    path = Path(__file__).resolve().parents[1] / "chirp-symbolic-seed80/vendor/stream.py"
    require(sha256(path.read_bytes()).hexdigest()
            == "04647a2c8fa6ec5a2f3cd091ca076249aaa7b655ffe868d68995469a0b53142d",
            "pinned Chafik chirp reference")
    spec = importlib.util.spec_from_file_location("chirp_chafik_reference", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def packet(flags, ell, sources, prefix=None):
    from cardinal_counts import Count
    from check_support import no_decode
    from chirp_odometer import Odometer
    from chirp_plan import ChirpPlan
    from ring_check_words import body, decode, tape, word_bits
    from scratch_pool import ScratchPool
    from session import OuterScope, erase_marker, initialize_marker, sealed_constructors
    from words import BLANK
    lengths = [ell-1+b for b in flags] + [ell]
    radices = [1 << n for n in lengths]
    A, cube = sum(lengths[:-1]), 1 << sum(lengths)
    p = max(16, A+13)
    raw_sources = b"".join(word_bits(value, ell) for value in sources)
    descriptor, source_port = tape(flags), tape(raw_sources)
    counts = tuple(Count.literal(v) for v in (len(flags), ell, p, 1))
    saved = tuple((bytes(v.tape.cells), v.tape.head) for v in counts)
    pool, odometer = ScratchPool(128), Odometer()
    scope = OuterScope(pool)
    model = reference().ChirpStream(1 << ell, radices, sources)
    expected_count = cube if prefix is None else prefix
    actual = []
    plan = None
    try:
        for value in pool.tapes:
            erase_marker(value)
            initialize_marker(value)
        with sealed_constructors(), scope.installed():
            try:
                plan = ChirpPlan(descriptor, *counts)
                plan.compile()
                with no_decode():
                    odometer.open(source_port, plan)
                initial_state = body(odometer.state)
                moves = odometer.state.meter.moves
                for index in range(expected_count):
                    observed = decode(odometer.phase)
                    # Independent closed formula in original tensor order.
                    remaining, direct = index, 0
                    for radix, source in reversed(list(zip(radices, sources))):
                        coordinate = remaining % radix
                        remaining //= radix
                        direct -= source*coordinate*coordinate*((1 << ell)//radix)
                    require(observed == model.phase == direct % (2 << ell), "physical chirp residue")
                    actual.append(observed)
                    with no_decode():
                        advanced = odometer.advance()
                    require(advanced == model.advance(), "physical carry and full-rollover flag")
                travel = odometer.state.meter.moves-moves
                require(odometer.visits == model.visits and odometer.wraps == model.wraps,
                        "literal PR479 axis-visit and wrap counts")
                require(travel <= 40*(ell+1)*(odometer.visits+len(sources)),
                        "local head travel rather than a complete-axis scan")
                if prefix is None:
                    require(odometer.visits < 2*cube and decode(odometer.phase) == 0
                            and body(odometer.state) == initial_state, "complete chirp rollover restoration")
            finally:
                odometer.close()
                if plan is not None:
                    plan.close()
                pool.empty()
        require(body(descriptor) == bytes(flags) and body(source_port) == raw_sources
                and saved == tuple((bytes(v.tape.cells), v.tape.head) for v in counts),
                "preserved odometer descriptors")
        require(all(t.head == 1 and all(b == BLANK for b in t.cells) for t in odometer.canonical),
                "erased odometer owned state")
        return {"ell": ell, "axes": len(sources), "prefix_only": prefix is not None,
                "residues": len(actual), "axis_visits": odometer.visits, "wraps": odometer.wraps,
                "state_head_moves": travel, "pool_peak": pool.peak,
                "sha256": sha256(bytes(actual)).hexdigest()}
    finally:
        for value in counts:
            value.close()
        for value in pool.tapes:
            erase_marker(value)


def run():
    return {"packets": [packet((0,), 2, (1, 3)), packet((1, 0), 2, (3, 1, 1)),
                        packet((0, 1), 3, (3, 5, 7)),
                        packet((0,)*39, 2, (1,)*39+(3,), prefix=64)]}
