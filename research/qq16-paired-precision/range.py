"""Independent whole-word all-depth component magnitude / dyadic-grid induction.

No predecessor code is executed. Input words must be authenticated by the caller.
The rules are the elementary pair-first Gaussian calculation stated in range-proof.md.
"""
from fractions import Fraction
import hashlib
import json


class Bound:
    __slots__ = ('m', 'g', 'a', 'b')
    def __init__(self, m=0, g=0, a=0, b=0):
        self.m = Fraction(m)
        self.g, self.a, self.b = (g, a, b) if self.m else (0, 0, 0)
    def as_json(self):
        return [str(self.m), self.g, self.a, self.b]
    def scale(self, coefficient):
        c = Fraction(coefficient)
        if not c or not self.m:
            return Bound()
        if c not in (1, -1, Fraction(1, 4), Fraction(-1, 4)):
            raise ValueError('unsupported scalar')
        return Bound(abs(c) * self.m, self.g + (2 if abs(c) == Fraction(1, 4) else 0), self.a, self.b)
    def plus(self, other):
        if not self.m:
            return Bound(other.m, other.g, other.a, other.b)
        if not other.m:
            return Bound(self.m, self.g, self.a, self.b)
        return Bound(self.m + other.m, max(self.g, other.g), max(self.a, other.a), max(self.b, other.b))


def ceiling_log2(value):
    value = Fraction(value)
    if value <= 0:
        raise ValueError('positive bound required')
    k = value.numerator.bit_length() - value.denominator.bit_length()
    if Fraction(2) ** k < value:
        k += 1
    return k


def audit(word, include_trace=False):
    if not isinstance(word, list):
        raise ValueError('word list required')
    states = {f'{side}{p}': Bound(1) for side in ('X', 'Y') for p in range(112)}
    owned = {f'{side}{p}' for side in ('Z', 'W') for p in range(112)}
    active = set()
    scope = None
    maxima = {'m': Fraction(0), 'g': 0, 'a': 0, 'b': 0}
    witnesses = {}
    counts = {}
    observations = []
    state_trace = []
    private_peak = 0
    def observe(index, label, value):
        observations.append([index, label, value.as_json()])
        for key in maxima:
            x = getattr(value, key)
            if x > maxima[key]:
                maxima[key] = x
                witnesses[key] = [index, label, value.as_json()]
    def read(name):
        if name not in states:
            raise ValueError('dirty or unavailable read: ' + str(name))
        return states[name]
    def write(name, value):
        if name not in owned | active:
            raise ValueError('unowned destination: ' + str(name))
        states[name] = value
    for i, e in enumerate(word):
        if not isinstance(e, list) or not e:
            raise ValueError('invalid event')
        op = e[0]
        counts[op] = counts.get(op, 0) + 1
        if op == 'clear':
            if len(e) != 3:
                raise ValueError('clear shape')
            write(e[1], Bound())
        elif op == 'add':
            if len(e) != 4 or e[1] == e[2]:
                raise ValueError('add shape or alias')
            c = Fraction(e[3])
            source, dest = read(e[2]), read(e[1])
            if abs(c) == Fraction(1, 4):
                observe(i, 'quarter predivision copy', source)
                observe(i, 'quarter first exact halving', Bound(source.m/2, source.g+1, source.a, source.b))
            scaled = source.scale(c)
            observe(i, 'scaled source', scaled)
            write(e[1], dest.plus(scaled))
        elif op == 'line':
            if len(e) != 4 or e[3] not in (-1, 1) or active:
                raise ValueError('line shape or private overlap')
            v = read(e[1])
            if v.m:
                observe(i, 'Gaussian pair sums', Bound(2*v.m, v.g, v.a+1, v.b+1))
                observe(i, 'Gaussian cross numerators', Bound(4*v.m, v.g, v.a+1, v.b+1))
                write(e[1], Bound(2*v.m, v.g+1, v.a+1, v.b+1))
            else:
                write(e[1], Bound())
        elif op == 'map':
            if len(e) != 5 or active:
                raise ValueError('map shape or private overlap')
            read(e[1])
        elif op == 'begin':
            if len(e) != 3 or active or e[2] not in (8, 16):
                raise ValueError('begin shape or overlap')
            active = {f'F{j}' for j in range(8)}
            if e[2] == 16:
                active |= {f'G{j}' for j in range(8)}
            scope = e[1]
            private_peak = max(private_peak, len(active))
        elif op == 'end':
            if len(e) != 3 or not active or scope != e[1] or len(active) != e[2]:
                raise ValueError('end mismatch')
            if any(read(name).m for name in active):
                raise ValueError('private field not cleared')
            for name in active:
                del states[name]
            active, scope = set(), None
        elif op == 'checkpoint':
            if len(e) != 2:
                raise ValueError('checkpoint shape')
        else:
            raise ValueError('unknown opcode: ' + str(op))
        if op in ('clear', 'add', 'line', 'map'):
            observe(i, 'event output ' + e[1], read(e[1]))
        state_trace.append([i, op, e[1] if len(e)>1 else None,
                            read(e[1]).as_json() if op in ('clear','add','line','map') else None])
    if active or any(name not in states for name in owned):
        raise ValueError('incomplete word')
    exponent = ceiling_log2(maxima['m'])
    receipt = {
        'model': 'strict input component bound 2^P h; lattice hZ; t=lambda-1>=0',
        'events': len(word), 'counts': counts, 'private_peak': private_peak,
        'max_M': str(maxima['m']), 'ceil_log2_max_M': exponent,
        'max_g': maxima['g'], 'max_a': maxima['a'], 'max_b': maxima['b'],
        'quantum': {'h_power_two_constant': -maxima['g'], 'h_power_two_t': -maxima['b']},
        'signed_width': {'P_coefficient': 1, 'constant': exponent+maxima['g']+1, 't_coefficient': maxima['a']+maxima['b']},
        'witnesses': witnesses, 'observation_count': len(observations),
        'observation_sha256': hashlib.sha256(json.dumps(observations,separators=(',',':')).encode()).hexdigest(),
        'state_trace_sha256': hashlib.sha256(json.dumps(state_trace,separators=(',',':')).encode()).hexdigest(),
        'final_bounds': {name: states[name].as_json() for name in sorted(owned)},
    }

    if include_trace:
        receipt['trace'] = state_trace
    return receipt


def compare(candidate, baseline):
    a, b = audit(candidate), audit(baseline)
    return {'candidate': a, 'baseline': b,
            'same_sufficient_quantum': a['quantum'] == b['quantum'],
            'same_sufficient_width': a['signed_width'] == b['signed_width'],
            'same_final_component_envelopes': a['final_bounds'] == b['final_bounds'],
            'completed_query_cuts': {'candidate': query_cut(candidate), 'baseline': query_cut(baseline)},
            'first_new_pair_sum': pair_cut(candidate),
            'independent_depth_checks': depth_checks(candidate, baseline)}


def audit_depth(word, depth):
    """Separate numeric recurrence; explicitly expands each Gaussian coordinate.

    This check does not call Bound, audit, or the grouped tensor rule. It
    checks the finite constants at selected depths; the proof supplies all depths.
    """
    if type(depth) is not int or depth < 1:
        raise ValueError('positive integer depth')
    fields = {f'{side}{p}': (Fraction(1), 0) for side in ('X','Y') for p in range(112)}
    max_m, max_g = Fraction(1), 0
    native_coordinate_lines = 0
    def visit(m,g):
        nonlocal max_m,max_g
        max_m, max_g = max(max_m,m), max(max_g,g if m else 0)
    for event in word:
        op = event[0]
        if op == 'clear':
            fields[event[1]] = (Fraction(0),0)
        elif op == 'add':
            dm,dg=fields[event[1]]; sm,sg=fields[event[2]]
            c=abs(Fraction(event[3]))
            if c == Fraction(1,4):
                visit(sm,sg);visit(sm/2,sg+1)
                sm,sg=sm/4,sg+2
            elif c != 1:
                raise ValueError('unexpected scalar')
            visit(sm,sg)
            m=dm+sm
            g=max(dg if dm else 0,sg if sm else 0) if m else 0
            fields[event[1]]=(m,g)
            visit(m,g)
        elif op == 'line':
            m,g=fields[event[1]]
            for _ in range(depth):
                native_coordinate_lines += 1
                visit(2*m,g);visit(4*m,g)
                if m:
                    m,g=2*m,g+1
                visit(m,g)
            fields[event[1]]=(m,g)
        elif op in ('map','begin','checkpoint'):
            pass
        elif op == 'end':
            for j in range(8):
                fields.pop(f'F{j}',None)
                if event[2] == 16:
                    fields.pop(f'G{j}',None)
        else:
            raise ValueError('unexpected opcode')
    return {'lambda':depth,'max_magnitude':str(max_m),'max_grid':max_g,
            'coordinate_Gaussian_lines':native_coordinate_lines,
            'final_bounds':{n:[str(m),g] for n,(m,g) in sorted(fields.items()) if n[0] in 'ZW'}}


def depth_checks(candidate,baseline,depths=(1,2,3,8)):
    ca,ba=audit(candidate),audit(baseline)
    result=[]
    for depth in depths:
        c,b=audit_depth(candidate,depth),audit_depth(baseline,depth)
        for exact,grouped in ((c,ca),(b,ba)):
            if Fraction(exact['max_magnitude']) > Fraction(grouped['max_M'])*2**(grouped['max_a']*(depth-1)):
                raise ValueError('grouped magnitude failed')
            if exact['max_grid'] > grouped['max_g']+grouped['max_b']*(depth-1):
                raise ValueError('grouped grid failed')
        if c != b:
            raise ValueError('numeric whole-word envelope differs')
        result.append({k:v for k,v in c.items() if k!='final_bounds'})
    return result


def query_cut(word):
    index=next(i for i,e in enumerate(word) if e == ['clear','Z10','query2'])
    trace=audit(word,include_trace=True)['trace']
    latest={row[2]:row[3] for row in trace[:index] if row[3] is not None}
    names=['Z1','Z2','Z3','Z4','Z5','Z6','Z8','Z9']
    return {'before_event':index,'query_bounds':{name:latest[name] for name in names},
            'scratch_D':latest['Z10'],'tenth_host':latest['Z11']}


def pair_cut(word):
    index=next(i for i,e in enumerate(word) if e == ['add','Z10','Z11','1'])
    trace=audit(word,include_trace=True)['trace']
    return {'event':index,'opcode':word[index],'bound':trace[index][3]}
