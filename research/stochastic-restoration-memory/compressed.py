"""Exact 76-bit retained log; physical integer/tape scratch remains unpriced."""
from itertools import product
from random import Random


def need(ok, message):
    if not ok:
        raise ValueError(message)


def nullspace(rows, columns):
    rows = list(rows)
    pivots, rank = [], 0
    for j in range(columns):
        i = next((i for i in range(rank,len(rows)) if rows[i] >> j & 1), None)
        if i is None:
            continue
        rows[rank], rows[i] = rows[i], rows[rank]
        for i in range(len(rows)):
            if i != rank and rows[i] >> j & 1:
                rows[i] ^= rows[rank]
        pivots.append(j)
        rank += 1
    basis = []
    for j in range(columns):
        if j in pivots:
            continue
        mask = 1 << j
        for i,col in enumerate(pivots):
            if rows[i] >> j & 1:
                mask ^= 1 << col
        basis.append(mask)
    return basis


def plan(events):
    cursor, result = 8411, {}
    for b in range(8):
        lo, size = 272+16*b, 137 if b < 3 else 142
        es = events[cursor:cursor+size]
        half = next(i for i,e in enumerate(es) if e[0] == 'SCALE' and e[-1] == 2)
        target = es[half][1]
        start = half
        while start and es[start-1][0] == 'ADD' and es[start-1][2] == target:
            start -= 1
        need(half-start == 12 and es[half][3:] == (1,2), 'literal first-half phase')
        # Parity rows over the original 16 bits and independent fresh noise bits
        # for every fractional shear. This grants more possible states than the
        # true rounded map and makes the relation valid for every input and tape.
        rows, variables = [1 << j for j in range(16)], 16
        for op,r,s,n,d in es[:start]:
            r -= lo
            if op == 'ADD':
                if d > 1:
                    rows[r] ^= 1 << variables
                    variables += 1
                elif n & 1:
                    rows[r] ^= rows[s-lo]
            else:
                need(d == 1 and n in (-1,2), 'integer pre-phase SCALE')
                if not n & 1:
                    rows[r] = 0
        transpose = [sum(((rows[r] >> j) & 1) << r for r in range(16))
                     for j in range(variables)]
        basis = nullspace(transpose,16)
        candidates = []
        for bits in product((0,1),repeat=len(basis)):
            mask = 0
            for bit,v in zip(bits,basis):
                if bit:
                    mask ^= v
            if mask >> (target-lo) & 1:
                continue
            phase = es[start:half]
            if any(d > 1 and mask >> (r-lo) & 1 for op,r,s,n,d in phase):
                continue
            if sum(n for op,r,s,n,d in phase if mask >> (r-lo) & 1) % 2:
                candidates.append(mask)
        need(candidates, 'recoverable half parity')
        mask = min(candidates)
        need(all((mask & row).bit_count() % 2 == 0 for row in transpose),
             'complete pre-phase parity relation')
        holders = tuple(lo+j for j in range(16) if mask >> j & 1)
        need(holders == ((lo+15,) if b < 3 else (lo+10,lo+15)),
             'literal recovery holders')
        result[cursor+half] = holders
        cursor += size
    return result


def rounded(n,d,u):
    q,r = divmod(n,d)
    return q+int(u < r)


def forward(initial,events,tape,recovery):
    x, logs = list(initial), []
    for i,((op,r,s,n,d),u) in enumerate(zip(events,tape)):
        if op == 'ADD':
            x[r] += rounded(n*x[s],d,u)
        else:
            if d == 2 and i not in recovery:
                logs.append((n*x[r]) % 2)
            x[r] = rounded(n*x[r],d,u)
    return x,logs


def backward(current,events,tape,logs,recovery):
    x, logs = list(current), list(logs)
    index = len(logs)
    for i in range(len(events)-1,-1,-1):
        op,r,s,n,d = events[i]
        u = tape[i]
        if op == 'ADD':
            x[r] -= rounded(n*x[s],d,u)
        elif d == 2:
            if i in recovery:
                bit = sum(x[j] for j in recovery[i]) % 2
            else:
                index -= 1
                need(index >= 0, 'retained residue available')
                bit = logs[index]
            x[r] = n*(2*x[r]-2*int(u < bit)+bit)
            if i not in recovery:
                logs[index] ^= (n*x[r]) % 2
                need(logs[index] == 0, 'retained residue cleaned')
        elif n == 2:
            need(x[r] % 2 == 0, 'reached doubled image')
            x[r] //= 2
        else:
            x[r] = -x[r]
    need(index == 0 and not any(logs), 'all 76 residue bits cleaned')
    return x,logs


def verify(events,old):
    recovery = plan(events)
    need(len(recovery) == 8 and sum(map(len,recovery.values())) == 13,
         'eight recovered residues from thirteen existing parity reads')
    rng = Random(606676)
    count = 0
    broken = dict(recovery)
    broken[min(broken)] = ()
    rejected = False
    for case in range(64):
        initial = ([0]*748 if case == 0 else
                   [((j*73)%251)-125 for j in range(748)] if case == 1 else
                   [rng.randrange(-(1<<30),1<<30) for _ in range(748)])
        tape = tuple(0 if case%4 == 0 else d-1 if case%4 == 1 else rng.randrange(d)
                     for op,r,s,n,d in events)
        saved = tuple(tape)
        expected,old_logs = old.forward(initial,events,tape)
        actual,logs = forward(initial,events,tape,recovery)
        need(actual == expected and len(old_logs) == 84 and len(logs) == 76,
             'unchanged literal predecessor forward map')
        restored,clean = backward(actual,events,tape,logs,recovery)
        need(restored == initial and clean == [0]*76 and tape == saved,
             'exact dirty restoration and unchanged tape')
        # Copying the same forward value to a dirty accumulator has the same ABI.
        accumulator = [17*j-12345 for j in range(748)]
        need([a+x for a,x in zip(accumulator,actual)] ==
             [a+x for a,x in zip(accumulator,expected)], 'same compute-accumulate endpoint')
        if not rejected:
            try:
                bad,_ = backward(actual,events,tape,logs,broken)
                rejected = bad != initial
            except ValueError:
                rejected = True
        count += 1
    # A false zero-parity replacement must fail on a reached input/tape.
    need(rejected, 'wrong parity holder rejected on a full reached state')
    return dict(retained_bits=76,omitted_parity_logs=8,existing_value_parity_reads=13,
                full_tape_protocols=count,recovery={str(i):list(v) for i,v in recovery.items()},
                forward_law='Byte-identical predecessor opcodes, coefficients and fresh tape; only residue retention changes.',
                physical_scratch_and_movement='Not priced; 76 counts retained residue capacity at the logical boundary.')
