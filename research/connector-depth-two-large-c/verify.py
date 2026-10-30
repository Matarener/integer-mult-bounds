"""Verify six-, seven- and eight-source depth-two unsigned-connector blocks for every large c.

Stdlib only. Checks use explicit exceptions so they stay active under -O.
The lifted-template criterion is Nick Petalas's (research/connector-five-halves-growth,
PR #6035, merged at 119de1d7f), generalized from base multiplicity 6 to any
base multiplicity u. The prefix criterion, concatenation lemma, word builder
and generic simulation follow research/connector-depth-blocks (PR #4248).
No predecessor code is imported.
"""
import hashlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
PACKAGE_FILES = ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json",
                 "CERTIFICATE.json", "verify.py")
BLOCK_MAX_C = {"six": 64, "seven": 64, "eight": 40}
# (c, template name, number of depth-two blocks, append a depth-one pair block)
WORD_CASES = ((8, "six", 1, False), (8, "six", 2, False), (9, "six", 2, True),
              (12, "seven", 1, False), (13, "seven", 1, True), (12, "seven", 2, False),
              (27, "eight", 1, False), (27, "eight", 1, True))


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
    """Map each nonzero mask to the first boundary pair whose prefixes sum to it mod c."""
    qs = prefixes(path, k, c)
    found = {}
    for t1 in range(len(qs)):
        for t2 in range(t1, len(qs)):
            s = tuple((a + b) % c for a, b in zip(qs[t1], qs[t2]))
            if max(s) <= 1 and any(s):
                found.setdefault(sum(bit << i for i, bit in enumerate(s)), (t1, t2))
    return found


def lifted_prefixes(base, cut, k, u):
    """Integer prefix vectors of the base walk: count n, minus u once n > cut."""
    cnt = [0] * k
    out = [tuple(cnt)]
    for j in base:
        cnt[j] += 1
        out.append(tuple(x if x <= cut[i] else x - u for i, x in enumerate(cnt)))
    return out


def check_template(base, cut, k, u):
    """Every nonzero mask is an integer sum of two lifted prefixes (finite proof core)."""
    require(counts_ok(base, k, u), "base walk counts")
    require(len(cut) == k and all(0 <= a < u for a in cut), "cut out of range")
    lp = lifted_prefixes(base, cut, k, u)
    require(lp[-1] == (0,) * k, "lifted walk does not return to zero")
    pairs = {}
    for t1 in range(len(lp)):
        for t2 in range(t1, len(lp)):
            s = tuple(a + b for a, b in zip(lp[t1], lp[t2]))
            if all(x in (0, 1) for x in s) and any(s):
                pairs.setdefault(sum(bit << i for i, bit in enumerate(s)), (t1, t2))
    require(set(pairs) == set(range(1, 2 ** k)), f"template covers {len(pairs)} of {2 ** k - 1}")
    return pairs


def expand(base, cut, u, c):
    """Replace the (cut_j+1)-th event of source j by a run of c-u+1 copies (none at c=u-1)."""
    require(c >= u - 1, "expansion needs c >= u-1")
    seen = [0] * len(cut)
    path = []
    for j in base:
        seen[j] += 1
        path += [j] * (c - u + 1) if seen[j] == cut[j] + 1 else [j]
    return path


def expanded_boundary(base, cut, u, c, t):
    """Boundary of the expanded walk that follows base event t."""
    seen = [0] * len(cut)
    pos = 0
    for j in base[:t]:
        seen[j] += 1
        pos += c - u + 1 if seen[j] == cut[j] + 1 else 1
    return pos


def unpack(tpl):
    return tpl["walk"], tpl["cut"], tpl["sources"], tpl["base_multiplicity"]


def check_blocks(tpl, pairs):
    base, cut, k, u = unpack(tpl)
    require(tpl["min_c"] == u - 1, "declared minimum characteristic")
    for c in range(u - 1, BLOCK_MAX_C[tpl["name"]] + 1):
        path = expand(base, cut, u, c)
        require(counts_ok(path, k, c), f"c={c} block counts")
        found = depth_two_readouts(path, k, c)
        require(set(found) == set(range(1, 2 ** k)), f"c={c} block covers {len(found)}")
        qs = prefixes(path, k, c)
        for m, (t1, t2) in pairs.items():
            u1 = expanded_boundary(base, cut, u, c, t1)
            u2 = expanded_boundary(base, cut, u, c, t2)
            s = tuple((a + b) % c for a, b in zip(qs[u1], qs[u2]))
            require(s == mask_vector(m, k), f"c={c} lifted readout fails for {m}")
    return BLOCK_MAX_C[tpl["name"]] - u + 2


def concat_walk(tpl, c, nblocks, pair):
    """Concatenate depth-two blocks on disjoint sources and optionally a b a^(c-1) b^(c-1)."""
    base, cut, k, u = unpack(tpl)
    block = expand(base, cut, u, c)
    hits = depth_two_readouts(block, k, c)
    path, blocks = [], []
    src = 0
    for _ in range(nblocks):
        start = len(path)
        path += [src + j for j in block]
        blocks.append((tuple(range(src, src + k)),
                       {mask_vector(m, k): (start + t1, start + t2)
                        for m, (t1, t2) in hits.items()}, 2))
        src += k
    if pair:
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


def check_floor_words(tpls):
    out = []
    for c, name, nblocks, pair in WORD_CASES:
        tpl = tpls[name]
        path, blocks, k = concat_walk(tpl, c, nblocks, pair)
        require(k == tpl["sources"] * nblocks + 2 * pair, f"c={c} source count {k}")
        require(counts_ok(path, k, c), f"c={c} floor walk counts")
        word = build_word(path, floor_readouts(path, blocks, k, c))
        check_word(word, k, c)
        out.append((c, k, len(word)))
    return out


SWAP_INDEX = 2  # base events 2 and 3 of the six-source walk (sources 0 and 1)


def swapped(base, i):
    """The base walk with events i and i+1 (distinct sources) exchanged."""
    w = list(base)
    require(w[i] != w[i + 1], "swap of equal sources")
    w[i], w[i + 1] = w[i + 1], w[i]
    return w


def check_controls(tpls):
    six = tpls["six"]
    base, cut, k, u = unpack(six)

    def five_blocks():
        path, blocks, kk = concat_walk(six, 8, 5, False)
        floor_readouts(path, blocks, kk, 8)

    def dropped_readout():
        path, blocks, kk = concat_walk(six, 8, 1, False)
        word = build_word(path, floor_readouts(path, blocks, kk, 8))
        word.remove(("A", 2 ** kk - 1))
        check_word(word, kk, 8)

    sb, sc, sk, su = unpack(tpls["seven"])
    trials = [
        # The unexpanded six-source base walk (a c=9 walk) read in characteristic ten.
        lambda: require(len(depth_two_readouts(base, k, 10)) == 2 ** k - 1, "c9 block mod 10"),
        # The c=8 block read in characteristic seven (it is not a c=7 walk).
        lambda: require(len(depth_two_readouts(expand(base, cut, u, 8), k, 7)) == 2 ** k - 1,
                        "c8 block mod 7"),
        # The c=12 seven-source block read in characteristic 11 (83 of 127 masks).
        lambda: require(len(depth_two_readouts(expand(sb, sc, su, 12), sk, 11)) == 2 ** sk - 1,
                        "c12 seven block mod 11"),
        # Moving every cut one event later breaks the integer criterion.
        lambda: check_template(base, [a + 1 for a in cut], k, u),
        lambda: check_template(sb, [a + 1 for a in sc], sk, su),
        lambda: check_template(*_eight_shifted(tpls["eight"])),
        # One adjacent transposition of the base walk breaks the criterion.
        lambda: check_template(swapped(base, SWAP_INDEX), cut, k, u),
        # Five six-source depth-two blocks exceed the eight readouts at c=8.
        five_blocks,
        # A floor word with one readout call dropped.
        dropped_readout,
    ]
    rejected = 0
    for trial in trials:
        try:
            trial()
        except CheckError:
            rejected += 1
    require(rejected == len(trials), f"only {rejected} of {len(trials)} controls rejected")
    return rejected


def _eight_shifted(tpl):
    base, cut, k, u = unpack(tpl)
    return base, [a + 1 for a in cut], k, u


def corollary_k(tpls, c):
    """Largest k*floor(c/2)+2(c%2) over templates valid at c (PR6035's bound if none)."""
    best = 5 * c // 2 if c >= 5 else 2 * c
    for tpl in tpls.values():
        if c >= tpl["base_multiplicity"] - 1:
            best = max(best, tpl["sources"] * (c // 2) + 2 * (c % 2))
    return best


def check_counting(tpls):
    """Consistency: every corollary value satisfies PR4248's counting necessary condition."""
    from math import comb
    for c in range(8, 129):
        k = corollary_k(tpls, c)
        require(comb(c * k + c - 1, c) >= 2 ** k - 1, f"corollary k={k} at c={c} violates counting")
    return [(c, corollary_k(tpls, c)) for c in (8, 9, 12, 13, 14, 27, 28)]


def receipt():
    h = hashlib.sha256()
    for name in PACKAGE_FILES:
        data = (HERE / name).read_bytes()
        h.update(name.encode() + b"\0" + hashlib.sha256(data).hexdigest().encode() + b"\n")
    return h.hexdigest()


def main():
    cert = json.loads((HERE / "CERTIFICATE.json").read_text())
    tpls = {t["name"]: t for t in cert["templates"]}
    require(set(tpls) == {"six", "seven", "eight"}, "template set")
    require([tpls[n]["sources"] for n in ("six", "seven", "eight")] == [6, 7, 8], "template sizes")
    lines = []
    for name in ("six", "seven", "eight"):
        tpl = tpls[name]
        base, cut, k, u = unpack(tpl)
        pairs = check_template(base, cut, k, u)
        nblocks = check_blocks(tpl, pairs)
        lines.append(f"k{k}:u{u}:integer_masks={len(pairs)}:blocks_c{u - 1}..{BLOCK_MAX_C[name]}={nblocks}")
    words = check_floor_words(tpls)
    controls = check_controls(tpls)
    table = check_counting(tpls)
    require(table == [(8, 24), (9, 26), (12, 42), (13, 44), (14, 49), (27, 106), (28, 112)],
            "README corollary table")
    print("templates", " ".join(lines))
    print("corollary", " ".join(f"N({c})>={k}" for c, k in table), "counting_consistent_c8..128")
    print("floor_words", " ".join(f"c{c}:k{k}:calls{n}" for c, k, n in words))
    print(f"controls={controls}")
    print("receipt_sha256", receipt())
    print("PASS_CONNECTOR_DEPTH_TWO_6_7_8 k6_every_c>=8 k7_every_c>=12 k8_every_c>=27 "
          "N(c)>=k*floor(c/2)+2(c%2)")


if __name__ == "__main__":
    try:
        main()
    except CheckError as exc:
        print("FAIL", exc)
        sys.exit(1)
