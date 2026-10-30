# Higher-rank labels in the current three-shared-core architecture

Douglas Colkitt, with OpenAI Codex assistance. October 9, 2026. Apache-2.0.

**The cover geometry and accounting extend to suitable rank-r blocks. A
target-capable arithmetic budget exists; a competitive block core does not
yet exist. No new supplier or multiplication exponent is certified.**

This pass uses the architecture of the selected construction, unlike the
older tensor-square model used in the [previous higher-rank comparison](../higher-rank-sixteenth/REPORT.md).
The current conditional witness remains `κ=0.000661885549259598`.
The improvement here is a more appropriate construction specification and
exact controls for it. None of the previously rejected geometries becomes
a supplier merely because the accounting is more favorable.

**Follow-up:** the [interaction-family design pass](../interaction-family-design/REPORT.md)
rejects the 250-port illustrative histogram in the conservative copied-center
model using joint scalar-support and source-span bounds. Its arithmetic
remains correct; that model cannot supply the proposed producer.

## 1. What a local block core must supply

Let the local address space A have dimension d and let each of v data ports
carry a rank-r subspace U_s, with `0<r<d`. A valid replacement must supply:

- A **complete** identity shear on source/target banks, restoring arbitrary
  dirty inputs, with source frames `T_(U_s)→F_A`, target frames
  `I→F_A T_(U_s)^(-1)`, and its exact reverse/complement orientation.
- Actual common frames at every gate, all injections, copied-center reads,
  dirty-response corrections, scalar inverses and data restoration. Labels
  alone or a scalar fitting matrix do not supply this word.
- A compatible cover: source blocks must have a common isometry type and
  their complements must admit specified identifications with a fixed
  `(d−r)`-space. This is a sufficient condition, not a claim about arbitrary
  block representations. In the complex binary geometry, equal dimension
  alone does not guarantee the required form type. Degenerate internal
  frames remain allowed by the inherited Clifford interface; an arbitrary
  degenerate source block is not automatically admitted by this cover.
- The literal local child histograms H, D, T for auxiliaries, sources and
  targets, and the entrance-gauge counts s_a. Scalar role counts and copied
  dependent streams must keep their distinct meanings.

The inherited complex representative has `T_U²` equal to a Pauli, not
necessarily the identity. Those operators and the actual rank-zero endpoint
adapters must remain in the construction. The bit and complex local scalar
identities still live in different fields from their address geometries.
For the complex extension established here, restrict source blocks and their
complements to orthogonal images of standard coordinate blocks, and use the
transported coordinate representatives with paid Pauli reconciliation.
Other binary form types need a separate representative/endpoint audit.
Higher-rank address labels do not authorize free matrix-valued scalar gates:
the local word must still use the retained scalar payload operations.

## 2. The block cover and endpoints

Write `A=U_s ⊥ V_s`, choose two fixed copies B,C of `V_s`, and first work in

`E₀=A ⊥ B ⊥ C`, with dimension `3d−2r`.

The first exchange fixes U_s and exchanges V_s with B. The third exchanges
V_s with C. The three active spaces are `U_s+B`, A, and `U_s+C`.
They have pairwise intersection U_s, and their commuting projectors sum
to `I_(E₀)+2P_(U_s)`.

The data chronology is the same three-shear chronology as the rank-one
cover, with every line replaced by its block:

| Stage | Scalar operation | X frame path | Y frame path |
| --- | --- | --- | --- |
| 1 | `Y+=X` | `U_s→U_s+B` | `0→B` |
| 2 | `X−=Y` | `U_s+B→A+B` | `B→V_s+B` |
| 3 | `Y+=X` | `A+B→E₀` | `V_s+B→E₀−U_s` |

The middle stage uses the complete reverse/complement local word, with
source and target exchanged. The offsets are `0`, B and `V_s+B`.
As in the existing cover, the third offset expressed at its invocation
vertex is the fixed `B+C`, independent of the port. Right multiplication
by the exchange maps gives bijective incidence routing. No positive-rank
interstage connector is introduced by this construction.

The complex scalar composition is `(X,Y)→(−Y,X)`. The physical data outputs
are `(-F_(E₀)y, F_(E₀)T_(U_s)^(-2)x)`. Apply the actual `T_(U_s)²` source
Pauli, the output sign and bank normalization. In the bit case the source
partial swap is an involution, so its square is already the identity.

Now adjoin two copies of the fixed source block, total dimension `2r`.
The full ambient space has dimension **m=3d**, and is isometric to three
copies of A. Each data output pays one width-`2r` complement child.
The one physical auxiliary bank visits three disjoint d-dimensional blocks
in sequence, with the data cover and auxiliary routing treated separately.
Its complete raw actions and reverse-stage Paulis telescope exactly as in
the inherited completed-core argument. A gauge of dimension a leaves one
width-`3a` correction after those visits.

This proves the finite geometric extension under the stated local-core and
isometry hypotheses. It does not construct a competitive local block core
or reprove the inherited all-size routing and recursive interfaces.

## 3. Complete rank and moment accounting

Per cover vertex, let R be the actual independent auxiliary stock. Set
`Γ=Σ a s_a`. The local auxiliary mass is

`Σ t H_t = Rd−Γ+L_aux`.

For monotone data paths, `Σ t(D_t+T_t)=2v(d−r)`. Any additional data-path
cost is `L_data≥0`; it is explicitly added rather than assumed free.
Write `L=L_aux+L_data`. The complete profile is

`W=2v+R`, `m=3d`,

`n_t=3(H_t+D_t+T_t)+2v·[t=2r]+Σ_a s_a·[t=3a]`.

Every three-stage invocation remains charged. Gauge mass cancels from the
**rank sum**, but its changed child sizes still affect the moment:

`Σ t n_t = Wm−2vr+3L`, hence **`Δ=2vr−3L`**.

For the inherited nested construction, the remaining local loss is the
copied-center charge. A new circuit must rederive that fact; arbitrary
retreats, reads or restoration steps may add loss. Physical aliases,
terminal accumulation and completed-bank substitutions likewise require
their literal changed inventory, not a free reduction of R. This formula
is a contract for a valid local profile, not permission to substitute r
for one in the scalar producer without changing its proof.

The raw contraction test at saving s is

`M(s)=Σ_t (n_t/W)(t/m)^(1−s)<1`.

Fallback, stopped leaves, full group stock, scalar/precision charges and
the all-size bridge remain additional obligations.

## 4. Rank-two controls, including phases and arbitrary inputs

The small complete local word uses one source, one target and one dirty
center in dimension `d=2`, with rank-one source block U. Chronologically:

1. At frame zero subtract the original dirty center from the target.
2. Raise the center to U and add the source at that common frame.
3. Reframe a **copy** of the center from U to zero and add it to the target.
4. Raise source and center to the full active frame; subtract the source
   to restore the center's arbitrary logical value.
5. Raise the target to the complementary source frame.

The copy read costs r; it is neither free nor a new independent input.
The local auxiliary bill is `d+r`, while each data path costs `d−r`.
Thus `R=v=1,L=r`, and the completed shared profile has deficit `−r`.
It is deliberately a negative control, not a characteristic-sensitive
improvement.

The rank-two version is its direct sum: `d=4,r=2`. The checker verifies
every original source, target and dirty coefficient as an exact sparse
operator expression, and then executes the complete literal inverse.
It checks the composed three-stage data and auxiliary endpoints, including
the padding children and middle-stage Pauli. No dirty value is set to zero.

For complex controls, coordinate operators are kept at order four. A
separate exact Gaussian-rational calculation verifies

`C=1/2 [[1+i,1−i],[1−i,1+i]]`, `C²=X`, `C⁴=I`.

Omitting the source Pauli fails the complex endpoint. This prevents the
binary symplectic involution from being substituted for the exact operator.
The small expressions use commuting coordinate factors; they do not claim
that arbitrary internal Clifford frames commute.

Both ranks use an explicit 720-element coordinate-permutation subgroup.
The checker verifies all data incidence bijections, source-block consistency
and auxiliary bank assignments. The six coordinate cells have size one
or two. There are 2,160 independent roles in each compositional control.
The local operator proof and all routing incidences establish the composed
endpoint; this is not a dense simulation of every global address. This
subgroup is also **not** a replacement for the full generic routing group
or its good-class estimate in a real supplier.

There is a second, source-pinned control on the selected complex profile:

| Quantity | Selected rank-one profile | Direct-sum rank-two profile |
| --- | ---: | ---: |
| local dimension d | 22 | 44 |
| ambient m | 66 | 132 |
| independent roles W | 13,326 | 13,326 |
| local loss L | 440 | 880 |
| total rank | 878,196 | 1,756,392 |
| deficit | 1,320 | 2,640 |

Every child width doubles with unchanged multiplicity. Therefore every
ratio `t/m` is identical, and **the entire raw moment function is unchanged**.
Exact interval replay at both target savings confirms this. The scalar
word stays the same, and direct-sum address frames preserve its common-gate
identities. New generic bases, eligible primes, group stock and the all-size
bridge have not been certified for this enlarged object; it is not admitted
as a new production supplier.

## 5. A more favorable budget, with explicit missing costs

For a zero-gauge local compiler with minimum-rank data paths, let `ρ=R/v`,
`λ=L_aux/(vd)` and `t=r/d` (so `L_data=0` in this screen).
Grant one child per source and target path, and pack auxiliary rank ideally
into width-d children. This gives the optimistic lower bound

`M(s) ≥ [6((1−t)/3)^(1−s)+2(2t/3)^(1−s)+3^s(ρ+λ)]/(2+ρ)`.

Fractional packing is a relaxation, not a physical implementation. A lower
bound above one rejects that model; a bound below one only leaves room.
Nonzero gauges must instead use the full histogram formula in section 3;
the zero-gauge auxiliary coefficient cannot be applied to them indiscriminately.
Data retreats likewise require their actual histogram; their extra mass
cannot simply be assigned the auxiliary width-d cost in this relaxation.

At one auxiliary role per label and zero local loss:

| `r/d` | Bit target `s=0.08` | Complex target `s=0.075` |
| --- | ---: | ---: |
| `1/3` | 1.032319895 | 1.025318640 |
| `2/5` | 1.016526149 | 1.009584276 |
| `5/11` | 1.002992985 | 0.996138996 |
| `7/15` | 0.999911922 | 0.993082204 |
| `9/19` | 0.998115890 | 0.991301013 |
| `1/2` | 0.991300392 | 0.984546350 |

The half-rank row is only an arithmetic control. Mutually annihilating
half-rank idempotents must be complements, which severely restricts the
interaction graph; it is not offered as a competitive family.

One explicit **unimplemented** integral budget is

`d=19, r=9, v=250, R=250, L=19`, with zero gauges,

`H={19:251}`, `D=T={10:250}`.

It gives `m=57,W=750,Δ=4443` and children

`1500×[10] + 500×[18] + 753×[19]`.

The raw moments are approximately **0.9995717124** and **0.9927488603**,
strictly below one at the bit and complex targets respectively. Here
`L/(vd)=1/250`; for the bit target the optimistic maximum at `ρ=1` is
approximately `0.00517676`. The extra allowance is small. No family of 250
rank-nine labels, scalar decoder or producer is supplied by these numbers.

The older two-axis block model fails at the same `r/d=9/19` and one local
auxiliary role per label. Thus the architecture change genuinely alters
the feasibility screen. It does not invalidate the earlier scoped results
or prove that either ideal profile can be physically realized.

## 6. What geometry search is justified—and what remains closed

The full intersection-one triple graph contains seven Fano lines whose
labels must mutually annihilate. Their images form a direct sum, so any
uniform-rank representation has `7r≤d`, even for oblique idempotents.

The modern bare data moment is

`M₀(t)=3((1−t)/3)^(1−s)+(2t/3)^(1−s)`.

At `s=1/15`, both endpoints of `0≤t≤1/7` exceed one. This function is
concave in t, so the whole interval fails. Each additional completed dirty
role pays at least its full rank capacity; it cannot repair an already
failed data contribution by enlarging W. The checker verifies the actual
Fano incidence and exact endpoint power inequalities.

This saving is weaker than the required coarse bit saving for `κ=1/16`.
Consequently **the full old triple annihilation graph remains excluded for
this shared-core data/tail contract, even at arbitrarily high block rank**.
That statement concerns the specified required edges; it does not prove
that every new scalar topology or changed support schedule must require them.

The next legitimate search is therefore for a different compatible label
and interaction family, or a scalar support schedule that changes those
annihilation obligations, measured against the modern shared-core budget.
An identity-preserving direct sum or the parked rank-two full-triple search
cannot provide the needed gain. A candidate must bring a paid local word
with it: favorable representation dimension by itself remains insufficient.

The bounded preparation pass is complete. No new geometry search, compiler
optimization campaign, publication or production-verifier change was launched.

## Reproduction and attribution

```sh
python3 -B research/shared-core-blocks/audit.py --check research/shared-core-blocks/certificate.json
python3 -B -m unittest discover -s research/shared-core-blocks -p 'test_*.py'
make selected-record-check
```

The completed-core sharing lineage credits an664, the paired-cube and exact
frame construction icekylinx, the local circuits and schedules eumemic and
subsequent contributors, and the selected physical construction Dugongue on
chafreaky's and the earlier community work. The pinned source notes retain
their full provenance. This pass extends the cover bookkeeping under stated
block hypotheses and supplies exact controls; it does not claim invention of
shared cores, direct sums or the elementary projection/phase identities.

All current analytic-domain, bit-wrapper, generic-basis, prime, full-group,
row-stock, precision and fixed-tape obligations remain in force. In
particular, a passing hypothetical moment does not remove the enforced
`b<1/32` admission guard or establish the larger analytic domain.
