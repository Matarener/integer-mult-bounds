# A Boolean table that cannot lower its degree by tree splitting

This contribution was produced by Nick Petalas. Apache-2.0.

Scoped proof with a finite exact certificate. The explicit eight-bit
membership table in [TABLE.json](TABLE.json) has exact minimum maximum
vertex degree **eight** among all exact tree tensor realizations over
fields of characteristic zero or F_101. Seven is impossible. The original
single tensor attains eight.

The contract permits arbitrary internal coefficients, any finite tree,
arbitrarily many vertices and arbitrary bundles of internal Boolean
wires. Every wire in a bundle counts toward vertex degree; each external
bit attaches once. This settles the acyclic universal-splitting route for
this table in Jacob Sussman's [PR #5817](https://github.com/CrocSwap/integer-mult-bounds/pull/5817),
Open next question 2. It does not settle the full cyclic or asymptotic
vector-table question.

## Proof and evidence

[PROOF.md](PROOF.md) proves that a table with full matrix rank on every
nontrivial cut must retain a vertex of degree at least its number of
external bits. The proof factors each cut through its internal wires,
then sums the resulting rank bounds at a weighted tree centroid.

The verifier establishes the hypothesis for the literal 256-entry Boolean
table, which contains 121 ones. It checks every one of its 127 unordered
nontrivial cuts. The cut-size counts are 8, 28, 56 and 35, with ranks
2, 4, 8 and 16. For each cut, modular elimination finds a square minor;
a separate input-word scan rebuilds it and fraction-free elimination
computes its exact integer determinant. All are nonzero modulo 101.

Further checks enumerate 2,785 weighted trees on one through four labeled
vertices with eight external legs. These corroborate the centroid
argument; the written proof covers arbitrary finite trees. Twelve
controls reject malformed tables, false low-rank witnesses, an incomplete
cut domain, an empty cut, a nonsquare minor and a cyclic graph passed as
a tree. A literal four-site integer-valued cycle has all seven full cut
ranks at degree three, demonstrating why the graph hypothesis matters.

The new contribution is the explicit Boolean witness and its sharp
application to this table-splitting question. Classical tensor unfolding
ranks, including [Oseledets's tensor-train work](https://doi.org/10.1137/090752286),
and weighted tree centroids retain their credit. The cut argument is
proved here. No literature priority is claimed for those methods.

## Reproduce

From the repository root, using the CPython 3.12 standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/boolean-table-tree-degree/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/boolean-table-tree-degree/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/boolean-table-tree-degree
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/boolean-table-tree-degree --check-source-history
```

Another CPython 3.12 installation can replace the absolute interpreter
path. Direct verification also works from a Git-free package export.
Expected marker is `PASS_BOOLEAN_TABLE_TREE_DEGREE`, with `cuts=127`,
`degree_minimum=8`, `small_weighted_trees=2785` and `controls=12` in the
generated JSON receipt. The receipt binds all seven package files by
SHA256 and is printed to stdout. Verification writes no files. Both
registered commands have 60-second limits and use explicit exceptions,
so checks remain active under optimization.

## Scope and provenance

Base is canonical main `de5ec2e7a6074068452f45b1a191b5c72832df4a`,
priority revision 8. The original `formal-interface-lemma` card is
explicitly changed to this mathematical side question in [TASK.json](TASK.json).
Selected source-binding orientation passed. It authenticates metadata,
not a supplier or this theorem. Selected kappa remains `62009/20000000`.

Jacob Sussman's source head is `be98f61484415d75197ed6218ad0239306e7b1a2`.
[SOURCES.json](SOURCES.json) records the exact question-source README blob
and SHA256. It is external historical motivation, with no runtime or
proof dependency on its conditional claims, code or unmerged Git objects.
The pinned catalogue and selected record are provenance only.

The [advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19216917)
followed live account/open-PR, Discussion, main-tree and merged-PR checks
and a local reservation. Cached coverage included 459 open PRs and
5,407 Discussion records with complete remote pagination; sparse local
coverage was 190 of 7,845 HEAD notes. Targeted all-main searches supplement
that limitation. Unpublished work and arbitrary historical diffs remain
outside coverage. No predecessor result was replayed as the deliverable.

This fixed eight-axis example does not establish such Boolean witnesses
at every larger dimension or violate a stated asymptotic degree cap.
Cyclic networks, approximation, structured inputs and different wire
alphabets remain outside the claim. No general Orthogonal Vectors lower
bound, physical supplier, recursive invoice improvement, new kappa,
selected-frontier change or complete multiplication theorem is supplied.
Lean, Docker and selected scientific cold replay were not run.
Independent human and formal proof-kernel review are unclaimed.

## Implementation bounds

The verifier has no recursion, subprocess, network or write path. Its
flattenings have at most 16 rows and 128 columns, with 256 entries;
square minors have order at most 16. The tree controls have at most four vertices and three edges.
All enumeration ranges are explicit and finite, and functions are below
60 physical lines. Bounded file reads cover seven fixed paths, at most
256 KiB each. Python runtime allocation is a managed-runtime deviation
from static allocation; the finite dimensions bound live collections.
Twelve immediately executed control callbacks have five fixed targets
and retain no state after execution, a bounded deviation from avoiding
indirect calls. Warning-strict normal and optimized runs and in-memory
compilation provide diagnostics without changing shared build settings.
Any larger input domain needs new bounds before these limits change.

## Open next questions

- Can a cyclic network represent this specific table at maximum degree
  seven with a useful total wire count? Start with one fixed graph and
  its complete 256-entry endpoint. A cyclic factorization and complete
  wire budget remain missing.
- Which structured membership families permit low-degree tree
  factorizations with few wires? Start with one explicit family, its
  exact cut ranks and a complete tensor factorization. The proposed
  consumer currently supplies no structural promise that avoids this
  obstruction.

These are follow-on questions; the investigation stops at the first
explicit witness above.
