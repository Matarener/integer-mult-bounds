# Independent B4 session-4 Boolean encoding argument

Original mathematical argument: **Brian Ross**. This independent construction
and verification package is by **Toik Y, with substantial OpenAI Codex assistance**.
It was constructed without reading predecessor/source code, proofs, existing
session packages, source-adapter files, or source-generated queries or receipts.
This document proves the stated schema. A separate adapter must still establish
that a particular source program constructs that schema; agreement of examples
alone would not establish that fact.

## 1. Precise object and domain

Let G = GL_3(F_2), with its complete 168-element address basis. A matrix is
represented by its three row masks; multiplication means ordinary matrix
multiplication over F_2. Let e=(1,2,4). For each ordered pair i != j there is one
label g_ij obtained from e by XORing row j into row i. There are exactly six
labels, and each label is an involution.

Let R=F_2[G], with [g][h]=[gh]. Register states are 3 by 3 matrices over R.
There is no natural-address projection: each of the nine entries has all 168
independent address coefficients. Scalar vectors u,v belong to F_2^3. A legal
normalized factor is

    F(u,v,g) = I_3 + ([e]+[g]) u v^T,
    v^T u = 1, and g is exactly one of the six labels.

There are 28 legal pairs (u,v), hence 168 parameter triples per call. With
chronological calls numbered 1,...,n, S_0=I_3 and S_t=F_t S_(t-1); thus
S_n=F_n ... F_1. The target is the **full** matrix

    D = diag([A],[B],[e]), A=(1,4,3), B=(2,4,3).

The quantified schema below is for every integer n>=1. The published CLI domain
is exactly n in {1,...,9}; saved focus cases are n=7 and n=8. A zero-call case is
explicitly outside that domain. This oracle guards zero at its published support
mask interface. A separate program's internal zero-call behavior is not, by
itself, a defect in its published n=1,...,9 interface. No SAT solving, RUP replay,
or minimum-nine assertion occurs in this package.

## 2. Exact coefficient recurrence

Fix a column c and output address h. Write s_(k,c,h) for its full ring coefficient.
Let lambda_l denote the six label bits, constrained to have exactly one true bit.
Define

    q_h = XOR_(k=0)^2 (v_k AND s_(k,c,h)),
    shifted_h = XOR_(l=0)^5 (lambda_l AND q_(g_l^(-1) h)),
    delta_h = q_h XOR shifted_h,
    s'_(r,c,h) = s_(r,c,h) XOR (u_r AND delta_h).

An OR may replace the XOR in shifted_h: exactly one label is true, so at most
one of the six gated summands is true. This replacement does not permit dropping
the exactly-one constraint. Since the coefficient of [h] in [g]q is precisely
q_(g^(-1)h), expansion of F S gives these equations for every r,c,h. In particular,
left multiplication of addresses requires the stated left pullback; substituting
h g^(-1) is generally wrong. The formulas cover all 1512 output bits.

The independent oracle uses two implementations of this step. `transition_dense`
uses the displayed pullback formula. `transition_ring` explicitly constructs the
nine sparse factor entries and performs group-ring convolution using matrix
multiplication. They agree on a dirty full-ring state for all 168 legal factors.
These finite checks supplement, rather than replace, the expansion argument.

## 3. Support specialization, including forbidden outputs

Let B_t contain all group elements expressible as a product of at most t labels.
Let T_c be A, B, or e for column c. At cut t use

    M_(t,c) = B_t intersect (B_(n-t) T_c),
    B_(n-t) T_c = {b T_c : b in B_(n-t)}.

The translation of T_c is on the **right**. This is the necessary support mask
supplied by the separately audited support theorem. Its short algebraic basis is
also consistent with the present schema: each factor has coefficient support in
{e,g}; moreover g^2=e and char(R)=2 imply ([e]+[g])^2=0, so F^2=I_3. Forward
expansion therefore gives support within B_t. Reversing the remaining factors
from D gives support within B_(n-t) T_c. Row mixing does not change this address
support bound.

Allocate s_(t,r,c,h) only when h belongs to M_(t,c), and interpret every other
state literal as the constant false. Impose the initial and final conditions on
**all nine entries and all 168 coefficients**, using those constants where needed.
Most importantly, impose every displayed transition equality even when its
left-hand output is a forbidden, constant-false state bit. Such an equation
constrains its right-hand recurrence to be false. Necessity of a support mask
alone does not justify simply discarding equations whose outputs are outside it.

For an attaining word, the support theorem guarantees that its actual states fit
these masks. Conversely, because all equations are present, extending allocated
states with the specified zeros gives the full unmasked recurrence. This is the
only direction in which the necessity theorem is used. No sufficiency of a mask,
or reachability conclusion from mask membership, is assumed.

## 4. Boolean gates, literals, and exact choice constraints

Literal 1 is true, literal -1 is false, and CNF contains the unit clause (1).
Every newly allocated variable is at least 2. Literal -a denotes logical NOT of
literal a. For a fresh positive output z, the full definitions are

    z <-> (a AND b): (-a,-b,z), (a,-z), (b,-z)
    z <-> (a XOR b): (-a,-b,-z), (a,b,-z), (-a,b,z), (a,-b,z).

These clauses are valid for signed operands. Equality a<->b uses (-a,b),(a,-b).
OR may be represented by -AND(-a,-b). The complete definitions are essential:
each gate direction has a concrete wrong-output assignment if its relevant
clause is omitted. The executable table records those witnesses.

For operands a,b, the constant, repeated, and opposite-literal simplifications
are Boolean identities: false AND b=false, true AND b=b, a AND a=a,
a AND -a=false; false XOR b=b, true XOR b=-b, a XOR a=false,
a XOR -a=true. Swapping operands preserves both gates. Complementing exactly
one XOR operand complements its output, and complementing both preserves it.
Consequently the encoder can cache canonical pairs, return a signed cached
output, or avoid allocation after these simplifications. These operations retain
the same total Boolean function. Tautological clauses may be removed; false
literals and duplicate literals may be removed from a clause; an empty clause
must remain an explicit contradiction.

The exactly-one-six-label constraint consists of the one six-literal positive
clause and all 15 negative pair clauses. It accepts exactly the six singletons.
The v^T u constraint consists of three ANDs, their XOR parity, and a unit forcing
that parity true. It accepts exactly 28 of the 64 u,v assignments. In particular,
an OR of those three products would not be a valid substitute for parity.

The frozen finite tables exhaust all 36 ordered pairs from {x,-x,y,-y,1,-1}
under all four x,y assignments for AND, XOR, and OR: 432 rows, with explicit
brute-force uniqueness of the auxiliary extension for each row. They also exhaust
all 576 signed AND/XOR raw-clause relation rows (including a free output bit),
and all 256 clause-normalization rows over the six signed/constant literals.
Normalization preserves multiplicities of non-tautological clauses, so an
adapter can compare complete clause multisets rather than silently lose duplicates.
The tables further exhaust
all 64 label assignments, all 64 u,v assignments, and all 4096 label/q-value
assignments for a six-way selector. Illegal labels are retained in that latter
table to show where OR and XOR differ without exactly-one.

## 5. Unique extension lemma

Consider any finite DAG built from these full gate definitions, in allocation
order, where each allocated auxiliary is the output of exactly one gate and
each operand is a primary, a constant, or an earlier gate's signed output. Fix
all primary values and force variable 1 true. At the first gate its operands
are determined, and its complete equivalence permits exactly the correct output.
Inductively this holds at every later gate. Thus the gate-definition CNF has
exactly one auxiliary extension. Simplified gates introduce no new variable;
cached gates introduce no new choice, so the conclusion still holds. Additional
equality or choice clauses can reject that extension but cannot create another.
This proves totality and uniqueness from the DAG, with no SAT-solver assumption.
It also explains reverse decoding: any satisfying assignment gives every gate
its intended Boolean value by induction in the same topological order.

## 6. Quantified SAT equivalence

For every integer n>=1, construct C_n with:

1. Exactly six label bits and six u,v bits at each call; the constraints in
   section 4 impose a legal normalized factor.
2. The masked primary state bits, false outside the mask, and full initial state
   I_3 and target D, as in section 3.
3. A finite acyclic gate expansion of every coefficient equation from section 2,
   equality at every output coefficient, and the complete gate definitions.

Then the precise statement is

    (there exist primary and auxiliary Boolean values satisfying C_n)
      iff
    (there exist legal normalized factors F_1,...,F_n with F_n ... F_1 = D
     as full 3 by 3 matrices over F_2[G]).

Forward direction: a satisfying assignment selects exactly one label and legal
u,v per call. Reverse decoding from section 5 makes every recurrence gate its
intended value. The initial state is the full identity. Induction over t, using
all output equalities including the constant-false ones, proves the reconstructed
full state is exactly F_t ... F_1. The full endpoint constraints therefore imply
F_n ... F_1=D in all nine entries and all 168 coefficients.

Reverse direction: take any such attaining word. Its actual full states obey
the recurrence by section 2 and obey the necessary masks by section 3. Assign
the allocated state bits and all choice bits their actual values. Section 5
gives the unique auxiliary extension. Every gate, output equality, initial
condition, endpoint condition, exactly-one constraint, and parity constraint
then holds. Thus C_n is satisfiable.

For each fixed legal attaining choice sequence the state and auxiliary extension
is unique. Neither this statement nor the equivalence proves existence of any
attaining word, unsatisfiability for any particular n, or a minimum word length.
The claim applies to an actual implementation only after the separate source
adapter verifies its complete wiring and clause construction against this schema.

## 7. Independent canonical expression API

An ANF polynomial is a `frozenset` of monomials; a monomial is a `frozenset` of
hashable primitive keys. The empty polynomial is zero and the polynomial whose
only monomial is empty is one. XOR is symmetric difference, AND distributes
and unions variable sets (x^2=x), NOT is 1 XOR p, and OR is p XOR q XOR pq.
With an explicit exclusive label group, a monomial containing distinct label
keys from that group is discarded. This is valid on all onehot assignments.
It does not assume a state-support theorem or silently identify different group
coefficients. Equality of these reduced polynomials is sufficient to certify
equal functions under those orthogonality conditions. Inequality alone does not
prove inequivalence under the additional sum-of-labels-equals-one condition.

`expected_column(state_rows,u,v,labels,pullbacks,exclusive_groups)` returns all
3 by 168 coefficient polynomials for one column. Inputs are polynomial arrays;
substitute zero for any excluded state bit. `pullbacks[l][h]` must be the index
of g_l^(-1)h in the **same enumerated full group basis** used for state rows.
`expected_transition` wraps all three columns in [r][c][h] order. Primitive keys
can be actual positive source variable IDs. `literal_anf` gives the polynomial
of a signed source primary literal with the 1/-1 constant convention. An adapter
can expand an actual ordered gate DAG using these operations and compare every
actual RHS polynomial to the independent expected result. It must separately
verify exactly-one groups, vTu, endpoint constants, every equality, and all CNF
clauses. The API itself does not infer that a trace contains all needed gates or
that trace metadata comes from the actual source.

## 8. Executable evidence and limits

The CLI writes nothing by default. `--fulltable` prints the complete deterministic
table to stdout; explicit shell redirection is what creates the frozen receipt.
Normal and Python 3.12 `-I -O -W error -B` runs are required to agree. Science
checks use explicit exceptions, never Python `assert`, so optimization cannot
disable them. The full table contains generic polynomials for every one of the
1512 output coefficients, all 168 independently checked one-call factors,
arbitrary dirty full-ring positive one-, two-, and four-call vectors, and the
n=7,8 right-translated support masks. A support-zero specialization at n=7,
cut 3 checks all 1512 expressions against direct zero substitution in the
unrestricted generic expression family.

Negative controls include removal of every AND/XOR direction, each equality
direction, the true unit, each of the 16 onehot clauses, and the vTu true unit.
For every one of the 1512 coefficient-output equations and every endpoint unit,
the test actually flips that one output while fixing the others: the complete
CNF rejects it and the corresponding single-omission CNF accepts it. Further
controls exhibit an actual wrong coefficient from right/left translation
confusion, an actual chronological product-order error, and distinct right/left
support translates. These detect relevant finite errors; the universal statement
rests on the proof above plus a complete source-conformance audit.

An additional local transition control starts from a coefficient allowed at
n=7, cut 3 and sends it to a forbidden coefficient at cut 4. All other output
coefficients are zero. Setting the forbidden output to false satisfies every
output equation except the one for that coefficient. The complete relation
rejects it; omission accepts it. This is a precise local omission witness and
does not claim that this partial transition extends to an attaining word.
