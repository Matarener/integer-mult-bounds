# Complete Pareto frontier for the (1,2,4) Boolean fanout

This contribution was produced by Nick Petalas. Apache-2.0.

For lee-phys's [PR #5514](https://github.com/CrocSwap/integer-mult-bounds/pull/5514)
demand `(1,2,4)` over `F2^3`, the aggregate count vectors
`(P_0,P_1,P_2; K_0,K_1,K_2)` of insertions and incoming ADDs have exactly
**31 Pareto-minimal elements**. The 25 vectors exposed by #5514's price
envelope are all of them except **six new unexposed vectors**:

    P = e_i,   K = (2,2,2) + e_i + e_h,   h != i.

So a one-insertion word can split its two extra ADDs between the insertion
row and any other row. It cannot place them in the two non-insertion rows:
`K = (2,2,2) + e_j + e_k` with `i` not in `{j,k}` is impossible. This
answers #5514 Open next question 1, including its suggested first step on
`(3,3,2)` and its permutations.

Claim type: **exact finite certificate** for the one-insertion layer over
`F2^3`, combined with #5514's **written** componentwise multi-insertion
bounds. The six new words are also proved for every commutative unital
Boolean ring with a nonzero pairwise orthogonal demand triple. No new
kappa, physical supplier or selected-frontier change is claimed.

## Contract

Unchanged from #5514: three arbitrary dirty rows, one preserved source,
gates `P_i(beta)` and `E_ij(alpha)` with every nonzero coefficient, any
finite word, and every original dirt column restored. Encode `x0+2x1+4x2`;
the ring identity is `7` and `g = 7`.

## The new words

For insertion row 0 with the extra ADD in row 2, write `l_r` for lambda_r:

    E_02(l1+l2), E_20(l1+l2), E_01(l1), E_10(l1),
    P_0(g),
    E_10(l1), E_20(l1+l2), E_02(l1+l2), E_21(l1).

The suffix moves the source column
`(g,0,0) -> (g,l1,0) -> (g,l1,l1+l2) -> (l0,l1,l1+l2) -> (l0,l1,l2)`.
Its dirt matrix `L` also has the four-gate word
`E_10(l1), E_01(l1), E_20(l1+l2), E_02(l1+l2)`, doubled in row 0. The
prefix is that word reversed, which is `L^-1` because every `E_ij` is an
involution in characteristic two. Incoming counts are `(2,1,1)` before and
`(1,1,2)` after the insertion, so `K = (3,2,3)`. The receipt lists all six
words, one per insertion row `i` and extra row `h != i`.

Every coefficient is a sum of distinct lambdas, hence nonzero. The words
are checked over the universal ring `F2[l0,l1,l2]/(l_r^2-l_r, l_r l_s)`,
which is `F2^4`. Any Boolean ring with a nonzero orthogonal triple receives
a ring map from it, so restoration and the source column transfer.

## Why the frontier is complete

1. **One insertion, at least eight ADDs.** #5514 shows the single insertion
   is `P_i(g)` and that the ADD-only suffix `L` and the prefix `L^-1` each
   need a gate into every row. Here the enumeration independently finds no
   word with at most three gates whose column `i` equals lambda. Hence
   `K >= (2,2,2)` and each side has exactly four gates when `sum K = 8`.
2. **The eight-ADD layer.** The verifier enumerates every word of exactly
   four nonzero gates (42 gates, 202,192 distinct matrices). For each root,
   104 matrices `L` split `g e_i`. Each has one or two destination-count
   vectors among its four-gate words. Pairing a suffix vector with a prefix
   vector of the same `L` gives exactly the five totals
   `(2,2,2)+2e_h` and `(2,2,2)+e_i+e_h`. For root 0 the classes are 56
   matrices doubled only in row 0, 20 only in row 1, 20 only in row 2, and
   4 each doubled in `{0,1}` or `{0,2}`. No matrix is doubled in both
   non-root rows.
3. **Nine or more ADDs are dominated.** The excess `K-(2,2,2)` has total at
   least three. Every such excess has a coordinate at least two or covers
   `e_i+e_h`, so it dominates one of the five eight-ADD excesses.
4. **Two or more insertions.** #5514's case analysis gives componentwise
   lower bounds dominating `D`, `T_i`, `R_(i,j;k)` or `M_(i,j;k)`, and
   attains each. These 16 vectors are cited, not replayed here.
5. The verifier checks that the 31 vectors are pairwise non-dominating.

Each new vector costs `mu_i + 2 sum(c) + c_i + c_h`, the average of
`U_(i,i)` and `U_(i,h)`. It therefore never uniquely minimizes a price,
which is why the 25-term envelope cannot see it.

## Evidence and reproduction

From the worktree root, with the repository CPython 3.12 interpreter:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/fanout-one-insertion-pareto/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/fanout-one-insertion-pareto/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/fanout-one-insertion-pareto
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/fanout-one-insertion-pareto --check-source-history
```

Standard library only; about one second per run. The verifier prints a
JSON receipt with SHA256 hashes of the five package files, then
`PASS_FANOUT_ONE_INSERTION_PARETO`. It writes no files. Coverage: all
ADD-only words with at most four nonzero gates, every root, six new words
on formal columns over `F2^3` and `F2^4` plus their reversed inverses,
24,576 literal width-one inputs, and 17 mutation controls (each deleted
gate and each altered ADD coefficient of one new word is rejected).

## Limits

The exclusion of non-root extra ADDs is a finite certificate over `F2^3`
only; no written proof is given, and larger Boolean rings are open. The
multi-insertion part rests on #5514's written proof, which is cited and
pinned, not re-verified. Directed-edge prices, helpers, restricted
coefficients and non-Boolean rings are outside this result. Independent
human and formal proof-kernel review are unclaimed.

## Open next questions

- Does the non-root exclusion hold over every Boolean ring with a nonzero
  orthogonal triple? Start with the same four-gate enumeration over the
  universal ring `F2^4` (90 gates), or a written invariant for suffix words
  doubled in a non-insertion row.
- What is the frontier with independently priced directed edges (#5514
  Open next question 2)? Start from the directed-edge multisets of the
  four-gate split words found here; destination counts lose parent data.

## Credit

lee-phys's #5514 supplies the question, contract, column lemma, return
lemma, multi-insertion case analysis and the 25 attaining words. That
proof credits #3063, #4916, #5163, #5139, #5259, #5304 and Ali Romman's
#5310; their roles are retained. New work: the exhaustive eight-ADD
one-insertion decision, the six new words, the universal-ring transfer and
the 31-vector frontier.
