# Independent audit of PR6053 at an exact scientific head

Target: apoursh, [PR6053](https://github.com/CrocSwap/integer-mult-bounds/pull/6053),
head **12385ca23315181e3d15eb23a2d9ffec65d9a909**.
Prepared for SHIN09-git with substantial OpenAI Codex assistance. Apache-2.0.

## Why the scope changed

At entry, the complete cached search identified the released questions in
PR6031 and no matching successor. Work began on a coordinate-minor attainment
argument and exact finite corroboration. A second complete live search found
PR6053, opened at 2026-10-28T03:27:51Z during the session. We inspected its exact
proof after finding that overlap. Its theorem is the same dimension law.

The package therefore became a bounded audit of that exact source. No novelty,
priority or independent human review is claimed. The separately developed
coordinate-minor construction is retained as an alternate verification route.
This audit does not claim to re-run the original PR6053 program or its 886-case
inventory. The new verifier imports no PR6053 executable code.

## Claims and separate evidence

| Reviewed claim | Evidence here |
|---|---|
| Every intermediate rank attains the dimension bound | PROOF.md Sections 2–4 give a coordinate-minor deletion construction; it does not require the two-block normal form used by PR6053. |
| rho0 = rank((B-H) A^-1 (A-H)) + rank((A-H) B^-1 (B-H)) + 2 rank H - 2d | Evaluated independently on all 9,389 declared cases and compared to the lifted pairing, T G G' T, and (on finite census domains) the complete subspace oracle. |
| Sector admissibility and least dimension | Every chosen row/column is from the original sector basis. Exhaustive subspace profiles agree on 171,259 pairs. |
| Actual commuting-idempotent witnesses | 32,051 literal P,Q constructions pass an independent raw-matrix checker for idempotence, commutation, A/B/H blocks and Schur rank. |
| Ternary behavior, including odd minima | Complete d=2 F3 input coverage by 8,136 conjugacy representatives, covering all 186,624 raw triples. There are 288 representative cases with rho0=1. |
| Ordered factors and both cost slopes matter | Nine real source mutants are required to fail at the intended scientific checks; ten fixture/formula controls also fail as expected. |

The structured rational/prime-field cases cover Q and F2,F3,F5,F7,F11 at
d=1..4. The d=3 binary family fixes one pivot pair and enumerates all H;
it does not replace PR6053's differently chosen d=3 cases or claim broader
coverage in every respect. Our total subspace-pair count is smaller than
PR6053's because its selected d=3 cases have different subspace inventories.

## Written-argument review

PR6053's six lifted spaces match the credited PR6031 deficiency identities.
The sign choice in the 01 right lift differs from our pure-sector convention
by a nonzero scalar, so it does not change the subspace or pairing rank.

Its two nonzero cross blocks use disjoint sector row/column spaces. Thus their
within-sector reductions can be made independently; the paired-coordinate
and radical selections respect the original block constraints. Our arbitrary
coordinate-minor chain supplies another attainment argument without needing
that special pairing sparsity.

For the closed rho0 formula, the block matrix [[F,H],[0,J]] has rank
d + rank(J A^-1 F) after adding the second block column to the first and
eliminating with A=F+H. Swapping F and J gives the ordered B expression.
Subtracting rank F and rank J yields the pairing ranks. Substitution into
rho0=2d-2nu+r gives the stated closed formula, with no commuting-factor step.

No discrepancy was found in these arguments or the declared exact checks.
This is a review conclusion within the stated field/invertible-pivot/common-
deletion scope, not a machine-checked universal proof. Physical realization
and all supplier costs remain outside the audit.
