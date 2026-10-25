# Literal census of five full-guard header laws

**Claim type: an independent exhaustive finite computation. No new κ.** It
checks five open counting proofs by Nick Petalas at sizes beyond their own
literal censuses.

## Object

Each of these PRs gives the exact fraction of complete headers
`G ∈ GL_m(F_q)` passing a family of requests. `G` passes `R` when the leading
principal minors of `G·R·G⁻¹` of orders `1..rank(R)` are nonzero.

| PR | Family (canonical basis) | Claim checked |
| --- | --- | --- |
| [#4261](https://github.com/CrocSwap/integer-mult-bounds/pull/4261) | `I − e1e1ᵀ`, `I − e2e2ᵀ` | all-field 2×2 transfer law `C(q,m)·|GL_(m−2)|`; binary closed form |
| [#4273](https://github.com/CrocSwap/integer-mult-bounds/pull/4273) | the same pair, over F3 | `4(49ⁿ − 2·25ⁿ + 19ⁿ) / [9(3^m−1)(3^m−3)3^(2m−4)]` |
| [#4274](https://github.com/CrocSwap/integer-mult-bounds/pull/4274) | `I − e1(e1+e2)ᵀ`, `I − e2e2ᵀ` (one-way) | `(9ⁿ − 5ⁿ) / [4(2^m−1)(2^m−2)2^(2m−4)]` |
| [#4275](https://github.com/CrocSwap/integer-mult-bounds/pull/4275) | `I − e_te_tᵀ`, `t = 1..k` | `k = 3` binary closed form; binary threshold `m ≥ k+1` |
| [#4259](https://github.com/CrocSwap/integer-mult-bounds/pull/4259) | `e1e1ᵀ ⊂ e1e1ᵀ + e2e2ᵀ`, and the split pair | laminar product `∏ O(q, d_v; children)`; binary obstruction |

Here `n = m − 1`. Each PR enumerates complete headers only up to `GL_4(F_2)`
and `GL_3(F_3)` (and `m = 2` for F4, F5). #4273's `m = 4` value comes from
normalized pairs, not complete headers.

## Results

Every count agrees with every applicable formula, at every size:

| q | m | complete headers | engine |
| --- | --- | ---: | --- |
| 2 | 2, 3, 4 | 6; 168; 20,160 | Python and C |
| 3 | 2, 3 | 48; 11,232 | Python and C |
| 4, 5 | 2 | 180; 480 | Python and C |
| **4** | **3** | 181,440 | C |
| **5** | **3** | 1,488,000 | C |
| **2** | **5** | 9,999,360 | C (11 s) |
| **3** | **4** | 24,261,120 | C (15 s) |

The bold rows are beyond the authors' complete-header censuses. Highlights:

- **Stated values.** The PRs' stated values all reappear:
  - #4261: 1/84 and 1/80;
  - #4274: 1/6, 1/12 and 151/3360;
  - #4273: 14/117, and at `m = 4`, **1727/21060 from all 24M complete
    headers**;
  - #4275: 1/1680, and 480 of 11,232 over F3;
  - #4259: 343/1404.
- **#4275's threshold.** Over F2, three requests first pass at `m = 4` (12
  headers). Four requests pass on 0 headers at `m = 4` and on **48** at
  `m = 5`.
- **#4261's transfer law over a non-prime field.** The law holds at F4,
  `m = 3` (39,690 headers), and at F5, `m = 3`.
- **#4259.** The laminar product holds at every size. The binary split
  obstruction is 0 at `m = 3, 4, 5`.

## Method and independence

- **Literal census.** Every matrix over `F_q` is enumerated, inverted, and
  each conjugated request is tested by elimination without row exchanges.
  The PRs' normalizations, transfer walks and reductions are not used to
  count.
- **Predictions.** The closed forms, #4261's 36-state transfer recurrence and
  #4259's `F`/`O` product are implemented from the statements in the PRs'
  READMEs and PROOF.md files. Nothing is imported.
- **Two engines.** Python, standard library, reruns the seven small cases in
  about 4 seconds. `headers.c` covers all eleven. Its recorded runs are bound
  to the source by SHA256, agree with Python on every small case, and are
  local evidence that CI does not recompile.

## Not covered

- All-`m` statements beyond these sizes, which rest on the PRs' proofs.
- Other bases. The PRs prove basis independence; this check uses one
  canonical family each.
- Any caller binding. These laws concern complete, equally weighted header
  covers, as #4228 cautions.

## Reproduce

```sh
python3.12 -B research/full-guard-header-census/verify.py
cc -O2 -o headers research/full-guard-header-census/headers.c && ./headers 3 4
```

The first prints `PASS_FULL_GUARD_HEADER_CENSUS`. The second prints the
GL_4(F_3) counts in about 15 seconds.

## Open next questions

None from this check.

## Credit

The models, theorems, closed forms and transfer laws are Nick Petalas's
(#4259, #4261, #4273, #4274, #4275, building on #4227, #4239 and #4246).
Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5)
assistance. Apache-2.0.
