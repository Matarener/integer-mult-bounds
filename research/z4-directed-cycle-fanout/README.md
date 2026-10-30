# Exact nonunit dirty fanout on a cheap directed cycle

This contribution was produced by Nick Petalas. Apache-2.0.

For demand `(2,1,1)` over `Z/4`, the exact price is **six** when source
insertion into row zero and the directed ADD cycle `0 -> 1 -> 2 -> 0`
cost one, while all other source insertions and ADD directions cost 100.
Every nonzero coefficient has its gate's price. All three inputs are
arbitrary dirty rows; the disjoint source is preserved. There is no workspace.

This is a **scoped written proof with an exact finite certificate**, answering
the concrete cheap-cycle case suggested in Open next question 1 of
[lee-phys, PR #5163](https://github.com/CrocSwap/integer-mult-bounds/pull/5163).
That predecessor determines destination-only prices and leaves independent
directed prices open. Its result is cited, rather than replayed as the
contribution. The new chronological word is

```text
E_21(-1), E_10(-1), P_0(1), E_10(1), P_0(1), E_21(1)
(a,b,c,p) -> (a+2p,b+p,c+p,p).
```

Here `E_ij(c)` adds `c A_j` into `A_i`, and `P_i(c)` adds `c p` into `A_i`.
Every gate costs one. The word uses a path inside the cycle; the third cheap
edge remains available to competitors. [PROOF.md](PROOF.md) proves the
endpoint at every positive width and excludes every cheaper word, with
arbitrary repetitions, interleavings and nonzero coefficients. This supplies
one exactly solved independent-edge instance, not an arbitrary-price formula.
No new kappa, physical caller or selected-frontier change is claimed.

## Evidence and reproduction

Complete cheap-word balls of radii two and three contain 99 and 613 literal
three-by-four coefficient matrices, and are disjoint. Every word of length
at most five would give an intersection, since all inverses are available.
A separate scalar interpreter checks all 256 four-scalar inputs and their
inverse executions. Nineteen controls cover six gate deletions, six sign
changes, invalid gates and capacity limits. All nine directed gate types
have their prices checked. Each successful invocation prints a generated
receipt bound to all package-file SHA256 hashes. No receipt is handwritten.

From the repository root, using CPython 3.12 and only its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/z4-directed-cycle-fanout/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/z4-directed-cycle-fanout/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/z4-directed-cycle-fanout
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/z4-directed-cycle-fanout --check-source-history
```

Any CPython 3.12 installation can replace the local path. Expected markers
are `PASS_Z4_DIRECTED_CYCLE_FANOUT`, `PASS_REGISTERED_RESEARCH_PACKAGE` and
`PASS_RESEARCH_COMMIT_BYTES`. Normal and optimized runs retain all checks.

## Sources and scope

Scientific base is canonical main `19fdb086ea96af9a9f87936a2b888e10af4ed810`,
priority revision eight. Selected-source orientation passed with
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY`; it was metadata orientation.
TASK.json changes the historical `bit-helper-contract` card to this algebraic
side question. There is no G20 implementation claim.

Credit lee-phys #5163 for the question, destination-price theorem and unit-arrival
argument; Krzysztof Wójt [#5045](https://github.com/CrocSwap/integer-mult-bounds/pull/5045)
for nonunit source-count classification and repeated-insertion words; and
Ross Richardson [#3121](https://github.com/CrocSwap/integer-mult-bounds/pull/3121)
and #3063 for edge-priced forest synthesis and dirt restoration. The new word
adapts established child-first preparation to separated source insertions.
Nick Petalas #4916, Cinna Davis #1944/#1968, Anthony #774, Oscar Fennell #759
and Tekalign #3130 retain the earlier lineage. Classical matrix identities
are not claimed as new methods. Predecessor proof text is provenance-pinned;
no predecessor executable is imported or scientifically replayed.

Entry overlap covered 310 open PRs and 5,456 Discussion records in the reported
cache, live handoff and fanout threads, account submissions, all-main README
terms and distinctive merged-PR searches. Only one recent account target came
from #5163; its equal-nonunit question differs from this unit-containing
independently priced instance. Unpublished work and arbitrary diffs remain
outside novelty coverage.

Independent human and formal proof-kernel review are unclaimed. Physical
coefficient preparation, native frames, movement, precision, tape, storage and
the full supplier invoice remain unpriced. No multiplication theorem, Lean,
Docker or selected scientific cold replay is supplied.

## Implementation limits

There is no recursion, external process, network or output file. Words have
at most 64 gates; matrices have twelve residues; search radius is at most
three with a checked 1,000-state capacity. Functions have fewer than sixty
lines. Python managed allocation is a deviation from Power of Ten's fixed
allocation rule, confined to these bounded matrices and searches. The
compensating controls reject larger radii and words. A larger search needs
separately reviewed capacities. Warning-strict normal and optimized checks
exercise the limits. No shared implementation is changed.

## Open next questions

1. Determine the full directed-price envelope for this demand. Start with
   directional subset cuts and a complete Pareto search. The present proof
   solves one price matrix and does not enumerate that envelope.
2. Price one physical realization before using the word in a supplier.
   Specify coefficient access, routing, native frames and restoration.
   Those complete physical prices are missing from the abstract model.
