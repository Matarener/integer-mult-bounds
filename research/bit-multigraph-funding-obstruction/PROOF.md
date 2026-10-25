# Parallel supports cannot fund the two-early-helper BIT controller

## 1. Model, theorem and source boundary

We use the explicit relaxed model of PR5456, now allowing arbitrary parallel
edges and arbitrary diagonal Q/D flags. Work over F2 with q²=0 and independent
commuting involutions D_i, i=0,...,c-1. Call i has a coordinate support C_i of
size four; every field belongs to exactly one or two supports. Let T_i apply
D_i on C_i and identity elsewhere. The chronological word is

    F_(c-1)...F_0,       F_i=T_i(I+qR_i).

Columns of R_i outside C_i vanish; rows outside C_i are allowed. There are
u_i,w_i supported on C_i with u_i!=0, R_i u_i=0 and R_i w_i=u_i. Completing
this chain to a four-role basis leaves two arbitrary helper columns. These
are the same favorable native-main/early-helper hypotheses as PR5456, not a
new physical assertion about every permitted matrix.

The required endpoint is diagonal, with entry

    (product_(i:a in C_i) D_i)(1+t_a q),        t_a in {0,1}.

Let Qcount=sum_a t_a. **Theorem: Qcount<=2c.** This covers every order, any
finite number of calls, private fields, arbitrary parallel intersections,
D-only targets and arbitrary helper writes outside the support. It needs
independent D symbols, coordinate four-supports, at most two owners and the
native length-two zero Jordan chain. It does not cover extra thin calls,
non-coordinate projectors, three owners or dependent D symbols.

For the retained actual FULL invoice, the theorem implies target rank minus
paid rank <=-63c, and strictly negative target-minus-paid moment for every
r^s tariff with 0<s<=1. Thus parallel edges cannot fund this entire class.
No selected frontier, native implementation, supplier or kappa is changed.

## 2. Exact labels and a triangular restriction for every call

Write h_i(a) for the incidence bit vector of calls j<i containing a. Factoring
all commuting T_i to the left shows that coefficient R_i(a,b) has group label
h_i(a)+h_i(b). Because q²=0 there are no higher R products. At each off-diagonal
matrix entry, coefficients with each independent group label cancel.

Fix i and restrict R_i to its four support rows/columns; call this A_i.
Partition C_i into private singleton fields and common-support classes
E_ij=C_i intersect C_j. Every E_ij has one partner j, since ownership<=2.
For distinct a,b in C_i:

- If b is private, its sole contributing call is i, so R_i(a,b)=0.
- If b in E_ij with j<i and a not in E_ij, the label at call i has bit j=1
  (b in C_j, a not); the label at call j has bit j=0. Thus R_i(a,b)=0.
- If b in E_ij with j>i and a in E_ik with i<k<j, the label at call j has
  bit k=1 and the label at call i has bit k=0. Thus R_i(a,b)=0.

Only calls i,j can contribute column b, so these unequal-label arguments
remain valid with completely arbitrary rows outside either support.
Order the blocks of C_i as future partners j>i in increasing j, then all past
partners, then private singletons. A column in a future block may write only
to its own or later blocks; a past block column writes only within that block;
private columns are diagonal. Therefore A_i is block lower triangular.
No claim is made that the full R_i is block triangular.

For each shared class E_ij, the two endpoint diagonal blocks satisfy

    A_ij+A_ji = diag(t_a : a in E_ij).                              (1)

Indeed, fields within this class have identical membership histories, hence
both group labels are zero, and only i,j contribute their columns. A private
diagonal block is the scalar t_a. These facts are valid in every chronology.

Let z(B) denote the algebraic multiplicity of eigenvalue zero in B; equivalently
z(B)=dim ker B^r for an r-by-r matrix. Block triangularity makes z(A_i) the sum
of the block z values. Restricting the actual native chain equations gives
A_i u_i=0, A_i w_i=u_i!=0, so z(A_i)>=2. This uses a genuine length-two chain,
not just singularity or a trace condition.

## 3. Local spectral lemma, including the exceptional triple

Let A,B be r-by-r binary matrices, A+B=diag(t), and let k=sum t be the integer
number of ones. For r<=3,

    z(A)+z(B) <= 2r-k,                                             (2)

except possibly r=3,k=2. In that case either the same bound4 holds, or
z(A)=z(B)=3 and the sum is6. The latter is the only exceptional case.

Proof: for k=0 the dimension bound suffices. For k=r, B=I+A, so z(B) is the
multiplicity of eigenvalue one in A. Distinct factors x and x+1 in its degree-r
characteristic polynomial give z(A)+z(B)<=r. The remaining cases for r<=3
have k=1 or r=3,k=2. When k=1, trace(A)+trace(B)=1, so A,B cannot both be
nilpotent; at least one has z<=r-1, proving the bound2r-1. For r=3,k=2,
trace(A)=trace(B). A sum greater than4 is5 or6. Sum5 would require multiplicities
3 and2: the former matrix is nilpotent with trace0, while the latter has
characteristic polynomial x²(x+1) over F2, hence trace1. This is impossible.
Sum6 means both multiplicities are3, as claimed.

The exception is real. In column-bit notation,
A=(2,7,5), B=(3,5,5) are nilpotent3 and A+B=diag(1,1,0).
The verifier checks their characteristic polynomials, powers and exact diagonal
sum using independent representations. Ignoring this exception would give a
false proof for mixed Q/D targets.

## 4. The exceptional cost cancels globally

First remove any class E_ij of size four. It exhausts both C_i,C_j, so those
two calls share no field with any other call. Their component has at most four
Q targets, exactly the required upper bound2×2, regardless of helper writes
outside its support. We may account for these vertices separately. The
remaining calls and field incidences have all shared classes of size<=3;
Section2 still applies to their restrictions and unchanged exact coefficient
conditions. No new subword endpoint is assumed by this bookkeeping removal.

Write c for the remaining number of calls, E for the number of shared fields
(counting multiplicity), P for the number of private fields, and Z for the
number of D-only fields (t_a=0). Then

    4c=2E+P,       Qcount=E+P-Z=4c-E-Z.                             (3)

Let b be the number of exceptional triple classes from Section3 for the
actual matrices. Their endpoint call pairs are disjoint: a four-support call
cannot contain two distinct size-three classes. Each exceptional endpoint has
z(A_i)>=3, since one of its diagonal blocks already has z=3. Every other call
has z(A_i)>=2. Therefore

    sum_i z(A_i) >= 2c+2b.                                        (4)

On the other hand, sum (2) over shared classes, allowing +2 at exactly the b
exceptions. A private field contributes1 precisely when it is D-only. Writing
Z_E,Z_P for the two kinds of D-only field, we obtain

    sum_i z(A_i) <= sum_shared(2|E_ij|-#Qflags)+Z_P+2b
                 = E+Z_E+Z_P+2b = E+Z+2b.                         (5)

The exceptional +2 terms cancel between (4) and (5). Hence E+Z>=2c, and (3)
gives Qcount<=2c. Adding back the four-edge components proves the theorem.
The proof is a global multiplicity/ownership argument, not repeated last-call
elimination and not a finite UNSAT claim.

In the all-Q subcase Z=0, equality in 2c<=E<=2c forces P=0 and E=2c. Thus a
completed all-Q word has no private fields. For example, the three-call doubled
path with supports {0,1,4,5},{0,1,2,3},{2,3,6,7} cannot close all eight Q flags.
Those eight flags would give a positive rank surplus33, but the theorem limits
it to six. The mixed triple counterexample does not repair that funding gap.

## 5. Complete actual signed invoice

The live source WORD has111 ports and439 original helpers. Giving each port two
early helper roles uses222 **distinct original helper owners** and leaves217
untouched H8 jobs per FULL. A helper is selected only at its unique first
departure from frame zero, which belongs to one port. The verifier scans the
actual D/A/B/C source sections:439 helper first departures,286 rank-one first
departures distributed over111 ports with at least two each, no helper write
before departure, and222 distinct owners when choosing two per port. Repeated
observations of one helper are not credited as new jobs. Reusing one owner at
multiple ports is outside this invoice premise. The retained complete paid profile per FULL is

    1323H1+1342H2+79H3+44H4+102H5+11H6+19H7,

of total rank5129. It includes the retained source's owned center-query charges;
none are removed. The independently authenticated source receipt and WORD
supply these quantities; the verifier checks them directly.

At a port, each call contributes four rank-seven D incidences. Independent
fresh D axes give rank7 for a private D factor and rank14 for a shared pair;
a Q flag adds one. Across c FULLs and111 ports, even permitting different
support multigraphs at different ports, target rank is at most

    217*8*c + 111*(28c+2c) = 5066c.

Thus the complete target-minus-paid rank is <=-63c. Before applying the
structural theorem its exact expression is111Qcount-285c for a uniform port
pattern, with the obvious sum over port-specific Q counts otherwise.
Selected helpers are included in these active target fields, not credited
again among the217 untouched helpers. Dirty input independence and all
retained helper targets remain charged. Adding physical prologue, chart,
movement, cleanup and storage costs cannot improve this already-negative
favorable native-only bill; those costs are not claimed implemented here.

All paid ranks are<=7, and every credited target rank is>=7. For 0<s<=1 the
function r^(s-1) is nonincreasing. Thus

    sum_targets r^s - sum_paid r^s
      <= 7^(s-1) (sum_targets r - sum_paid r)
      <= -63c * 7^(s-1) < 0       (c>0).

This proves the signed concave-moment gate, not merely the t=1 test. It uses
independent D axes and the specific actual helper debit. Dependent D symbols,
changed axis overlaps, a different retained source, three owners, extra thin
calls or non-coordinate supports require a new proof and full invoice.

## Evidence and attribution

The written argument is the quantified result. Exact finite tests corroborate
local spectral cases, chronology/label block ordering, native chains, complete
positive endpoints and signed counts. They are not a controller search or a
proof certificate for PR5456's saved solver outcomes. No solver is invoked.

PR5456 at0d64d4d5d73f370182ada9825a611c86cfbf0049 supplies the model, simple-graph
last-call argument and complementary-word control. This proof restates all
needed hypotheses and proves its new global lemma without importing that
pending package. Its immutable proof SHA256 is
8f8f3ef5682adb154ccacd8b533b6733ff08a00dd47a38363587ef816fe59e62.
PR5452/5388 motivate early helper observations; the actual retained PR589/555
source and its eumemic/Anthropic-assisted lineage are pinned locally.
Prepared by JoyboyBrian with substantial OpenAI Codex assistance; Apache-2.0.
No independent human or proof-kernel acceptance is claimed.
