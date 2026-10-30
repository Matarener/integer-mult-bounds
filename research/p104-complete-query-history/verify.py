"""Check all chronological P104 field histories in both orientations.

Ali Romman with OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import json
import sys

HERE = Path(__file__).resolve().parent
PRIME = 2**61 - 1


def need(ok, label):
    if not ok:
        raise ValueError(label)


def dot(a, b):
    if len(a) > len(b):
        a, b = b, a
    return sum(v * b.get(i, 0) for i, v in a.items())


def packed(row):
    return [[i, v.numerator, v.denominator] for i, v in sorted(row.items())]


def update(dst, src, q, prime=None):
    for i, a in src.items():
        value = dst.get(i, 0) + q * a
        if prime:
            value %= prime
        if value:
            dst[i] = value
        else:
            dst.pop(i, None)


def transpose_word(w):
    program = []
    for e in reversed(w['program']):
        op, r = e[:2]
        if op == 'MOVE':
            program.append([op, r, e[3], e[2], e[4]])
        elif op in ('ADD', 'COPY'):
            program.append(['ADD', e[2], r, *e[3:]])
            if op == 'COPY':
                program.append(['CLEAR', r, e[-1]])
        elif op in ('INIT', 'CLEAR'):
            program.append(['CLEAR', r, e[-1]])
        else:
            need(op == 'SCALE', 'Transpose opcode')
            program.append(e)
    return dict(w, program=program, initial=w['final'], final=w['initial'])


def frame_classes(w):
    frames = []
    for b in w['frames']:
        span = {0}
        for x in b:
            need(0 < x < 512 and x not in span, 'Binary frame basis')
            span |= {y ^ x for y in tuple(span)}
        frames.append(tuple(sorted(span)))
    return frames


def replay(w, reverse=False, modular=False):
    if reverse:
        w = transpose_word(w)
    frames = frame_classes(w)
    spaces = {}
    one = 1 if modular else Q(1)
    rows = [{r: one} for r in range(735)] + [{} for _ in range(8)]
    current = list(w['initial']) + [None] * 8
    cert = sha256()
    counts, dimensions, minimum = Counter(), [], None
    first_control = None

    def insert(frame, row, event=None):
        nonlocal minimum, first_control
        pivots = spaces.setdefault(frame, {})
        z = dict(row)
        while z:
            # The modular pass eliminates in the opposite coordinate order.
            k = max(z) if modular else min(z)
            value = z[k]
            if k not in pivots:
                if event is not None and not modular:
                    witness = {k: Q(1)}
                    for j in sorted(pivots, reverse=True):
                        val = -sum(a * witness.get(i, 0) for i, a in pivots[j].items() if i != j)
                        if val:
                            witness[j] = val
                    need(all(dot(b, witness) == 0 for b in pivots.values()), 'Every earlier same-frame basis row')
                    response = dot(row, witness)
                    need(response == value and response, 'Separating query input')
                    norm = dot(witness, witness)
                    relative = response**2 / (9 * norm * dot(row, row))
                    entry = dict(event=event, pivot=k, witness=packed(witness),
                                 response=[response.numerator, response.denominator],
                                 squared_relative_error_floor=[relative.numerator, relative.denominator])
                    cert.update(json.dumps(entry, sort_keys=True, separators=(',', ':')).encode() + b'\n')
                    if minimum is None or relative < minimum[0]:
                        minimum = (relative, entry)
                    if first_control is None:
                        first_control = (dict(row), {j: dict(b) for j, b in pivots.items()})
                inv = pow(value, -1, PRIME) if modular else 1 / value
                pivots[k] = {i: (a * inv % PRIME if modular else a * inv) for i, a in z.items()}
                return True
            update(z, pivots[k], -value, PRIME if modular else None)
        return False

    for r, f in enumerate(w['initial']):
        need(insert(frames[f], rows[r]), 'Independent original input')
    for k, e in enumerate(w['program']):
        op, r = e[:2]
        if op == 'MOVE':
            a, b = e[2:4]
            need(current[r] == a, 'Native input frame')
            need(insert(frames[b], rows[r], [k, r, b]), 'No paid query lies in its complete earlier history')
            counts[abs(len(w['frames'][a]) - len(w['frames'][b]))] += 1
            current[r] = b
        elif op in ('INIT', 'CLEAR'):
            need(r >= 735, 'Owned zero operation')
            rows[r] = {}
            current[r] = e[-1]
        else:
            q = Q(e[-2])
            if modular:
                q = q.numerator * pow(q.denominator, -1, PRIME) % PRIME
            need(current[r] == e[-1], 'Scalar destination chart')
            if op == 'SCALE':
                rows[r] = {i: (q*a % PRIME if modular else q*a) for i, a in rows[r].items()}
            else:
                s = e[2]
                need(current[s] == e[-1], 'Scalar source chart')
                if op == 'COPY':
                    need(r >= 735 and not rows[r], 'Owned copy target')
                    rows[r] = {i: (q*a % PRIME if modular else q*a) for i, a in rows[s].items()}
                else:
                    need(op == 'ADD', 'Scalar opcode')
                    update(rows[r], rows[s], q, PRIME if modular else None)
            need(not insert(frames[e[-1]], rows[r]), 'Every scalar history is already in the available span')
    live = set(w['live'])
    for r, row in enumerate(rows):
        want = {r: one} if r < 735 else {}
        if reverse and r in live:
            want[r+112] = one
        elif not reverse and r-112 in live:
            want[r-112] = one
        need(row == want, 'Complete arbitrary-input endpoint')
    for frame, basis in sorted(spaces.items()):
        dimensions.append([list(frame), len(basis)])
    out = dict(paid={str(k): v for k, v in sorted(counts.items())}, queries=sum(counts.values()),
               total_available_dimension=sum(len(b) for b in spaces.values()),
               frame_classes=len(spaces), dimensions_sha256=sha256(json.dumps(dimensions, separators=(',', ':')).encode()).hexdigest())
    if not modular:
        out['separator_sha256'] = cert.hexdigest()
        out['minimum_squared_relative_error_floor'] = [minimum[0].numerator, minimum[0].denominator]
        out['minimum_witness'] = minimum[1]
        row, basis = first_control
        def member(v, b):
            v = dict(v)
            while v:
                j = min(v)
                if j not in b:
                    return False
                update(v, b[j], -v[j])
            return True
        need(not member(row, basis), 'Absent-query control')
        z = dict(row)
        while z and min(z) in basis:
            j = min(z)
            update(z, basis[j], -z[j])
        j = min(z)
        value = z[j]
        basis[j] = {i: a/value for i, a in z.items()}
        need(member(row, basis), 'Injected early query becomes available')
        need(member(row, basis), 'Duplicate history adds no dimension')
    return out


def main():
    for pin in json.loads((HERE / 'INPUTS.json').read_text()):
        need(sha256((HERE / pin['file']).read_bytes()).hexdigest() == pin['sha256'], 'Exact source pin')
    w = json.loads(gzip.decompress((HERE / 'inputs/WORD.json.gz').read_bytes()))
    out = dict(status='PASS_P104_COMPLETE_QUERY_HISTORY', source_pr=5580,
               minimum_width=40, gram_lower_bound='1/9', original_inputs=735,
               prime=PRIME, all_earlier_values_granted=True)
    for direction, reverse in [('forward', False), ('transpose', True)]:
        exact = replay(w, reverse)
        modular = replay(w, reverse, True)
        need(all(exact[k] == value for k, value in modular.items()), 'Independent modular dimensions and ranks')
        need(exact['queries'] == 3454 and exact['total_available_dimension'] == 4189, 'Complete paid census')
        out[direction] = exact
    out['controls'] = ['early_query_changes_availability', 'duplicate_history_has_no_rank', 'all_scalar_histories_included']
    path = HERE / 'RESULT.json'
    if '--write' in sys.argv:
        path.write_text(json.dumps(out, indent=2, sort_keys=True) + '\n')
    else:
        need(out == json.loads(path.read_text()), 'Complete replay receipt')
    print(json.dumps(out, sort_keys=True))


if __name__ == '__main__':
    main()
