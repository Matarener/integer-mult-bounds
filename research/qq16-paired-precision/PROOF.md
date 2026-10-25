# PR4106: range, rounding and the 800-unit saving

This is a scoped numerical audit of the unchanged PR4106 word against PR4015.
Endpoint/frame identity and the logical inverse are inherited from their pinned
proofs, not reproved by importing their executables. The new interpreters execute
neither predecessor code nor the canonical decoder verifier. Exact retained bytes,
source heads and canonical semantic inputs are authenticated before analysis.

## 1. Common sufficient format for every tensor depth

Let lambda>=1, t=lambda-1, h=2^z with integer z, and integer P>=0. Every real and
imaginary component of the 224 borrowed entry fields must belong to hZ and have
absolute value strictly below B=2^P h, uniformly over owners and payloads. Owned
and private storage may be dirty until its first charged CLEAR. Native/cover
semantics are the pinned full tensor semantics, not a finite sample of payloads.

Both complete words admit

```
q = h 2^(-9-3t),       W = P+28+6t signed component bits.
```

The component induction in [range-proof.md](range-proof.md) tracks magnitude,
lattice and both tensor-depth exponents. It includes scalar partials, the two
halvings implementing a quarter coefficient, all coordinate Gaussian interiors,
private state and the deferred tenth output definition. A coordinate Gaussian
has output component bound2L and cross-numerator bound4L, even though it is unitary
in a different norm. Repeated across lambda coordinate layers, these bounds
produce the grouped all-depth rules. This is a specified pair-first numerical
reference, not an unpriced replacement for a recursive child.

Both words yield M<=171043, g<=9 and depth exponents a,b<=3. Therefore every
observed component is on the q lattice and has magnitude

```
<171043 B 2^(3t) < 2^(P+18+3t) h = 2^(W-1) q.
```

All specified shifts are divisible on this lattice. Thus signed W bits suffice
without overflow or arithmetic rounding. The new D+=E temporary doubles a local
bound230 to460, but lies below the agreeing completed-query bound11864. Every
one of the224 endpoint envelopes agrees; the whole prefix and suffix were
included. An uninitialized deferred host is never treated as a bounded number.

A second certificate uses a different representation and dispatcher. Put u=2^t.
`independent.py` propagates exact positive polynomials and observes every logical
write and largest native cross numerator. For

```
F(u)=445+28230u+96u^2+142272u^3,
```

each difference F-observation has nonnegative coefficients after substituting
u=1+y. Hence it is nonnegative for all u>=1. There are3932 candidate and4032
baseline observations; the observation streams are hashed. Since F(1)=171043
and degreeF=3 with nonnegative coefficients, F(u)<=171043u^3. Decreasing its
cubic coefficient by1 makes both certificates reject. This is a certificate
control, not a lower bound on an optimal physical width. A separate explicit
coordinate recurrence at depths1,2,3,8 checks the grouped rule; these finite
checks do not supply the all-depth quantifier. Independent agent calculations
also checked depth17 during development.

The result concerns a **common sufficient uniform format**. It does not prove
minimum widths, equal attainable maxima, or domination over a baseline whose
operations use separately optimized widths.

## 2. Rounding: three distinct implications

First, the specified exact reference above has zero arithmetic residual. There
is no precision surcharge relative to PR4015 in this domain.

Second, approximate native callbacks can still give relative bit identity under
explicit fixed-grid premises. Both words must use common q and format; changed
unit additions must be exact and non-overflowing. Every normalizer/map callback
must be deterministic, bank-independent and isolated, with the same specified
scratch entry/return contract. `binding.py` verifies from the literal words:

- the prefix differs only by deferring the tenth host's original X-copy;
- each of104 captured sources has exactly the same port/map/inverse-line recipe;
- queries never alter their captured borrowed or corrected sources;
- response arithmetic is identical;
- nine versus ten output definitions are charged, and the subsequent suffix is
  identical; the old tenth host had no earlier consumer.

The actual query subsequences agree on all104 source coefficient vectors and two
mixed integer regressions. For arbitrary q-integers, distributivity and integer
associativity prove that equal-sign pair sharing and independent source
reordering preserve all eight completed queries. Identical deterministic response
and suffix callbacks then preserve final bits. This permits common approximate
normalizer outputs, but does not certify their absolute accuracy, native interior
range or exact private cleanup. The exact-reference range proof alone cannot be
used to assert nonoverflow of an approximate implementation.

Third, floating significand rounding is not associative. The exact rational
precision2, ties-to-even rounder in `rounding.py` executes the actual query scalar
subsequences with supplied normalized components v76=4,v87=v92=1, others0.
Baseline Q0=RN(RN(4+1)+1)=4; candidate Q0=RN(4+RN(1+1))=6. The other query
components agree. This is a query-cut countermodel to automatic rounded bit
transfer, not a reachability claim for a complete rounded caller.

For a conservative absolute error comparison, let epsilon bound entry component
errors, eta the residual of each complete scalar ADD against ideal dst+c*src,
and nu the output residual of each complete signed native call. Eta includes
scaling, addition and storage error; neither eta nor nu is assumed to equal one
unit roundoff. CLEAR, covers and monomial signed permutations are exact. With
x=2^lambda, the new interpreter propagates

```
ADD: E_dst <- E_dst+|c|E_src+eta;       native: E <- xE+nu.
```

Both words have identical224 endpoint polynomials, in six distinct classes. Both
also have the same coefficientwise whole-word logical-cut enclosure:

```
E_entry  =445+14115x+2964x^2+17784x^3,
E_scalar =16380+14451x+19104x^2+17784x^3,
E_native =14121+2964x+17784x^2.
```

Triangle inequalities prove this for arbitrarily correlated errors; shared sum
errors are counted in every affected channel. Coefficient maxima need not occur
at the same cut and do not enclose native interiors. See
[rounding-proof.md](rounding-proof.md) for the complete recurrence and witness.

The common signed format has logical-cut margin

```
(2^18-171043) B 2^(3t) = 91101 B 2^(3t).
```

Thus E_entry epsilon+E_scalar eta+E_native nu strictly below that margin is a
sufficient logical-cut nonoverflow condition. At lambda1 this reads
`182803epsilon+263970eta+91185nu < 91101B`. Native interiors, actual error-width
relations and private restoration remain separate premises; this inequality is
not an implementation admission.

## 3. Cost comparison with declared units

The frozen words contain1920 versus1820 unit ADDs. Both have896 quarter ADDs,
416 CLEARs,224 signed H1 calls,448 monomial wrappers and352 covers. Private peak16
and persistent banks are unchanged. Hence their inherited logical scalar
allowances26944 and26144 differ by800. A common positive tariff at the common
width preserves that logical saving.

For an explicit distinct numerical reference set N=2^(73lambda) complex coordinates
per owner. Count2N component adds for each unit ADD;2N shifts by two plus2N adds
for a quarter ADD;2N zero stores per CLEAR. Each coordinate Gaussian costs10N
numeric primitives:4N adds,2N halves,4N copies. A signed monomial costs6N
(2N signs plus out-and-back copies); a cover costs4N copies. Both permutations
use one reusable complex buffer and return to the original fixed bank, so no
free handle rebinding is assumed. The prescribed bills are

```
baseline: (12352+2240lambda)N,
candidate:(12152+2240lambda)N.
```

The difference is exactly200N real-component additions. Under a common uniform
positive primitive tariff tau(W), the reference bound falls by200N tau(W).
Under distinct primitive tariffs, unchanged counts cancel and the differing
real additions still cost200N times their common-width price. Storage is at most
(930N+12) W-bit component slots in this numerical model, including224 borrowed,
224 owned,16 private complex fields, one complex permutation buffer and12 scalar
temporaries. Physical addressing, placement and native recursive workspace are
outside this count. See [cost-proof.md](cost-proof.md).

If an actual implementation forces different widths, its uniform-tariff
break-even condition is

```
tau(W_c)/tau(W_b) < (12352+2240lambda)/(12152+2240lambda).
```

For tau(W)=W and extra candidate bits Delta, the condition is
`Delta < 200 W_b/(12152+2240lambda)`. Equal sufficient widths satisfy it. This
makes the precision boundary measurable without claiming minimality or assigning
a fictitious recursive tariff.

## 4. Producer connection and precise remaining obstruction

The canonical #3303 producer theorem is inherited, not rerun. It provides quantum
`q_prod=h2^(-71-19t)` and signed width `W_prod=P+215+38t` for its different producer
entry contract. Its outputs consequently have absolute value strictly below
`2^(P+214+38t)q_prod`. Substituting `h_D=q_prod` and `P_D=P+214+38t` into this audit
gives the conditional numerical composition

```
q_joint=h2^(-80-22t),       W_joint=P+242+44t.
```

This substitution does not establish that the selected F0 caller supplies that
producer, its decoder entry or native workspace. It does not pay conversion or
physical movement. Neither selected kappa nor any supplier record changes.

The next justified experiment is to pin **one actual recursive H1 implementation**
and its caller's entry grid and range. Obtain its component width, complete
output residual nu(W,lambda), interior range and scratch restoration contract,
plus tariff and layout costs. Use that one contract to test the logical margin,
private cleanup, full native interiors and the break-even inequality above. A
missing bound or forced width surcharge is a precise stopping obstruction. More
floating samples or another isolated decoder constant do not supply this missing
contract.

## Evidence and credit

RANGE.json, ROUNDING.json, COST.json, POLYNOMIAL.json and RESULT.json are entirely
recomputed and compared with type-sensitive equality. Gaussian elementary cases,
actual query regressions, dirty reads, altered captures, missing restoration,
changed coefficients and missing natives are exercised. Tests reject source,
manifest and retained-data corruption before analysis, duplicate keys, false
receipts and attempts to overwrite receipts. Registered normal/optimized and
Git-free read-only replay preserve every exported byte.

PR3985 owns the336-to224 native reduction; PR4015 owns streaming and output hosting;
PR4106 owns the scalar pair construction. PR4003 supplies the residual lineage.
Retain ywz65/#2707, Arham Tahir/#2681, Ali Romman and the native/decoder/compiler
lineage recorded in retained proofs. NickPetalas/#3303 owns the producer grid
and ToikY/#3652 its independent review; Tekalign/tekuuu/#4030 is a distinct shared
frame gate. This new audit is by Chris R / Clear1nsight with substantial OpenAI
Codex assistance, including independent range, rounding/cost and adversarial
agents. This is AI-assisted mathematical evidence, not human or formal approval.
