"""Literal fixed-role unary geometry -> one-target dense-guard stencil.

The program touches tapes only through read/write/move. It never inspects
host lengths, heads, counters, cell lists, geometry integers or coordinates.
The Tape class supplied by the simulator has a permanent LEFT cell.
"""

LEFT, END, BLANK = "<", ">", "_"
SKIP = ("S", False, False, "0", "0")


def rewind(tape):
    while tape.read() != LEFT:
        tape.move(-1)


def empty_word(tape):
    tape.move(1)
    tape.write(END)
    tape.move(-1)


def validate(tape):
    if tape.read() != LEFT:
        raise ValueError("input must enter at permanent LEFT")
    tape.move(1)
    while True:
        symbol = tape.read()
        if symbol == END:
            # The initially blank tail is part of the tape input contract;
            # this checks that END is immediately followed by blank.
            tape.move(1)
            if tape.read() != BLANK:
                raise ValueError("nonblank immediately after unary END")
            rewind(tape)
            return
        if symbol != "1":
            raise ValueError("unary input alphabet or missing END")
        tape.move(1)


def positive(tape):
    tape.move(1)
    ok = tape.read() == "1"
    rewind(tape)
    if not ok:
        raise ValueError("required positive unary field")


def difference(left, right, out):
    """Protected unary left-right, rejecting underflow before writing out."""
    left.move(1)
    right.move(1)
    while True:
        symbol = right.read()
        if symbol == END:
            break
        if symbol != "1" or left.read() != "1":
            raise ValueError("unary subtraction underflow")
        left.move(1)
        right.move(1)
    out.move(1)
    while True:
        symbol = left.read()
        if symbol == END:
            out.write(END)
            break
        if symbol != "1":
            raise ValueError("internal unary subtraction alphabet")
        out.write("1")
        out.move(1)
        left.move(1)
    rewind(left)
    rewind(right)
    rewind(out)


def plus_one(source, out):
    source.move(1)
    out.move(1)
    while source.read() == "1":
        out.write("1")
        source.move(1)
        out.move(1)
    out.write("1")
    out.move(1)
    out.write(END)
    rewind(source)
    rewind(out)


def three(out):
    out.move(1)
    out.write("1")
    out.move(1)
    out.write("1")
    out.move(1)
    out.write("1")
    out.move(1)
    out.write(END)
    rewind(out)


def skip(source, stencil):
    source.move(1)
    while source.read() == "1":
        stencil.write(SKIP)
        stencil.move(1)
        source.move(1)
    rewind(source)


def digit(source, stencil):
    source.move(1)
    symbol = source.read()
    first = True
    while symbol == "1":
        source.move(1)
        symbol = source.read()
        stencil.write(("D", first, symbol == END, "0", "0"))
        stencil.move(1)
        first = False
    rewind(source)


def leading_guard(source, stencil, first):
    source.move(1)
    while source.read() == "1":
        stencil.write(("G", first, False, "0", "1"))
        stencil.move(1)
        source.move(1)
        first = False
    rewind(source)


def trailing_guard(source, stencil):
    source.move(1)
    symbol = source.read()
    while symbol == "1":
        source.move(1)
        symbol = source.read()
        stencil.write(("G", False, symbol == END, "0", "0"))
        stencil.move(1)
    rewind(source)


def erase(tape):
    rewind(tape)
    tape.move(1)
    while True:
        symbol = tape.read()
        tape.write(BLANK)
        if symbol == END:
            break
        tape.move(1)
    rewind(tape)


def produce(G, H, K, Y, J, B, Tape, include_parity=False,
            wrong_lower_pivot=False, wrong_upper_pivot=False,
            omit_cleanup=False, omit_output_return=False):
    """Six protected canonical unary words -> owned one-target stencil.

    Each input is LEFT, 1^n, END followed by initially blank tail, head LEFT.
    On successful validation G>=1,H>=G,K>=G+4,Y>=J+K,J/B>=0.
    Eight fixed private unary roles are erased, including every END marker.
    Fixed booleans select named mutation programs for verification only.
    """
    HG, KG, THREE, A, TAIL, JP, YJ, YJK = (
        Tape(), Tape(), Tape(), Tape(), Tape(), Tape(), Tape(), Tape())
    stencil = Tape()
    work = (HG, KG, THREE, A, TAIL, JP, YJ, YJK)
    for tape in work:
        empty_word(tape)
    empty_word(stencil)
    try:
        for tape in (G, H, K, Y, J, B):
            validate(tape)
        positive(G)
        difference(H, G, HG)
        difference(K, G, KG)
        three(THREE)
        difference(KG, THREE, A)
        positive(A)  # K-G-3 >= 1, exactly K >= G+4.
        plus_one(G, TAIL)
        plus_one(J, JP)
        difference(Y, J, YJ)
        difference(YJ, K, YJK)
        stencil.move(1)
        skip(HG, stencil)
        digit(G, stencil)
        skip(HG, stencil)
        digit(G, stencil)
        skip(YJK, stencil)
        if include_parity:
            stencil.write(("G", True, False, "0", "0"))
            stencil.move(1)
        leading_guard(A, stencil, not include_parity)
        stencil.write(("G", False, False,
                       "0" if wrong_lower_pivot else "1",
                       "0" if wrong_upper_pivot else "1"))
        stencil.move(1)
        trailing_guard(TAIL, stencil)
        skip(J if include_parity else JP, stencil)
        skip(B, stencil)
        stencil.write(END)
        if not omit_output_return:
            rewind(stencil)
    except ValueError:
        # All private words remain complete on every grammar/admission
        # rejection. Input values are never written in either branch.
        for tape in work:
            erase(tape)
        erase(stencil)
        for tape in (G, H, K, Y, J, B):
            rewind(tape)
        raise
    if not omit_cleanup:
        for tape in work:
            erase(tape)
    for tape in (G, H, K, Y, J, B):
        rewind(tape)
    return work, stencil
