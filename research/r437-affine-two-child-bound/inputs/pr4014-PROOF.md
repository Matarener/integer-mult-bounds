# One-child dirty echo boundary and the fixed two-child budget

Chris R / Clear1nsight, with substantial OpenAI Codex assistance. Apache-2.0.
This is a scoped obstruction and cost decision, not a new multiplication bound.

## 1. Changed proposal and optimistic gate

PR3982 supplies an all-class rank-seven COPY conjugator with 8036 ordered ADD
slots per column, 196 ordinary interchanges and one reversed 7f child. Its
ordinary tariff remains a positive exponent-gap term under the available B1/B2
upper bounds. The new proposal tested here removes ordinary interchanges by
using coupled dirty payload roles, coordinatewise reversible/Boolean echo,
and the existing reversed child as the only backward address primitive.
This is a changed consumer/operation contract, not a smaller permutation route.

The completed old bill is

 T_R(v,7f,w) + 196 b(v,f) + C_q v(8036f+196+3) + Gamma

plus 63 actual dirty XOR readers and outer owner/producer/return costs when
not already included. All of these are charges; none is a negative credit.
For a candidate with child widths k_1 f,...,k_t f and no ordinary calls, use

 sum_i T_R(v,k_i f,w) + C_scan(v; clone, coordinatewise gates, ordered ADDs,
 readers, transfers, releases, disposal, head return) + Gamma_echo.       (1)

Its reserve must sum the whole-run visited maxima on fixed reusable source,
owned-output, helper, child, coefficient and parking inventories. Erasure does
not refund previously visited cells, and disjoint occurrence inventories cannot
be replaced by a maximum. These implementation-dependent scan and reserve terms
are unknown here. Setting all of them to zero is the optimistic gate below,
not a physical upper bound.

The source profile has m=64, W=28416, paid rank mass1808352, hence deficit
64W-1808352=10272. It has2592 COPY executions (nine captures in each of nine
stages and32 replicas), already using one private transformed stream through
63 readers. A fixed schedule replacing every one with two rank-seven children
adds2592*7=18144 mass, giving1826496 and excess7872. Its optimistic moment is

 M_two(c)= (1/W) sum_r n_r(r/64)^(1-c)
                  + (2592/W)(7/64)^(1-c).

For every c>=0, each term (r/64)^(1-c)>=r/64, so

 M_two(c) >= M_two(0)=1826496/1818624=1+41/9472>1.       (2)

Thus this particular fixed two-rank-seven replacement fails even before the
remaining positive costs in(1). This does NOT follow for an adaptive schedule
or for two children of different widths. If only a fraction theta pays one
extra rank-seven child, the zero-exponent necessary condition is
 theta<10272/(2592*7)=107/189. At positive c the necessary bound is
 theta < (1-M_old(c))/((2592/W)(7/64)^(1-c)), when the numerator is positive.
The obstruction below supplies a worst-case class, not its density. It does
not license inserting theta=1 into an adaptive original good/fallback scheme.

## 2. Actual address convention and the relaxed operation class

Fix an odd prime q, w>=1, R=Z/q^w and A=q^w. Take the allowed subsequence
n=64f with any f>=1 (delta=0); a uniform all-size claim must cover it. In one
fixed physical prefix/fresh-row/spectator fiber, order the two banks as

 head atoms 0,...,n-1; reflected tail atoms n,...,2n-1.

Atom a=if+j in the head is paired with physical tail atom 2n-1-a. The standard
reversed child W_l swaps a with2n-1-a for0<=a<l and fixes every other address
coordinate. Its complete source-preserving payload operation is the pullback
 F'(x)=F(W_l x), exposing one transformed output and no additional payload
channels; borrowed sources and helpers are restored. A rank-k child in the incumbent notation has l=kf.

An ordered ADD has its source physically before its target. Its address matrix
is lower unitriangular: x_i <- x_i+a x_j for j<i, with a determined by fixed
metadata. Products and inverses remain in the group U of lower unitriangular
matrices over R. We generously allow ALL such matrices on the two banks,
including cross-bank ordered additions, not just PR3982's same-bank alphabet.
Optional invertible diagonal factors would not change the argument.

The macro circuit is finite and its event schedule and address permutations
are independent of payload values. It may have arbitrarily many payload roles,
clones, dirty helpers and fresh constants. At any full physical address it may
apply arbitrary Boolean functions of roles at that SAME address, including
address-dependent masks, not merely XOR or linear mixing. It may apply any
number of U pullbacks on a role, and at most one completed W_l pullback event,
where l<n. Owned release/reset and required restoration are allowed. Every
primitive preserves the prefix/fresh-row/spectator fiber.

This is an address-dependency class, not a claim every Boolean gate has an
admitted physical tariff. Allowing them for free only strengthens a negative
result. A global payload-dependent branch that reads one address to control
another is excluded: it adds cross-address dependency edges. A differently
routed physical scan, table lookup, gather/scatter or arbitrary-address copy
is also not silently counted as a coordinatewise operation. Such primitives
change the hypothesis and must appear in(1). Fixed metadata may depend on q,w,
header and column; it must not convey source payload information.

Linearity of the body-address alphabet is essential. An affine translation
z -> z+(y-x) reaches the separating y from x, so admitting arbitrary address
translations destroys this particular orbit obstruction even with no child.
An addition from a fixed nonzero header/address digit into a body digit may
also act affinely on the fiber and is outside U here. No claim excludes every
legal physical scan or proves that such an enlarged alphabet is expensive;
a complete translated/affine mechanism would need its own full cost gate.

## 3. The dependency-orbit theorem

Define lead(z) as the first nonzero coordinate of z. If L is lower
unitriangular, lead(Lz)=lead(z), with the leading value unchanged. This holds
over R including nonunits and high carries: before the leading coordinate all
summands are zero, and at it the diagonal entry is1.

Let x=e_n, the first physical tail coordinate. For every V in U, Vx has zeros
before n and value1 at n. If l<n, W_l fixes coordinate n. It moves any nonzero
among the last l coordinates to the first l positions. Therefore

 lead(W_l Vx) is either <l or n.

Applying another U preserves that lead. Consequently the set

 O_1(x) = Ux union {L W_l Vx : L,V in U}                  (3)

contains no vector with lead n-1, because l<=n-1. This is an exact all-ring,
all-f statement; it does not enumerate the huge address cube.

Now unroll the macro circuit in time. A dependency path from a final output
bit backwards to an initial payload bit stays at its address through a
coordinatewise gate and changes address through the pullback's matrix at an
address operation. A path can cross the ONE chronological child execution at
most once, even if the role graph reuses roles or has apparent cycles. Collapse
all its ordered-ADD matrices on either side to U. Every input address that can
influence output at x is in(3). Fanout and Boolean cancellations cannot create
an input dependency absent from this union. This proof covers arbitrary dirty
helper contents: compare two runs with identical initial helpers and metadata,
changing only one source bit outside(3). Their final output at x is identical.
No restoration assumption is needed for the lower bound, so requiring all
helpers and the borrowed source to be restored cannot invalidate it.

## 4. A legal all-class rank-seven COPY outside the orbit

Let Q=diag(0,...,0,1,...,1) on64 coordinates, with ones precisely at57,...,63.
Let H=diag(h_i) be arbitrary ancestor units (possibly depending on column and
fixed header). The required two-bank map in paired head/tail coordinates is

 D_H(Q)=diag(H,I) [[I-Q,Q],[Q,I-Q]] diag(H^-1,I).

Apply the same Q on each of f columns, and reflect the physical tail as above.
At x=e_n only the tail atom paired to head n-1 is nonzero. Thus

 D_H(Q)x = h_(63,f-1) e_(n-1) = y.

The unit h makes lead(y)=n-1, so y is absent from(3). The two arbitrary Boolean
sources zero and delta_y require different COPY-output bits at x. The circuit
class in§2 produces the same bit, a contradiction. Thus at least two proper-
width reversed-child events, or another address-mixing operation, are needed
for a uniform all-class COPY in this class. A single wider child of width42f
still fails; width n leaves this obstruction but is not a smaller recursive
child at delta=0. No sufficiency claim is made for two events or for width n.

This Q is NOT asserted to be one of the nine literal capture matrices P.
Every literal rank-seven capture is a split projector over the admitted ring;
a basis of im(P) followed by a basis of ker(P) gives P=T E T^-1. A permutation
S sends the first seven basis axes to57,...,63. Then g=S T^-1 is invertible
and g P g^-1=Q. The all-class contract ranges over precisely such GL64 low
classes and lifts. The verifier reconstructs the actual capture frames from
the pinned R437 word and builds these conjugacies in finite local-ring cases.
The proof uses the quantified split-projector premise, not small-q admission.

Choose any physical prefix, unused fresh rows and spectator address, hold it
fixed, and put delta_y only there. The contradiction is a full-volume source
counterexample with every other bit zero. Unequal physical prefixes are not
merged. Adding untouched spectators, or the63 downstream dirty readers, does
not create the missing source-to-private-output dependency.

## 5. Why fanout and pooling alone do not pay the old term

The inherited private result is already computed once and retained through all
63 readers. Dividing its invoice by63 would only amortize a constant. If a
new contract really supplies K identical requests from one unchanged source,
source sharing can replace K evaluations by one, but it still costs
 T_R+196 b+K X+Gamma+cleanup, with the shared result preserved until last use.
For the available bound b(v,f)<=C v(fw)^p+E, write n~e^alpha,w~e^beta
with f proportional to n. The ratio of its leading term to K v n scales as
e^delta/K, delta=(alpha+beta)p-alpha. At a proposed R437 target selector
alpha=1-c_R,beta=c_R and p=1-a_B, this is delta=c_R-a_B>0 for both
pinned B1/B2 rates. This is a conditional target-scaling calculation; it does
not establish a retuned R437 selector or its admission. The retained ordinary
selector pattern is n=floor((e-k)/w), with k=o(e), as in PR3562 head
abb93be8b9ceca07a2b17f3a97db7bb6b074271d, PROOF lines110–165 (there c=1/577). This explicitly distinguishes original ordinary width e
from reduced width n. A fixed K
(including63) cannot remove this upper-tariff gap. To infer absorption from
that tariff would require growing K at least on the e^delta scale, while
also paying readers, storage, source compatibility and preparation. This is
not a lower bound on actual adapter runtime.

For different independent source payloads, packing K fibers enlarges volume
from v to Kv; the same volume-linear tariff gives196 C Kv(fw)^p, so dividing
by K gives no reduction at all. Identical field labels are not identical
physical sources. Different Q maps likewise need not yield the same private
stream: delta sources separate distinct address permutations. No new equality
of the actual R437 captures is asserted. PR3995's pooled owner IR still needs
its replica-indexed physical contract; its finite profile does not establish
source equality or free transport. PR3989 similarly demonstrates why a finite
coupled identity's lifted transfer cannot be priced without its full consumer.

## 6. Decision, evidence, and limits

Stop this fixed one-child dirty-echo route: it fails the full-cube dependency
contract even after relaxing pointwise operations. Stop the fixed two-rank-
seven-per-COPY repair: its optimistic moment already exceeds1. These are two
separate conclusions, not a universal lower bound of fourteen recursive ranks.
A 7f+1f or other mixed-width construction, an adaptive schedule with an actual
class-frequency proof, a legal backward address operation with a cheaper full
tariff, or a changed producer/consumer can reopen the question. Each needs an
exact complete bill and the appropriate whole-profile moment before expansion.

Finite checks authenticate source bytes, all nine capture classes and high-lift
conjugacies, reachable address orbits in small cubes, a separating arbitrary
payload bit and arbitrary fixed dirty helpers, and exact profile/tariff
arithmetic. Controls break the premise deliberately (a full-width child or
an extra child permits the formerly absent dependency), detect wrong target
orientation/weight, and reject invalid source/invoice inputs. The mathematical
proof, finite checks and same-session AI cross-review are distinct evidence.
No encoded supplier, formal-kernel proof, full native execution, selected cold
replay, improved kappa or frontier change is claimed.
