# CLAIM — P104 commuting-contact cascade on the PR #5580 word

Base: canonical main `5e0052ca0aa3036a3afa8b0438927377c8d97d53`, priority revision 7.
Exact construction input: [PR #5580](https://github.com/CrocSwap/integer-mult-bounds/pull/5580) at `6efa248cf456d6101d757e9d09ba29711d18a13a` (`research/p104-event-contact-step`, conditional $\kappa = 0.00308189$).

Question: PR #5580 explicitly left open whether a changed scalar event order within commuting windows can improve the complete paid profile beyond its fixed-order invoice ceiling `(0.00308189496866, 0.00308189496867)`. Because PR #5561, PR #5569, and PR #5580 preserved the exact linear order of the 21,686 scalar instructions from PR #5551, early moves of main ports `113` and `198` to 1-plane `597` (`[82]`) at events `13524` and `13528` (to read helper `710`) trapped subsequent commuting `ADD` writes into `198` (from `648, 649, 650, 652`) and into `113` (from `531`) at frame `597`.

Result:
1. **Stage A (Fixed-Endpoint Supporting Word `WORD-FIXED-ENDPOINTS.json.gz`, $\kappa = 0.00308415$):** Commuting `13625, 13628, 13631, 13634` (`198 += ±1/2 * 648/649/650/652`) before `13528` (`MOVE 198: 3 -> 597`) to frame `3` (`0D`) vacates frame `597` (`1D`) on all four helpers `648, 649, 650, 652`, collapsing `3 (0D) -> 597 (1D) -> 120 (5D)` (`H1 + H4`) into `3 (0D) -> 120 (5D)` (`H5`). All 735 `initial` and `final` frames and all 527 helper targets remain identical to PR #5580. Local paid delta: `-4 H1 - 4 H4 + 4 H5` (`-72` complete paid calls, `66,852 -> 66,780`), raising the raw crossing to `(0.00308415555080, 0.00308415555081)` (`+2.26058214e-6` over PR #5580).
2. **Stage A+B (Headline Cascade Word `WORD.json.gz`, $\kappa = 0.00308520$):** Commuting `13806` (`113 += 531`) before `13524` (`MOVE 113: 3 -> 597`) to frame `3` (`0D`) allows all three initial read contacts of helper `531` (`13806` with `113`, `13843` with `197`, and `14404` with `507`) to execute at frame `3` (`0D`) with `initial[531] = 3`. Because `197` remains at `3` (`0D`) after `13843`, its next contact `13846` (`197 += 319`) demotes from 3-plane `617` (`[30, 44, 76]`) to 2-plane `355` (`[30, 44]`), vacating `617` on both `197` and `319` and vacating `597` on `531, 197, 507`. Combined local paid delta vs PR #5580: `-8 H1 - H3 - 2 H4 + 4 H5` (`-126` complete paid calls, `66,852 -> 66,726`), with local helper target delta `-H8 + H9` (productive fields `12,814` and rank-mass surplus `760` unchanged), raising the raw crossing to `(0.00308521055201, 0.00308521055202)` and certifying **conditional $\kappa = 0.00308520$** at `TESTED = 0.0030852005` (`+3.31558335e-6` raw over PR #5580).

```json
{
  "schema": "integer-mult-coordination/v1",
  "kind": "CLAIM",
  "task": "scalar-to-moment",
  "scope": "P104 commuting-write contact cascade on the PR5580 word; complete paid-profile step",
  "base": "5e0052ca0aa3036a3afa8b0438927377c8d97d53",
  "expiry": "2026-10-25T23:59:59+00:00",
  "artifact": "research/p104-commuting-contact"
}
```
