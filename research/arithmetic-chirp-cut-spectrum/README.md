# Arithmetic chirps require growing transfer dimension

This contribution was produced by Nick Petalas. Apache-2.0.

**Claim type:** scoped written proof with exact finite corroboration.
For the diagonal phase

    U|x> = exp(2 pi i (a x^2+b x)/N)|x>,

the complete cut spectrum is explicit for every integer a,b and every
factorization N=L H, with the declared order x=u+L v. Put

    Q = H/gcd(2a,H),   L=q Q+t,   0<=t<Q.

The squared operator-Schmidt coefficients are H(q+1), t times, and Hq,
Q-t times, omitting zeros. The cut rank is min(L,Q). Their sum is N.

For N=2^n, let nu=v_2(gcd(2a,2^n)). In consecutive binary order,

    rank at cut k = 2^min(k,max(n-k-nu,0))
    minimum exact peak bond = 2^floor((n-nu)/2).

Every nonzero normalized squared coefficient at that cut is 1/rank.
An operator-norm error epsilon<1 therefore requires bond at least
ceil((1-epsilon^2) rank) there. The exact optimal squared relative
Hilbert-Schmidt error at one cut and rank D is max(0,1-D/rank).
The latter optimum is not claimed for operator norm or for simultaneous
approximation at every cut.

For odd a at width 65 the exact peak bond is 2^32. This example is an
encoded formula check, not a materialized 2^65-entry endpoint. In contrast,
the mixed-radix split N=12,L=4,a=1 has the nonflat squared spectrum (6,3,3).
[PROOF.md](PROOF.md) supplies the full argument and attaining cut factorization.

## Why this is a separate contribution

[zxv's PR #5441](https://github.com/CrocSwap/integer-mult-bounds/pull/5441)
supplies the physical transfer contract and earlier half-swap and binary
dot-product examples. Its open directions motivate source-specific cuts
and approximation bounds. The new step here is the arithmetic chirp's
complete spectrum and its coefficient-valuation-dependent binary profile.
Its predecessor executables and claims are cited, not audited or replayed.
The full source lineage remains credited there.

The card scope is explicitly changed to an algebraic side result. No
selected primitive or actual caller is identified with this full endpoint.
The obstruction can screen a proposed bounded-state arithmetic-phase
representation; it does not discharge any selected framework assumption.
The order and demanded endpoint are essential. A short circuit or a changed
representation may still exist. No physical memory, tape-time, query-price,
supplier-admission, complete multiplication theorem or new kappa is claimed.

Character orthogonality, low-rank approximation and the matrix-product/
automata correspondence are classical. The references include Crosswhite
and Bacon, Tyson's related QFT spectrum and Chen and Lindsey's compressible
reindexed QFT. Global literature priority is unclaimed. Independent human
and formal proof-kernel review are unclaimed.

## Reproduction and finite evidence

From the repository root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/arithmetic-chirp-cut-spectrum/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -W error -B research/arithmetic-chirp-cut-spectrum/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/arithmetic-chirp-cut-spectrum
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/arithmetic-chirp-cut-spectrum --check-source-history --check-modes
```

The direct checker prints `PASS_ARITHMETIC_CHIRP_CUT_SPECTRUM` and a generated
JSON receipt bound to the six package files. It uses exact integer
cyclotomic reduction, with no floating-point tolerance or predecessor import.
It checks all N=1..36, all ordered factorizations and a=0..N-1, at b=0,-3:

- 5,870 phase cases and 567,828 upper-triangular Gram entries;
- 15,316 truncation values and 492 nonflat cases;
- 8,256 encoded binary valuation profiles, 715,520 cuts, through width 128;
- three structural controls, 21 signed/shifted phase controls and four
  invalid-input rejections.

Finite cases corroborate the written proof. The large binary checks compare
exact integer formulas and do not materialize their exponential matrices.
The two source notes are pinned as historical provenance; they are not
live executable inputs. Direct replay works without Git or those notes.
No selected cold replay, physical multiplier, Lean or Docker run is included.

## Open next questions

Structured questions with relevance and first steps are in [TASK.json](TASK.json).

1. Bind one actual arithmetic phase request, its permitted order and all
   demanded outputs to this endpoint before using the obstruction in a caller.
2. Determine whether a legal bit permutation lowers the peak bond. Natural
   order and its complete reversal are covered; arbitrary orders are open here.
3. Determine the optimum operator-norm error at fixed cut rank. The theorem
   supplies a necessary bound and a sharp Hilbert-Schmidt result only.

## Verifier resource contract

`verify.py` is a finite, no-argument exact checker. All functions are under
60 lines, loops are bounded by order 36 or width 128, and checks remain active
under optimized Python. No recursion, subprocess, dynamic evaluation or
external module loading is used. Python necessarily allocates integers and
collections during arithmetic. This is a managed-runtime deviation from
Power of Ten rule 3: materialized matrices have at most 36^2 entries and
polynomials at most 37 coefficients; encoded arithmetic uses dimensions
bounded by 2^128. Six fixed local files are read for receipt hashes. If arbitrary
orders or external files are accepted later, their capacities and boundary
validation must be designed before expanding this checker.
