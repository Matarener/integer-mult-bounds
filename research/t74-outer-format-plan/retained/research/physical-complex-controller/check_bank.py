# SPDX-License-Identifier: Apache-2.0
"""Independent indexed oracle for complete physical bank transactions."""
from hashlib import sha256
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cohort
cohort.activate()
from bank_packets import BankPackets
from cardinal_counts import Count
from records import Tape
from words import BLANK


def body(tape):
    return bytes(tape.cells[1:]).rstrip(bytes([BLANK]))


def fill(tape, raw):
    tape.clear()
    for bit in raw:
        tape.append(bit)
    tape.rewind()


def run():
    dig = sha256()
    cases = 0
    for prefix_n, unused_n, row_n in ((1, 1, 1), (2, 3, 11), (3, 2, 17)):
        shape = (prefix_n, 4, 3, unused_n, row_n)
        keys = ((3, 2), (0, 0), (1, 2))
        engine = BankPackets(4, 3, len(keys) + 2)
        engine.select(keys)
        counts = tuple(Count.literal(n) for n in (prefix_n, unused_n, row_n))
        bank, stale = Tape(), Tape()
        expected = [((i * i + i // 7 + 13) % 11) & 1
                    for i in range(prefix_n * 12 * unused_n * row_n)]
        fill(bank, expected)
        fill(stale, expected)
        for repeat in range(2):
            before = bytes(expected)
            packets = engine.gather(bank, *counts)
            packet_extent = unused_n * row_n
            for slot, (family, cover) in enumerate(keys):
                offsets = [(p * 12 + family * 3 + cover) * packet_extent for p in range(prefix_n)]
                oracle = bytes(expected[o + j] for o in offsets for j in range(packet_extent))
                cohort.require(body(packets[slot]) == oracle, "complete prefix-preserving gather")
                # Distinct changes expose slot-order and repeated-prefix mistakes.
                changed = bytes(bit ^ ((j + slot + repeat) % 3 == 0) for j, bit in enumerate(oracle))
                fill(packets[slot], changed)
                for p, offset in enumerate(offsets):
                    expected[offset:offset + packet_extent] = changed[p * packet_extent:(p + 1) * packet_extent]
            try:
                engine.scatter(stale, *counts)
            except ValueError as error:
                cohort.require(str(error) == "replace the acquired current bank", "stale bank rejection")
            else:
                raise ValueError("accepted a stale bank")
            returned = engine.scatter(bank, *counts)
            cohort.require(body(returned) == bytes(expected) and body(bank) == before,
                           "complete replacement preserves original until commit")
            engine.commit(bank)
            cohort.require(body(bank) == bytes(expected) and engine.state == "closed" and
                           not engine.pool.live and all(t.read() == BLANK for t in engine.packets),
                           "committed latest bank and closed packets")
            dig.update(body(bank))
            engine.select(keys)
            cases += 1
        for count in counts:
            count.close()
        bank.clear()
        stale.clear()
    return {"transactions": cases, "outer_prefixes": [1, 2, 3],
            "stale_bank_rejections": cases, "sha256": dig.hexdigest(),
            "unused_packet_roles": 2,
            "scope": "Generic complete encoded bank boundary with a partially selected fixed inventory."}


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
