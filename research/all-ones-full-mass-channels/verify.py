"""Exact finite checks for PROOF.md: maximum-mass destination channels at n = 2^g - 1.

Model (PR2177 PROOF3 Part B): unit errors at the destinations of distinct completed leaves of
PR628's balanced reserved-depth dirty word, read in one register w at one later cut t. The
channel of leaf i is the free-algebra entry M_{i->t}[w, y_i]; its mass is the absolute
coefficient sum. All factors are free noncommuting symbols.

Checks:
  WORD   this word generator equals the predecessor's check2.gen leaf order, n = 1..64, both signs
  G      a call of size 2^h (h = 1..5) has exactly two leaves whose exit has h scratch entries
  P2     size 2^h (h = 2..5): mass-h channels only at top cuts in V (+, <= 1), V' (+, <= 2) and
         V' (-, <= 1); each bound attained
  CLASS  n = 2^g - 1 (g = 3..6): every channel has mass <= g - 1, and the class bounds of PROOF.md
  MAIN   at most 4g - 3 channels of mass g - 1 at any cut and register; equality is attained
  CTRL   ceil-half split mutation breaks MAIN or CLASS; an understated bound 4g - 4 is rejected
Usage: python3 -B verify.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PRED = os.path.join(HERE, '..', 'leaf-destination-transport-bound')


def word(n, s, x=0, y=1, depth=1, base=0, ceil_split=False):
    """PR628 word as leaves (x, y, factor, sign). Scratch level d is register 1 + d."""
    if n == 1:
        return [(x, y, base, s)]
    b = (n + 1) // 2 if ceil_split else n // 2
    z = 1 + depth

    def U(sg):
        return word(b, sg, x, z, depth + 1, base, ceil_split)

    def V(sg):
        return word(n - b, sg, z, y, depth + 1, base + b, ceil_split)

    parts = [U(1), V(1), U(-1), V(-1)] if s == 1 else [V(1), U(1), V(-1), U(-1)]
    return [e for p in parts for e in p]


def top_phases(n, s, ceil_split=False):
    """Top-call phase name of every leaf, in time order."""
    b = (n + 1) // 2 if ceil_split else n // 2
    names = ['U', 'V', "U'", "V'"] if s == 1 else ['V', 'U', "V'", "U'"]
    out = []
    for name, sg in zip(names, (1, 1, -1, -1)):
        k = b if name[0] == 'U' else n - b
        out += [name] * len(word(k, sg, ceil_split=ceil_split))
    return out


def registers(n):
    return 2 + max(1, (n - 1).bit_length())


def channels(w_, R):
    """For every cut t and register v: list of (leaf i, channel mass) for nonzero channels.

    Backward row propagation: row v of Pre(i -> t) is updated by each leaf transposed."""
    for t in range(len(w_)):
        rows = [{v: {(): 1}} for v in range(R)]
        resp = [[] for _ in range(R)]
        for j in range(t, -1, -1):
            x, y, f, sg = w_[j]
            for v in range(R):
                r = rows[v]
                p = r.get(y)
                if p:
                    resp[v].append((j, sum(abs(c) for c in p.values())))
                    q = r.setdefault(x, {})
                    for m, c in p.items():
                        k = m + (f,)
                        val = q.get(k, 0) + sg * c
                        if val:
                            q[k] = val
                        else:
                            del q[k]
        for v in range(R):
            yield t, v, resp[v]


def exit_scratch_sizes(n, s):
    """Number of nonzero scratch entries of each leaf's exit column (forward transport)."""
    w_ = word(n, s)
    out = []
    for i, (_, yi, _, _) in enumerate(w_):
        col = {yi: {(): 1}}
        for x, y, f, sg in w_[i + 1:]:
            cx = col.get(x)
            if not cx:
                continue
            cy = col.setdefault(y, {})
            for m, c in cx.items():
                k = (f,) + m
                val = cy.get(k, 0) + sg * c
                if val:
                    cy[k] = val
                else:
                    del cy[k]
        out.append(sum(1 for v, p in col.items() if v >= 2 and p))
    return out


def F(k):
    """PROOF3 Lemma F closed form: 2j - 1, j = number of leading 1-bits of k."""
    s = bin(k)[2:]
    return 2 * (len(s) - len(s.lstrip('1'))) - 1


def census(n, ceil_split=False):
    """Per (sign, top cut phase): max over cuts/registers of (U-start, V-start, same-phase, all)
    counts of mass-fl(n) channels; plus the global maximum channel mass."""
    H = n.bit_length() - 1
    worst, maxmass = {}, 0
    for s in (1, -1):
        ph = top_phases(n, s, ceil_split)
        for t, _, resp in channels(word(n, s, ceil_split=ceil_split), registers(n)):
            maxmass = max([maxmass] + [m for _, m in resp])
            full = [i for i, m in resp if m == H]
            cu = sum(1 for i in full if ph[i] != ph[t] and ph[i][0] == 'U')
            cv = sum(1 for i in full if ph[i] != ph[t] and ph[i][0] == 'V')
            cc = sum(1 for i in full if ph[i] == ph[t])
            key = (s, ph[t])
            old = worst.get(key, (0, 0, 0, 0, 0))
            worst[key] = tuple(max(a, b) for a, b in zip(old, (cu, cv, cc, cv + cc, len(full))))
    return worst, maxmass


def class_bounds(g):
    """PROOF.md section 3 bounds: (U-start, V-start, same-phase, V-start + same-phase, all)."""
    Fb = F(2 ** (g - 1) - 1)
    return {
        (1, 'U'): (0, 0, 0, 0, 0),
        (1, 'V'): (Fb, 0, 2, 2, Fb + 2),
        (1, "U'"): (0, 2, 0, 2, 2),
        (1, "V'"): (2 * Fb, 3, 1, 3, 2 * Fb + 3),
        (-1, 'V'): (0, 0, 2, 2, 2),
        (-1, 'U'): (0, 2, 0, 2, 2),
        (-1, "V'"): (Fb, 3, 1, 3, Fb + 3),
        (-1, "U'"): (0, 4, 0, 4, 4),
    }


def check_main(g, worst, maxmass, bound):
    fails = []
    if maxmass > g - 1:
        fails.append(('MASS', maxmass))
    for key, lim in class_bounds(g).items():
        got = worst.get(key, (0,) * 5)
        if any(a > b for a, b in zip(got, lim)):
            fails.append(('CLASS', key, got, lim))
    top = max(v[4] for v in worst.values())
    if top > bound:
        fails.append(('MAIN', top, bound))
    return top, fails


def main():
    sys.path.insert(0, os.path.abspath(PRED))
    import check2  # predecessor generator, used only for the WORD cross-check

    bad = []
    for n in range(1, 65):
        for s in (1, -1):
            if word(n, s) != [e for e, _ in check2.gen(n, s)]:
                bad.append(('WORD', n, s))
    print('WORD n=1..64 both signs', 'ok' if not bad else bad[:3])

    for h in range(1, 6):
        for s in (1, -1):
            sizes = exit_scratch_sizes(2 ** h, s)
            if max(sizes) != h or sizes.count(h) != 2:
                bad.append(('G', h, s, max(sizes), sizes.count(h)))
    print('G h=1..5', 'ok' if not any(b[0] == 'G' for b in bad) else 'FAIL')

    want = {(1, 'V'): 1, (1, "V'"): 2, (-1, "V'"): 1}
    for h in range(2, 6):
        worst, maxmass = census(2 ** h)
        got = {k: v[4] for k, v in worst.items() if v[4]}
        if maxmass != h or got != want:
            bad.append(('P2', h, maxmass, got))
    print('P2 h=2..5', 'ok' if not any(b[0] == 'P2' for b in bad) else 'FAIL')

    for g in range(3, 7):
        n = 2 ** g - 1
        worst, maxmass = census(n)
        top, fails = check_main(g, worst, maxmass, 4 * g - 3)
        if top != 4 * g - 3:
            fails.append(('ATTAIN', top))
        under = check_main(g, worst, maxmass, 4 * g - 4)[1]
        if not any(f[0] == 'MAIN' for f in under):
            fails.append(('CTRL-UNDER',))
        bad += fails
        print('MAIN g', g, 'n', n, 'max full-mass count', top, '= 4g-3' if top == 4 * g - 3 else '',
              'ok' if not fails else fails[:3], flush=True)

    ctrl_hits = 0
    for g in range(3, 6):
        worst, maxmass = census(2 ** g - 1, ceil_split=True)
        if check_main(g, worst, maxmass, 4 * g - 3)[1]:
            ctrl_hits += 1
    if ctrl_hits == 0:
        bad.append(('CTRL-CEIL',))
    print('CTRL ceil-half split rejected at', ctrl_hits, 'of 3 sizes')

    if bad:
        print('FAIL', bad[:5])
        return 1
    print('PASS_ALL_ONES_FULL_MASS_CHANNELS')
    return 0


if __name__ == '__main__':
    sys.exit(main())
