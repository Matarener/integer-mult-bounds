# One-sided connector obstruction, rank cuts, and a complete escape word

**No new kappa.** The new result is an unbounded obstruction with a short
proof, an explicit positive word outside it, and a precise search target
whose optimistic price remains favorable.

In the full-rank star stage contract, no three leaves can have identical
columns in every thin connector. The same statement holds for rows. This
covers every finite port dimension, every finite number of orthogonal stage
splits, every call order, and any number or rank of connector queries. It
strictly extends [PR5649](https://github.com/CrocSwap/integer-mult-bounds/pull/5649),
which kept four prescribed connectors and two calls per stage.

[PROOF.md](PROOF.md) replaces the order census by a prefix identity. The
forbidden chronology would make a matrix product have both determinants
`(1+x)^(3d)` and `(1+x)^d`. It also gives a rank and signature cut for arbitrary
connectors. For one-port binary copies, 127 leaves require at least ten thin
queries. Coupled ports must use their actual block dimension in this cut.

[ESCAPE-WORD.json](ESCAPE-WORD.json) is a real binary escape: eight fields,
six full calls, eight thin queries, and sixteen exact coefficients in the
complete polynomial endpoint. Its connectors distinguish individual leaves.
The proof prices it and rejects every concave moment at the pinned P104
bill. The separate 127-leaf, ten-query profile has an exact positive price
margin at saving .0035, but **has no operator**. A smaller target with 31
leaves and five rank-two connectors also passes that price test. The new
cut permits its coupled-port budget and rejects the corresponding one-port
budget. Both are search targets.

The cycle-frame and smaller-connector searches remain incomplete. Their
solver timeouts are retained as unknown. [DISCOVERY.md](DISCOVERY.md) records
what was searched and which positive candidates failed higher coefficients.
It also gives commands for the saved discovery tools and archive.

## Reproduce

Python 3.12 and the standard library suffice for the read-only checks. The
registered metadata check also needs the explicitly pinned PR5649 Git object.
In a fresh clone, fetch that provenance object first:

```sh
git fetch https://github.com/CrocSwap/integer-mult-bounds.git 0c27282f56a0e8ec6c1fbad0f2ccca646d0d8442
python3.12 -B scripts/research_package.py --package research/crossed-connector-caller
python3.12 -I -O -B research/crossed-connector-caller/verify.py
python3.12 -I -O -B research/crossed-connector-caller/test_verify.py
```

Expected status: `PASS_ONE_SIDED_CONNECTOR_OBSTRUCTION`.
[RESULT.json](RESULT.json) records the exact evidence. The independent checker
uses no solver or discovery module. It checks fifteen paired-order identities,
the full positive word, coupled chronology controls, the prefix factorization,
rank cuts, exact integer-power price intervals, and corruptions.

The general theorem is a written matrix proof. Finite controls support it;
they do not constitute proof-assistant or independent human acceptance. The
binary word does not establish a characteristic-zero lift, native frame
adapters, ownership, a complete compiler, or a new outer bound. Selected
kappa remains .00310045 at the pinned base. This package changes no frontier.

## Open next questions

- Construct a long word whose connectors have distinct leaf signatures in
  both directions. Start with 31 leaves and five rank-two queries per coupled
  port pair, or 127 leaves and ten rank-one queries per binary copy. Both
  optimistic prices pass at .0035. Use the saved word as a positive control.
  The fixed-source growth tests fail; resynthesize old connector restrictions
  or call order, then test every polynomial coefficient.
- Solve or certify the remaining finite searches. Seven thin queries at three
  leaves and the separate cycle frame have timeout cases. First use exact
  certificates or longer bounded solves on those saved cases. A timeout is
  not an obstruction.
- Give a native lift and complete invoice for any profitable binary word.
  Charge every adapter, helper, query, copy, clear, return and route. The
  current P104 tariff is only an optimistic comparison for this algebra.

Structured versions are in [TASK.json](TASK.json). Work began on canonical
main `df0137efd35e11b4445734bf612bdd4c7ebc330c`, priority revision seven.
The canonical investigation is [Discussion5593](https://github.com/CrocSwap/integer-mult-bounds/discussions/5593).
The live remote overlap check covered 344 open PRs and 4,952 Discussion
records; the sparse local notes were incomplete. Active native-word claims
were kept separate. [SOURCES.json](SOURCES.json) records exact source pins.

Credit Cinna Davis's controller/simplex work; PR5617/5631/5649 for the
query-frame and fixed-star work; and all retained P104, native, helper,
compiler and outer contributors. The vendored discovery alphabet retains
Cinna Davis's notice. Prepared for Ali Romman with substantial OpenAI Codex
assistance; no subagents. Apache-2.0.
