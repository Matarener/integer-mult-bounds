# Proof of the P104 Commuting-Contact Cascade ($\kappa = 0.00308520$)

This package modifies the [PR #5580](https://github.com/CrocSwap/integer-mult-bounds/pull/5580) P104 word (`research/p104-event-contact-step`, pinned at `6efa248cf456d6101d757e9d09ba29711d18a13a`) by commuting independent `ADD` instructions across two 1-plane transport barriers at frame `597` (`[82]`, $\dim 1$). Every scalar instruction, register operand, and dyadic coefficient is preserved; only the relative order of commuting `ADD` operations and their chart labels change.

## 1. Stage A: Fixed-Endpoint Commuting Writes on Port `198` and Helpers `648, 649, 650, 652`

In the PR #5580 word, main port `198` stays at the 0-dimensional origin chart `3` (`[]`) from initialization through event `13527`, receiving only `ADD` writes (`198 += c * s`). At events `13528..13634`, the relevant events on `198` and helpers `648, 649, 650, 652` are:

```text
13528: ['MOVE', 198, 3, 597, False]
13529: ['ADD', 198, 710, '2', 597]
13623: ['ADD', 205, 648, '-1/2', 3]
13624: ['MOVE', 648, 3, 597, False]
13625: ['ADD', 198, 648, '1/2', 597]
13626: ['ADD', 205, 649, '-1/2', 3]
13627: ['MOVE', 649, 3, 597, False]
13628: ['ADD', 198, 649, '-1/2', 597]
13629: ['ADD', 205, 650, '-1/2', 3]
13630: ['MOVE', 650, 3, 597, False]
13631: ['ADD', 198, 650, '1/2', 597]
13632: ['ADD', 205, 652, '1/2', 3]
13633: ['MOVE', 652, 3, 597, False]
13634: ['ADD', 198, 652, '1/2', 597]
13770: ['MOVE', 648, 597, 120, False]
13772: ['MOVE', 649, 597, 120, False]
13774: ['MOVE', 650, 597, 120, False]
13778: ['MOVE', 652, 597, 120, False]
```

### Commutativity and Subspace Nesting (Stage A)
1. **Write-epoch commutativity on `198`:** Between `13528` and `13634`, register `198` is never read or scaled; its only operations are `13529` (`198 += 2 * 710`) and `13625, 13628, 13631, 13634` (`198 += ±1/2 * r` for `r in {648, 649, 650, 652}`). Additions into a common destination register commute with each other and with chart transport of that destination register.
2. **Read-epoch invariance on `648, 649, 650, 652`:** Each helper `r in {648, 649, 650, 652}` is initialized at chart `3` (`[]`, $\dim 0$) and is only read (never written or scaled) prior to event `13771`. Thus at event `13528`, each `r in {648, 649, 650, 652}` already holds its unmodified initial symbol at chart `3`.
3. **Elimination of chart `597` on `648, 649, 650, 652`:** Executing `13625, 13628, 13631, 13634` at chart `3` immediately before `13528: ['MOVE', 198, 3, 597, False]` eliminates the four climbs `3 -> 597` (`13624, 13627, 13630, 13633`) and replaces the four climbs `597 -> 120` (`13770, 13772, 13774, 13778`, where `120` has 5-dimensional basis `[7, 25, 75, 160, 288]`) with direct climbs `3 -> 120`.
4. **Stage A Paid Delta:** On each of `648, 649, 650, 652`, the paid itinerary `3 (0D) -> 597 (1D) -> 120 (5D)` (`H1 + H4`) becomes `3 (0D) -> 120 (5D)` (`H5`). All 735 `initial` and `final` frames and all 527 helper targets remain unchanged. The Stage A local paid delta is:
   $$\Delta P_{\text{Stage A}} = -4 H_1 - 4 H_4 + 4 H_5$$
   which reduces complete paid calls by $72$ (`66,852 -> 66,780`) and raises the raw moment crossing from `(0.00308189496866, 0.00308189496867)` to `(0.00308415555080, 0.00308415555081)`. This supporting word is shipped as `WORD-FIXED-ENDPOINTS.json.gz`.

---

## 2. Stage B: Commuting-Write Domino Cascade on `113, 531, 197, 319, 507`

In the PR #5580 word, main port `113` stays at chart `3` (`0D`) up to event `13524`, where it moves `3 -> 597` (`[82]`, $\dim 1$) for `13525: ['ADD', 113, 710, '2', 597]`, followed by `13806: ['ADD', 113, 531, '1', 597]`. Because PR #5561's fixed-order solver could not commute `13806` before `13525`, helper `531` was forced to start at `597` (`1D`), which in turn forced `197` and `507` to climb `3 -> 597` for `13843: ['ADD', 197, 531, '-1', 597]` and `14404: ['ADD', 507, 531, '-1', 597]`:

| Frame | Basis | Dimension |
| --- | --- | --- |
| `3` | `[]` | 0 |
| `355` | `[30, 44]` | 2 |
| `597` | `[82]` | 1 |
| `617` | `[30, 44, 76]` | 3 |
| `728` | `[30, 44, 76, 391]` | 4 |
| `741` | `[13, 19, 65, 423]` | 4 |
| `788` | `[13, 19, 33, 65, 390]` | 5 |

Note that $30 = 13 \oplus 19 \in \text{span}(788)$ and $44 = 13 \oplus 33 \in \text{span}(788)$, so $\text{span}(3) \subset \text{span}(355) \subset \text{span}(788)$ and $\text{span}(355) \subset \text{span}(728)$ are strict subspace chains.

### Domino Cascade Steps (Stage B)
1. **Commute `13806` before `13524` at chart `3` (`0D`):** Between `13524` and `13806`, register `113` receives only `ADD` writes (`13525` and `13806`), and helper `531` is in its initial read-only epoch (unmodified until `14478`). Setting `initial[531] = 3` (`0D`) and executing `13806: ['ADD', 113, 531, '1', 3]` immediately before `13524: ['MOVE', 113, 3, 597, False]` preserves `113`'s itinerary `3 (0D) -> 597 (1D) -> 614 (3D)`.
2. **Vacate `597` (`1D`) on `531, 197, 507`:** Because `531` is now at chart `3` (`0D`) during its initial read epoch, `13843: ['ADD', 197, 531, '-1', 3]` and `14404: ['ADD', 507, 531, '-1', 3]` execute at chart `3` (`0D`). Helper `507` skips `597` (`1D`) and climbs directly `3 (0D) -> 728 (4D)` (`H4` instead of `H1 + H3`), and helper `531` climbs `3 (0D) -> 741 (4D)` (`H4` instead of `H3`) while its helper target credit increases from `H8` (`9 - 1`) to `H9` (`9 - 0`).
3. **Demote `13846` (`ADD 197 += 319`) from `617` (`3D`) to `355` (`2D`):** Because `197` stays at `3` (`0D`) after `13843` instead of climbing to `597` (`[82]`, which is not in `span(355) = span([30, 44])`), `197` now climbs directly `3 (0D) -> 355 (2D)` to meet `319` at `355` (`2D`) for `13846: ['ADD', 197, 319, '1', 355]`, and then climbs `355 (2D) -> 788 (5D)`. This vacates `617` (`3D`) on both `197` (`H2 + H3` instead of `H1 + 2 H2`) and `319` (`355 (2D) -> 728 (4D)`, `H2` instead of `2 H1`).

### Combined Stage A+B Invoice and Strict Concave Gain
Combining Stage A and Stage B across each of the 18 forward local calls gives:
- **Local paid delta:** $\Delta P_{\text{local}} = -8 H_1 - H_3 - 2 H_4 + 4 H_5$ (`-7` local `MOVE` instructions, `25,140 -> 25,133` events).
- **Global paid delta (18 calls):** $\Delta P = -144 H_1 - 18 H_3 - 36 H_4 + 72 H_5$ (`-126` paid calls, `66,852 -> 66,726`).
- **Local target delta:** $\Delta T_{\text{local}} = -H_8 + H_9$ (`-18 H_8 + 18 H_9` globally, keeping `12,814` productive fields and rank-mass surplus `760` invariant).

The exact rational interval engines enclose the raw moment crossings:

| Word | Lower endpoint | Upper endpoint |
| --- | --- | --- |
| PR #5580 (`p104-event-contact-step`) | `0.00308189496866` | `0.00308189496867` |
| Stage A (`WORD-FIXED-ENDPOINTS.json.gz`) | `0.00308415555080` | `0.00308415555081` |
| Stage A+B (`WORD.json.gz`, headline) | `0.00308521055201` | `0.00308521055202` |

The raw gain over PR #5580 is strictly between `0.00000331558334` and `0.00000331558336`. The claimed conditional saving is **$\kappa = 0.00308520$**, tested at `0.0030852005` with raw headroom `1.055201e-8 .. 1.055202e-8`.
