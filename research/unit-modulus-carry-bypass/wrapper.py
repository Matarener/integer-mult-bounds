"""Prepend a literal unit-modulus return to a fixed quarter-carry table.

Produced by Nick Petalas. Apache-2.0.
The retained tape machine and quarter-carry table keep their source credit.
"""

PREFIX_SIZE = 7
MAX_INSTRUCTIONS = 100_000


def wrap(program, symbols):
    """Accept the pinned table ABI, without receiving any runtime values."""
    rows = program["instructions"]
    if program["tapes"] != 19 or not 0 < len(rows) <= MAX_INSTRUCTIONS:
        raise ValueError("bounded nineteen-tape input table required")
    entry = program["entry"]
    if type(entry) is not int or not 0 <= entry < len(rows):
        raise ValueError("invalid retained entry")
    zero, one, right = (symbols[name] for name in ("ZERO", "ONE", "RIGHT"))
    prefix = [
        ["move", 5, 1],
        ["branch", 5, [[right, 2], [zero, 4], [one, 4]], 6],
        ["move", 5, -1],
        ["halt"],
        ["move", 5, -1],
        ["goto", entry + PREFIX_SIZE],
        ["reject", "canonical positive odd modulus required"],
    ]
    suffix = []
    for row in rows:
        if row[0] == "branch":
            suffix.append(["branch", row[1],
                           [[s, pc + PREFIX_SIZE] for s, pc in row[2]],
                           row[3] + PREFIX_SIZE])
        elif row[0] == "goto":
            suffix.append(["goto", row[1] + PREFIX_SIZE])
        elif row[0] in ("move", "write", "halt", "reject"):
            suffix.append(list(row))
        else:
            raise ValueError("unsupported retained instruction")
    return {"tapes": 19, "entry": 0, "instructions": prefix + suffix}
