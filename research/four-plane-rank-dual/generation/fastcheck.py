
def build_table():
    """bound(S, T, X, Z) for every zero mask Z (12 off-diagonal pairs), as a flat bytearray"""
    tab = bytearray(4096 * 15 * 15 * 15)
    for S in UNIONS:
        for T in UNIONS:
            for X in UNIONS:
                rows = [P for P in SINGLES if P & S & X]
                cols = [Q2 for Q2 in SINGLES if Q2 & T & X]
                if not rows or not cols:
                    continue
                rel = [i for i, (P, Q2) in enumerate(OFF) if P in rows and Q2 in cols]
                base = ((S - 1) * 15 + T - 1) * 15 + X - 1
                for m in range(4096):
                    Z = {OFF[i] for i in rel if m >> i & 1}
                    br = {frozenset(Q2 for Q2 in cols if (P, Q2) not in Z) for P in rows} - {frozenset()}
                    bc = {frozenset(P for P in rows if (P, Q2) not in Z) for Q2 in cols} - {frozenset()}
                    tab[m * 3375 + base] = min(len(br), len(bc))
    return tab


def cert_ok(tt, cert, tab):
    """exact: integer-scaled weights; tt is the 225 tariffs in KEYS order"""
    den = 1
    for _, _, w in cert:
        den = den * w.denominator // __import__("math").gcd(den, w.denominator)
    iw = [(m * 3375, X - 1, int(w * den)) for m, X, w in cert]
    for k, (S, T) in enumerate(KEYS):
        base = ((S - 1) * 15 + T - 1) * 15
        if sum(w * tab[m + base + x] for m, x, w in iw) > tt[k] * den:
            return False
    return True
