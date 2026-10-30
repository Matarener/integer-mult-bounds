"""Persistent ROM backing for the source-bound CRT row query.

New interface produced by Nick Petalas. Apache-2.0.
The source query and producer retain their original notices and credit.
"""


def need(condition, message):
    if not condition:
        raise ValueError(message)


def capacities(registers, precision, height):
    """PR5519's credited role extents, used as supplied blank capacities."""
    need(len(registers) == 44 and len(set(registers)) == 44, "44 scalar roles")
    need(1 <= height < precision, "Compiled precision and height")
    n = 1 << height
    sizes = {name: precision + 2 for name in registers}
    sizes.update(arena=5 * precision * n * (height**2 + 3 * height + 1) + 2,
                 spool=n * (2 * height - 1) + 2,
                 layers=(n + 1) * (2 * height - 1) + 2, rom=n + 2,
                 h=precision + 2, modulus=precision + 2,
                 selected_layer=precision + 2, offsets=precision + 3)
    need(len(sizes) == 52, "52 distinct bank roles")
    return sizes


class BankPool:
    """A supplied clean bank, with a single compiled owner at a time.

    Allocation is fixture initialization. Runtime acquire/release only changes
    ownership metadata; it never reads, clears, copies or resizes tape contents.
    Blank reentry is a proved precondition, observed separately by the verifier.
    """

    def __init__(self, sizes):
        need(len(sizes) == 52 and all(n > 0 for n in sizes.values()), "Bank shape")
        self.cells = {name: ["_"] * size for name, size in sizes.items()}
        self.leased = False

    def acquire(self):
        need(not self.leased, "Bank already leased")
        self.leased = True
        return self.cells

    def release(self, cells):
        need(self.leased and cells is self.cells, "Bank lease ownership")
        self.leased = False


def adapt_source(source):
    """Add one explicit bank parameter; retain every runtime tape instruction."""
    edits = (
        ("start, row, fault=None):", "start, row, banks, fault=None):"),
        ("        self.fault = fault", "        self.fault = fault\n        self.banks = banks"),
        ("        headers = {name: Tape() for name in names}",
         "        self.service = banks.acquire()\n"
         "        headers = {name: Tape(self.service[name]) for name in names}"),
        ("        self.service = {name: ['_'] for name in rom_module.REGS+('arena','spool','layers','rom')}\n"
         "        self.service.update({name: headers[name].cells for name in names})\n", ""),
        ("        self.entry.close()\n        self.closed=True",
         "        self.entry.close()\n"
         "        if self.service is not None:self.banks.release(self.service)\n"
         "        self.closed=True"),
    )
    for old, new in edits:
        need(source.count(old) == 1, "Exact source-bound allocation seam")
        source = source.replace(old, new, 1)
    return source
