# Native endpoints of the diagonal J handoff

The caller lane owns the changed physical stage and local scalar handoff.
This note proves the homogeneous endpoint and tariff statements in
`diagonal_j_factory_gate.py`. It does not serialize a complete all-q
physical caller or remove its public-reader/core coupling.

Let q>=2, n=2q+2, k=2q+1, m=4q+4 and f>=1. Use the actual phase-correct
J from `EVEN-PARITY-SOURCE.json`, N=N0, A=N^-1 J and B_s=P_s A. All
products below retain those actual Gaussian operators. The proposed
nonfinal recurrence is `u'=B_even u`, `v'=-B_odd J v`, and the last
pair has the same homogeneous factors. The transferred base includes
`u1=B3 J*(core row2)=P3 N*(core row2)`. Therefore, up to the stated
overall sign on v, its factories are

    D_even = (P_2q A)...(P_4 A),
    D_u = D_even P3 N,
    D_v = (-1)^(q-2) (P_(2q+1) N)...(P5 N).

Put F=product_(j=1..k) Nj, the exact completed fresh prefix, and E=N F.

On each p or q half, A is an X shear with binary B form
`e0 e1^T+e1 e0^T+e1 e1^T`. Moving all whole-plane permutations to the
right puts D_even into left shear normal form. It is a star with anchor
plane1, leaf sum on the distinct even fresh planes4,6,...,2q, and anchor
diagonal coefficient q-1 modulo2. Each half has rank two, so
`arity(D_even)=4f`, independent of q.

Adding this star to the fresh identity block of F preserves its
invertibility. On the anchor-plus-leaf sector its Schur complement is
`1+(q-1)+(q-1)=1` over F2. Thus F D_even is full on every fresh plane
and still misses common0. The base factor must not be dropped:
`P3 N=N3 P3`. Fresh3 is disjoint from the star and the permutation
path. It cancels that plane's old progress. Consequently

    arity(F D_u)=4q f.

D_v has distinct left native support on the odd fresh planes
5,7,...,2q+1, exactly q-1 planes. Therefore

    arity(F D_v)=(2q+4)f.

The exposed factory endpoint arities sum to `(6q+4)f`. The stipulated
prefix mass is `2(nk+q+2)f`, and n-2 full public outputs have stock
`(n-2)mf`. Their difference is `(6q+8)f`. Even if these factories were
already independent owner endpoints with all coupling removed for free,
that proposed retirement misses the needed stock by 4f. A raw coupled H
cannot instead be credited with these arities without a real owner
interface; a different factorization can have a different gate.

For a separate factory-first completion to the full target E, the exact
unary operators are `E D_u^-1 F^-1` and `E D_v^-1 F^-1`. At the binary
level E commutes with the shear/permutation factors; any actual phase
commutator is a Pauli and does not alter rank. The u correction has the
disjoint star of rank4f, fresh3 of rank2f and common0 of rank2f, giving
8f. The v correction has q-1 odd fresh planes plus common0, giving 2qf.
Their total `2q+8` exceeds the prefix deficit `2q` before additional
core or reader work. This is a gate for that separate completion, not a
lower bound for an unfactored joint correction or a coupled owner.
The changed caller's F J output gauge is distinct. Finite matching-cost
checks do not establish this E-completion bill for F J at every q.

The source definitions tensor bitwise with their displayed global N/J
units, so every binary rank scales exactly by f. Actual Clifford ranks
q=2..8 at f=1,2 additionally check the closed formulas, including the
physical F and E factors. Both the written all-q proof and those finite
checks are local mathematical evidence, not a formal-kernel proof,
all-size supplier, precision bound, tape realization or new exponent.
