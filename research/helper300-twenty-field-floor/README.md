# Exact 38-H1 floor for the twenty-field backward helper block

The retained backward window **[9044,9137)** already has the minimum paid
invoice **38 H1** in the model below. Arbitrary rational ADD/SCALE
refactorizations cannot merge any of its climbs into a larger-rank job.
This is a source-bound, computer-assisted local obstruction; **no new κ**
or whole-provider impossibility is claimed.

This answers the twenty-field follow-up left open by
[PR5471](https://github.com/CrocSwap/integer-mult-bounds/pull/5471), whose
eight-field result is at `77d29520c4f90a65787873d6becc205796630c23`.
The larger boundary changes the exit frames and introduces two more
zero-frame helpers, so the earlier two-carrier argument does not transfer.
The new proof uses directed reachability and multicolumn rank cuts.

## Contract and accounting

The fixed-point dependency closure of roles `{19,300,301}` in the interval is
`[18,19,39,40,288,289,290,291,292,293,294,295,296,297,298,299,300,301,302,303]`.
The twenty entering values are arbitrary and independent. Helpers 300–303
enter at frame zero, not with value zero. The prefix is invertible within
the inherited normalized/native chart interpretation.

Allowed replacements use those same twenty fields, arbitrary rational
coframed ADDs and nonzero SCALEs, and strictly increasing subspace climbs,
with exactly the original entry/exit values and frames. There are no new
warps, auxiliary fields, descents, chart-changing exchanges, COPY/CLEAR,
cross-column conversions or changed boundaries. A basis notation change
at a station does not create a transport edge. The eight disjoint events
in the 93-event interval remain unchanged.

| Quantity | Exact value |
|---|---|
| Selected events | 85: 38 climbs, 43 ADD, 4 SCALE |
| Entry / exit frame-rank sum | 16 / 54 |
| Retained and proved minimum invoice | 38 H1 |
| Ideal endpoint invoice, **infeasible** | 3 H1 + 16 H2 + H3 |
| Product of all monotone path counts | 154,618,822,656 |
| Distinct paid histograms before constraints | 35 |
| Assignments after reachability propagation | 448 |
| Further reachability / rank-cut rejections | 315 / 132 |
| Surviving frame-path assignments | 1, exactly the retained paths |

The endpoint relaxation would save `38 - (3 + 16*2^q + 3^q)` for every
`0 < q < 1`, but has no realization in this contract. Of all assignments,
153,714,841,515 contain a rank-two or rank-three climb and would strictly
improve that moment; all are excluded. The other 903,981,141 have the same
38-H1 invoice, and all but the retained trajectory assignment are excluded.
This does not imply uniqueness of the scalar program.

Productive target credits are unchanged. Same-boundary equality would give
zero external restoration/consumer charge and preserve later cache relations
by composition. No candidate is supplied. Any changed boundary, auxiliary
carrier or native map needs its own complete invoice. Selected κ remains
`0.003027288235` at the pinned base.

## Evidence and reproduction

[PROOF.md](PROOF.md) gives the necessary-condition lemmas and their finite
application. Every legal factorization induces an enumerated monotone path
per field. The screen allows free mixing at shared subspaces and ignores
chronology, relaxing the program. A path assignment must transport every
nonzero input coefficient and enough independent information across every
cut. Rejection in this relaxation excludes a legal realization. Passing
alone would not establish one; here the sole survivor is realized by the source.

`verify.py` extracts the exact rational transfer and enumerates all paths
through subspaces of dimension at most three. Ordered domain eliminations
and all 447 remaining rejection witnesses are in [RESULT.json](RESULT.json).
The separately authored `check_window.py` reconstructs the transfer through
row arithmetic, an independent macro formula and basis-vector runs, checks
determinant one and a two-sided inverse, without importing `verify.py`. A third separately authored checker,
`check_certificate.py`, validates all domain removals and all remaining
witnesses by deleting the listed cut edges and checking disconnection,
without trusting the search or max-flow implementation. Meaningful failure
controls run with assertions disabled as well.

From the repository root, using Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/helper300-twenty-field-floor
```

All six registered runs pass on CPython 3.12.14 (macOS arm64), covering
all three checkers normally and under `-O`. Explicit
certificate regeneration is:

```sh
python3.12 -I -B research/helper300-twenty-field-floor/verify.py --write-result
```

All live inputs and historical provenance are pinned in `SOURCES.json`;
`VERIFY.json` declares live inputs for CI invalidation. No pending-PR Git
object, solver, network request or predecessor package is needed. Native
chart semantics are inherited, not reproved. These checks are not independent
human review, formal-kernel acceptance, a fresh physical/phase replay or a
full multiplication-theorem audit.

## Expansion decision

Before this experiment, the changed interface, source pins, cost obligations
and twenty-field cap were recorded. The alternative of paying an extra H1
for auxiliary transport costs more than one H1+H1 to H2 merge saves. The
endpoint relaxation passed the arithmetic screen but was not accepted as a
construction. The exact local floor closes this session.

## Open next questions

Two consecutive fixed-boundary tests have produced no gain. Do not continue
by merely enlarging this interval again. A justified next experiment must
change and price a premise of the information-transport model:

- **Can a native map or auxiliary transport provide several independent
  channels at a positive net gain?** Write one explicit producer/consumer
  boundary and its complete signed invoice, including restoration and
  productive-target debits, before synthesis. The blocker is the missing
  legal, fully charged transport operation; one extra H1 does not pay for
  one merge.
- **Can a different bottleneck expose larger-rank delivery?** Refresh family
  status and inspect open handoffs for an identified supplier obligation.
  Start from its source-bound budget; neither this floor nor a favorable
  relaxation justifies a larger census.

The original card and structured questions are in `TASK.json`. Coordination
is in [Discussion5470](https://github.com/CrocSwap/integer-mult-bounds/discussions/5470).

## Sources and attribution

Scientific inputs are the selected PR5413 backward provider and its canonical
source at base `32890bc5de034ab8fc93ac88ead7279a6a416d04`.
[PR5465 R13](https://github.com/GamingPuzzled/integer-mult-bounds/blob/b123ff44a211b9fc96b9f8fd1538e9965a95b34e/research/frontier-word-reorder-ceilings/r13-reorder/README.md)
motivated changed-ADD refactorization beyond its fixed-word reorder scope.
PR5465 and PR5471 are motivation/attribution references, not replay inputs.

Credit Cao Yifan (#4610), Dillon Amburgey (#5402), Ali Romman's cached-centre
relations, Chris R/Clear1nsight (#5413), GamingPuzzled (#5465), tomdif's
historical #1286 basis-change screen, and the retained native/compiler
lineage. Directed reachability and cut-rank bounds are standard linear
information-flow arguments; this contribution is their exact source-bound
application and replayable certificate.

Prepared by **apoursh** with substantial OpenAI Codex assistance from a
coordinator, synthesis worker, mathematical auditor and separately authored
source/cut checker. Worker separation is not independent human review.
Apache-2.0.
