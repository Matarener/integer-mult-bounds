# Price CRT switch layers by occupied color

**Scoped tariff lemma. No new κ.** The selected conditional exponent stays
`605457647/200000000000`. #4100 is not accepted.

## Result

CRT.md §4 colors active targets by position modulo `K` and charges a switch
layer for `O(K)` colors. The macro that paragraph prices is one occupied
color. For every batch cut by the pinned #4174 layout,

```text
c ≤ r ≤ r_max.
```

Here `r` is the number of active targets, `c` is the number of distinct
residues modulo `K`, and `r_max` is the layout's batch cap. Empty residues
are not macros. Two targets exactly `K` apart are one macro.

At `d = 65536`, `ell = 24`, and alternating widths `24/23`, with the
constructor call `p = 6L` used by `research/pr4100-guard-coloring`, the
parameters recompute as `L = 1540096`, `K = 196608`, `r_max = 5`, and
`H = 15360`. The §4 color factor may be `5` instead of `196608`. The ratio
is exactly `196608/5`. The all-short width `23` row recomputes as
`r_max = 4` and ratio `49152`.

The proof is in [PROOF.md](PROOF.md). The singleton-color hypothesis in the
predecessor's open question is sufficient but not necessary: the batch cap
already forces `c ≤ r_max` when a color collides.

## Scope

Task card `uniform-transfer-audit`, priority revision 7, base
`32890bc5de034ab8fc93ac88ead7279a6a416d04`. Scope status is **refined**.

The card asks whether one quantified step of #4100 holds at its caller.
This package prices the occupied-color factor in the CRT.md §4 layer
sentence. It is item 12 of the ordered list below.

Ordered eligible list for session r44, rebuilt on 2026-10-25 against
`32890bc5de034ab8fc93ac88ead7279a6a416d04`. Open handoffs from the 19
October index come first. Answered handoffs are dropped. Priority-table
rows come next, and inside `uniform-transfer-audit` the still-open
successors follow the order recorded in
`research/pr4100-ledger-boundary-exponent`: the first still-open successor
of an answered row, then the second. A row is dropped when a merged
package, an open pull request, an excluded unpaidmoon delivery, or a fork
`cursor/*` branch already answers it.

1. A caller that accepts `(w, q, v_N)` without restoring the original source
   slots (discussion comment 19030045).
2. Whether the PR2809 continuation serializer parks the ancestor chain or
   one root-sized stream per cut.
3. Whether marker, template, and erased-backing cells sit inside the
   `26041 V` budget.
4. Whether the stored narrow band has at most `2p` off-diagonal entries and
   the rounding meets `2^{-5p}`.
5. Whether a byte-identical `outer/check_ledger.py` regenerates the
   `tau_eff` point.
6. Whether the word-level scalar inventory fits constant one at the two
   excluded `p = 2` corners.
7. Whether the full-batch allowance composes with reservoir placement and
   the paid repair-key service.
8. Whether the normalized 1-norm stays below the infinity norm on longer
   Gaussian paths.
9. An explicit `C` and `k` for `mu ≤ C (W/B) (log p)^k`.
10. A physically costed producer for the 32-bit CRT source ROM.
11. The control cost of the joined producer, scanner, and repair.
12. **This package.** Macros per occupied color, bounded by `r_max`.

Dropped before this cut: the fresh T385 wrapper, the six-tape head-move
bill, the retiming handoff, the four-provider rebind, the matched
park/restore comparison (open #4167 and #4172), the literal `evaluate_key`
tape service, the separator-corner enclosure and its immediate Neumann
readings, the stack `O_q(V)` claim, and the printed `tau_eff` choice.
Catalogue cards already closed by this account, including the rank-8
producer, the difference-basis census, the compact-switch audit, and the
stock, replay, packing, and scalar-itinerary cards, stay off the list.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3 -B research/crt-occupied-color-macros/verify.py
python3 -B scripts/research_package.py --package research/crt-occupied-color-macros
```

`verify.py` prints

```text
PASS_CRT_OCCUPIED_COLOR_MACROS K=196608 r_max=5 ratio=196608/5 uniform23_r_max=4 ratio=49152 same_color_pair_macros=1 no_new_kappa=true
```

It hashes CRT.md and the layout allocator, checks the §4 sentences, exhausts
the `2^12` subsets of a 12-point universe at `K = 6`, and recomputes both
production rows. Not run: the 104,864-plan census, Lean, Docker, and the
selected cold replay.

## Open next questions

1. Can §5's `ell^2 polylog p` line be rewritten with `r_max` in place of the
   hidden `K` factor, and does any later numerical budget use the looser
   factor? The first step is to expand `O(log d)` levels times `O(ell)`
   layers times `c ≤ r_max` colors. The blocker is that §5 does not display
   `K` as a separate multiplier.
2. Does one same-color macro's repair bill stay inside the one-color `O(V)`
   when that color holds two targets? The first step is the bad-density line
   at `r = 2` and this `K`. The literal many-target tape macro is still
   unpinned, so this question does not ask for that program.

## Credit

The coloring, the `O(K)` layer sentence, and the one-color cost are Cinna
Davis's #4100. The batch cap `r_max = L // (100 G)` is Hiroki KUMAZAKI's
#4174 layout, as vendored by Ryanson Jonathan in
`research/pr4100-guard-coloring`. That package leaves the occupied-color
price open and proves the `(K−1)`-bit guard lemma cited here. #4321
(unpaidmoon) stated the disjoint-guard hypothesis that package decided.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No independent human review and no formal-kernel acceptance are claimed.
