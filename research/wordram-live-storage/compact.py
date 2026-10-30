"""Static temporary-cell reuse for the pinned forward Word RAM template."""

from bisect import bisect_left, bisect_right
from dataclasses import dataclass
from heapq import heappop, heappush

MAX_INSTRUCTIONS = 1_000_000
MAX_TEMPORARIES = 20_000


def require(condition, message):
    if not condition:
        raise ValueError(message)


def operands(instruction):
    """Return destination and semantically required direct-address reads."""
    op, *args = instruction
    if op == "accept":
        require(not args, "accept arity")
        return None, ()
    if op == "bltz":
        require(len(args) == 2, "branch arity")
        return None, (args[0],)
    require(op in ("one", "add", "sub", "mul"), "unsupported opcode")
    require(len(args) == (1 if op == "one" else 3), "arithmetic arity")
    reads = () if op == "one" else tuple(args[1:])
    if op == "sub" and args[1] == args[2]:
        reads = ()  # This instruction is zero for every incoming word.
    return args[0], reads


def lifetimes(program, temporaries, scratch, zero):
    require(0 < len(program) <= MAX_INSTRUCTIONS, "instruction capacity")
    require(0 < len(temporaries) <= MAX_TEMPORARIES, "temporary capacity")
    require(0 < len(scratch) <= 64 and zero in scratch, "scratch contract")
    require(not temporaries & scratch, "temporary/scratch overlap")
    require(all(type(x) is int for x in temporaries | scratch), "address type")
    cleanup = [("sub", x, x, x) for x in sorted(temporaries)]
    cleanup += [("sub", x, x, x) for x in sorted(scratch - {zero})]
    cleanup += [("accept",)]
    end = len(program) - len(cleanup)
    require(end > 0 and program[end:] == cleanup, "cleanup suffix")
    first, last, branches = {}, {}, []
    for pc in range(end):
        ins = program[pc]
        require(ins and all(type(x) is int for x in ins[1:]), "operand type")
        require(ins[0] != "accept", "early halt")
        dst, reads = operands(ins)
        for cell in reads:
            if cell in temporaries:
                require(cell in first, "read before initialization")
                last[cell] = pc
        if dst in temporaries:
            first.setdefault(dst, pc)
            last[dst] = pc
        if ins[0] == "bltz":
            target = ins[2]
            require(pc < target < end, "nonforward or escaping branch")
            branches.append((pc, target))
    require(first.keys() == temporaries, "unused temporary")
    starts = sorted(first.values())
    for pc, target in branches:
        require(bisect_left(starts, target) == bisect_right(starts, pc),
                "branch skips initialization")
    return end, tuple(sorted((first[x], last[x], x) for x in temporaries))


def allocate(intervals, physical_cells):
    active, free, mapping = [], [], {}
    capacity = 0
    for start, finish, cell in intervals:
        require(start <= finish, "reversed lifetime")
        # At most one retirement per supplied interval, over the whole run.
        for _ in range(len(active)):
            if active[0][0] >= start:
                break
            _, slot = heappop(active)
            heappush(free, slot)
        if free:
            slot = heappop(free)
        else:
            require(capacity < len(physical_cells), "physical capacity")
            slot = physical_cells[capacity]
            capacity += 1
        mapping[cell] = slot
        heappush(active, (finish, slot))
    return mapping, capacity


def check_allocation(intervals, mapping, physical_cells):
    require(set(mapping) == {x for _, _, x in intervals}, "mapping domain")
    require(set(mapping.values()) <= set(physical_cells), "mapping range")
    previous_end = {}
    for start, finish, cell in intervals:
        slot = mapping[cell]
        require(previous_end.get(slot, -1) < start, "overlapping aliases")
        previous_end[slot] = finish


@dataclass(frozen=True)
class CompactProgram:
    program: list
    mapping: dict
    intervals: tuple
    cleanup_start: int
    capacity: int


def compact(program, temporaries, scratch, zero):
    end, intervals = lifetimes(program, temporaries, scratch, zero)
    physical = sorted(temporaries)
    mapping, capacity = allocate(intervals, physical)
    check_allocation(intervals, mapping, physical)
    result = []
    for ins in program:
        op, *args = ins
        if op == "bltz":
            args[0] = mapping.get(args[0], args[0])
        else:
            args = [mapping.get(x, x) for x in args]
        result.append((op, *args))
    require(len(result) == len(program), "instruction count changed")
    return CompactProgram(result, mapping, intervals, end, capacity)
