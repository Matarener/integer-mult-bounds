# Conditional range and atomic-defect theorem for the two pinned 651-input words

This note separates an exact finite calculation from the general linear-algebra
argument that gives it an all-input interpretation. It does not prove a native
rounded supplier, a finite-precision implementation, or a new multiplication
bound. There is no formal-kernel proof.

## 1. Exact model and source domain

There are 651 public scalar coordinates and a private coordinate `p=651`.
The public entrance coordinates are partitioned into source `0..110`, target
`111..221`, and 429 arbitrary dirty helpers `222..650`. The private entrance is
zero. Arithmetic is over the integers for the finite calculation and over the
reals for the range/error theorems.

Both pinned words have 16,102 records. Their normalized atomic interpretations
are:

* `ADD(d,s,c)`: `z_d <- z_d+c z_s`, with `c=+1` or `-1`;
* `MOVE(d)`: identity on normalized coefficients, with the recorded paid rank;
* `COPY(s)`: `z_p <- z_s`;
* `ERASE`: `z_p <- 0`.

The literal reverse reads records backward, negates each ADD coefficient, and
exchanges COPY with ERASE. It is an inverse only on the appropriate ideal
reachable states. COPY and ERASE are noninvertible linear assignments on the
extended state space.

For every ideal prefix the checker proves that a copied source is unchanged
until its paired erasure and that the private value equals that source at
erasure. It proves zero private return and literal restoration of all 429
helpers. These ideal facts do **not** imply rounded cleanup. In particular,
setting the additive defect of ERASE to zero below still presupposes the
abstract zero assignment. It does not permit deleting a small physical residual.

The normalization assumes that native frame changes give precisely this scalar
model. Native child interiors, frame implementation, scratch, actual rounding
rules, finite exponent limits, and physical zero-return are outside the theorem.

## 2. Exact local prefix range

Let `R_t` be the matrix from the 651 public entrance coordinates to all 652
coordinates after the first `t` events, with the private entrance fixed to zero.
For a row `r` write

`a(r)=sum_source |r_j|`, `b(r)=sum_target |r_j|`,
`c(r)=sum_helpers |r_j|`.

The checker starts with the public identity rows and a zero private row, updates
the changed row under every event, and records every triple `(a,b,c)`. Unchanged
rows were already recorded. Consequently the saved set is the complete set of
block row norms over every row and prefix, including COPY values. It is not a
claim that every triple is a distinct exposed face of a minimal envelope.

For entrance block bounds `||x||_infinity<=X`, `||y||_infinity<=Y`,
`||h||_infinity<=H`, every ideal prefix coordinate is bounded by

`max_(a,b,c in envelope) (a X+b Y+c H)`.

This follows by the triangle inequality on each exact row. For `X=Y=H=1`, the
maximum is exactly `max_t ||R_t||_infinity`: choosing the entrance signs of a
maximizing row attains its row L1 norm. The saved maximizing row and signs are
independently replayed by scalar forward evaluation.

| Word | Forward exact maximum | Literal reverse exact maximum |
| --- | ---: | ---: |
| Parent, gzip `1a6841fc...` | 34,285 | 5,839,860 |
| Candidate, gzip `e8026111...` | 80,639 | 239,014 |

Thus the forward maximum increases. Only the literal reverse maximum decreases.

The exact endpoint has the integer form

`(x,y,h) -> (A x, y+T x+E h, h)`.

The checker verifies the source/target support and the identity target self
block before using it. The largest absolute row sums of the indicated blocks
are:

| Word/direction | `A` | `T` | `E` |
| --- | ---: | ---: | ---: |
| Parent forward | 12,711 | 26,235 | 224 |
| Parent reverse | 136,165 | 5,839,659 | 224 |
| Candidate forward | 15,675 | 70,795 | 224 |
| Candidate reverse | 5,521 | 238,823 | 224 |

`T=A` is not asserted over the integers. Helper leakage is even but need not be
zero over the integers.

## 3. Source code and controller binding

The source code is the actual subsequence of ADD records in phases 21 through
24: respectively 474, 504, 47, and 474 ADDs, for 1,499 total. Its endpoint equals
the full local word's source endpoint in each direction. Reversing these ADDs
and negating their coefficients gives the exact inverse on all 111 columns.

| Word | Source forward prefix / endpoint | Source reverse prefix / endpoint |
| --- | ---: | ---: |
| Parent | 22,961 / 12,711 | 136,165 / 136,165 |
| Candidate | 15,675 / 15,675 | 5,521 / 5,521 |

The controller file has a historical 6,372-gate `inplace_code_CNOTs` list. Its
binary endpoint differs from the selected 1,499-gate code in nine rows. Therefore
the calculation is **a new source-selected instantiation of its abstract
ordered schedule**, not a replay of that historical gate list. Both endpoints
and the first mismatch are recorded.

The reason the schedule still applies in the binary VALUE model is independent
of that historical list. Write `Abar` for the selected source matrix modulo two.
The full local coefficient calculation verifies, on all columns,

`F_Abar(x,y,h)=(Abar x,y+Abar x,h)`,

and its literal inverse is

`F_Abar^-1(x,y,h)=(Abar^-1 x,y+x,h)`.

At a reverse stage the controller supplies source `Y` and target `X`. Thus its
abstract pair updates, with `G_s=Abar` at an even stage and `G_s=Abar^-1` at an
odd stage, are

`forward: (X,Y) -> (G_s X,Y+G_s X)`,

`reverse: (X,Y) -> (X+Y,G_s Y)`.

Code sweeps left-multiply their selected bank by the listed generators. Bridges
are the two prescribed binary bank shears. Idle endpoints preserve normalized
values and advance the native chart; the terminal exchange swaps each pair.

The checker evaluates every prefix on eight independent formal bank variables
in the free noncommuting polynomial algebra over GF(2). Its final diagonal is
`G_8 G_7 ... G_0` on all eight variables. Polynomial evaluation proves that this
identity holds for any linear maps substituted for the generators; no
commutation assumption is made. The stage updates above bind the selected
local word to this identity. Native chart/owner implementation and a physical
supplier remain separate premises. The identity is binary, and does not
replace the different integer `T` and `E` blocks in a range calculation.

## 4. The complete ordered range recurrence

Maintain nonnegative bounds `n[p][side]` for the eight DATA banks, initially one.
Suppose all completed native frame, idle, address and owner maps preserve the
chosen norm, hosted helpers restore literally, and the actual source-selected
codes are available at the scheduled charts.

For a source code with exact prefix norm `P` and endpoint norm `U`, update

`global_prefix <- max(global_prefix, P n)`, `n <- U n`.

For a local call, let `x,y` be the current source and target bank bounds and let
`h=max_(all current banks) n`. Use its complete envelope to enlarge the running
prefix bound by `max(a x+b y+c h)`. With its exact endpoint block bounds
`U,T,E`, update the source to `U x` and target to `y+T x+E h`. Other bank
endpoints are unchanged because helpers restore. Using `h=1` would be
unjustified: hosted helpers may be in banks already enlarged by code sweeps.

Each ordinary bridge has coefficient `+1` or `-1`. The triangle inequalities
give `n[d][X] += n[s][X]` and `n[s][Y] += n[d][Y]`. These two sources are not the
two just-modified destinations. Exchange only permutes the bounds.

Induction over all 56 ordered controller events proves the saved bound.
The receipt lists every intermediate bank bound, all 35 forward and 28 reverse
source-code factors, five forward and four reverse local calls, 18 bridge
shears, ten isometric idle events and the exchange. No factor is inferred from
an endpoint-only norm.

The resulting coefficient upper bounds have bit lengths 458 and 401. These
are valid upper bounds under the stated scalar instantiation and isometry
premises, not exact global maxima.

For an additional per-bank inverse decode of `G_8...G_0`, there are five reverse
and four forward source-code factors. Every source prefix norm is at least one.
Hence the product `P_forward^4 P_reverse^5` bounds each prefix of that decode.
Multiplying the running bound by it gives bit lengths 601 and 519. The eight
bank decodes are independent; multiplying this factor eight times would be
unnecessary. Any additional normalization wrappers are assumed isometries.
This is a range bound for that conditional sequence, not a proof of terminal
decoder correctness or admission.

The reported 64-bit block ceilings are respectively 512 to 448 and 640 to 576.
They are ceilings of coefficient-growth bit lengths. Actual signed storage
width also depends on input magnitude, errors, fractional grids, scaling and
internal native prefixes; no concrete precision saving follows here.

## 5. Exact atomic additive-defect constants

The following argument applies to every finite real linear word, including
noninvertible assignments. Number its matrices `M_0,...,M_(m-1)` and let

`S_i=M_(m-1)...M_(i+1)`, with `S_(m-1)=I`.

Use matched ideal and perturbed entrances. An independent scalar defect
`delta_i` is added to the single destination coordinate `d_i` immediately after
event `i`. Linearity and induction give the identity

`error_final = sum_i S_i e_(d_i) delta_i`.

This identity holds for every real entrance and defect choice. The receipt's
domain is the fixed two 652-coordinate words, with their chosen assignment
extension. It does not infer any actual rounding rule or independent-error
behavior of a native implementation.

For any subset `I` of defect locations and `|delta_i|<=epsilon` there,
with other defects zero, define

`C_I=max_output_r sum_(i in I) |(S_i)_(r,d_i)|`.

Then `||error_final||_infinity <= C_I epsilon`. This constant is exact for the
stated independent-error model: choose a maximizing output row `r*` and
`delta_i=epsilon sign((S_i)_(r*,d_i))`. That output equals `C_I epsilon`.
This sharpness does not assert that these errors can be generated by rounding
while satisfying physical copy/erase preconditions.

The commonly used `sum_i max_r |(S_i)_(r,d_i)|` is a generally looser bound.
The checker retains the row sums before taking the maximum. For groups with
different uniform allowances, the exact constant is
`max_r sum_g epsilon_g sum_(i in group_g) |(S_i)_(r,d_i)|` for a disjoint
partition. Saved per-group row vectors permit this calculation; overlapping
summary groups must not be counted twice.

The sparse-column reverse recurrence is:

* ADD `d<-d+c s`: column `s <- column s+c column d`;
* COPY `p<-s`: column `s <- column s+column p`, then column `p <- 0`;
* ERASE: column `p <- 0`;
* MOVE: unchanged.

These formulas are right multiplication `S <- S M_i`. They include the
assignment's destruction of an old private value. Each destination column is
read **before** this update because the error is injected after that event.
The complete ordered destination-column stream is hashed.

The reported exact aggregate uses every ADD, MOVE and COPY, with ERASE defects
zero but the abstract ERASE assignment still assumed:

| Word/direction | Exact `C_I` | Loose sum of per-event maxima |
| --- | ---: | ---: |
| Parent forward | 880,068 | 965,052 |
| Candidate forward | 1,081,994 | 1,099,680 |
| Parent reverse | 34,848,225 | 34,872,847 |
| Candidate reverse | 1,255,309 | 1,289,381 |

Allowing defects after ERASE leaves these four aggregate maxima unchanged,
although it adds a private-coordinate row and raises each loose sum by one.

If only MOVE and COPY have defects, the exact forward constants are 383,045
and 479,557; the reverse constant is 1,239 for both. Every reverse paid-rank
group is unchanged. Therefore the large reverse all-event improvement concerns
ADD-defect sensitivity; it is not a reduction of this MOVE/COPY aggregate.

## 6. Finite witnesses and limits

All four full scans cover every record and every paid rank. Peak single-defect
influences are 3,457 / 86,476 for the parent forward/reverse words and
3,935 / 4,366 for the candidate. Each saved peak impulse is independently
propagated forward. For each aggregate, a separate scalar-adjoint pass produces
the attaining error signs, and direct forward evaluation of all simultaneous
errors attains the claimed constant. Local range peaks and maximum suffix row
norms also have directly evaluated sign witnesses.

Source-specific negative controls detect a wrong adjoint direction, reversed
suffix order, ignoring a real COPY, and replacing the required error signs by
all-positive errors. These execute after source authentication and operate on
the actual source events.

The all-input arguments above are written linear-algebra proofs. The reported
numbers, symbolic schedule identity and witnesses are finite exhaustive exact
computations for the pinned words. They do not establish an all-size native
precision theorem, a formal-kernel result, physically legal rounded cleanup,
error propagation through the 63 global code factors, general sign optimality,
or an improved supplier/exponent.
