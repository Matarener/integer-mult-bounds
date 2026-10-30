# No two-target UT4 word has n_b = 7 with middle ranks (2,2)

**Result.** In the explicit `F2[UT4(F2)]` central-target alphabet of
[CrocSwap/integer-mult-bounds#1662](https://github.com/CrocSwap/integer-mult-bounds/pull/1662),
no legal word realizing two central targets — of any finite length, on any
finite restored dirty workspace — has exactly seven paid `b` calls with middle
ranks `(rank X, rank Y) = (2, 2)`, under the same unrestricted side-zero
profile reduction used by
[CrocSwap/integer-mult-bounds#3887](https://github.com/CrocSwap/integer-mult-bounds/pull/3887).

Middle-rank patterns `(2,3)` and `(3,2)`, and unrestricted `n_b = 7` (any middle
ranks), are explicitly left open. This package does **not** claim that every
`n_b = 7` word is impossible.

No new κ. Selected decimal stays `0.001672660197076918`.

## Why it matters

#3887 ruled out `n_b = 6`, so every realizing word has `n_b >= 7`. At `n_b = 7`
the #1662 rank bound `n_b >= 2 + rank X + rank Y` with `rank X, rank Y >= 2`
permits patterns `(2,2)`, `(2,3)` and `(3,2)`. The `(2,2)` slice still places
every middle coupling in a fixed 2-plane, so the #3887 dirty-contraction /
unrestricted-profile screen applies directly. Closing that slice narrows the
remaining weighted-tariff gate toward `(abcb)^2`.

## Method

[PROOF.md](PROOF.md) records the argument. With `rank X = rank Y = 2`, all seven
`b` couplings lie in an active 2-plane `H`. Interior dirty contractions cannot
touch the `{a,b}` / `{c,b}` side coefficients or the cross coefficients `abc`
and `cba`. Those necessary equations reduce to a two-role profile problem with
unrestricted outer length.

The census (self-contained in `core.py`, formulas matching #1690) enumerates
all 49,686 GL2-minimal zero-sum length-7 middle sequences, keeps the 49,140
with ranks exactly `(2,2)`, builds every side-zero transport key via a 3+4
meet-in-the-middle, and pairs keys for `abc = cba = I_2`. **Zero pairs survive.**
A low-rank control middle with ranks `(1,2)` still produces pairs, so the screen
is not empty by accident.

| Stage | Count |
|---|---:|
| Canonical zero-sum middles | 49,686 |
| `rank X = rank Y = 2` | 49,140 |
| Sum of side-zero key-set sizes | 46,169,088 |
| Key pairs with `abc = cba = I_2` | **0** |

## Evidence

- `verify.py` (read-only, `need()` gates survive `python -O`): source pins;
  corrupted temporary certificate and duplicate JSON key rejection; low-rank
  positive control; full census against `CERTIFICATE.json`.
- `independent.py` does **not** import `verify.py`; it re-runs the census with
  a separate base-16 half-profile MITM and matches the certificate.
- `test_package.py`: isolated `-O` read-only replay, independent import guard,
  certificate pair corruption, duplicate keys, SOURCES sha drift.

## Reproduce

```sh
python3 -B scripts/research_package.py --package research/ut4-two-target-nb7-ranks-22
# Direct:
python3 -I -B research/ut4-two-target-nb7-ranks-22/verify.py
python3 -I -O -B research/ut4-two-target-nb7-ranks-22/independent.py
python3 -I -B research/ut4-two-target-nb7-ranks-22/test_package.py
```

## Open next questions

1. **Does any two-target word have `n_b = 7` with middle ranks `(2,3)` or
   `(3,2)`?** Why it matters: those patterns saturate
   `n_b = 2 + rank X + rank Y` and need dirty roles beyond the two-plane
   reduction used here. First step: extend the profile/key analysis to `r >= 3`
   with one middle-excess role, or find an algebraic obstruction. Blocked by:
   dirty-role structure beyond the unrestricted two-role reduction.

2. **Is every `n_b = 7` two-target word impossible?** Why it matters: finishes
   the first step of #1816 open question 2 once `(2,3)` and `(3,2)` are decided.
   First step: combine this `(2,2)` exclusion with a `(2,3)/(3,2)` argument; do
   not treat the present package as that claim. Blocked by: open mixed-rank
   cases above.

## Limits

- Decides only `n_b = 7` with middle ranks `(2,2)` under the #3887 unrestricted
  side-zero reduction. Does **not** decide `(2,3)`, `(3,2)`, or full `n_b = 7`.
- Does not restate the unit-tariff minimum 16 from #1816; does not reopen
  three-target lengths 21/22; does not reprint the #3887 `n_b = 6` census as new.
- Quotient-level obstruction (sufficient for the formal endpoint). No
  proof-assistant or independent human review. No supplier or κ change.

## Credit

#1662 (@ToikY) for the model and `n_b >= 6` bound. #1816 for unit-tariff
exactness and the weighted open question. #3887 for the `n_b = 6` exclusion and
the unrestricted side-zero reduction reused here. #1690 (Aaron Wang / @navinor)
for the profile/key pipeline, as used by #1816. #1680 for workspace context.
Prepared by Wentao Li `<wentaol4@illinois.edu>` with substantial AI assistance.
Apache-2.0.
