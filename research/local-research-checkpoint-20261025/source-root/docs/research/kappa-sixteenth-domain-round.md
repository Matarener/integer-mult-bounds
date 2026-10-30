# First bounded round toward κ = 1/16

Douglas Colkitt, with OpenAI Codex assistance. 2026-10-09. Apache-2.0.

**No new multiplication bound, stronger supplier or enlarged theorem domain.**
The selected conditional witness remains `κ=0.000661885549259598`.
This round completes the first dependency map and compares two mechanisms
against the [preparation budget](kappa-sixteenth-preparation.md).

The main finding changes the priority: improving producer/readout boundaries
while retaining today's gross endpoint budget and small-child cap cannot
reach this target, even with all scratch and central losses removed.
Two quantitatively different departures remain: more useful endpoint deficit,
or genuinely larger recursive children. The latter passes an optimistic
numerical screen, but no implementation earns a construction run yet.

## 1. A region of arithmetic slack, not an isolated point

Fix `κ=1/16`, `β=1/100`, and backoff `h=10^-6`. Consider the whole rectangle

`7/100 ≤ a ≤ 71/1000`, `3/40 ≤ b ≤ 19/250`.

The bit wrapper budget from preparation supplies a hypothetical effective
saving `A=0.0740028844925`, above every `a` in this rectangle. Its supplies
are still missing. Throughout this region:

* All **44 exponent-dependent slacks other than the small-domain guard**
  are strictly positive.
* The two finite scalar/row bridge slacks remain separate assumed inputs.
* `1/32−b` is strictly negative. The production checker still rejects.

Here is the algebra behind the exact interval certificate. Set
`q=a(1−2h)`, `ε=(1−h)/(1+q)`, `G=εq`, `r=G+h/2` and `δ=h/8`.
Then `G=1−h−ε`, and the potentially delicate cancellations reduce to:

| Quantity | Exact expression |
| --- | --- |
| Internal saving gap `a−q` | `2ah` |
| Both lambda ordering gaps | `ah` |
| Reservation gap `c−q` | `h/4` |
| Compact geometry `1−ε(1+c)` | `h−εh/4` |
| Normalization `1−ε−r` | `h/2` |
| Small-field gap `1−ε−G` | `h` |
| Cell/band gap `ε−(1−r)/2` | `1/2−G/2−3h/4` |
| Artificial-boundary gap | `8−ε+3h/8` |
| Phase-local / boundary gaps | `G+7h/8`, `G+3h/8` |

Since `b>a`, the internal exponent is `1−a`. The leaf saving is
`(1−β)b`; its worst gap above `a` in the box is `0.00325`.
The seven margins simplify to
`G+h, a, G, a, G+3h/8, G+7h/8, ε`.
Their minimum is `G`: the interval upper bound for `G` is below both
the lower bound for `a` and the lower bound for `ε`.

The [script](../../scripts/audit_sixteenth_round.py) applies exact rational
interval arithmetic to these reduced expressions. It also compares all 47
expressions with the pinned original function at nine points as a transcription
regression. Those point checks are not the proof for the rectangle; the
algebraic reductions and outward interval bounds are. No statement about the
full theorem follows solely from the displayed-slack certificate.

## 2. Dependency map for the larger supplier budget

The following conclusions concern the inspected, repository-retained proof
chain. They do not independently reprove its inherited all-size contracts.
The [receipt](kappa-sixteenth-domain-round.json) records the source hashes.

| Dependency and inspected source | Actual requirement | Finding / remaining obligation |
| --- | --- | --- |
| [Selected assembly](../../research/coordinated-frames-and-entrance-banks/arithmetic/balanced_shared.py), inherited from PR141 and earlier structured/balanced checkers | Explicit `b<1/32` | Still a binding admission guard. The inspected derivations do not derive 1/32 as a sharp analytic threshold. No permission to remove it follows from this search. |
| [Moment enclosure](../../research/coordinated-frames-and-entrance-banks/arithmetic/interval_moment.py) and [bit verifier](../../research/coordinated-frames-and-entrance-banks/bit/prove.py) | Exponential argument below 1/4; complex search upper bracket 1/32, bit bracket 1/100 | Research-only range reduction now encloses larger arguments. New search brackets and suppliers still require independent admission; these numerical limits are distinct from a theorem range. |
| [Stopped bit recurrence and ordinary wrapper](../../notes/stopped-product-interface.tex) | Strict moments at powers 1 and `1−a₀`; `0<a₀<1`; paid stopping and row conditions | The induction uses these contraction gaps, not a numerical 1/32 ceiling. The proposed wrapper has `A<θ<1−A`. A real new weighted compiler, bad-class bill and all-size implementation remain necessary. |
| [Stopped complex recurrence](../../notes/structured-bulk-assembly.tex) | Strict complex moment, `0<β<1`, `(1−β)b>a`, proper children | The potential and geometric sums use positive gaps. The target box provides the exponent gaps; it provides no new moment or tensor operator. |
| [Completed-child precision](../../notes/structured-bulk-assembly.tex), selected [bridge](../../research/coordinated-frames-and-entrance-banks/arithmetic/shared_bridge.py) | `r_max<m`, full scalar bill, `2B(m−r_max)≥s+E`, `C₁=1`, `ε<1` | Saving size is not the precision induction's parameter. Every new word must reprice scalar operations, denominators, maximum child and `C₀`; published constants are not transferable by default. |
| [Arbitrary-source router](../../references/semantic-bulk/rad20/reports/compact-arbitrary-source-routing.md) | Complete ordinary interchange, spectators/restoration, short-record condition `ε>a` | The target satisfies the exponent condition. A changed primitive must preserve the whole contract, not just improve a rank score. |
| [Balanced layout application](../../references/copied-fixed/pr34/ASSEMBLY_PROOF.md) | `K=o(ell)`, `c>q`, `ε(1+c)<1`, paid complete permutations | All corresponding gaps hold throughout the box. The inherited layout proof is still an assumption of composition. |
| [Phase-cell inverse](../../references/semantic-bulk/rad20/reports/downstream-phase-cell-inverse.md) | Eventual `u=Θ(p^r)≥log₂(8p)`, `ud≤p`, `ε>(1−r)/2`, polynomial setup and retained recovery | `r>0`, `ε+r<1` and cell separation hold. The retained checker also requires `r<1/4`, which the target satisfies; no extension of that restriction is needed here. |
| [Bulk microboxes](../../references/semantic-bulk/rad20/reports/downstream-microbox-resampling.md) | Both `p^τ` and `d` exposure terms; `L≈p^8`, halos `≈p^3`, original period cuts | Keep both exposure terms. The historical sentence making the `d` term lower order assumes `ε<τ`, which this box does not satisfy. The complete cost formula already charges it through the `1−ε` margin, so the box does not rely on that simplification. |
| [Prime, setup and row stock map](../../notes/structured-bulk-assembly.tex) | Fixed `0<ε<1`, distinct-prime packing, finite exceptional sets, positive polynomial row-degree gap | The growth comparisons remain eventual at these exponents. A different dimension, denominator set or recursion depth requires new prime and stock certificates. |
| [Explicit cutoff routine](../../research/coordinated-frames-and-entrance-banks/references/pr141/balanced_stopped.py) | Positive gaps and construction-specific `C₀`, maximum dimension and row suffix | The displayed comparisons admit finite thresholds once these constants are supplied. The old routine has an older bridge schema; it is not an executable cutoff certificate for a hypothetical new supplier. |

This narrows the domain-extension task: no new exponent obstruction appeared
in this dependency pass, but a reviewable extended-domain transfer statement
must explicitly retain the complete costs, implementation hypotheses and
eventual thresholds. A numerical pass with an assumed bridge is insufficient.
Earliest historical motivation for choosing 1/32 remains undetermined.

## 3. Mechanism A: improve the endpoint deficit

The selected bit and complex ledgers both satisfy

`Δ=Wm−s=2v−3L`, with `L≥0` and `W≥2v`.

Grant **zero** central loss and **zero** auxiliary roles. Under that retained
ledger, `Δ/(Wm)≤1/m`. If all positive children have width at most `t_max`,
the raw moment at saving `x` obeys

`M(x) ≥ (1−1/m)(m/t_max)^x`.

This is stronger than the preparation screen, which kept today's central
loss fixed. At both target savings the new lower bound still exceeds one:

| Side | `m` | Retained child cap | Target | Optimistic defect per data role needed at this cap |
| --- | ---: | ---: | ---: | ---: |
| Complex | 66 | 20 | 0.075 | At least 6 rank units |
| Bit | 72 | 22 | 0.08 | At least 7 rank units |

The last column means: replace the favorable bound `Δ/W≤1` by `Δ/W≤r`,
and find the least integer `r` for which
`(1−r/m)^q(m/t_max)^p<1`, with target `x=p/q`.
It is an optimistic necessary budget, not a high-rank label construction.
Keeping scratch roles or central losses makes the requirement stricter.

**Assessment:** tuning the current boundary schedule while preserving this
gross ledger is an incremental lane, not a sufficient 1/16 strategy. Higher-rank
endpoints or a different topology could change the ledger, but direct sums
that increase useful rank and ambient dimension proportionally do not supply
the required ratio improvement. The previous
[Fano saturation and covariant block-label exclusions](../../research/kappa-nine/ASSESSMENT.md)
still apply to their specified geometries. This round supplies no new geometry
evading them and does not restart the retired clean aggregate branch.

## 4. Mechanism B: genuinely larger recursive operations

At fixed rank mass, replacing fragmented children by larger ones reduces
`Σ t^(1−x)` for `0<x<1`. As a deliberately favorable relaxation, ignore
physical boundaries and pack all rank units into children of width `m−1`
and at most one remainder. Concavity makes this the minimum under that
integer cap and mass: transfer rank from a smaller nonempty piece to a
larger unsaturated piece until a piece vanishes or hits the cap.

With today's actual role counts and rank masses, that relaxation gives:

| Side | Relaxed histogram | Target raw moment | Halving depth |
| --- | --- | ---: | ---: |
| Complex | 13,510 children of width 65, one of width 46 | 0.9996445468 | 46 |
| Bit, normalized by 3 | 59,895 children of width 71, one of width 15 | 0.9997545629 | 50 |

The bit row scales roles, rank and multiplicities together; it is not a new
physical replica schedule. These histograms are **not executable suppliers**.
They grant unproved batching across different roles, times and scalar gates.
Even their passing moments omit candidate-specific fallback and bridge costs.

The necessary cap at the existing mass is already 65 on the complex side
and 71 on the bit side. Granting the packing of just three current maximum
children only reaches caps 60 and 66; both fail an exact lower-bound test.
Thus simply batching one child from each of the three current stages is
insufficient under this mass accounting.

**Assessment:** this is a quantitative opening for a different recursive
operation, not evidence that ordinary batching works. A proposed operation
must identify actual adjacent/composable transformations, establish its exact
all-role endpoint and scalar chronology, and prove a recursive implementation
whose charged children give the improved moment. If it exposes a new restricted
child type, that family must be closed and its multitype recurrence proved.
Adding ranks and declaring a single child is not an implementation.

Larger children also cost more recursion depth. The optimistic complex
`66→65` depth is 46 instead of 1. Even retaining the old 2,159-bit role bound,
the row coefficient would rise to `46·2159+9909+252=109475`, requiring degree
strictly above `223329` under the old reserve formula. The published degree
70000 would fail. Larger fixed stock is asymptotically possible but must be
paid; bit restoration and its internal stock require their own new derivation.

## Decision and next bounded experiment

Do not launch a larger local-frame or scratch search for the 1/16 target.
The gross-ledger exclusion is stronger than those searches can overcome.

The next experiment worth trying is an **operation-level fusion diagnostic**:
take one explicitly delimited region spanning scalar incidences, write the
complete composed operator and all external obligations, and determine whether
it admits a larger recursive child or closed child family. Use exact common
address-map commutation across a scalar gate only when it acts identically
on every incident operand; account for all other alignments. Stop after one
region if the gain requires unproved cross-role regrouping or restores the
same fragmented bill. The near-full-child screen is a target for that proof,
not a demand that the first small example reach the full headline.

Follow-up: the [one-region diagnostic](scalar-gate-fusion.md) now rejects
the aligned-register common-frame model on its exact fixed boundary, including
arbitrary common Clifford frames and a copied unchanged control. It supplies
no instance of the optimistic packing above.

No construction prototype was run in this round: neither assessed mechanism
yet specifies a paid operation that passes the admission test. The completed
work is the domain dependency map, a region certificate, and two quantitative
mechanism assessments. No background search or goal loop remains running.

## Reproduction and attribution

```sh
python3 -B scripts/audit_sixteenth_round.py --check docs/research/kappa-sixteenth-domain-round.json
python3 -B tests/test_sixteenth_round.py
python3 -B tests/test_kappa_sixteenth_preparation.py
python3 -B tests/test_assembly_domain.py
python3 -B tests/test_selected_result.py
make selected-record-check
```

The finite profiles retain Dugongue/chafreaky/eumemic and their cumulative
community lineage. The analytic transfer retains RaD/hipotures, Zhihao Chen,
James Chang, icekylinx and subsequent integrations credited in the
[preparation note](kappa-sixteenth-preparation.md) and linked sources.
No historical source or frozen production verifier was edited.
