# Select compatible invoice edits

Use this tool when several edits compete for the same helper, cut, or original
job. It checks every subset of up to 16 declared edits. It returns a complete
combined invoice and exact bounds on the best possible cost in that finite set.

```sh
python3 -B scripts/select_recursive_edits.py BASELINE.json PLAN.json \
  --exponent 0.9969 --bits 128 > selection.json
```

The plan has schema `integer-mult-recursive-edit-plan/v1`, a `capacities` object,
and an `edits` list. Each edit has a unique `id`, an `invoice`, and a `uses` object.
An invoice is the complete result of that one edit to the baseline. All invoice
contracts must match. Each resource use and capacity is a nonnegative integer.
For example, a capacity of one can prevent two edits from using the same cut.
Include all adapters, restoration, and other fees in each complete edit invoice.

For a selected set, the output is the baseline plus the sum of the edit deltas.
The sum of resource uses must not exceed any capacity. The total removal of each
original paid or target rank must not exceed its original count. An addition by
one edit cannot supply an input to another edit. Such sequential edits need a
single complete candidate invoice instead.

At exponent `1/2`, consider baseline paid ranks `[100,25,25]`. Edit A changes 100
to 9 and uses two helpers. Edits B and C each change one 25 to 1 and use one
helper. With capacity two, A saves 7, but B and C together save 8. The tool selects
B and C. This example is a test; it is not a legal circuit construction.

The search enumerates all subsets. It prunes a branch only when a nonnegative
resource use or gross removal already exceeds a limit. Later choices cannot
repair that failure. The report counts feasible and infeasible subsets, so their
sum must be `2^n`. Exact dyadic power bounds enclose each signed cost delta. The
minimum lower bound and the best feasible upper bound enclose the true optimum.

`certified_optimal` is true only if every competitor has lower bound at least the
chosen upper bound, or has the identical signed histogram. Otherwise the report
retains an explicit precision limit. Increase `--bits` up to 256 if needed.
`possible_optima` is a preview; `possible_optima_count` gives its full size.
Interval overlap does not prove equality. Ties can have different source costs
or obligations that this arithmetic model does not encode.

Limits: 16 edits, 32 resources, 64 uncancelled ranks, and the existing invoice
count limits. Invalid plans exit 2 without a partial result. The report records
exact input hashes. Inputs are not changed.

This proves an optimum only over the supplied independent edits and declared
capacities. It does not prove physical independence, target ownership, a source
map, or a new κ. Incomplete capacities can admit an illegal combination. Review
those declarations before using the combined bill in a complete caller.

## Open next questions

Derive resource exclusions from a checked source word. Compare the best combined
bill with the complete selected caller. Use that result to choose which source
construction merits a full replay.

Credits: existing signed-invoice and exact-power tools, mightyOil's T16 audit,
and their retained predecessors. Prepared for Ali Romman with OpenAI Codex
assistance. Apache-2.0.
