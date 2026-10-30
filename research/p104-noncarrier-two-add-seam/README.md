# P104: two non-carrier ADDs across the helper 572 seam fail

**Scoped exact exclusion; no new kappa.** On the selected PR6030 word,
none of 4,500 declared two-ADD location pairs restores every outside-V output
following the unit overwrite of helper 572 after event 13637. The corrections
may temporarily change original input rows, so this is outside the carrier-only
models of [PR6067](https://github.com/CrocSwap/integer-mult-bounds/pull/6067)
and [PR6069](https://github.com/CrocSwap/integer-mult-bounds/pull/6069).

The first ADD is at chart 595 after any event 13637..13651. The second is at
chart 603 after 13652,13654 or13655. All original events, fields, charts and
lifetimes stay fixed. Coefficients are arbitrary rationals, including zero.
Every original input and the new independent z are symbolic. [PROOF.md](PROOF.md)
specifies the complete domain and endpoint polynomial.

All cases fail even after relaxing the product `a*b` to an independent third
unknown. Each has an exact independently checked linear contradiction:
4,262 use one equation and 238 use two. Four separate literal whole-word checks
validate the polynomial on all input columns, including a nonzero interaction
term. A synthetic changed-boundary two-ADD repair is accepted, while a wrong
seam chart and a forged contradiction certificate are rejected. A retained false positive clears the z-leak but corrupts original inputs.
[RESULT.json](RESULT.json) retains the deterministic certificate digest and counts.

The scientific base is canonical main `721c03822c421b7f7fcbb2598993b947c4d88419`,
priority 8, selected conditional kappa 0.003125804. The canonical investigation is
[Discussion 6074](https://github.com/CrocSwap/integer-mult-bounds/discussions/6074).

## Reproduce

Python 3.12 and its standard library, from the repository root:

```sh
python3.12 -I -B research/p104-noncarrier-two-add-seam/verify.py
python3.12 -I -O -B research/p104-noncarrier-two-add-seam/verify.py
python3.12 -B scripts/research_package.py --package research/p104-noncarrier-two-add-seam
```

Direct normal replay took about 8.6 seconds on macOS arm64. Both registered
modes have 30-second limits. Every guard remains active under `-O`.
`--write` regenerates only this package's RESULT.json; default replay is read-only.
There are no executable pending-PR dependencies: the sole external live input
is the selected WORD.json.gz, source-pinned in SOURCES.json and declared in VERIFY.json.

## Coverage and overlap

This follows the original-row-changing correction question in PR6067 at
`4d629cf0d20a06d65b3ba0cf3a34e105128725e3` and PR6069 at
`b3f5aabddbae2d65f80bb8356e6993e0a65cd245`. Their carrier-only exclusions are
credited rather than replayed. The package derives its boundary data directly
from the selected word; neither pending proof is an executable dependency.

Preclaim overlap read 341 open PRs,5,722 discussion records and 8,348 local notes.
That metadata coverage is not a novelty guarantee or a search of historical
diffs/unpublished work. The companion receiver-recoding task concerns helper 469
and is separate. No fixed-invoice repacking or selected-word application audit
is repeated here.

The full necessary endpoint condition fails, so there is no edited supplier to
price. No native/compiler/caller/precision/outer replay, selected cold replay,
Lean, Docker or full multiplication proof is supplied. No universal bound or
claim about more edits follows. The five selected assumptions remain.

## Open next questions

A longer source-bound correction or a different chronological window remains
outside this exclusion. Before a new search, supply a concrete candidate word
that changes the failed original-input equations, then check its full symbolic
endpoint, pairing, lifetime and complete bill. No broader search is proposed
merely because this bounded model failed. Structured first steps and blockers
are in TASK.json.

## Credit

Prepared for **JoyboyBrian**, with substantial OpenAI Codex assistance in
triage, derivation, implementation and verification. This is AI-assisted
research, not independent human or proof-kernel approval. Apache-2.0.

Credit apoursh (PR6067), Jonathan Capalbo (PR6069), JosieElliston (PR6045),
Nick Petalas (PR6040), Matarener (PR5994), flyingviper (PR5718), Ali Romman,
DreamingOfClouds (PR6030/5907) and the retained P104/native/compiler lineage.
Frozen predecessor packages and the selected construction are unchanged.
