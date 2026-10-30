# Exact Schur rank–dimension law over every field

**Scoped algebraic theorem with finite corroboration; no new κ.** This resolves
both open questions in Nick Petalas's [PR #6031](https://github.com/CrocSwap/integer-mult-bounds/pull/6031):
the minimum-dimension law holds for every field and every positive block size,
and the forced minimum rank has a formula using only d-by-d matrix products.
The [proof](PROOF.md) supplies the universal claim; finite computations do not.

For prescribed A,B in GL_d(K), H in M_d(K), put F=A-H, J=B-H and
T00=I-A-B+H. Among commuting idempotents P,Q with leading blocks A,B and
(PQ)11=H, and Schur complements S,Z, let rho=rank(SZ-ZS). Then

```
n0   = rank T00 + rank F + rank J + rank H,
nmax = 3d + rank T00 + nullity F + nullity J + nullity H,
rho0 = rank(J A^-1 F) + rank(F B^-1 J) + 2 rank H - 2d,
n_min(rho) = max(n0 + rho - rho0, nmax - 2(2d-rho)).
```

Every integer rho in [rho0,2d] occurs, and it occurs at ambient dimension n
exactly when n >= n_min(rho). No other rank occurs. Here nmax names the least
dimension attaining rank 2d, not a maximum ambient dimension. The argument
preserves sector constraints: the deficiency pairing has two independent
cross-sector blocks, each admitting a rank core and radicals over any field.
Selecting matched coordinates and radical coordinates attains the lower bound.

PR #6031 established the lower bound and certified equality only at d=2 over
F2. The new proof removes both restrictions. It also explains the missing
invariant: the two cross-sector pairing ranks. They need not agree. For
A=diag(1,2), B=[[1,1],[0,1]], H=I over F3, rho0=1 and the minimum dimensions
at ranks 1,2,3,4 are 5,6,7,9. Thus binary d=2 evenness does not generalize.

## Reproduction and evidence

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -W error -B research/schur-ranks-all-fields/verify.py
python3.12 -I -O -W error -B research/schur-ranks-all-fields/verify.py
python3.12 -B scripts/research_package.py --package research/schur-ranks-all-fields
python3.12 -B scripts/check_research_commit.py --package research/schur-ranks-all-fields --check-source-history
```

The verifier independently enumerates admissible sector subspaces and computes
their direct G G' image/quotient ranks, rather than deriving the oracle's minima
from the new pairing formula. The oracle and formula checks share the exact
prime-field arithmetic module; independence is at the algorithmic level.
It compares both formulas, constructs literal
commuting idempotent witnesses, and recomputes their Schur complements. Its
printed receipt records exact finite coverage, controls and a result digest.
The code supports only its declared bounded prime-field test domains; the proof
also covers extension fields and infinite fields. No predecessor executable is
imported and no network or Git is needed by the standalone verifier.

Finite coverage: **886 triples, 303,878 admissible subspace pairs and 3,516
literal witnesses**. Exhaustive domains are d=1 over F2/F3/F5 (2/12/80
triples) and all 576 d=2 binary triples. The remaining domains are fixed
deterministic samples: 192 d=2 ternary triples and 24 d=3 binary triples,
including high-nullity and odd-rank cases. Eight controls reject omitted or
equated cross blocks, forced evenness, an incorrect minimum, a corrupted
witness, a wrong product block, a slope-one-only law and reordered products.
Gaussian-binomial counts check the complete subspace inventories. The verifier
checks the expected coverage and digest, including the predecessor's 576-triple /
2,496-witness binary census. Expected rows SHA256:
`c38f9ced06db3ecf1bc4c7f8802df7f1b3228f3435946700e7340b115d3156db`.
Each direct replay takes about 4.5 seconds on CPython 3.12.14, macOS arm64.
Timing is descriptive, not a performance claim.
Independent subagent derivations checked the proof and the odd-rank fixture;
this is AI-assisted review, not independent human or proof-kernel acceptance.

## Scope, sources and contribution process

The base is canonical main `721c03822c421b7f7fcbb2598993b947c4d88419`, priority
revision 8, selected conditional κ=0.003125804. [TASK.json](TASK.json) retains
the original `formal-interface-lemma` card with an explicit changed scope:
a released algebraic side question, not formalization or discharge of any of
the five selected-record assumptions. [SOURCES.json](SOURCES.json) binds exact
predecessor bytes as provenance. [VERIFY.json](VERIFY.json) registers bounded
normal and optimized checks with no external live inputs.

Family-expansion decision:

1. Exact sources are #6031 at `acc000f4edfa0b0c4a90b505c6e02a4c3572f74c`
   and Krzysztof Wojt's #5128 at `2839d35e58b3285a1992a3ecbae2809ebef7661b`.
   Both are merged archives; that status is not scientific acceptance.
2. Boundary: one common block deletion, invertible prescribed pivots, arbitrary
   product block. Neither a physical header nor an implemented supplier follows.
3. The complete algebraic cost here is ambient dimension. Physical header
   production/consumption, restoration, precision, stock, compiler and outer
   costs remain unpriced, not free. There is no signed invoice or κ comparison.
4. The result settles the predecessor's open attainment question and decides
   which rank/dimension requests are algebraically feasible before pricing.
5. Immediate pencil follow-ups to our #5672 were already covered by #5683,
   #5689, #5692 and #5712. The active P104 correction line has distinct physical
   obligations. This released question offered a bounded proof with a clear
   stop rule; no further construction round is justified without a caller.

The live #1166 handoff `discussioncomment-19230733` explicitly released #6031's
scope. Targeted all-state searches for Schur ranks and #6031 found no subsequent
extension at intake; recent board claims were inspected. Coverage is targeted,
not a census of arbitrary historical diffs or unpublished work. The [canonical progress update](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19232628)
records the preliminary local result and publication plan. Browser trouble
delayed the post; it is not described as an advance claim.

## Open next questions

Can an actual decoder/header caller use a point on this sharp frontier with a
favorable complete physical bill? First specify its exact A,B,H, desired rank,
allowed sector dimensions, and charged production/consumption/restoration
operations, then evaluate the theorem at that boundary. The missing caller and
cost contract are blockers; an algebraic minimum alone is not a saving.
The corresponding structured question is in [TASK.json](TASK.json).

## Credit

New proof and verifier prepared by **apoursh**, with substantial OpenAI Codex
assistance in derivation, implementation, independent subagent checking and
verification. Apache-2.0. Nick Petalas #6031 supplies the open questions,
sector-subspace cost reduction, lower bounds and binary census; Krzysztof Wojt
#5128 supplies the arbitrary-pivot maximal-rank theorem and realization. The
literal witness construction follows those credited predecessors. The ordered
Schur factorization is Nick Petalas #4597; sector/split methods retain ssafwann
#4657/#4671 and Nick Petalas #4746/#4771/#4774/#4785 attribution. Classical
bilinear rank normal form is used without a historical-priority claim.
