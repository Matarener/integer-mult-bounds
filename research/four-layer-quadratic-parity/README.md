# Four Hamming layers improve quadratic Walsh-Hadamard agreement

This contribution was produced by Nick Petalas.

Claim type: a scoped written proof with exact finite corroboration. For n=4m
and every integer m>=4, the rational matrix

```
A_m(x,y) = (-1)^m (2(sum_i x_i y_i - m)^2 - 5)/3
```

has exact rank 1+n+binom(n,2). It agrees with the Walsh-Hadamard matrix on
strictly more entries than every quadratic parity interpolant on three
consecutive overlap weights, each of which has that same exact rank.

At n=16, both ranks are 137. Agreement rises from 2633821596 entries to
2713419648, a gain of 79598052 out of 4294967296 entries. The four matching
weights are 2,3,5,6; the best consecutive triple is 3,4,5.

[PROOF.md](PROOF.md) supplies the all-dimension proof, exact factorization,
unique best consecutive triple and positive rational gain formula. This settles
a small instance of the equal-degree polynomial-comparison question in Jacob
Alan Sussman / jacobalansussman's [PR #5817](https://github.com/CrocSwap/integer-mult-bounds/pull/5817),
Open next question 1. That package supplies the question. None of its external
complexity claims is needed or rechecked here. Alman and Williams's
[monomial-rank and consecutive-layer construction](https://arxiv.org/html/1611.05558#S3)
is classical background; the claimed new step is this four-layer construction
and exact comparison. A bounded repository/PR search found no matching result,
which is not proof of historical novelty.

The original `complex-rank-shape-decoder` card is explicitly changed to this
low-rank side question. The first verified improvement ends this investigation.
It does not meet the card's complete supplier gate. No new kappa or selected
frontier change is claimed.

## Reproduce

From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/four-layer-quadratic-parity/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/four-layer-quadratic-parity/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/four-layer-quadratic-parity
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/four-layer-quadratic-parity --check-source-history
```

Any CPython 3.12 executable can replace the local path. Only the standard
library is required. The direct verifier prints a generated JSON receipt with
SHA256 hashes of all six package files, then `PASS_FOUR_LAYER_QUADRATIC_PARITY`.
It writes no files. Explicit exception checks remain active under optimized
Python.

Finite checks cover 125 dimensions n=16,20,...,512; ten exact pair-count cases,
including two dense enumerations; 10920 factorization entries; eight invertible
feature-minor cases; and 18 mutation, input-boundary and scope controls. Counts
at n=16 use exact Hamming-layer multiplicities and an independent sum by row
weight, rather than a dense replay of its roughly four billion entries.

## Limitations

This is an exact agreement comparison between two polynomial families over the
rationals, reals or complexes. It is not optimality among all quadratics or all
rank-137 matrices. At n=40 a rank-one constant matrix already agrees on more
entries than the four-layer construction. No numerical stability, operator-error
bound, per-row correction, physical native implementation, complete recursive
invoice, supplier admission or multiplication theorem is supplied. No Lean or
selected-supplier cold replay was run. Independent human and formal proof-kernel
review are unclaimed.

The verifier's managed-runtime deviation from fixed-allocation Power of Ten
rules is bounded by n<=512, feature dimension at most 37 and dense enumeration
at n<=8. Its only indirect call is the rejection helper with four local check
functions. All loops have finite bounds and all receipts are generated.

## Open next questions

- What is the best exact agreement of a quadratic in the integer overlap,
  including constants? First classify its two rational level sets at 1 and -1,
  then optimize their binomial mass. This could distinguish a local improvement
  from a global low-degree optimum; the present comparison does not do so.
- Does a higher-degree nonconsecutive equality set improve a useful complete
  Walsh-Hadamard construction after row corrections and coefficient costs?
  Begin with one fixed degree and an explicit factorization. A full transform
  bill and legal consumer remain missing.

Structured questions are in [TASK.json](TASK.json). The adjacent #5917 studies
acyclic Boolean-table tensor degree, a different model and question. No
predecessor's certificate is replayed as this deliverable.
