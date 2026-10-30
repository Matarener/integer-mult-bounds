"""Independent dense exact engine for nine-axis Clifford operators.

Every operator is a full 512 x 512 matrix of Gaussian integers over a common
power-of-two denominator, held in a complex128 NumPy array (all entries are
integers far below 2^53, so every product and sum is exact).  Nothing here
imports the Clifford compiler, a tableau, or a sparse state column; equality is
equality of all 262,144 entries after normalization.

Conventions (the retained ones of the selected word; see PROOF.md s1):
  basis |x>, x in {0..511}, bit i of x is axis i; a circuit [g1, g2, ...] applies
  g1 first, so its matrix is ... M(g2) M(g1).
  P(G)        |x> -> |G x>,  (G x)_i = parity(G_i & x)   (rows G_i of a binary matrix)
  X(b)        |x> -> |x xor b>
  D(Q, alpha) |x> -> i^q(x) |x>,  q(x) = sum_{i in x} alpha_i + 2 sum_{i<j in x} Q_ij  (mod 4)
  phase(p)    i^p I
  C(q, +1)    ((1+i) I + (1-i) X(q)) / 2 ;  C(q, -1) its inverse ((1-i) I + (1+i) X(q)) / 2
  Gamma_W     the canonical chart of a binary frame W (list of r vectors):
              I for r = 0, F9 = C(e_0) ... C(e_8) for r = 9, otherwise K F_r K^-1 with
              K = D(Q_W) P(G_W), G_W the matrix whose columns are W completed by unit
              vectors, Q_W the binary Gram matrix of the columns of G_W^-1 with its
              diagonal complemented, F_r = C(e_0) ... C(e_{r-1}).
"""
import numpy as np

N = 9
DIM = 1 << N
ADDR = np.arange(DIM)
IPOW = np.array([1, 1j, -1, -1j])
BOUND = 2.0 ** 40          # guard: numerators must stay far below 2^53


def parity(x):
    return x.bit_count() & 1


def mv(rows, x):
    return sum(parity(r & x) << i for i, r in enumerate(rows))


def transpose(rows, n=N):
    return tuple(sum(((rows[j] >> i) & 1) << j for j in range(n)) for i in range(n))


def inverse(rows, n=N):
    a = [r | (1 << (n + i)) for i, r in enumerate(rows)]
    for j in range(n):
        k = next(i for i in range(j, n) if a[i] >> j & 1)
        a[j], a[k] = a[k], a[j]
        for i in range(n):
            if i != j and a[i] >> j & 1:
                a[i] ^= a[j]
    if [r & ((1 << n) - 1) for r in a] != [1 << i for i in range(n)]:
        raise ValueError("singular binary matrix")
    return tuple(r >> n for r in a)


def complete_basis(vectors, n=N):
    """vectors, then unit vectors, keeping each one that is independent of the earlier kept ones."""
    kept, pivots = [], {}
    for v in list(vectors) + [1 << i for i in range(n)]:
        w = v
        while w:
            j = w.bit_length() - 1
            if j not in pivots:
                pivots[j] = w
                kept.append(v)
                break
            w ^= pivots[j]
    if len(kept) != n:
        raise ValueError("frame vectors are dependent")
    return tuple(kept)


class Dense:
    """U = num / 2^d with num a complex128 array of Gaussian integers."""
    __slots__ = ("num", "d")

    def __init__(self, num, d):
        self.num = num
        self.d = d

    @staticmethod
    def identity():
        return Dense(np.eye(DIM, dtype=np.complex128), 0)

    def copy(self):
        return Dense(self.num.copy(), self.d)

    def check(self):
        a = self.num
        if not (np.all(a.real == np.round(a.real)) and np.all(a.imag == np.round(a.imag))):
            raise ValueError("non-integral numerator")
        if np.abs(a.real).max() >= BOUND or np.abs(a.imag).max() >= BOUND:
            raise ValueError("numerator bound exceeded")
        return self

    def normalize(self):
        """Divide out common factors of two; the result is a canonical representative."""
        while self.d > 0:
            h = self.num / 2
            if np.all(h.real == np.round(h.real)) and np.all(h.imag == np.round(h.imag)):
                self.num = h
                self.d -= 1
            else:
                break
        return self.check()

    def equals(self, other):
        a, b = self.copy().normalize(), other.copy().normalize()
        return a.d == b.d and np.array_equal(a.num, b.num)

    def dagger(self):
        return Dense(self.num.conj().T.copy(), self.d)

    def matmul(self, other):
        """self @ other (apply other first)."""
        return Dense(self.num @ other.num, self.d + other.d).check()

    def is_unitary(self):
        prod = self.num @ self.num.conj().T
        return np.array_equal(prod, (4.0 ** self.d) * np.eye(DIM))

    # ---- left application of one primitive (gate applied after the current operator)
    def apply(self, gate):
        tag = gate[0]
        if tag == "P":
            img = np.fromiter((mv(gate[1], x) for x in range(DIM)), dtype=np.int64, count=DIM)
            new = np.empty_like(self.num)
            new[img] = self.num          # row x of the old operator becomes row G x
            self.num = new
        elif tag == "X":
            self.num = self.num[ADDR ^ gate[1]]
        elif tag == "D":
            Q, alpha = gate[1], gate[2]
            q = np.fromiter((qvalue(Q, alpha, x) for x in range(DIM)), dtype=np.int64, count=DIM)
            self.num = self.num * IPOW[q][:, None]
        elif tag == "phase":
            self.num = self.num * IPOW[gate[1] % 4]
        elif tag == "C":
            q, sgn = gate[1], gate[2]
            a, b = (1 + 1j, 1 - 1j) if sgn == 1 else (1 - 1j, 1 + 1j)
            self.num = a * self.num + b * self.num[ADDR ^ q]
            self.d += 1
        else:
            raise ValueError("unknown primitive " + repr(tag))
        return self.check()

    def column_supports(self):
        return np.count_nonzero(self.num, axis=0)

    def support_rank(self):
        """log2 of the common column support size; raises if the columns differ or are not powers of two."""
        s = self.column_supports()
        k = int(s[0])
        if not np.all(s == k) or k & (k - 1):
            raise ValueError("column supports are not a common power of two")
        return k.bit_length() - 1

    def is_monomial(self):
        a = self.copy().normalize()
        if a.d != 0 or not np.all(a.column_supports() == 1):
            return False
        nz = a.num[a.num != 0]
        return bool(np.all(np.isin(nz, IPOW)))


def qvalue(Q, alpha, x):
    v = 0
    for i in range(N):
        if x >> i & 1:
            v += alpha[i] + 2 * parity((Q[i] >> (i + 1)) & (x >> (i + 1)))
    return v % 4


def circuit_matrix(circuit):
    m = Dense.identity()
    for g in circuit:
        m.apply(g)
    return m.normalize()


# ---- circuits in the written conventions
def fourier(r):
    return [("C", 1 << i, 1) for i in range(r)]


def frame_circuit(W):
    r = len(W)
    if r == 0:
        return []
    if r == N:
        return fourier(N)
    cols = complete_basis(W)
    G = transpose(cols)                       # rows of the matrix whose columns are `cols`
    Gi = inverse(G)
    icols = transpose(Gi)                     # columns of G^-1
    Q = tuple((1 << i) ^ sum(parity(icols[i] & icols[j]) << j for j in range(N)) for i in range(N))
    alpha = tuple((Q[i] >> i) & 1 for i in range(N))
    K = [("P", G), ("D", Q, alpha)]
    K_inv = [("D", Q, tuple((-a) % 4 for a in alpha)), ("P", Gi)]
    return K_inv + fourier(r) + K


def monomial_circuit(rec):
    return [("D", tuple(rec["quadratic_rows"]), tuple(rec["linear_Z4"])),
            ("P", tuple(rec["matrix_rows"])), ("X", rec["offset"]), ("phase", rec["phase"])]


def recipe_circuit(rec):
    r = rec["rank"]
    if r == 0:
        if rec["right"] is not None:
            raise ValueError("rank-zero recipe with a right factor")
        return monomial_circuit(rec["left"])
    return monomial_circuit(rec["right"]) + fourier(r) + monomial_circuit(rec["left"])


# ---- small dense tensor-power controls on k active axes (k <= 4)
def small_matrix(circuit, axes):
    """Dense matrix of a nine-axis circuit that only touches `axes`, written on 2^len(axes) states."""
    k = len(axes)
    full = circuit_matrix(circuit)
    idx = [sum(((s >> t) & 1) << axes[t] for t in range(k)) for s in range(1 << k)]
    sub = full.num[np.ix_(idx, idx)]
    # the operator must be the identity on the other axes: check its block structure
    rest = [x for x in range(DIM) if all(not (x >> a & 1) for a in axes)]
    for off in rest:
        blk = full.num[np.ix_([i | off for i in idx], [i | off for i in idx])]
        if not np.array_equal(blk, sub):
            raise ValueError("circuit acts outside the given axes")
    return Dense(sub, full.d)


def kron(a, b):
    return Dense(np.kron(a.num, b.num), a.d + b.d)


def tensor_power(m, f):
    out = m
    for _ in range(f - 1):
        out = kron(out, m)
    return out
