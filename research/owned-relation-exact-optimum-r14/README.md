# Exact owned-relation optimum on the #4610 word, and the #5413 caller re-funded at κ = 0.0030272882389

This package has two parts.

**Part A (numerical; compiler headroom only).** The complete #5413 caller, its invoice, its height carrier and
its precision proof stay unchanged. Re-funding it inside its own reserve gives conditional
**κ = 30272882389/10¹³ = 0.0030272882389**, tested at **0.0030272882489**. This is
**3.9 × 10⁻¹²** above the selected #5413 value 0.003027288235. The recursive economic gain is
**zero**. No paid job, target, word or compiler parameter changes, and the raw moment is identical. The
result uses part of the 1.5 × 10⁻¹¹ gap between #5413 and the fixed-profile ceiling U = 0.00302728825
(#5409). It stays below U.

**Part B (exact; negative for further relation gains).** We solve exactly for the best owned
helper-relation subspace on Cao Yifan's #4610 word, in both orientations. The search space covers:

- relation sets that omit #5383's eight relations, which is #5433's open question;
- pivots on the 26 rank-4 and 6 rank-8 frame-0 helpers;
- rows that carry warp words.

The optimum is **8 (8^t + 1 − 9^t) = 0.07570927 raw moment per backward local**, and #5383's span
attains it. It is an optimum, not the unique one. Replacing component 194 by 207 (the relation
h288 − h294 − h296 − h297 + h300 + h303 = 0) gives a different eight-dimensional space with the same
value; zxv found this tie in review, and `relations.py` checks it as a regression. The forward optimum
is 0. No ninth relation and no better joint set exists. The 144 exchanges of the
#5398/#5413 controller are the maximum.

## Part B: model and certificate (`relations.py`)

The model is #5377/#5383's, as generalised by #5433. Helpers starting in the common input frame 0 are free
inputs. There are 358 of them: 326 have rank-9 targets, 26 have rank-4 targets and 6 have rank-8 targets. A
relation subspace V consists of linear forms in these inputs. Each dimension owns one pivot helper, which
loses its productive target.

- A paid climb is free iff its row vanishes on the restricted domain.
- Rows are replayed exactly over Q in the free group ring of warp words. A row therefore vanishes iff, for
  every warp word, its coefficient vector (its *component*) lies in V.
- A centre job is free iff `row(centre) − row(snapshot)` lies in V.

| Check | backward | forward |
|---|---:|---:|
| helper-only paid climbs | 224 (166 word-free, 50 two-word, 8 three-word) | 358 |
| distinct components, linearly independent over Q | 225 | 358 |
| centre snapshot options (all in the component span, rank-9 support) | 56 (8 centres) | 0 |
| connected pieces (components joined by climbs/options) | 110×1, 1×3, 8×7, 4×14 | 358×1 |
| exact optimum per local call | **8(8^t+1−9^t)**, attained by the span of #5383's relations (not uniquely; see the 194→207 tie) | **0** |

The certificate has four steps:

1. WLOG V is the span of a set S of components. An option outside span(S) adds a dimension with a rank-9
   pivot, which costs 9^t, more than the 8^t it can save.
2. Since S is independent, any pivot set has a perfect matching to S inside the supports (Laplace expansion).
   The lost target moment is therefore at least Σ_{c∈S} min-target(c)^t.
3. Each centre's seven options are supported on its zero-site rank-1 climb plus at most one private climb.
   These supports are disjoint across centres.
4. Each piece (at most 14 components) is enumerated exactly with 60-digit Decimal powers.

This extends #5433 in three ways. It covers sets without #5383's relations, cheaper pivots and word-carrying
rows. The ILP cross-check below also covers off-frame helpers, which are outside the admissible construction.
A side check with HiGHS on all 408 helpers, including helpers in non-common start frames (332 rows, 4 disjoint
circuits), gives the same optimum. That check is not part of the registered replay.

## Part A: what changes and what is reused (`endpoint.py`)

1. Authenticate all 63 capsule files of `research/coupled-helper-neutral-completion` against its
   `SOURCE-BINDINGS.json`, whose SHA256 its `verify.py` pins. Copy them into private scratch.
2. Rerun #5413's invoice/funding engine with only its two endpoint literals substituted. The regenerated
   invoice equals #5413's expected invoice. Funding passes all endpoint predicates and the 54 strict plus 4
   functional outer predicates.
   - The gap stays 1/7·10¹¹, the height grid stays j = 55099 and H = 38569300000000000.
   - The fields that downstream checks read are identical: paid and target profiles, reserve 10⁻¹², tuple,
     BIT stock and controls.
3. Rerun #5413's precision checker on a manifest whose funding row points to the new receipt. Its output
   equals #5413's expected precision receipt except the manifest hash. The written precision proof is
   symbolic in N = 2^H and uses only H, j and the gap, so it applies unchanged. Its §8 sentence naming the old
   pair is the one textual difference.
4. Rerun #5413's 25-premise conjunction with only the endpoint-gate literals moved to the new pair: PASS,
   25/25.
5. Controls:
   - #5413's unsubstituted conjunction rejects the new funding.
   - Tested values .00302728825 and .00302728824898 fail `funded_alpha_reserve`.
   - A non-unit gap fails the height grid.
   - Brackets, computed with #5413's directed engine:
     - raw root ∈ (.0030272882499, .00302728825);
     - reserve-limited tested saving ∈ (.00302728824897, .00302728824898).

At the same carrier, the reserve-limited maximum is κ < 0.00302728823898. The chosen κ is 8×10⁻¹⁴ below that
bound; against the certified bracket it sits between 7×10⁻¹⁴ and 8×10⁻¹⁴ below the actual reserve-limited
maximum (corrected from 8×10⁻¹⁶ after review). A smaller unit gap, such as 1/7·10¹² (κ ≈ 0.0030272882479), also passes the endpoint arithmetic. It
would change H, however, and #5413's precision checker pins the gap. It is not claimed here.

**Assumptions.** The κ is conditional on exactly the five retained selected premises of #5413:

- native all-column operation;
- owned erasure;
- the compiler contract;
- precision/tape;
- analytic recovery.

No unconditional theorem, formal-kernel acceptance or κ-maximality is claimed. On macOS, `endpoint.py` skips
the precision checker's `RLIMIT_AS` call, which Darwin cannot lower. Linux runs that checker byte-unchanged.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/owned-relation-exact-optimum-r14
python3.12 -I -B research/owned-relation-exact-optimum-r14/relations.py      # PASS_OWNED_RELATION_EXACT_OPTIMUM_EQUALS_5383 (~3 s)
python3.12 -I -B research/owned-relation-exact-optimum-r14/endpoint.py       # PASS_5413_CALLER_REFUNDED_AT_KAPPA_0.0030272882389 (~10 s)
python3.12 -I -B research/owned-relation-exact-optimum-r14/test_controls.py  # PASS_OWNED_RELATION_EXACT_OPTIMUM_CONTROLS
```

The registered replay also reruns #5413's full `verify.py`, which Part A depends on.

## Open next questions

- Can a changed paid profile on the #4610 word fund κ above the fixed-profile ceiling U = .00302728825, rather
  than a relation exchange? Relations are now exhausted exactly. The endpoint headroom left at this carrier is
  below 1.1×10⁻¹¹. First step: price one candidate histogram change with `scripts/compare_recursive_invoices.py`
  before building a word.
- Can a precision proof that is parametric in the gap admit a finer unit gap? A gap of 1/7·10¹² would add about
  9×10⁻¹² more, and it is numerical only.

## Credit

- Cao Yifan (intqwq) supplied the #4610 word.
- Ali Romman (aliromman) supplied the owned-relation method and its successors:
  - #5377, the first owned relation;
  - #5383, eight joint relations;
  - #5392, owned circuit transposition;
  - #5398, the direct backward caller;
  - #5421, nine BIT relations.
- Dillon Amburgey (dillona) supplied the #5402 coupled provider.
- Chris R (Clear1nsight) supplied:
  - the #5413 complete caller, its funding engine and its conjunction;
  - the reviews #5384 (owned-relation price ceiling), #5395 (eight-relation price plane) and
    #5396/#5399/#5400/#5407/#5414.
- Dugongue supplied #5387/#5390, the reserve refinements.
- Mark (Matarener) supplied #5433, the relation-subspace certificate and open question that Part B answers.
- #5409 supplied the fixed-profile ceiling U.
- Lineage credit is retained for Cinna Davis, zxv, Jacob Alan Sussman (mixed-target paradigm, #4359) and the
  native, compiler, BIT and analytic predecessors.

Prepared by Joel Pulikkan (GamingPuzzled). AI disclosure: Claude Opus 5.5 (Anthropic) via Claude Code,
directed by Joel Pulikkan (GamingPuzzled). New material is Apache-2.0.
