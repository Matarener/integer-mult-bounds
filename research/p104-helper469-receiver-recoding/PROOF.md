# Helper469: receiver recoding still cannot remove the frame593 rung

This is a one-interval exact rational exclusion, not a new multiplication
construction, native implementation, cost improvement, or universal barrier.
All indices below are zero-based and a slot is the state before an event.

## Source and changed hypothesis

The sole computational input is the selected PR6030 word at main
`721c03822c421b7f7fcbb2598993b947c4d88419`, SHA256
`7834725d9e34ee846a9ccc615221ea81e0201613938afa185d2eda0c9a6c232f`.
Its inherited helper468 and helper470 removals are retained.
Jonathan Capalbo's [PR6069](https://github.com/CrocSwap/integer-mult-bounds/pull/6069),
head `b3f5aabddbae2d65f80bb8356e6993e0a65cd245`, excludes donor-only
endpoint resynthesis but explicitly excludes receiver scaling/recoding from
its claim. Its `ENDPOINT-PROOF.md` SHA256 is
`2e7a08c289cfd7761a02d4fcdf0be804a8882a66c532e84058c91ed41134148c`.
That pending proof is contextual attribution, not an imported code dependency
or an assumption of this certificate; the elementary argument is given below.
No foreign source-history ancestry is fabricated or required.

We allow any finite rational receiver-only ADD/SCALE program in the two
maximal contact-free endpoint windows, with every SCALE nonzero. Other roles'
programs, public inputs, owned lifetimes and charts are fixed. Replace only
469's MOVE 3->593 at14357, its ADD469+=2*703 at14380, and its
MOVE593->713 at14417 by a direct MOVE3->713 and the endpoint programs.
The receiver must regain its entire original scalar row at chart713 before
its next contact at14850. No new MOVE, owned storage or altered donor is allowed.

## Exact rows and legal windows

The previous receiver contact is a read at7895. Its next contact after the
second MOVE is the incoming ADD at14850. Thus endpoint slots are
[7896,14357] at chart3 and [14418,14850] at chart713, inclusively.
No original operation reads or changes469 within either window.

Start all770 public roles as independent coordinate rows e_0,...,e_769;
owned roles enter with zero rows on INIT. ADD/SCALE/COPY have literal rational
semantics; MOVE changes the chart and leaves the decoded scalar row unchanged.
This is the selected word's scalar contract, not a new native-map assertion.

Exact prefix replay gives receiver entry

    f = e_469 + (1/2)e_537.

Write Delta = 2 row_703(14380), the one removed interior contribution.
The verifier records every coefficient of Delta in RESULT.json and checks
that the full original receiver row at14418 and14850 equals f+Delta.
In particular Delta has coefficient1/2 at public-input coordinate1.

Collect every other live row at the beginning of each window, then every
other role's row immediately after a MOVE arrival at its endpoint chart
through the last slot. These569 timestamped generators comprise568 at the
first endpoint and1 at the second. Every collected value is available at its
recorded slot: the receiver can read it then, without retaining a donor after
its departure. Exact replay proves every generator has coordinate1 zero.
The receiver f also has coordinate1 zero.

Every other donor version available later in a window lies in the span of
these generators: same-chart ADD, SCALE and COPY preserve the accumulated
span; INIT contributes zero; CLEAR and departure cannot enlarge it; each MOVE
arrival is included. No original read of469 occurs within either window,
so modifications to469 do not affect donor rows. This is PR6069's credited
accumulated-span argument, specialized here and independently checked.

## Normal form and complete decision

Any finite receiver-only endpoint program has scalar form

    r_out = lambda f + sum_j c_j g_j,  lambda != 0,

because every ADD adds a fixed donor row and every SCALE multiplies all
existing coefficients. A direct MOVE preserves this row; combining both
endpoint programs multiplies their nonzero receiver coefficients. The desired
restoration is r_out=f+Delta, equivalently

    (lambda-1) f + sum_j c_j g_j = Delta.                 (1)

This is an exact rational affine system with the invertibility side condition.
For completeness, any formal coefficients of timestamped generators can be
realized in chronological order with arbitrary rational ADDs: scale at the
first slot by lambda, then add each generator at its recorded slot, taking the
direct MOVE after the first window. Donors are unchanged and never read469;
no new storage or free retention is needed. This scalar realization does not
establish the physical scalar alphabet or its cost. Those gates would follow
only if a solution existed.

Apply the linear functional L(v)=v[1] to(1). The left side is0 for every
rational lambda and c_j, while the right side is1/2. Contradiction.
The feasible lambda set is therefore empty, even if zero multipliers were
granted. This separates the entire affine span, not a finite coefficient
search or a first-order screen. It decides the prescribed invertible model.

The obstruction explicitly concerns an arbitrary input column; replacing703
by a label or checking only an ideal fixture would not establish it. The
original receiver row must be restored before14850; postponing repair or
changing another role is outside the model. The precise scientific review
obligations are the scalar interpretation, the complete window boundary,
the accumulated-span induction and its normal-form applicability.

No candidate survives to be priced. No favorable direct-transition native
rank, paid profile, productive-target histogram, ordinary cost or kappa is
claimed. This exclusion does not decide changed donor routes, new storage,
new receiver contacts, a different word or coupled receiver/donor recoding.
