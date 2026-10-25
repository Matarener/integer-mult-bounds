# Shared-port graphic query boundary

This package proves the exact multi-terminal projection rule for graphic query
attachments. For two old query ports, one additional difference-query transfer
test is necessary and sufficient for all finite three-terminal networks.
It adds a shared-port case beyond PR3535's independent single-port attachment.

The 30 displayed rational non-Fano/GF4 choices split into 13 compatible and
17 failed fixed-template cases. The compatible cases preserve the literal
pair-reader floor for arbitrary finite attached graphs. The failed cases
need a different argument. A literal six-term rank-(4,4) failed-map control
costs 14 against baseline 4, so it supplies no saving or new kappa.

Read [PROOF.md](PROOF.md) for the unbounded argument and exact scope,
[RESULT.json](RESULT.json) for the complete finite result, and
[WITNESS.json](WITNESS.json) for the actual factors and bill. The 13 cases are
not a classification of all marked pairs, other coefficient choices or
other transfer maps. Characteristic zero is the old-field application scope.

## Reproduce

Use CPython 3.12, standard library only, from the repository root.

```sh
python3.12 -I -O -Werror -B research/p112-multiport-query-boundary/verify.py
python3.12 -I -O -Werror -B research/p112-multiport-query-boundary/independent.py
python3.12 -I -O -Werror -B research/p112-multiport-query-boundary/test_controls.py
python3.12 -B scripts/research_package.py --package research/p112-multiport-query-boundary
python3.12 -B scripts/check_research_commit.py --package research/p112-multiport-query-boundary --check-source-history
```

The primary uses rational/GF4 elimination and checks the star and reduced
partition tests. The independent program uses exact integer minors, all GF4
annihilators, and separate boundary-functional/path/cut checks. Both recheck
the inherited base implications, all 64 subsets at each of 30 placements,
the actual literal endpoint/ranks/charges, and all 1,024 five-vertex edge
subsets. The fault controls run both real optimized CLIs, with four mutations
on private regular byte copies. The repinned source mutation must reach the
scientific base-transfer check. Source hashes stay unchanged.

For an offline scientific replay, export committed bytes with the repository's
exporter, check that export, extract it into an owned directory and run the
first three commands there. The export includes all four live proof/source
inputs. Scientific commands require no Git objects or network. Metadata and
history checks require a complete Git checkout.

## Sources and limits

SOURCES.json pins current-main runtime and mathematical proof inputs.
SOURCE-CLOSURE.json retains exact original PR3506 identities and predecessor
credit. COMPARISONS.json identifies the pending PR3535 context, which is not a
runtime or proof dependency. No frozen input is edited or copied just to gain
provenance. The selected record remains unchanged.

The proof is author-written. Independent human and formal proof-kernel review
are unclaimed. Finite replay is not a complete multiplication theorem.
Acquisition, coefficient execution, dirty restoration, physical frames,
hosting, precision, stock, compiler/all-size admission and complete paid
consumption remain unproved. No physical supplier is proposed, so this scoped
boundary result does not authorize another dependent construction round.

## Open next questions

- Can a failed displayed attachment admit a different characteristic-two
  transfer? Test the explicit marks E,F, ports G,F+G configuration first.
  The failure certificate concerns the supplied map only.
- Can a literal operator outside these transfer cases beat its full binary
  rectangle bill? Give both actual factors, the exact operator and every
  rectangle charge before attempting physical synthesis. The retained control
  is a losing example, and no cheaper consumer is supplied.
- Which larger terminal sets satisfy the partition criterion? Start with one
  explicit four-terminal potential list. Every new partition and the complete
  bill must be checked. The two-port table does not cover repeated attachments.

Credit stays with Philippe Van Velzen, ctoth and the actual-reader lineage
through PR3414/3463/3472/3489/3491/3505, plus Nick Petalas's PR3506/3524/3535.
See the preserved source proofs for their full predecessor notices.
