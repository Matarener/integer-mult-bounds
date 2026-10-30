#!/usr/bin/env python3
"""Exact R438 local replacement with a coded source and literal dirty repairs.

This is a changed local interface, not an admitted nine-stage supplier.  All
660 public scalar input columns are independent over F2.  The native operator
and integer-lift/controller obligations are independently owned by the sibling
recursive specialist.  No source checkout is modified.
"""
from collections import Counter
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]  # rebound explicitly by reconstruct.py
WORD = REPO / 'research/bit-r438-transport-rehost/words/r438-t154.json.gz'
BUILDER = REPO / 'research/bit-boundary-persistence/build.py'
MAIN_PIN = '20ecf2891d80b5acf18d980b2164fb44ea7faa90'
WORD_SHA = 'a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022'
BUILDER_SHA = '58f402c365eb18b9c3dd736523999676f1d1652e40c1a9b4f6967c1b7acb72df'


def require(value, message):
    if not value:
        raise ValueError(message)


def bits(mask):
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def rank(rows):
    pivots = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot in pivots:
                row ^= pivots[pivot]
            else:
                pivots[pivot] = row
                break
    return len(pivots)


def product(left, right):
    """Rows of left times rows of right, both bit-packed over F2."""
    return [sum_xor(right[j] for j in bits(row)) for row in left]


def sum_xor(values):
    result = 0
    for value in values:
        result ^= value
    return result


def inverse(rows):
    n = len(rows)
    aug = [row | (1 << (n + j)) for j, row in enumerate(rows)]
    for j in range(n):
        pivot = next((i for i in range(j, n) if aug[i] >> j & 1), None)
        require(pivot is not None, 'Singular section')
        aug[j], aug[pivot] = aug[pivot], aug[j]
        for i in range(n):
            if i != j and aug[i] >> j & 1:
                aug[i] ^= aug[j]
    require([row & ((1 << n) - 1) for row in aug] == [1 << j for j in range(n)],
            'Inverse left block failed')
    return [row >> n for row in aug]


def load():
    require(hashlib.sha256(WORD.read_bytes()).hexdigest() == WORD_SHA,
            'R438 source gzip pin changed')
    require(hashlib.sha256(BUILDER.read_bytes()).hexdigest() == BUILDER_SHA,
            'Baseline replay source pin changed')
    word = json.loads(gzip.decompress(WORD.read_bytes()))
    require((word['v'], word['R'], word['h']) == (111, 438, 8), 'Wrong dimensions')
    spec = importlib.util.spec_from_file_location('pinned_boundary_builder', BUILDER)
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    baseline, records = builder.replay(word)
    return word, builder, baseline, records


def matrices(word):
    v, count = word['v'], 2 * word['v'] + word['R']
    rows = [1 << j for j in range(count)]
    for phase in ('D', 'A'):
        for _, dst, sources in word[phase]:
            for src in sources:
                rows[dst] ^= rows[src]
    ret_rows = [rows[j] for j in word['ret']]
    source_mask = (1 << v) - 1
    helper_mask = ((1 << count) - 1) ^ ((1 << (2 * v)) - 1)
    require(all(row & ~ (source_mask | helper_mask) == 0 for row in ret_rows),
            'A retained total reads an arbitrary target')
    R = [row & source_mask for row in ret_rows]
    T = [row & helper_mask for row in ret_rows]
    K = [sum(1 << j for j in subset) for subset in word['scatter']]
    M = product(R, K)
    require(M == [507, 135, 238, 349, 185, 437, 205, 503, 425], 'RK changed')
    require(rank(M) == 9 and rank(R) == 9, 'Wrong query rank')
    selected, columns = [], []
    for p in range(v):
        column = sum(((row >> p) & 1) << j for j, row in enumerate(R))
        if rank(columns + [column]) > len(columns):
            selected.append(p)
            columns.append(column)
        if len(selected) == 9:
            break
    S = [sum(((row >> p) & 1) << j for j, p in enumerate(selected)) for row in R]
    Sinv = inverse(S)
    L = product(Sinv, M)
    U = [0] * v
    for j, p in enumerate(selected):
        U[p] = L[j]
    W = [k ^ u for k, u in zip(K, U)]
    Q = product(U, R)
    H = [(1 << p) ^ row for p, row in enumerate(product(W, R))]
    J = [(1 << p) ^ row for p, row in enumerate(product(K, R))]
    require(product(R, W) == [0] * 9, 'RW is not zero')
    require(product(H, H) == [1 << p for p in range(v)], 'H is not involutive')
    require(product(R, H) == R, 'RH differs from R')
    require(product(J, H) == [(1 << p) ^ Q[p] for p in range(v)], 'JH residual failed')
    require(product(Q, H) == Q, 'Repair query changes under H')
    require([p for p, row in enumerate(Q) if row] == selected, 'Repair support changed')
    return dict(R=R, T=T, K=K, M=M, selected=selected, S=S, Sinv=Sinv,
                L=L, U=U, W=W, H=H, Q=Q, J=J)


def construct(word, baseline_records, data):
    v, count = word['v'], 2 * word['v'] + word['R']
    require(all(f == 0 for f in word['start'][v:]), 'Initial target/helper frames differ')
    require(all(f == 1 for f in word['final'][:v] + word['final'][2*v:]),
            'A source/helper is not FULL at the new H cut')
    require(not any(v <= s < 2*v for phase in ('D', 'A', 'B', 'C')
                    for _, _, ss in word[phase] for s in ss), 'Target read in original word')
    old_comp = [0] * v
    for frame, dst, sources in word['D']:
        require(frame == 0 and v <= dst < 2*v, 'Original D is not a zero-frame target shear')
        for src in sources:
            require(src >= 2*v, 'Original D reads data instead of a dirty helper')
            old_comp[dst-v] ^= 1 << src
    # The original D and extra KT compensation commute at frame zero.
    # Cancel their duplicate parity gates before emitting the changed D.
    comp = [old ^ extra for old, extra in zip(old_comp, product(data['K'], data['T']))]
    prefix = [[1, v+p, src, 1, 0, 10]
              for p, row in enumerate(comp) for src in bits(row)]
    # Keep every original public-register frame visit, including empty-source
    # visits.  Only the nine owned copied totals and their scatter are removed.
    clean = [rec[:] for rec in baseline_records
             if rec[0] not in (2, 3) and not (rec[0] == 1 and (rec[2] == count or rec[5] == 1))]
    borrow = list(range(2*v, 2*v+9))
    # Four simultaneous banks of CNOTs implement x -> (I+WR)x while every
    # arbitrary dirty z_j is restored.  RW=0 is checked above.
    phase1 = [[1, p, borrow[j], 1, 1, 11]
              for p, row in enumerate(data['W']) for j in bits(row)]
    phase2 = [[1, borrow[j], p, 1, 1, 12]
              for j, row in enumerate(data['R']) for p in bits(row)]
    phase3 = [[1, p, borrow[j], 1, 1, 13]
              for p, row in enumerate(data['W']) for j in bits(row)]
    phase4 = [[1, borrow[j], p, 1, 1, 14]
              for j, row in enumerate(data['R']) for p in bits(row)]
    repairs = []
    b = borrow[0]
    for p in data['selected']:
        cap = word['final'][v+p]
        # Each episode reads one physical unchanged dirty register b.  The
        # private field is zero before COPY and exactly equals b at ERASE.
        # No zero-initialized query register or second simultaneous copy is used.
        episode = [[2, b, count, 1, cap, 1],
                   [1, v+p, count, 1, cap, 15],
                   [3, b, count, 1, cap, 0]]
        gather = [[1, b, src, 1, 1, 16] for src in bits(data['Q'][p])]
        repairs.extend(episode)
        repairs.extend(gather)
        repairs.extend(episode)
        repairs.extend([rec[:4] + [1, 17] for rec in gather])
    records = prefix + clean + phase1 + phase2 + phase3 + phase4 + repairs
    parts = dict(prefix=prefix, clean=clean, H1=phase1, H2=phase2, H3=phase3,
                 H4=phase4, repairs=repairs)
    return records, parts


def replay(word, builder, records, data, reverse=False, mutate_snapshot=False):
    v, count = word['v'], 2 * word['v'] + word['R']
    values = [1 << j for j in range(count)] + [0]
    current = (word['final'] if reverse else word['start'])[:]
    masks = [sum(1 << j for j in frame) for frame in word['frames']]
    dims = [builder.rank(word['lines'][j] for j in frame) for frame in word['frames']]
    profile, live, snapshots, paths = Counter(), None, 0, [[f] for f in current]
    old_private, changed = None, False
    for number, rec in enumerate(reversed(records) if reverse else records):
        op, dst, src, coefficient, frame, phase = rec
        if op == 0:
            old, new, paid = src, coefficient, frame
            if reverse:
                old, new = new, old
            require(current[dst] == old, f'Wrong climb start at {number}')
            require((masks[new] & ~masks[old] == 0) if reverse else
                    (masks[old] & ~masks[new] == 0), f'Non-nested move {number}')
            require(abs(dims[new]-dims[old]) == paid, f'Wrong climb rank {number}')
            current[dst] = new
            paths[dst].append(new)
            profile[paid] += 1
        elif op == 1:
            require(current[dst] == frame, f'Wrong ADD destination frame {number}')
            require((old_private if src == count else current[src]) == frame,
                    f'Wrong ADD source frame {number}')
            require(src != count or live is not None, 'Read from erased private field')
            values[dst] ^= values[src]
            if mutate_snapshot and live is not None and not changed:
                values[live] ^= 1
                changed = True
        elif op == (3 if reverse else 2):
            require(live is None and values[count] == 0, 'COPY overwrites live dirt')
            require(current[dst] == coefficient, 'COPY source frame differs')
            require(masks[frame] & ~masks[coefficient] == 0, 'COPY goes upward')
            paid = dims[coefficient]-dims[frame]
            require(paid > 0, 'Nonpositive COPY rank')
            profile[paid] += 1
            values[count] = values[dst]
            old_private, live = frame, dst
            snapshots += 1
        elif op == (2 if reverse else 3):
            require(live == dst and old_private == frame, 'ERASE mismatched source/frame')
            require(current[dst] == coefficient, 'ERASE source frame differs')
            require(values[count] == values[dst], f'ERASE snapshot changed at {number}')
            values[count], old_private, live = 0, None, None
        else:
            raise ValueError(f'Unknown operation {op}')
    require(live is None and values[count] == 0, 'Private field not clear')
    require(current == (word['start'] if reverse else word['final']), 'Final frames differ')
    expected = [1 << j for j in range(count)] + [0]
    for p in range(v):
        expected[p] = data.get('Hinv', data['H'])[p] if reverse else data['H'][p]
        expected[v+p] ^= (1 << p) if reverse else data['H'][p]
    require(values == expected, f'Wrong {"reverse" if reverse else "forward"} dirty map')
    return dict(public_columns=count, nonzero_output_rows=sum(bool(x) for x in values),
                endpoint_sha256=hashlib.sha256(canonical(values)).hexdigest(),
                profile=dict(sorted(profile.items())),
                rank_mass=sum(k*n for k,n in profile.items()), copies=snapshots,
                max_live_copies=1, dirty_helpers_restored=word['R'],
                paths_sha256=hashlib.sha256(canonical(paths)).hexdigest())


def positive_bounds(records, count):
    bounds = []
    for reverse in (False, True):
        values, maximum = [1] * count + [0], 1
        for op, dst, src, coefficient, frame, phase in reversed(records) if reverse else records:
            if op == 1:
                values[dst] += values[src]
                maximum = max(maximum, values[dst])
            elif op == (3 if reverse else 2):
                values[count] = values[dst]
                maximum = max(maximum, values[count])
            elif op == (2 if reverse else 3):
                values[count] = 0
        bounds.append(maximum)
    F, R = bounds
    local, nine = 64*F**3*R**2, (1 << 18)*F**5*R**4
    return dict(forward=F, reverse=R, local_bits=local.bit_length(), nine_bits=nine.bit_length(),
                historical_local_guard_pass=local < 1 << 104,
                historical_nine_guard_pass=nine < 1 << 192,
                applicability='Numerical screen only; changed source-code interface not admitted')


def must_fail(name, thunk):
    try:
        thunk()
    except (ValueError, AssertionError) as error:
        return dict(name=name, detected=True, message=str(error))
    raise ValueError(f'Negative control escaped: {name}')


def main():
    word, builder, baseline, old_records = load()
    data = matrices(word)
    records, parts = construct(word, old_records, data)
    forward = replay(word, builder, records, data)
    reverse = replay(word, builder, records, data, reverse=True)
    expect = Counter({int(k): n for k,n in baseline['profile'].items()})
    expect[7] -= 9
    expect[1] += 18
    require(forward['profile'] == dict(sorted(expect.items())), 'Unexpected profile delta')
    require(reverse['profile'] == forward['profile'], 'Reverse profile differs')
    require(forward['rank_mass'] == 5076 and forward['copies'] == 18, 'Wrong local bill')
    controls = [
        must_fail('omit_changed_dirty_compensation', lambda: replay(
            word, builder, records[len(parts['prefix']):], data)),
        must_fail('omit_first_bulk_H_phase', lambda: replay(
            word, builder, [r for r in records if not (r[0] == 1 and r[5] == 11)], data)),
        must_fail('omit_repair_dirty_restore', lambda: replay(
            word, builder, [r for r in records if not (r[0] == 1 and r[5] == 17)], data)),
        must_fail('mutate_live_snapshot_source', lambda: replay(
            word, builder, records, data, mutate_snapshot=True)),
    ]
    container = dict(format='coded-r438-local-records-v1', register_order='X0..110,Y0..110,H0..437,C',
                     public_registers=660, private_register=660, word_path=str(WORD),
                     word_gzip_sha256=WORD_SHA, start=word['start'], final=word['final'],
                     record_schema='[op,dst,src,coefficient/sourceframe,frame/privateframe,phase/rank]',
                     copy_schema='[2,physical_source,660,sourceframe,privateframe,rank]',
                     erase_schema='[3,physical_source,660,sourceframe,privateframe,0]',
                     records=records)
    raw = canonical(container)
    outword = HERE / 'BIT-TRANSVECTION-WORD.json.gz'
    outword.write_bytes(gzip.compress(raw, mtime=0))
    output = dict(status='PASS_CHANGED_LOCAL_GF2_INTERFACE_NO_GLOBAL_SUPPLIER_NO_NEW_KAPPA',
                  source_pin=MAIN_PIN, source_word=str(WORD), source_gzip_sha256=WORD_SHA,
                  source_builder=str(BUILDER), builder_sha256=hashlib.sha256(BUILDER.read_bytes()).hexdigest(),
                  output_word=str(outword), output_canonical_sha256=hashlib.sha256(raw).hexdigest(),
                  output_gzip_sha256=hashlib.sha256(outword.read_bytes()).hexdigest(),
                  matrices=data, source_query_supports=[r.bit_count() for r in data['R']],
                  helper_query_supports=[r.bit_count() for r in data['T']],
                  baseline={k:v for k,v in baseline.items() if k != 'paths'},
                  forward=forward, reverse=reverse,
                  adds=sum(r[0] == 1 for r in records), records=len(records),
                  part_adds={k:sum(r[0] == 1 for r in rows) for k,rows in parts.items()},
                  positive=positive_bounds(records, 660), negative_controls=controls,
                  contract=dict(forward='(x,y,h)->(Hx,y+Hx,h)',
                                literal_inverse='(x,y,h)->(Hx,y+x,h)',
                                initial_frames='source Pp; target0; every helper0',
                                final_frames='source FULL; target Pp-perp; every helper FULL',
                                private='One live immutable copied snapshot; zero between episodes',
                                changed_original_hypotheses=['H4: appended source H and helpers restored by a new word',
                                                             'End source is coded Hx, not x']),
                  unresolved=['Independent exact native operator lift including complementary backward cuts',
                              'Ordered signed integer lift and applicable precision theorem',
                              'Whole9-stage controller code removal at actual cap queries',
                              'Chronological owner/stock and complete outer recurrence admission'])
    (HERE / 'BIT-TRANSVECTION.json').write_text(json.dumps(output, indent=2, sort_keys=True)+'\n')
    print(json.dumps({k:output[k] for k in ('status','forward','adds','records','part_adds','positive')},
                     indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
