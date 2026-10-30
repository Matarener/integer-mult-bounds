"""Primary 3+3 method (run by verify.py; numpy_crosscheck.py is the second method): stdlib only, column-major encoding,
right-multiplication meet-in-the-middle with splits 6+3 (restricted) and 5+3 (unrestricted).
Imports nothing from lemma.py or numpy_crosscheck.py.  Column c of a 6x6 F2 matrix is the 6-bit field at 6c."""
import itertools

COL0 = sum(1 << (6 * c) for c in range(6))


def gate(x, d, s):                     # row d ^= row s, applied to every column field
    return x ^ (((x >> s) & COL0) << d)


def ball(gens, radius):
    ident = sum(1 << (7 * c) for c in range(6))
    dist = {ident: 0}
    front = [ident]
    for k in range(1, radius + 1):
        nxt = []
        for x in front:
            for d, s in gens:
                y = gate(x, d, s)
                if y not in dist:
                    dist[y] = k
                    nxt.append(y)
        front = nxt
    return dist


def right_table(M):
    cols = [(M >> (6 * c)) & 63 for c in range(6)]
    tab = [0] * 64
    for pat in range(1, 64):
        low = pat & -pat
        tab[pat] = tab[pat ^ low] ^ cols[low.bit_length() - 1]
    return tab


def mitm(M, small, big, cap):
    """min |u|+|v| over M*u = v with u in small, v in big (exact when <= cap), else cap+1."""
    tab = right_table(M)
    best = cap + 1
    for u, du in small.items():
        x = 0
        for c in range(6):
            x |= tab[(u >> (6 * c)) & 63] << (6 * c)
        dv = big.get(x)
        if dv is not None and du + dv < best:
            best = du + dv
    return best


def exits():
    """All (T, K): T in GL3(F2), K in M_3x3(F2); column-major 6x6 [[T,0],[K,I]]."""
    def inv3(T):
        rows = [[T[r][c] for c in range(3)] + [int(r == c) for c in range(3)] for r in range(3)]
        for c in range(3):
            p = next((r for r in range(c, 3) if rows[r][c]), None)
            if p is None:
                return False
            rows[c], rows[p] = rows[p], rows[c]
            for r in range(3):
                if r != c and rows[r][c]:
                    rows[r] = [a ^ b for a, b in zip(rows[r], rows[c])]
        return True
    out = []
    for tb in range(512):
        T = [[tb >> (3 * r + c) & 1 for c in range(3)] for r in range(3)]
        if not inv3(T):
            continue
        for kb in range(512):
            K = [[kb >> (3 * r + c) & 1 for c in range(3)] for r in range(3)]
            x = 0
            for r in range(6):
                for c in range(6):
                    if r < 3 and c < 3:
                        v = T[r][c]
                    elif r >= 3 and c < 3:
                        v = K[r - 3][c]
                    else:
                        v = int(r == c)
                    x |= v << (6 * c + r)
            out.append((T, K, x))
    return out


def canonical(T, K):
    best = None
    for s in itertools.permutations(range(3)):
        Tp = tuple(tuple(T[s.index(r)][s.index(c)] for c in range(3)) for r in range(3))
        Kp = tuple(sorted(tuple(K[r][s.index(c)] for c in range(3)) for r in range(3)))
        key = (Tp, Kp)
        if best is None or key < best:
            best = key
    return best


def main():
    full = [(d, s) for d in range(6) for s in range(6) if d != s]
    restr = [(d, s) for d, s in full if not (d < 3 <= s)]
    B3, B5 = ball(full, 3), ball(full, 5)
    P3, P6 = ball(restr, 3), ball(restr, 6)
    blk = sum(1 << (6 * c + r) for r in range(3) for c in range(3, 6))  # helper rows x target columns
    assert not any(k & blk for k in P3) and not any(k & blk for k in P6)  # restricted balls stay in P_{3,3}
    E = exits()
    classes = {}
    for T, K, x in E:
        classes.setdefault(canonical(T, K), []).append((T, K, x))
    hist_p, hist_f, adv, twisted = {}, {}, 0, 0
    for key, members in classes.items():
        T, K, x = members[0]
        dp = mitm(x, P3, P6, 9)
        df = mitm(x, B3, B5, 8)
        assert dp <= 9 and df <= dp, (key, dp, df)  # every exit has a restricted word of length <= 9
        for T, K, _ in members:
            if T != [[1, 0, 0], [0, 1, 0], [0, 0, 1]]:
                twisted += 1
                hist_p[dp] = hist_p.get(dp, 0) + 1
                hist_f[min(df, dp)] = hist_f.get(min(df, dp), 0) + 1
                adv += df < dp
    print("independent33 exits", len(E), "classes", len(classes), "twisted", twisted,
          "strict_advantage", adv, "dP_hist", sorted(hist_p.items()), "dfull_hist", sorted(hist_f.items()))
    return len(E), len(classes), twisted, adv, sorted(hist_p.items())


if __name__ == "__main__":
    main()
