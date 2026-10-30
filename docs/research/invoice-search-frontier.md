# Reduce a candidate pool before a power search

Run the tool on complete invoices with the same declared boundary:

```sh
python3 -B scripts/prune_recursive_invoices.py candidate-*.json > frontier.json
```

The report lists retained input indices and the SHA-256 of each input file.
For every discarded candidate, it names a retained candidate and gives the
exact hinge values of their signed difference. Keep that receipt with the
source construction. A shared target or an omitted fee can invalidate the
input invoice even when the arithmetic certificate passes.

The tool compares paid costs minus target credits. It keeps all incomparable
candidates. It groups equal signed bills even when their gross paid and target
counts differ; the earliest representative is retained. Equal bills are only
accounting equivalents. They need not have the same physical properties.

For a signed bill d, its coordinate at k is sum d[r] min(r,k). The coordinates
at all support ranks determine its order under every increasing concave tariff
with f(0)=0. Componentwise smaller coordinates therefore give a safe replacement
in this accounting problem. Transitivity ensures that each discarded member
has a retained witness. A nonzero domination is strict for r^t, 0<t<1. Mixed
hinge signs establish neither a crossing nor power optimality.

The separate `verify_frontier` function checks the full partition, each witness
and every retained pair with the existing pairwise comparator. It does not use
the producer's coordinate sweep. Limits are 256 invoices and 8192 distinct union
ranks. Rank magnitudes can reach the existing invoice limit of 10^9; no dense
rank array is used. The tool does not change source files.

## Open next questions

Bind each retained invoice to a legal construction, then use a certified power
comparison on the smaller pool. If storage or native endpoints differ, use a
separate pool or prove the compatibility condition before replacement.

This tool uses classical Pareto reduction and the concave-order method in
`compare_recursive_invoices.py`, with credit to mightyOil's T16 moment-order
audit and its retained predecessors. Prepared for Ali Romman with substantial
OpenAI Codex assistance. Apache-2.0. No new kappa or physical theorem is claimed.
