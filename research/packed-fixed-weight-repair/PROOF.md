# A rational series for fixed-weight agreement

## Cited premise and the new claim

Use the original packed selected-bit primitive with `B=2^K`, `K>=6`,
`m=f-1` used source bits and `0<=rho<K`. Fix the source pattern
`c=(c_0,...,c_(m-1))`. Both dirty fields range over their complete sets.
Hanson Sun / bbMisk's PR #1245 proves that if the one positions are
`j_1<...<j_w`, the agreement fraction is

\[
 a(c)=\prod_{t=1}^{w-1}(1-2B^{-(j_{t+1}-j_t)}).
\]

For `w<=1` this is an empty product, equal to one. That theorem, including
its dirty restoration and inactive-suffix statements, is a dependency.
It is not proved or replayed here. The new claim concerns the sum

\[
 A_{m,w}=\sum_{c\in\{0,1\}^m,\ |c|=w} a(c).
\]

For any real `B>=4`, these numbers have formal generating function

\[
 F(z,u)=\sum_{m\ge0}\sum_{w=0}^m A_{m,w}z^m u^w
 =\frac{B+(2u-1)z}
 {B-(B+1+(B-2)u)z+(1-u)z^2}.                 \tag{1}
\]

The formal-series argument works over the rational functions in `B` as
well. For the binary gadget, the exact forward failure density, and also
the density of its correction-permutation support on the union of these
complete fibers, is

\[
 \delta_{m,w}=1-\frac{A_{m,w}}{\binom mw}.     \tag{2}
\]

Every source pattern has the same number of dirty-field values, so uniform
sampling of source patterns makes their fractions average with equal
weights. The predecessor's support-permutation argument acts within each
source fiber and gives the same correction-support fraction. Unused source
bits, inactive suffixes and spectators must have equal multiplicities for
these fibers, or the source weights must be specified separately.

## Unique decomposition by gaps

There is exactly one all-zero word of every length, contributing
`1/(1-z)` to `F`. A word with `w>=1` has a unique decomposition into:

* a nonnegative number of leading zeros;
* its first one;
* `w-1` gaps of lengths `d>=1` from one to the next;
* a nonnegative number of trailing zeros.

A gap of length `d` accounts for `d-1` zeros and the next one, so it
contributes length `d` and agreement factor `1-2B^-d`. Define

\[
 G(z)=\sum_{d\ge1}(1-2B^{-d})z^d
 =\frac{z}{1-z}-\frac{2z}{B-z}
 =\frac{z(B-2+z)}{(1-z)(B-z)}.
\]

Leading and trailing zeros contribute two factors `1/(1-z)`. The first
one contributes `uz`, and each subsequent gap contributes `uG(z)`. Thus

\[
 F(z,u)=\frac1{1-z}
       +\frac{uz}{(1-z)^2}\sum_{k\ge0}(uG(z))^k
 =\frac1{1-z}+\frac{uz}{(1-z)^2(1-uG(z))}.    \tag{3}
\]

Each coefficient has finitely many decompositions, so all products and
the geometric series are legitimate formal power series. Substituting
`G` into (3) gives numerator

\[
 (1-z)(B-z)-uz(B-2+z)+uz(B-z)
 =(1-z)(B-z+2uz).
\]

Cancel the formal unit `1-z` and expand the denominator. This gives (1).
No source independence assumption, random gap approximation or numerical
interpolation enters this identity.

## Coefficients, recurrence and exact finite counts

The length-zero and length-one polynomials are `A_0(u)=1` and
`A_1(u)=1+u`. Multiplying (1) by its denominator and comparing every
coefficient of length `m>=2` gives

\[
 B A_{m,w}=(B+1)A_{m-1,w}+(B-2)A_{m-1,w-1}
             -A_{m-2,w}+A_{m-2,w-1}.         \tag{4}
\]

Entries outside `0<=w<=m` are zero. This proves the recurrence at every
length and weight. At fixed length `m`, (4) needs only the two previous
rows and at most a quadratic number of arithmetic operations to produce
all rows up to `m`. This is an arithmetic-operation count, not a bit-time
bound for physical execution.

For an integer radix, put `S_0=[1]` and, for `m>=1`,
`S[m,w]=B^(m-1) A[m,w]`. These are integers. Indeed the gap-product
denominator for one pattern is `B^(j_w-j_1)`, and its span is at most
`m-1`. The initial rows are

```text
S_1 = [1,1],    S_2 = [B,2B,B-2].
```

For `m>=3`, multiply (4) by `B^(m-2)` to obtain the integer recurrence

```text
S[m,w] = (B+1)S[m-1,w] + (B-2)S[m-1,w-1]
         - B S[m-2,w] + B S[m-2,w-1].
```

In the binary gadget, there are `B^(2m)` pairs of active dirty digits per
source pattern. Their total agreeing count at weight `w` is therefore
`B^(m+1) S[m,w]` for `m>=1`; for `m=0` it is one. Spectator multiplicities
multiply agreement and total size equally. This converts the fractions
into actual finite address counts whenever the declared complete-fiber
domain is supplied.

At `m=3,w=2`, the patterns `110,011,101`, written low bit first, have
agreement `1-2/B`, `1-2/B`, `1-2/B^2`. Hence

\[
 \delta_{3,2}=\frac{4/B+2/B^2}{3}.
\]

For `B=64`, this is `43/2048`, distinct from both the unrestricted mean
and the fixed-weight worst case. This is a new exact aggregation of the
predecessor's formula; its per-pattern values are inherited.

## Verification boundary and implementation bounds

The verifier compares the new integer recurrence with direct enumeration
of the cited gap product at every weight through length 14 and radices
`4,6,64,128`. It also checks empty, zero-weight, one-bit, all-ones and
unrestricted-source marginal identities through length 128. These checks
corroborate (1), and do not audit the eight-gate program or prove its
gap-product premise. The written unique-decomposition argument supplies
the all-parameter conclusion. The complete multiplier, physical layout,
native delivery, uniform compiler, precision/tape and recovery remain
outside scope. There is no new kappa or selected-frontier update.

All verifier loops have fixed finite bounds. The arithmetic API accepts
only even integer radices from 4 to 65536 and lengths at most 128; the
enumeration uses at most `2^14` patterns per length and radix. Every
function is shorter than 60 lines, calls are direct, there is no recursion
or dynamic code, and checks use explicit exceptions under both normal and
optimized Python. No compiler or external library is needed; registered
commands enable warning errors. Python runtime allocation is a deviation
from fixed-allocation execution: at most `129^2` integer table cells are
live per recurrence, their values have at most 2177 bits since
`0<=S[m,w]<=2^m B^(m-1)`, and enumerated patterns are consumed one at a
time. This does not bound the interpreter's internal allocator overhead.
If these API limits are raised, the capacity and replay-time bounds must
be reconsidered. The package has no steady-state or constant-allocation
claim.

The default verifier only reads its six named source files and receipt.
The explicit receipt writer creates one new path exclusively, refuses an
existing path, checks the write length and closes the handle on all exits.
No file, network or process lifetime is hidden in the arithmetic routines.

The gap-product theorem and classical generating-series operations retain
their authors' credit. The new fixed-weight series and recurrence were
produced by Nick Petalas. Independent human and formal proof-kernel review
are unclaimed.
