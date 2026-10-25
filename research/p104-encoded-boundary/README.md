# P104 row/column encoded-boundary audit

The natural row-fiber encoding and reversed column-fiber encoding do not match
at fixed physical slots, even on the constant-address sector where all positive
C_U charts act as identity. A two-unit pivot input creates 48 extra signed unit
Y fields under the row encoding and none under the column encoding.

This adds the missing cross-axis condition to [PR3954](https://github.com/CrocSwap/integer-mult-bounds/pull/3954)'s
common-completed-C commutation control. The exact replacement is
`K = S Pi_c L_c S L_r^-1 Pi_r`; all dirty helper values are retained. A direct
common-chart factor word is counted explicitly, with physical transport,
ownership, helper completion and precision left as unknown obligations.
The unchanged favorable whole-scaffold gate still exceeds capacity by 44,096.

**Scope:** a source-bound interface lemma and concrete physical-sector
counterexample for one proposed row/column encoding. The retained caller
supplies an actual two-stage boundary; it does not supply an actual adjacent
completed P104 pair. The reversed column encoding is a proposed swapped-role
contract, not an independently replayed inverse native word. No supplier,
new kappa, physical runtime gain or selected-frontier change is claimed.

See [PROOF.md](PROOF.md) for equations, the full obligation ledger and stop rule;
[RESULT.json](RESULT.json) for exact finite counts; [TASK.json](TASK.json) for
scope and next questions; [PREDECESSORS.json](PREDECESSORS.json) for credit.

## Reproduce

Standard-library Python 3.12:

```
python3.12 -I -B research/p104-encoded-boundary/verify.py
python3.12 -I -O -B research/p104-encoded-boundary/independent.py
python3.12 -I -O -B research/p104-encoded-boundary/test_verify.py
python3.12 -B scripts/research_package.py --package research/p104-encoded-boundary
python3.12 -B scripts/check_research_commit.py --package research/p104-encoded-boundary --check-source-history
```

The primary checker reconstructs the canonical 104 roots and B, checks 208
local inverse basis columns (all fibers are disjoint), the physical-sector
counterexample and complete conditional gate. The separate dense checker
assembles four small whole-grid operators, including varying invertible chart
blocks, without importing the primary implementation. It checks all columns
and both literal occupancy and orientation failure controls. Tests check
optimized execution, bad result/source bytes and an offline read-only export.
Finite checks support the displayed algebraic proof; no human or kernel review
or full selected supplier replay is claimed.

## Open next questions

The actionable question is an actual chronological pair of completed calls
whose exit and entrance share one physical encoding on every role. Begin with
one named owner schedule and its source/target orientation, not a new scalar
adapter. Its helper maps, chart transports, fixed returns and complete cost
must be specified before native expansion. Alternatively, change the owner or
coverage contract and derive a new favorable gate first. The sibling copy and
coverage studies are separate investigations, not premises of this result.

## Credit and source history

Chris R / Clear1nsight, with substantial OpenAI Codex assistance. Apache-2.0.
PR3882/3940/3943 and PR3954 retain credit for residual encoding, actual caller,
cleanup, and physical two-axis compatibility/gate. PR3956 independently matches
the 960/1152 adapters; this package does not repeat that comparison. Rohan Arun
(PR1972), Chafik Boukhalfa (PR1991), Adam Gall (PR1940), Josie Elliston/E8,
Sagar Thakrar/PR1012, Douglas Colkitt, Dominik Scholz and the retained native,
compiler, occupancy and terminal-floor lineage retain their original credit.
The three live source inputs are canonical-main files. Pending PRs are credited
context; no unmerged Git object is required for replay.
