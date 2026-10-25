# A sharp B1 call bound for isolated-axis exposure

Exposing `g` isolated source axes onto `g` disjoint isolated target axes,
while fixing every other axis, requires at least `g` completed B1 block
exchanges. The transposition extension attains `g`. This remains true
when intermediate calls move arbitrary spectator axes.

[PROOF.md](PROOF.md) gives the all-size argument. One contiguous equal-block
exchange can create at most four broken adjacencies. Every allowed exposure
has exactly `4g`, including the two sentinel boundaries. Sequential calls
to the existing complete-stream binary wrapper therefore have a sharp
`Theta_q(Vg)` tariff. They cannot provide a fixed sublinear power of `g`,
even with a fixed polylogarithmic factor.

This closes one narrow implementation option for the arbitrary-support
exposure left open by the [actual-width T74 proposal](https://github.com/CrocSwap/integer-mult-bounds/discussions/2612#discussioncomment-19009513).
The hard family meets its exact spacing and width domain. It does not
exclude fused physical routing, a larger-support extension or a changed
consumer/view contract. No supplier, integer exponent or selected-frontier
change follows. The B1 upper implementation remains conditional on its
retained source/refinement premises; the factorization lower bound is
self-contained.

## Replay and evidence

Use standard-library CPython 3.12 from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/isolated-axis-exposure
python3.12 -B scripts/check_research_commit.py --package research/isolated-axis-exposure --check-source-history
```

The registered commands authenticate the two exact source inputs and check
188,948 exchange/inverse comparisons on all permutations through seven
axes. They check all 4,365 supported completions in 30 bounded families,
and constructive upper words totaling 105 calls. An independent pointwise
model enumerates every shorter word for `g=1,2,3`, without importing the
primary checker or its receipt. Adjacent support, larger endpoint support
and a simultaneous non-B1 operation are explicit scope controls.

The primary CLI runs normally and optimized. Six actual optimized CLI
mutations reject changed source bytes, omitted source input, a false cut
constant, an omitted sentinel, a changed result and a missing result.
Acceptance does not use Python assertions. Missing evidence fails without
repair; `--emit-to NEW`
creates a fresh external result exclusively. Exact observed environments
and replay limits are in [EVIDENCE.md](EVIDENCE.md).

The finite checks corroborate the written proof. They do not constitute
independent human or formal proof-kernel acceptance, a production router
execution or a full selected cold replay.

## Open next questions

Can a fully priced exposure use fused scans, a larger-support extension
or a changed view contract and compose its inverse with the actual T74
consumer? Test the explicit sources `iK+2` and targets `iK`. Account for
every moved spectator through the consumer and return. The blocker is
a concrete physical routing and restoration invoice, not another
contiguous-width B1 exponent calculation. No further construction round
is proposed by this package.

## Sources and credit

[SOURCES.json](SOURCES.json) pins canonical main `20ecf289` and the unchanged
PR2899 binary wrapper and proof. Only their completed B1 contract is used;
no predecessor executable or pending Git object is imported. The new
runtime closure is the three package scripts and the Python standard
library. [COMPARISONS.json](COMPARISONS.json) separates public motivation
and overlapping work from mathematical premises.

Jose Manuel supplied the B1 implementation, the actual-width exposure
question and the T74 physical caller. Retain David Arias's C0 proof,
Nick Petalas's ordinary-wrapper work, and their credited native,
geometry/compiler, hosting and numerical lineage. The pending PR3576
rate/factory result is complementary and is not repeated. The cut-count
argument is elementary; no first discovery of a general sorting theorem
is claimed. Nick Petalas. Apache-2.0. Independent human and formal
proof-kernel review are unclaimed.
