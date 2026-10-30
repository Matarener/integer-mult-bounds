# Native boundary compression and common-chart experiments

This continuation closes three specific questions raised by the retained
128-port consumer. It supplies a literal native geometry for nine common
9-axis charts, an exact rank census for all 256 partially common chart
patterns, and a counterexample to gathering the eight scalar queries before
their source-dependent native line transforms.

**None of these experiments produces a new kappa.** The complete common-chart
geometry uses its entire raw saving before a residual consumer is paid. The
partial patterns also fail the retained target under the optimistic price
screen supplied by the neighboring invoice experiment. The scalar query
counterexample concerns a restricted order of operations; it is not a lower
bound for general native circuits.

## Reproduction and retained sources

Run from the repository root:

```sh
python3 -B research/kappa-boundary-continuation/native-boundary/uniform_geometry.py
python3 -B research/kappa-boundary-continuation/native-boundary/partial_geometry.py
python3 -B research/kappa-boundary-continuation/native-boundary/query_envelope.py
```

All scripts use Python's standard library. The geometry and query scripts
accept `--scope` pointing to the frozen `kappa-global-continuation` directory;
all three accept `--out` for a fresh evidence directory. No predecessor file
is modified. The retained inputs are:

| Input | SHA-256 binding |
|---|---|
| Native `DATA-PHASES.json` bytes | `c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa` |
| Controller `TEMPLATE.json.gz` bytes | `21297b20f1f2dc76eb9dd8124416068c3cb096bab9df17fa4da19bc68dfe082e` |
| `ALTERNATING-CONSUMER-IR.json.gz` decompressed payload | `6d6818a0694987878a4e54c4a5dc7125b38e1d3fe8d94578593044c8172c4cf8` |

The phase and template inputs are retained inside
`kappa-global-continuation/inputs/kappa-consumer-followup`. The query IR is in
that frozen scope's `helper-consumer/evidence` directory. Source locations
and bindings are explicit in the generators. The new native program's
decompressed payload hash is recorded in `evidence/UNIFORM81-RESULT.json`;
compression container bytes are not used as a replay equality criterion.

## 1. A literal common-chart geometry in dimension 81

Let `B_0,...,B_8` be nine disjoint standard coordinate blocks of dimension 9.
Write `q_j` for the actual old-port norm-one label embedded in `B_j`, and
write `F_t` for the positive native full transform on `B_0+...+B_t`.
At stage `j`, use the standard block swap `B_0 <-> B_j` on every port.
This route is genuinely common to all 128 ports. A scalar port operation
commutes with it; the native construction no longer introduces a different
owner conjugation for each ordinary label.

For each of the original 112 ports, the local entrance gauges are
`(C_q, I)` and its exit gauges are `(FULL9, FULL9 C_q^-1)`. The 16 additional
ports have `(I,I)` entrances and `(FULL9,FULL9)` exits. These are the retained
native contracts, including their asymmetry.

Consequently, an old port leaving stage `t` has gauges

\[
X:F_t,\qquad Y:F_tC_{q_t}^{-1}.
\]

At each later active stage `j`, first apply `C_{q_j}` on X and
`C_{q_{j-1}}` on Y. Both banks then have the required common exterior
`F_(j-1)` at that local entrance. This costs 224 rank-1 native children
at each of eight boundaries, or **1792 H1**. The zero-label ports advance
through fresh 9-dimensional blocks and require no interstage catch-down.

The native idle words use the actual eight-vector orthonormal basis of
`q`-perpendicular space supplied by the phase data. Each change of basis
includes its exact affine translation. The verifier follows the controller's
literal local, idle, bridge, and terminal order, rather than only comparing
a final aggregate phase.

### Productive endpoint closure

The initial normalized X coordinate is `C_q0^-1 x`. After the ordinary
scalar controller and its signed exchange are canceled, a productive endpoint
must cancel this initial factor. The final Y idle gauge must therefore be

\[
\mathrm{FULL81}\,C_{q_0}^{-1},
\]

followed by the retained translation `q_0`. Leaving the final hole at
`q_8` would not accomplish that cancellation.

For the four bank pairs, the final local stages are 2, 4, 6, and 8.
Their old-port X completion ranks are `54,36,18,0`; the corresponding
Y completion ranks are **`56,38,20,2`**. The two extra axes are the previous
normal and `q_0`. The inverse on `q_0` is a positive native line followed
by its actual translation. These two axes can be fused with the final idle
child. They add 896 units of raw rank across all ordinary ports and pairs;
the construction does not charge 896 unnecessarily separated H1 calls.

For comparison, the six earlier idle intervals have old-port ranks
`17,9,35,9,53,9` on each side. The extra zero ports use
`18,9,36,9,54,9`, then final ranks `54,36,18,0` on each side.
The complete per-port idle masses are consequently 488 and 486.

| Complete optimistic invoice item | Raw rank mass |
|---|---:|
| Nine local words | 45630 |
| Common-chart boundary children | 1792 |
| Original ports' idle work, `112 x 488` | 54656 |
| Additional ports' idle work, `16 x 486` | 7776 |
| Maximum retained helper-width deletion, `9 x 2990` | -26910 |
| Total before any residual consumer | **82944** |
| Productive normalization, `81 x 1024` | **82944** |

This equality rules out a positive kappa for this emitted geometry even
if its scalar residual is inverted for free. The argument uses a positive
remaining child list: ideal exact-width helper hosting can delete at most
26910 units of idle rank. Every completed positive remaining profile has
at least 82944 units of rank. For a positive saving exponent `a`, each
positive child rank `r<81` has

\[
(r/81)^{1-a}>r/81.
\]

Thus the normalized recursive moment exceeds one. This is not an argument
that applies concavity indiscriminately to a signed cost expression, nor
is it a universal lower bound for every possible initial or final chart.
The independent invoice review confirmed the stated positive-child model.

The native phase check is exact. It represents each Fourier multiplier as
a degree-at-most-two polynomial modulo 4, using
`parity(a.x) = sum a_i x_i - 2 sum_(i<j) a_i a_j x_i x_j (mod 4)`.
A translation contributes twice a linear parity. All normalizations fix
the uniform vector, so no untested constant Gaussian phase remains.
Every emitted child has an orthonormal axis list, every scalar bridge joins
equal actual gauges, and all 1024 physical endpoints are FULL81 conditional
on the separately stated scalar residual cancellation. Omitting initial-normal
closure fails an explicit nonzero Fourier character. This phase calculation
extends by tensoring the verified native operators; it does not replace
the scalar controller or dirty-helper proof.

## 2. Partially common chart patterns

`partial_geometry.py` enumerates every subset `S` of stages 1 through 8.
A stage in `S` uses a fresh common 9-block. A remaining stage uses the
original normal `q_0` and eight fresh axes, as in the dimension-73 geometry.
The full dimensions are

\[
d_j=9+8j+\#\{s\in S:s\le j\},\qquad m=73+|S|.
\]

The current old-port normal is `q_j` at a common stage and `q_0` otherwise.
The rank census includes the same ten actual idle intervals and the same
initial-normal endpoint obligation as the complete geometry.

Each common entrance costs 224 H1. A return from a common stage to a fixed
stage requires `C_qprevious C_q0^-1` on Y. The normals lie in disjoint blocks,
so this is **112 H2**, followed by the explicit `q_0` translations. Counting
two H1 instead would overprice a legitimate fused rank-2 operation.
Each fixed entrance uses the retained inverse virtual-normal line on both
zero-port banks, for 32 H1.

This is an exact rank census for those specified gauge formulas. It does
not replay the native program for all 256 patterns, establish their complete
finite helper allocations, or claim a query-child deletion. The all-common
81-dimensional phase program is replayed here; the all-fixed 73-dimensional
phase program is retained in the predecessor scope.

The independent `invoice-experiments/partial_tariffs.py` screen applies
the exact retained moment engine, the literal H1/H2 boundary tariffs, and
an optimistic price for remaining idle work at each pattern's largest
available idle rank. At the retained target, **all 255 nonempty patterns
fail even with a free residual consumer**. The best nonempty pattern is
`S={7,8}`, dimension 75; its extra-H8 allowance is already approximately
`-5.16966896734`. The empty pattern retains an optimistic allowance of
`7.60767374010 H8`, before the extra obligations of a complete consumer
and finite allocation are supplied. See the independently generated
`invoice-experiments/PARTIAL-TARIFFS.json` for rational enclosures.

There is therefore no reason to construct hundreds of full phase traces
or infer a saving from a scalar rank reduction in this tested family.

## 3. Why a fixed scalar gather cannot precede the native lines

The actual scalar query matrix `R` has rank 8 and 112 nonzero columns.
Its 112 norm-one source labels `q_p` are distinct. Consider the physical
boundary component

\[
T=R\,\operatorname{diag}(C_{q_p}).
\]

Suppose it were implemented by a source-independent scalar pregather `A`
on the port index, followed by an arbitrary operator on the gathered fields.
On Fourier character `xi`, the rows of
`R diag(i^(q_p.xi))` must lie in the row space of `A`; otherwise a vector
in the pregather kernel could have a nonzero desired output. The zero
character gives the rows of R itself. Since

\[
i^{q_p\cdot\xi}=(1+i)/2+(1-i)(-1)^{q_p\cdot\xi}/2,
\]

the same row space must contain every row of
`R diag((-1)^(q_p.xi))`.

For each source column `p`, choose `k` with `R[k,p] != 0`. Exact Fourier
character isolation gives

\[
\frac{1}{512R_{k,p}}\sum_{\xi\in\mathbb F_2^9}
(-1)^{q_p\cdot\xi}
R_{k,:}\operatorname{diag}((-1)^{q_t\cdot\xi})=e_p^T.
\]

The verifier checks every term's accumulated column coefficient exactly.
All 112 independent coordinate rows are necessary: **a fixed scalar
pregather envelope smaller than 112 cannot implement this boundary**.
The later operation may be arbitrary; increasing its recursive rank cannot
restore source information discarded before it starts.
The same obstruction holds on any positive number of tensor layers: choose
a Fourier character that is zero on every layer except the first. Its native
multipliers are exactly the one-layer multipliers used in the proof.

A concrete failure uses source ports `0,7,27,57,76` with coefficients
`-1/2,1/2,-1/2,-1/2,1`. Their R query is zero. Place this coefficient vector
on Fourier character `xi=1`. Applying the actual positive native C_q lines
and gathering produces, at address zero,

\[
(0,1-i,1-i,0,0,0,0,0).
\]

The exact Gaussian calculation checks all 512 coordinates of this input
and output Fourier vector. It does not claim to test 512 independent input
columns. An equal-label positive control confirms that a genuinely common
native line can commute through a scalar gather.

Each query row's 56 label support spans an 8-dimensional binary hyperplane.
Their unique nonzero annihilators are
`42,7,25,52,82,127,97,76`. Each is norm one, but their binary Gram matrix
is all ones: **they are not an orthogonal frame**. Individual support
hyperplanes do not supply a simultaneous orthogonal query chart.

### The single-layer affine formula is not a tensor shortcut

On one layer, `C_q=a I+b X_q`, where `a=(1+i)/2` and `b=(1-i)/2`.
On two layers, the true operator applied to a point mass has amplitudes
`a^2,ab,ba,b^2`; in particular, the two cross-layer amplitudes are 1/2.
The proposed diagonal-cover replacement `a I+b (X_q tensor X_q)` has
zero cross-layer amplitudes. The verifier checks this exact rejection.
Consequently the one-layer formula cannot erase a recursive native child
by being applied unchanged to the tensor cover's rank-zero translation
grammar.

These obstructions leave routed or native pregathers, source-dependent
query charts, interstage sharing, and producer retiming open. They do not
certify any general minimum number of native children.

## Open next questions

1. Can a native query stage be shared while preserving its actual owner
   charts and dirty-helper release contract? A useful first step is one
   exact adjacent-stage word with a literal removed child. The scalar
   pregather obstruction identifies why merely reducing the number of
   scalar query coordinates is insufficient.
2. Can an existing helper entry or return be retimed so a native boundary
   line is already present in another paid child? Bind the changed local
   trace first, then charge the exact lost owner-tail capacity. The
   neighboring entry-retiming work addresses this smaller target.
3. Can another initial/terminal chart family improve the invoice without
   paying the closure ranks exhibited here? Any candidate must name both
   physical endpoint gauges and the admitted terminal owner permutation;
   this package has only ruled out its explicit family.

## Attribution and scope

The retained PR3734/dataisfire construction, PR3682 and earlier native,
owner, and outer suppliers, Ali Romman's source-code construction, and
all authors credited by the pinned follow-up package retain their credit.
The prior symmetric transition and alternating-record analysis are used
as frozen research inputs. This continuation supplies new local research
code and evidence, with substantial OpenAI Codex assistance, under the
repository's Apache-2.0 license and inherited notices. No external claim,
post, pull request, or selected-frontier change is made by this package.
