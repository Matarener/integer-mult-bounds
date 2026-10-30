# Exact admissible primes for ordered matrix-shear factors

This scoped proof was produced by Nick Petalas. An integer matrix admits its
rational lower/partial-permutation/lower factorization over the rationals
integral at a prime q exactly when every northeast submatrix preserves rank
modulo q. The exact bad primes divide the product of those blocks' top
determinantal divisors. [PROOF.md](PROOF.md) gives the constructive argument.

Preserving total rank is insufficient even for a matrix of determinant one.
For either [[1,N],[0,0]] or [[1,N],[0,1]], and q dividing positive N, the first
prime-power width with no such ordered factorization is exactly v_q(N)+1.
This allows any partial permutation at each width. For N=3, both pass at
width one modulo 3 and fail at width two modulo 9.

The retained matrix-shear compiler chooses a prime avoiding a finite rational
factor table. This result gives an intrinsic admissibility test before that
table is built. It does not assert that any contributor used a total-rank-only
test, select a different actual compiler prime, or improve kappa. The source
cost theorem and physical primitives are cited rather than re-verified here.
The source's additional odd-prime requirement is retained independently.

## Evidence and reproduction

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/ordered-shear-admissible-primes
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -I -B research/ordered-shear-admissible-primes/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/ordered-shear-admissible-primes --check-source-history --check-modes
```

Other machines may substitute their CPython 3.12 path. Registered normal and
optimized checks use explicit guards that remain enabled under optimization.
The direct checker needs this package and its single declared manuscript input;
it works without Git or network and writes no files. Its stdout is a generated
receipt bound to all six package-file hashes. No receipt is handwritten.

The finite domain contains every two-dimensional matrix with entries -2..2
and every three-dimensional zero/one matrix, each at five primes. Rational
ordered elimination is compared with independently expanded integer minors
and modular ranks. A separate oracle enumerates every lower invertible factor
pair and all seven partial permutations over each of Z/2, Z/3, Z/4, Z/5, Z/8
and Z/9, then checks both families at every residue. Semantic controls reject
total-rank-only and determinant-only criteria, a wrong pattern, corrupted
factors, wrong triangular direction, a bad denominator and a nonunit diagonal.

The run checks 1,137 matrices, 5,685 matrix/prime pairs and 33,386 minors.
The finite-ring oracle enumerates 897,148 factor products and checks 62 family
memberships. Seven false-claim controls and four invalid-input controls pass.
These are finite corroboration counts; the written proof supplies the universal
criterion and width threshold.

## Scope and credit

The original `uniform-transfer-audit` card is changed to this source-relative
arithmetic interface theorem. It addresses one finite prime-avoidance step;
it is not admission of the selected compiler or discharge of an assumption.
No full uniform word, physical tariff, precision/tape improvement, supplier,
new kappa, complete multiplication theorem, human review or formal proof-kernel
acceptance is claimed. The first verified result is packaged without extending
the search to the selected compiler's enormous matrix list.

Credit the retained manuscript and Grigor'ev's classical Bruhat decomposition,
as cited in `04-swap.tex`, for the ordered rational factorization and its cost
use. Credit Rohan Arun / [PR39](https://github.com/CrocSwap/integer-mult-bounds/pull/39)
and James Chang's preceding rank-cut work for the project's northeast-rank
profiling context. Classical rank profiles and determinantal divisors are
background; no global literature-priority claim is made. Existing BIT/native,
ordinary, ROW, routing, analytic and physical compiler contributions retain
their credit. No predecessor files or credit lines are changed. Apache-2.0.

commdata2338 / [PR2160](https://github.com/CrocSwap/integer-mult-bounds/pull/2160)
already supplies a unit-pivot local-ring branch and distinguishes residue-zero
entries from zero at higher width. That context is credited, not rediscovered.
The new result is the intrinsic all-block criterion and the sharp threshold
for the two explicit families, without replaying its selected residual.

Base is canonical main a5bff3bf133e482541c09eba4e773884bdb2b1b7, priority
revision 8, selected kappa .003125804. Exact source/provenance pins are in
[SOURCES.json](SOURCES.json). The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19272193)
records the planned scope. Live PR, Discussion, merged README and targeted
merged-PR searches were bounded overlap checks, not a novelty guarantee.

## Open next questions

Can one actual finite compiler matrix list be assigned its intrinsic bad-prime
set without expanding the huge uniform word? Start with a source-bound
structured representation and its northeast determinantal ideals. The list,
its symbolic minors and complete physical implementation costs remain blockers.

At a bad prime, can a changed physical factorization retain the rank-priced
shear tariff? Start with the N=3, width-two example and explicitly price every
operation outside lower changes and a partial permutation. This obstruction
does not exclude another route or supply one for free.

## Verifier constraints

The verifier has no recursion, subprocesses, imports of predecessor engines,
network access or output files. Matrices have dimension at most three and
integer entries bounded by 512. All production loops have finite bounds from
these domains; finite-ring oracles admit only the six displayed moduli. Each
file read is capped at one MiB and the source inventory at eight rows.
Functions remain below 60 lines. Registered checks enable Python warnings as
errors; mathematical acceptance uses explicit runtime checks.

Power-of-ten rule 3 deviation: CPython allocates managed integers, Fractions
and containers during this bounded offline checker. The input domains above
bound arithmetic depth, live matrix size and the finite-ring reachable set
by 9^4 matrices. Normal and optimized runs exercise the whole fixed domain.
A fixed-allocation implementation would require a separate runtime. No other
dynamic dispatch, generated code or unbounded retry is introduced.
