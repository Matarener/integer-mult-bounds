# A last-call obstruction for a simple support graph

This is a scoped negative result over F2. It does not give a kappa value or an
obstruction to every BIT controller.

## Model

There are finitely many field coordinates and f>0 calls, in order 0 through
f-1. Call i has a coordinate support C_i of size four. Every coordinate lies
in one or two supports. Two distinct supports intersect in at most one
coordinate. Thus shared coordinates form a simple graph; private coordinates
fill the supports to size four.

Let q squared be zero. For every call i, let D_i be a separate commuting
involution. Its formal group symbol is independent of the other symbols.
Write T_i for the diagonal matrix which applies D_i on C_i and the identity
outside C_i. The call is

    F_i = T_i (I + q R_i).

Every column of R_i outside C_i is zero. Rows outside C_i are permitted.
There must be u_i,w_i in the span of C_i with

    u_i != 0,    R_i u_i = 0,    R_i w_i = u_i.

This is the native main Jordan chain. Complete (u_i,w_i) to a basis of C_i
with two helper directions. Their R_i columns are arbitrary, including
writes outside C_i. This is a relaxation of the two-early-helper caller
interface; the theorem does not require a physical implementation for every
matrix it permits.

The desired endpoint is diagonal. On coordinate a it is

    (product of D_i for which a is in C_i) (I + t_a q),

where each t_a is zero or one. Thus D-only targets are permitted. The word
has no additional thin call. A scalar basis change is permitted only when
it can be absorbed into this stated form and the supports remain coordinate
supports. Non-coordinate D projectors are outside this model.

## Coefficient equation

Let s_i(a) be the bit vector of earlier calls k<i whose supports contain a.
Factoring all diagonal T_i to the left in

    F_(f-1) ... F_1 F_0

shows that the q coefficient from R_i(a,b) has group label

    s_i(a) XOR s_i(b).

There are no products of two R terms because q squared is zero. Independent
D symbols give an exact equation for every group label at every matrix entry.
At an off-diagonal entry, every such coefficient must cancel.

## The last call

Let l=f-1. Take distinct a,b in C_l. If b is private, only R_l can have a
nonzero column b. Its off-diagonal coefficient therefore has no term with
which to cancel, and R_l(a,b)=0.

If b also belongs to an earlier support C_i, only calls i and l can supply
this column. A nonzero R_l(a,b) requires their group labels to agree. The bit
i is absent from s_i(a) XOR s_i(b). In s_l(a) XOR s_l(b), that bit is zero
only if a also belongs to C_i, since b belongs to C_i. But a is already in
C_l, and the simple-graph hypothesis gives C_i intersect C_l={b}. This would
force a=b, a contradiction. Hence R_l(a,b)=0 in this case as well.

The restriction A of R_l to the four rows and columns C_l is diagonal over
F2, so A squared is A. Restrict the native chain equations to these rows:

    A u_l = 0,    A w_l = u_l.

They imply

    0 = A u_l = A squared w_l = A w_l = u_l,

contrary to u_l!=0. No word in the stated model has the required endpoint.
The proof does not use the diagonal target flags t_a, so it also covers the
D-only choices.

## Boundary and positive control

The theorem needs the simple-graph and at-most-two-owner hypotheses. Two
calls with four shared fields are outside the simple-graph class. The saved
matrices in CONTROL.json obey the native main chains and satisfy R_0+R_1=I.
On these four fields both T_i are scalar diagonal blocks, so

    T_1 (I+qR_1) T_0 (I+qR_0) = T_1 T_0 (I+qI).

The verifier multiplies these stage matrices in the exact group ring and
checks the complete endpoint. It also checks the independent four-role basis
and both early-helper column updates for each call.

For the arithmetic control, use two retained PR589 FULL invoices. Each has
paid profile {1:1323,2:1342,3:79,4:44,5:102,6:11,7:19}. Using two helper roles
per port leaves 217 original H8 targets per FULL. The active four fields,
at each of 111 ports, each receive two seven-axis D factors and one Q factor.
The complete declared target profile is therefore {8:434,15:444}. Its target
rank minus paid rank is -126. All paid ranks are below all target ranks, so
this negative rank surplus also rules out a gain for every tariff r^t with
0<t<=1. This is a check of the declared invoice, not a new physical supplier.

## Evidence scope

The general argument above proves the simple-graph result. The standard-
library verifier checks 48 K4/K4-minus-edge order fixtures and all 3,840
four-dimensional diagonal-matrix/nonzero-u/w cases. These fixtures exercise
the proof implications; they do not replace the general argument.

The 80 saved UNSAT outcomes in solver-evidence/ are separate finite solver
evidence. They include 48 simple-graph cases and 32 explicit parallel-edge
cases. No proof certificate accompanies them. The standard-library verifier
checks their hashes, counts and support descriptions. It does not prove those
UNSAT statuses. Optional replay uses the pinned Z3 version and is not part of
the registered verification.

This result does not cover fields in three or more calls, non-coordinate D
supports, dependent D symbols, paid thin calls, or a different native main
block. It does not prove a complete multiplication theorem or a new kappa.
