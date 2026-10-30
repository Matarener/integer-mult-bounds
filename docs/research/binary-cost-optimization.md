# Optimize a declared binary frame model

Recent [restricted coframe work](../../research/restricted-gaussian-coframe-mincut/README.md)
uses exact cuts to optimize a whole class of binary frame choices. This shared
tool makes the finite optimization step available to other source adapters.
It does not change that construction or establish a new native interface.

```json
{"schema":"submodular-binary-costs/v1",
 "unary":[[0,3],[4,0]],"fixed":[null,null],
 "pairs":[{"i":0,"j":1,"costs":[0,2,1,0]}]}
```

```sh
python3 -B scripts/optimize_binary_costs.py problem.json > certificate.json
python3 -B scripts/optimize_binary_costs.py problem.json --check certificate.json
```

A unary row lists costs at choices 0 and 1. A pair row lists costs at 00, 01,
10 and 11, in that order. All terms are added. Repeated pair terms remain
separate charges. Signed integer costs are allowed. Every pair must satisfy
E00+E11 <= E01+E10. The tool rejects a pair that fails this condition. Fixed
choices are null, 0 or 1; they remain fixed in the returned assignment.

For w=E01+E10-E00-E11, write a pair cost as
E00+(E10-E00)x_i+(E11-E10)x_j+w(1-x_i)x_j. Since w>=0, the last term is the
capacity of a directed cut edge. Unary terms become source or sink edges plus
an exact constant. A fixed-choice edge exceeds the sum of all finite edge
capacities, so it cannot improve a legal optimum by changing a fixed choice.

The producer uses Dinic's algorithm. The separate checker reconstructs the
reduction, checks flow capacities and conservation, and checks equality of the
flow and cut values. The original table cost must equal the cut plus its
constant. This proves global optimality over all declared binary assignments,
including ties. No floating-point calculation enters the certificate.

Limits: 512 choices, 8192 pair terms and integer cost magnitudes at most 10^12.
For rational costs, use a common exact scale. For power-cost intervals, a cut
on rounded values alone is not an optimum proof for the real objective; retain
and bound the rounding error as the source-specific coframe work does.

## Open next questions

Bind each table entry to an authenticated native word and complete target/paid
bill. Check that no omitted term couples three or more choices. Unsupported
cost laws need another solver; they cannot be replaced by submodular tables
without a separate proof. Native, dirty-state and compiler obligations remain.

Credit: classical graph-cut reduction and Dinic flow; Dugongue's general
coframe-cut work and the restricted coframe package, with all retained native
supplier credits. Prepared for Ali Romman with substantial OpenAI Codex
assistance. Apache-2.0. No new kappa or selected-frontier change.
