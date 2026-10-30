# Higher-rank geometry: two bounded screens for κ = 1/16

Douglas Colkitt, with OpenAI Codex assistance. October 9, 2026. Apache-2.0.

**Neither candidate earns a construction round. No new supplier or κ.**
The two tests compare different ways of obtaining higher-rank labels:
grouping existing orthogonal lines without enlarging the ambient space, and
tensoring the characteristic-sensitive core with overlapping fractional
blocks. The former destroys the required scalar interactions; the latter
preserves a valid block geometry but fails the target recurrence budget.

The selected conditional witness remains `κ=0.000661885549259598`. The
[sixteenth preparation](../../docs/research/kappa-sixteenth-preparation.md)
supplies our target coarse bit saving `0.08` and complex saving `0.075`.
Its analytic-domain and complete-supplier obligations remain open.

## The decision rule and its limitations

We first grant the hypothetical two-axis block ledger already specified in
[the earlier rank-two screen](../kappa-nine/block_fano_obstruction.py).
This is a **proposed compiler model**, not an established transfer theorem
for arbitrary blocks, and it is not the selected PR186 supplier's ledger.
Its failures exclude proposals retaining these obligations, not all uses of
the tested geometries.

Let a label have rank `r` in dimension `d`, let `m=d²`, and let `ρ` be the
independent auxiliary roles per label on each axis. Per data pair, grant:

| Charged children | Multiplicity |
| --- | ---: |
| `(d−r)²` | 2 |
| `r²` | 1 |
| `r(d−r)` | 4 |
| `dr` | `2ρ` |
| `m−dr` | `2ρ` |

The normalization is `W=2+2ρ`; the gross rank deficit is `r²`. We erase all
central loss, grant full batching within every listed macro, and omit other
nonnegative implementation costs. At saving `s`, the necessary raw test is

`M(s) = Σ n_t (t/m)^(1−s) / W < 1`.

If the proposed compiler retains a transparent identity factorization
`JLV=I_n` through `R` independent auxiliary roles, rank gives `R≥n` and
therefore `ρ≥1`. This is an explicit obligation of that compiler model.
It is **not** a lower bound for every possible producer. A changed circuit
may evade it, but must exhibit how the factorization or role obligation
changes. Dependent copies cannot simply be counted as additional independent
payload roles to enlarge `W`.

Every added role contributes `x^(1−s)+(1−x)^(1−s)>1`, where `x=r/d`.
Consequently a failed moment at the applicable role floor remains failed
when more such roles are added. The moment itself need not increase: this
is a weighted-average argument between quantities exceeding one.

## Candidate A: maximal sunflower packets of triple lines

Set `h=2r+1`, with `r≥5`. Choose a center point `c` and partition the other
`2r` points into `r` pairs. Adjoin `c` to each pair, obtaining triples
`S_1,...,S_r`. With `G=I−J/9`, their indicator vectors are mutually
orthogonal and have squared norm two. Thus

`P = (1/2) Σ_i x_(S_i) x_(S_i)^T G`

is a rational rank-`r` idempotent in dimension `2r+1`. The label rank ratio
approaches one half. This genuinely changes endpoint rank without tensoring
the ambient dimension. It is not merely a repeated direct sum.

The exact `r=5,h=11` control checks two different matchings, idempotence,
rank, a nondegenerate common form and noncommutation. Its bare target moment
even passes when every auxiliary role and central loss is removed.

**The scalar compatibility fails before compilation.** If any triple `T`
were orthogonal to all packet lines, it would intersect each `S_i` in exactly
one point. Summing those intersections gives both `r` and

`3+(r−1)·1_(c∈T)`.

The latter is either `3` or `r+2`, never `r` for `r≥5`. Thus no triple line
is orthogonal to an entire maximal packet. In particular, two packet
projectors cannot annihilate each other. This holds for every choice of
centers and matchings, not just the two controls.

Under the proposed central-map rule—diagonal one, with an off-diagonal one
permitted only between annihilating labels—the central matrix is forced to
be the identity. Its binary rank equals the number of labels. Grouping these
lines therefore loses the characteristic-sensitive low-rank interaction
which motivated the core. A different rule or partially filled packet is
outside this rejection; neither is supplied here.

## Candidate B: a fractional-cycle tensor of the two-field core

In dimension eleven, define coordinate five-planes

`Q_i = span{e_(i+2j mod 11) : 0≤j<5}`, for `0≤i<11`.

Adjacent cycle labels have zero product. The binary matrix
`C_cycle=I+Adj(C_11)` has diagonal one and permits precisely those
off-diagonal interactions. Combine it with the full triple core on ten
points:

`P_(S,i)=P_S ⊗ Q_i`, `C=C_triple ⊗ C_cycle`.

Here `P_S=x_S x_S^T(I−J/9)/2` and
`(C_triple)_(S,T)=|S∩T| mod 2`. This gives **1,320 valid rational block
labels of rank five in dimension 110**, with a binary central matrix of
rank 110. The block labels are noncommuting because the triple factor is.
This avoids rejecting the construction merely for being a coordinate
coloring.

All required annihilations follow factorwise: a nontrivial permitted
interaction changes the triple label, the cycle label, or both; at least
one corresponding projector product is zero. The certificate checks all
14,400 triple-factor pairs, all 121 cycle-factor pairs and exact binary
ranks. Tests independently expand small Kronecker matrices and check the
three cases, including their reversed products.

The overlapping-block construction is motivated by fractional block
representations; see [Bukh and Cox, *On a fractional version of Haemers'
bound*](https://arxiv.org/html/1802.00476v2). Our particular tensor is
verified directly here. Neither that literature nor this algebra supplies
an all-role multiplication network automatically.

**This candidate fails the budget even at zero auxiliary roles and zero
central loss.** Tensoring preserves compatibility but reduces the label
rank ratio to `5/110=1/22`. No detailed producer search is justified within
the stipulated ledger. This test concerns the explicit ten-point, eleven-cycle
tensor; it is not an exhaustive search over fractional representations,
graph products, or alternative central matrices.

## Exact comparison

Values below are decimal summaries of certified rational intervals. A
moment above one rejects the specified recurrence profile.

| Geometry / granted costs | Bit target `0.08` | Complex target `0.075` |
| --- | ---: | ---: |
| Sunflower rank 5 in 11, no auxiliary roles | 0.9994107202 | 0.9926569601 |
| Same, one auxiliary role per label per axis | **1.0280533942** | **1.0228577799** |
| Tensor rank 5 in 110, no auxiliary roles | **1.0311939790** | **1.0289793819** |
| Idealized rank one half, same auxiliary floor | **1.0173221432** | **1.0121171620** |

The last row is a control, not an attained geometry or an assertion that
one half minimizes the moment over every rank ratio. It shows how even a
favorable rank ratio can fail once the specified producer ports are charged.

Neither candidate survives both compatibility and optimistic cost checks.
Accordingly **no paid circuit fragment was attempted**, and no complex
companion was constructed. This follows the agreed stop rule rather than
leaving a promising surviving candidate unfinished. Applying the complex
target to a hypothetical histogram is a rejection screen, not evidence that
the rational bit geometry has a complex implementation.

## Strategy for the next round

Require a proposal to specify both its geometry and how information enters
and leaves it. These tests identify two distinct ways a high-rank proposal
can fail: preserving dimension while destroying useful interactions, and
preserving interactions while enlarging dimension too much.

A new candidate should provide, before a large search:

1. A concrete source of characteristic-sensitive interactions and an exact
   small label construction, or a sharply specified missing identity.
2. A proposed producer/readout contract that explicitly changes a charged
   obligation when the old block budget fails.
3. An optimistic **complete cost ledger**, with uncertainty shown as a cost
   allowance rather than silently omitted. An optimistic pass only earns
   implementation work; an optimistic failure stops that model.
4. One representative paid circuit fragment testing the biggest uncertainty,
   followed by an exact complete witness if the fragment survives.
5. A specific scaling reason and complex-companion plan before expanding
   instance size or solver time.

Limit the next round to two mechanisms. A timeout stays inconclusive; a
failed ansatz does not become a general lower bound. Reopen a rejected model
only when a proposal changes an identified premise. Avoid spending another
round on the open dimension-15 triple branch merely because it remains
open: its old target budget was for `2^-9`, not this much larger target.

No presently identified candidate has earned a large construction campaign.
The next discovery task is joint geometry and producer design, with a
demonstrable way to preserve useful interactions at a high rank ratio while
paying for their access. That is a narrower question than unrestricted
matrix search, but it remains a substantial mathematical opening.

## Reproduction

```sh
python3 -B research/higher-rank-sixteenth/screen.py --check research/higher-rank-sixteenth/certificate.json
python3 -B -m unittest discover -s research/higher-rank-sixteenth -p 'test_*.py'
make selected-record-check
```

The receipt pins the inherited ledger and target-budget sources. Enclosures
are independently certified with integer powers; no floating-point rank or
inequality is used for acceptance. The original triple geometry, copied-block
accounting and community construction retain their existing attribution.
These scoped screens assert no priority for tensor products, fractional
representations or the underlying elementary projection identities.
