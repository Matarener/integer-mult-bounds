"""Whole prepared tiles: periodic seams, repeated starts and a clipped last block."""
from hashlib import sha256
from expansion_sources import require
from expansion_check_block import expected_page, inputs, models, packet_bytes, periodic_error


def run(case):
    from cardinal_counts import Count
    from check_support import no_decode
    from expansion_tile import Tile
    from expansion_tile_geometry import TileHeader
    from expansion_tile_prepare import TilePreparation, copy_cells
    from gaussian_rationals import read_count
    from records import Tape
    from ring_check_words import body, decode
    from ring_words import Signed, read_signed, write_signed
    from router_metadata import owned
    from session import erase_marker
    from words import BLANK
    require(case in ("overlap", "wrap"), "declared complete tile fixture")
    if case == "overlap":
        s, t, alpha, radius, source_start, source_count, capacity, start, length = 3, 4, 2, 1, -3, 8, 8, 0, 2
    else:
        s, t, alpha, radius, source_start, source_count, capacity, start, length = 3, 4, 2, 2, -1, 9, 16, 3, 3
    p, bits, sigma = 4, 32, 3
    preparation, tile = TilePreparation(), Tile()
    page = returned = None
    source = Tape()
    with owned(*(Count.literal(v) for v in
                 (s, t, alpha, radius, abs(source_start), source_count, capacity, abs(start), length, p, bits, sigma))) as args:
        S, T, a, b, source_origin, count, padded, target_origin, target_count, target_p, P, scale = args
        saved = [(bytes(value.tape.cells), value.tape.head) for value in args]
        try:
            with no_decode():
                page = preparation.run_explicit(S, T, a, b, Signed(source_origin, source_start < 0),
                    count, padded, Signed(target_origin, start < 0), target_count, target_p, P, scale)
            page_bytes = packet_bytes(page)
            expected, descriptions = [], []
            word_count = 2*capacity
            with owned(TileHeader(page)) as (header,):
                require(decode(header.blocks) == (length+radius-1)//radius
                        and decode(header.input_capacity) == capacity and decode(header.source_count) == source_count,
                        "complete expansion catalogue metadata")
                offset = 0
                for _ in range(decode(header.blocks)):
                    block_page = Tape()
                    try:
                        with owned(read_count(page)) as (cells,):
                            copy_cells(page, block_page, cells)
                        block_page.rewind()
                        m = min(radius, length-offset)
                        block_start, factors, c = expected_page(block_page, s, t, alpha, radius,
                                                               start+offset, m, p, bits, sigma)
                        data = inputs(block_start, len(factors["A"]), s)
                        values, premature, error = models(data, factors, c, s, t, alpha, block_start,
                                                         start+offset, m, p, bits, sigma)
                        expected.extend(values)
                        descriptions.append({"source_start": block_start, "source_length": len(data),
                                             "target_start": start+offset, "target_length": m,
                                             "values": values, "premature_values": premature,
                                             "finite_error": str(error)})
                        word_count += 4*len(data)+6*m+8
                        offset += m
                    finally:
                        block_page.clear()
                        erase_marker(block_page)
                require(page.read() == BLANK and offset == length, "complete expansion block catalogue")
            page.rewind()
            global_error = periodic_error(expected, s, t, alpha, start, p)
            with owned(Count.literal(p+2)) as (width,):
                data = inputs(source_start, source_count, s)+[(0, 0)]*(capacity-source_count)
                for pair in data:
                    for value in pair:
                        numerator = int(value*(1 << p))
                        with owned(Signed(Count.literal(abs(numerator)), numerator < 0)) as (encoded,):
                            write_signed(encoded, source, width)
                source.rewind()
                source_bytes = body(source)
                before = dict(tile.word.calls)
                with no_decode():
                    returned = tile.run(page, source)
                raw = body(returned)
                actual = []
                for _ in range(length):
                    with owned(read_signed(returned, width), read_signed(returned, width)) as (real, imaginary):
                        actual.append([(-1 if v.negative else 1)*decode(v.magnitude) for v in (real, imaginary)])
                require(actual == expected and returned.read() == BLANK,
                        "complete streamed expansion equals independently staged blocks")
                require(any(v for pair in actual for v in pair), "nonzero complete expansion tile")
                calls = {key: tile.word.calls[key]-before[key] for key in before}
                require(sum(calls.values()) == word_count, "whole tile word invoice includes padding validation")
                first = descriptions[0]["source_start"]-source_start
                end = first+descriptions[0]["source_length"]
                fresh = descriptions[0]["source_length"]
                overlap = 0
                for record in descriptions[1:]:
                    begin = record["source_start"]-source_start
                    overlap += end-begin
                    following = begin+record["source_length"]
                    fresh += following-end
                    end = following
                expected_counts = {"blocks": len(descriptions), "validation_records": capacity,
                                   "fresh_records": fresh, "overlap_records": overlap,
                                   "initial_skipped": first, "tail_skipped": capacity-end}
                require(tile.last_counts == expected_counts
                        and first+fresh+capacity-end == capacity,
                        "one validation scan and one monotone source scan with bounded overlaps")
                if case == "overlap":
                    require(descriptions[0]["source_start"] == descriptions[1]["source_start"]
                            and overlap > 0, "actual zero-advance source-window reuse")
                else:
                    require(start < t < start+length and descriptions[-1]["target_length"] < radius
                            and capacity > source_count, "actual period crossing, clipped last block and zero padding")
                require(packet_bytes(page) == page_bytes and body(source) == source_bytes,
                        "tile preserves borrowed complete catalogue and input")
                require(saved == [(bytes(value.tape.cells), value.tape.head) for value in args],
                        "tile producer preserves borrowed global parameters")
                require(preparation.closed and not preparation.pool.live and tile.closed and not tile.pool.live,
                        "complete tile owner restoration")
                result = {"case": case, "s": s, "t": t, "alpha": alpha, "radius": radius,
                          "source": [source_start, source_count, capacity], "target": [start, length],
                          "p": p, "P": bits, "sigma": sigma, "values": actual,
                          "page_sha256": sha256(page_bytes).hexdigest(), "core_sha256": sha256(raw).hexdigest(),
                          "periodic_error": str(global_error), "blocks": descriptions,
                          "word_calls": calls, "stream_counts": tile.last_counts,
                          "preparation_counts": preparation.last_counts,
                          "preparation_pool_peak": preparation.pool.peak, "tile_pool_peak": tile.pool.peak,
                          "scope": "complete encoded tile production and streaming at explicit finite grids; no production-size tile execution"}
        finally:
            for tape in (returned, page, source):
                if tape is not None:
                    tape.clear()
                    erase_marker(tape)
            tile.idle()
    return result
