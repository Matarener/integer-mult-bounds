# THREE-base supplier: independent paid-event census

**Finite accounting audit; no new kappa.** The supplier-census question left by
[Ryanson Jonathan's #4426](https://github.com/CrocSwap/integer-mult-bounds/pull/4426)
is answered for its pinned THREE-base word. Separate standard-library code
recovers the unsplit paid histogram

```text
{1:2487, 2:713, 3:224, 4:102, 5:20, 8:8}
```

in both orientations: **3,554 paid calls, rank mass 5,157**. The 408 nested
helper frame increments give `{5:28, 6:18, 7:56, 8:93, 9:213}`, rank mass
**3,301**. These agree exactly with the supplier receipt used by #4426.

This closes its finite census handoff, not the supplier's operator or physical
correctness obligations. Evidence is an author-executed, separately implemented
check; no independent human or proof-assistant review is claimed.

## What is reconstructed

The native input actually contains the **split** centers, with 22,633 events
and paid profile `{1:2487, 2:713, 3:232, 4:102, 5:28}` in each direction.
Its 16 center events form eight consecutive pairs. Their frame dimensions are
`8 -> 3 -> 0` forward and `0 -> 3 -> 8` backward. Coalescing each pair recovers
the unsplit program's 22,625 events without changing any scalar or warp event.

The resulting paid census, identical in the two orientations, is:

| Phase | Rank 1 | Rank 2 | Rank 3 | Rank 4 | Rank 5 | Rank 8 | Calls | Rank mass |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A | 950 | 12 | 20 | 38 | 0 | 0 | 1,020 | 1,186 |
| Centers | 0 | 0 | 0 | 0 | 0 | 8 | 8 | 64 |
| B | 1,161 | 571 | 150 | 64 | 20 | 0 | 1,966 | 3,109 |
| Cleanup tail | 72 | 53 | 0 | 0 | 0 | 0 | 125 | 178 |
| Final | 304 | 77 | 54 | 0 | 0 | 0 | 435 | 620 |
| **Total** | **2,487** | **713** | **224** | **102** | **20** | **8** | **3,554** | **5,157** |

For the 15 native invocations inherited from Cinna Davis's #4416, the supplier
part alone is `{1:37305, 2:10695, 3:3360, 4:1530, 5:300, 8:120}`, rank mass
77,355. Controller idles are additional. This multiplication by 15 is arithmetic;
#4426 retains credit for reconstructing the controller, its targets and idles.

## Method and proof boundary

1. Authenticate exactly three inputs against [SOURCES.json](SOURCES.json), then
   require the supplier receipt's artifact hashes to name those actual native
   and canonical bytes. They are already retained on the pinned main branch;
   no unpublished Git object or network fetch is needed for this package.
2. Independently eliminate all 1,159 nine-bit frame bases over F2. Every basis
   must be independent. For each paid transition, compute containment by the
   rank of the concatenated bases and derive the rank difference. The event's
   declared rank is only a comparison target, never the rank calculation.
3. Trace frames on 632 persistent fields and the owned C0 field. Check paid
   entrances, warp entrances, scalar operands, final persistent frames, and
   the final explicit center clear. `adapter`, `residual_adapter` and `phase`
   are markers in the inherited event format; the paid moves they annotate
   appear explicitly as `climb` or `center` events. Scalar and warp costs are
   outside this recursive-child histogram.
4. Verify both literal split programs and coalesce their adjacent center
   pairs. Under the inherited common-frame convention, if
   `T(a,b) = F_b F_a^-1`, then
   `T(b,c) T(a,b) = F_c F_b^-1 F_b F_a^-1 = T(a,c)`.
   Complex conjugation preserves this identity. The shared middle reference,
   immediate adjacency, dimensions and nesting are checked; a scalar inserted
   between the two pieces is rejected. This is telescoping of frame symbols,
   not a fresh check of serialized Clifford phases or a regeneration of the
   original unsplit word from its ancestor.
5. For each helper `L224` through `L631`, independently verify the nested
   entry/exit spaces and count their dimension difference. C0 receives no
   productive credit. Compare the full distributions, not only rank masses,
   to the receipt. Recheck frames and counts on the coalesced programs too.

The verifier imports no repository module and executes no predecessor
interpreter. The source interpreter was read to identify the native format
and tariff. The elimination algorithm, census, center reconstruction, controls
and receipt are separately written. The selected construction already had
native replays; this package supplies additional independent accounting
coverage requested by #4426, not a first proof of the supplier.

## Verification

From the repository root, Python 3.12, standard library only:

```sh
python -B scripts/research_package.py --package research/three-base-paid-census --check-only
python -B scripts/research_package.py --package research/three-base-paid-census
python -O -B research/three-base-paid-census/verify.py
```

The direct verifier recomputes and compares [RESULT.json](RESULT.json).
`--write` regenerates only that package-local result. All assertions use explicit
exceptions and remain active under `-O`.

There are **16 rejecting controls**: source corruption, artifact misbinding,
wrong paid rank, a deleted climb, a same-dimension nonnested edge, stale warp
entrance, wrong scalar frame, borrowed-field clearing, missing/interrupted
center pairs, a dependent basis, wrong final frame, unknown event, two
rank-mass-preserving paid-profile changes, and a helper-distribution change
preserving both count and rank mass. All 512 ordered triples in F2^3 additionally
cross-check elimination against enumerated spans, including dependent triples.

An explicit **coverage probe** changes an ADD sign in memory and obtains the
same census. It demonstrates why these checks cannot certify the operator
identity. Actual input-file changes are separately rejected by SHA256 binding.

## Sources, overlap and limitations

Base: canonical main `2a13eb1827784206202db90e5dc8327cf8a250db`, priority revision
7, selected conditional kappa `23/10000`. Exact input blobs and SHA256 values
are in [SOURCES.json](SOURCES.json); scope and freshness are in [TASK.json](TASK.json).
Coordination: [discussion #4445](https://github.com/CrocSwap/integer-mult-bounds/discussions/4445),
with a pointer replying to the [handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19103994).

The overlap refresh covered all 5,731 tracked local package notes/ledger entries,
301 open PR bodies and 3,290 Discussion records, with complete pagination at
21:05/21:06 UTC on October 21. It surfaced #4426's explicit missing census and
no separate competing census. Closed work was covered through local notes and
the ledger, not a fresh scan of every closed PR body; code diffs are outside
the helper's search. A submission refresh at 21:16/21:17 UTC covered 303 open
PRs and 3,294 Discussion records, with complete pagination and no warnings or
new competing census. Canonical main, guidance and the inputs were unchanged.
The older `t360-local-rewrite-census` searches rewrites of prior words, rather
than reconstructing this full-identity receipt. This is not proof of novelty.
#4441's changed helper word is a different input; this frozen audit does not
certify its invoice.

Not rerun: arbitrary-input operator equality, exact Clifford phases, scalar
primitive pricing/prefix norms, helper physical normalization, the p7 controller,
121-axis admission, tensor/strictification arguments, compiler, precision/stock,
fixed-tape and outer/analytic obligations. The source baseline command was
attempted but could not complete with omitted source-closure directories in
this sparse checkout (`Invalid package root: research/kappa-accounted-composition`).
It is not reported as passing. The targeted inputs are all materialized and
authenticated. The complete `frontier4359-verify` replay was not run.

## Open next questions

No further census question is justified for these exact bytes: both orientations
and the full distributions match, with the stated rejection controls. The
physical/operator, phase and downstream boundaries listed above remain inherited
in this audit. Their absence here does not mean the repository lacks evidence
for them. Consult the selected proof review and live handoffs before proposing
any additional independent check; a changed native word needs its own census.

## Credit

- **Ryanson (Ryan) Jonathan / pinterbanget**, #4426 at
  `6f918e2658c727007611d98ffb8d3c7336e2290c`, for the independent p7 controller
  invoice reconstruction and this explicit handoff; #4420 for the arithmetic audit.
- **Cinna Davis / 1337isnot1337**, #4416 at
  `e9058860b5c850760fdf970e796a96aefcdb1d98`, for the p7 construction and invoice.
- **zxv**, #4359's retained source closure at
  `da637c87c89482bc4c86be36bd0071b3d400dbed`, for the full-identity supplier,
  center split and productive-helper construction. Jacob Alan Sussman supplies
  the mixed-target recursion; David Ganz, Rohan Arun, Cinna Davis, Jeremy Kothe,
  Marius-Paul Dumitrean, Erwan Secousses and the retained native/frame contributors
  are credited in the [checkpoint contributor map](../../docs/research/community-productive4359-contributors.md).

Prepared for **mihir-s-05** with substantial **OpenAI Codex** assistance in
research, implementation, verification and writing. Apache-2.0. Frozen sources
and their attribution are unchanged.
