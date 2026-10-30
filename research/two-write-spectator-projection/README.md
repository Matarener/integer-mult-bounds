# Exactly two writes: a support-sensitive projector constraint

**Scoped written lemma and exact finite corroboration; no new kappa.** This
continues Nick Petalas's PR6012 at `3d9d5eb2ae784356497771661960ad0455b137db`,
`research/two-three-cycles-every-dimension/PROOF.md`, Sections 2–4 and Open next
question 3. It derives the two-write analogue with all middle-label terms
retained. It does not exclude the residual ten-call case.

## Model and projection

Use PR6012's formal model `M_2(F2[GL_n(F2)])`, with ordinary matrix product for
address labels and row `k` represented by `e_k^T`. A call is
`D(g,N)=(I+N)+[g]N`, where `g=E_ij=I+e_i e_j^T` writes `i`, reads `j`, and
`N` is a rank-one binary idempotent. Every endpoint coefficient is formal.
Free scalar maps are normalized into the call projectors as in the source;
move scalar maps to one end by conjugating the projectors. Augmentation of
the endpoint `[c]I` forces that terminal scalar map to be `I`. Thus every
normalized subword has augmentation `I`.

Suppose exactly two calls write coordinate `k`. Write the complete word as

`P=A D(g,N) B D(h,M) C`, with `g=E_kj`, `h=E_kl`, `j,l != k`.

The factors in `A,B,C` do not write `k`; all their address support belongs to
`S_k={b:e_k^T b=e_k^T}`. Write `B=sum_b [b] B_b`, and let `pi_k` retain only
labels in `S_k`. Define the **selected and relabelled** middle polynomial

`T_(j,l)(B)=sum_(b in S_k : e_j^T b=e_l^T) [g b h] B_b`.

Then the exact identity is

`pi_k(P)=A ((I+N) B (I+M) + N T_(j,l)(B) M) C`.             (1)

Proof: expand the two calls into their four terms. The term using neither
address label lies in `S_k`. The two terms using exactly one lie outside it:
`S_k g S_k` and `S_k h S_k` are disjoint from the subgroup. In the double
term, put `r=e_j^T b`. Since `b` fixes row `k`,

`e_k^T g b h = e_k^T + r + (1+r_k)e_l^T`.

This equals `e_k^T` precisely when `r=e_l^T`: if `r_k=1`, equality would force
`r=0`, impossible for an invertible `b`; if `r_k=0`, it forces `r=e_l^T`.
Multiplication on either side by support in `S_k` preserves membership in
`S_k`, proving (1). In general `g b h` is not `b`, so merely filtering `B`
without relabelling is incorrect. All scalar matrix orders in (1) matter.

## Equal and complementary projector pairs

Let the endpoint be `[c]I`, as for the two equal coordinate 3-cycles. Put
`S=sum_(e_j^T b=e_l^T) B_b`, the augmentation of the selected middle terms.
The augmentation of `A,B,C` is `I`.

If `c` fixes row `k`, applying augmentation to (1) gives

`I=(I+N)(I+M)+N S M`.                                    (2)

Multiply (2) on the left by `I+N` to get `(I+N)M=0`, and on the right by
`I+M` to get `N(I+M)=0`. Thus `M=NM=N`. Equation (2) then reduces to
`N S N=N`. This is a necessary projector condition for **any restored
coordinate written exactly twice**, without restricting the intermediate reads.
The equality conclusion uses idempotence; it holds beyond rank one as well,
but only the stated rank-one source model is used here.

If `c` moves row `k`, then `pi_k([c]I)=0`, so instead

`0=(I+N)(I+M)+N S M`.                                    (3)

Left multiplication by `I+N` gives `(I+N)(I+M)=0`. This alone does not
force complementary projectors. Each paid call is an involution, so the inverse is a legal reversed word.
Apply the same argument to that inverse:
its two writer projectors occur in order `M,N`; every other label still fixes
row `k`. Since a subgroup is closed under inversion, `c^{-1}` also moves row
`k`. Thus `(I+M)(I+N)=0` as well. In dimension two, the first equality gives
`im(N)=ker(M)` and the second gives `im(M)=ker(N)`. Consequently `MN=NM=0`,
and the first equality now yields **`M=I+N`**. The two projections of the word
and its inverse are both essential. The remaining necessary coefficient
condition from (3) is `N S (I+N)=0`.

## Residual ten-call consequence and limits

PR6012's cited reduction leaves `n=5`, two scalar roles and the ten-call
write profile `(target,spectator)=(6,4)`. Both spectators are therefore written
exactly twice. Their two writer projectors must be equal by (2). Applying the
transpose/reversed-word version gives the same necessary equality for the
two reads of each spectator. Total length ten and PR6012's two-read minimum
for each of the five coordinates force exactly two reads per coordinate.
Each of the three target coordinates is also written and read exactly twice;
its writer pair and reader pair must each be complementary. These equalities
are necessary, not sufficient for a full formal endpoint;
no length-ten or length-eleven exclusion is asserted.

## A live two-write spectator and a necessary relabelling term

Take distinct address coordinates `i,j,k`, put `g=E_kj`, `h=E_ik`,
`t=E_ij`, and fix any one rank-one projector `N`. In the address group,
`g h g h t=e`. Products with the same projector satisfy
`D(a,N)D(b,N)=(I+N)+[ab]N`. Consequently

`D(g,N) D(h,N) D(g,N) D(h,N) D(t,N)=I`.

Coordinate `k` is written twice and read twice, and all inputs are restored.
This refutes an unrestricted claim that every live restored spectator must
be written at least three times. It is not a ten-call two-cycle counterexample.
For the middle `B=D(h,N)`, both support labels pass the selection with `j=l`,
but `g h g != h`. Omitting the relabelling in (1) changes the result. The
identity can be inserted before the known twelve-call endpoint, giving a
seventeen-call positive endpoint with a live two-write spectator.

## Evidence and reproduction

```sh
python3.12 -I -W error -B research/two-write-spectator-projection/verify.py
python3.12 -I -W error -B research/two-write-spectator-projection/independent.py
python3.12 -B scripts/research_package.py --package research/two-write-spectator-projection
```

The standard-library checker compares all 3,600 two-write contexts with a
middle of zero or one calls in the declared three-coordinate domain, checks
all 576 augmented `(N,M,S)` cases and all six commutator fixtures. It finds
6 restored pairs, 12 forward-zero pairs, but only 6 pairs passing both forward
and inverse conditions: exactly the complements. Controls reject missing
middle support selection, missing relabelling and each deleted commutator
call; the extra forward-only pairs refute the insufficient one-sided argument.
`independent.py` uses complete permutations of all address vectors as group
**labels**, retaining a separate scalar coefficient for every permutation.
It does not accept equality merely in the permutation-module representation.
Its separate dense scalar arithmetic checks all 288 GL(3,2) return-filter
cases, 72 five-coordinate contexts with outer subwords and longer middles,
the twelve-call positive endpoint, and all six seventeen-call insertions.
Both engines were prepared in this session; this is implementation diversity,
not independent human review. A separate read-only agent review independently
checked the proof, augmented matrices and group fixtures; no proof-kernel
acceptance is claimed. Finite checks corroborate the written proof. No unrestricted length-ten or
length-eleven search is part of this task.

## Open next questions

Can the full off-subgroup equations combine the equal spectator pairs and
complementary target pairs to exclude the residual `(6,4)` case? First analyze
these constraints on the read/write incidence cycles, then bind a proposed
strengthening to the complete endpoint.
The missing implication is formal cancellation, not a larger sampled word set.

## Credit and scope

Canonical base `721c03822c421b7f7fcbb2598993b947c4d88419`, priority 8, selected
PR6030 kappa `0.003125804`, unchanged. [Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/6075).
Credit Nick Petalas/PR6012 for the single-write projection and reduction,
Mihir Srivastava/PR4939 for the formal model, James Reed/jwr404 #5005/#5379 for
the cited exact small-dimension costs, and JoyboyBrian/#4974 for the prior
single-cycle reduction. The commutator identity is standard, not a new group
identity. This application and checks were prepared by JoyboyBrian with
substantial OpenAI Codex assistance. Apache-2.0. No native tariff, physical
supplier, complete multiplication theorem or new kappa is claimed.
