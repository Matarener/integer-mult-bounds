"""Observe literal frozen Count/Tape execution, including every basis input."""

from hashlib import sha256

import tape_padding


def need(condition, message):
    if not condition:
        raise ValueError(message)


def decode(count):
    from words import RIGHT

    count.rewind()
    result = 0
    try:
        for bit in range(tape_padding.MAX_COUNT_BITS + 2):
            digit = count.read()
            if digit == RIGHT:
                return result
            need(digit in (0, 1), "observer sees binary count")
            result += digit << bit
            count.step(1)
        raise ValueError("observer bit capacity")
    finally:
        count.rewind()


def payload(tape):
    from words import BLANK

    return bytes(tape.cells[1:]).rstrip(bytes([BLANK]))


def plans(retained):
    from cardinal_counts import Count

    digest = sha256()
    accepted = rejected = legacy_rejected = 0
    for r in range(1, 25):
        for s in range(1, 49):
            rows, stock = Count.literal(r), Count.literal(s)
            before = (payload(rows.tape), payload(stock.tape))
            try:
                if s >= 2 * r:
                    try:
                        tape_padding.plan_rows(rows, stock, retained)
                    except ValueError:
                        rejected += 1
                    else:
                        raise ValueError("inadmissible padding accepted")
                else:
                    padded, added = tape_padding.plan_rows(rows, stock, retained)
                    try:
                        want = ((r + s - 1) // s) * s
                        need(
                            (decode(padded), decode(added)) == (want, want - r),
                            "exact taped plan",
                        )
                        digest.update(f"{r},{s},{want}\n".encode())
                        accepted += 1
                    finally:
                        padded.close()
                        added.close()
                    if r < s:
                        try:
                            retained.plan_rows(rows, stock)
                        except ValueError:
                            legacy_rejected += 1
                        else:
                            raise ValueError("legacy covering restriction disappeared")
                need(
                    before == (payload(rows.tape), payload(stock.tape)),
                    "borrowed counts preserved",
                )
                need(rows.tape.head == stock.tape.head == 1, "count heads restored")
            finally:
                rows.close()
                stock.close()
    return {
        "accepted": accepted,
        "rejected": rejected,
        "legacy_rejected": legacy_rejected,
        "sha256": digest.hexdigest(),
    }


def one_endpoint(retained, prefixes, rows, stock, width, origin):
    from cardinal_counts import Count
    from records import Tape

    counts = [Count.literal(x) for x in (prefixes, rows, stock, width)]
    source = Tape()
    volume = prefixes * rows * width
    bits = bytes(int(i == origin) for i in range(volume))
    for bit in bits:
        source.append(bit)
    source.rewind()
    observations = []

    def callee(padded, padded_rows):
        r = decode(padded_rows)
        data = payload(padded)
        need(len(data) == prefixes * r * width, "complete padded endpoint")
        output = Tape()
        for offset in range(0, len(data), width):
            for bit in reversed(data[offset : offset + width]):
                output.append(bit)
        output.rewind()
        observations.append(r)
        return output

    try:
        output = tape_padding.complete(source, *counts, callee, retained)
        try:
            expected = b"".join(
                bits[i : i + width][::-1] for i in range(0, volume, width)
            )
            need(payload(output) == expected, "independent Boolean basis endpoint")
            need(
                payload(source) == bits and source.head == output.head == 1,
                "borrowed source preserved",
            )
            need(
                output is not source
                and observations == [((rows + stock - 1) // stock) * stock],
                "one completed compatible-row call",
            )
        finally:
            output.clear()
    finally:
        source.clear()
        for count in counts:
            count.close()


def endpoints(retained):
    cases = columns = 0
    for prefixes, rows, stock, width in (
        (1, 4, 6, 3),
        (2, 4, 6, 3),
        (3, 7, 12, 4),
        (2, 8, 8, 3),
        (2, 9, 6, 5),
    ):
        volume = prefixes * rows * width
        for origin in range(volume):
            one_endpoint(retained, prefixes, rows, stock, width, origin)
            columns += 1
        cases += 1
    return {
        "fixtures": cases,
        "independent_basis_inputs": columns,
        "new_domain": "first three fixtures have stock/2 < rows < stock",
        "callee": "synthetic rowwise reversal, not selected C0",
    }
