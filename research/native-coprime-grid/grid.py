"""Native coprime tensor-grid reference model. Apache-2.0.
Dugongue, with substantial OpenAI Codex assistance.
Counters concern displayed arithmetic, not an emitted RAM instruction trace.
"""
from math import prod


def need(ok, message):
    if not ok:
        raise ValueError(message)


class Words:
    def __init__(self, width):
        need(type(width) is int and width >= 2, 'invalid word width')
        self.width = width
        self.limit = (1 << (width - 1)) - 1
        self.operations = 0
        self.peak = 0

    def keep(self, value, cost=1):
        need(type(value) is int and abs(value) <= self.limit, 'word overflow')
        self.operations += cost
        self.peak = max(self.peak, abs(value).bit_length())
        return value

    def gcd(self, a, b):
        a, b = self.keep(a), self.keep(b)
        while b:
            a, b = b, self.keep(a % b, 3)  # DIV, MUL, SUB
        return a

    def inverse(self, a, modulus):
        need(modulus > 1 and 0 < a < modulus, 'inverse domain')
        old_r, r, old_x, x = modulus, a, 0, 1
        while r:
            q = self.keep(old_r // r)
            old_r, r = r, self.keep(old_r - self.keep(q*r))
            old_x, x = x, self.keep(old_x - self.keep(q*x))
        need(old_r == 1, 'non-coprime inverse')
        return self.keep(old_x % modulus, 3)


def build(k, count, words=None, candidate_budget=None):
    need(type(k) is int and k >= 2 and type(count) is int and count >= 1,
         'invalid grid shape')
    if candidate_budget is not None:
        need(type(candidate_budget) is int and candidate_budget >= 0, 'invalid budget')
    w = words or Words(8*(k*count + 2))
    bound = w.keep(1 << k)
    exclusion = 2
    moduli = []
    trials = 0
    for _ in range(count):
        candidate = bound - 1
        while candidate > 1:
            if candidate_budget is not None and trials >= candidate_budget:
                raise ValueError('candidate budget exhausted; no completed grid')
            trials += 1
            if w.gcd(candidate, exclusion) == 1:
                moduli.append(candidate)
                exclusion = w.keep(exclusion*candidate)
                break
            candidate = w.keep(candidate-2)
        else:
            raise ValueError('not enough admissible moduli below target')
    return moduli, {'candidates': trials, 'arithmetic_operations': w.operations,
                    'peak_bits': w.peak, 'word_bits': w.width,
                    'maximum_deficit': max(bound-s for s in moduli),
                    'sum_deficits': sum(bound-s for s in moduli)}


class CRTGrid:
    def __init__(self, moduli, words=None):
        need(bool(moduli) and all(type(s) is int and s >= 3 and s % 2 for s in moduli),
             'odd moduli >= 3 required')
        self.moduli = tuple(moduli)
        bits = sum(s.bit_length() for s in moduli) + 2
        self.words = w = words or Words(8*bits)
        product = 1
        for s in moduli:
            need(w.gcd(product, s) == 1, 'moduli must be pairwise coprime')
            product = w.keep(product*s)
        self.size = product
        self.input_steps = []
        self.output_steps = []
        for s in moduli:
            cofactor = w.keep(product//s)
            inverse = w.inverse(w.keep(cofactor % s, 3), s)
            self.input_steps.append(w.keep(cofactor*inverse))
            self.output_steps.append(cofactor)

    def indices(self, dual=False, coordinates=False):
        """Stream addresses; copying d coordinates is an optional test-only cost."""
        digits = [0]*len(self.moduli)
        steps = self.output_steps if dual else self.input_steps
        address = 0
        changes = 0
        for serial in range(self.size):
            yield (address, tuple(digits)) if coordinates else address
            if serial + 1 == self.size:
                break
            for axis, radix in enumerate(self.moduli):
                digits[axis] += 1
                changes += 1
                address = self.words.keep(address+steps[axis])
                if address >= self.size:
                    address = self.words.keep(address-self.size)
                if digits[axis] < radix:
                    break
                digits[axis] = 0
        self.last_changes = changes

    def from_coordinates(self, coordinates, dual=False):
        need(len(coordinates) == len(self.moduli) and
             all(type(x) is int and 0 <= x < s for x, s in zip(coordinates,self.moduli)),
             'coordinate domain')
        steps = self.output_steps if dual else self.input_steps
        total = 0
        for x, c in zip(coordinates, steps):
            term = self.words.keep(x*c)
            total = self.words.keep((total+term) % self.size, 4)
        return total


def volume_certificate(k, moduli):
    bound = 1 << k
    need(all(type(s) is int and 1 < s < bound for s in moduli), 'volume domain')
    deficit = sum(bound-s for s in moduli)
    need(deficit < bound, 'simple product lower bound is nonpositive')
    source = prod(moduli)
    target = bound**len(moduli)
    need(source*bound >= target*(bound-deficit), 'product lower bound failed')
    return {'source_volume': source, 'target_volume': target,
            'inflation_upper_numerator': bound, 'inflation_upper_denominator': bound-deficit}


def build_squares(k, count):
    """Guaranteed composite axes below 2**k; k must be even."""
    need(type(k) is int and k >= 4 and k % 2 == 0, 'even exponent >= 4 required')
    roots, stats = build(k//2, count)
    w=Words(8*(k*count+2))
    moduli=[w.keep(a*a) for a in roots]
    stats={'root_construction':stats,'squaring_operations':w.operations,
           'maximum_deficit':max((1<<k)-s for s in moduli),
           'sum_deficits':sum((1<<k)-s for s in moduli)}
    return moduli, roots, stats


def root_floor(value, words):
    need(type(value) is int and value >= 0, 'square-root domain')
    low, high = 0, words.keep(1 << ((value.bit_length()+1)//2))
    while low < high:
        middle=words.keep((low+high+1)//2)
        if words.keep(middle*middle) <= value:
            low=middle
        else:
            high=middle-1
    return low


def build_bands(targets, squares=False, candidate_budget=None):
    """Use the actual PR4029 guard-safe intervals; optionally only composites."""
    need(bool(targets) and all(type(t) is int and t >= 4 and t&(t-1)==0 for t in targets),
         'power-of-two targets required')
    need(type(squares) is bool, 'boolean square mode required')
    if candidate_budget is not None:
        need(type(candidate_budget) is int and candidate_budget >= 0, 'invalid budget')
    d=len(targets)+1
    words=Words(8*(sum(t.bit_length() for t in targets)+4))
    excluded=2;moduli=[];witnesses=[];trials=0
    for target in targets:
        lower=words.keep(target*(3*d-1)//(3*d)+1)
        upper=words.keep(target*(4*d-1)//(4*d))
        if squares:
            low=root_floor(lower,words)
            if low*low<lower:low+=1
            high=root_floor(upper,words)
        else:
            low,high=lower,upper
        candidate=high if high%2 else high-1
        while candidate >= max(3,low):
            if candidate_budget is not None and trials >= candidate_budget:
                raise ValueError('candidate budget exhausted; no completed grid')
            trials+=1
            if words.gcd(candidate,excluded)==1:
                excluded=words.keep(excluded*candidate)
                modulus=words.keep(candidate*candidate) if squares else candidate
                moduli.append(modulus);witnesses.append(candidate)
                break
            candidate=words.keep(candidate-2)
        else:
            raise ValueError('guard-safe interval exhausted')
    return moduli, witnesses, {'candidates':trials,'arithmetic_operations':words.operations,
                               'peak_bits':words.peak,'word_bits':words.width}
