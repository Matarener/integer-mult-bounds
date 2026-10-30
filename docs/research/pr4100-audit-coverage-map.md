# Which parts of #4100 have an independent audit?

Use this map before choosing a `uniform-transfer-audit` task on
[#4100](https://github.com/CrocSwap/integer-mult-bounds/pull/4100)'s proposed
unconditional construction ([package](../../research/unconditional-batched-crt/README.md),
retained head `337d04939571a637aeab54a0f58f54fde811663a`, Cinna Davis). It lists, for
each obligation row of #4100's [AUDIT.md](../../research/unconditional-batched-crt/AUDIT.md),
the open PRs that audit it and what remains. The snapshot was taken on
2026-10-21 at 06:50 UTC against canonical main
`12fa8c5c844be21bfefb38a19503fbd867a11244`, priority revision 7. It was
updated at 07:45 UTC to add #4320, at 08:30 UTC to add #4321 and #4325, at 09:05 UTC to add #4327, at 09:20 UTC to add #4328, at 09:26 UTC for #4328's two-target update, at 09:36 UTC to add #4329, and at 09:47 UTC for #4329's width-pattern update, at 09:52 UTC to add #4330, at 09:57 UTC for #4330's binding update, and at 11:15 UTC to add #4319 and #4336.

**This is navigation, not acceptance.** Every outcome below is what that PR
reports. This map did not replay any package or recheck any proof. A positive
scoped audit closes only its own proposition, at its own caller and domain.
None of these PRs accepts #4100, changes the selected record or claims a new κ.
Check the PR's current head before you rely on it. The heads are in the
[source table](#exact-heads-at-the-check).

## Coverage by obligation

Rows follow AUDIT.md's "Prior premises" table, grouped by the four audit
partitions in the [family record](research-family-status.md#current-leads).

### CRT repair and placement (CRT.md)

| AUDIT.md obligation | Open audits | Reported outcome | Still open |
| --- | --- | --- | --- |
| Nonlinear CRT near ε=1: balanced tree and padded caller (§1) | #4195 | Positive. Binds the declared widths `h_i∈{ell−1,ell}` to the complete padded balanced-tree caller. Reversing the levels and rows inverts every padded state. | Uniform evaluator cost (see the E row below). |
| Beneš switch compiler (§2) | #4192 | Positive, conditional. Lowers the compiler on an *encoded permutation* to fixed tapes in `O(N³(p+2)^7)` time. | Turning CRT reconstruction, modular inversion and split descriptors into that permutation. The full `E(p,ell)` evaluator. |
| Reservoir placement (§3) | #4174; [#4173](https://github.com/CrocSwap/integer-mult-bounds/discussions/4173) thread | Positive. At most 25,600 batches per layer and three disjoint exchanges, with dense left-child dependencies kept. | Dirty restoration is conditional on the repaired switch's all-address contract. |
| Compact switches and total repair (§4) | #4169; #4321; #4328; #4329 | Positive. Every control omits every active target, which is the condition CRT.md states. #4169 also gives an explicit inverse on dirty addresses, and a counterexample shows that omitting only a control's own target fails. #4321 (unpaidmoon) notes that the displayed gadget reuses `t_i` as a frozen coefficient while the cancellation and the published `primitive_f` use the live digit. It proves the live-digit lemma and finds the `2B` guard margin sufficient but stricter than needed. #4328 prices the sparse repair at `Θ(p)`-bit records, where PR2250's `M·A³` tariff does not carry over: per color `≤ 9MR+5M` dense and `N(L+R)(9L+6)` sorted, which is `≤ p³(p+2)^-64·V` at #4100's `G`. #4328 also proves the exact `r`-target density `1−[(1−1/B)²(1−8B/2^K)]^r`, which implies CRT.md's union bound. It checks this exactly on all `2^20` two-target addresses (943/1024), where the repair realizes the switch on every record. Its caution: the reinsertion check accepts any keys that permute the holes, so correctness rests on the inverse keys. #4329 decides the disjoint-guard premise. Under mod-`K` coloring it needs **`(K−1)`-bit** guards, as the code and the `8B/2^K` term use. With literal `K`-bit guards, #4100's own gadget fails on 3,888 of its good two-target addresses. On all 104,864 of #4174's production plans, and on eight more regular width patterns, no two active targets can share a color, so the premise holds vacuously and each macro handles one target. It is not vacuous in general: an admitted pattern (uniform 24 with `ell−1` axes 16384..16407) puts same-color targets exactly `K` apart, so the `K−1` correction is needed. | Composing the hole mask, key evaluator and repair into one program; the full `E(p,ell)` evaluator. |
| Last-K elementary branch (§4) | #4187 | Positive, conditional. A two-slice schedule has `M/2^(H+1)` preparations and costs `O(VK)`. | It assumes the uniform evaluator, the complete omitted suffix and the ordinary width-one callee. |
| Dense guard detection at Θ(p)-bit records (§4) | #4201, #4208 | Positive. #4201 gives a literal three-tape scan for an *admitted* stencil. #4208 produces that stencil for one target from unary fields. | Many-target and binary/global descriptor production. |

### Native and free-algebra lift (COMPLEX.md)

| AUDIT.md obligation | Open audits | Reported outcome | Still open |
| --- | --- | --- | --- |
| Mixed native tensor lift | #4184 | Positive. Formal free-word cancellation holds on all four actual PR4088 programs, and a written proof covers every positive multiplicity. | Native realization, physical placement and the complete caller invoice. |
| Whole-call hosting and exact phases | #4180 (finite admission of the PR4088 provider set, task `supplier-boundary-audit`) | Finite PR4088 admission passes. | COMPLEX.md's arbitrary-f lift and complete-cover execution. No audit found. |
| Complex recursion and precision | #4178; #4171 | **#4178 reports a defect.** The common-grid allocation omits the incoming height `t0`. A constant input lands half a unit below the stated grid. The PR proposes a `P+t0+Bh` fractional allocation and does not reject the exponent. #4171 independently recomputes the exact root and every paid-power slack, all positive. | The author's response to #4178. The stopped-moment and common-grid height proof outside #4178's caller. |

### Precision and conditioning (GAUSSIAN.md, INVERSE-CONDITIONING.md, HALO.md)

| AUDIT.md obligation | Open audits | Reported outcome | Still open |
| --- | --- | --- | --- |
| Fine primes and setup precision | Merged lineage audit [`pr1786-fine-prime-transfer-audit`](../../research/pr1786-fine-prime-transfer-audit/README.md). #4100's `vendor/FINE-PRIME.md` is byte-identical to the PR1786 text it audits (SHA256 `47d1b1b4…`). | Positive. The `θ` interval is exact for `p=2..2000`, and `S/T > 1/2` whenever `d ≤ p`. The Trudgian step is sound. Setup precision satisfies `a ≤ 16⌈log₂ p⌉` for every `p ≥ 3`. | Only the size of "eventually" at #4100's `ε = 1−10^−30`. The audit's cutoff condition gives `ln p ≈ 4.3·10⁸` at `ε = 0.9999999`; the same condition gives roughly `ln p ≈ 1.5·10³²` here (my estimate, informational). Merged #4029 (ToikY) covers a different tensor caller. |
| Gaussian conditioning, narrow | #4282; #4283, #4285, #4286; #4319, #4336 | **#4282:** INVERSE-CONDITIONING.md's compression sentence does not cover the circular sections the caller uses. Counting walks inside an arc repairs it. Under the caller's stated gap, bandwidth and row norm, both 2-norms are below `p^10` for every `p≥2`. #4283/#4285/#4286: Schur complements do not keep bandwidth `b` (a middle interval reaches `2b−1`; circular arcs follow arc length), but the inverse bounds survive. **#4319/#4336**, one `p=19` section (survivors `0,1,2,7,8,9`): the normalized Schur inverse has `‖·‖_∞ = 3.6006` (#4319's bracket) and `‖·‖₁ = 2.8138` (#4336), against INVERSE-CONDITIONING.md's ceilings 27 and 3938 at #4317's tight gap. The 1-norm ceiling is about 1400 times loose there. | Whether the row-gap hypothesis itself holds (see the row-gap row below). Whether GAUSSIAN.md's `O(W)` Schur bandwidth at the actual carve matches #4285's `2b−1` cap. Not checked here. |
| Gaussian conditioning, broad | #4193; [#4191](https://github.com/CrocSwap/integer-mult-bounds/discussions/4191) | A tightening, not a defect: the capped broad inverse allowance improves from `p^6` to `p^(1+ξ+o(1))`. | Its truncation-perturbation condition at the caller. |
| Narrow row-gap estimate `‖N−I‖∞ ≤ e^(−2aθ)+5e^(−2a)` | Retained proof: [PR1673 LOG-A-PHASE-SCHUR-AUDIT.md §1](../../research/capped-phase-fusion/LOG-A-PHASE-SCHUR-AUDIT.md), valid for every `θ>0` and counting the periodic aliases. It is re-derived independently in that package's [lineage review](../../research/capped-phase-fusion/evidence/independent_fusion_review_ultra/gaussian_layout_review.md) and in the merged `pr1786-fine-prime-transfer-audit`. | Positive. The `1/(8p²)` margin holds for every `p ≥ 1` (checked exactly to 5000), and the column analogue is proved. #4304–#4309 are `p=19` instances of the shifted interior kernel `exp(−aρh²−2aβ0h)`, not of `N`'s rows; with a centred chirp one entry exceeds 1 (#4304). | An explicit statement that alias removal, band truncation and rounding keep half the gap (PR1786 asserts this in one sentence; #4217's open question 1). Which chirp origin the interior caller uses. |
| Shallow interior and tensor circuits | #4198, #4205, #4209, #4220; [#4196](https://github.com/CrocSwap/integer-mult-bounds/discussions/4196), [#4202](https://github.com/CrocSwap/integer-mult-bounds/discussions/4202) | Positive scoped results: exact rational Stein generators (#4198), rounded words executed against shared finite-core references (#4205), same-ρ Schur closure for the parity-triangular child (#4209), and an independent scalar-enclosure oracle (#4220). | A full tensor-circuit cost. Each PR lists its own remaining hypotheses. |
| Boundaries and current sparse values | #4186; [#4182](https://github.com/CrocSwap/integer-mult-bounds/discussions/4182); union schedule: merged PR2578 ([`pr1731-union-rect-review`](../../research/pr1731-union-rect-review/README.md)) and #4327 | Positive. The rounded block-solve error at gap `1/(16p²)` has no factor equal to the number of row blocks (#4186). For the union schedule, PR2578 reviewed its operator and volume identities on the predecessor text; #4100's copy changes only the numbers in §5b. #4327 checks §2.3's head accounting and the variable-length transpose on a literal multitape simulation: per round at most `17·RW·N·(⌈log₂g⌉+⌈log₂a⌉+1)` plus bit terms, with exact Kronecker results and complete-line checks. Rewinds over stale cells break the bound. | The boundary-arithmetic row-field movement on the same tape model, and the record header width. The union row has slack ≈ 0.406. |
| Position-dependent halo corrections | #4217 | Positive, with a minor slip. The locality witness has the exact radius `(2J−1)W`. The core error constant should be `2g`, not `g`; the `2^−Cp` margin absorbs this. | Charging the source-driven enumeration when an address lies in many rectangles (#4217's open question 2). The halo ledger rows. |
| Common-grid precision at the Gaussian caller | #4178; [#4175](https://github.com/CrocSwap/integer-mult-bounds/discussions/4175) | See #4178 in the complex recursion row above. | The author's response. |

### BIT supplier, fallback and fixed-tape cost (BIT.md, NORMAL-FORM.md, FALLBACK.md, PROOF.md)

| AUDIT.md obligation | Open audits | Reported outcome | Still open |
| --- | --- | --- | --- |
| A specified odd prime `q=2^89−1` | None found | n/a | An independent check of the 20-node Lucas certificate. Low priority: `2^89−1` is a known Mersenne prime. |
| Local-ring split ranks | #4215 | Positive. The normal-form identity holds over every commutative ring, with exhaustive checks on small rings. | The `f>1` fiber argument was not executed. |
| Good and bad packets at every width | #4227, #4228; #4239, #4246 and successors | A sharpening, not a defect. Exact good-header fractions are given for every rank. The bad fraction is below `(r+1)/q`, so each request fits `43/(2^89−1)`. They hold only for *complete, equally weighted* header covers; a restricted cover can be entirely bad. | **Binding the count to the actual emitted header stream** (#4215's open question 1, #4228's open question 1). |
| Fallback child bound | #4237; #4247, #4262; #4235, #4245 | The 49,911-child bound is valid but not sharp: the sharp maximum is 33,269 at `m=64`, `f≥2` (#4237). The conjectured rank-dependent bound is refuted (#4247), and the excess is unbounded (#4262). #4235 is an alternative pivoted fallback with at most `1+12r` children, with #4245 bounding pivot policies. | Which headers actually reach the fallback in the BIT recurrence. |
| Weighted leaves and fast header routes | No #4100-specific audit. BIT.md reuses PR2915's reached call sites; see the [physical contract map](selected-bit-physical-contract-map.md) for that lineage's review status. | n/a | BIT.md's two completed stages that use the preceding stage at both reached primitive sites, at the new `c`. |
| Row stock, whole high packets and fixed tapes | No #4100-specific audit. BIT.md cites the PR2809 block construction, which is still partially reviewed ([caller and storage map](selected-bit-caller-storage-map.md)). | n/a | Divisible stock, depth induction, complete-field preparation, encoded state and geometric work accounting. #4228 and #4235 exclude these explicitly. |
| BIT recurrence moment at the retuned `c = 8667/5,000,000` | #4330 (certified, independent of #4100's engine); #4171 checks only `a1`, `a2`. | Positive. `μ_1` is exact and equals the ledger. `μ_(1−c) < 0.99999991163325597` (margin `> 8.8·10⁻⁸`, enclosure width `< 10⁻³⁰`). The root `c*` lies in `(0.0017334270, 0.0017334271)`. One extra rank-1 child in `H` breaks the inequality, and the stage algebra and body-word states hold exactly. #4330 also binds `H`, `W` and the `ηF` surcharge to the selected BIT supplier, and its root reproduces the selected `bit_lower` within `10⁻²⁰`. | None beyond the selected record's own cold replay. |
| Chirp generation | #4320 (the identity); #4325 (the tariff) | Positive. The chirp identity holds for all `x, z` exactly when `s·t` is even, so PROOF.md's even-`t` condition suffices (#4320). With literal four-tape head counts, table travel is `≤ 31·TP` uniformly in `d` under the factor-two radix premise, with fewer than two products per record and error `≤ (2d−1)√2·2^(−P)` (#4325). A per-record `d`-scan and skewed radices both fail. | Table setup cost, and interleaving with the packed payload records. |
| Input order and exact recovery | #4320 | Positive. The address isomorphism (equal to CRT.md's root map), synthetic convolution, Gaussian identity and factorization, dilation commutation and recovery inequalities all hold with PROOF.md's normalizations. `T < 2^b` holds from `b ≥ 8`. A presentational note: the carry scan must flush a final carry when `S = 2Ndigits − 1`. | The `2^-4p` precision constant. Invertibility of `N` follows from the retained row gap (see the row-gap row above). |
| Strict powers and logarithms | #4171 | Positive. A second implementation shows every paid-power and side-condition slack strictly positive, and all five obsolete routes still rejected. | None within the ledger; the ledger does not validate the constructions. |

## Shortest list of unaudited obligations

At this check, nothing audits the following: no open PR or discussion, and no
merged audit of byte-identical lineage text. All lie on the critical path of
the written theorem.

1. BIT.md: weighted leaves and fast header routes, and the row-stock,
   whole-high-packet and fixed-tape induction, at the new `c`. Their PR2809,
   PR2899 and PR2915 lineage is partially reviewed; start from the two BIT
   scope maps.
2. PROOF.md: the `2^-4p` precision constant. Its algebraic identities are
   audited in #4320 and its chirp head-travel tariff in #4325.
3. GAUSSIAN.md: the boundary-arithmetic row-field movement. The union
   schedule's algebra is reviewed in the lineage, and its head travel in #4327.
4. CRT.md: the full uniform `E(p,ell)` evaluator from CRT data. The repair
   tariff is audited in #4328.
5. COMPLEX.md: the arbitrary-f lift's complete-cover execution and physical
   placement.

**Correction, 2026-10-21 08:20 UTC.** Earlier versions of this map listed
the fine-prime interval and the all-size narrow row gap as unaudited. Both
have merged lineage audits of identical or cited text: PR1673's LOG-A §1 with
its review, and `pr1786-fine-prime-transfer-audit`. The first search covered
only open records that cite #4100, so it missed them.

Name one proposition and its actual caller before starting; the card asks for
one quantified implication. Search again first: this list goes stale quickly.

## Exact heads at the check

| PR | Author (GitHub) | Head |
| --- | --- | --- |
| #4169 | kumagi | `835c3563ee7ede8ceaf329ede7372e50f7823136` |
| #4171 | petalas | `a3be6becf547c5c7657446843b59fdb50e655eac` |
| #4174 | kumagi | `5fec853f0c048871de3b8098d1e30d4ee19cda23` |
| #4178 | jmbarrancoml | `3e69c9360f609bdbf3617d35ea44f497f5506f93` |
| #4180 | yssite | `15a4153e734a8d1d485c6d3bea9b1a8201328a4c` |
| #4184 | ToikY | `94b9ca9cf59ea6de346a59c92b414454bdde1de4` |
| #4186 | jmbarrancoml | `a20501df8fc07f5ceb32e6fd64bce9ad8fe594bf` |
| #4187 | ToikY | `45fc0750436ae5cc14b95fba81c030a3d7df3412` |
| #4192 | ToikY | `519d811cc48693ad9969d6d7994bef3940167005` |
| #4193 | jmbarrancoml | `52e962e318423be1fe8ed9d705dba92067795b61` |
| #4195 | ToikY | `19cf7a065115d28dd8ee37c0fb4b626d8ddf289a` |
| #4198 | jmbarrancoml | `e457d5e912a27307d725827aeca7198169320b84` |
| #4201 | ToikY | `4f49743a9df0cf7501cdc62bd5707a122fa071e9` |
| #4205 | jmbarrancoml | `78c72e563173f3822fcb4efed9ceeccf05630258` |
| #4208 | ToikY | `fb1f3c84535f3e5138bd07e7ed2f211f08fc296d` |
| #4209 | ToikY | `ccc33bfde8baadef7979fac81e28c0a6f6f278c4` |
| #4215 | petalas | `06e7762684bd6342c9b6bd12e8cd414174f09d17` |
| #4217 | petalas | `d2479b3606beeb745c19210219acdd96967bf8eb` |
| #4220 | ToikY | `5cf23ba47a28b78a98eb0665177b5030e65c01b9` |
| #4227 | petalas | `3d793eade8de2ba49ec08f8d004c1b2f566a78e6` |
| #4228 | petalas | `bb25dcedb5bbbacd3c35359eb6b5488b087bcde6` |
| #4235 | petalas | `27f1ce44126cb3a841756834649f556de0ce00e9` |
| #4237 | petalas | `34af2cd420ccf5339ce05e3aefe5c569aaf17f85` |
| #4239 | petalas | `5e24dfb5463d540721687d92c369609da5589523` |
| #4245 | petalas | `b55d08ec08b08bea170aea5b28e33c81411365c9` |
| #4246 | petalas | `a2d99d73bf21b39fbb0a9a88917424ff26c2e63c` |
| #4247 | petalas | `1ed4cf2ed0da7946a06587901356927a5c11c8ca` |
| #4262 | petalas | `3f4767099a29dd8a528d0a0932ab67010255aabf` |
| #4282 | jwr404 | `c63dc63a5df57c7c602f58f2d36dac835f8116dc` |
| #4283 | jwr404 | `c24b40b144fea80619177347a0033958bda0ffc4` |
| #4285 | jwr404 | `dfeb6fa00c47a7d7b3f0cf01ee4e01f7f7576556` |
| #4286 | jwr404 | `daef9f3c26596371731226dc71bfd52c7f3b90a9` |
| #4304 | jwr404 | `32255e82b3e79ed48c0bcd70a80e4ffaeadb412b` |
| #4305 | jwr404 | `3436fb8f75faee31c4632e72217dd3102933ed25` |
| #4307 | jwr404 | `e59ae5559aaf4c9db60b61067ff1c50c5120dd32` |
| #4308 | jwr404 | `8421ce3dec790743cc59c701eedc6746d9a6ce68` |
| #4309 | jwr404 | `106e26e3c0f62a6e0017afb0a72fc81bd20271fd` |
| #4320 | pinterbanget | `178986e09670a5607794202339a3ce87dbfcdb74` |
| #4321 | unpaidmoon | `05ff71ae097fe5cf19894beb83178cac442bbd35` |
| #4325 | pinterbanget | `404e307ccb29a854e1f0a34289c86c4bf2a7dd7b` |
| #4327 | pinterbanget | `a020d6c25cb9201d19bebdf0ab5675b780a3caa2` |
| #4328 | pinterbanget | `b3ea5ee525b131273d190747b892e5f3667d286f` |
| #4329 | pinterbanget | `a3b9095c536c404e11d2ed868699fc4fcd4d4f57` |
| #4319 | jwr404 | `5373e431733ab14f5741adf88b500279ed35a984` |
| #4330 | pinterbanget | `b5b72817d7b3a85a1125d5b203e0922fcf4930b3` |
| #4336 | pinterbanget | `2d2ea7bd2ae310a50cf29d0a6fe989b4336b891b` |

Header-law successors to #4239/#4246 (#4240, #4259, #4261, #4273–#4275, #4278)
answer counting questions that #4228 raised. They change the card's scope to
new theorems and do not audit a #4100 premise, so they are omitted above.
#4268 quotes #4100's exponent only for comparison, and #4270 is a separate
conditional transfer. Neither audits a #4100 premise.

## How this map was built, and its limits

1. `python3 scripts/find_overlap.py --task uniform-transfer-audit` refreshed a
   complete snapshot at 06:50 UTC: 419 open PRs and 3,174 discussion records,
   with complete pagination.
2. I kept records citing #4100, `unconditional-batched-crt` or a #4100 proof
   file, then read every matching PR body and its limitations section. Any
   PR citing a #4100 author or file without the number was checked by hand.
3. `gh pr list --state closed --search "4100 in:body"` found one closed PR,
   #4165, which records an idle cost and does not audit #4100.
4. I fetched every head above with `gh pr view` at the check time. A final
   refresh just before this PR opened, at about 06:57 UTC, found one new
   related PR, #4309, now included. A refresh at 07:42 UTC found no new
   #4100 audit other than #4320.

The limits:

- This map summarizes PR bodies. It does not read package contents.
- A "None found" entry means no matching open record existed at the check
  time. It is not a novelty guarantee: discussion-only claims may still exist
  without the keywords searched.
- Rows are assigned by the AUDIT.md premise each PR names. A PR touching
  several premises is listed where its main result applies.

Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5)
assistance, 2026-10-21. Apache-2.0. All mathematical results belong to the
cited authors. #4100's construction and AUDIT.md table are by Cinna Davis with
OpenAI Codex assistance.
