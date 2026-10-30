# Independent read-only E120 precision and invoice review

Reviewed author seal
`cb40b9602eec2c4c8950af4f9e8a06ea0d99db5ca74ceafd8b7781acc0aaccf6`
at `/tmp/full-e8-e-adapter120-20261025-structural`. Every author file is checked
against that seal. This review modifies no author byte and runs no dense
physical replay.

## Finding and corrected argument

The stated constants survive. One intermediate norm explanation in
`PRECISION-SCOPE.md` should be read with the following correction when an
arbitrary incoming scratch error is allowed.

Let B be any partially accumulated scalar K matrix, with its physical unitary
address blocks. The actual coefficient row and column absolute sums are at
most7. The block Schur bound gives `||B||2<=7`. On mains plus scratch the
accumulation is the full shear

`T_B(x,s)=(x,s+Bx)`,

so the correct general bound is

`||T_B||2 <= ||I||2+||T_B-I||2 <=1+7=8`.

The reversed bilinear transpose has the same norm. The expression
`sqrt(1+7^2)` follows immediately for the restricted input `(x,0)`, but does
not follow from the row/column premise for arbitrary `(x,s)`. For example,
the scalar shear with B=7 sends `(7,1)` to `(7,50)`; its squared norm ratio is
2549/50>50. This refutes that generic inference, not the actual K construction.
The bound8 used by the author's C,Q,M constants remains valid.

All remaining stages of one output cube are SWAP isometries and owned CLEAR
projections; OWN_ZERO is an isometric zero embedding. A suffix beginning
inside accumulation has a remaining partial B with the same bound. In the
reverse transpose, its corresponding prefixes have the same norm. Completed
cubes implement orthogonal K on mains and remove their private scratch.
Different cubes act on disjoint main blocks and clear scratch before reuse;
an incoming scratch error can reach the current cube's outputs, but cannot
flow through a cleared scratch into a later cube. Hence the prefix/suffix
bound for the complete sequential product-cube stage is8, rather than a
product of8 over all3375 cubes.

The exact four chronological recoder receipts cover both original words and
both reversed transposes. A selector axis's120^2 batches act on disjoint
120-field blocks. After at most two complete selector axes, multiplying their
endpoint bounds by the active axis prefix bound gives the reported squared
bound14320735522816/15. Its exact integer square-root upper bound is977096;
it is not raised to43200.

For each E or inverse code, two recoder stacks, one modal scale of at most1351,
and the corrected K bound give `C=8*1351*S^2`. Physical L maps are unitary.
Query gathering has two recoders and COPY norm at most2; scattering has two
recoders and shear norm at most1351. Thus `Qbound=2*1351*S^4` covers every
prefix/suffix, including the reverse owned transpose. The original-ground
queries remain full H25 calls; no modal support discount is used.

Distinct source-owner contact copies have combined norm at most2, regardless
of how often each retained contact is subsequently read. The inverse target
stage has block row/column bound7, including partial ADD sums, giving8.
Two code stages, the query pair, and these two native passes give the existing
`M=16*C^2*Qbound`. Ordinary boundaries are monomial. The three-module plus
three-code bound remains `M^3*C^3`. The checker reproduces all existing exact
constants and advertised strict powers without evaluating the dense circuit.

These are bounds at the declared whole-field primitive boundaries. A SWAP is
an exact SWAP primitive here, and a paid Gaussian is a completed unitary
child. If SWAP is lowered into3ADD+sign microcode or a Gaussian recursively
expanded, its internal error service/prefixes must be separately accounted.
No per-bit coordinate allocation is inferred from these field-l2 bounds.

## Invoice orientation and source timing

An independent census of the actual512-owner native inverse gives, per owner:

| primitive | count |
|---|---:|
| ADD |76|
| COPY |1|
| CLEAR |1|
| P |15|
| D |15|
| X |17|
| phase |6|

Its paid calls are one each of H8,H9,H15,H16 per owner. Transposing a COPY
adds one ADD and CLEAR; final CLEAR becomes OWN_ZERO. The forward monomial
boundary adds3 X operations per owner. Therefore the unified native upper
bill ADD77V, P15V, D15V, X20V, phase6V, COPY V, OWN_ZERO V, CLEAR2V covers
both orientations, with V=120^3.

The query's extra+h ADD accounts for the transpose of modal COPY. Its h
OWN_ZERO accounts for transposed final mode CLEAR. Two E codes allocate and
clear V fields each. The resulting total OWN_ZERO is3V+h, not2V+h, and agrees
with the published module invoice. The script independently recomputes every
ordinary local/three-stage upper count and the V+h+512 owned peak.

A metadata-only source version pass checks all512 actual source owners and
76 reads per owner. Each reverse source-Y COPY occurs at its actual unchanged
contact version, before that inverse source path finishes. Base120's8 query
calls precede the source-consuming native word; the emitted corrections are
-15 in backward and+15 in inverse. Thus the inverse acquires the authentic
native contacts first, restores ground Y by E, queries original Y, undoes the
correction, and then finishes native X inversion.

Bilinear transpose retains every real ADD/SCALE coefficient once, reverses
chronology and exchanges ADD source and target. The review checks every such
non-address primitive against the emitted inverse. Address P transposes to
its inverse, Gaussian C is symmetric, D/X are symmetric and scalar phase is
unchanged; these phase identities remain the author's pinned physical science
and root's independent physical replay, rather than a new dense replay here.

The displayed algebra uses only `[E,R]=0`, E real symmetric, and Q,D commuting
on their disjoint axes. It does not move E through Q separately. Inverse Y
restoration followed by original-ground correction has the stated order.
The boundary `diag(D^2,D^2) J (WB^-1)^T J^-1`, J=diag(Q^2,I), gives the forward
blocks `[[ED,0],[DEQ^-1,DE]]`; the first block uses commutation with R^2.
Owner coefficients act once; only physical address words tensor lift.

No material invoice, direction or finite field-norm error was found beyond
the intermediate arbitrary-scratch explanation corrected above. The negative
terminal remains UNKNOWN. This review does not establish coordinate/TM
precision, all-size storage/routing, a complete new supplier, scientific
adoption or any new kappa.
