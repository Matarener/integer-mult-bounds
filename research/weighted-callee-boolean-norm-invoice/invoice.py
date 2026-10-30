"""Complete paid Boolean-fixture invoice for Norm∘F_(2,1) on PR2808.

On the unchanged PR2808 ordinary body (outer.body_ordinary) with Boolean
origin bit-planes, the failing weighted callee a=(2,1) on G=(Z/3Z)^2 is
normalized by post-composing each F_a call with the two output scales that
realize F_{P'} for P'=T P, T=diag(1,2). The wrapper then attains interchange
J on all 81 addresses (raw F_a alone attains 9/81).

Exact line-item meters are taken from the live Boolean callee path plus the
pinned padding.complete contract (added=0 ⇒ one inbound and one outbound
payload copy of volume V per call). Admission uses need(); survives -O.

Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

import importlib.util
import sys
from contextlib import contextmanager
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SOURCE = ROOT / "research/selected-outer-borrowing-wrapper"
WWC = ROOT / "research/weighted-wrapper-contract"

MODULUS = 3
DIMENSION = 2
WEIGHTS = (2, 1)
SCALE_FACTOR = 2
SCALE_T = (1, 2)
V = MODULUS**DIMENSION  # 9 bank vectors; address volume = V*V = 81
ADDRESS_VOLUME = V * V  # 81
PLANES = max(1, ADDRESS_VOLUME.bit_length())  # 7
CALLS_PER_PLANE = 2
TOTAL_CALLS = PLANES * CALLS_PER_PLANE  # 14

# Closed-form invoice (Boolean run over all planes)
SCALE = 2 * ADDRESS_VOLUME * TOTAL_CALLS  # Norm: 2 scales/address/call
INVERSE = 2 * ADDRESS_VOLUME * TOTAL_CALLS  # P^{-1}: 2 inv-muls/address/call
WEIGHT_MULT = 2 * ADDRESS_VOLUME * TOTAL_CALLS  # P forward weight muls
SOURCE_ACCESS = ADDRESS_VOLUME * TOTAL_CALLS
CALLEE_COPY = ADDRESS_VOLUME * TOTAL_CALLS
RESTORATION_PAYLOAD = ADDRESS_VOLUME * TOTAL_CALLS
# Count.literal(1) row tape is [BLANK, ONE, BLANK-terminator encoding]; cells[1:]
# length is 2 on this fixture (see live meter).
ROWCOUNT_CELLS = 2
RESTORATION_ROWCOUNT = ROWCOUNT_CELLS * TOTAL_CALLS
RESTORATION = RESTORATION_PAYLOAD + RESTORATION_ROWCOUNT
FRAME_REWIND = TOTAL_CALLS
# padding.complete with rows=stock=1 ⇒ added=0: transform pad copies V_addr,
# restrict copies V_addr (pinned padding.py scan_rows mode=copy).
PAD_FRAME_COPY_IN = ADDRESS_VOLUME * TOTAL_CALLS
PAD_FRAME_COPY_OUT = ADDRESS_VOLUME * TOTAL_CALLS
FRAME_COPY = PAD_FRAME_COPY_IN + PAD_FRAME_COPY_OUT + CALLEE_COPY

RAW_AGREEMENTS = 9
NORMALIZED_AGREEMENTS = 81
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
    names = ("_boolean_norm_pred", "_boolean_norm_outer")
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
        "modulus": MODULUS,
        "dimension": DIMENSION,
        "weights": list(WEIGHTS),
        "scale_T": list(SCALE_T),
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


def destination_norm_fa(address, modulus=MODULUS, weights=WEIGHTS, gap=1, suffix=1):
    """Address remap for Norm∘F_a (keeps proposed weights; post-scales outputs)."""
    n = len(weights)
    width = modulus**n
    pref, h, middle, d, tail = unpack(address, width, gap, suffix)
    hv, dv = digits(h, modulus, n), digits(d, modulus, n)
    nh = [weights[j] * dv[n - 1 - j] % modulus for j in range(n)]
    nd = [
        hv[n - 1 - j] * pow(weights[n - 1 - j], -1, modulus) % modulus
        for j in range(n)
    ]
    nh = [nh[0], (nh[1] * SCALE_FACTOR) % modulus]
    nd = [(nd[0] * SCALE_FACTOR) % modulus, nd[1]]
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


def destination_pprime(address, modulus=MODULUS, gap=1, suffix=1):
    """Direct F_{P'} with P'(x0,x1)=(2 x1, 2 x0) = (P')^{-1}."""
    n = DIMENSION
    width = modulus**n
    pref, h, middle, d, tail = unpack(address, width, gap, suffix)
    hv, dv = digits(h, modulus, n), digits(d, modulus, n)
    nh = number([(SCALE_FACTOR * dv[n - 1 - j]) % modulus for j in range(n)], modulus)
    nd = number([(SCALE_FACTOR * hv[n - 1 - j]) % modulus for j in range(n)], modulus)
    return pack(pref, nh, middle, nd, tail, width, gap, suffix)


def algebra_identity_checks():
    """Norm∘F_a equals F_{P'}; (P')^2=I; formula (5) raw count."""
    for i in range(ADDRESS_VOLUME):
        need(destination_norm_fa(i) == destination_pprime(i), "Norm o F_a = F_P'")
    # P'^2 = I on bank vectors
    for x0 in range(MODULUS):
        for x1 in range(MODULUS):
            y0 = (SCALE_FACTOR * x1) % MODULUS
            y1 = (SCALE_FACTOR * x0) % MODULUS
            z0 = (SCALE_FACTOR * y1) % MODULUS
            z1 = (SCALE_FACTOR * y0) % MODULUS
            need((z0, z1) == (x0, x1), "(P')^2 = I")
    # P^2 = 2 I for a=(2,1)
    for x0 in range(MODULUS):
        for x1 in range(MODULUS):
            y0 = (WEIGHTS[0] * x1) % MODULUS
            y1 = (WEIGHTS[1] * x0) % MODULUS
            z0 = (WEIGHTS[0] * y1) % MODULUS
            z1 = (WEIGHTS[1] * y0) % MODULUS
            need((z0, z1) == ((2 * x0) % MODULUS, (2 * x1) % MODULUS), "P^2 = 2I")
    from math import gcd, prod

    expected = (MODULUS**DIMENSION) * prod(
        gcd(MODULUS, (WEIGHTS[i] * WEIGHTS[DIMENSION - 1 - i] - 1) % MODULUS)
        for i in range(DIMENSION)
    )
    need(expected == RAW_AGREEMENTS, "formula (5) raw agreements")


def run_boolean_fixture(*, normalize: bool, wrong_scale: int | None = None):
    """Execute unchanged outer.body_ordinary on Boolean origin planes.

    Returns (agreements_with_J, volume, planes, meters).
    """
    with installed_outer() as outer:
        from cardinal_counts import Count
        from records import Tape
        from words import Arena, Ring

        q = 3
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
        scale_factor = SCALE_FACTOR if wrong_scale is None else wrong_scale
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
                            nh[1] = (nh[1] * scale_factor) % modulus
                            nd[0] = (nd[0] * scale_factor) % modulus
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
            # Wrong-scale controls may collapse the address permutation; only the
            # successful Norm path is required to keep origin labels bijective.
            if normalize and wrong_scale is None:
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
    """Pinned padding.complete copy traffic when added=0 (rows=stock)."""
    # plan_rows(rows=1,stock=1) ⇒ padded=1, added=0; each transform copies
    # prefixes*rows*body = volume cells inbound and again on restrict.
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
    # Negative controls
    bad_scale_agrees, _, _, _ = run_boolean_fixture(normalize=True, wrong_scale=1)
    need(bad_scale_agrees < NORMALIZED_AGREEMENTS, "identity-scale control fails")
    bad_scale2, _, _, _ = run_boolean_fixture(normalize=True, wrong_scale=0)
    need(bad_scale2 < NORMALIZED_AGREEMENTS, "zero-scale control fails")
    invoice = closed_form_invoice()
    return {
        "schema_version": 1,
        "claim": (
            "On the unchanged PR2808 Boolean fixture (M=3,n=2,a=(2,1)), "
            "metered Norm∘F_a admits the ordinary wrapper at 81/81 with a "
            "complete paid inventory (scale+inverse+source-access+restoration+"
            "frame/copy); raw F_a alone fails at 9/81. No new kappa."
        ),
        "fixture": {
            "q": 3,
            "w": 1,
            "weights": list(WEIGHTS),
            "prefixes": 1,
            "rows": 1,
            "stock": 1,
            "gap": 1,
            "suffix": 1,
            "address_volume": ADDRESS_VOLUME,
            "bit_planes": PLANES,
            "wrapper": "research/selected-outer-borrowing-wrapper/outer.py:body_ordinary",
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
            "wrong_scale_1_agreements": bad_scale_agrees,
            "wrong_scale_0_agreements": bad_scale2,
        },
        "invoice": invoice,
        "kappa_decimal": KAPPA_DECIMAL,
        "kappa_fraction": KAPPA_FRACTION,
        "no_new_kappa": True,
    }
