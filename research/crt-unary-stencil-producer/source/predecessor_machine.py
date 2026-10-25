"""Three fixed tape roles and a marker-driven, finite-control guard program.

Tape.head and read/write/move totals are SIMULATOR OBSERVERS. The program
below never reads them, a tape length, or a host L/M/position counter.
Stencil atoms form a fixed finite product alphabet, independent of geometry.
"""

LEFT, END, BLANK = "<", ">", "_"
SKIP = ("S", False, False, "0", "0")


class Tape:
    """One cell/head operation per method; permanently marked left boundary."""

    def __init__(self, cells=None):
        self.cells = [LEFT] if cells is None else list(cells)
        self.head = 0
        self.reads = self.writes = self.moves = 0

    def read(self):
        self.reads += 1
        return self.cells[self.head]

    def write(self, symbol):
        self.writes += 1
        self.cells[self.head] = symbol

    def move(self, direction):
        # Only the emulator uses a numerical head coordinate. The program
        # emits one LEFT/RIGHT action and branches only on the read symbol.
        if direction not in (-1, 1):
            raise ValueError("one-cell direction")
        self.moves += 1
        self.head += direction
        if self.head < 0:
            raise ValueError("crossing permanent left boundary")
        if self.head == len(self.cells):
            self.cells.append(BLANK)  # Initially blank infinite tape cell.

    @property
    def actions(self):
        return self.reads + self.writes + self.moves


def rewind(tape):
    while tape.read() != LEFT:
        tape.move(-1)


def compare_flag(flag, bit, threshold, last_difference_wins):
    """L/E/G are three finite control states; all arguments have finite range."""
    if bit == threshold:
        return flag
    if flag == "E" or last_difference_wins:
        return "L" if bit == "0" else "G"
    return flag


def predicate(stencil, counter, lower_strict, upper_inclusive, last_difference_wins):
    good = True
    all_ones = False
    lower = upper = "E"
    active = "S"
    stencil.move(1)
    counter.move(1)
    while True:
        token = stencil.read()
        if token == END:
            if active != "S":
                raise ValueError("unterminated admitted interval")
            return good
        bit = counter.read()
        if bit not in ("0", "1"):
            raise ValueError("counter/stencil alignment")
        # Tuple fields decode one atom of a FIXED finite alphabet. They do
        # not index a parameter-sized geometry table or interval collection.
        kind, begin, end, lower_bit, upper_bit = token
        if kind == "D":
            if begin:
                active = "D"
                all_ones = True
            all_ones = all_ones and bit == "1"
            if end:
                good = good and not all_ones
                active = "S"
                all_ones = False
        elif kind == "G":
            if begin:
                active = "G"
                lower = upper = "E"
            lower = compare_flag(lower, bit, lower_bit, last_difference_wins)
            upper = compare_flag(upper, bit, upper_bit, last_difference_wins)
            if end:
                lower_ok = lower == "G" if lower_strict else lower != "L"
                upper_ok = upper != "G" if upper_inclusive else upper == "L"
                good = good and lower_ok and upper_ok
                lower = upper = "E"
                active = "S"
        stencil.move(1)
        counter.move(1)


def increment_and_return(counter, skip_low_counter_bit):
    """Counter starts at END; overflow returns False at permanent LEFT."""
    counter.move(-1)
    if skip_low_counter_bit:
        counter.move(-1)
    while True:
        bit = counter.read()
        if bit == "1":
            counter.write("0")
            counter.move(-1)
        elif bit == "0":
            counter.write("1")
            rewind(counter)
            return True
        elif bit == LEFT:
            return False
        else:
            raise ValueError("binary carry alphabet")


def erase_counter(counter):
    """Restore private data to BLANK, including its allocated END marker."""
    counter.move(1)
    while True:
        symbol = counter.read()
        counter.write(BLANK)
        if symbol == END:
            break
        counter.move(1)
    rewind(counter)


def transduce(stencil, lower_strict=False, upper_inclusive=False,
              last_difference_wins=False, omit_output_return=False,
              skip_low_counter_bit=False):
    """Admitted stencil -> protected stencil, blank private work, owned BAD mask.

    The booleans select fixed mutation programs for verification. The normal
    transducer has all False. There is no function/E-evaluator callback.
    """
    counter, mask = Tape(), Tape()  # Two fixed roles, reused throughout.
    stencil.move(1)
    counter.move(1)
    while True:
        symbol = stencil.read()
        if symbol == END:
            counter.write(END)
            break
        counter.write("0")
        stencil.move(1)
        counter.move(1)
    rewind(stencil)
    rewind(counter)
    mask.move(1)
    while True:
        good = predicate(stencil, counter, lower_strict, upper_inclusive, last_difference_wins)
        mask.write("0" if good else "1")
        mask.move(1)
        rewind(stencil)
        if not increment_and_return(counter, skip_low_counter_bit):
            break
    erase_counter(counter)
    mask.write(END)
    if not omit_output_return:
        rewind(mask)
    # A fixed final control state replaces all transient finite flags.
    return counter, mask
