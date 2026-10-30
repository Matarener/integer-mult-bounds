# #4100's cached chirp odometer: literal head travel and rounding

**Claim type: a scoped proof audit (written amortization with explicit
constants), checked against a literal four-tape head-movement count. No new
κ.** This does not accept #4100 and changes nothing in it.

## Object, and why it matters

The object is the section "Chirp tables: eliminating another d-factor scan"
in Cinna Davis's [PROOF.md](../unconditional-batched-crt/PROOF.md), #4100 head
`337d04939571a637aeab54a0f58f54fde811663a`. That section claims three things:

- each emitted chirp costs `O(p)` table head travel on average, uniformly in
  `d`;
- at most `Σ_(j≥0)(j+1)/2^j` factors are recomputed per record;
- the pointwise error is `O(d·2^-P)`.

The ledger charges these phases at power 0. A leftover per-record `d` factor
would cost power `ε = 1−10^-30 > 1−κ`. #4100's own
`composition-controls.json` rejects exactly that route
(`old_per_record_d_chirp = (1−κ)−ε < 0`), and the verifier checks that
equality. So this tariff is load-bearing, and it is new in #4100 with no
lineage audit. [#4320](https://github.com/CrocSwap/integer-mult-bounds/pull/4320)
audited the chirp *identity* and listed this tariff as open.

**Outcome: the tariff holds, with explicit constants and the factor-two
premise PROOF.md states.**

## Model

Every term below counts head moves on unit cells. A word has `P` cells.

- **Radices.** `t_i ≥ 2` are powers of two, with `t_max ≤ 2t_min`. In #4100
  `t_i ∈ {r, r/2}`. Records are enumerated lexicographically, with axis 0
  fastest.
- **Table tape.** The `d` tables in axis order; table `i` holds `t_i` words.
- **Cache tape.** Slot `k` holds `π_k = Π_(i≥k) a_i(x_i)`. The emitted chirp
  is `π_0`.
- **Counter tape.** The address as one binary number.
- **One step.** Emit `π_0`, then increment the address. If the carry stops at
  axis `j`, recompute `π_j, …, π_0` in that order. Each recomputation reads
  table entry `(k, x_k)` and slot `k+1`, multiplies, and writes slot `k`.
  `π_(d−1)` is a table entry and needs no product.

This is the layout PROOF.md describes: tables and cached prefixes on
sequential tapes in axis order, recomputing exactly the changed suffix, with
no division.

## Results

**Theorem.** The cached odometer emits all `T = Π t_i` chirps with the
following costs.

1. **Table tape:**
   `≤ TP[1 + 2(t_max+1) Σ_(j=1)^(d−1) (j+1)/Π_(i<j) t_i]`, which is at most
   `TP(1 + 12(t_max+1)/t_min) ≤ 31·TP`.
2. **Cache tape:**
   `≤ 2TP + P Σ_(j=0)^(d−1) (j+1)(j+5)·T/Π_(i<j) t_i + 2d(d+2)P`, which is at
   most `30·TP + 2d(d+2)P`.
3. **Counter tape:** `≤ 4T`.
4. **Products:** exactly `Σ_(k=0)^(d−2) T/Π_(i<k) t_i < 2T`.
5. **Rounding.** Round toward zero at `P` fractional bits. Every table value
   and prefix product stays in the unit disk, and
   `|π̃_0 − π_0| ≤ (2d−1)√2·2^(−P)`.

**Proof of 1.** Count the steps by where their carry stops.

- A step whose carry stops at axis 0 reads the next entry of table 0. The
  head is already there, so the step costs only the `P`-cell sweep.
- A step whose carry stops at `j ≥ 1` starts at the end of table 0. It reads
  `(j, x_j)` at travel `≤ Σ_(i=1)^j t_i P`, then `(j−1,0), …, (0,0)`. Each
  of those costs `≤ (t_k + 2)P`, because the entry starts its table. The total
  is `≤ 2(j+1)(t_max+1)P`.

At most `T/Π_(i<j) t_i ≤ T/(t_min·2^(j−1))` steps stop at axis `j` or above.
Since `Σ_(i≥0)(i+2)/2^i = 6`, the sum is at most `6/t_min`. Finally
`t_max ≤ 2t_min` and `t_min ≥ 2` give `(t_max+1)/t_min ≤ 5/2`.

**Proof of 2.** The emit read costs `2P`. Each recomputation in a step whose
carry stops at `j` costs `≤ (j+3)P` of travel plus two sweeps. The sum uses
the same counts, and `Σ(j+1)(j+5)/2^j = 28`.

**Proof of 3.** The binary-counter amortization: `T` increments flip fewer
than `2T` bits, and each flip is visited twice.

**Proof of 4.** `π_k` is recomputed once per value of `(x_k, …, x_(d−1))`.
That count is `T/Π_(i<k) t_i ≤ T·2^(−k)`. PROOF.md's `Σ(j+1)/2^j = 4` is a
valid but looser bound.

**Proof of 5.** Truncating components toward zero cannot increase the
modulus. Each truncation of a value in the unit disk errs by `< √2·2^(−P)`.
By induction on the prefix chain, with `|ã| ≤ 1` and `|π| = 1`,
`e_k ≤ e_(k+1) + 2√2·2^(−P)` and `e_(d−1) ≤ √2·2^(−P)`.

**At #4100's caller.** `P = Θ(p)`, `t_i ∈ {r, r/2}` and `t_min ≥ 2`, so the
table, cache and counter travel are each `O(Tp) = O(V)`, uniformly in `d`.
Fewer than two `O(p log p)` products per record give `O(V log p)`. This
matches the ledger's power-0 row for cached scalar phases.

## Evidence

`verify.py` uses only the standard library and takes about 1.4 seconds.

**Literal head counts:** 36 cases.

| Family | `d` range | Table travel per `TP` | Cache travel per `TP` | Products per record |
| --- | --- | --- | --- | --- |
| all radices 2 | 1–12 | up to 6.997, flat from `d=6` | up to 11.995 | 1.999 |
| all radices 4 | 1–8 | up to 4.333 | up to 8.000 | 1.333 |
| radices 2 and 4 | 1–10 | up to 4.428 | up to 8.571 | 1.429 |
| radices 4 and 8 | 1–6 | up to 3.188 | up to 6.991 | 1.165 |

Every case is checked against:

- the per-case written bounds for the table and cache tapes;
- the uniform constant 31;
- the `4T` counter bound;
- the exact product count.

**Rounding:** 4,820 records at `d = 2..10` and `P = 16..32`, against a
60-digit reference. The worst error is 0.754 of the bound.

**Controls,** each of which must fail:

- **Per-record `d`-scan.** This is the route the ledger rejects. Table travel
  grows linearly, from 1.0 to 66.0 `TP` over `d = 1..12`.
- **Skewed radices `(2, 512)`.** These violate the factor-two premise and
  reach 258.5 `TP`, so the premise is load-bearing.
- **Round-to-nearest.** 112 table entries leave the unit disk.
- **Unit-ratio running product** instead of cached recomputation. It drifts
  to 965× the error bound.

**Source binding:** SHA256 pins of PROOF.md and `composition-controls.json`,
8 exact PROOF.md phrases, and the ledger identity
`old_per_record_d_chirp = (1−κ) − ε`.

## Not covered

- Table setup cost, `d·2^O(ell)·poly(p)`, which PROOF.md charges as `o(V)`.
- The multiplier's own tapes.
- Interleaving with the payload stream and polynomial-record packing of
  axis 0.
- The precision constant `2^-4p`. See #4320's open question 1.

The model is a unit-cell multitape count: a faithful model of the stated
layout, not a finite-state transition table. There is no proof-kernel check.

## Reproduce

```sh
python3 scripts/research_package.py --package research/pr4100-chirp-odometer-tariff --check-only
python3.12 scripts/research_package.py --package research/pr4100-chirp-odometer-tariff
python3.12 -B research/pr4100-chirp-odometer-tariff/verify.py
```

The verifier prints `PASS_PR4100_CHIRP_ODOMETER_FINITE`.

## Open next questions

1. **Interleave the chirp stream with the actual payload layout.**
   - *Why it matters:* polynomial records pack axis 0 as `r` coefficients.
     The chirp must be emitted in the payload's physical order, with no extra
     pass.
   - *First step:* extend the four-tape model with a payload tape of packed
     records, and count one pointwise pass.
   - *Blocked by:* nothing.
2. **Price table setup at the real parameters.**
   - *Why it matters:* it is the remaining `o(V)` claim in this section.
   - *First step:* bound the elementary `cos`/`sin` evaluation at `Cp+o(p)`
     bits per entry, times `d·t` entries.
   - *Blocked by:* fixing `C` (#4320's open question 1).

## Credit

The construction and the audited claims are Cinna Davis's #4100 (OpenAI Codex
assistance). #3935 (jmbarrancoml) is a related physical chirp/Gaussian
transform for an earlier family, and is not audited here. Prepared by Ryanson
Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
Apache-2.0.
