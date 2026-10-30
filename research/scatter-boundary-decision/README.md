# Scatter multiplicity at the checker/exporter boundary: reproduction and successor decision

The archived [scatter/export parity audit](../scatter-export-parity-audit/README.md)
reports that appending `[0, 0]` to row 0 of the selected bit word passes the
complete symbolic checker but changes the exported F2 endpoint. This package
reproduces that fixture on an independent route from the pinned bytes, then
decides what a successor checker/exporter must enforce. No new kappa, no
supplier, no selected-frontier change.

## Result

Measured on the pinned tuned word `bitE8mut-p111-tuned.json.gz` (v = 111,
R = 439, 661 columns, 9 retained totals, 527 scatter terms):

| appended occurrences of index 0 in row 0 | checker | exporter records | semantics agree | normalised export differs |
|---:|---|---:|---|---|
| 0 | accept | 27,234 | yes | no |
| 1 | reject (`targets not y + x: [0]`) | 27,235 | yes | no |
| 2 | **accept** | 27,235 | **no** | **yes** |
| 3 | reject (`targets not y + x: [0]`) | 27,235 | yes | no |
| 4 | **accept** | 27,235 | **no** | **yes** |
| 5 | reject (`targets not y + x: [0]`) | 27,235 | yes | no |
| 6 | **accept** | 27,235 | **no** | **yes** |

The exact divergence class is **positive even multiplicity**. The pinned checker
XORs a copied total once per occurrence (multiplicity parity); the exporter
emits one ADD when the index occurs at all (membership). For one index, the two
lowerings agree exactly when every positive multiplicity is odd. A
checker-accepted word can still have even multiplicities, and only those
words are exported with the wrong operator. Odd multiplicities are already
rejected by the checker, so the hazard class that can reach the exporter through
a checked pipeline is exactly the even positive multiplicities 2, 4, 6, ...

Reproduced exactly against the archived receipt: baseline 27,234 records
`ea44aa047a2a9cf034de8b56b2166c49cf2dbdf9cd9ed6a20299a4f2b05ef09a`, the pair
mutant 27,235 records `5629b522bb0381127e3514396f034f308e0aa797f134f833e4d8feb678dce744`
and a single changed target register 111 whose difference support matches the
archived 98-column witness, with input column 472 present.

## Producer guarantee and the successor decision

The retained producer chain cannot currently emit a repeated index:

- `decoder_rows` in `gen_p3.py` builds every row from
  `itertools.combinations`, which is strictly increasing and therefore simple;
  the local control re-checks that combinations over a small range are simple
  supports for every size.
- `pwordl.build` copies the rows (`scatter=[list(scatter_rows[t]) for t in ports]`),
  preserving a simple input.
- `tune/apply.py` never mentions `scatter`, and the tuned word's rows are
  byte-equal to the untuned base word's rows.
- Both pinned words measure zero repeated rows and maximum multiplicity 1.

Decision for a separately versioned successor: enforce simple supports (reject
duplicates) in both the checker and the exporter while `decoder_rows` is the
only producer, because it costs nothing and states the invariant locally. If a
future producer ever makes multiplicity meaningful, canonicalise rows to parity
inside the exporter instead of lowering by membership, which makes the exported
operator equal the checker's parity operator for every word. Both options must
also declare the index type domain explicitly: `true` is accepted as `1` by
both stages, a float index crashes the checker with an uncaught `TypeError`
while the exporter silently lowers it as membership, and a string index never
matches the exporter.

## What this does not establish

- It is a finite reproduction and a boundary decision on the pinned selected
  bytes; it is not a proof about all bit words, producers, or versions.
- The native scalar check rejecting the mutant endpoint was rerun from the
  archived package's own harness as a local black-box control
  (`PASS_SCATTER_EXPORT_NATIVE_PARITY_CONTROL native_legality_accepts=3 scalar_rejects=2`);
  it is a rerun of that control, not an independently written native route, and
  it is not registered as a CI check.
- No other retained archive's scatter lists were censused here. The census
  covers the two words in the selected tuned chain.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/scatter-boundary-decision
python3.12 -B scripts/check_research_commit.py --package research/scatter-boundary-decision --check-source-history
python3.12 -I -Werror -B research/scatter-boundary-decision/verify.py
python3.12 -I -O -Werror -B research/scatter-boundary-decision/test_verify.py
```

`verify.py --emit` prints the generated receipt; without `--emit` it byte-compares
against `RESULT.json`. The registered replay command runs the first form.

## Open next questions

1. **Adoption with a regression fixture.** A successor exporter should reject
   (or parity-canonicalise) duplicate rows and add the paired fixture to its
   full symbolic/export/native sequence. First step: patch a successor copy of
   `export_records.py`, run the selected baseline, single and pair fixtures, and
   require the baseline record bytes to stay identical. Blocked by: no successor
   checker/exporter is versioned yet; frozen packages stay unchanged.
2. **Coverage of other retained words.** Census every retained archive word with
   a scatter list for repeated indices, not only the two words in the selected
   tuned chain. First step: extend the live-input set with the earlier
   PR543/PR555/PR589 lineage words and rerun the census. Blocked by: additional
   source pins and a bounded replay budget.

## Credit

The counterexample, its fixture and the opt-in guard are Nick Petalas's, in
[#2977](../scatter-export-parity-audit/README.md); eumemic wrote the punctured
generator and word checker lineage, DreamingOfClouds the punctured-star and
retained bit construction lineage, Dylan Crow the exporter and native checkers,
and Douglas Colkitt supplied the selected source bindings and review. The
independent record route, the multiplicity-class sweep, the producer census and
the boundary decision are by Nick Petalas, produced with AI assistance.
Apache-2.0. Independent human and formal proof-kernel review are unclaimed.
