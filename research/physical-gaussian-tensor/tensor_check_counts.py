"""Complete exact products, aliased operands and scoped setup adaptation."""
from hashlib import sha256
from tensor_sources import require


def run():
    from cardinal_counts import Count
    from check_support import no_decode
    from ring_check_words import decode
    from router_metadata import owned
    from scratch_pool import ScratchPool
    from session import OuterScope, borrowed_tape, erase_marker, initialize_marker, sealed_constructors
    from tensor_counts import exact_setup_arithmetic
    from words import BLANK
    pool = ScratchPool(64)
    scope = OuterScope(pool)
    for tape in pool.tapes:
        erase_marker(tape)
    pairs = [(a, b) for a in range(16) for b in range(16)]
    for width in (1, 7, 8, 9, 31, 48, 113, 372, 512, 1023, 1024, 1025, 2049):
        maximum = (1 << width)-1
        pairs.extend(((maximum, maximum), (maximum, maximum//3), (maximum, 1),
                      (0, maximum), (1 << (width-1), maximum)))
    pairs.extend(((1 << 2049)-1, (1 << width)-1) for width in (1023, 1024, 1025))
    digest = sha256()
    original = Count.__dict__["product"]
    for a, b in pairs:
        with owned(Count.literal(a), Count.literal(b)) as (first, second):
            saved = bytes(first.tape.cells), bytes(second.tape.cells)
            for tape in pool.tapes:
                initialize_marker(tape)
            try:
                with sealed_constructors(), scope.installed():
                    try:
                        with exact_setup_arithmetic(), no_decode():
                            result = Count.product(first, first if a == b else second)
                        with owned(result):
                            require(decode(result) == a*b, "independent complete integer product including alias and carry cases")
                            digest.update(bytes(borrowed_tape(result.tape).cells))
                    finally:
                        pool.empty()
            finally:
                for tape in pool.tapes:
                    erase_marker(tape)
            require(saved == (bytes(first.tape.cells), bytes(second.tape.cells))
                    and first.tape.head == second.tape.head == 1, "setup product preserves both borrowed inputs")
            require(Count.__dict__["product"] is original, "setup arithmetic restores the exact retained class method")
    try:
        with exact_setup_arithmetic():
            raise RuntimeError("planned setup interruption")
    except RuntimeError:
        pass
    require(Count.__dict__["product"] is original, "setup interruption restores the exact retained class method")
    require(not pool.live and all(t.head == 1 and all(v == BLANK for v in t.cells) for t in pool.tapes),
            "setup product restores its fixed tape inventory")
    return {"products": len(pairs), "maximum_operand_bits": 2049, "pool_peak": pool.peak,
            "sha256": digest.hexdigest(), "scope": "exact schoolbook setup arithmetic with bounded thirty-two-bit digits"}
