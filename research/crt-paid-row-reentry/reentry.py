"""Consume a returned CRT row into the owned source after query retirement.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The topology is compiled. Runtime coordinates remain on finite-symbol tapes.
"""


def need(ok, message):
    if not ok:
        raise ValueError(message)


def retain_stream(output, staging):
    """Copy the live result before its owner closes. Both heads return to L."""
    need(output.read() == 'L' and staging.read() == '_', 'Result and blank staging entry')
    while True:
        symbol = output.read()
        need(symbol in ('L', 'R', '|', '0', '1'), 'Finite result alphabet')
        staging.write(symbol)
        if symbol == 'R':
            break
        output.step(1)
        staging.step(1)
    output.rewind()
    staging.rewind()


def consume_into_source(query, staging, widths, level, start):
    """Retire the query, update only its right-node coordinates, and erase staging."""
    if query.output is None:
        query.close()
        return
    retain_stream(query.output, staging)
    query.close()
    # The source borrow has ended. The caller owns its coordinate fields.
    w, records, source = query.w, query.records, query.source
    middle, stop = start + (1 << (level - 1)), start + (1 << level)
    need(staging.read() == 'L', 'Staged result entry')
    staging.step(1)
    for axis, width in enumerate(widths):
        need(source.read() == records.ROOT, 'Axis record tag')
        source.step(1)
        for _ in range(width):
            need(source.read() == w.ONE, 'Compiled unary width')
            source.step(1)
        need(source.read() == records.WORD_END, 'Width delimiter')
        source.step(1)
        for _ in range(width):
            need(source.read() in (w.ZERO, w.ONE), 'Modulus bit')
            source.step(1)
        need(source.read() == records.WORD_END, 'Modulus delimiter')
        source.step(1)
        chosen = middle <= axis < stop
        for _ in range(width):
            need(source.read() in (w.ZERO, w.ONE), 'Current coordinate bit')
            if chosen:
                bit = staging.read()
                need(bit in ('0', '1'), 'Returned coordinate bit')
                source.write(w.ONE if bit == '1' else w.ZERO)
                staging.step(1)
            source.step(1)
        need(source.read() == records.RECORD_END, 'Axis record end')
        source.step(1)
        if chosen:
            need(staging.read() == '|', 'Returned coordinate delimiter')
            staging.step(1)
    need(source.read() == w.RIGHT and staging.read() == 'R', 'Complete source and result')
    source.rewind()
    staging.erase()
