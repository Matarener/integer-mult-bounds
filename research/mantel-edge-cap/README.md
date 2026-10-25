# A triangle-free graph on at most 7 vertices has at most `floor(n^2/4)` edges

**Partial. No new exponent.**

For a degree-`k` vertex, the braid note bounds the incident six-cycles by the
number of edges in a triangle-free graph on those `k` neighbors. That number
is at most `floor(k^2/4)`.

Every graph on `n <= 7` vertices with more than `floor(n^2/4)` edges contains
a triangle. There are 407,058 such graphs, from the one triangle on 3 vertices
through the 401,930 graphs on 7 vertices with at least 13 edges. The balanced
complete bipartite graph meets the count and has no triangle: its parts have
sizes `floor(n/2)` and `ceil(n/2)`, and

```text
floor(n/2) * ceil(n/2) = floor(n^2/4)
```

for every `n` from 1 through `2^20`. The selected kappa is unchanged.

## What was executed

The checker enumerates the graphs above the cap and compares the bipartite
edge count with `floor(n^2/4)`. It does not replay the centre window.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the six-cycle paragraph of PR
3147, head `5cbc48b18cb05327a8dacab3f626412d3bc5e924`.

## Scope and evidence

Original card: `centre-path-sharing`, priority revision 6, refined to this
cap. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/mantel-edge-cap/verify.py
python3.12 -B research/mantel-edge-cap/test_verify.py
python3.12 -B scripts/research_package.py --package research/mantel-edge-cap
```

## Open next questions

Every graph above the cap on at most 7 vertices contains a triangle, and the
bipartite count matches through 2^20. A centre-window replay would leave this
package.

## Credit

dcharb78 invoked this cap for the dependent-triple braid in PR 3147. This
package checks the graphs and the bipartite count.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
