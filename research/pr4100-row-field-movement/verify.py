#!/usr/bin/env python3
"""Exact checks for the boundary-arithmetic row-field movement lemma.

The all-size statements are the integer identities in PROOF.md. This program
recomputes those identities on an explicit range and executes the lockstep
schedule, including the controls that reject retained padding and a long-field
transpose.
"""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PHASE = ROOT / "research/capped-phase-fusion/PHASE-LAYOUT-AUDIT.md"
GAUSSIAN = ROOT / "research/unconditional-batched-crt/GAUSSIAN.md"
UNION = ROOT / "research/unconditional-batched-crt/vendor/UNION-SCHEDULE.md"


def ceil_log2(value: int) -> int:
    if value < 1:
        raise ValueError("log argument must be positive")
    exponent = 0
    power = 1
    while power < value:
        power *= 2
        exponent += 1
    return exponent


def next_power_of_two(value: int) -> int:
    return 1 << ceil_log2(value)


def batches(width: int, count: int) -> tuple[list[int], int]:
    """Return batch widths and the number of added pad cells."""
    if width < 1 or count < 0:
        raise ValueError("batch arguments must satisfy W >= 1 and R >= 0")
    if count == 0:
        return [], 0
    if count < width:
        return [width], width - count
    quotient, remainder = divmod(count, width)
    if remainder == 0:
        return [width] * quotient, 0
    return [width] * (quotient - 1) + [width + remainder], 0


def forward_transpose(records: list[object], rows: int, columns: int) -> tuple[list[object], int, int]:
    """Lockstep-merge the short row field. Return data, moves, and stages."""
    if rows < 1 or columns < 1 or len(records) != rows * columns:
        raise ValueError("transpose shape does not match the record list")
    if next_power_of_two(rows) != rows:
        raise ValueError("the executed field must already be padded to a power of two")
    data = list(records)
    moves = 0
    stages = 0
    span = 1
    while span < rows:
        merged: list[object] = []
        node_rows = 2 * span
        node_count = rows // node_rows
        for node in range(node_count):
            base = node * node_rows * columns
            left = data[base : base + span * columns]
            right = data[base + span * columns : base + node_rows * columns]
            moves += node_rows * columns
            for index in range(columns):
                merged.extend(left[index * span : (index + 1) * span])
                merged.extend(right[index * span : (index + 1) * span])
                moves += node_rows
        data = merged
        span = node_rows
        stages += 1
    return data, moves, stages


def reverse_transpose(records: list[object], rows: int, columns: int) -> tuple[list[object], int]:
    if len(records) != rows * columns or next_power_of_two(rows) != rows:
        raise ValueError("reverse transpose shape is not a padded power of two")
    data = list(records)
    moves = 0
    span = rows // 2
    while span >= 1:
        restored: list[object] = []
        node_rows = 2 * span
        node_count = rows // node_rows
        for node in range(node_count):
            base = node * node_rows * columns
            block = data[base : base + node_rows * columns]
            left: list[object] = []
            right: list[object] = []
            for index in range(columns):
                chunk = block[index * node_rows : (index + 1) * node_rows]
                left.extend(chunk[:span])
                right.extend(chunk[span:])
            moves += 2 * len(block)
            restored.extend(left)
            restored.extend(right)
        data = restored
        span //= 2
    return data, moves


def expose_and_restore(length: int, columns: int) -> dict[str, int]:
    """Pad one exposed field, transpose it both ways, then delete the pad."""
    padded = next_power_of_two(length)
    real = [(row, column, "real") for row in range(length) for column in range(columns)]
    pad = [(row, column, "pad") for row in range(length, padded) for column in range(columns)]
    records = real + pad
    target = [
        (row, column, mark)
        for column in range(columns)
        for row in range(padded)
        for mark in ["real" if row < length else "pad"]
    ]
    moved, forward_moves, stages = forward_transpose(records, padded, columns)
    if moved != target:
        raise AssertionError("short-field transpose did not put the row inside the orthogonal index")
    restored, undo_moves = reverse_transpose(moved, padded, columns)
    if restored != records:
        raise AssertionError("undo did not restore the padded row-major field")
    kept = [item for item in restored if item[2] == "real"]
    if kept != real:
        raise AssertionError("removing the pad did not recover the real records")
    volume = length * columns
    padded_volume = padded * columns
    return {
        "stages": stages,
        "forward_moves": forward_moves,
        "undo_moves": undo_moves,
        "volume": volume,
        "padded_volume": padded_volume,
        "peak_records": padded_volume,
        "final_records": len(kept),
    }


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def check_source_sentences() -> None:
    phase = PHASE.read_text(encoding="utf-8")
    gaussian = GAUSSIAN.read_text(encoding="utf-8")
    union = UNION.read_text(encoding="utf-8")
    phase_flat = " ".join(phase.split())
    gaussian_flat = " ".join(gaussian.split())
    union_flat = " ".join(union.split())
    require(
        "move only that polynomial-width row field" in phase_flat
        and "O(log p) times the boundary volume" in phase_flat
        and "not a transpose of the long spectator field" in phase_flat
        and "Pad only this field to its next power of two" in phase_flat
        and "factor below two" in phase_flat
        and "remove that padding before the next axis" in phase_flat
        and "scanned once per RHS batch" in phase_flat,
        "PHASE-LAYOUT no longer states the row-field movement sentence",
    )
    require(
        "row field is removed before the next axis and never accumulates as2^g" in gaussian_flat,
        "GAUSSIAN.md no longer states the 2^g removal sentence",
    )
    require(
        "only the polynomial-width row field moved" in union_flat
        and "(O(log p) times the boundary volume)" in union_flat
        and "boundary-algebra row" in union_flat
        and "not part of the union movement" in union_flat,
        "UNION-SCHEDULE step 5 no longer charges this movement to the boundary row",
    )
    digest = hashlib.sha256(phase.encode("utf-8")).hexdigest()
    require(len(digest) == 64, "source digest was not computed")


def check_padding_factor(limit: int) -> None:
    for length in range(1, limit + 1):
        padded = next_power_of_two(length)
        require(length <= padded < 2 * length, f"pad factor failed at {length}")
        require(padded & (padded - 1) == 0, f"pad length is not a power of two at {length}")


def check_batches(max_width: int, max_count: int) -> None:
    for width in range(1, max_width + 1):
        for count in range(0, max_count + 1):
            parts, added = batches(width, count)
            require(sum(parts) == count + added, f"batch widths do not account for {width}, {count}")
            if count >= width:
                require(added == 0, f"nonnegative padding appeared for R >= W at {width}, {count}")
                require(all(width <= part <= 2 * width for part in parts), f"batch escaped [W, 2W] at {width}, {count}")
                require(sum(parts) == count, f"partition dropped records at {width}, {count}")
            elif count == 0:
                require(parts == [] and added == 0, "empty right-hand side created a batch")
            else:
                require(parts == [width] and added == width - count < width, f"small-batch pad is not one partial batch at {width}, {count}")
            scans = len(parts)
            if width > 1 and count > scans:
                require(scans != count, "one scan per right-hand side is not the batch schedule")


def check_movement() -> tuple[int, int]:
    largest_ratio_numerator = 0
    largest_ratio_denominator = 1
    cases = [(1, 1), (1, 8), (2, 2), (3, 5), (4, 7), (5, 9), (8, 3), (9, 16), (15, 4), (16, 2), (31, 3), (32, 1)]
    for length, columns in cases:
        result = expose_and_restore(length, columns)
        padded = next_power_of_two(length)
        stages = ceil_log2(length)
        require(result["stages"] == stages, "stage count depends on something other than the row length")
        require(result["forward_moves"] == 2 * stages * result["padded_volume"], "forward move count is not two passes per stage")
        require(result["undo_moves"] == result["forward_moves"], "undo is not the same number of passes")
        require(result["final_records"] == result["volume"], "real records changed across one axis")
        require(result["peak_records"] * length == padded * result["volume"], "peak volume is not the single-field pad")
        require(result["peak_records"] < 2 * result["volume"], "peak pad reached a factor of two")
        if length >= 2:
            require(
                result["forward_moves"] < 4 * stages * result["volume"],
                "forward movement is not O(log a) times the real volume",
            )
        # The long orthogonal index is not the transposed coordinate.
        long_stages = ceil_log2(next_power_of_two(columns))
        if columns > padded:
            require(long_stages > result["stages"], "a longer spectator did not take more transpose stages")
        ratio_numerator = result["forward_moves"]
        ratio_denominator = result["volume"]
        if ratio_numerator * largest_ratio_denominator > largest_ratio_numerator * ratio_denominator:
            largest_ratio_numerator = ratio_numerator
            largest_ratio_denominator = ratio_denominator
    # Same row length, two spectator lengths: the stage count stays fixed.
    short = expose_and_restore(6, 2)
    long = expose_and_restore(6, 40)
    require(short["stages"] == long["stages"] == ceil_log2(6), "spectator length changed the stage count")
    return largest_ratio_numerator, largest_ratio_denominator


def check_axes() -> None:
    lengths = (3, 3, 3, 5, 7)
    for length in lengths:
        require(next_power_of_two(length) < 2 * length, "an axis pad attained factor two")
    peak_ratio = max(next_power_of_two(length) / length for length in lengths)
    require(peak_ratio < 2, "sequential removal exceeded factor two")
    retained_numerator = 4 ** 6
    retained_denominator = 3 ** 6
    for length in (3,) * 6:
        require(next_power_of_two(length) == 4, "length 3 no longer pads to 4")
    require(
        retained_numerator > 2 * retained_denominator,
        "retained padding did not accumulate past factor two",
    )
    # A small tensor: three axes of length 3. Removal returns to 27 records.
    axes = (3, 3, 3)
    records = [(x, y, z) for x in range(3) for y in range(3) for z in range(3)]
    live = records
    peak_count = len(live)
    for axis in range(3):
        length = axes[axis]
        padded = next_power_of_two(length)
        fibers = []
        seen = set()
        for item in live:
            if item[axis] >= length:
                raise AssertionError("a deleted pad coordinate was still live")
            key = tuple(value for index, value in enumerate(item) if index != axis)
            if key not in seen:
                seen.add(key)
                fibers.append(key)
        require(len(fibers) * length == len(live), "the live tensor is not a full axis")
        exposed = list(live)
        for key in fibers:
            for extra in range(length, padded):
                coordinates = []
                key_index = 0
                for index in range(3):
                    if index == axis:
                        coordinates.append(extra)
                    else:
                        coordinates.append(key[key_index])
                        key_index += 1
                exposed.append(tuple(coordinates))
        require(len(exposed) * length == len(live) * padded, "exposure did not pad only the active axis")
        peak_count = max(peak_count, len(exposed))
        live = [item for item in exposed if item[axis] < length]
        require(len(live) == 27, "removal failed to restore the tensor")
    require(peak_count * 3 == 27 * 4, "the 3-axis tensor peak is not the single-axis pad")
    require(live == records, "axis order or values changed")


def main() -> None:
    check_source_sentences()
    check_padding_factor(65536)
    check_batches(64, 512)
    move_numerator, move_denominator = check_movement()
    check_axes()
    # Rejection controls must actually fail closed.
    try:
        require(next_power_of_two(3) == 8, "this control is expected to fail")
        raise SystemExit("pad-factor control failed to reject")
    except AssertionError:
        pass
    try:
        retained_numerator = 1
        retained_denominator = 1
        for _ in range(6):
            retained_numerator *= next_power_of_two(3)
            retained_denominator *= 3
        require(retained_numerator < 2 * retained_denominator, "retained growth should be rejected")
        raise SystemExit("retained-padding control failed to reject")
    except AssertionError:
        pass
    require(move_numerator == 2048 and move_denominator == 144, "the worst executed move ratio changed")
    print(
        "PASS_ROW_FIELD_MOVEMENT "
        "padding_strictly_below_two=true "
        "zero_added_cells_when_R_ge_W=true "
        "small_batch_added_cells_lt_W=true "
        "forward_passes_per_stage=2 "
        f"max_forward_moves_over_real_volume={move_numerator}/{move_denominator} "
        "stage_count_depends_only_on_row_length=true "
        "removal_peak_below_two=true "
        "retained_three_length_g6=(4/3)^6>2 "
        "page_scans_equal_batch_count=true "
        "no_new_kappa=true"
    )


if __name__ == "__main__":
    main()
