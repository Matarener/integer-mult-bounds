# Field-l2 precision scope and ordinary work

`precision120.py` replays every rational prefix of T,T^-1 and their actual
chronological linear transposes. For a matrix P,
||P||2^2 <= ||P||1 ||P||infinity. Max row-l1 times max column-l1 therefore
bounds every prefix. The120^2 batches within one selector axis act on
disjoint sets of fields, so their norm is the maximum block norm. After
three owner axes the largest squared bound over all four orientations is
14320735522816/15. The integer S=977096 bounds each full three-axis stack
and each of its prefixes. It is not raised to43200.

Each physical L word, P/D/X/phase and positive Gaussian child is unitary
at every positive field width. Scalar owner coefficients act once. A
partial K output accumulation has absolute row and column sums at most7.
Keeping the unchanged mains and scratch together bounds its extended norm
by sqrt(1+7^2)<8. SWAP is unitary and CLEAR is contractive; completed
disjoint cubes have norm1. The same bound covers the reversed linear
adjoint. Ordinary zero scratch supplies no input error of its own.

Use C=8*1351*S^2 for an E or Ei code and its linear adjoint. COPY of a
set of original coordinates has norm at most2, modal scatter has norm at
most1+max|lambda|=1351, and the gather/scatter recoders contribute S^4.
Thus Qbound=2*1351*S^4 bounds the query pair. Source contact snapshots have
norm at most2 as a set. The remaining native triangular ADD stage has
norm at most1+7=8, using absolute coefficient row and column sums, including
partial sums. Therefore16 covers native inverse contact acquisition and
its reverse transpose. Source/target halves can be separated by E code
and query because their factors2 and8 are applied to those separate passes.

A uniform local module bound is M=16*C^2*Qbound <2^202. The three modules
and three positive ordinary exit codes are bounded by M^3*C^3 <2^764.
The four recoder orientations also bound reversed adjoint prefixes, hence
the corresponding suffix maps; COPY/CLEAR ownership is transposed exactly.
These are deliberately loose finite constants, with exact integers in
`PRECISION120.json`.

If L primitive error injections each have l2 norm at most epsilon over
the collection of whole fields, final local l2 error is at most L*M*epsilon.
The bound is independent of positive address width. A per-coordinate
rounding convention can add a square-root dimension factor. This package
does not assert a fixed extra coordinate precision, storage bound, or
all-size Turing-machine closure; those require a separate allocation and
an admitted negative terminal.

For the odd3 local module the conservative unified ordinary upper bill is:

| operation | count |
|---|---:|
| ADD |2,829,471,232|
| SCALE |29,074,432|
| SWAP |34,905,600|
| P |39,744,000|
| D |39,744,000|
| X |34,560,000|
| phase |10,368,000|
| COPY |1,750,016|
| owned zero |5,206,016|
| CLEAR |6,956,032|

This dominates both F and B orientations and keeps COPY/zero/CLEAR
separate from paid calls. The local paid bill is V each of H8,H9,H15,H16
plus22016 H25, with V=120^3. The global inverse/forward owned peak is at
most V+22016+512=1,750,528 fields. Sequential three-stage reuse obeys the
same peak. The exact base120 primitive counts and smaller actual peaks
are in `MACROS120.json`; the global upper is a structured loop count.

No owned field is counted as productive helper mass. No query is credited
below full H25 on the strength of modal support geometry. No conditional
budget margin is presented as a supplier, exponent, or scientific adoption.
