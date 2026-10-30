# Exact finite scalar and prefix consequences of the C01 replacement

This note concerns the two immutable PR3605 words at head
`3efbb5de06a49ffeea6684482f2d3fe48cdca3fb`. It checks the replacement produced in
the companion design package. It does not establish a new recursive bound,
physical Clifford implementation, or rounded native supplier.

## Models and input domains

The raw word has 704 historical register names, of which 72 are removed
identities. Every one of the remaining 632 logical inputs is an arbitrary
independent element. These comprise 112 sources, 112 targets and 408 helpers.
The 91 separate cleanup buffers enter at zero and must return exactly to zero.
The formal warp letters are independent invertible noncommuting operators.

For the full raw word, `check_word.py` checks all coefficients in the dyadic free
warp algebra. Its integer rows use a common power-of-two denominator and
canonical signed integer coefficients. A warp left-multiplies each formal
word and cancels only an adjacent inverse pair. No numerical specialization of
the warp letters is used for this endpoint check.

The inverse-transpose replay transposes and negates each ADD and inverts each
SCALE. Each dual warp letter represents `K^-T`, an independent free generator
in that orientation. Identifying it with `conjugate(K)` additionally uses the
inherited unit-modulus monomial premise; arbitrary invertibility alone is not
that premise. This is a separate interpretation of the same free-generator
names. The literal reverse inverse is also checked in each
orientation by reversing the entire chronological list and inverting every
gate. The two orientations and their inverses each cover all 632 arbitrary
input columns and all 91 required-zero buffer outputs.

A second, explicitly weaker model is the **complete scalar projection** of the
emitted local programs. Every scalar macro is expanded by binary Horner into
ADD, DOUBLE, HALVE, NEGATE, COPY and CLEAR operations. All nonscalar native
events act as the identity in this projection. CLEAR is the assignment of zero,
with unit cost; it is not being proved to be reversible physical erasure.
Logical inputs remain arbitrary, while the eight center registers, 91 cleanup
buffers and one coefficient work register start at zero. Exact symbolic rows
are maintained through every primitive, including every internal Horner step.

## Panel identity and availability

Write the original frame-zero compensation as

    (y,h) -> (y+C h,h).

The proposed target forest is an invertible unit shear product `T`, and the
helper preparation is a product `H` of 88 disjoint signed unit shears. The
literal chronological panel is

    T; H; +(T C H^-1) h; H^-1; T^-1.

At the correction cut the stored helper vector is `H h`. Consequently

    T^-1 [T y + (T C H^-1)(H h)] = y + C h.

Restoring `H` returns every arbitrary helper value. Neither preparation uses a
clean helper. The identity holds over every module over the dyadic rationals.
Its inverse subtracts `C h`; its inverse transpose adds `-C^T y` into the helper
bank. The finite check independently replays all four interfaces.

There are 207 helper coordinates used in the panel. All are live and absent
from both `start_extra` and `helper_final` of the pinned source words. The
pinned transport's definition therefore gives each entrance frame zero and
exit frame FULL. Both preparation and restoration occur in the existing
frame-zero compensation phase, before the native entry adapters.

The independent checker verifies that every field of the full word other than
`compensation` is unchanged. It also binds the raw panel to its compact
canonical register numbering and to every emitted zero-frame event. The
entire event suffix starting at entry adapters, and the entire nonscalar event
stream, are byte-semantically unchanged. This preserves their existing charges;
it does not price them at zero.

## Complete scalar invoice

For a reduced nonzero dyadic coefficient `a/2^d`, the literal binary-Horner
expansion costs

    p(a/2^d) = 3 + floor(log2(abs(a))) + popcount(abs(a)) + d

per real component. The three fixed operations are the initial work clear,
target addition and final work clear. Every numerator doubling, numerator
addition and denominator halving is included.

The following panel counts are the same for the base and extra providers and
in both orientations:

| Part | ADD macros | Primitives per real component |
| --- | ---: | ---: |
| Target preparation | 95 | 380 |
| Helper preparation | 88 | 352 |
| Residual correction | 1922 | 9169 |
| Helper restoration | 88 | 352 |
| Target restoration | 95 | 380 |
| Candidate total | 2288 | 10633 |
| Original panel | 5736 | 31214 |
| Historical C01 rank-basis panel | 3214 | 17334 |

The historical rank-basis panel is authenticated and freshly replayed on all
632 input columns in all four orientations. Its old receipt is not used as an
acceptance oracle.

The complete emitted scalar programs, including their unchanged scalar
suffixes, have the following literal prices:

| Orientation | Original | Candidate | Saving |
| --- | ---: | ---: | ---: |
| Forward, per real component | 79072 | 58491 | 20581 |
| Inverse transpose, per real component | 79096 | 58515 | 20581 |
| Forward, two real components | 158144 | 116982 | 41162 |
| Inverse transpose, two real components | 158192 | 117030 | 41162 |

There are 17449 original scalar macros and 14001 candidate macros in either
emitted orientation. All native event charges, the recursive child histogram,
helper identities, helper widths, private buffers and source-wrapper charges
are retained. This finite scalar saving supplies no change in a recursive
rank moment or exponent.

## Exact scalar-prefix and grid consequences

For the scalar projection, let `A_j` be the matrix taking the 632 initial
logical inputs to all logical and private registers after primitive `j`.
Private initial values are zero. The checker computes every row of every
`A_j` exactly, without rounding. Define

    M = max_j max_r sum_i abs((A_j)[r,i]).

The maximum is attained: the receipt includes an exact maximizing row, and
choosing each input's sign to match that row attains the row sum on the unit
input cube. These are exact scalar-projection range bounds, not physical
native-prefix norms.

| Orientation | Original M | Candidate M | Original/candidate extra grid bits D |
| --- | ---: | ---: | ---: |
| Forward | 302 | 302 | 4 / 4 |
| Inverse transpose | 169 | 181 | 5 / 5 |

The dual range bound becomes worse. It remains below 256 in both cases.
The forward bound remains below 512. For inputs bounded by `B` in absolute
value, all projected scalar registers are bounded by `M B`.

For any integer `g`, if all logical inputs lie on the grid `2^-g Z`, the
checked primitive prefixes lie on `2^-(g+D) Z`. This follows by writing the
computed matrix rows as integer numerators divided by `2^D`. The receipt
includes a primitive, register and input coefficient having an odd numerator
at the stated maximum denominator. Applying the corresponding basis input
`2^-g e_i` therefore needs exactly `D` extra fractional bits at that prefix.
One fewer extra bit cannot represent that input's exact intermediate value.
Thus `D` is both sufficient and necessary for exact common-grid representation
of this finite scalar projection over the unrestricted common-grid input
domain. It is not a minimum physical guard count for a native supplier.

On a fixed-point implementation of precisely this scalar projection, with
the stated exact input lattice and sufficient range, those grid bits make
every listed primitive exact. No rounding tie rule is exercised. This
conditional statement concerns the listed assignment/COPY primitives as
well; it does not establish an implementation of their physical contracts.

The checker separately propagates a cancellation-free positive envelope from
unit bounds on logical inputs and zero bounds on private inputs. It applies
the absolute coefficient to every source contribution and resets the envelope
on each CLEAR assignment. Its largest values are:

| Orientation | Original positive envelope | Candidate positive envelope |
| --- | --- | --- |
| Forward | 202390250292205836324211411723 / 512 | 277593730512244114269209832351 / 512 |
| Inverse transpose | 4091250694836343058381993950001 / 128 | 18499730109946033497554374971719 / 128 |

The least integer `b` giving a strict bound by `2^b` is 89 in both forward
cases and changes from 95 to 97 in the inverse transpose. These envelopes are
conservative; they are not the exact attained ranges `M`, a physical storage
invoice, or a local-defect/error-feedback theorem.

## Defect sensitivity and limits

Sixteen semantic panel controls per provider must fail after exact arithmetic:
omitted target preparation, omitted helper preparation, omitted helper
restoration, omitted target restoration, stale original correction instead of
the current pullback, a final literal sign error, and wrong target restoration
order in both orientations; plus failure to reverse the literal inverse and a
wrong dual sign. Every rejection has a concrete differing output row in the
receipt. These are mathematical failures rather than authentication failures.

The scalar replay observes nonzero linear forms at thousands of charged CLEAR
assignments, including eight final center clears. It records their counts
instead of treating those assignments as a strict-zero physical cleanup proof.
The 91 separate zero buffers do return to zero by literal exact computation
before their free events.

The results comprise finite exact symbolic computations, together with written
linearity and grid arguments covering every input in the stated domains.
No formal proof assistant or kernel certificate is supplied. The result does
not establish a globally optimal two-sided factorization, all-size native
precision, physical Clifford phases, rounded strict-zero cleanup, recursive
source access, complete tape costs, or a new multiplication exponent.
