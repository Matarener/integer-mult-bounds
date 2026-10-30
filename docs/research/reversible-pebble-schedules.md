# Construct a scratch schedule with cleanup

A fixed lifetime allocation cannot choose when to erase or recompute a value.
This tool searches those choices for a small dependency DAG. It produces a
minimum-cost reversible pebble schedule, or a finite infeasibility certificate,
under the specified scratch limit.

```json
{"schema":"reversible-pebble-problem/v1","space":3,"targets":[2],"nodes":[
  {"parents":[],"width":1,"compute":1,"erase":1},
  {"parents":[0],"width":1,"compute":2,"erase":1},
  {"parents":[1],"width":1,"compute":3,"erase":1}
]}
```

```sh
python3 -B scripts/plan_reversible_pebbles.py problem.json > certificate.json
python3 -B scripts/plan_reversible_pebbles.py problem.json --check certificate.json
```

Nodes are in topological order. Each move computes an absent node or erases a
present node. All parents must be present for either move. The sum of widths of
present nodes cannot exceed `space`. The initial state is empty. The final
state contains exactly the target nodes; all other nodes must be erased. Costs
for computation and erasure can differ. External inputs remain available and
are outside this scratch count. Each node must denote a fixed pure function of
its listed parents. Bind that premise to source before using the schedule.

The producer uses Dijkstra's algorithm on at most 65536 states. The checker
checks closure of the listed state set under every legal move and checks the
potential inequality d(v) <= d(u)+cost(u,v). Since d(empty)=0, every path to the
final state costs at least its listed potential. A literal schedule replay
attains that bound. If the closed state set excludes the target, no legal
schedule exists. This is a finite certificate for the declared pebble model.

The limit is 16 nodes. Widths and positive costs are integers at most 10^12.
The full state certificate can be large. No time or memory optimum is claimed
outside this model. In particular, a pebble is clean stored data, not an
arbitrary productive dirty helper. Native implementation, physical registers,
input storage, precision, routes and all other charges remain separate.

## Open next questions

Extract a small source DAG whose compute and erase operations satisfy this
model. Compare several scratch budgets, then price the actual generated word.
Do not substitute a pebble schedule for the native or dirty-restoration proof.

Credit: classical reversible pebbling, Dijkstra shortest paths and feasible
potential certificates. Prepared for Ali Romman with substantial OpenAI Codex
assistance. Apache-2.0. No kappa or selected-frontier change.
