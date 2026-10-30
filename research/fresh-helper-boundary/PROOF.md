# Proof and conditional transfer

## 1. Boundary contract

Use the source full-identity native unit with 632 independent persistent
fields: 224 main fields and 408 helpers. Its two orientations give the source
main shears, while every helper is autonomous in its own logical reference.
The separately owned C0 field is cleared before each use and at return. No
arbitrary persistent input is overwritten or cleared.

A field at frame f has physical value `C_f z`, where z denotes its logical
value and `C_f` is the source canonical Fourier frame. At entry this means
`z=C_start^-1 x` for an arbitrary physical input x. It does **not** require
precomputing a Fourier transform of x for free. The helper's actual final
operator is `C_end C_start^-1`, not merely `C_end`.

For nested frame spaces S<T, pay the positive transport
`C_T C_S^-1`. The source exact compiler lowers this to a Fourier child of
rank `dim(T)-dim(S)` with monomial adapters. Every newly used edge is checked
by serializing and independently decoding its complete monomial/Fourier
factorization, comparing both Pauli tableau and exact zero-state phase.
The backward orientation uses the conjugate operation, and is checked
separately. The unchanged edges retain the pinned source phase evidence.

## 2. Retiming lemma

Keep scalar order and coefficients, main entrances and exits, every warp's
actual input/output frames and logical word, and the entire owned center
program fixed. Give selected scalar contacts a new common frame, and give
helpers new entrance or exit frames. Suppose every persistent frame path is
still nested and ascending and every scalar contact and fixed warp is legal.
Replace the old climbs by the direct climb needed before each next contact,
and complete each field to its declared final frame after its last contact.

This replacement has the same logical scalar/free-operator program. Indeed,
a transport changes `C_S z` to `C_T z`; it leaves z unchanged. At a common
frame, a scalar addition gives `C_f z_i+a C_f z_j = C_f(z_i+a z_j)`. A scalar
scale has the same property. The fixed physical warp and center contacts
retain their logical actions. Induction over the chronological word therefore
preserves every logical row as a formal expression in all independent inputs
and noncommuting warp words. No finite-order relation between warp symbols
or numerical Fourier characters is used in this argument.

Main boundary frames stay fixed, so the physical main operator is unchanged.
Every helper remains logically autonomous. Its new physical operator is
`C_end C_start^-1`; its full Clifford factorization gives a standard positive
Fourier transform of the stated width with rank-zero monomial input/output
normalizers. Apply those normalizers at the boundaries of the **whole** local
invocation. Helpers are fresh distinct inputs, so a helper normalizer cannot
interfere with a borrowed main idle or a different suspended call.

This argument also explains the source all-column lifting obligation. Retiming
uses the same formal gauge identity at every permitted column multiplicity;
it does not lift a sum by tensoring a matrix identity. New fixed coordinate,
phase and monomial generators must use the same allowed block lifts as the
source native contract. Their scalar coefficients and dimensions are finite.
The original source all-column/native and physical-tape hypotheses are
retained rather than inferred from a single nine-axis replay.

## 3. Literal finite construction

CHANGES.json pins 117 helper entrance changes, 42 helper exit changes and 395
scalar-frame changes against the actual forward word. Each scalar location
is identified by source phase and ordinal with its original frame. The source
backward word is matched against the literal inverse-transpose scalar action
at every corresponding contact before the same frame change is installed.
The program generator checks uniqueness and original-frame equality.

Resynthesis checks each source and target frame, permits only strict nested
positive persistent transports, and retains all eight complete rank-8 center
paths. It does not invent a cheaper center or omit an old response. Both
retained interpreters run on the actual resulting words with every one of the
632 persistent inputs arbitrary, plus an arbitrary owned-center entry column
which is erased legally. Every helper output equals its own input logically;
the main outputs are exactly the source forward/backward shears. This is a
finite exact operator replay, not a formal all-size theorem checker.

The exact local profiles are

```
H={4:26,5:2,7:29,8:42,9:309},
P={1:2253,2:515,3:445,4:102,5:40,8:8}.
```

The helper rank mass is 3,434 and paid rank mass is 5,290. The complete scalar
allowances stay 158,120 forward and 158,168 backward. The ideal formal prefix
row-L1 maxima stay 457 and 169. These figures are source interpreter counts
and ideal prefix bounds; physical monomial routes and rounded recursive
constants are handled by the finite-template prescription below.

## 4. Join the unchanged p7 word

Replace each of the 15 source local invocations by the new unit of its actual
orientation. The main operator and its native external reference are unchanged,
so the complete p7 main contact/owner construction remains the source one.
Replay the full rational Laurent program including both scalar boundaries,
all local calls, signed swaps and retained main idle windows. Its main endpoint
profile stays `{25:448,41:448,57:448,121:224}`. Every one of its 2,688 whole
main idle calls is retained, with its original physical owner and phase recipe.
Each of the 6,120 helper occurrences has a distinct independent input and its
own new whole-job boundary normalizers. Owned centers receive no productive
credit.

This gives exactly the T and P printed in README.md: 7,688 productive fields,
53,133 paid calls, target mass 133,718 and paid mass 133,110. The rank-one
surplus is 608. None of those scalar counts or the surplus alone establishes
an exponent.

For `F(C)=sum T_k k^(1-C)-sum P_r r^(1-C)`, outward rational intervals give
`F(.0027212601275)>0` and `F(.0027212601276)<0`. To establish a fixed-profile
ceiling, arithmetic.py encloses `sum (T_r-P_r) r^(1-C) log r` on each of 16
closed intervals covering `[0,1/20]`, and proves a strictly positive lower
bound throughout. Thus F is strictly decreasing there. On 128 further closed
intervals covering `[1/20,1]`, it bounds F directly strictly below zero. These
are interval implications for every real C in the covered intervals, not
extrapolation from point samples. The positive rank-one surplus at C=0 then
gives the unique relevant crossing and excludes any later positive region.

A chronological tensor power multiplies both moments. Paid completion of a
rank-K target by D axes changes its moment by `(K+D)^t-K^t <= D^t`, which is
at most the added paid charge. Splitting a paid job on disjoint axes increases
or preserves its t-charge. Hence tensoring, this paid completion and paid
splitting cannot pass the raw fixed-profile ceiling. This is not a ceiling
on different native profiles or other algorithms.

## 5. Pay both strictification tails

Let `C=.00272125`, `t=1-C`, `u=3/10`, `v=150`, `J=10^v` and `L=15^v`.
Use the chronological native product of PR4416 and PR4433, restoring every
whole-job matcher and center before resuming a suspended caller. The product
has target and paid moments `T_t^v` and `P_t^v`, respectively; it is a
substitution of whole array programs, not the tensor power of a sum.

Canonicalize each complete raw job with both recorded monomial factors; these
need not be an inverse pair. Subsequent placement on specified disjoint axes
is coordinate conjugation. No raw Clifford endpoint is assumed conjugate to
a canonical Fourier transform merely because its rank agrees.

After the product finishes, complete every productive rank K<L by a paid
transform on L-K disjoint axes of that same arbitrary physical field. Split
all original and added paid jobs into disjoint-axis jobs of rank at most J.
No new input or productive credit is introduced. Every final target has rank
at least L and every final paid job has rank at most J, with J<L.

For an original paid rank R>J, its split charge is at most
`2 R J^-C <= 2 R^(t+u) J^-u`, since `t+u>=1`. A completion has charge below
`2 L J^-C`. Therefore the complete normalized paid moment is bounded by

```
alpha^v + 2 gamma^v + 2 delta^v,
alpha=P_t/T_t,
gamma=P_(t+u)/(10^u T_t),
delta=7688*15/(10^C T_t).
```

The interval engine certifies `alpha<1-16/10^9`, `gamma<911/1000` and
`delta<173/200`. Bernoulli's inequality and an exact rational power test give

```
1/(1+150*16/10^9) + 2*(911/1000)^150 + 2*(173/200)^150 < 1.
```

Both original tails and every completion are paid. The product ambient rank
is `m=121^150`, with no need to materialize its immense word.

## 6. Uniform compiler, BIT and outer bill

Use the inherited finite integer mixed-target compiler only after strict
separation. Its fields, source complements, owned centers, integral batching,
matcher restoration and final exits are those of the specified new unit.
The new logarithmic majorant of PR4433 applies with `theta=6/7` and power 13:
`10^7<15^6`, `2*(10^150)^7 <= (121^150)^6`, and
`eta=t*121^(-150*C) > theta^13`. Its base-range condition is checked as well.
For declared `kappa=.00272124`, put `d=(C-kappa)/7=1/700000000` and uniform
saving `C-d`. The explicit integer comparison at `H=349300000000` is

```
(H+1)^13 < 2^499,  d*H=499.
```

It specifies a finite uniform supplier at `N=2^H` with the required strict
saving. The instruction list and integer width B_N are generated by the
source finite algorithm rather than emitted here.

The source BIT all-size parameter proof gives, before its last relaxation,
`(1-.003)*.00275 + .003*.0000384599 = .0027418653797`. Admit this unchanged
supplier at `.00273`; both the atom/adapter and borrowed-stock inequalities
remain strict. No BIT native word, cover or precision premise is weakened.
The old `.0027` relaxation fails the new outer bill and is a rejection control.

Set `b=kappa+5d`, `a=kappa+4d`, `q=kappa+3d`, `epsilon=1-d`, `beta=1-3d`,
`r0=d/10`, `stop=d` and `layout=d`. The complete retained ledger recomputes all
nine cost rows, 54 current strict predicates and three functional guards.
Every one is strictly positive at this point. Closed uniform/epsilon gaps,
the insufficient old BIT relaxation and the unfunded tested endpoint fail.

## 7. Costs and the precise conditional boundary

Replace the old finite-unit constants by counts of the actual new word:
3363 paid local calls, the complete unchanged scalar lists and coefficients,
new serialized monomial/phase generators, 632 persistent fields and one owned
C0, all 408 helper normalizers, the unchanged p7 bridges and whole idles, the
150-fold chronological substitution, every completion and split, and finally
every integer-compiler unit, route, owned bank and rank-one leaf. A literal
finite recursive enumeration defines their counts and coefficient heights;
no p3 raw count is substituted for the compiled word. The new transport and
helper recipes are available explicitly in NATIVE-RESULT.json.gz. Internal
normalizers are restored before resuming a caller.

Apply the source finite-template precision and stock argument with these new
constants. The native fixed coefficients and generators are finite, semantic
prefix bounds are rechecked, and all changed movement/scalar/normalizer work
enters the finite constants. The positive outer spare powers absorb those
constants after an effective threshold, under the inherited semantic,
all-column, physical primitive and fixed-tape hypotheses. This is the same
conditional transfer mechanism used by PR4416/4433, not a proof that local
savings are automatically a multiplication theorem.

Analytic decomposition, permitted physical movement and whole-job frame
realization, source all-column correctness, finite-template closure, fine-prime
padding, fixed-tape execution and exact recovery remain stated source premises.
There is no formal verification or independent human mathematical review of
the complete theorem, no practical implementation claim, and no selected-result
change. Source files and contributor attribution are retained.
