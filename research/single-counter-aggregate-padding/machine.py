"""One-counter aggregate scan, produced by Nick Petalas; Apache-2.0.

Only bit/marker reads, writes, and unit head moves drive this machine.
Cardinality, width, position, and volume integers belong to the checker.
"""


def rewind(tape):
    tape.move(-1)
    while tape.read() != "^":
        tape.move(-1)
    tape.move(1)


def borrow(counter):
    """Subtract one at fixed width; return underflow and restore the head."""
    while True:
        bit = counter.read()
        if bit == "$":
            rewind(counter)
            return True
        if bit == "1":
            counter.write("0")
            rewind(counter)
            return False
        if bit != "0":
            raise ValueError("invalid counter symbol")
        counter.write("1")
        counter.move(1)


def load(descriptor, counter, complement=False):
    """Copy q-1 or its fixed-width complement; report a nonzero result."""
    nonzero = False
    while True:
        bit = descriptor.read()
        if bit == "$":
            break
        if bit not in ("0", "1"):
            raise ValueError("invalid descriptor symbol")
        value = ("1" if bit == "0" else "0") if complement else bit
        nonzero = nonzero or value == "1"
        counter.write(value)
        descriptor.move(1)
        counter.move(1)
    if counter.read() != "$":
        raise ValueError("counter width mismatch")
    rewind(descriptor)
    rewind(counter)
    return nonzero


def clear(counter):
    while counter.read() != "$":
        counter.write("0")
        counter.move(1)
    rewind(counter)


class Coordinate:
    """One immutable descriptor, one zero-owned counter, one phase bit."""

    def __init__(self, descriptor, counter):
        self.descriptor = descriptor
        self.counter = counter
        self.genuine = True
        load(descriptor, counter)

    def advance(self):
        if not borrow(self.counter):
            return False
        if self.genuine and load(self.descriptor, self.counter, True):
            if borrow(self.counter):
                raise RuntimeError("nonzero padding countdown underflowed")
            self.genuine = False
            return False
        load(self.descriptor, self.counter)
        self.genuine = True
        return True

    def finish(self):
        clear(self.counter)


def scan(coordinates, source, target, control, restrict=False):
    """Scan five coordinates, then restore work and heads.

    Entry tapes are well-formed delimited binary words. All counters have the
    descriptor's width and initially contain zeros. Output is fresh owned work.
    The callback records a fixed finite-control action in the model.
    """
    if len(coordinates) != 5:
        raise ValueError("five coordinates required")
    while True:
        control("emit")
        genuine = all(coordinate.genuine for coordinate in coordinates)
        if restrict:
            bit = source.read()
            if bit not in ("0", "1"):
                raise ValueError("short or nonbinary source")
            source.move(1)
            if genuine:
                target.write(bit)
                target.move(1)
        else:
            bit = "0"
            if genuine:
                bit = source.read()
                if bit not in ("0", "1"):
                    raise ValueError("short or nonbinary source")
                source.move(1)
            target.write(bit)
            target.move(1)
        complete = True
        for coordinate in reversed(coordinates):
            control("advance")
            if not coordinate.advance():
                complete = False
                break
        if complete:
            break
    if source.read() != "$":
        raise ValueError("long source")
    target.write("$")
    rewind(source)
    rewind(target)
    for coordinate in coordinates:
        coordinate.finish()
