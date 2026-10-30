# Conditional κ = 0.00296 through query-thinned productive controllers

The new construction replaces selected full native calls by paid rank-one
query shears, charging the lost productive helpers and removing the same
stage multipliers from the idle and main transforms. It gives an author-checked
conditional multiplication saving **κ = 37/12500 = 0.00296**, approximately
**10.18% above #4416/#4433's 0.00268647**.

The complex controller uses 17 pairs, 19 full native calls and 16 query shears.
The accompanying BIT controller uses 16 pairs, 18 full calls and 15 query
shears, supporting a stronger ordinary BIT saving of 0.0034 after all cover
and atom-conversion charges. The complete outer ledger passes at κ=0.00296.

[PROOF.md](PROOF.md) gives the native query implementation, chronological
product and paid completion, effective compiler ranks, changed BIT stock
parameters, full cost/precision obligations, attribution and conditional scope.
[RESULT.json](RESULT.json) records the exact arithmetic and rejection controls.
The two controller JSON files contain their actual emitted event lists and
constant scalar boundary programs. `controller.py` regenerates them; normal
verification directly replays them without repeating factor discovery.

```sh
python3.12 -B scripts/research_package.py --package research/query-thinned-controllers
python3.12 -O -B research/query-thinned-controllers/verify.py
```

See VALIDATION.md for the exact executed environments and commands.

This retains the reviewed source's all-column native, owned-erasure,
whole-job matching, fixed-tape, precision, analytic, prime and recovery
premises. It claims no unconditional theorem, formal verification, practical
speedup, global controller optimum or selected-frontier change.

## Open next questions

Open next questions are recorded in [TASK.json](TASK.json), with relevance,
first steps and blockers. Prepared for Cinna Davis with substantial OpenAI
Codex assistance; no subagents. Apache-2.0. Source attribution is in PROOF.md
and the unchanged pinned predecessor notices.
