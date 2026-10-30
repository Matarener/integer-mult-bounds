# Conditional dependency, admission and endpoint proof

Hiroki Kumazaki with substantial OpenAI Codex assistance. Apache-2.0.

## 1. Literal closure

Give every initial bank a distinct state version. Each transport/sign depends
on its preceding bank version; ADD depends on both the preceding target and
current source; zero has no value predecessors; erase depends on its current
private value. The least predecessor-closed set containing an observation is
its graph ancestor set. This proves the SSA algorithm's literal minimality.

For any touched private lifetime, also require its matching erase. Iterate
predecessor closure and this requirement to a fixed point. Each iteration only
adds vertices in a finite graph, so it terminates. Any legal set satisfying
these two conditions contains every iteration, hence contains the result.
This minimality is graph-theoretic, not a lower bound against cancellation or
alternative schedules. The independent reverse scan propagates live demands
through precisely the same literal instructions without constructing this DAG.

The 675 observations use the exact published PR3423 port-index hash. At an ADD
observation, predecessor closure retains both the current recipient history and
the actual source history. Running retained instructions in their original
order therefore yields each observed ideal value, by induction. Private erase
checks prove exact zero scalar rows, rather than silently discarding dirt.

The original 146 endpoint observations require 265 inputs. Requesting the
original endpoints of those 265 inputs adds 215 events and no new inputs.
This is a selected-output projection. Other outgoing effects are not implied
by preserving its selected endpoints; they are explicitly listed separately.

## 2. Native premise and normalized rows

Assume the relevant initial and current chart maps `A_H` are unitary
automorphisms of `B9`, and every used native transport has its archived operator
`T_(H->K) = A_K A_H^-1`, and that each complete native primitive is unitary,
preserves `B9 = E Z[i]^512`, and is exact for the admitted module on the common
grid. These are the existing chart/module implications, not consequences of
our file hashes. The new check binds all used occurrences to their source data.

Put `z_s = A_initial(s)^-1 v_s(0)`. Induction gives

`v_b(t) = A_frame(b,t) sum_s r[b,s,t] z_s`.

Transport changes the outer frame only. Common-frame ADD performs the literal
rational row addition. Sign negates a row. Private zero creates the zero row;
erase is allowed only for the zero row. These arguments quantify over arbitrary
independent dirty initial arrays, not just the three numerical fixtures.
The final formula keeps both frame factors; neither initial X frames nor final
Y frames can be dropped.

The exact retained matrix shows normalized restoration of 213 non-X banks and
an identity X diagonal plus a rank-9 Y map on the 52 X endpoints. The rank is
computed by corrected rational pivot elimination, with duplicate/dependent-row
regressions. A separate explicit factorization expresses all 52 rows using
nine named rows and verifies every coefficient; a 9-by-9 minor of those rows
has determinant `-1/128`. These give the matching upper and lower rank bounds. The separate literal fixture interpreter
checks projection/full ideal-word agreement but is not the universal proof;
the induction and complete exact rows provide that statement.

## 3. Minimal independent dyadic product entrance

Restrict each independent initial bank to `2^k_s B9`, `k_s >= 0` an integer.
The chart automorphism premise makes each normalized `z_s` independently
arbitrary in that same module. For any one row, its output lies in `B9` for all
such inputs if and only if `r[b,s] 2^k_s` is an integer for every source s.

Sufficiency follows from integer linear closure of B9. For necessity, set every
other input to zero and choose `z_s = 2^k_s E e_0`. Applying `E^-1` to that row
leaves its nonintegral scalar coefficient in the zeroth coordinate. The outer
chart is an automorphism, so it cannot repair nonmembership. All coefficients
are real dyadic rationals; the maximum reduced-denominator exponent over every
retained row is consequently the coordinatewise-minimal k_s.

The computed maxima are two for all 104 Y inputs, one for the 38 listed N
inputs, and zero for the other 123. Reducing any positive exponent by one is
rejected using its actual coefficient witness (142 cases). This is a condition
for the retained *prefix invariant*. It does not characterize correlated inputs
or domains admitting only the final cut. N33/N34's omitted full-word half-reads
are not licensed by this projection's weaker entrance.

Every retained ADD includes its before and after rows. Under this entrance both
are in B9, hence their difference—the actual increment—is also in B9. Thus
rational coefficient divisions are exact on the common grid. Native prefix
exactness uses the separate inherited module premise; scalar rows alone do not
verify a native circuit's phase or intermediate rounding.

The event-312 witness is stronger than an odd-integer half: `N100(x)=2*x_0`
is in B9 because its only nonzero Newton coefficient is `2/(1+i)=1-i`.
No instruction has touched N100 before its half-read. All other banks remain
zero beforehand. Its arithmetically exact half `x_0` has coefficient
`1/(1+i)=(1-i)/2`, outside the Gaussian integers. `4*x_0` is the positive
2B9 control. This satisfies every original 63-bank entrance assumption and
exhibits an independent external admission obligation.

## 4. Conditional payload width

Let H bound each real and imaginary physical input component across the 265
inputs. Each 512-entry complex vector has Euclidean norm at most `32H`.
Unitary initial chart normalization preserves this norm. Triangle inequality
and the exact row identity give `||v_b||_2 <= 32H sum_s |r[b,s]|`.
The retained maximum is `127/2`, first at event 3589, so `2032H` bounds each
payload component. Unitary complete native prefixes preserve the entrance norm;
partially written disjoint components inherit a bound from their before/after
stage. This reproduces the retained norm estimate on the actual recipient
slice, not a new global estimate or a physical storage theorem.

H itself, initial domain preparation, physical allocation, scratch layout,
movement, controls, exposed codecs and recursive interfaces still need a paid
caller. The unchanged-profile `599/584` stop is unaffected.
