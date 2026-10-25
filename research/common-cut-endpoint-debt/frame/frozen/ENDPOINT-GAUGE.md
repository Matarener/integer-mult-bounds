# Scoped endpoint rank for the common-code relay

This is an independent review of the parent/algebra lane's endpoint
calculation. It applies to a specific changed caller: all ports use one
shared orthogonal common 2-plane C=span(p,q); stage s uses an otherwise
disjoint fresh 5-plane F_s; both public banks carry the same extracted
logical code; each local source normalizer pre preserves the computational
and full-native Lagrangians. It does not cover retained noncommon bank
codes, overlapping fresh blocks, different routed products, or the reverse
full-source boundary.

Let P=pre^-1. Because pre is a common-F monomial, P has binary symplectic
form

    P = [ G          0    ] .
        [ G+G^-T    G^-T ]

In the orthogonal decomposition C plus F, set T=F_F (the actual paired
diagonal, up to Pauli), and M=C_p C_q^-1 (binary Fourier on C). Direct
matrix multiplication gives

    B(T P M) = diag(G_CC, (G^-T)_FF).

For any invertible G, complementary nullity gives

    nullity((G^-T)_FF) = nullity(G_CC).

One elementary proof identifies a kernel vector w in F of the lower-right
block of G^-1 with the vector G^-1(0,w), which lies in C and is killed by
G_CC; the inverse map sends a kernel vector v in C to the F component of
G(v,0). Transposing does not change either nullity. Consequently

    rank B(T P M) = h-4+2 rank(G_CC).

The exact normalized local source identity is post S pre=T, where post is
monomial. Hence

    S M = post^-1 T P M,

and its native rank has the same expression. For the actual h7 OPEN
sources, the pinned source operators give

    rank(S_A M)=rank(S_B M)=5,
    rank(S_C M)=3.

Thus the common corner of inverse(pre) has rank 1 at every A/B port and
rank 0 at every C port. These conclusions hold for every source normalizer
in the declared common-F family, not merely the finite winners. The corner
of pre itself is not the relevant corner and can have a different rank.

In a sequence of stages with pairwise disjoint fresh blocks, no later
factor can return amplitude from an earlier factor's fresh block into C.
Therefore

    (G_total)_CC = (G_last)_CC ... (G_first)_CC.

The parent/algebra lane derives, after its literal terminal field exchange,
the isolated Y operator

    F_fresh P_total (C_p C_q^-1),
    P_total=pre_last^-1 ... pre_first^-1,

up to explicitly tracked Pauli factors, which do not affect native rank.
The same block calculation at global arity m gives

    rank(Y) = m-4+2 rank((G_total)_CC).

Thus C ports in this relay remain deficient by four native directions;
A/B ports are deficient by at least two. No choice among the common-F
normalizers, including the zero-query inverse-B winners, removes this
particular terminal deficit. It must be completed with a paid terminal
operator or consumed by a genuinely different caller. The number of Y
banks, their stock and the actual completion histograms belong in the
parent's whole-word bill; this note does not treat a rank per port as a
complete budget.

The finite exact checks in the producing lanes retain the actual Clifford
phases. This argument concerns their binary native rank and cannot decide
the phase or scalar arithmetic of a terminal decoder. Tensoring the same
operator identities over f bit positions multiplies every binary rank by
f, so the deficit is a real native child arity, not a finite-character
artifact. Expanding a one-bit decoder into a fixed number of translations
does not remove that all-size cost.
