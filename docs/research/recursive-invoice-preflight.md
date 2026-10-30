# Compare the complete recursive invoice before extending a construction

For explicit equal-mass paid concentration or target refinement, use the
[rank-transfer planner and replay checker](recursive-rank-transfers.md).

The same local edit can save scalar instructions while worsening its recursive
bill. Conversely, owning a helper can remove paid work while also surrendering
a productive target. Compare **both** paid jobs and target credits first:

```sh
python3 -B scripts/compare_recursive_invoices.py OLD.json NEW.json
```

For an `inconclusive` result, use the separate
[exact rational-power comparison](recursive-power-comparison.md) at a declared
exponent. It can certify a strict sign or report an interval that still contains
zero. It does not turn a local invoice gain into a complete κ claim.

For a certificate over the whole interval `0<t<1`, use the
[general-rank root-budget tool](recursive-power-variation.md). It combines a
proved root-count bound with exact endpoint roots and rational brackets. It
reports `inconclusive` if roots remain unaccounted for; a grid alone is not a
uniform-order certificate. The common-base Sturm tool remains the complete
polynomial classifier when all uncancelled ranks share one integer base.

This standard-library tool uses integer arithmetic, without a root search or
contribution replay. It reports an exact certificate for every increasing
concave rank tariff with f(0)=0, including r^(1-C), 0<C<1. The method is classical
concave order, already used by mightyOil's
[T16 audit](../../research/t16-moment-order-audit/README.md) and its predecessors.
The shared interface adds signed target accounting; it is not a new theorem.
The concurrent [source-bound pricing oracle #5391](https://github.com/CrocSwap/integer-mult-bounds/pull/5391)
checks compatibility of reviewed physical, invoice, closure and funding receipts.
This comparator is an earlier arithmetic screen, not a replacement for that
evidence join or its trusted policies.

For a source model with submodular binary choices, the
[exact binary-cost optimizer](binary-cost-optimization.md) constructs a global
minimum and checks it with a flow/cut certificate.

## Input and meaning

Both files use this schema, with identical declared accounting contracts:

```json
{
  "schema": "integer-mult-recursive-invoice/v1",
  "contract": {
    "model": "mixed-target-unnormalized-power-v1",
    "rank_semantics": "H_r costs r^(1-C); debit surrendered productive fields",
    "ambient_rank": 145,
    "boundary": "complete unit before the same mixed-target compiler"
  },
  "paid": {"1": 1, "8": 1},
  "targets": {"9": 1}
}
```

For repeated independent components, the
[invoice combiner](recursive-invoice-composition.md) adds both paid and target
histograms and emits a source receipt. Prove that the components compose at the
declared boundary before using that arithmetic as a construction bill.

Ranks are canonical positive integer strings; counts are nonnegative integers.
The contract identifies the common pricing and consumer boundary. A change in
ownership can change targets inside that boundary, but requires its own legal
construction and complete debit. Different rank meanings, normalization rules
or transfer contracts require a separately justified comparison. Matching text
does not prove applicability.

The tool hashes the exact input bytes. It does **not** derive the invoice from
a circuit, detect an omitted target debit, or authenticate an author's source
claim. Keep the source word, extraction command and exact head with the invoice.
The [worked package](../../research/owned-relation-exhaustion/README.md)
independently reconstructs its complete source invoice before comparing it.

## Export the selected P104 bill

For the selected P104 helper-subspace source, use the opt-in exporter:

```sh
python3 -B scripts/export_selected_invoice.py \
  --evidence /tmp/selected-invoice-evidence.json > /tmp/selected-invoice.json
python3 -B scripts/compare_recursive_invoices.py \
  /tmp/selected-invoice.json CANDIDATE.json
```

The exporter first runs the selected source-binding check. It then counts each
local MOVE from its frame dimensions and each productive public helper from its
endpoint frames. It counts LOCAL calls, query calls, whole idle jobs and main
diagonal targets from the physical controller. All component bills and the full
bill must agree with the authenticated local, native and complete caller receipts.
The evidence file records separate components and exact input hashes. The invoice
on standard output uses the comparator schema without extra fields.

This closes the manual transcription gap for the supported selected source.
The candidate still needs its own complete, justified bill. The exporter does
not replay scalar endpoint matrices, native phases or compiler inequalities.
Use the selected record's reproduction command for those checks. Unknown source
formats and controllers fail; a future selection can require another extractor.
The source word, controller, receipts and selected result remain unchanged.

The tests compare the bill with an independent count from the two path lengths.
They remove each physical charge class and each paid or target rank entry, test
source and ownership errors, and corrupt actual source files before running the
CLI. Run them with:

```sh
python3 -B -m unittest discover -s tests -p 'test_research_selected_invoice.py' -v
```

The source P104 word is by Pierre-Loic Doulcet (hexapode). Ali Romman supplied
the complete caller and helper accounting; Cinna Davis supplied the controller.
Jacob Alan Sussman supplied productive recursion. The comparator is by zxv.
The exporter is by Ali Romman with substantial OpenAI Codex assistance.

| Result | What it establishes | Next action |
|---|---|---|
| `uniformly_worse` | Larger paid-minus-target cost for every power 0<t<1. | Stop this raw-moment improvement claim; identify a changed charge or contract before expanding it. |
| `equal` | Identical net raw moment at every rank tariff. | Report scalar/compiler/implementation gains separately. Same invoice can still improve a funded compiler endpoint. |
| `uniformly_better` | Smaller paid-minus-target cost for every power 0<t<1. | Price the complete candidate and prove its source, ownership, phase and caller obligations. |
| `inconclusive` | Concave order does not decide the comparison. | Use a scoped exact power-moment calculation; mixed signs alone establish no crossing or failure. |

For general concave tariffs the order is weak: a linear tariff can give equality.
The strict power conclusion requires a nonzero signed difference. These results
do not imply circuit equivalence, an admitted supplier or a compiler endpoint.

## Recent discriminating examples

* [#5350](https://github.com/CrocSwap/integer-mult-bounds/pull/5350): the filtered
  151-ADD compression preserves the recursive invoice. Its unfiltered variant
  splits one H4 into two H2 jobs, a strict loss for every 0<t<1. Scalar event count
  alone chooses the wrong variant.
* [#5377](https://github.com/CrocSwap/integer-mult-bounds/pull/5377) and
  [#5383](https://github.com/CrocSwap/integer-mult-bounds/pull/5383): removing H1+H8
  and debiting H9 gives a strict gain, 1+8^t-9^t>0. Leaving the H9 target credited
  produces a much larger, unsupported budget.
* [#5387](https://github.com/CrocSwap/integer-mult-bounds/pull/5387) and
  [#5390](https://github.com/CrocSwap/integer-mult-bounds/pull/5390): compiler
  refinements retain the same recursive invoice. #5390 also reports a smaller
  sufficient compiler at a matched exponent. `equal` is therefore not a reason
  to dismiss a compiler or implementation contribution.

Run the source-bound current examples:

```sh
python3 -B scripts/compare_recursive_invoices.py \
  research/owned-relation-exhaustion/examples/source.json \
  research/owned-relation-exhaustion/examples/exchange-128.json
python3 -B scripts/compare_recursive_invoices.py \
  research/owned-relation-exhaustion/examples/source.json \
  research/owned-relation-exhaustion/examples/h4-split.json
```

The second is a declared single-H4 edit to the complete source invoice, illustrating
the unfiltered retiming's algebra; it is not a newly emitted physical supplier.

## Inspect a tariff witness

For a bounded menu of smaller targets and explicit piece fees, use the
[target-partition optimizer](target-partition-optimization.md).

To show exact old and new costs for the strongest positive and negative hinges:

```sh
python3 -B scripts/explain_recursive_invoices.py OLD.json NEW.json
```

Each witness gives a cap `k` and the tariff `min(r,k)`. The report debits target
credits and binds both input files by SHA256. No witness is emitted for zero cost
change. The comparator and its source bytes remain unchanged.

For old paid jobs `{"2":2}` and new paid jobs `{"1":1,"4":1}`, cap 2 gives
costs 4 and 3; cap 4 gives costs 4 and 5. Thus neither invoice wins for every
concave tariff. This does not imply a power crossing: their power-cost difference
is `(2^t-1)^2`, which is positive for every `0<t<1`.

## Certificate and bounds

Use the [exact two-fee region](recursive-fee-region.md) to price route and
restoration patterns together under the concave-order test.

Set d_r=Δpaid_r-Δtargets_r. The report gives K(k)=Σ d_r min(r,k) at every support
breakpoint. Between breakpoints K is linear. If all K are nonnegative, every
increasing concave cost change is nonnegative; reversing the signs gives the
reverse order. The discrete-slope proof is in the script and the worked package.
No equal-rank-mass assumption is required.

Inputs are bounded to 1 MiB, 4,096 keys per histogram, ranks at most 10^9 and counts
at most 10^60. The implementation sweeps sparse support; it does not allocate an
array of ambient width. Duplicate keys, floats, booleans and differing contracts
fail with a diagnostic and exit code 2. Valid comparisons, including inconclusive
ones, exit 0: this is an arithmetic report, not an automatic acceptance gate.

Prepared for zxv with substantial OpenAI Codex assistance. Apache-2.0.

For a difference whose uncancelled ranks are powers of one integer, the
[polynomial comparison](power-polynomial-comparison.md) classifies the power
cost on the whole open interval `0 < t < 1`. It distinguishes strict order,
interior equality and actual crossings without a numerical exponent grid.

For a finite search pool, use the [certified invoice frontier](invoice-search-frontier.md)
to remove dominated bills and retain all incomparable candidates.
