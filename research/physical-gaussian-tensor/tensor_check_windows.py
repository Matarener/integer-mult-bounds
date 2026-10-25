"""Periodic seams, overlap reuse, gaps, equal ends and exact source-core order."""
from hashlib import sha256
from unittest.mock import patch
from tensor_sources import require


def run():
    from cardinal_counts import Count
    from check_support import no_decode
    from expansion_check_block import packet_bytes
    from expansion_records import write_integer
    from gaussian_rationals import write_count
    from records import Tape
    from ring_words import Signed
    from router_metadata import owned
    from session import erase_marker
    from tensor_windows import CoreAssembly, PeriodicWindows
    from words import BLANK
    emitter, assembler = PeriodicWindows(), CoreAssembly()
    evidence = []
    def clear(tape):
        tape.clear()
        erase_marker(tape)
    def packet(data):
        tape = Tape()
        for bit in data:
            tape.append(bit)
        tape.rewind()
        return tape
    def descriptors(windows):
        tape = Tape()
        for start, length in windows:
            with owned(Signed(Count.literal(abs(start)), start < 0), Count.literal(length)) as (a, b):
                write_integer(a, tape)
                write_count(b, tape)
        tape.rewind()
        return tape
    def bits(value, width):
        return bytes((value >> bit) & 1 for bit in range(width))
    def restored(owner):
        require(owner.closed and not owner.pool.live
                and all(t.head == 1 and all(v == BLANK for v in t.cells) for t in owner.pool.tapes),
                "complete halo/core owner restoration")
    cases = ((2, 7, 8, 8, 5, ((-2, 6), (-1, 7), (1, 7), (3, 7))),
             (2, 8, 8, 4, 5, ((-1, 4), (1, 4), (3, 4), (5, 4))),
             (1, 9, 12, 3, 5, ((-4, 2), (1, 2), (6, 2))),
             (1, 11, 16, 9, 5, ((-2, 9), (0, 7))))
    for C, s, t, q, R, windows in cases:
        raw = b"".join(bits(c*s+j+1, R) if j < s else bytes(R) for c in range(C) for j in range(t))
        expected = b"".join(b"".join(bits(c*s+(j % s)+1, R) for j in range(start, start+length))
                            +bytes((q-length)*R) for c in range(C) for start, length in windows)
        source, frames = packet(raw), descriptors(windows)
        frame_bytes = packet_bytes(frames)
        with owned(*(Count.literal(v) for v in (C, s, t, len(windows), q, R))) as parameters:
            saved = [(bytes(v.tape.cells), v.tape.head) for v in parameters]
            with no_decode():
                output = emitter.run(source, frames, *parameters)
            actual = packet_bytes(output)
            require(actual == expected, "actual periodic windows match independent modular source indexing")
            fresh, overlap, gaps, skipped = windows[0][1], 0, 0, 0
            previous_start = windows[0][0]
            end = sum(windows[0])
            for start, length in windows[1:]:
                if start >= end:
                    gaps += start-end
                    fresh += length
                else:
                    overlap += end-start
                    fresh += length-(end-start)
                    skipped += start-previous_start
                previous_start, end = start, start+length
            expected_counts = dict(rows=C, windows=C*len(windows), input_records=C*s,
                                   fresh_records=C*fresh, overlap_records=C*overlap,
                                   initial_skipped=C*(s+windows[0][0]), gaps_skipped=C*gaps,
                                   retained_skipped=C*skipped, tail_skipped=C*(2*s-end))
            require(emitter.last_counts == expected_counts
                    and expected_counts["initial_skipped"]+C*(fresh+gaps)+expected_counts["tail_skipped"] == C*3*s,
                    "whole triple-lift monotone scan and bounded overlap invoice")
            require(packet_bytes(source) == raw and packet_bytes(frames) == frame_bytes
                    and saved == [(bytes(v.tape.cells), v.tape.head) for v in parameters],
                    "halo preserves borrowed source, descriptors and parameters")
            restored(emitter)
            evidence.append({"C": C, "period": s, "stored": t, "capacity": q, "record_bits": R,
                             "windows": [list(v) for v in windows], "counts": emitter.last_counts,
                             "output_sha256": sha256(actual).hexdigest()})
            clear(output)
        clear(source)
        clear(frames)
    C, s, t, q, R = 2, 7, 8, 2, 5
    cores = ((0, 1), (1, 2), (3, 2), (5, 2))
    raw = b"".join(b"".join(bits(c*s+j+1, R) for j in range(start, start+length))
                   +bytes((q-length)*R) for c in range(C) for start, length in cores)
    expected = b"".join(bits(c*s+j+1, R) if j < s else bytes(R) for c in range(C) for j in range(t))
    source, frames = packet(raw), descriptors(cores)
    with owned(*(Count.literal(v) for v in (C, s, t, len(cores), q, R))) as parameters:
        with no_decode():
            output = assembler.run(source, frames, *parameters)
        require(packet_bytes(output) == expected and packet_bytes(source) == raw,
                "full core concatenation restores original increasing source indices and dyadic padding")
        assembly_hash = sha256(packet_bytes(output)).hexdigest()
        clear(output)
        restored(assembler)
    clear(source)
    clear(frames)
    controls = []
    with owned(*(Count.literal(v) for v in (1, 7, 8, 2, 8, 4))) as parameters:
        raw = b"".join(bits(j+1, 4) if j < 7 else bytes(4) for j in range(8))
        good = ((-2, 6), (-1, 7))
        def reject(call, fragment):
            try:
                with no_decode():
                    call()
            except ValueError as error:
                require(fragment in str(error), "specific periodic-window failure: " + str(error))
            else:
                raise ValueError("missing periodic-window failure")
        for label, data, windows, fragment in (
                ("short_input", raw[:-1], good, "zero tensor padding"),
                ("extra_input", raw+b"\x00", good, "input rectangle"),
                ("nonzero_source_pad", raw[:-1]+b"\x01", good, "zero tensor padding"),
                ("left_lift", raw, ((-8, 6), (-1, 7)), "begins within triple"),
                ("right_lift", raw, ((-2, 6), (12, 7)), "ends within triple"),
                ("backward_start", raw, ((-2, 6), (-3, 8)), "monotone halo starts"),
                ("backward_end", raw, ((-2, 6), (-1, 2)), "monotone halo ends"),
                ("capacity", raw, ((-2, 9), (-1, 7)), "rectangular capacity")):
            source, frames = packet(data), descriptors(windows)
            frame_bytes = packet_bytes(frames)
            reject(lambda: emitter.run(source, frames, *parameters), fragment)
            require(packet_bytes(source) == data and packet_bytes(frames) == frame_bytes
                    and emitter.output.read() == BLANK, "failed halo emission restores ports and clears partial output")
            restored(emitter)
            controls.append(label)
            clear(source)
            clear(frames)
        source, frames = packet(raw), descriptors(good)
        original = emitter.copy_records
        def allocate(source, target, records, width, counter):
            original(source, target, records, width, counter)
            if counter == "overlap_records":
                Tape()
        with patch.object(emitter, "copy_records", allocate):
            reject(lambda: emitter.run(source, frames, *parameters), "physical Tape allocation inside")
        restored(emitter)
        controls.append("late_sealed_allocation")
        with no_decode():
            output = emitter.run(source, frames, *parameters)
        snapshot = packet_bytes(output)
        reject(lambda: emitter.run(source, frames, *parameters), "consume prior periodic-window output")
        require(packet_bytes(output) == snapshot, "protected complete halo output survives rejected reuse")
        controls.append("protected_halo_return")
        clear(output)
        clear(source)
        clear(frames)
    # A late nonzero core-padding record must not escape through assembly.
    with owned(*(Count.literal(v) for v in (1, 7, 8, 4, 2, 4))) as parameters:
        frames = descriptors(cores)
        raw = b"".join(b"".join(bits(j+1, 4) for j in range(start, start+length))
                       +bytes((2-length)*4) for start, length in cores)
        wrong = raw[:4]+b"\x01"+raw[5:]
        source = packet(wrong)
        reject(lambda: assembler.run(source, frames, *parameters), "zero tensor padding")
        require(packet_bytes(source) == wrong and assembler.output.read() == BLANK,
                "core assembly rejects nonzero discarded slots and clears partial output")
        restored(assembler)
        controls.append("nonzero_core_pad")
        clear(source)
        source = packet(raw)
        with no_decode():
            output = assembler.run(source, frames, *parameters)
        clear(output)
        clear(source)
        clear(frames)
        restored(assembler)
    return {"halo_cases": evidence, "assembly_sha256": assembly_hash,
            "controls": controls, "halo_pool_peak": emitter.pool.peak, "assembly_pool_peak": assembler.pool.peak,
            "scope": "complete physical periodic halo and core streams; numerical tensor composition remains separate"}
