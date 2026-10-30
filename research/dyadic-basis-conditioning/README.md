# Sharp conditioning of two-role dyadic helper completion

This contribution was produced by Nick Petalas. Apache-2.0.

For every dyadic row a and column b of length two with ab=1, the least
Euclidean condition number of a compatible invertible dyadic basis has an
exact formula. Write A=||a||_2^2 and B=||b||_2^2. Choose every integer k with

    2^(2k-1) <= B/A <= 2^(2k+1).

Then q=A*2^k+B*2^(-k), and the optimum is

    cond_2(R) = (q+sqrt(q^2-4))/2,
    R = [b, ±2^k*(-a_2,a_1)^T].

There are at most two optimal exponents. The optimizer finds them by two
exact rational comparisons, without numerical logarithms or eigenvalues.
[PROOF.md](PROOF.md) classifies every compatible completion and proves
global optimality over all integer exponents, including ties.

This is a scoped mathematical proof with exact finite corroboration.
It builds on the dual-pair interface of Ali Romman's merged
[PR #5611](https://github.com/CrocSwap/integer-mult-bounds/pull/5611).
That source constructs legal completions and leaves their growth and
precision costs payable. Its constructor is cited, not audited or replayed.
The new result optimizes endpoint conditioning in the two-role contract.

For its pair a=(3,5), b=(2,-1)^T, the unique optimal determinant magnitude
is 1/2, with R=[[2,-5/2],[-1,3/2]]. The condition number is exactly
(27+sqrt(725))/2. The cited unit-determinant completion has q=39; the new
one has q=27, hence strictly smaller condition number. Real completions
without the dyadic inverse requirement reach sqrt(170)+13, strictly below
the dyadic optimum. Thus arithmetic reversibility can impose a genuine
conditioning penalty. At a=(1,0), b=(1,1)^T, both k=0 and k=1 are optimal.

## Reproduce

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/dyadic-basis-conditioning/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -W error -B research/dyadic-basis-conditioning/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/dyadic-basis-conditioning
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/dyadic-basis-conditioning --check-source-history
```

Other hosts may substitute their CPython 3.12 interpreter. The last command
checks the committed publication. Normal and optimized scientific commands
print `PASS_DYADIC_BASIS_CONDITIONING` and a generated SHA256-bound receipt.
The launcher prints `PASS_REGISTERED_RESEARCH_PACKAGE`. No receipt is
handwritten. The scientific verifier writes no files, imports no predecessor
code, and runs without Git or the network, including from a standalone export.

The finite domain contains all 308 integer dual pairs with each coordinate
in [-5,5], with seven reciprocal dyadic rescalings per pair. These 2,156
presentations are compared against 71,148 directly constructed exponent
matrices. Both determinant signs give 4,760 checked optimal representatives;
224 presentations have tied exponents. A separate second-column oracle
enumerates 56,628 literal matrices over 52 smaller dual pairs, finding 488
compatible grid matrices and the same optima. Four size-boundary pairs and
14 rejection controls cover malformed inputs, odd denominators, size limits,
bad duality, a nonunit determinant, wrong endpoints, exponents and spectral
proxies. All checks remain active under Python optimization. These finite
counts corroborate the proof and do not replace its universal argument.

## Scope and credit

Scientific base is canonical main
19fdb086ea96af9a9f87936a2b888e10af4ed810, priorities revision 8. The current
selected-source binding check passed after sparse inputs were materialized.
The originating card is explicitly changed from a physical helper-inventory
construction to this endpoint precision-interface theorem. It supplies no
new productive targets or favorable complete signed moment. Discovery stopped
at this first result. [TASK.json](TASK.json) records the scope change and
[SOURCES.json](SOURCES.json) pins provenance; there are no live source inputs.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19228475)
preceded substantive work.

Credit Ali Romman #5611 for the completed dual-pair interface, its explicit
nonunit-entry pair and open growth/precision obligation; #5602 and #5599 for
the helper-splitting context and their retained P104/native/controller/compiler
lineage. Nick Petalas #5115 supplies earlier row preparation in a different
single-hub interface. The dyadic-unit classification, Cauchy-Schwarz and
two-by-two singular-value identities are classical. Their application to this
exact constrained optimum and the optimizer are the new contribution.
Predecessor files and credit lines are unchanged. Independent human and
formal proof-kernel review are unclaimed.

Live PR lists and bodies, recent account work, handoffs, local reservations,
merged searches and distinctive all-main README searches were checked.
The cached card search had complete remote pagination but sparse local notes;
direct Git-tree searches supplemented that limit. These are bounded overlap
checks, not proof of novelty or coverage of unpublished work.

The theorem fixes exactly two roles, real dyadic scalar coefficients,
the prescribed row and column, dyadic invertibility and the Euclidean norm.
It also applies to the same scalar basis tensored with an identity on banks.
It does not optimize extra workspace, scalar instructions, intermediate growth
or rounded error. No physical cut, frames, ownership/restoration, source access,
stock, tape, native costs, compiler, supplier admission, complete multiplication
theorem or new kappa is claimed. Lean, Docker and the selected complete cold
replay are unrun. The selected frontier is unchanged.

## Open next questions

- Can one actual helper cut use this optimal basis while keeping intermediate
  scalar growth and the full paid/target invoice favorable? Start with its
  exact two-role pair and emit a chronological scalar schedule. Physical
  compatibility, rounding, restoration and the complete bill are blockers.
- What is the exact optimum with at least three prescribed helper roles?
  Start with one three-coordinate dual pair. The complementary basis is no
  longer a single scalar parameter, so the dyadic determinant restriction
  alone does not solve the problem. No higher-dimensional optimum is claimed.

## Executable bounds

Build the Lever led to the reusable exact optimizer. Prove It Works led to
the separate direct-column oracle and dense Gram/inverse checks. Foundational
Thinking kept the endpoint contract as a row/column pair and separated it
from physical schedules. Power of Ten inspection covers the two new Python
files. There is no recursion, generated code, network, subprocess or callback
dispatch. Functions have at most 28 physical lines. External coordinates are
integers or Fractions with at most 64 numerator bits and 64 denominator bits
after the binary point. The optimizer's loops have at most two entries and
its powers are bounded by 260 in magnitude. The finite oracle uses fixed
domains, including at most 261 candidate exponents, 1,089 second columns
and 308 stored integer pairs. Package hashing reads seven files of at most
256 KiB each.

Python allocation is a rule 3 managed-runtime deviation confined to this
bounded offline command. The fixed coordinate, matrix and enumeration limits
bound live data; no steady service is supplied. A lower-level runtime would
need fixed storage before widening these limits. Warning-strict normal and
optimized execution plus in-memory compilation provide local diagnostics;
no separate Python linter is available on PATH. No shared configuration or
predecessor code is changed.
