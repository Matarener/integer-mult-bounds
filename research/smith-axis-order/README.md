# Exact optimal ordering of heterogeneous Smith axes

This contribution was produced by Nick Petalas. New material is Apache-2.0.

**Scoped proof with finite corroboration; no new kappa.** For a tensor of
integral factors `C_a = [[i,1],[1,(1+i)^a-i]]`, arbitrary Gaussian-integer
inputs, and every raw residue precision P>=0, the minimum complete two-pass
addition-precision mass is attained by descending valuation gaps in the
triangular gather and ascending gaps in delivery. Every optimal order is
classified by sorting the clipped gaps `min(a,P)` in those directions.

The first strict example has gaps (1,4) and P=3: the same four-coordinate
tensor costs **18 instead of 22** residue-digit ADD units. Both words have
eight nominal ADD positions. This is an exact arithmetic-work comparison,
not a measured runtime or an admitted supplier.

[PROOF.md](PROOF.md) gives the all-size modular word, full two-pass formula,
adjacent-exchange identity, equality cases and proof. [circuit.py](circuit.py)
implements the new heterogeneous circuit and ordering; [verify.py](verify.py)
uses independent coordinate-pair accounting, dense tensor multiplication and
Gaussian parity-lattice congruence checks. It imports no predecessor code.

## Relation to the source and current priorities

Credit Dugongue / David Ganz's [PR #5815](https://github.com/CrocSwap/integer-mult-bounds/pull/5815),
exact head `f0fcda576df410dc15cd5b8183d4f74d284eba2b`, for the integral Gaussian
Smith circuit, propagated moduli, complete two-pass accounting, and the
parameter-efficiency continuation. In particular, consumer-construction.md
C2–C8 supplies the starting word. Tensor factorization, valuation arithmetic
and adjacent exchanges are classical; no literature-wide priority is claimed.

The new step changes identical Gaussian gaps a=2 to **unequal supplied
gaps** and optimizes the entire order class, including delivery. Identical
Gaussian gaps tie, so this adds no ordering gain to #5815's existing word.
No earlier implementation or mathematical result was audited or replayed.

This is a declared side result from the formal-interface-lemma card, rather
than a formal-kernel or selected-caller proof. It can guide a heterogeneous
ordinary tensor backend once such a backend's complete physical bill is
supplied. The selected .00310045 result and five assumptions retain their
status. Main was refreshed at `de5ec2e7a6074068452f45b1a191b5c72832df4a`,
priority revision 8. The source limitations and live overlap searches are in
[TASK.json](TASK.json) and [SOURCES.json](SOURCES.json).

## Reproduce

From the worktree root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/smith-axis-order/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/smith-axis-order
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/smith-axis-order --check-source-history
```

Any CPython 3.12 path may replace the shown interpreter. The direct verifier
ends `PASS_SMITH_AXIS_ORDER`; registered verification also runs optimized
Python. To save a generated, package-hash-bound receipt, pass
`--receipt /path/outside-the-checkout/receipt.json` to the direct verifier.
Default execution writes no files. Counts are printed from actual enumeration.

## Local evidence

- All 153,405 physical-axis orders across 2,259 profile/precision cases pass;
  all 593,730 adjacent-exchange identities pass. Profiles are nondecreasing
  multisets of 1–5 gaps in 0–4, precisions 0–8, with every physical-axis
  permutation including repeated-gap permutations.
- 18,648 basis endpoints and 4,320 arbitrary-input endpoints agree with a
  direct dense tensor oracle: all ordered profiles in 0–2 through four axes,
  precisions 0–5, and the optimal/opposite order pairings.
- 357 complete finite-ring input cases cover gaps 0,1,2,4 in one axis and
  (1,4) in two axes, at precisions 0–2. Thirteen malformed inputs reject;
  six semantic controls cover strictness, clipped ties, corrupted output,
  early truncation and omitted delivery.

The counts are finite corroboration of the separate written proof. These are
not independent human review or formal proof-kernel results.

## Limits and engineering inspection

The executable accepts 1–8 axes, gaps and precision in 0–64, and Gaussian
input components of height at most 10^6. The proof covers all finite n and
nonnegative integer gaps and precisions. Finite tests cover smaller ranges;
they do not establish the universal theorem by themselves.

The tariff is the sum of operand precision for all ADDs in both declared
triangular passes. Phase, scale, truncation, owned storage, cleanup, access,
physical layout and full compiler costs remain separate. Axis scheduling
does not permute coordinates in this indexed circuit, but a physical tape
host still needs its access bill. Owned truncation is permitted; reversible
truncation is a different contract. No Lean, Docker, supplier cold replay or
complete rounded multiplier was run. Independent human and formal
proof-kernel review are unclaimed.

All loops have finite bounds from at most eight axes and 256 coordinates;
verification domains are fixed. There is no recursion or network dependency.
Python allocation and arbitrary-precision integers are explicit managed-runtime
deviations from fixed allocation: live arrays are bounded by 256 coordinates,
and tensor valuation exponents by 512. The verifier's largest dense matrix
has 256 Gaussian entries. Local module loading and the sorting key are bounded
dispatch deviations. Relevant diagnostics, ordinary and optimized replays,
boundary rejections and committed-byte checks are recorded in the PR.

## Open next questions

1. **Unequal per-axis ADD prices.** Which order minimizes the bill when axes
   have different physical prices? It matters when routing or coefficient
   work varies by axis. Start with the two-axis exchange formula, now weighted
   by those prices, and look for context-dependent comparisons. A universal
   sorting rule is unproved.
2. **One actual heterogeneous backend.** Does an existing caller produce
   unequal Smith gaps whose complete physical bill benefits from this order?
   Start with one explicitly supplied tensor factorization and source-bound
   input/output grids. Actual routing, scales, truncation, cleanup and consumer
   costs block a supplier or kappa conclusion.
