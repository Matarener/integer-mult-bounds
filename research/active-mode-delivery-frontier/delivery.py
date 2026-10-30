"""Emit and check the complete eight-mode delivery word. Apache-2.0."""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
import json
from inputs import need, index


def choose(responses):
    selected = {}
    for item in sorted(responses, key=lambda x: (x['rank'], x['event'])):
        mode = list(map(F, item['mode']))
        if item['rank'] != 8 or mode.count(F(1)) != 1 or mode.count(F(0)) != 7:
            continue
        selected.setdefault(mode.index(F(1)), item)
    need(set(selected) == set(range(8)), 'Every mode has a rank-eight delivery')
    need(all(len(item['scatter']) == 1 and item['scatter'][0][1] == '1' for item in selected.values()),
         'Attaining single-field witnesses')
    return selected


def emit(word, modes, choices):
    events = word['programs']['backward']
    omissions = set()
    # Bind every precompensation update before omitting it.
    pos = 0
    for mode in range(8):
        slot = mode + 1
        need(events[pos] == ['scalar', ['clear', ['C', slot]], 0], 'Mode capture start')
        pos += 1
        for i, a in enumerate(modes[mode]):
            if a:
                a /= 4
                need(events[pos] == ['scalar', ['add', ['C', slot], ['L', 112+i], a.numerator, a.denominator], 0], 'Exact original capture')
                pos += 1
        for h, value in sorted(word['helper_modes'][str(mode)]):
            a = -F(value)
            need(events[pos] == ['scalar', ['add', ['L', h], ['C', slot], a.numerator, a.denominator], 0], 'Exact original helper debit')
            omissions.add(pos); pos += 1
    tail = []
    for mode in range(8):
        for i, a in enumerate(modes[mode]):
            if a:
                a = -a
                tail.append(['physical_add', ['L', i], ['C', mode+1], a.numerator, a.denominator, 1, 0, []])
        tail.append(['scalar', ['clear', ['C', mode+1]], 0])
    need(events[-len(tail):] == tail, 'Every omitted tail and final owned clear is bound')
    tail_start = len(events) - len(tail)
    need(all(e[0] != 'physical_add' for e in events[:tail_start]), 'No other relaxed operation')
    at = {}
    for mode, item in choices.items():
        at.setdefault(item['event'], []).append((mode, item))
    out = []
    for pos, event in enumerate(events):
        for mode, item in at.get(pos, []):
            slot, frame = mode + 1, item['frame']
            out.append(['center', slot, 0, frame, 8])
            for field, value in item['scatter']:
                need(field < 632, 'Attaining scatter uses an original field')
                a = -F(value)
                out.append(['scalar', ['add', ['L', field], ['C', slot], a.numerator, a.denominator], frame])
            out.append(['scalar', ['clear', ['C', slot]], 0])
        if pos in omissions or pos >= tail_start:
            continue
        out.append(deepcopy(event))
    need(len(omissions) == 367, 'All eight source helper precompensation sets')
    return out, omissions


def replay(word, program, core, expected, allow_zero_cleanup=False):
    n = 633 + word['owned_extra_slots_by_direction']['backward']
    rows = [core.identity(i) for i in range(632)] + [{} for _ in range(n-632)]
    cur = word['canonical']['start'][:] + [None] * (n-632)
    paid = Counter(); ordinary = Counter(); peak = 0; clean = []; dropped = Counter()
    for event in program:
        kind = event[0]
        if kind == 'scalar':
            op, frame = event[1:]; d = index(op[1]); tag = op[0]
            if tag == 'clear':
                need(d >= 632, 'Only owned data can be erased')
                redundant = not rows[d] and cur[d] == frame
                rows[d] = {}; cur[d] = frame
            else:
                need(cur[d] == frame, 'Scalar destination coframe')
                redundant = False
                if tag in ('copy', 'add'):
                    s = index(op[2]); need(cur[s] == frame, 'Scalar source coframe')
                    if tag == 'copy':
                        need(d >= 632, 'Only owned data can be overwritten')
                        redundant = not rows[s] and not rows[d]
                        rows[d] = dict(rows[s])
                    else:
                        need(d != s, 'Nonaliasing ADD')
                        redundant = not rows[s] or not op[3]
                        core.add(rows[d], rows[s], F(op[3], op[4]))
                else:
                    need(tag == 'scale' and op[2], 'Nonzero source SCALE')
                    redundant = not rows[d]
                    rows[d] = {key: value * F(op[2], op[3]) for key, value in rows[d].items()}
            if redundant and allow_zero_cleanup:
                dropped[tag] += 1
                continue
            ordinary[tag] += 1
        elif kind == 'climb':
            _, _, d, start, end, rank = event
            need(cur[d] == start, 'Climb source coframe')
            need(rank == len(word['canonical']['frames'][end])-len(word['canonical']['frames'][start]) and rank > 0, 'Source climb rank')
            cur[d] = end; paid[rank] += 1
        elif kind == 'center':
            _, slot, start, end, rank = event; d = 632 + slot
            need(cur[d] == start, 'Delivery source coframe')
            need(rank == abs(len(word['canonical']['frames'][end])-len(word['canonical']['frames'][start])), 'Delivered native rank')
            cur[d] = end; paid[rank] += 1
        elif kind == 'warp':
            _, ref, op, start, end = event; d = index(ref)
            need(cur[d] == start, 'Warp source coframe')
            rows[d] = core.warp(rows[d], op, True); cur[d] = end
        else:
            need(kind in ('phase', 'adapter'), 'No unimplemented cross-frame opcode')
        clean.append(event)
        peak = max(peak, sum(bool(x) for x in rows[632:]))
    need(rows[:632] == expected, 'All 632 original columns with every native word retained')
    need(all(not row for row in rows[632:]), 'All arbitrary-helper obligations and owned-zero returns')
    need(cur[:632] == word['canonical']['final'], 'Every original final frame')
    result = dict(paid=dict(paid), ordinary=dict(ordinary), peak_live_owned=peak, events=len(clean),
                  dropped_zero_operations=dict(dropped), word_sha256=sha256(json.dumps(clean,separators=(',',':')).encode()).hexdigest())
    return result, clean


def conjugate(ce, op):
    result = ce.ident(op.n)
    for gate in op.circuit:
        kind = gate[0]
        if kind == 'D': part = ce.diag(op.n, gate[1], [-x % 4 for x in gate[2]])
        elif kind == 'C': part = ce.cgate(op.n, gate[1], -gate[2])
        elif kind == 'P': part = ce.perm(op.n, gate[1])
        elif kind == 'X': part = ce.xgate(op.n, gate[1])
        else:
            need(kind == 'phase', 'Known scalar phase')
            part = ce.Op(op.n, ce.identity(op.n), [('phase', -gate[1] % 4)])
        result = result.then(part)
    return result


def native(word, choices, ce, quadratic):
    result = {}
    for mode, item in choices.items():
        # Backward frames are the conjugates of the forward canonical frames.
        op = conjugate(ce, ce.canonical_frame(9, word['canonical']['frames'][item['frame']]))
        recipe, compiled = ce.lower_child(op)
        need(recipe['rank'] == 8, 'Actual signed native grade of the delivery')
        need(quadratic.equal_operators(op, compiled), 'Native wrappers include the absolute phase')
        bad = compiled.then(ce.Op(9, ce.identity(9), [('phase', 1)]))
        need(not quadratic.equal_operators(op, bad), 'Wrong wrapper phase rejected')
        need(op.zero_state() == compiled.zero_state(), 'Independent literal zero-column phase')
        result[str(mode)] = dict(frame=item['frame'], recipe=recipe, gates=len(compiled.circuit))
    return result
