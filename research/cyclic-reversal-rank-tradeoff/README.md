# Sharp rank cost of noncentral cyclic reversal

For q independent p-cycles over any field, the exact minimum rank of J-I
needed to conjugate the complete stage to its inverse is

    q floor((p-1)/2).

This holds with any finite identity-stage workspace and arbitrary mixing
with it. For a boundary rank budget r, the exact minimum rank of the
complete reversal defect is

    max(0, q*(p-gcd(p,2))-2r).

Partial permutation reflections attain every budget, including in
characteristics dividing p. Different input and output boundaries must
have total rank at least q*(p-gcd(p,2)), also sharply. [PROOF.md](PROOF.md)
states the complete all-input contract and proves these claims.

Claim type: **scoped proof with finite exact corroboration**. No new kappa
is claimed. Ordinary matrix rank is not automatically a native tariff.

## Source and contribution

The source question is Ali Romman's
[PR6168](https://github.com/CrocSwap/integer-mult-bounds/pull/6168), specifically
the noncommuting native-map route left open in
`research/cyclic-stage-rank-budget/README.md`. This result changes that
constant-in-stage premise to a specified noncentral boundary. It supplies
a necessary boundary-rank allowance before attempting a physical cyclic
reversal. The predecessor's query tariff is not rechecked or used as a
theorem dependency. No predecessor implementation is copied or imported.

Base: canonical main `a5bff3bf133e482541c09eba4e773884bdb2b1b7`, priority
revision 8. The selected conditional kappa `781451/250000000` is unchanged.
The decoder card is explicitly changed to this boundary-rank subproblem.
[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19272032).
Source pins and exact scope are in [SOURCES.json](SOURCES.json) and
[TASK.json](TASK.json).

The rank inequalities and permutation-cycle facts are classical. The
sharp stable rank tradeoff and this application are produced by Nick Petalas.
Ali Romman retains the question and cyclic caller context; Cinna Davis and
the retained native/query/caller lineage retain their source contributions.
No worldwide priority claim is made. Apache-2.0.

Adam Gall / [PR1941](https://github.com/CrocSwap/integer-mult-bounds/pull/1941)
already gives concrete cyclic-reflection permutations and swap counts for
even cycles. This result adds optimality over all invertible boundaries,
the residual-rank tradeoff and arbitrary-field workspace stability.

## Reproduce

From the repository root, using CPython 3.12 and its standard library:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/cyclic-reversal-rank-tradeoff/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/cyclic-reversal-rank-tradeoff/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/cyclic-reversal-rank-tradeoff
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/cyclic-reversal-rank-tradeoff --check-source-history
```

The direct marker is `PASS_CYCLIC_REVERSAL_RANK_TRADEOFF`. Every replay emits
a generated JSON receipt binding the six package files by SHA256. It writes
no files and needs neither Git nor a network connection. Registered replay
runs both warning-strict normal and optimized modes.

Evidence covers partial-reflection constructions at periods 2 through 32,
one through four cycles and zero or three workspace coordinates. A separate
dense elimination checks fields F2,F3,F5,F7,F11 through period 12. Complete
binary matrix enumerations include a dirty-workspace case and characteristic
dividing the period. The replay checks 5,544 constructions, 1,560 dense
field cases and 5,912 two-sided permutation boundaries. It enumerates 132,096 binary matrices,
including 40,656 invertible boundaries. The receipt reports each census
and minimum defect rank. Controls check a wrong rank-one boundary, a boundary
mixing dirty workspace, a nonfaithful stage, and agreement of the dense and
bit-matrix implementations. These finite domains are not the proof of the
unbounded theorem.

## Limitations

The stage is the stated direct sum of regular permutation cycles and an
identity workspace action. The charge is rank(J-I), with the complete
defect measured on all rows and columns. It does not cover a promised input
subspace or equate rank with a norm-error guarantee. Native Clifford
realization and phases, concave recursive price, helper targets, restoration
outside this identity-stage model, caller, compiler, precision, storage and
movement have not been established. The selected scientific cold replay,
Lean and Docker are not run. Independent human and formal proof-kernel
review are unclaimed.

## Open next questions

- Bind one explicit native noncentral map to this regular-cycle action and
  derive its actual paid rank profile. First identify the complete native
  action, including phases and every spectator. This needs a source-specific
  realization; ordinary rank alone does not price the map.
- Price a complete caller using a noncentral boundary. First include both
  boundaries and all productive target changes in its signed invoice.
  This result supplies a rank floor, not a passing bill or a physical word.

## Verification design

The finite domains bound every loop. The largest exhaustive domain contains
2^16 binary matrices. Functions are at most one page; failures raise explicit
exceptions under normal and optimized Python. Python-managed allocation is
a documented Power of Ten deviation, bounded by the fixed domain sizes.
No recursion, dynamic code loading, solver, dependency or shared-state write
is used. Build the Lever shaped the rerunnable exact checker; Prove It Works
requires complete-matrix checks, including workspace coordinates. Laziness
Protocol kept this to one self-contained package.
