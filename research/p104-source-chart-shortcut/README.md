# Screened P104 source chart after one Gram undo

**Negative result for one shortcut. No new κ.** Selected conditional κ stays
`0.001672660197076918`.

## Scope and evidence

Card `p104-side-correction`, scope **refined**. Discussion #1166 comment
19035513 asks for a caller that fuses the physical source-normalization
factor with a full-output interface and a favorable complete bill. This
package does not build that caller. It certifies the screened shortcut named
in that handoff.

On `F81 = F_2^9 ⊗ F_2^9`, every nonzero row chart `r ⊗ F_2^9` and column chart
`F_2^9 ⊗ c` meet in one line and span 17 dimensions. The codimension in `F81`
is 64, over all `511 × 511` nonzero pairs. Local FULL is not global `F81`.

On the prepared entrance `(T^{-1} x, y)` of the PR #3978 joint cut, deleting
either Gram factor leaves the physical source equal to `F T^{-1} x`. The
rank-one chart tariff on all `N = 104^2 = 10816` data positions equals the
debt-free allowance `C < 10816`. The screened bill equals capacity `81 W =
2965248` before any further nonnegative charge, so the strict gate fails.

The proof is in [PROOF.md](PROOF.md). Exact integers are in [RESULT.json](RESULT.json).
The inherited positive-debt excess 832 is retied only as a transcription check
of the published `#3978` gate. PR #3978's head is not an ancestor of canonical
main, so its files are cited rather than pinned as live inputs.

## Reproduce

Python 3.12, standard library, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/p104-source-chart-shortcut
```

The chart census checks 261121 pairs and takes roughly twenty seconds on
CPython 3.12. One registered command. No native replay, Lean, or Docker run.

## Open next questions

A fused caller that changes the entrance from `(T^{-1} x, y)` to a chart
already cleared, or that changes the debt and progress binding, is not ruled
out by equality at `81 W`. The first step is one literal producer whose source
bank is `F x` at the same cut, with owners, dirty returns and a bill strictly
under `81 W` after every nonnegative charge. It is blocked until that
entrance and those charges are specified. Applying `T` as `N` extra rank-one
children on this shortcut does not open a margin.

## Credit

The prepared cut, the gate `C < N - 208 d`, and the tariff that charges each
`K = T^{-1}` as one rank-one child are PR #3978 (`48e2e44d8785be8204d8c4b719850332f4f9abe0`,
`research/p104-joint-compensation`) by Chris R / Clear1nsight. The fusion
question is discussion comment 19035513, from the same handoff as PRs #3981,
#3979, #3984 and #3978. Retained lineage: Rohan Arun / #1972, Chafik
Boukhalfa / #1991, Adam Gall / #1940, and the E8, native and compiler sources
named there.

New chart census, noncommutative source expansion and debt-free comparison
are by unpaidmoon with Grok assistance in Cursor. Apache-2.0. No human or
proof-assistant review is claimed. The selected frontier is unchanged.
