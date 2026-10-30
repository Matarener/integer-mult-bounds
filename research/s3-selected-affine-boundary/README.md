# S3 convolution and the selected affine data interface

No new kappa. This is a scoped admission-gap result for PR2224's proposed
selected-program placement, not a counterexample to its rank-nine convolution
formula. The selected result and all predecessor packages are unchanged.

The exact predicate is whether the regular rational S3 convolution on twelve
independent input arrays can occur inside the frozen selected gauge44 program,
using affine input and output maps, fixed linear native operations and arbitrary
dirty helpers. It cannot. The argument covers any finite composition in that
interface, so enumerating six-source/six-target support choices cannot find it.

PR2224 explicitly leaves actual source placement open. This result answers one
literal interpretation of that handoff. It does not establish what alternative
interpretation its author intended, or exclude an operator-valued construction.

## Source boundary

Canonical main is `6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority revision 6.
The selected conditional kappa is `836330098538459/500000000000000000`.
Its complex primitive saving is `67018507072324140917/40000000000000000000000`;
the BIT saving is `1733427039589844234749/1000000000000000000000000`.
These are inherited source-bound values, not primitive replays here.

The pinned selected replay archive contains the gauge44 local-program member
`candidate/strict/global/base/providers/gauge44/LOCAL-PROGRAMS.json.gz`, SHA256
`241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a`.
Both orientations have 24,767 events. Each has 19,693 scalar instructions,
3,486 climbs, 1,090 chart adapters, 480 residual adapters, eight center operations
and ten fixed phase markers. The scalar operations are fixed-coefficient ADD,
SCALE, COPY and CLEAR. The retained invoice code interprets their operands and
constant coefficients. It does not multiply one payload field by another.

At the ideal exact interface, a climb, center operation, chart adapter or
residual adapter is a fixed linear operator on payload arrays. A phase marker
is fixed control metadata, not a data-dependent branch. This uses the selected
native/compiler semantics; it does not reprove their all-size realization.
The proof below allows arbitrary fixed linear operators at those sites and
therefore does not depend on a particular Clifford matrix or frame choice.
Rounding and nonlinear implementations are outside this interface theorem.

`SOURCES.json` binds these bytes, the source archive, the selected record and
PR2224's exact coefficient receipt. PR2224's live head was checked as
`de6310e495c94c7553dc353b7a58aa117af4271b`, merged. Its original selected-record
hash is historical; the numerical kappa is unchanged, and this package freezes
the current record separately. No pending Git object is needed for replay.

## Proof

Let the payload space be any vector space over the rationals or complexes.
Take independent inputs `x=(x_g)`, `y=(y_h)`, dirty output `z` and arbitrary
helper state `s`. The desired output is

```text
z'_k = z_k + sum_{g h = k} x_g y_h.
```

It suffices to restrict all arrays to one scalar coordinate. For any map `F`,
define its mixed difference, with all other inputs and helpers fixed, by

```text
Delta(F;x,y) = F(x,y) - F(x,0) - F(0,y) + F(0,0).
```

Every affine map has zero mixed difference. Fixed-coefficient ADD, SCALE,
COPY and CLEAR are linear. Every fixed native linear map is linear as well.
Induction over the finite event list shows that all intermediate payloads are
affine in the input data after an affine encoder. An affine decoder preserves
this property. Arbitrary helpers and constants contribute affine terms; fixing
their initial values removes those terms from the mixed difference. Requiring
their restoration only narrows the class, so granting unlimited dirty helpers
does not evade the argument.

For S3 convolution, take `x=e_g`, `y=e_h`. Its mixed difference is exactly
`e_(g h)`, which is nonzero. In particular the identity/identity pair already
contradicts the affine invariant. Hence no such encoding/program/decoding
composition computes the required bilinear module on twelve independent
inputs. The argument also applies to an extracted chronological subprogram.

The verifier separately checks all 36 group-basis products of PR2224's nine
terms, using its exact rational coefficients. Every mixed difference is the
correct nonzero basis vector. This confirms the convolution formula and the
type mismatch at the same time. It does not infer that an omitted physical
mapping was ever claimed as established by PR2224.

Fixing one convolution argument changes the hypothesis. The resulting map is
linear in the other argument. Thirty-six exact positive controls verify this
case and dirty-output subtraction. An operator-valued or data-dependent
boundary also needs a separate argument; none is excluded here.

## Kappa case and complete ledger status

The proposed eight-block screen changes the selected local histogram by
`-288 H1 + 8 H9`, from rank mass 5,586 to 5,370, and assigns 216 mass units to
idle remainders. PR2224 certifies its favorable primitive interval
`[0.001775158769926,0.001775158769927]` in its declared relaxation. That
interval is inherited conditional arithmetic, not an achieved saving.

The source-bound baseline and the S3 tensor identity are established under
their stated assumptions. The new literal affine-data embedding is disproved
above. The implication from tensor rank nine to one recursive address-rank-nine
child is unproved; these are different quantities and no conversion is supplied
here. Source access, transforms, frames, consumer fanout, helper restoration,
ownership, precision/division and a complete recursive invoice remain unknown
for a changed implementation. Unknown charges are not assigned zero for
admission. BIT and the analytic transfer are inherited only for the selected
construction, not automatically for this replacement.

An initial planning point used `a=17/10000`. Its `17/10017` transfer is only a
limiting cap. A strict finite trial would need slack, such as
`kappa=1697/1000000`, and every applicable outer inequality. No such trial is
claimed here because the literal module already fails admission. No additional
rank charge can repair a type mismatch while keeping every operation affine.

The family decision is **narrow, then stop**. The bounded test was the selected
opcode inventory and the exact mixed-difference invariant. It fails before
native synthesis or owner search. No universal S3 obstruction, source-count
exclusion, changed selected frontier or new kappa follows.

## Reproduction and verification limits

Python 3.12 and the standard library suffice. The direct commands are read-only,
Git-free and use package-local frozen inputs:

```sh
python3.12 -I -W error -B research/s3-selected-affine-boundary/verify.py
python3.12 -I -O -W error -B research/s3-selected-affine-boundary/verify.py
python3.12 -B scripts/research_package.py --package research/s3-selected-affine-boundary
```

The marker is `PASS_S3_SELECTED_AFFINE_BOUNDARY_NO_NEW_KAPPA`. Four controls
reject a data-valued coefficient, a Boolean coefficient, a data-product opcode
and an omitted S3 tensor term. Stored receipt comparison distinguishes Boolean
and integer JSON values. Source hashes authenticate inputs; they are not proofs
of native semantics. The event audit does not replay Clifford matrices, selected
endpoints, hosted owners, precision or the full multiplication theorem.
No Lean, Docker, selected cold replay or historical heavy suite is needed.

## Open next questions

Specify a concrete changed S3 interface before another support search. If one
argument is fixed, identify its coefficient values and the actual linear native
operation being replaced. If the arguments are operators, give their action,
composition order and literal selected occurrence. A nonlinear encoding needs
its implementation and complete paid bill. Each route must explain how its
tensor factors become legal recursive children with the correct payload volume,
frames and restoration. No such conversion is supplied by a child-count census.

## Credit and overlap

Cinna Davis supplied PR2224's exact rational S3 convolution formula and its
explicitly conditional screen. Strassen's seven-product matrix formula and the
standard rational decomposition of the S3 group algebra retain their usual
credit. Rohan Arun's selected PR1094 packing, Jeremy Kothe's word lineage,
Hao Yan's controller and all predecessors credited in the selected review remain
the source construction. Douglas Colkitt's ceiling model underlies PR2224's
screen; its arithmetic is not rerun or extended here. Nick Petalas contributes
this scoped affine-interface argument and source-bound check. Apache-2.0.

The shared intake covers 247 open PRs at 22:04:28 UTC and 2,170 Discussion
records at 22:05:00 UTC on October 17, 2026. Its older 2,630 closed PRs have a
20:44:55 UTC cutoff. Exact S3/convolution and decoder searches used an
authenticated private offline copy. The original placement handoff in
Discussion 1167 is the starting point. Newly closed non-prior-batch bodies,
arbitrary diffs and unpublished work are not completely covered. Nearby
group-algebra register-word tariffs concern a different operator interface.
No novelty claim is inferred from absence of a search match.
