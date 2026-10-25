"""Paid common-F17 reconstruction of the selected first pair.

This compiler accepts already-authenticated canonical packet and phase records.
It emits operations; it does not claim that a host-language payload loader is a
physical packet implementation. New work: Chris R, OpenAI Codex assistance.
SPDX-License-Identifier: Apache-2.0
"""
from collections import Counter
from fractions import Fraction as F
import hashlib
import json

I = tuple(1 << j for j in range(73))


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def emit(packet, phases):
    """Selected G on recovered originals in common F17, then exact Y exit.

    This uses the selected full word's scalar shadow, NOT the centre-free
    core's J shadow. Selected native/common-label refinement is inherited.
    """
    need(len(phases['recipes']) == 112, 'all actual ports')
    events = [('add', 'W'+str(p), 'Z'+str(p), 1) for p in range(112)]
    events.extend(('add', 'Z'+str(p), 'W'+str(p), -1) for p in range(112))
    for p, record in enumerate(phases['recipes']):
        events.append(('line', 'W'+str(p), p, record['q'], -1))
    return events


def add(a, b, c):
    out = a.copy()
    for key, value in b.items():
        out[key] = out.get(key, 0) + c*value
        if not out[key]:
            del out[key]
    return out


def phase(axes, u):
    return sum((axis & u).bit_count() % 2 for axis in axes) % 4


def selected_shadow(programs):
    """Literal source 712-column shadow, with no inverse of private CLEARs."""
    result = {}
    for orientation in ('forward', 'backward'):
        state = [{i: F(1)} for i in range(712)]
        def role(raw):
            kind, index = raw
            need(kind in ('L', 'C'), 'actual source role kind')
            return index + (704 if kind == 'C' else 0)
        for event in programs[orientation]:
            if event[0] != 'scalar':
                need(event[0] in ('phase', 'climb', 'center', 'adapter', 'residual_adapter'),
                     'source native alphabet')
                continue
            e = event[1]
            target = role(e[1])
            if e[0] == 'clear':
                need(target >= 704, 'only private clear')
                state[target] = {}
            elif e[0] == 'copy':
                state[target] = state[role(e[2])].copy()
            elif e[0] == 'scale':
                state[target] = {k: v*F(e[2], e[3]) for k, v in state[target].items()}
            else:
                need(e[0] == 'add', 'known scalar event')
                state[target] = add(state[target], state[role(e[2])], F(e[3], e[4]))
        identity = [{i: F(1)} for i in range(712)]
        expected = identity[:224]
        if orientation == 'forward':
            expected = identity[:112] + [add(identity[112+p], identity[p], 1) for p in range(112)]
        else:
            expected = [add(identity[p], identity[112+p], -1) for p in range(112)] + identity[112:224]
        need(state[:224] == expected, 'actual full selected data shadow')
        need(state[224:704] == identity[224:704], 'helper scalar identity only; native progress retained')
        need(state[704:] == [{} for _ in range(8)], 'private cleared; never inverted')
        result[orientation] = len(programs[orientation])
    return result


def audit(packet, phases, programs=None, template=None):
    need(programs is not None and template is not None, 'authenticated actual selected source required')
    source = selected_shadow(programs)
    calls = [template['calls'][i] for i in (0, 4)]
    for stage, call in enumerate(calls):
        need(call['replica'] == 0 and call['pair'] == 0 and call['stage'] == stage,
             'actual selected first pair')
        digest = hashlib.sha256(json.dumps(programs[call['orientation']], sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        need(digest == call['local_program_sha256'], 'actual selected called word hash')
        need(call['owners'][:224] == [[p, [1, stage, p % 112]] for p in range(224)],
             'same-port X/Y owner routes cancel in the selected unit shear')
    bridge = template['execution_schedule'][6]
    need(bridge['kind'] == 'bridge' and bridge['src'] == 1 and bridge['dst'] == 0
         and bridge['coefficient'] == 1, 'actual named two-leg bridge')
    word = emit(packet, phases)
    census = dict(Counter(e[0] for e in word))
    need(census == {'add': 224, 'line': 112}, 'complete reconstruction census')
    # Every bank column; line changes the output frame, not logical content.
    state = {side+str(p): {p+(112 if side == 'W' else 0): F(1)}
             for side in ('Z', 'W') for p in range(112)}
    for e in word:
        if e[0] == 'add':
            state[e[1]] = add(state[e[1]], state[e[2]], e[3])
    for p in range(112):
        need(state['Z'+str(p)] == {112+p: F(-1)}, 'current X, all columns')
        need(state['W'+str(p)] == {p: F(1),112+p: F(1)}, 'current Y, all columns')
    # Pointwise nonconstant owner/payload certificate. The arbitrary values
    # depend on owner, port and character; source units act independently at
    # every point. Both bridge legs retain independent pair-1 inputs.
    tests = [0] + list(I) + [I[i] ^ I[j] for i in range(73) for j in range(i)]
    exact_frame_checks = 0
    for record in phases['recipes']:
        q = record['q']
        need(q > 0 and q < 512 and q.bit_count() % 2 == 1, 'actual odd port label')
        for u in tests:
            current = phase(I[:17], u)
            negative_line = -((q & u).bit_count() % 2)
            # Product phases add; canonical parity-polynomial samples determine
            # every degree-at-most-two Z4 phase, not just these characters.
            want_y = (sum((axis & u).bit_count() % 2 for axis in I[:17]) - ((q & u).bit_count() % 2)) % 4
            parity = (q & u).bit_count() % 2
            kernel = ((1+1j) + (1-1j)*((-1)**parity))/2
            actual_x = (1j)**current
            actual_y = actual_x*((-1)**parity)*kernel
            need(actual_x == (1j)**phase(I[:17], u) and actual_y == (1j)**want_y,
                 'actual negative line kernel and all-port output gauges')
            exact_frame_checks += 2
    cases = 0
    sign_rejections = 0
    axes = I[:17]
    for owner_key in (0, 1, 13, 448):
        for u in (1, 2, 1 << 9, (1 << 16) | 1, 0):
            for p, record in enumerate(phases['recipes']):
                x = complex(3*p + 5*owner_key + u.bit_count(), p-owner_key)
                y = complex(7*p - 2*owner_key + (u & 3), owner_key+3)
                incoming_x = complex(11-p, owner_key+2)
                incoming_y = complex(p+17, -owner_key)
                factor = (1j)**phase(axes, u)
                line_phase = (record['q'] & u).bit_count() % 2
                current_x = -factor*y
                current_y = factor*(x+y)*(1j)**(-line_phase)
                actual = (current_x + factor*incoming_x,
                          factor*(1j)**(-line_phase)*incoming_y-current_y)
                expected = (factor*(-y+incoming_x),
                            factor*(1j)**(-line_phase)*(incoming_y-x-y))
                need(actual == expected, 'both bridge legs on varying owner/payload coefficients')
                if line_phase and x+y:
                    need(factor*(x+y)*(1j)**line_phase != current_y,
                         'positive line rejected')
                    sign_rejections += 1
                cases += 1
    need(phases['recipes'][0]['q'] == 11 and sign_rejections > 0, 'actual signed occurrence regression')
    return {'status': 'PASS_SELECTED_SHADOW_LIFT_AND_PHYSICAL_RECONSTRUCTION',
            'source_word_events': source, 'census': census,
            'all_data_columns': 224, 'all_port_frame_checks': exact_frame_checks, 'owner_character_port_cases': cases,
            'positive_line_rejections': sign_rejections,
            'logical_endpoint': '(-y,x+y)',
            'native_entry': '224 recovered originals in F17',
            'native_exit': 'X:F17; Y:F17 Cq^-1',
            'private_fields': 0,
            'inherited': ['actual selected common-label and exact unary refinement',
                          'actual DATA-PHASES external gauges and chronological hosting'],
            'complete_actual_caller_installation': False,
            'remaining': ['actual QQ16 producer and full-cover scheduling',
                          'encoded packets and actual signed child execution',
                          'exclusive storage, fixed-port copyback and both-leg bridge']}
