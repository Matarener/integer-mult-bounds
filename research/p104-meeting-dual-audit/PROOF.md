# Scalar cut and restoration audit

This audit concerns PR #5751 at `8483f9a679d06c1e270141dbc686a7e76e7a7522`.
The source construction, cut vectors and basis formulas are credited inputs.
The contribution is a separate vector checker, explicit restoration obligations,
negative controls and an authenticated complete bill. No new general theorem
or construction is claimed.

## A sufficient cut certificate

Fix one scalar word. Let A be its prefix at the cut, B its suffix, and T = BA.
The matrices include public and dirty owned coordinates. INIT, CLEAR and COPY
can make them singular. This proof does not invert A, B or T.

Let a be the retirement row, b the injection column, c = aA and d = Bb. Let e
be the unit column at the chosen helper pivot h. The checker requires

```text
ab = 1,   cd = 1,   Ad = b,
cT = c,   Td = d,   e^T T = e^T,   Te = e.
```

The last four equations state the exact identity modes needed for restoration.
The checker obtains c by propagating a backward through the prefix and obtains
d by propagating b forward through the suffix. It checks all these equations
on the current intermediate word, after every earlier split.

The input basis Q first subtracts c_i times each other field from h, scales h
by d_h, then adds (d_i/d_h) times h to each other field. The cut basis S scales
h by a_h, adds the other a_i fields to h, then subtracts b_i times h from the
other fields. The two pivots must be nonzero dyadic units. Thus both bases and
their reverse programs are legal rational invertible maps. Direct propagation
checks `Qe=d`, `cQ=e^T`, `Sb=e` and `e^T S=a`.

Put c_rest = c - c_h e^T. The input basis has the explicit form

```text
Q = I + (d-e)e^T - d c_rest.
```

Every left vector in its nonidentity terms is fixed by T; every right row is
fixed by right multiplication by T. Hence TQ = QT. The cut equations give

```text
SAQ e = e,     e^T SAQ = e^T.
```

The old helper is therefore isolated at the cut in both directions. Its value
is the old independent input, and no other cut coordinate depends on that input.
Retain it as an output and put a new independent input z in its continuing role.
After S inverse, the change is b times (z - x_h). After the suffix it is d times
that difference. Q inverse sends d to e, and Q commutes with T. All continuing
outputs therefore have their old T values, except the continuing pivot, which
has z. The retired output retains x_h. This argument holds for every rational
input, including every initially dirty owned coordinate under the stated INIT
and CLEAR semantics.

## Physical scalar interfaces

A scalar basis may act only on fields in the same current frame. The audit
tracks each public field and each owned lifetime, checks every operand frame,
and requires strict binary-subspace inclusion for each paid MOVE. It checks
that a partial query advances only across events that do not access that field.
The intermediate frame must be strictly between the two old query frames.
Every added query remains in the word and in the paid count.

The supports of c and d must be independent full helpers: input frame 3, output
frame 127, and no main coordinate. The supports of a and b must actually be at
the cut frame. Owned labels shift with each fresh public input. Rebuilding all
21 meetings gives all 23 cuts and the exact published WORD and WITNESS.

Frame 105 is sequential. Its pivots 557, 455 and 115 create inputs 762, 763 and
764. Their cut indices are 14105, 14107 and 14112; the final cut is 14174. The
third retirement row uses the new field 763. Reusing the first cut's matrices
for all three steps would not check this dependence. The three split bases
use 2, 6 and 118 scalar operations. Five paid subdivisions support the meeting.

The whole-word check propagates each of the 776 input basis columns separately.
It checks all 602,176 coefficients, including nine dirty owned columns. All main
shears, independent helpers and zero owned exits match. Before every COPY, its
owned destination is zero for each input column. This establishes the zero
condition for arbitrary input, not just for a zero-initialized sample.

## Why the extra restoration predicates matter

Take A = I on two scalar fields, a = (1,0), b = (1,1)^T and

```text
B = [[1, 0], [2, -1]].
```

B is the invertible program `field1 *= -1; field1 += 2*field0`. Then c = a,
d = b, ab = cd = 1 and Ad = b. Even cT = c and Td = d hold. But Te differs from e
for pivot 0. With input (1,0) and new input z = 0, the proposed replacement gives
continuing output 0 where the old word gives 2. The short cut identities alone
are insufficient. The actual PR #5751 cuts pass all the restoration predicates.

A separate actual-word control inserts a nonzero ADD immediately before COPY.
COPY erases that added value, so the tested endpoint stays unchanged. The COPY
zero precondition still fails. This protects a legality condition that endpoint
equality alone cannot establish.

## Complete invoice and limits

All native ranks are recounted from the independent frame bases and the literal
MOVE sequence. Relative to PR #5718, the local deltas are

```text
Delta paid    = 35 H1 - 5 H2 - 3 H3 + 16 H5 - 16 H6
Delta targets = 23 H1 + 23 H8 - 23 H9.
```

Each sum has zero rank-mass change. There are 27 additional paid queries and
23 additional productive helpers per local call. The exact retained controller
has 18 forward local calls, 15 query shears and 15 whole idles. Its actual main
diagonals supply the other targets. Both old and new complete histograms match
their published receipts. The old counts are 66,348 paid calls and 12,976 targets;
the new counts are 66,834 and 13,390. The rank surplus remains 760.

The scalar allowance is 224,138. The source's stated route allowance gives
5,239,000, with eleven owned lifetimes and peak two. Their sum is below the
retained local allowance of ten million. This checks the inventory and the
stated allowance arithmetic; it does not prove the implementation cost of a
native map or route.

INVOICE.json and SOURCE-INVOICE.json use the repository's common signed-invoice
format. Their contract is the same p16/a7 unnormalized moment gate. Completion
parameters are excluded. PR #5751 changes those parameters, so a comparison of
these bills alone cannot establish the published exponent.

The audit does not import the source constructor, scalar checker, native engine
or pricing code. Six nested export manifests and all their payload hashes are
checked as data. The scalar engine is also compared with explicit dense matrix
products for all 4,369 words of length at most three over its 16-operation
finite control alphabet. That finite check supports the implementation; the
linear induction above supplies the general scalar argument.

Native Gaussian phases, physical caller operator equality, the compiler,
interval moments, outer predicates and the five inherited framework assumptions
remain separate obligations. This audit does not select a frontier or establish
independent human acceptance. Its conclusion applies only to the pinned source.
