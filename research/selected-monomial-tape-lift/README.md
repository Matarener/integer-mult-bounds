# The selected caller's monomials and J routes as fixed, f-independent record lists

**Scoped positive result; no new κ.** PR #5442 (`allwidth-caller-certificate`) splits
`native_all_columns` for the selected #5413 caller into an algebraic half, which it closes,
and a physical half: executing `g^(tensor f)` and the port adapters on a fixed number of
tapes, for all `f` columns at once with one fixed primitive list, without disturbing
spectators, at the retained tariff. This package executes the record-level part of that
physical half, following the written realization of `SPECIALIZATION.md` §2–§3:

- every one of the **896 port wrappers** is a fixed list of at most 107 records (the §2 bound
  is 171), each an `XROW` / `NOT` movement record (one compact-control selected-bit addition
  or translation) or a phase record (`S`, `CZ`, global `i`); the list is independent of `f`
  and realizes the lift `m^(tensor f)` exactly, spectators untouched;
- the body's **1,088 own monomial words** (283 distinct: 800 whole-job helper normalizers, 240
  Z-map block maps, 32 C8 routes and aliases, and the provider's 8 mode `output_N` words that
  #5442's mode-output certificate binds) are fixed lists of at most 76 records each, read off
  the exact engine as group elements;
- the **central translation** `X0` is one record; `C0` and `D` are positive-rank children of
  the recursion, not adapters;
- the **16,748 `SWAP_BITS` events** of the plan's 119 `J` routes (main, helper and idle
  targets) are three `XROW` records each and realize the declared 145-axis permutations;
  the 16 central `X` corrections are one record each.

The tariff per movement record is the compact-control Proposition
(`notes/compact-control-movement.tex`): `O(V((f log p)^tau + 1))` on fixed tapes for
`f <= p`, `A = O(p)`. That domain is the actual layer's domain (`f <= e <= b_in^epsilon`,
`p = 6 b_in`, SPECIALIZATION §3), so the restriction `f <= p` is not a gap. What remains
inherited is the Proposition's own proof and the control-field reservations of the 145-axis
layout (`compact-control-layout.tex`). [PROOF.md](PROOF.md) has the lemma and its scope.

## Evidence (`verify.py`, standard library, CPython 3.12)

| check | coverage |
|---|---|
| wrappers, `f = 1`, exhaustive | 896 x 512 addresses, random spectators |
| wrappers, engine agreement | 8 wrappers x 512 basis states against `clifford_exact` |
| wrappers, `f = 2`, exhaustive | 2 wrappers x 262,144 addresses |
| wrappers, `f = 2, 3, 4`, sampled | 896 x 48 addresses each |
| body and mode words | 283 distinct words (1,088 uses), engine read-off certified as group elements, `f = 1` exhaustive, `f = 2, 3, 4` sampled |
| `X0` | one `NOT(0)` record, `f = 3` |
| `J` routes | 119 targets x (pre, post) literal words, 145 axes, `f = 2`, 12 addresses each |
| controls (`test_verify.py`) | unlifted global phase fails at `f = 2`; a dropped row addition, a removed swap, a single-column phase record and an asymmetric `Q` are rejected; spectators untouched |

Record totals over the 896 wrappers and the maxima are in RESULT.json.

```sh
python3.12 -B scripts/research_package.py --package research/selected-monomial-tape-lift
```

## Relation to `lockstep-completion-pass`

That package counts the records the compiler and the completion/splitting pass add per unit
instance (normalizer pairs, relocations, child calls, bank scans) without pricing them. This
package gives the record list and count of each normalizer and route of the selected caller.
Together they give the record-level bill of the compiled template; the price per record is the
Proposition's tariff in its domain.

## Open next questions

1. Execute the Proposition itself: a bit-level simulator of the four-update rotation scheme
   with dirty compact fields `u, t, b`, the chunk swaps and the overflow repair, at small
   `f, K, G`, checking exact XOR at the `f` selected positions and restoration of the fields.
2. Verify the control-field reservations of `compact-control-layout.tex` for the 145-axis
   plan layout (front fields before, back field after every active slot pair).
3. Replay the forward body's wrappers (review only; the selected controller runs the backward body).

## Credit

Cao Yifan / intqwq (#4610 and the P1 specialization), Cinna Davis (compact-control notes
and the controller/helper lineage), zxv (#4359 free-word substitution, #5428), Chris R /
Clear1nsight (#5413), Dillon (#5402), Ali Romman (#5383/#5398/#5376), Dugongue and icekylinx
(Clifford engine lineage), and the parallel #5442 census. Prepared by Mark (Matarener) with
substantial Claude Code assistance. Apache-2.0. No independent human or formal-kernel review.
