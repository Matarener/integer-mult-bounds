#!/usr/bin/env python3
"""Exact check of deferred P112 five-plane endpoint corrections."""
from __future__ import annotations
import hashlib
import importlib.util
import json
from fractions import Fraction as Q
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
PREDECESSOR = ROOT / "research/five-plane-port-p112-seed1f7fdfe4"


def need(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def load_predecessor_core():
    spec = importlib.util.spec_from_file_location("five_plane_core", PREDECESSOR / "core.py")
    need(spec is not None and spec.loader is not None, "cannot load predecessor core")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def apply_c(state: dict[int, tuple[int, int]], q: int) -> dict[int, tuple[int, int]]:
    """Apply the unnormalised Gaussian-dyadic lift C_q used by the predecessor."""
    out: dict[int, tuple[int, int]] = {}

    def add(index: int, real: int, imag: int) -> None:
        old_real, old_imag = out.get(index, (0, 0))
        out[index] = (old_real + real, old_imag + imag)

    for index, (real, imag) in state.items():
        add(index, real - imag, real + imag)
        add(index ^ q, real + imag, imag - real)
    return {index: value for index, value in out.items() if value != (0, 0)}


def xor_group(labels: list[int], group: list[int]) -> int:
    shift = 0
    for port in group:
        shift ^= labels[port]
    return shift


def verify_partition(candidate: dict) -> list[list[int]]:
    groups = candidate["groups"]
    residual = candidate["residual"]
    blocks = candidate["blocks"]
    need(blocks == groups + [residual], "block order differs from the cover")
    need(len(groups) == 22 and all(len(g) == 5 for g in groups), "expected 22 five-frames")
    need(len(residual) == 2, "expected one residual pair")
    flat = [port for group in blocks for port in group]
    need(sorted(flat) == list(range(112)), "blocks do not partition P112")
    return blocks


def main() -> None:
    # Direct runs enforce the package's live source pins too.
    source_manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    for row in source_manifest["files"]:
        if row["usage"] == "input":
            path = ROOT / row["path"]
            need(path.is_file(), "missing input: " + row["path"])
            need(hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"],
                 "input hash mismatch: " + row["path"])

    core = load_predecessor_core()
    labels, _ = core.load_sources()
    record = json.loads((PREDECESSOR / "CANDIDATE.json").read_text())
    candidate = record["candidate"]
    blocks = verify_partition(candidate)
    need(len(labels) == 112, "wrong selected label count")

    block_deltas = [xor_group(labels, group) for group in blocks]
    all_labels_xor = 0
    for label in labels:
        all_labels_xor ^= label
    all_deltas_xor = 0
    for delta in block_deltas:
        all_deltas_xor ^= delta
    need(all_labels_xor == 0, "selected P112 labels no longer have zero xor")
    need(all_deltas_xor == all_labels_xor, "partitioned correction xor differs from label xor")
    need(core.rank_rows(block_deltas, core.DIM) == 9, "expected full-rank block correction set")
    expected_deltas = [98, 70, 100, 274, 50, 506, 247, 352, 304, 56, 19, 274,
                       22, 445, 152, 388, 268, 254, 463, 508, 322, 475, 235]
    need(block_deltas == expected_deltas, "per-block endpoint translations changed")

    # Each local C_E^2 translation is checked on every basis address (512 states).
    local_cases = 0
    for group, delta in zip(blocks, block_deltas):
        for start in range(1 << core.DIM):
            state = {start: (1, 0)}
            for port in group + group:
                state = apply_c(state, labels[port])
            expected = {start ^ delta: (1 << (2 * len(group)), 0)}
            need(state == expected, "local C_E^2 endpoint identity failed")
            local_cases += 1
    need(local_cases == 23 * (1 << core.DIM), "wrong local endpoint case count")

    # If these corrections share one address register, their product is one
    # translation by xor(block_deltas), hence identity on every address state.
    for start in range(1 << core.DIM):
        destination = start
        for delta in block_deltas:
            destination ^= delta
        need(destination == start, "deferred global endpoint correction is nonidentity")

    hist = {int(rank): int(count) for rank, count in candidate["copy_rank_histogram"].items()}
    profile, centre = core.profile_for(hist)
    fused_screen = core.moment_screen(profile, centre)
    need(fused_screen == candidate["moment_screen_u5"], "predecessor local screen changed")
    separate_profile = profile.copy()
    separate_profile[1] = separate_profile.get(1, 0) + len(blocks)
    separate_screen = core.moment_screen(separate_profile, centre + len(blocks))
    need(separate_screen == candidate["one_unit_per_aggregate_translation_screen"],
         "separate-correction screen changed")
    need(Q(fused_screen["ceiling_upper"]) > Q(separate_screen["ceiling_upper"]),
         "deferring corrections did not recover local ceiling")
    overhead = candidate["all_in_rank1_overhead_threshold"]
    max_overhead = overhead["largest_passing"]["extra_rank1_equivalent_charge"]
    need(max_overhead == 157 and max_overhead - len(blocks) == 134,
         "rank-one overhead arithmetic changed")

    # Negative controls: one missing block leaves its nonzero translation behind;
    # a duplicated port violates the exact cover before any algebra is applied.
    missing_xor = 0
    for delta in block_deltas[:-1]:
        missing_xor ^= delta
    need(missing_xor != 0, "missing-block control did not expose endpoint debt")
    bad_blocks = [group[:] for group in blocks]
    bad_blocks[-1][0] = bad_blocks[0][0]
    bad_flat = [port for group in bad_blocks for port in group]
    need(sorted(bad_flat) != list(range(112)), "duplicate-port control was accepted")

    print("PASS_GLOBAL_P112_ENDPOINT_CANCELLATION",
          f"blocks={len(blocks)}", f"local_basis_cases={local_cases}",
          f"label_xor={all_labels_xor}", f"delta_rank=9",
          f"separate_a_ceiling={separate_screen['ceiling_upper_decimal']:.12f}",
          f"deferred_a_ceiling={fused_screen['ceiling_upper_decimal']:.12f}",
          f"rank1_overhead={max_overhead}",
          "physical_shared_register=OPEN")


if __name__ == "__main__":
    main()
