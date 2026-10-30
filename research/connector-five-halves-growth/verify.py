"""Verify five-source depth-two connector blocks and N(c) >= floor(5c/2).

Stdlib only. Checks use explicit exceptions so they stay active under -O.
The prefix criterion, concatenation lemma, word builder and generic
simulation follow research/connector-depth-blocks (PR #4248).
"""
import hashlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
PACKAGE_FILES = ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json",
                 "CERTIFICATE.json", "verify.py")
K = 5
BASE_C = 6
BLOCK_MAX_C = 64
WORD_CS = (5, 6, 7)


class CheckError(Exception):
    pass


def require(cond, message):
    if not cond:
        raise CheckError(message)


def mask_vector(m, k):
    return tuple((m >> j) & 1 for j in range(k))


def prefixes(path, k, c):
    q = [0] * k
    out = [tuple(q)]
    for j in path:
        q[j] = (q[j] + 1) % c
        out.append(tuple(q))
    return out


def counts_ok(path, k, c):
    return all(path.count(j) == c for j in range(k)) and len(path) == c * k


def depth_two_readouts(path, k, c):
    """Map each nonzero mask to the first boundary pair whose prefixes sum to it."""
    qs = prefixes(path, k, c)
    found = {}
    for t1 in range(len(qs)):
        for t2 in range(t1, len(qs)):
            s = tuple((a + b) % c for a, b in zip(qs[t1], qs[t2]))
            if max(s) <= 1 and any(s):
                found.setdefault(sum(bit << i for i, bit in enumerate(s)), (t1, t2))
    return found


def lifted_prefixes(base, cut):
    """Integer prefix vectors of the base walk: count i, minus BASE_C after the cut."""
    cnt = [0] * K
    out = [tuple(cnt)]
    for j in base:
        cnt[j] += 1
        out.append(tuple(x if x <= cut[j] else x - BASE_C for j, x in enumerate(cnt)))
    return out


def check_template(base, cut):
    """Every nonzero mask is an integer sum of two lifted prefixes (proof core)."""
    require(counts_ok(base, K, BASE_C), "base walk counts")
    require(all(0 <= a < BASE_C for a in cut), "cut out of range")
    lp = lifted_prefixes(base, cut)
    require(lp[-1] == (0,) * K, "lifted walk does not return to zero")
    pairs = {}
    for t1 in range(len(lp)):
        for t2 in range(t1, len(lp)):
            s = tuple(a + b for a, b in zip(lp[t1], lp[t2]))
            if all(x in (0, 1) for x in s) and any(s):
                pairs.setdefault(sum(bit << i for i, bit in enumerate(s)), (t1, t2))
    require(set(pairs) == set(range(1, 2 ** K)), f"template covers {len(pairs)} of 31")
    return pairs


def expand(base, cut, c):
    """Replace the (cut_j+1)-th event of source j by a run of c-5 copies (none at c=5)."""
    seen = [0] * K
    path = []
    for j in base:
        seen[j] += 1
        path += [j] * (c - BASE_C + 1) if seen[j] == cut[j] + 1 else [j]
    return path


def expanded_boundary(base, cut, c, t):
    """Boundary of the expanded walk that follows base event t."""
    seen = [0] * K
    pos = 0
    for j in base[:t]:
        seen[j] += 1
        pos += c - BASE_C + 1 if seen[j] == cut[j] + 1 else 1
    return pos


def five_block(cert, c):
    return expand(cert["template_walk"], cert["template_cut"], c)


def check_blocks(cert, pairs):
    base, cut = cert["template_walk"], cert["template_cut"]
    for c in range(5, BLOCK_MAX_C + 1):
        path = five_block(cert, c)
        require(counts_ok(path, K, c), f"c={c} block counts")
        found = depth_two_readouts(path, K, c)
        require(set(found) == set(range(1, 2 ** K)), f"c={c} block covers {len(found)}")
        qs = prefixes(path, K, c)
        for m, (t1, t2) in pairs.items():
            u1 = expanded_boundary(base, cut, c, t1)
            u2 = expanded_boundary(base, cut, c, t2)
            s = tuple((a + b) % c for a, b in zip(qs[u1], qs[u2]))
            require(s == mask_vector(m, K), f"c={c} lifted readout fails for {m}")
    return BLOCK_MAX_C - 4


def floor_walk(cert, c):
    """Concatenate floor(c/2) five-source depth-two blocks and, for odd c, a b a^(c-1) b^(c-1)."""
    path, blocks = [], []
    src = 0
    for _ in range(c // 2):
        block = five_block(cert, c)
        start = len(path)
        hits = depth_two_readouts(block, K, c)
        path += [src + j for j in block]
        blocks.append((tuple(range(src, src + K)),
                       {mask_vector(m, K): (start + t1, start + t2)
                        for m, (t1, t2) in hits.items()}, 2))
        src += K
    if c % 2:
        a, b = src, src + 1
        start = len(path)
        path += [a, b] + [a] * (c - 1) + [b] * (c - 1)
        blocks.append(((a, b), {(1, 0): (start + 1,), (1, 1): (start + 2,),
                                (0, 1): (start + c + 1,)}, 1))
        src += 2
    return path, blocks, src


def floor_readouts(path, blocks, k, c):
    require(sum(d for _, _, d in blocks) <= c, "block depths exceed c")
    readouts = {}
    for m in range(1, 2 ** k):
        bits = mask_vector(m, k)
        ts = []
        for srcs, hit, _ in blocks:
            key = tuple(bits[j] for j in srcs)
            if any(key):
                ts += hit[key]
        require(len(ts) <= c, f"mask {m} needs {len(ts)} readouts")
        readouts[m] = tuple(ts) + (0,) * (c - len(ts))
    return readouts


def build_word(path, readouts):
    at = {}
    for m, ts in readouts.items():
        for t in ts:
            at.setdefault(t, []).append(m)
    word = []
    for t in range(len(path) + 1):
        word.extend(("A", m) for m in sorted(at.get(t, [])))
        if t < len(path):
            word.append(("B", path[t]))
    return word


def check_word(word, k, c):
    """Generic simulation over Z/c (PR #4248): z as coefficients of (z0, B_j x_j)."""
    z = [1] + [0] * k
    outs = {}
    for kind, idx in word:
        if kind == "B":
            z[1 + idx] = (z[1 + idx] + 1) % c
        else:
            acc = outs.setdefault(idx, [0] * (k + 1))
            for i in range(k + 1):
                acc[i] += z[i]
    require(z == [1] + [0] * k, "connector not restored")
    require(set(outs) == set(range(1, 2 ** k)), "output set mismatch")
    for m, acc in outs.items():
        acc = [x % c for x in acc]
        require(acc[0] == 0, f"connector dirt left in output {m}")
        require(tuple(acc[1:]) == mask_vector(m, k), f"wrong row for output {m}")
    counts = {}
    for call in word:
        counts[call] = counts.get(call, 0) + 1
    require(set(counts.values()) == {c}, "some operator not called exactly c times")
    require(len(counts) == k + 2 ** k - 1, "operator set mismatch")
    require(len(word) == c * (k + 2 ** k - 1), "length differs from the floor")


def check_floor_words(cert):
    out = {}
    for c in WORD_CS:
        path, blocks, k = floor_walk(cert, c)
        require(k == 5 * c // 2, f"c={c} source count {k}")
        require(counts_ok(path, k, c), f"c={c} floor walk counts")
        word = build_word(path, floor_readouts(path, blocks, k, c))
        check_word(word, k, c)
        out[c] = (k, len(word))
    return out


def check_controls(cert):
    rejected = 0
    base, cut = cert["template_walk"], cert["template_cut"]
    trials = [
        # The unexpanded c=6 block read in characteristic seven.
        lambda: require(len(depth_two_readouts(base, K, 7)) == 31, "c6 block mod 7"),
        # The c=5 block read in characteristic four (the walk is not a c=4 walk).
        lambda: require(len(depth_two_readouts(expand(base, cut, 5), K, 4)) == 31, "c5 block mod 4"),
        # Moving every cut one event later breaks the integer criterion.
        lambda: check_template(base, [a + 1 for a in cut]),
        # Three five-source blocks exceed the five readouts at c=5.
        lambda: floor_readouts(*_three_blocks(cert)),
        # A floor word with one readout call dropped.
        lambda: _dropped_readout(cert),
    ]
    for trial in trials:
        try:
            trial()
        except CheckError:
            rejected += 1
    require(rejected == len(trials), f"only {rejected} of {len(trials)} controls rejected")
    return rejected


def _three_blocks(cert):
    block = five_block(cert, 5)
    hits = depth_two_readouts(block, K, 5)
    path, blocks = [], []
    for b in range(3):
        start = len(path)
        path += [K * b + j for j in block]
        blocks.append((tuple(range(K * b, K * b + K)),
                       {mask_vector(m, K): (start + t1, start + t2)
                        for m, (t1, t2) in hits.items()}, 2))
    return path, blocks, 3 * K, 5


def _dropped_readout(cert):
    path, blocks, k = floor_walk(cert, 5)
    word = build_word(path, floor_readouts(path, blocks, k, 5))
    word.remove(("A", 2 ** k - 1))
    check_word(word, k, 5)


def receipt():
    h = hashlib.sha256()
    for name in PACKAGE_FILES:
        data = (HERE / name).read_bytes()
        h.update(name.encode() + b"\0" + hashlib.sha256(data).hexdigest().encode() + b"\n")
    return h.hexdigest()


def main():
    cert = json.loads((HERE / "CERTIFICATE.json").read_text())
    pairs = check_template(cert["template_walk"], cert["template_cut"])
    blocks = check_blocks(cert, pairs)
    words = check_floor_words(cert)
    controls = check_controls(cert)
    print(f"template_integer_masks={len(pairs)} depth_two_blocks_checked={blocks} "
          f"(c=5..{BLOCK_MAX_C})")
    print("floor_words", " ".join(f"c{c}:k{k}:calls{n}" for c, (k, n) in words.items()))
    print(f"controls={controls}")
    print("receipt_sha256", receipt())
    print("PASS_CONNECTOR_FIVE_HALVES depth_two_k5_every_c>=5 N(c)>=floor(5c/2)")


if __name__ == "__main__":
    try:
        main()
    except CheckError as exc:
        print("FAIL", exc)
        sys.exit(1)
