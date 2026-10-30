"""Independent forward propagation and bounded checks of the new safety criterion."""
from __future__ import annotations

from itertools import product

from model import Event, backward_caps, event_model, planes_in, space
from sweep import closure, next_events


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def basis_of_mask(mask: int) -> tuple[int, ...]:
    basis: list[int] = []
    pivots: dict[int, int] = {}
    for value in range(1, 512):
        if not mask >> value & 1:
            continue
        reduced = value
        for bit in range(8, -1, -1):
            if reduced >> bit & 1 and bit in pivots:
                reduced ^= pivots[bit]
        if reduced:
            pivots[reduced.bit_length() - 1] = reduced
            basis.append(value)
    return tuple(basis)


def forward_reference(events, baseline, registers, seed, plane):
    current = [None] * registers
    for event in events:
        for reg, frame in zip(event.regs, event.before, strict=True):
            if current[reg] is None:
                current[reg] = frame
    counts = list(baseline)
    injected = basis_of_mask(plane)
    for index, event in enumerate(events):
        vectors = list(event.frame.basis)
        if index == seed:
            vectors.extend(injected)
        for reg in event.regs:
            vectors.extend(current[reg].basis)
        frame = space(tuple(vectors))
        if event.fixed and frame.mask != event.frame.mask:
            return None
        for reg, original in zip(event.regs, event.before, strict=True):
            old = event.frame.dim - original.dim
            new = frame.dim - current[reg].dim
            require(new >= 0, "reference monotonicity")
            if old:
                counts[old] -= 1
            if new:
                counts[new] += 1
            current[reg] = frame
    return tuple(counts)


def toy_checks() -> int:
    from model import append_event

    ambient = (1 << 8) - 1
    lines = [space((value,)).mask for value in range(1, 8)]
    flats = [1, *lines, *(plane | 1 for plane in planes_in(ambient)), ambient]
    checks = 0
    for first, second, third in product(flats, repeat=3):
        current = [space(())] * 3
        events = []
        append_event(events, current, ("seed", 0), (0, 1), ())
        append_event(events, current, ("mix", 0), (1, 2), ())
        for reg, mask in enumerate((first, second, third)):
            append_event(events, current, ("fixed", reg), (reg,), basis_of_mask(mask), True)
        baseline = [0] * 10
        for event in events:
            for before in event.before:
                rank = event.frame.dim - before.dim
                if rank:
                    baseline[rank] += 1
        cap = backward_caps(events, 3)[0]
        for plane in planes_in(ambient):
            result = forward_reference(events, baseline, 3, 0, plane)
            require((result is not None) == (plane & cap == plane), "backward criterion toy mismatch")
            if result is not None:
                actual = closure(events, next_events(events, 3), baseline, 0, plane)
                require(actual == result, "toy profile mismatch")
            checks += 1
    return checks


def run_controls(result: dict) -> int:
    from verify import load_word

    word, _ = load_word()
    events, baseline, registers = event_model(word)
    following = next_events(events, registers)
    for row in result["profiles"]:
        seed, plane = row["witness"]
        reference = forward_reference(events, baseline, registers, seed, plane)
        require(reference == tuple(row["profile"]), "full-frame witness differs from sparse closure")
    require(forward_reference(events, baseline, registers, 0, (1 << 1) | (1 << 2) | (1 << 3)) is None,
            "forbidden injection accepted")
    try:
        closure(events, following, baseline, 0, (1 << 1) | (1 << 2) | (1 << 3))
    except ValueError:
        pass
    else:
        raise ValueError("sparse closure accepts forbidden injection")
    changed = dict(result["profiles"][0])
    changed["profile"] = list(changed["profile"])
    changed["profile"][1] += 1
    seed, plane = changed["witness"]
    require(forward_reference(events, baseline, registers, seed, plane) != tuple(changed["profile"]),
            "corrupted profile accepted")
    toy_count = toy_checks()
    require(toy_count == 28672, "toy domain changed")
    return len(result["profiles"]) + 3 + toy_count
