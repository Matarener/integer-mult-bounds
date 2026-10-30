"""Actual two-axis coefficient preparation and original-coordinate bindings."""
from hashlib import sha256
from tensor_sources import require


def run():
    from cardinal_counts import Count
    from check_support import no_decode
    from expansion_records import read_integer
    from expansion_tile_geometry import TileHeader
    from gaussian_page import Header as CoreHeader
    from gaussian_rationals import read_count
    from ring_check_words import decode, tape, word_bits
    from router_metadata import owned
    from scratch_pool import ScratchPool
    from session import OuterScope, erase_marker, initialize_marker, sealed_constructors
    from tensor_catalogue import Catalogue, TensorPreparation, read_frame
    from tensor_fixture import CATALOGUE_SHA256, prepared_catalogue
    from expansion_check_block import packet_bytes
    from words import BLANK
    preparation = TensorPreparation()
    pool, evidence = ScratchPool(512), []
    scope = OuterScope(pool)
    for item in pool.tapes:
        erase_marker(item)
    sources, flags = tape(word_bits(7, 3)*2), tape(bytes((1,)))
    expected = {
        "expansion_windows": [(-2, 6), (-1, 7), (1, 7), (3, 7)],
        "compression_windows": [(-1, 4), (1, 4), (3, 4), (5, 4)],
        "cores": [(0, 1), (1, 2), (3, 2), (5, 2)],
        "compression_sources": [(-1, 4), (1, 3), (3, 3), (4, 4)],
    }
    with owned(*(Count.literal(v) for v in (1, 3, 48, 2, 1, 80, 4, 1, 8, 1, 1))) as parameters:
        with no_decode():
            output = preparation.run(sources, flags, *parameters)
        require(preparation.last_counts == dict(global_axes=1, reused_axes=1, tiles=4, expansion_blocks=8),
                "one actual global-axis producer and exact reuse for its identical second axis")
        digest = sha256(bytes(output.cells)).hexdigest()
        require(packet_bytes(output) == prepared_catalogue(),
                "fresh physical coefficient producer reproduces the immutable consumer input exactly")
        catalogue = None
        for item in pool.tapes:
            initialize_marker(item)
        try:
            with sealed_constructors(), scope.installed():
                try:
                    with no_decode():
                        catalogue = Catalogue(output, pool.acquire)
                    for i in range(2):
                        with owned(Count.literal(i)) as (index,):
                            with no_decode():
                                profile = catalogue.profile(index)
                        try:
                            actual = {}
                            for name, pairs in expected.items():
                                stream = getattr(profile, name)
                                actual[name] = []
                                for _ in pairs:
                                    with no_decode():
                                        origin, length = read_integer(stream), read_count(stream)
                                    with owned(origin, length):
                                        actual[name].append(((-1 if origin.negative else 1)*decode(origin.magnitude), decode(length)))
                                require(stream.read() == BLANK, "complete tensor descriptor stream")
                            require(actual == expected, "independent global-coordinate expansion and compression endpoints")
                            for k in range(4):
                                with no_decode():
                                    page = read_frame(profile.expansion_pages, pool.acquire)
                                try:
                                    with no_decode():
                                        header = TileHeader(page)
                                    with owned(header):
                                        require([decode(getattr(header, name)) for name in
                                                 ("s", "t", "p", "P", "alpha", "input_capacity", "target_length", "blocks")]
                                                == [7, 8, 48, 80, 2, 8, 2, 2], "actual expansion tile header")
                                finally:
                                    page.clear()
                                with no_decode():
                                    page = read_frame(profile.compression_pages, pool.acquire)
                                try:
                                    with no_decode():
                                        header = CoreHeader(page)
                                    with owned(header):
                                        require([decode(getattr(header, name)) for name in
                                                 ("p", "P", "width", "m", "target_length", "core_offset", "core_length", "band")]
                                                == [48, 80, 546, expected["compression_sources"][k][1], 4,
                                                    (1, 0, 0, 1)[k], (1, 2, 2, 2)[k], 2],
                                                "actual old-H compression page header")
                                finally:
                                    page.clear()
                            require(profile.expansion_pages.read() == profile.compression_pages.read() == BLANK,
                                    "complete four-tile numerical page streams")
                            evidence.append(actual)
                        finally:
                            profile.close()
                finally:
                    if catalogue is not None:
                        catalogue.close()
                    pool.empty()
        finally:
            for item in pool.tapes:
                erase_marker(item)
        require(sha256(bytes(output.cells)).hexdigest() == digest and output.head == 1,
                "catalogue reader preserves the entire original prepared page")
        require(not pool.live and all(item.head == 1 and all(v == BLANK for v in item.cells) for item in pool.tapes),
                "catalogue reader restores its fixed tape inventory")
        preparation.idle()
        output.clear()
        erase_marker(output)
    for item in (sources, flags):
        item.clear()
        erase_marker(item)
    return {"sha256": digest, "packet_sha256": CATALOGUE_SHA256, "axes": evidence, "producer": preparation.last_counts,
            "producer_pool_peak": preparation.pool.peak, "reader_pool_peak": pool.peak,
            "scope": "actual explicit p48 P80 two-axis catalogue; reduced halos, no production locality claim"}
