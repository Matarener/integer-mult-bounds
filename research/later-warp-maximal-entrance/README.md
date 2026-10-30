# Later-warp maximal entrance

**Negative result. No new κ.** Selected κ stays `0.001672660197076918`.

## Scope and evidence

Original card: `scalar-to-moment`, scope **changed**. The card asks whether
one scalar simplification improves a paid profile. This package answers the
first open question of the warp-0 transported-frame bill: one later native
event's maximal legal entrance, with entrance, terminal, and caller charges.

Warp array index 13 is the native event immediately after warp 0 on the
PR #3929 base word. It uses lender 349 at original B position 916. The
original entrance is `span(416, 70, 19, 13)`.

On that word:

- Backward capacity returns `C = U + span(7)`, dimension 5. The same pass
  recovers PR #3933's warp-0 entrance `U0 + span(7)` as a transcription
  control.
- Exactly one of the 31 quotient lines is legal. One explicit dimension-6
  join fails the terminal caps.
- The least completion inserts one identity scale on register 349. The named
  caller fields stay byte-identical. Terminal end-climbs stay `H1: 289`,
  `H2: 77`, `H3: 54`. Cleanup gains exactly one inverse scale.
- The forward histogram changes by `+28 H1 − 16 H2 − 4 H3 + 4 H4`. Rank mass
  stays 5134.

[PROOF.md](PROOF.md) factors that delta as `4*((2-2^q)^2+(3-3^q))`, strictly
positive for every power tariff `r^q` with `q` in `[0, 1)` and zero at rank
mass. The zero caller and terminal end-climb deltas cannot reverse that sign.

The base word and frame bill are the bytes already hashed by the warp-0
price. SHA256 pins are checked by `verify.py`. Catalogue provenance is in
[SOURCES.json](SOURCES.json). [vendor/NOTICE.md](vendor/NOTICE.md) records
why those bytes are not files of this base commit.

## Reproduce

From the repository root, Python 3.12, standard library only:

```sh
python3.12 -B scripts/research_package.py --package research/later-warp-maximal-entrance
```

Direct check:

```sh
python3.12 -B research/later-warp-maximal-entrance/verify.py
```

Observed marker:

`PASS_LATER_WARP_MAXIMAL_ENTRANCE warp=13 lender=349 next_native_after_warp0 C=U+span(7) dim=5 admitted_line=7 entrance=+1H1 terminal_end_climbs=0 caller_fields=0 histogram=+28H1-16H2-4H3+4H4 mass=5134 power_tariff_strict_for_q_in_[0,1) no_new_kappa`

Not run: the other 62 native events, native phase replay, an owner fill
against PR #3945, a selected cold replay, Lean, or Docker. The power-tariff
sign is the argument in PROOF.md; the verifier checks the integer hypotheses
that argument cites.

## Open next questions

1. Does any of the other 62 native events after warp 0 have a legal entrance
   enlargement whose full entrance-terminal-caller bill lowers a power tariff?
   First step: the next native event after warp 13, with the same backward
   pass and least completion. Blocker: those capacity masks are not stored
   here.
2. Can PR #3945's idle-owner fill absorb `+28 H1` without a new slot? First
   step: add this exact child delta to the pinned #3945 profile. Blocker:
   that word is not an input of this package.

## Credit

Dugongue, PR #3929, for the transported-frame word and maps. ToikY, PR #3933,
for the backward-capacity theorem and the warp-0 canonical delta used as the
transcription control. Sagar Thakrar for `audit_core.py`, following Arham
Tahir's BORROW-WORD reading. The word label credits the PR #2312 lineage.
The warp-0 three-charge split that posed this question is the fork package
`research/transported-frame-caller-price`. Prepared by unpaidmoon with
substantial Cursor Grok assistance. Apache-2.0. No independent human or
formal-kernel review is claimed.
