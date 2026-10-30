"""Independent audit of the upward/reversed-downward connector construction.

Stdlib; a separate reflected recursion and literal 2x2 matrix execution over
Z/c, including singular noncommuting maps and arbitrary dirty input columns.
Prepared by apoursh with substantial OpenAI Codex assistance. Apache-2.0.
The interface and depth-one pair are credited to Nick Petalas (PR4248/6035),
following Ross Richardson and the retained unsigned connector lineage.
No claim of an independent human or formal-kernel review.
"""
from collections import Counter, defaultdict


def require(value, message):
    if not value:
        raise ValueError(message)


def gray(k):
    if k == 0:
        return [0]
    previous = gray(k - 1)
    return previous + [x | (1 << (k - 1)) for x in reversed(previous)]


def block(path, k, c):
    require(path[0] == 0, 'start')
    up, down = [], []
    locations = {0: (0, 0)}
    for old, new in zip(path, path[1:]):
        delta = old ^ new
        require(delta > 0 and not delta & (delta - 1), 'one bit')
        j = delta.bit_length() - 1
        require(j < k, 'coordinate')
        (up if new & delta else down).append(j)
        locations.setdefault(new, (len(up), len(down)))
    require(set(locations) == set(range(1 << k)), 'cover')
    counts = Counter(up + down)
    require(max(counts.values(), default=0) <= c, 'capacity')
    middle = [j for j in range(k) for _ in range(c - counts[j])]
    word = up + middle + list(reversed(down))
    pairs = {m: [a, len(word) - d] for m, (a, d) in locations.items() if m}
    return word, pairs


def check_prefix(word, reads, k, c, *, depth=None):
    require(Counter(word) == Counter({j: c for j in range(k)}), 'source counts')
    pref = [[0] * k]
    for j in word:
        q = pref[-1].copy()
        q[j] += 1
        pref.append(q)
    require(set(reads) == set(range(1, 1 << k)), 'output set')
    for mask, times in reads.items():
        require(depth is None or len(times) <= depth, 'depth')
        require(all(0 <= t <= len(word) for t in times), 'boundary')
        require(all(sum(pref[t][j] for t in times) % c == (mask >> j & 1)
                    for j in range(k)), 'wrong mask')


def compose(parts, c):
    word, total_k, all_parts = [], 0, []
    for subword, subreads, k in parts:
        all_parts.append((len(word), total_k, subreads, k))
        word.extend(j + total_k for j in subword)
        total_k += k
    reads = {}
    for mask in range(1, 1 << total_k):
        times = []
        for offset, shift, subreads, k in all_parts:
            submask = mask >> shift & ((1 << k) - 1)
            if submask:
                times.extend(t + offset for t in subreads[submask])
        require(len(times) <= c, 'read budget')
        reads[mask] = sorted([0] * (c - len(times)) + times)
    return word, reads, total_k


ZERO = (0, 0, 0, 0)
I = (1, 0, 0, 1)


def add(a, b, c):
    return tuple((x + y) % c for x, y in zip(a, b))


def mul(a, b, c):
    return ((a[0]*b[0]+a[1]*b[2]) % c, (a[0]*b[1]+a[1]*b[3]) % c,
            (a[2]*b[0]+a[3]*b[2]) % c, (a[2]*b[1]+a[3]*b[3]) % c)


def literal(word, reads, k, c):
    """Apply every call to exact block matrices for all arbitrary input columns."""
    check_prefix(word, reads, k, c)
    require(all(len(ts) == c for ts in reads.values()), 'complete A count')
    maps = [(0, 1, 0, 0), (0, 0, 1, 0), (1, 1, 0, 1), (1, 0, 1, 1)]
    B = [maps[j % 4] for j in range(k)]
    A = {m: maps[(m + 1) % 4] for m in reads}
    # Input block k is the arbitrary initial dirty connector, the others sources.
    z = [ZERO] * k + [I]
    y = {m: [ZERO] * (k + 1) for m in reads}
    at = defaultdict(list)
    for m, ts in reads.items():
        for t in ts:
            at[t].append(m)
    for t in range(len(word) + 1):
        for m in at[t]:
            y[m] = [add(old, mul(A[m], q, c), c) for old, q in zip(y[m], z)]
        if t < len(word):
            j = word[t]
            z[j] = add(z[j], B[j], c)
    require(z == [ZERO] * k + [I], 'dirty restoration')
    for m in reads:
        expected = [mul(A[m], B[j], c) if m >> j & 1 else ZERO for j in range(k)] + [ZERO]
        require(y[m] == expected, 'literal operator')
    require(mul(maps[0], maps[1], c) != mul(maps[1], maps[0], c), 'noncommuting control')
    return len(word) + sum(map(len, reads.values()))


def rejected(fn):
    try:
        fn()
    except ValueError:
        return 1
    raise ValueError('mutation accepted')


def run():
    blocks = calls = 0
    # Independent reflected recursion, both simple paths and repeated-label
    # paths with an inserted closed excursion before the complete Gray path.
    for k in range(1, 8):
        path = gray(k)
        flip = Counter((a ^ b).bit_length()-1 for a,b in zip(path,path[1:]))
        require([flip[j] for j in range(k)] == [1 << (k - 1 - j) for j in range(k)], 'flip law')
        for c in [max(flip.values()), max(flip.values()) + 1, max(flip.values()) + 3]:
            if c < 2:
                continue
            w, r = block(path, k, c)
            check_prefix(w, r, k, c, depth=2)
            full = {m: [0] * (c-2) + ts for m, ts in r.items()}
            calls += literal(w, full, k, c)
            require(len(w) + c * len(r) == c * (k + (1 << k)-1), 'floor')
            blocks += 1
        repeated = [0, 1, 0] + path[1:]
        counts = Counter((a ^ b).bit_length()-1 for a,b in zip(repeated,repeated[1:]))
        c = max(counts.values())
        w,r = block(repeated,k,c)
        calls += literal(w,{m:[0]*(c-2)+ts for m,ts in r.items()},k,c)
        blocks += 1
    composed = 0
    for c in range(2,7):
        k = min(3,c.bit_length())
        w,r = block(gray(k),k,c)
        parts = [(w,r,k)] * (c//2)
        if c % 2:
            # Independent depth-one two-source fixture from predecessor.
            tail = [0,1]+[0]*(c-1)+[1]*(c-1)
            parts.append((tail,{1:[1],3:[2],2:[c+1]},2))
        joined, reads, n = compose(parts,c)
        require(n == k*(c//2)+2*(c%2), 'source count formula')
        calls += literal(joined,reads,n,c)
        composed += 1
    w,r = block(gray(3),3,4)
    controls = 0
    controls += rejected(lambda: block(gray(3),3,3))
    controls += rejected(lambda: block([1,0],1,2))
    controls += rejected(lambda: block([0,3],2,2))
    controls += rejected(lambda: block([0,1],2,2))
    controls += rejected(lambda: check_prefix(w[:-1],r,3,4))
    altered={m:ts.copy() for m,ts in r.items()}
    altered[1]=[0,0]
    controls += rejected(lambda: check_prefix(w,altered,3,4))
    bad_middle=w.copy();bad_middle[0]=1
    controls += rejected(lambda: check_prefix(bad_middle,r,3,4))
    # Reverse-down order is essential: its first nontrivial counterexample.
    longer,lr=block(gray(4),4,8)
    up=[(a^b).bit_length()-1 for a,b in zip(gray(4),gray(4)[1:]) if b&(a^b)]
    down=[(a^b).bit_length()-1 for a,b in zip(gray(4),gray(4)[1:]) if not b&(a^b)]
    bad=longer[:-len(down)]+down
    controls += rejected(lambda: check_prefix(bad,lr,4,8))
    controls += rejected(lambda: compose([(w,r,3)]*3,4))
    print(f'PASS_GRAY_CONNECTOR_INDEPENDENT blocks={blocks} composed={composed} literal_calls={calls} controls={controls}')

if __name__=='__main__':
    run()
