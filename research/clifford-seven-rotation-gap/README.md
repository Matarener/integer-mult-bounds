# Odd-axis Clifford tensor Gram lower bound above one half

This contribution was produced by Nick Petalas. Apache-2.0.

For every odd n>=3 and every tensor width f>=4n+4, the normalized Gram
matrix of the full projective Gaussian-dyadic Clifford alphabet satisfies

    Gram_f >= (14601049/29130752) I > (1/2) I.

This improves Hiroki KUMAZAKI's #5694 sufficient lower constant
1491359/4161536 by exactly 1/7 in this domain. The new constant is
approximately 0.501224582187. It answers the odd-axis part of the
phase-aware spectral-strengthening question in Javier Vera's #5714.
The exact spectrum and optimal constant remain open.

Claim type: scoped written mathematical proof with exact finite
corroboration. Independent human and formal proof-kernel review are
unclaimed. No new kappa or physical supplier follows.

## New step and dependencies

Seven quarter turns associated with the nonzero vectors of a
three-dimensional isotropic Pauli space commute and multiply to I.
Their regular-action adjacency sum is at least -10 I. Averaging over
Clifford conjugation improves the rank-one displacement contribution
by the factor 5/7. At the odd-axis initial width its coefficient is
positive. The cited higher-rank count bounds the remaining terms.
Entrywise Gram multiplication propagates the result to later widths.

[PROOF.md](PROOF.md) gives the argument, normalization and phase restriction.
We cite Ali Romman's #5526 trace framework and #5694's count and rational
tail certificate. No predecessor executable, group census or caller replay
is run. [SOURCES.json](SOURCES.json) pins their proof bytes and #5714's
explicit open question on canonical main
de5ec2e7a6074068452f45b1a191b5c72832df4a.

This is a side result with scope changed from the `scalar-to-moment`
suggestion. The revision-8 selected baseline binding example passed;
the result concerns quantitative native-alphabet separation rather than
a complete paid/target invoice. The selected record is unchanged.

## Reproduction and evidence

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/clifford-seven-rotation-gap/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/clifford-seven-rotation-gap/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/clifford-seven-rotation-gap
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/clifford-seven-rotation-gap --check-source-history
```

Another CPython 3.12 path can replace the absolute interpreter path.
[VERIFY.json](VERIFY.json) registers both warning-strict normal and
optimized commands, each with a 120-second limit. The verifier writes
only to stdout, including a generated SHA-256-bound receipt. No saved
receipt is maintained by hand.

The exact finite checks enumerate:

* All 135 isotropic three-spaces in F_2^6, with each of the 63 points
  occurring exactly 15 times. This tests the new averaging geometry.
* All 1,080 basis columns of their signed seven-rotation words, using
  literal Pauli actions and integer Gaussian arithmetic.
* All 4,096 fourth-root tuples with product one. Their adjacency
  minimum is -10.
* All 512 characters of the diagonal subgroup Z4^3 x Z2^3. Its adjacency
  spectrum has multiplicities {-10:7, -6:56, -2:203, 2:168, 6:77, 14:1}.
* Forty-nine omitted/replaced-word controls, two semantic controls and
  five out-of-scope controls, plus 120 width fixtures and exact arithmetic
  for the new rational constant.

Finite corroboration does not enumerate the full three-axis Clifford
group or prove the all-dimension quantifiers. Those are supplied by the
written argument using the cited inputs. The receipt authenticates bytes,
not mathematical correctness. The verifier neither imports nor executes
the predecessor checks.

## Limits and implementation constraints

The initial-width improvement requires odd n>=3. For even n, the starting
width is four modulo eight and the rank-one coefficient has the opposite
sign. Arbitrary non-Clifford operators, nonunitary scales, nonlinear leaves
and rounded equalities are outside the theorem. Exact scalar-phase copies
must be combined before using a projective Gram matrix. Source-dependent
physical costs, ownership, restoration and the five selected framework
assumptions are not discharged.

The standalone verifier has fixed finite domains, no recursion, no child
processes and no output files. Functions remain below 60 physical lines.
Explicit exceptions keep every check active under optimized execution.
Managed Python allocation is a deviation from Power of Ten rule 3:
the root scan streams at most 4^7 tuples, stores seven spectral bins,
135 seven-point spaces and at most 512 eight-entry character tuples.
The source inventory has at most eight rows, its JSON at most 64 KiB,
and each authenticated input/package file at most 1 MiB. Runtime/library
allocation is not inspected. A port to a restricted runtime would require fixed arrays
before a constant-allocation claim. Library iteration and dispatch are
bounded by these domains; there are no user-supplied callbacks.
Warning-strict execution and the repository metadata/commit checks provide
the available diagnostics; no external static analyzer is required by the
package.

## Open next questions

1. Can a phase-aware argument improve the even-axis bound at f=4n+4?
   Its rank-one sign is negative, so the new lower adjacency estimate
   does not help there. First seek an upper adjacency or joint-rank
   inequality that accounts for the trivial character. No such bound
   or complete even-axis spectrum is provided.
2. What is the best odd-axis Gram lower constant? The seven-root
   inequality is sharp for that local relation, while the full-group
   averaging and higher-rank triangle bounds can lose information.
   First relate the higher displacement classes to the same local
   subgroups. A full representation argument remains missing.

## Credit and overlap

Credit Javier Vera / #5714 for the explicit open question and row-method
limitation, Hiroki KUMAZAKI / #5694 for the count and tail certificate,
and Ali Romman / #5526 for the trace-lift/projective Gram framework.
Their classical Pauli, symplectic and Clifford sources and retained
native/kernel attribution remain with those pinned packages.
MatShep's #5549/#5594/#5675 one-/two-axis spectra and Ali Romman's #5727
finite-span contraction tools concern distinct results and are not replayed.
No global literature-priority claim is made.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19214984)
states the odd-axis scope. Overlap checking covered live open titles,
recent account contributions, recent handoffs, active Discussions,
relevant PR bodies, distinctive main README/proof terms and merged searches.
The card overlap helper reported incomplete local sparse coverage, which
was supplemented by Git-object searches. These checks do not establish
universal novelty or cover unpublished work.
