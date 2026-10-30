# G20 MAIN-bank target ranks

**Independent finite source-bound audit; no new bound or supplier admission.**
This answers open question 2 of Matarener's [PR5955](https://github.com/CrocSwap/integer-mult-bounds/pull/5955),
head `52115896549090117a3f3101b17106cad4466408`. Every one of the 3,552 MAIN
owners in each PR5679/PR5708 inventory agrees with a rank derived from its
retained controller. The MAIN rank mass is 154,290 in each candidate.

| Address-projector rank | MAIN targets per candidate |
| --- | ---: |
| 15, 22, 29, 36, 43, 50, 57 | 444 each |
| 64, 127 | 222 each |

## Derivation and its contract

The retained source proof describes a central line and eighteen disjoint
seven-dimensional stage spaces. The ambient address space is their direct
sum, of dimension 127. Let z reflect the central line and let x_s reflect
stage s's block, acting identically on every other block. These commuting
involutions are the stated controller model, not newly admitted primitives.

The checker first reconstructs all 32 labeled output polynomials from the
154 physical events and both boundary programs. Coefficients are in F2;
each term retains its original input-bank label. ADD is symmetric difference,
SWAP is three ADDs, and multiplying an involution toggles its monomial bit.
A LOCAL event applies the central shear and its stage factor; IDLE applies
its listed stage factors. Every off-diagonal coefficient must cancel, and
each remaining diagonal monomial must equal the source declaration. No
predecessor Python module or rank routine is imported.

For a surviving monomial z times the product of x_s over S, evaluate its
sign on each of the 127 coordinate basis columns. It is negative exactly
on the central line and the disjoint blocks indexed by S. Thus
P = (I - R)/2 is diagonal, with an identity minor on those columns and all
other columns zero. Its rank is exactly 1 + 7|S|. The code evaluates the
signed columns and cross-checks this formula rather than trusting a target
rank or the controller's invoice. This rank is the **address projector's
native job rank**, not the rank of a full FUNCTION permutation matrix.

Every bank has 111 ports. For each MAIN descriptor, the checker verifies
owner = 111*bank + port, uniqueness, complete owner coverage, its individual
rank, both candidate invoice histograms and the controller's MAIN histogram.
Both retained controllers are byte-identical. The full per-bank list and
15 rejecting controls are in [RESULT.json](RESULT.json).

## Scope, evidence and reproduction

Base: `e21a287a7c4883c24cec069113ac7cfd5efcb3ca`, priority revision 8.
PR5679 source head: `715dda75fc4cefb1e492349fa0e331d5f15d0f53`.
PR5708 source head: `829d01fc031f7323ffcfa423fdfd1f24dcbe3190`.
Exact retained source paths, Git blobs and SHA256 pins are in SOURCES.json.
The verifier authenticates every live input before parsing it. TASK.json
records the explicit refinement from the current BIT card.

```sh
python3.12 -B scripts/research_package.py --package research/g20-main-target-ranks
```

Expected marker: `PASS_G20_MAIN_TARGET_RANKS`. Each registered command has
a 60-second timeout and uses only the standard library. Normal and optimized
commands recompute the result and reject changed diagonals, missing or duplicate
stages, wrong ambient dimensions, changed boundary gates, unknown opcodes,
wrong target ranks/ports/owners, operator labels or route obligations, an equal-rank bank alias, missing targets,
a count-and-rank-mass-preserving invoice change, and changed source bytes.
`--write-result` explicitly regenerates RESULT.json; ordinary replay writes
no package artifact. Semantic controls operate on copies after authentication.

This closes only the source-relative MAIN rank input, including the formal
controller endpoint that PR5955 did not replicate. It does not reprove the
physical orthogonal-block realization, native all-column/whole-job adapters,
FRAMES geometry, OWNED erasure, paid query ranks, global stream, finite fees,
compiler, precision/tape, modulus domain, ordinary-to-admitted BIT conversion
or outer assembly. The five framework assumptions remain. No selected record,
frozen predecessor or original invoice is changed. Independent human and
formal proof-kernel review are unclaimed. Hosted CI is separate from local checks.

## Open next questions

Bind one actual MAIN bank's physical projector and whole-job adapter to its
all-column, arbitrary-spectator contract. This matters for physical admission;
start from the exact coordinate action above and its retained native wrapper.
The inherited native/compiler/precision obligations require a separate audit.
The structured question and blocker are in TASK.json.

## Credit and overlap

Matarener supplied the independent review and explicit open question. Ali
Romman, Dugongue, ai-nanachi and the retained G20 controller/native lineage
supplied the constructions. JoyboyBrian's earlier bit-paid-owner-binding
already emits productive ranks from the supplied controller diagonal; this
package adds a separate complete polynomial reconstruction and current
per-owner comparison, rather than claiming the rank formula is new.
DreamingOfClouds, eumemic, Cinna Davis and the retained compiler/ownership
authors keep their original attribution; no predecessor source is copied.

Remote overlap refresh covered 315 open PRs, 5,221 closed PRs and 5,694
Discussion records. Sparse local notes covered 7/8,346 paths; exact-gap
searches of pinned Git notes and relevant older owner-binding code supplement
that limited coverage. No competing exact-gap derivation was identified;
this is not a global novelty guarantee. Coordination:
https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19231258

New checker and exposition by Dennis / antunishdPursuit with substantial
OpenAI Codex assistance, no subagents. Apache-2.0. Orthogonal direct sums,
reflection projectors and rank by an identity minor are standard methods.
