"""Paid tagged/raw adapter around authenticated PR3884 axis_kernel.

New adapter by Clear1nsight with substantial OpenAI Codex assistance.
The inherited axis program is injected after outer source authentication.
No recursive H1 tariff is attached to this direct bit-tape implementation.
"""
from collections import Counter
from fractions import Fraction


def need(ok, why):
    if not ok:
        raise ValueError(why)


class TaggedTape:
    def __init__(self, cells, origin=0):
        self.cells = list(cells)
        self.origin = origin
        self.head = origin
        self.count = Counter()

    def read(self):
        p = self.head - self.origin
        need(0 <= p < len(self.cells), 'tagged read outside interval')
        self.count['read'] += 1
        return self.cells[p]

    def write(self, bit):
        p = self.head - self.origin
        need(0 <= p < len(self.cells), 'tagged write outside interval')
        need(type(bit) is int and bit in (0, 1), 'payload bit')
        self.count['write'] += 1
        self.cells[p] = bit

    def move(self, direction):
        need(direction in (-1, 1), 'unit direction')
        p = self.head - self.origin + direction
        need(0 <= p <= len(self.cells), 'tagged head outside interval')
        self.count['move'] += 1
        self.head += direction


def seek(tape, offset):
    target = tape.origin + offset
    while tape.head != target:
        tape.move(1 if target > tape.head else -1)


def binary_map(columns, x):
    out = 0
    for j, column in enumerate(columns):
        if (x >> j) & 1:
            out ^= column
    return out


def basis(q, n):
    need(type(n) is int and n >= 1 and type(q) is int and 0 < q < 1 << n,
         'nonzero q in address space')
    pivot = (q & -q).bit_length() - 1
    return (q,) + tuple(1 << j for j in range(n) if j != pivot)


def permutation(q, n, depth):
    """Fixture-sized tensor basis; quantified construction is in PHYSICAL.md."""
    need(type(depth) is int and depth >= 1, 'positive tensor depth')
    columns = basis(q, n)
    one = [binary_map(columns, x) for x in range(1 << n)]
    need(len(set(one)) == len(one), 'basis bijection')
    inverse = [one.index(x) for x in range(1 << n)]
    mask = (1 << n) - 1
    return [sum(inverse[(x >> (n*j)) & mask] << (n*j) for j in range(depth))
            for x in range(1 << (n*depth))]


def bit_reverse(x, bits):
    return sum(((x >> j) & 1) << (bits-1-j) for j in range(bits))


def variation(order, width):
    positions = [x*width+b for x in order for b in range(width)]
    return positions[0] + sum(abs(b-a) for a,b in zip(positions, positions[1:])) + positions[-1]


def bill(n, depth, width, owners, q, sign):
    need(sign in (-1, 1) and width >= 2 and owners >= 1, 'bill domain')
    size = 1 << (n*depth)
    d = n*n+n*depth
    length = d+2*width+2
    entry = permutation(q, n, depth)
    offset = sum(q << (n*j) for j in range(depth)) if sign == -1 else 0
    exit_order = [entry[bit_reverse(x,n*depth) ^ offset] for x in range(size)]
    entry = [entry[bit_reverse(x,n*depth)] for x in range(size)]
    scalar = owners*size*width
    tagged_moves = 4*owners*size*length - 2*owners*(d+3) - 2
    raw_moves = 2*owners*(variation(entry, width)+variation(exit_order, width))
    counts = {'read': (4+6*depth)*scalar, 'write': (6+6*depth)*scalar,
              'move': tagged_moves+raw_moves+20*depth*scalar}
    return {'actions': counts, 'total_cell_actions': sum(counts.values()),
            'tagged_moves': tagged_moves, 'raw_adapter_moves': raw_moves,
            'axis_cell_actions': 32*depth*scalar,
            'reserved_cells': owners*size*length+2+4*size*width,
            'physical_tapes': 7, 'axis_calls': owners*depth,
            'parameter_scope': 'finite fixture; symbolic all-size invoice in PHYSICAL.md'}


def execute(tagged, raw, n, depth, width, owners, q, sign, axis_module,
            omit_negative_offset=False, omit_raw_cleanup=False, omit_tag_reversal=False):
    """Only read/write/unit-move access touches payloads.

    Nonuniform control depends on n,depth,width,owners,q,sign. Numeric array
    indices here simulate that fixed compiled controller, not free tape reads.
    """
    size = 1 << (n*depth)
    d = n*n+n*depth
    length = d+2*width+2
    need(len(raw) == 6 and len({id(t) for t in [tagged]+raw}) == 7,
         'seven distinct tape objects')
    need(len({id(t.cells) for t in [tagged]+raw}) == 7, 'disjoint physical tape storage')
    need(len(tagged.cells) == owners*size*length+2, 'tagged reserved interval')
    need(all(t.head == t.origin for t in [tagged]+raw), 'entry heads at supplied origins')
    entry = permutation(q, n, depth)
    offset = sum(q << (n*j) for j in range(depth)) if sign == -1 else 0
    if omit_negative_offset:
        offset = 0
    for owner in range(owners):
        for record in range(size):
            x = record if omit_tag_reversal else bit_reverse(record,n*depth)
            for c in range(2):
                for bit in range(width):
                    seek(tagged, 1+(owner*size+record)*length+d+1+c*width+bit)
                    seek(raw[c], entry[x]*width+bit)
                    raw[c].write(tagged.read())
        for tape in raw[:2]:
            seek(tape, 0)
        for factor in range(depth):
            axis_module.axis_kernel(raw, n*depth, width, n*factor, 1)
        for record in range(size):
            x = record if omit_tag_reversal else bit_reverse(record,n*depth)
            for c in range(2):
                for bit in range(width):
                    seek(tagged, 1+(owner*size+record)*length+d+1+c*width+bit)
                    seek(raw[c], entry[x ^ offset]*width+bit)
                    tagged.write(raw[c].read())
                    if not omit_raw_cleanup:
                        raw[c].write(0)
        for tape in raw[:2]:
            seek(tape, 0)
    seek(tagged, 0)
    counts = Counter()
    for tape in [tagged]+raw:
        counts.update(tape.count)
    return dict(counts)


def oracle(re, im, q, n, depth, sign):
    """Exact direct signed C_q tensor, separately ordered from the adapter."""
    re, im = list(map(Fraction, re)), list(map(Fraction, im))
    for factor in range(depth):
        axis = q << (n*factor)
        rr = [(re[x]-sign*im[x]+re[x^axis]+sign*im[x^axis])/2 for x in range(len(re))]
        ii = [(im[x]+sign*re[x]+im[x^axis]-sign*re[x^axis])/2 for x in range(len(re))]
        re, im = rr, ii
    return re, im


def fixture(axis_module, n, depth, width, owners, q, sign, **mutations):
    size = 1 << (n*depth)
    d = n*n+n*depth
    length = d+2*width+2
    cells = ['^']
    inputs = []
    # Multiples of 2^depth ensure every axis numerator is even. Large width
    # supplies strict numerator room; ranges checked against exact oracle.
    for owner in range(owners):
        re = [((7*x+3*owner)%11-5)*(1 << depth) for x in range(size)]
        im = [((5*x+owner)%7-3)*(1 << depth) for x in range(size)]
        inputs.append((re,im))
        for record in range(size):
            x = bit_reverse(record,n*depth)
            tag = [int(c) for c in format(owner,'0'+str(n*n)+'b')] + [(x >> j)&1 for j in range(n*depth)]
            cells.extend(tag+[':']+axis_module.encode([re[x],im[x]],width)+[';'])
    cells.append('$')
    tagged = TaggedTape(cells, -13)
    original = tuple(cells)
    raw = [axis_module.Tape([1]*(size*width), 17+i*31) for i in range(2)]
    raw += [axis_module.Tape([1]*(size*width//2), -71-i*13, discardable=True) for i in range(4)]
    actual = execute(tagged,raw,n,depth,width,owners,q,sign,axis_module,**mutations)
    expected = bill(n,depth,width,owners,q,sign)
    need(all(t.head == t.origin for t in [tagged]+raw), 'all seven heads return')
    need(all(not any(t.cells) for t in raw), 'all six temporary windows zero')
    for owner, (re,im) in enumerate(inputs):
        rr,ii = oracle(re,im,q,n,depth,sign)
        need(all(v.denominator == 1 for v in rr+ii), 'integral oracle fixture')
        for record in range(size):
            x = bit_reverse(record,n*depth)
            start = 1+(owner*size+record)*length+d+1
            need(tagged.cells[start:start+2*width] == axis_module.encode([int(rr[x]),int(ii[x])],width),
                 'actual signed native endpoint')
    need(actual == expected['actions'], 'complete metered bill')
    payload = {1+k*length+d+1+b for k in range(owners*size) for b in range(2*width)}
    need(all(tagged.cells[j] == original[j] for j in range(len(cells)) if j not in payload),
         'tags and fences preserved')
    return {'n':n,'depth':depth,'width':width,'owners':owners,'q':q,'sign':sign,**expected}


def audit(axis_module):
    cases = [(2,1,10,2,3,1),(2,2,12,2,3,-1),(3,2,14,1,5,1),
             (5,1,12,2,19,-1),(5,1,12,1,19,1),(9,1,12,1,11,1),(9,1,12,1,448,-1)]
    records = [fixture(axis_module,*case) for case in cases]
    controls = {}
    for name, changes in [('missing negative offset', {'omit_negative_offset':True}),
                          ('missing raw cleanup', {'omit_raw_cleanup':True}),
                          ('missing tagged bit reversal', {'omit_tag_reversal':True})]:
        try:
            fixture(axis_module,2,1,10,1,1 if name == 'missing tagged bit reversal' else 3,-1,**changes)
        except ValueError as error:
            controls[name] = str(error)
        else:
            raise ValueError('ineffective control '+name)
    return {'status':'PASS_TAGGED_SIGNED_NATIVE_ADAPTER', 'fixtures':records,
            'controls':controls, 'conditional_physical_contract':True,
            'recursive_H1_tariff_admitted':False}


def coverage(word, native_receipt):
    """Bind actual4106calls to authenticated canonical native recipe data."""
    recipes = native_receipt['native']['signed_rank_one_recipes']
    index = {(r['port'],r['sign']):r for r in recipes}
    need(len(recipes) == len(index) == 224, 'complete112 signed source recipes')
    records = []
    for event, e in enumerate(word):
        if e[0] != 'line':
            continue
        _, field, port, sign = e
        r = index[port,sign]
        q = r['q']
        left = basis(q,9)
        right = [binary_map(r['right_columns'],x) for x in range(512)]
        need(r['rank'] == 1 and list(left) == r['left_columns'], 'literal rank/basis recipe')
        need(r['left_offset'] == (q if sign == -1 else 0), 'literal signed affine offset')
        need(all(binary_map(left,right[x]) == x for x in range(512)), 'actual wrapper inverse')
        # One input basis column has two Gaussian output coefficients. Compare
        # those exact complex numerators to the direct signed q formula.
        for x in range(512):
            u = right[x]
            offset = r['left_offset']
            actual = {binary_map(left,u)^offset:(1,1),
                      binary_map(left,u^1)^offset:(1,-1)}
            need(actual == {x:(1,sign),x^q:(1,-sign)}, 'all512signed native columns')
        records.append({'event':event,'field':field,'port':port,'q':q,'sign':sign})
    histogram = Counter(x['sign'] for x in records)
    occurrences = Counter((x['port'],x['sign']) for x in records)
    need(len(records) == 224 and histogram == {1:120,-1:104}, 'actual224call histogram')
    need(len(occurrences) == 216 and Counter(occurrences.values()) == {1:208,2:8}, 'recipe reuse histogram')
    return {'events':records,'positive':120,'negative':104,'distinct_recipes':216,
            'source_column_comparisons':224*512,'tensor_extension':
            'Independent factors preserve the checked basis identity for every integer depth>=1; n=73 identity spectators are explicit.'}
