"""Complete tile ownership, malformed boundaries, sealed allocation and reuse."""
from hashlib import sha256
from unittest.mock import patch
from expansion_check_block import expected_page, inputs, models, packet_bytes
from expansion_sources import require


def run():
    from cardinal_counts import Count
    from check_support import no_decode
    from expansion_tile import Tile
    from expansion_tile_geometry import TileHeader
    from expansion_tile_prepare import TilePreparation, copy_cells
    import expansion_prepare
    from gaussian_rationals import read_count
    from records import Tape
    from ring_check_words import decode
    from ring_words import Signed, read_signed, write_signed
    from router_metadata import owned
    from session import erase_marker
    from words import BLANK, RIGHT
    preparation, tile = TilePreparation(), Tile()

    def packet(data):
        result = Tape()
        for value in data:
            result.append(value)
        result.rewind()
        return result

    def count_bytes(value):
        return bytes([(value >> bit) & 1 for bit in range(max(1, value.bit_length()))]+[RIGHT])

    def position(data, fields):
        start = 0
        for _ in range(fields):
            start = data.index(RIGHT, start)+1
        return start

    def changed(data, field, value):
        start = position(data, field)
        end = data.index(RIGHT, start)+1
        return data[:start]+count_bytes(value)+data[end:]

    def clear(tape):
        tape.clear()
        erase_marker(tape)

    def restored(owner):
        require(owner.closed and not owner.pool.live
                and all(t.head == 1 and all(v == BLANK for v in t.cells) for t in owner.pool.tapes),
                "complete tile fixed scratch restoration")
        if hasattr(owner, "parameter_pool"):
            require(not owner.parameter_pool.live
                    and all(t.head == 1 and all(v == BLANK for v in t.cells) for t in owner.parameter_pool.tapes),
                    "complete tile parameter scratch restoration")

    def rejected(call, message):
        try:
            with no_decode():
                call()
        except ValueError as error:
            require(message in str(error), "specific tile rejection: " + message + ": " + str(error))
        else:
            raise ValueError("missing tile rejection: " + message)

    source = Tape()
    controls = []
    with owned(*(Count.literal(v) for v in (3, 4, 2, 1, 2, 5, 8, 0, 1, 4, 24, 0))) as args:
        s, t, alpha, radius, start, length, capacity, target, target_length, p, bits, sigma = args
        arguments = (s, t, alpha, radius, Signed(start, True), length, capacity,
                     Signed(target), target_length, p, bits, sigma)
        saved = [(bytes(v.tape.cells), v.tape.head) for v in args]
        with no_decode():
            page = preparation.run_explicit(*arguments)
        page_bytes = packet_bytes(page)
        restored(preparation)
        restored(preparation.block)
        rejected(lambda: preparation.run_explicit(*arguments), "consume prior expansion tile page")
        controls.append("protected_producer_page")
        require(packet_bytes(page) == page_bytes, "protected producer page survives rejected reuse")
        block_page = Tape()
        with owned(TileHeader(page)) as (header,):
            with owned(read_count(page)) as (cells,):
                copy_cells(page, block_page, cells)
        block_page.rewind()
        origin, factors, c = expected_page(block_page, 3, 4, 2, 1, 0, 1, 4, 24, 0)
        data = inputs(origin, 5, 3)
        expected, premature, error = models(data, factors, c, 3, 4, 2, origin, 0, 1, 4, 24, 0,
                                           check_premature=False)
        clear(block_page)
        page.rewind()
        with owned(Count.literal(6)) as (width,):
            for pair in data+[(0, 0)]*3:
                for value in pair:
                    integer = int(value*16)
                    with owned(Signed(Count.literal(abs(integer)), integer < 0)) as (encoded,):
                        write_signed(encoded, source, width)
            source.rewind()
            source_bytes = packet_bytes(source)
            with no_decode():
                result = tile.run(page, source)
            with owned(read_signed(result, width), read_signed(result, width)) as pair:
                actual = [[(-1 if v.negative else 1)*decode(v.magnitude) for v in pair]]
            require(actual == expected and result.read() == BLANK, "whole ownership tile matches separate staged oracle")
            result_bytes = packet_bytes(result)
            rejected(lambda: tile.run(page, source), "consume prior expansion tile output")
            require(packet_bytes(result) == result_bytes, "protected full tile output survives rejected reuse")
            controls.append("protected_tile_output")
            clear(result)
            child_start = position(page_bytes, 15)
            child = page_bytes[child_start:]
            factor_start = position(child, 14)
            factor_width = 30
            negative = bytes([1]*factor_width)
            bad_factor = child[:factor_start]+negative+child[factor_start+factor_width:]
            # Header edits keep the nested cell count truthful, so a semantic
            # rejection cannot hide behind an unrelated short-page failure.
            prefix = page_bytes[:position(page_bytes, 14)]
            def child_packet(value):
                return prefix+count_bytes(len(value))+value
            target_position = position(child, 13)
            bad_target = child[:target_position]+bytes([0])+count_bytes(1)+child[position(child, 14):]
            source_position = position(child, 12)
            bad_origin = child[:source_position]+bytes([1])+count_bytes(3)+child[position(child, 13):]
            padding = source_bytes[:60]+bytes([1])+source_bytes[61:]
            non_disk = bytes((24 >> i) & 1 for i in range(6))+source_bytes[6:]
            variants = (
                ("tile_version", changed(page_bytes, 0, 1), source_bytes, "tile version"),
                ("precision_guard", changed(page_bytes, 2, 23), source_bytes, "precision guard"),
                ("tile_block_count", changed(page_bytes, 11, 2), source_bytes, "block count"),
                ("source_capacity", changed(page_bytes, 8, 9), source_bytes, "padded capacity"),
                ("short_page", page_bytes[:-1], source_bytes, "catalogue cell"),
                ("extra_page", page_bytes+b"\x00", source_bytes, "streamed expansion tile"),
                ("short_input", page_bytes, source_bytes[:-1], "complete"),
                ("extra_input", page_bytes, source_bytes+b"\x00", "source extent"),
                ("nonzero_padding", page_bytes, padding, "zero expansion source padding"),
                ("input_outside_disk", page_bytes, non_disk, "disk-grid input"),
                ("child_precision", child_packet(changed(child, 1, 5)), source_bytes, "precision guard"),
                ("target_order", child_packet(bad_target), source_bytes, "ordered expansion target"),
                ("source_origin", child_packet(bad_origin), source_bytes, "begins in supplied halo"),
                ("negative_factor", child_packet(bad_factor), source_bytes, "nonnegative normalized"),
                ("zero_normalization", child_packet(child[:-factor_width]+bytes(factor_width)),
                 source_bytes, "positive normalized expansion reciprocal"),
            )
            for name, bad_page, bad_source, message in variants:
                first, second = packet(bad_page), packet(bad_source)
                try:
                    rejected(lambda: tile.run(first, second), message)
                    require(packet_bytes(first) == bad_page and packet_bytes(second) == bad_source,
                            "failed tile preserves both malformed borrowed ports")
                    tile.idle()
                    restored(tile)
                    restored(tile.block)
                    require(tile.output.read() == BLANK, "failed tile clears partial output")
                    controls.append(name)
                finally:
                    clear(first)
                    clear(second)
            def allocate(*args, **kwargs):
                Tape()
            with patch.object(tile, "copy_records", allocate):
                rejected(lambda: tile.run(page, source), "physical Tape allocation inside")
            controls.append("dynamic_physical_tape")
            with no_decode():
                result = tile.run(page, source)
            require(packet_bytes(result) == result_bytes and packet_bytes(page) == page_bytes
                    and packet_bytes(source) == source_bytes, "positive tile reuse after failed calls")
            clear(result)
        clear(page)
        with patch.object(expansion_prepare, "prepare_page", allocate):
            rejected(lambda: preparation.run_explicit(*arguments), "physical Tape allocation inside")
        controls.append("producer_dynamic_physical_tape")
        restored(preparation)
        restored(preparation.block)
        require(preparation.output.read() == BLANK, "failed producer clears partial catalogue")
        with no_decode():
            page = preparation.run_explicit(*arguments)
        require(packet_bytes(page) == page_bytes, "positive producer reuse preserves exact generated coefficients")
        require(saved == [(bytes(v.tape.cells), v.tape.head) for v in args], "complete producer preserves parameter ports")
        clear(page)
        tile.idle()
        restored(tile)
        restored(preparation)
    clear(source)
    return {"values": actual, "premature_values": premature, "finite_error": str(error),
            "controls": controls, "producer_calls": preparation.calls, "tile_calls": tile.calls,
            "page_sha256": sha256(page_bytes).hexdigest(), "core_sha256": sha256(result_bytes).hexdigest(),
            "producer_pool_peak": preparation.pool.peak, "tile_pool_peak": tile.pool.peak}
