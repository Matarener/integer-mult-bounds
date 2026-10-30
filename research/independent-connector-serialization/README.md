# Extra independent dirty roots do not lower the connector tariff

Every finite generic connector word on arbitrarily many uncoupled dirty roots
can be serialized onto one dirty root with identical counts of every named
source and output call. [The proof](PROOF.md) first groups commuting calls by
root, then reuses the restored row. Each block cancels its own independent dirt.
This closes the extra-workspace premise without a larger source-word search.

As a corollary, Adam Gall's [PR2063 one-root tariff](../connector-all-tariff-optimum/README.md)
and all sixteen minimal aggregate profiles remain exact for any number of
independent dirty roots, for root-uniform positive complete map prices:

```text
OPT = 2 sum_j b_j + 2 sum_(m=1..31) a_m
      + 2 min({b_0,...,b_4} union {a_m: weight(m) is 3 or 5}).
```

At unit map prices the bill remains 74. The arbitrary finite-word serialization
is the contribution. The one-root tariff, its witnesses and its original census
remain credited predecessor results. There is no supplier or kappa improvement.

## Exact scope

Sources are immutable. Each call is either `z_p += B_j x_j` or
`y_i += A_i z_p`; the same map is available at every port. Maps are arbitrary
compatible F2-linear maps, including singular and noncommuting maps. All roots
and outputs start arbitrary, roots restore, and outputs are observed at
completion. Each child restores disjoint private scratch and agreed heads.
No root transfers, frames, source writes, output reads or hidden buffers occur.

Adding independent rows alone cannot improve this map-call objective. A proposal
must change an actual coupling, observation, map or physical-price hypothesis.
The complete physical bill still needs the caller's admission, preparation,
program/storage, routing, hosting and dispatch terms. Reordering can change
those terms and the available parallelism; no elapsed-time comparison follows.

## Replay and serializer

Python 3.12+, standard library only, from the repository root:

```sh
python3 -I -B scripts/research_package.py --package research/independent-connector-serialization
python3 -I -O -Werror -B research/independent-connector-serialization/verify.py
python3 -I -O -Werror -B research/independent-connector-serialization/independent.py
python3 -I -O -Werror -B research/independent-connector-serialization/serialize.py research/independent-connector-serialization/EXAMPLE.json
```

The last command emits a one-root program to stdout. The JSON schema has exactly
`sources`, `roots`, `targets`, and `events`. Target entries are bit masks;
events are `["B", source_index, root_port]` or `["A", output_index, root_port]`,
with zero-based indices. The CLI checks the full formal dirty endpoint before
and after serialization, preserves every map count and writes no files.
Its bounded API accepts at most eight sources, sixteen roots, 255 outputs,
4,096 events and one MiB of JSON. These are executable resource limits;
the written proof covers all finite sizes.

[RESULT.json](RESULT.json) records the exact agreement of two enumeration
engines on all 87,381 words of length zero through eight in the two-root,
one-source, one-output alphabet. Of these, 8,909 restore both roots and have
a source-only output. Both engines check every accepted serialization and its
complete digest and histogram. The independent engine uses full linear matrices.
The primary engine tracks formal source and dirt symbols.

Thirty-two five-source fixtures include all sixteen credited 74-call witnesses
and interleaved three-root versions with cancelling contributions. Five further
fixtures reach eight sources and sixteen roots. A separate dense interpreter
checks every dirty basis column and literal inverse at widths one, two and
three, with singular and noncommuting maps. It also replays PR2065's credited
coupled word and the unequal-port-price counterexample. Four behavioral groups
exercise invalid dirt cancellation, actual producer mutation, CLI limits,
source/receipt corruption, and optimized read-only replay without Git.
See [VALIDATION.md](VALIDATION.md) for exact counts, diagnostics and limits.
`verify.py --emit` prints a newly computed receipt; default replay never rewrites
committed evidence.

## Sources and attribution

Scientific base is canonical main `6f100d4bb5083f8c35d96fd95a539811c62f245c`,
priority revision 6. [SOURCES.json](SOURCES.json) binds exact main blobs and
SHA256 values. Replay needs no pending PR object or network access. The task
refines `connector-alphabet-change` to an independently checked no-saving result
for extra uncoupled workspace. No new operation or supplier is admitted.

Credit Ross Richardson / PR943 and the PR934 lineage for the universal
connector and dirty-prefix contract; Cinna Davis / PR1770 and PR1811 for
weighted and odd-mask predecessors; Adam Gall / PR2063 for the full one-root
price frontier and witnesses. Gareth Davidson / PR1498, Hanson Sun / PR1615,
and Adam Gall / PR2065 study transfer-coupled incidence-minimal words and are
complementary predecessors. Their results are preserved. New work is Apache-2.0.
Scope and review obligations are recorded in [TASK.json](TASK.json).
The two implementations are author checks, not independent human review.

[Canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/2049#discussioncomment-19009168).
No selected source, frozen archive, predecessor package or shared index changes.

## Open next questions

For a real caller that can improve this bill, identify the exact paid coupling
or nonuniform port contract that prevents serialization. Bind it to legal
source/reader access, dirty restoration and all setup/routing costs before
optimizing more abstract words. PR2065 already supplies a coupled construction;
its missing real caller and complete port/transfer prices remain the relevant
blockers. Do not repeat the independent-root search under unchanged hypotheses.
