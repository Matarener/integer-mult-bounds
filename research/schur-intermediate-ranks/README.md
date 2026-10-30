# Nonmaximal Schur-commutator ranks for prescribed pivots

**Scoped all-field proof plus an exact finite certificate. No new kappa.**
Produced by Nick Petalas. Apache-2.0.

Krzysztof Wojt's [PR #5128](https://github.com/CrocSwap/integer-mult-bounds/pull/5128)
(`research/arbitrary-pivot-schur-minimum`) finds the least dimension n at which
commuting idempotents P,Q with prescribed invertible pivots `P11=A`, `Q11=B`
and product block `(PQ)11=H` reach Schur-commutator rank 2d. Its Open next
question 1 asks which smaller ranks are feasible at each ambient dimension. It
names d=2 over F2, rank two, as a first step. This package answers that first
step for every rank and proves an all-field lower bound.

## Result

Write `T00=I-A-B+H`, `T10=A-H`, `T01=B-H`, `T11=H`, `nu_j = nullity T_j`,
`nmax = 3d + rank T00 + Σ nu_j` (#5128), and

```
n0   = rank T00 + rank T10 + rank T01 + rank T11,
rho0 = rank(T M T),   T = diag(T10,T01,T11),
```

where `M = G G'` is built from #5128's ordered factors (PROOF.md §1).

**Theorem (every field, every d; [PROOF.md](PROOF.md)).**

1. No pair exists below n0. At n0 the rank is forced to rho0.
2. For n >= n0, the feasible ranks form the interval `[rho0, rhomax(n)]`.
   Ranks below rho0 never occur.
3. For rho0 <= rho <= 2d,
   ```
   n_min(rho) >= max( n0 + rho - rho0,  nmax - 2(2d - rho) ).
   ```
   Both terms are tight at their endpoints: `n_min(rho0)=n0` and
   `n_min(2d)=nmax`.

The second term comes from a new deficiency identity. If the sector images
lose total dimension a and the sector kernels have total dimension b, then
`rank R = 2d-a` and `rank L = 2d-b` exactly. Hence
`2d-a-b <= rho <= 2d-max(a,b)`.

**Finite certificate (d=2, F2).** Equality holds in (3) for all 576 triples
`A,B in GL_2(F2)`, `H in M_2(F2)`, 288 of them with AB != BA. rho0 is 0 for
408 triples, 2 for 144 and 4 for 24, with 16 distinct profiles. For the first
step named in #5128: rank two is feasible at n exactly when rho0 <= 2 and
`n >= max(n0+2-rho0, nmax-4)`. The 24 triples with T10, T01, T11 all
invertible admit only rank four.

Example: A=B=H=I gives the profile n = 2, 4, 6, 8, 10 for rho = 0..4, so each
extra rank costs two dimensions. Profiles with crossover, such as
n = 3, 4, 5, 7, 9, show both terms of the maximum binding.

## Evidence

[verify.py](verify.py) is standard-library only. For each triple it enumerates
every admissible block pair `im T_j ⊆ I_j`, `N_j ⊆ ker T_j` and computes
the exact least dimension of every rank. On every enumerated pair it checks
`rank R = 2d-a`, `rank L = 2d-b` and the sandwich bound. It checks the closed
law for every triple. For every triple and every feasible rank, it then
assembles a literal pair P,Q at the claimed least n. It recomputes S and Z from
the matrix entries and checks idempotence, commutation, all three prescribed
blocks and the rank: 2,496 literal witnesses. Four seeded controls must be
rejected: a slope-one-only law, the rank-2d formula used at every rank, a
corrupted P entry and a wrong prescribed H.

The exhaustive minimum is complete for d=2 over F2 because of the reduction
in PROOF.md §1. Every pair arises from sector factorizations, and the cost
of each (I,N) choice is its proved minimum.

## Reproduce

From the repository root (any CPython 3.12; about 2 s each):

```sh
python3.12 -I -W error -B research/schur-intermediate-ranks/verify.py
python3.12 -I -O -W error -B research/schur-intermediate-ranks/verify.py
python3.12 -B scripts/research_package.py --package research/schur-intermediate-ranks
python3.12 -B scripts/check_research_commit.py --package research/schur-intermediate-ranks --check-source-history
```

Expected final line: `PASS_SCHUR_INTERMEDIATE_RANKS_D2_F2`, with
`rows_sha256 e18d15092793582f8d16939086fb512563ecbffc95e0f537ddece6873232dc81`.

## Limitations

Equality in the lower bound is proved only for d=2 over F2. For other d and
fields it is a bound, not a formula. The theorem concerns one common deletion
with invertible pivots. It gives no header frequency, physical producer or
consumer, dirty-owner restoration, precision, stock or outer transfer. The
selected frontier and kappa are unchanged. No independent human or formal
proof-kernel review is claimed.

## Open next questions

1. **Does equality hold for every d and field?** Equality would give a closed
   form for the whole trade-off and complete #5128's question 1. First step:
   run the same reduction for d=2 over F3 and d=3 over F2. Then try a two-phase
   chain: single efficient steps up to the crossover, followed by paired I/N
   steps that keep `im R ∩ ker L = 0`. Blocker: over small fields that
   transversality might fail for every admissible choice.
2. **Is there a closed form for rho0?** The ranks of the T_j alone do not fix
   it in the binary data. Begin with the proved sandwich
   `2d - 2Σ nu_j <= rho0 <= 2d - Σ nu_j` and find the extra invariant.

## Credit

Produced by Nick Petalas. Krzysztof Wojt's #5128 supplies the arbitrary-pivot
sector factorization, the ordered maps L, R and the rank-2d minimum, and poses
the question answered here. These are cited, not rechecked. The earlier
Schur-family lineage credited in that package keeps its credit: ssafwann's
#4657/#4671 sector and split-factor method, Nick Petalas's #4597/#4746/#4771/
#4774/#4785, Ryanson Jonathan's #4609/#4617 and lee-phys's #4634. The new work
is the reduction to block subspace pairs, the unit-step interval theorem, the
deficiency identity with its lower bound, and the d=2 binary certificate.
