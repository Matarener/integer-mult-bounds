"""Complete Boolean paid inventory for dual-scale Norm∘F_(4,1) at p=3,w=2.

Precision-blind family a=(1+p^{w-1},1)=(4,1) on G=(Z/9Z)^2. The single-factor
Norm pattern of research/weighted-callee-boolean-norm-invoice (shared scale s on
H'_1 and D'_0) never yields an involutory P' here. Dual asymmetric scales
(s_H1,s_D0)=(7,4) realize F_{(4,7)} with (P')^2=I on the same two-coordinate
scale support, and the ordinary PR2808 Boolean fixture attains interchange J
on all 6561 addresses (raw F_a alone attains 729/6561 by formula (5)).

Exact line-item meters come from the live Boolean callee path plus the pinned
padding.complete contract (added=0). Admission uses need(); survives -O.

Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

import importlib.util
import sys
from contextlib import contextmanager
from math import gcd, prod
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SOURCE = ROOT / "research/selected-outer-borrowing-wrapper"

Q = 3
W_EXP = 2
MODULUS = Q**W_EXP  # 9
DIMENSION = 2
WEIGHTS = (4, 1)  # a=(1+p^{w-1},1)
# Dual asymmetric scales on the same two coordinates as #4053 (H'_1, D'_0).
SCALE_H1 = 7
SCALE_D0 = 4
TARGET_WEIGHTS = (4, 7)  # P' with (P')^2 = I
V = MODULUS**DIMENSION  # 81 bank vectors
ADDRESS_VOLUME = V * V  # 6561
PLANES = max(1, ADDRESS_VOLUME.bit_length())  # 13
CALLS_PER_PLANE = 2
TOTAL_CALLS = PLANES * CALLS_PER_PLANE  # 26

# Closed-form invoice (Boolean run over all planes); two scales per address/call.
SCALE = 2 * ADDRESS_VOLUME * TOTAL_CALLS
INVERSE = 2 * ADDRESS_VOLUME * TOTAL_CALLS
WEIGHT_MULT = 2 * ADDRESS_VOLUME * TOTAL_CALLS
SOURCE_ACCESS = ADDRESS_VOLUME * TOTAL_CALLS
CALLEE_COPY = ADDRESS_VOLUME * TOTAL_CALLS
RESTORATION_PAYLOAD = ADDRESS_VOLUME * TOTAL_CALLS
ROWCOUNT_CELLS = 2
RESTORATION_ROWCOUNT = ROWCOUNT_CELLS * TOTAL_CALLS
RESTORATION = RESTORATION_PAYLOAD + RESTORATION_ROWCOUNT
FRAME_REWIND = TOTAL_CALLS
PAD_FRAME_COPY_IN = ADDRESS_VOLUME * TOTAL_CALLS
PAD_FRAME_COPY_OUT = ADDRESS_VOLUME * TOTAL_CALLS
FRAME_COPY = PAD_FRAME_COPY_IN + PAD_FRAME_COPY_OUT + CALLEE_COPY

RAW_AGREEMENTS = (MODULUS**DIMENSION) * prod(
    gcd(MODULUS, (WEIGHTS[i] * WEIGHTS[DIMENSION - 1 - i] - 1) % MODULUS)
    for i in range(DIMENSION)
)  # 729
NORMALIZED_AGREEMENTS = ADDRESS_VOLUME  # 6561
KAPPA_DECIMAL = "0.001672660197076918"
KAPPA_FRACTION = "836330098538459/500000000000000000"

INPUTS = (
    "research/weighted-wrapper-contract/TASK.json",
    "research/weighted-wrapper-contract/README.md",
    "research/weighted-wrapper-contract/algebra.py",
    "research/weighted-wrapper-contract/runtime_check.py",
    "research/selected-outer-borrowing-wrapper/README.md",
    "research/selected-outer-borrowing-wrapper/VENDOR.json",
    "research/selected-outer-borrowing-wrapper/controls.py",
    "research/selected-outer-borrowing-wrapper/outer.py",
    "research/selected-outer-borrowing-wrapper/predecessor.py",
    "research/selected-outer-borrowing-wrapper/vendor/pr2786/PREDECESSOR.json",
    "research/selected-outer-borrowing-wrapper/vendor/pr2786/README.md",
    "research/selected-outer-borrowing-wrapper/vendor/pr2786/padding.py",
    "research/selected-outer-borrowing-wrapper/vendor/pr2786/predecessor.tar.gz",
    "research/selected-outer-borrowing-wrapper/vendor/pr2786/source.py",
)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digits(value, modulus, n):
    result = [0] * n
    for i in range(n - 1, -1, -1):
        value, result[i] = divmod(value, modulus)
    need(value == 0, "bounded digit vector")
    return result


def number(values, modulus):
    result = 0
    for value in values:
        result = result * modulus + value
    return result


def unpack(address, width, gap, suffix):
    address, tail = divmod(address, suffix)
    address, d = divmod(address, width)
    address, middle = divmod(address, gap)
    prefix, h = divmod(address, width)
    return prefix, h, middle, d, tail


def pack(prefix, h, middle, d, tail, width, gap, suffix):
    return (((prefix * width + h) * gap + middle) * width + d) * suffix + tail


def load_source(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


@contextmanager
def installed_outer():
    names = ("_precision_blind_norm_pred", "_precision_blind_norm_outer")
    need(not set(names).intersection(sys.modules), "private namespace starts empty")
    predecessor = load_source(names[0], SOURCE / "predecessor.py")
    try:
        with predecessor.installed():
            yield load_source(names[1], SOURCE / "outer.py")
    finally:
        for name in names:
            sys.modules.pop(name, None)


def closed_form_invoice():
    return {
        "q": Q,
        "w": W_EXP,
        "modulus": MODULUS,
        "dimension": DIMENSION,
        "weights": list(WEIGHTS),
        "scale_H1": SCALE_H1,
        "scale_D0": SCALE_D0,
        "target_weights": list(TARGET_WEIGHTS),
        "address_volume": ADDRESS_VOLUME,
        "bit_planes": PLANES,
        "callee_calls": TOTAL_CALLS,
        "line_items": {
            "scale": SCALE,
            "inverse": INVERSE,
            "source_access": SOURCE_ACCESS,
            "restoration": RESTORATION,
            "restoration_payload": RESTORATION_PAYLOAD,
            "restoration_rowcount": RESTORATION_ROWCOUNT,
            "frame_copy": FRAME_COPY,
            "frame_copy_pad_in": PAD_FRAME_COPY_IN,
            "frame_copy_pad_out": PAD_FRAME_COPY_OUT,
            "frame_copy_callee": CALLEE_COPY,
            "frame_rewind": FRAME_REWIND,
            "weight_mult": WEIGHT_MULT,
        },
        "raw_agreements": RAW_AGREEMENTS,
        "normalized_agreements": NORMALIZED_AGREEMENTS,
        "kappa_decimal": KAPPA_DECIMAL,
        "no_new_kappa": True,
    }


def destination_norm_fa(
    address,
    modulus=MODULUS,
    weights=WEIGHTS,
    scale_h1=SCALE_H1,
    scale_d0=SCALE_D0,
    gap=1,
    suffix=1,
):
    """Address remap for dual-scale Norm∘F_a (same two-coordinate support)."""
    n = len(weights)
    width = modulus**n
    pref, h, middle, d, tail = unpack(address, width, gap, suffix)
    hv, dv = digits(h, modulus, n), digits(d, modulus, n)
    nh = [weights[j] * dv[n - 1 - j] % modulus for j in range(n)]
    nd = [
        hv[n - 1 - j] * pow(weights[n - 1 - j], -1, modulus) % modulus
        for j in range(n)
    ]
    nh = [nh[0], (nh[1] * scale_h1) % modulus]
    nd = [(nd[0] * scale_d0) % modulus, nd[1]]
    return pack(pref, number(nh, modulus), middle, number(nd, modulus), tail, width, gap, suffix)


def destination_fa(address, modulus=MODULUS, weights=WEIGHTS, gap=1, suffix=1):
    n = len(weights)
    width = modulus**n
    pref, h, middle, d, tail = unpack(address, width, gap, suffix)
    hv, dv = digits(h, modulus, n), digits(d, modulus, n)
    nh = number([weights[j] * dv[n - 1 - j] % modulus for j in range(n)], modulus)
    nd = number(
        [
            hv[n - 1 - j] * pow(weights[n - 1 - j], -1, modulus) % modulus
            for j in range(n)
        ],
        modulus,
    )
    return pack(pref, nh, middle, nd, tail, width, gap, suffix)


def destination_target(address, modulus=MODULUS, weights=TARGET_WEIGHTS, gap=1, suffix=1):
    """Direct F_{P'} for involutory P'=(4,7)."""
    return destination_fa(address, modulus=modulus, weights=weights, gap=gap, suffix=suffix)


def single_factor_norm_involutory_exists():
    """Whether any shared scale s on (H'_1,D'_0) makes Norm∘F_a an involution."""
    for s in range(MODULUS):
        # Induced P' from shared s: H=(a0 d1, s d0)=(4 d1, s d0) ⇒ p0=4, p1=s
        # D=(s h1, inv(a0) h0)=(s h1, 7 h0). For F_{P'}: D should be P'^{-1} H
        # ⇒ 1/p1 ≡ s and 1/p0 ≡ 7. Latter holds (inv(4)=7). Former: s*p1≡1 with
        # p1=s ⇒ s^2≡1. Also need p0*p1≡1 for weighted involution: 4s≡1.
        if (s * s) % MODULUS == 1 and (4 * s) % MODULUS == 1:
            return True
    return False


def algebra_identity_checks():
    need(RAW_AGREEMENTS == 729, "formula (5) raw agreements")
    need(not single_factor_norm_involutory_exists(), "single-factor Norm obstruction")
    for i in range(ADDRESS_VOLUME):
        need(
            destination_norm_fa(i) == destination_target(i),
            "dual-scale Norm o F_a = F_(4,7)",
        )
    # (P')^2 = I on bank vectors
    p0, p1 = TARGET_WEIGHTS
    for x0 in range(MODULUS):
        for x1 in range(MODULUS):
            y0 = (p0 * x1) % MODULUS
            y1 = (p1 * x0) % MODULUS
            z0 = (p0 * y1) % MODULUS
            z1 = (p1 * y0) % MODULUS
            need((z0, z1) == (x0, x1), "(P')^2 = I")
    # P_a^2 = 4 I (precision-blind defect)
    for x0 in range(MODULUS):
        for x1 in range(MODULUS):
            y0 = (WEIGHTS[0] * x1) % MODULUS
            y1 = (WEIGHTS[1] * x0) % MODULUS
            z0 = (WEIGHTS[0] * y1) % MODULUS
            z1 = (WEIGHTS[1] * y0) % MODULUS
            need(
                (z0, z1) == ((4 * x0) % MODULUS, (4 * x1) % MODULUS),
                "P_a^2 = 4I",
            )
    # Single shared scale s=2 (the #4053 factor) fails involution on a sample
    bad = 0
    for x0 in range(MODULUS):
        for x1 in range(MODULUS):
            # Induced equal-weight image (2 x1, 2 x0) then squared
            y0 = (2 * x1) % MODULUS
            y1 = (2 * x0) % MODULUS
            z0 = (2 * y1) % MODULUS
            z1 = (2 * y0) % MODULUS
            if (z0, z1) != (x0, x1):
                bad += 1
    need(bad == 72, "shared-scale-2 image not involutory on 72/81 banks")


def run_boolean_fixture(
    *,
    normalize: bool,
    scale_h1: int | None = None,
    scale_d0: int | None = None,
):
    """Execute unchanged outer.body_ordinary on Boolean origin planes at q=3,w=2.

    Returns (agreements_with_J, volume, planes, meters).
    """
    with installed_outer() as outer:
        from cardinal_counts import Count
        from records import Tape
        from words import Arena, Ring

        q = Q
        prefixes = rows = stock = gap = suffix = 1
        modulus, n = MODULUS, DIMENSION
        volume = prefixes * rows * modulus ** (2 * n) * gap * suffix
        need(volume == ADDRESS_VOLUME, "pinned address volume")
        arena = Arena(modulus.bit_length() + 1)
        indices = Arena(max(3, n.bit_length() + 1))
        mod, atoms = arena.input(modulus), indices.input(n)
        ring = Ring(mod)
        counts = [Count.literal(x) for x in (prefixes, rows, stock, gap, suffix)]
        meters = {
            "scale": 0,
            "inverse": 0,
            "source_access": 0,
            "restoration_payload": 0,
            "restoration_rowcount": 0,
            "callee_copy": 0,
            "frame_rewind": 0,
            "weight_mult": 0,
            "callee_calls": 0,
            "rowcount_cells": None,
        }
        recovered = [0] * volume
        planes = max(1, volume.bit_length())
        need(planes == PLANES, "pinned plane count")
        sh = SCALE_H1 if scale_h1 is None else scale_h1
        sd = SCALE_D0 if scale_d0 is None else scale_d0
        try:
            for plane in range(planes):
                source = Tape()
                for i in range(volume):
                    source.append(((i + 1) >> plane) & 1)
                source.rewind()
                saved = bytes(source.cells)
                state = {"call_index": 0}

                def callee(padded, row_count, state=state, meters=meters):
                    state["call_index"] += 1
                    meters["callee_calls"] += 1
                    padded_count = sum(
                        bit << j
                        for j, bit in enumerate(row_count.tape.cells[1:])
                        if bit in (0, 1)
                    )
                    total = (
                        prefixes
                        * padded_count
                        * modulus ** (2 * n)
                        * gap
                        * suffix
                    )
                    before = bytes(padded.cells)
                    row_before = bytes(row_count.tape.cells)
                    if meters["rowcount_cells"] is None:
                        meters["rowcount_cells"] = len(row_before) - 1
                    target = [0] * total
                    width = modulus**n
                    for i in range(total):
                        pref, h, middle, d, tail = unpack(i, width, gap, suffix)
                        hv, dv = digits(h, modulus, n), digits(d, modulus, n)
                        nh = []
                        nd = []
                        for j in range(n):
                            meters["weight_mult"] += 1
                            nh.append(WEIGHTS[j] * dv[n - 1 - j] % modulus)
                        for j in range(n):
                            inv = pow(WEIGHTS[n - 1 - j], -1, modulus)
                            meters["inverse"] += 1
                            nd.append(hv[n - 1 - j] * inv % modulus)
                        if normalize:
                            meters["scale"] += 2
                            nh[1] = (nh[1] * sh) % modulus
                            nd[0] = (nd[0] * sd) % modulus
                        dest = pack(
                            pref,
                            number(nh, modulus),
                            middle,
                            number(nd, modulus),
                            tail,
                            width,
                            gap,
                            suffix,
                        )
                        bit = padded.cells[i + 1]
                        meters["source_access"] += 1
                        need(bit in (0, 1), "Boolean payload bit")
                        target[dest] = bit
                        meters["callee_copy"] += 1
                    output = Tape()
                    for bit in target:
                        output.append(bit)
                    output.rewind()
                    meters["frame_rewind"] += 1
                    need(
                        bytes(padded.cells) == before and padded.head == 1,
                        "callee input restored",
                    )
                    need(
                        bytes(row_count.tape.cells) == row_before
                        and row_count.tape.head == 1,
                        "callee rows restored",
                    )
                    meters["restoration_payload"] += total
                    meters["restoration_rowcount"] += max(0, len(row_before) - 1)
                    return output

                output = outer.body_ordinary(
                    source, atoms, ring, q, *counts, callee
                )
                try:
                    need(state["call_index"] == 2, "exactly two weighted calls")
                    need(
                        bytes(source.cells) == saved and source.head == output.head == 1,
                        "literal body preserves source and heads",
                    )
                    need(len(output.cells) == volume + 1, "complete returned payload")
                    for destination, bit in enumerate(output.cells[1:]):
                        need(bit in (0, 1), "Boolean output")
                        recovered[destination] |= bit << plane
                finally:
                    output.clear()
                    source.clear()
            width = modulus**n
            agrees = 0
            for i in range(volume):
                pref, h, middle, d, tail = unpack(i, width, gap, suffix)
                j_dest = pack(pref, d, middle, h, tail, width, gap, suffix)
                if recovered[j_dest] == i + 1:
                    agrees += 1
            if normalize and scale_h1 is None and scale_d0 is None:
                need(
                    len(set(recovered)) == volume,
                    "origin labels remain bijective",
                )
            need(meters["callee_calls"] == TOTAL_CALLS, "call census")
            need(meters["rowcount_cells"] == ROWCOUNT_CELLS, "rowcount cell width")
            return agrees, volume, planes, meters
        finally:
            for count in counts:
                count.close()
            ring.close()
            arena.free(mod)
            indices.free(atoms)


def padding_frame_copy_invoice(volume=ADDRESS_VOLUME, calls=TOTAL_CALLS):
    return {
        "pad_in": volume * calls,
        "pad_out": volume * calls,
        "note": "added=0 on rows=stock=1; scan_rows mode=copy both directions",
    }


def build_certificate():
    algebra_identity_checks()
    raw_agrees, volume, planes, raw_meters = run_boolean_fixture(normalize=False)
    need(raw_agrees == RAW_AGREEMENTS, "raw Boolean agreements")
    need(raw_meters["scale"] == 0, "raw path performs no Norm scales")
    norm_agrees, volume2, planes2, meters = run_boolean_fixture(normalize=True)
    need(volume == volume2 == ADDRESS_VOLUME, "volume pin")
    need(planes == planes2 == PLANES, "planes pin")
    need(norm_agrees == NORMALIZED_AGREEMENTS, "normalized Boolean agreements")
    need(meters["scale"] == SCALE, "scale line item")
    need(meters["inverse"] == INVERSE, "inverse line item")
    need(meters["source_access"] == SOURCE_ACCESS, "source_access line item")
    need(meters["callee_copy"] == CALLEE_COPY, "callee_copy line item")
    need(
        meters["restoration_payload"] == RESTORATION_PAYLOAD,
        "restoration payload",
    )
    need(
        meters["restoration_rowcount"] == RESTORATION_ROWCOUNT,
        "restoration rowcount",
    )
    need(meters["frame_rewind"] == FRAME_REWIND, "frame_rewind")
    need(meters["weight_mult"] == WEIGHT_MULT, "weight_mult")
    pad = padding_frame_copy_invoice()
    need(pad["pad_in"] == PAD_FRAME_COPY_IN, "pad_in")
    need(pad["pad_out"] == PAD_FRAME_COPY_OUT, "pad_out")

    def algebraic_norm_hits(scale_h1, scale_d0):
        hits = 0
        for i in range(ADDRESS_VOLUME):
            if destination_norm_fa(i, scale_h1=scale_h1, scale_d0=scale_d0) == destination_target(
                i
            ):
                hits += 1
        return hits

    need(
        algebraic_norm_hits(SCALE_H1, SCALE_D0) == ADDRESS_VOLUME,
        "dual-scale algebraic identity full",
    )
    shared2_hits = algebraic_norm_hits(2, 2)
    identity_hits = algebraic_norm_hits(1, 1)
    zero_hits = algebraic_norm_hits(0, 0)
    swapped_hits = algebraic_norm_hits(SCALE_D0, SCALE_H1)
    need(shared2_hits < ADDRESS_VOLUME, "shared-scale-2 algebraic control")
    need(identity_hits < ADDRESS_VOLUME, "identity-scale algebraic control")
    need(zero_hits < ADDRESS_VOLUME, "zero-scale algebraic control")
    need(swapped_hits < ADDRESS_VOLUME, "swapped dual-scale algebraic control")
    # One live Boolean wrong-scale control (shared factor from the a=(2,1) invoice).
    shared2, _, _, _ = run_boolean_fixture(
        normalize=True, scale_h1=2, scale_d0=2
    )
    need(shared2 < NORMALIZED_AGREEMENTS, "shared-scale-2 Boolean control fails")
    invoice = closed_form_invoice()
    return {
        "schema_version": 1,
        "claim": (
            "On the precision-blind PR2808 Boolean fixture (q=3,w=2,a=(4,1)), "
            "dual-scale Norm∘F_a with (s_H1,s_D0)=(7,4) on the same two-coordinate "
            "support admits the ordinary wrapper at 6561/6561 with a complete paid "
            "inventory; single shared-factor Norm is obstructed; raw F_a fails at "
            "729/6561. No new kappa."
        ),
        "fixture": {
            "q": Q,
            "w": W_EXP,
            "modulus": MODULUS,
            "weights": list(WEIGHTS),
            "scale_H1": SCALE_H1,
            "scale_D0": SCALE_D0,
            "target_weights": list(TARGET_WEIGHTS),
            "prefixes": 1,
            "rows": 1,
            "stock": 1,
            "gap": 1,
            "suffix": 1,
            "address_volume": ADDRESS_VOLUME,
            "bit_planes": PLANES,
            "wrapper": "research/selected-outer-borrowing-wrapper/outer.py:body_ordinary",
            "scale_support_coordinates": ["H'_1", "D'_0"],
            "single_factor_norm_involutory": False,
        },
        "counts": {
            "raw_agreements": raw_agrees,
            "normalized_agreements": norm_agrees,
            "address_volume": ADDRESS_VOLUME,
            "bit_planes": PLANES,
            "callee_calls": TOTAL_CALLS,
            "scale": meters["scale"],
            "inverse": meters["inverse"],
            "source_access": meters["source_access"],
            "restoration": meters["restoration_payload"]
            + meters["restoration_rowcount"],
            "restoration_payload": meters["restoration_payload"],
            "restoration_rowcount": meters["restoration_rowcount"],
            "frame_copy": FRAME_COPY,
            "frame_copy_pad_in": PAD_FRAME_COPY_IN,
            "frame_copy_pad_out": PAD_FRAME_COPY_OUT,
            "frame_copy_callee": meters["callee_copy"],
            "frame_rewind": meters["frame_rewind"],
            "weight_mult": meters["weight_mult"],
            "shared_scale_2_agreements": shared2,
            "shared_scale_2_algebraic_hits": shared2_hits,
            "identity_scale_algebraic_hits": identity_hits,
            "zero_scale_algebraic_hits": zero_hits,
            "swapped_dual_scale_algebraic_hits": swapped_hits,
        },
        "invoice": invoice,
        "kappa_decimal": KAPPA_DECIMAL,
        "kappa_fraction": KAPPA_FRACTION,
        "no_new_kappa": True,
    }
