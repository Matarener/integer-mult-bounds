# Rank 32 from a local repair of the P112 frame packing

Replacing two full eight-frames and four leftover pairs in PR3356 with two
six-groups and three four-groups reduces its **34 scalar queries to 32**.
Eleven eight-frames remain unchanged. A forced identity minor proves that this
new matching's minimum fitting rank is **32 over every field**, or **32d** for
uniform d-dimensional port payloads with arbitrary directed free blocks.

The construction uses fewer full frames (11 versus 13) but fewer total even
groups (16 versus 17). Maximizing the number of full frames and minimizing the
number of scalar queries are different objectives. The exact 24-port repair,
complete mask argument and lower-bound witness are in [PROOF.md](PROOF.md) and
[CERTIFICATE.json](CERTIFICATE.json).

The full-plane copied-information tariff is still **224**, with profile
`22 rank-8 + 4 rank-6 + 6 rank-4`. This is a finite algebraic construction;
it supplies no physical decoder, new κ, selected-frontier change, or optimum
over all matchings. Native source access, restoration, frames, hosting,
precision and recursive costs remain separate obligations.

## Reproduce

Base `6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority revision 6.
The selected label input and retained predecessor bytes are authenticated by
[SOURCES.json](SOURCES.json). PR3356's certificate is retained verbatim as
`PREDECESSOR.json` from head `a91a44a049cd6114d0edaea714914b64f90c601d`; no
pending Git history or network access is required to replay the proof checks.

```sh
python3.12 -B scripts/research_package.py --package research/paired-plane-frame-repair
```

Expected: `PASS_FRAME_REPAIR_PRIMARY`, `PASS_FRAME_REPAIR_INDEPENDENT`,
`PASS_FRAME_REPAIR_CONTROLS`, followed by a successful package replay.
Direct Git-free replay uses
`python3 -I -B research/paired-plane-frame-repair/verify.py --suite primary`;
replace `primary` with `independent` or `controls` for the other suites.

The primary checker reconstructs every group, the entire ordered scalar mask,
the forced I32 and the complete-plane tariff. The separately written checker
uses explicit nine-component vectors, all sixteen vector-pair combinations per
plane pair, dense ranks over three fields, and the literal field sum/add/cleanup
program on all source and dirty-target columns. Controls reject broken
partitions, a partition-preserving nonorthogonal swap, false clique witnesses,
and source corruption, and expose the incorrect half-price representative-only
invoice. [RESULT.json](RESULT.json) records exact receipts and
[VALIDATION.md](VALIDATION.md) records the final environment checks.

Discovery is optional and is not proof evidence. `discover.py` uses
`python-sat==1.8.dev24`/CaDiCaL 1.9.5 and `six==1.17.0`; the normal verification
requires only Python's standard library. Its seed-40 order reproduces the
bounded 24-port repair search and refuses to overwrite output. Solver-reported
negative cases and exploratory timeouts are explicitly delimited in PROOF.md;
no failed search is called a global obstruction.

## Open next questions

- Can a different 32-port repair or matching use fifteen even groups? Start
  from a named cut and check a complete rank-30 fitting matrix. The tested
  three-frame domain is incomplete; fourteen full frames also remain open.
- Can the new query interface have a complete native realization below tariff
  224? Specify the changed source/reader contract before implementation and
  price every physical helper, copy, frame change and restoration. Fewer scalar
  channels alone does not lower this tariff.

Credit Nick Petalas/PR3356, Matarener/Mark/PR3335, ywz65, thakrarsagar,
Cinna Davis, Adam Gall, ctoth, Philippe Van Velzen, Jeremy Diviney and the
selected E8/P112 lineage. Tekalign, substantial OpenAI Codex assistance.
Apache-2.0. Independent mathematical review remains open.
