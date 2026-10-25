# Complex copy budgets for three to six unpaid coordinates

**Planning screen. No construction, no supplier and no new κ.** The selected
record is unchanged.

[plane-port-copy-budgets](../plane-port-copy-budgets/README.md) prices the
two-unpaid (plane-port) coverage law: the decoder copy charge per call may be
about 160 before it loses to the incumbent. The next structural question is what
**more** unpaid coordinates buy, alone and together with **large local
children**. [kappa010-complex-lever-floor](../kappa010-complex-lever-floor/README.md)
answers this only at `κ = 0.1`. This package gives the complete charge budgets on
the complex side for `u = 1..6`, from the incumbent tie up to `κ = 0.1`.

## Model

The engine is [complex-local-word-ceiling/ceiling.py](../complex-local-word-ceiling/ceiling.py),
imported unchanged and SHA256-pinned. The premises generalise the predecessor's
complex `shrink` bracket:

- `u` unpaid coordinates per live family;
- each of the 224 data incidences per call climbs `u−1` coordinates less;
- `selected` removes those units as rank-1 children of the shipped word, and
  `rank L` places all remaining non-copy local mass fractionally at a single rank
  `L ∈ {8, 16, 32}`;
- the eight rank-8 centre copies are replaced by `k` decoder copies of rank
  `r ∈ {2, 8}`, with charge `C = r·k`;
- idle mass goes to the rank-51 cap.

A budget is the largest charge whose relaxed moment is certified below one at the
target, with one more copy certified above one. **A missing budget rules out every
construction under these premises. A budget is only a necessary target.**

## Result: largest copy charge per call (copy rank 8; rank 2 differs by at most 10)

| `u` | local delivery | tie (selected κ) | κ ×2 | κ ×4 | a = 1/99 | κ = 0.05 | κ = 0.1 |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | selected word | 64 | 24 | – | – | – | – |
| 1 | rank 32 | 88 | 80 | 56 | 40 | – | – |
| 2 | selected word | 160 | 128 | 56 | – | – | – |
| 2 | rank 16 | 176 | 168 | 136 | 104 | – | – |
| 2 | rank 32 | 184 | 176 | 160 | 144 | – | – |
| 3 | selected word | 264 | 232 | 160 | 96 | – | – |
| 3 | rank 16 | 280 | 264 | 232 | 208 | – | – |
| 3 | rank 32 | 288 | 280 | 256 | 240 | 32 | – |
| 4 | selected word | 360 | 328 | 264 | 200 | – | – |
| 4 | rank 16 | 376 | 368 | 336 | 304 | – | – |
| 4 | rank 32 | 384 | 376 | 360 | 336 | 128 | – |
| 5 | rank 32 | 488 | 472 | 456 | 440 | 224 | – |
| 6 | rank 16 | 576 | 560 | 536 | 504 | 160 | – |
| 6 | rank 32 | 584 | 576 | 552 | 536 | 312 | 64 |

All 48 rows × 7 targets are in [RESULT.json](RESULT.json).

**Reading.**

1. Each extra unpaid coordinate adds about 100 units of copy budget per call
   (`w = 896/9 ≈ 99.6` families per call), at every target.
2. With the shipped local word, `a = 1/99` first opens at `u = 3`. The
   predecessor already showed that two unpaid coordinates alone stop below it.
3. Large local children matter most at high targets. `κ = 0.05` needs `u ≥ 3`
   with rank-32 delivery (budget 32), `u ≥ 4` for a usable budget (128), or
   `u ≥ 5` with rank 16.
4. `κ = 0.1` first opens at `u = 6` with rank-32 delivery, with budget 54–64.
   This is consistent with kappa010-complex-lever-floor's exact boundary.
5. For comparison, independent per-port payload copies cost about `112·u`
   (PR2203's 224 at `u = 2`). That is above every tie budget, so any useful
   realization must share copy work across ports.

## Controls and reproduction

```sh
python3.12 -B research/complex-multi-unpaid-copy-budgets/verify.py      # ~3.5 min
python3 scripts/research_package.py --package research/complex-multi-unpaid-copy-budgets --check-only
```

`--write` regenerates RESULT.json; `-O` is refused. Controls:

- `u = 2` reproduces all six of plane-port-copy-budgets' complex `shrink` cells
  (164/160 at the tie, 160/160 at +10%, none at 1/99);
- `u = 1` with the shipped word gives exactly today's charge of 64 at the
  selected endpoint;
- `a = 1/9` opens first at `u = 6` for rank-32 delivery, matching
  kappa010-complex-lever-floor.

## Scope and limits

This covers the complex side only. The bit side would need the analogous screen
with the bit levers. The data-shrink model is the favourable bracket, and
fractional single-rank delivery is an idealisation, not a decoder. Physical
routes, dirty-state restoration, hosting, precision and every native cost not
expressed as copy charge are unpriced. No construction attaining any budget is
claimed.

## Open next questions

- **Can a k-dimensional port contract with `u = k ≥ 3` be realized with shared
  copies below these budgets?** This is the binding question for the lever. A
  first step is an exact masked fitting rank for good k-group covers of the P112
  labels (for k = 2 a rematched cover reaches 34; see PR3335), followed by a native
  price per channel. The blocker is that no accepted native price per shared
  channel exists.
- **What are the bit-side budgets?** The bit supplier must rise as well. A first
  step is to rerun this table with `bit-revision3-levers-seed03`.

## Credit

The engine and coverage law come from complex-local-word-ceiling (Douglas
Colkitt) and PR1012. The plane-port contract is ctoth's and discussion 1587's;
the budget method is plane-port-copy-budgets (JosieElliston); the κ = 0.1
boundary is kappa010-complex-lever-floor; the independent-block bill is
Jeremy Diviney's PR2203. Prepared by Claude (Anthropic) via Claude Code, in a
session donated by Mark. Apache-2.0.
