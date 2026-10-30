"""Every-word contamination-charge construction (stdlib only).

Registers 0..H-1 are helpers, H..H+Y-1 targets.  A gate (d, s) is r[d] ^= r[s].
A matrix is a list of row bitmasks over the n = H+Y dirty inputs.
`simulate(word, H, Y)` returns a restricted word (no helper<-target gate) and the
explicit charge ledger.  The invariant  M_t = P_phi U(Z_t) N_t  is asserted after
every gate, so no invertibility hypothesis is used anywhere.
"""


def identity(n):
    return [1 << r for r in range(n)]


def apply(word, rows):
    rows = list(rows)
    for d, s in word:
        if d == s:
            raise ValueError("self XOR")
        rows[d] ^= rows[s]
    return rows


def in_parabolic(rows, H, Y):
    tmask = ((1 << Y) - 1) << H
    return all(rows[r] & tmask == 0 for r in range(H))


def frame_rows(N, Z, phi, H, Y):
    """Physical rows of P_phi U(Z) N."""
    n = H + Y
    virt = list(N)
    for b in range(H):
        z = Z[b]
        while z:
            j = (z & -z).bit_length() - 1
            virt[b] ^= N[H + j]
            z &= z - 1
    return [virt[phi[r]] for r in range(n)]


def simulate(word, H, Y, check=True):
    n = H + Y
    phi = list(range(n))            # physical register -> virtual register
    Z = [0] * H                     # Z[b]: Y-bit row of the contamination matrix
    N = identity(n)                 # restricted simulation state
    M = identity(n)                 # actual state
    out = []                        # restricted word (virtual labels = physical labels)
    led = {"length": len(word), "virtual_feedback": 0, "clean_reads": 0,
           "contaminated_reads": 0, "singular_reads": 0, "read_charge": 0,
           "relabel_swaps": 0}

    def emit(d, s):
        if d < H <= s:
            raise AssertionError("emitted a feedback gate")
        out.append((d, s))
        N[d] ^= N[s]

    for d, s in word:
        if d == s or not (0 <= d < n and 0 <= s < n):
            raise ValueError("bad gate")
        M[d] ^= M[s]
        vd, vs = phi[d], phi[s]
        if vd < H and vs >= H:                       # virtual feedback: absorbed, cost 0
            Z[vd] ^= 1 << (vs - H)
            led["virtual_feedback"] += 1
        elif vd < H:                                 # helper mixing
            emit(vd, vs)
            Z[vd] ^= Z[vs]
        elif vs >= H:                                # target mixing y_i ^= y_j
            i, j = vd - H, vs - H
            emit(vd, vs)
            for b in range(H):
                if Z[b] >> i & 1:
                    Z[b] ^= 1 << j
        else:                                        # read y_i ^= h_a
            i, a = vd - H, vs
            Za = Z[a]
            col = [b for b in range(H) if Z[b] >> i & 1]
            if not Za and not col:
                led["clean_reads"] += 1
                emit(vd, a)
            elif not Za >> i & 1:                    # contaminated, nonsingular
                led["contaminated_reads"] += 1
                led["read_charge"] += bin(Za).count("1") + len(col)
                for j in range(Y):
                    if Za >> j & 1:
                        emit(vd, H + j)
                emit(vd, a)
                for b in col:
                    emit(b, a)
                for b in col:
                    Z[b] ^= Za
            else:                                    # singular: target block loses rank
                led["singular_reads"] += 1
                led["read_charge"] += bin(Za).count("1") + len(col) - 2
                for j in range(Y):
                    if j != i and Za >> j & 1:
                        emit(vd, H + j)
                emit(vd, a)
                rest = Za ^ (1 << i)
                for b in col:
                    if b != a:
                        emit(b, a)
                        Z[b] ^= rest
                Z[a] = rest
                for r in range(n):                   # swap roles of virtual a and virtual H+i
                    if phi[r] == a:
                        phi[r] = vd
                    elif phi[r] == vd:
                        phi[r] = a
        if check and frame_rows(N, Z, phi, H, Y) != M:
            raise AssertionError("frame invariant failed")

    led["final_in_P"] = in_parabolic(M, H, Y)
    if led["final_in_P"]:
        # M in P and N in P force U(Z) = I and a block-preserving phi.
        assert all(z == 0 for z in Z), "Z must vanish at a parabolic endpoint"
        assert all((phi[r] < H) == (r < H) for r in range(n)), "phi must preserve blocks"
        # physical r must hold virtual phi[r]: sort with 3-XOR swaps inside each block
        cur = list(range(n))                         # cur[r] = virtual content now in register r
        for r in range(n):
            if cur[r] != phi[r]:
                q = cur.index(phi[r])
                for (x, y) in ((r, q), (q, r), (r, q)):
                    emit(x, y)
                cur[r], cur[q] = cur[q], cur[r]
                led["relabel_swaps"] += 1
        assert N == M, "restricted word must reproduce the endpoint"
    led["charge"] = led["read_charge"] + 3 * led["relabel_swaps"]
    led["restricted_length"] = len(out)
    if led["final_in_P"]:
        assert len(out) == led["length"] - led["virtual_feedback"] + led["charge"]
    return out, led
