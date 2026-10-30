# A rank cut for stage reuse

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.

## 1. Result and exact model

This is a scoped obstruction for complete caller words. It does not keep
the inputs to earlier paid calls fixed. It allows arbitrary invertible
binary changes of basis between calls.

There are n independent main fields, a central involution Q, and independent
commuting involutions z_x, one for each transverse axis. Work in the group
algebra over F2. A full call has the form

```text
(I + (d_i + 1) P_i) (I + Q N_i),
d_i = product(z_x : x in S_i),   |S_i| = b.
```

Here P_i is an idempotent of rank two, N_i is a nilpotent of rank one,
and P_i N_i = N_i P_i = N_i. A thin call is I + Q N_i. The sets S_i can
overlap or repeat in any way. Ordinary scalar changes of basis are free
for this necessary test. Helpers stay separate independent jobs. The
main target, after constant invertible binary input and output bases, is

```text
diag(Q * product(z_x : x in T_j) : j = 1,...,n).
```

Its charged Fourier rank is 1 + |T_j|. Each full call uses a fresh complete
local helper inventory. A thin call costs one rank-one query per port.
Sections 1-8 describe the controller on each port. The complete price
applies these bounds across the v ports. Those sections keep ports
separate. Section 9 extends the shortest-query result to arbitrary
scalar mixing across all ports at the stated saturated main-field count.
The principal theorem permits no idle axis maps or other paid main maps.
Section 2 also gives a necessary cut when such idle maps are present.

Let L count all query-bearing calls and f count the full calls. The
shortest case is L = n + 1. For n >= 4, the following statements hold.

1. If axis x occurs in k_x full calls, it can occur in at most
   k_x + (k_x mod 2) independent main targets.
2. At most two full calls can have an axis that occurs in no other call.
3. With b = 8 and either pinned P104 local inventory, the complete
   target moment minus paid moment is at most -8 for every exponent
   0 < t <= 1. The bound is sharp at t = 1.

This includes all main-field counts, all full/thin placements, every
commuting coordinate overlap, and all scalar bases in the declared
binary model. A finite search is not the proof of these statements.

For n = 2, the three-full-call unit is the exception. Its optimistic
complete moment is already negative at kappa = 0.002 for both pinned
inventories, and remains negative for every larger kappa below one.
Thus no shortest caller in this model improves the selected bound.

The binary model does not cover arbitrary complex scalar codes with
even denominators, noncommuting stage operators, an advancing operator
with unbounded order, joint main/helper codes, or a changed target
contract. An integral symbolic caller that reduces to this model must
pass its test. No reduction of every physical Clifford program to this
model is asserted.

## 2. General query-frame cut

Set Q = 1 + e, with e squared equal to zero. Absorb the ordinary changes
of basis and each call's constant value at Q = 1 into adjacent bases.
Each query then has the form I + e R_i, where

```text
R_i = u_i v_i,   v_i u_i = 0,   sum_i R_i = I_n.
```

The corresponding full-call projector still has rank two and satisfies
P_i R_i = R_i P_i = R_i. This normalization is a conjugation. It does
not change ranks, independence, or the number of paid calls.

Put U_0 = [u_0 ... u_(L-1)] and let V_0 have rows v_i. Then U_0 V_0 = I.
The query Gram matrix K = V_0 U_0 is an idempotent of rank n. Its diagonal
is zero. If L <= n, rank forces L = n and V_0 U_0 = I, a contradiction.
Thus L >= n + 1. Write h = L - n. The complementary idempotent I - K
has rank h.

For any axis x, let S be the set of its full-call occurrences, with
|S| = k. Set that axis to 1 + d, where d squared is zero; set all other
axes and Q to one. The full-call derivative is P_i at an occurrence and
zero elsewhere. The monomial target gives an idempotent E_x whose rank
r_x is the number of target jobs that contain x. Hence

```text
E_x = sum_(i in S) P_i.
```

More generally, h_x separately charged one-field idle occurrences add
h_x matrices of rank at most one to this sum. The same argument below
allows those terms.

For each i, choose a_i in the image of P_i with v_i a_i = 1. Such a
choice exists because v_i P_i = v_i is nonzero. Choose b_i as the
coordinate of u_i in the basis (u_i, a_i) of that image, with b_i zero
on the kernel of P_i. Then

```text
P_i = u_i b_i + a_i v_i,
b_i u_i = v_i a_i = 1,   b_i a_i = v_i u_i = 0.
```

Factor the sum E_x = A B. Use the columns u_i, a_i of A and the rows
b_i, v_i of B, then append a rank-one factor for each idle term. Thus A
has 2k + h_x columns. Because E_x is an idempotent,

```text
rank(I_(2k+h_x) - B A) = 2k + h_x - r_x.                 (1)
```

To prove (1), U: w -> A w maps the kernel of I - B A bijectively onto
the image of E_x. Its inverse is y -> B y. This proves the dimension
identity even when A or B has a kernel.

Select the rows of B A that came from v_i and the columns that came
from u_j. The corresponding submatrix of the identity is zero. The
selected submatrix of I - B A is therefore -K[S,S]. A submatrix cannot
have larger rank than its parent. Equation (1) gives the necessary cut

```text
r_x <= 2k + h_x - rank K[S,S].                         (2)
```

This cut uses the actual query Gram matrix. It applies to longer words
as well as shortest words. Since K[S,S] = I_k - (I-K)[S,S],

```text
rank K[S,S] >= max(0, k-h),
r_x <= k + min(k,h) + h_x.                             (3)
```

The cut can reject a proposed target inventory before the full stage
polynomial is built. Passing it is not an operator identity or admission.

## 3. Sharp capacity at the shortest query count

Suppose L = n + 1. The rank-one complementary idempotent I - K has
diagonal one. Over F2 it is the all-one matrix. Thus

```text
v_i u_j = 1 for i != j, and 0 for i = j.
```

In particular, n is even. Every k by k principal submatrix is I_k + J_k,
where J_k is all one. It has rank k when k is even, and rank k-1 when
k is odd. Substitution in (2) gives

```text
r_x <= k + (k mod 2) + h_x.                            (4)
```

The algebraic bound is sharp. In a space with coordinates 0,1,...,k,
take, for i = 1,...,k,

```text
u_i = e_0 + e_i,   v_i = e_0^T + e_i^T,
P_i = e_0 e_0^T + e_i e_i^T.
```

These R_i have the required pairings. Each P_i is an idempotent of
rank two that contains its R_i. Their sum is diagonal: it is one on
each private coordinate and is k mod 2 on coordinate zero. Its rank
is exactly k + (k mod 2). This is a sharp local algebraic witness,
not a complete profitable caller.

The written results also extend to any field of characteristic two.
In that case the rank-one complement is a b^T, with a_i b_i=1, rather
than necessarily the all-one matrix. Replace u_i by a_i u_i and v_i
by v_i/a_i. This preserves each R_i and makes every off-diagonal
pairing equal to one. The proofs below then use the same simplex.
The general cuts and the rank-two complement argument use only field
linear algebra and integer target counts. The executable filters and
finite controls in this package use F2; they do not enumerate extension
fields. This extension still gives no characteristic-zero reduction.

## 4. At most two calls can have private axes

This step uses Cinna Davis's minimum-query projector lemma from
`productive-controller-basis-search/GLOBAL-PROOF.md`. Its hypotheses
hold for every call with a private axis, even when other calls share
arbitrary axes. The other stages need not have independent multipliers.

For a private axis at call s, its target derivative is P_s. Independence
of that target projector from Q gives

```text
[P_s, sum_(j>s) R_j] = 0.
```

All private-axis target projectors commute with one another because
they are diagonal in the same output basis. They also satisfy
P_s R_s = R_s P_s = R_s.

Here is the retained argument. Normalize the simplex to
u_i = e_i and v_i = 1 + e_i for i < n, with u_n = v_n = 1. For an
interior position s, set U_s = sum_(j>s) u_j and V_s = sum_(j>s) v_j.
Commutation forces the image of P_s to contain u_s,U_s and its row
space to contain v_s,V_s. These two pairs are independent. Their
pairing matrix is

```text
[0  n-s; n-s  0] over F2.
```

There is no rank-two projector if n-s is even. If n-s is odd, the only
choice is P_s = u_s V_s + U_s v_s. Two different interior choices do
not commute: for s < t, P_s u_t = U_s, P_t u_t = u_t, and P_t U_s = 0.

An initial private-axis call can coexist with an interior one only at
s = 1. Otherwise its forced two-dimensional image and row space have
zero pairing. A terminal private-axis call can coexist with an interior
one only at s = n-1, for the same reason. For n >= 4 one interior call
cannot be both positions. There are at most two private-axis calls.

With b axes per full call, at most 2b axes can have multiplicity one.
Let s count those axes. The total axis occurrence count is b f. For
k >= 2, k + (k mod 2) <= 4k/3. With no idles, (4) therefore gives

```text
R := sum_x r_x
   <= 2s + (4/3)(bf-s)
   <= (4bf+4b)/3.                                     (5)
```

Also R <= 2bf. These are bounds on all main outputs together. They do
not count a stage map as a new independent field.

For future callers with idles, let H = sum_x h_x. At most H private
axes can have h_x > 0. The same argument gives the weaker useful tradeoff

```text
R - H <= (4bf + 4b + 2H)/3.                           (6)
```

Equation (6) is a linear rank budget. It is not an all-concave rejection
when idle calls can combine several axes at a concave price.

## 5. Complete P104 price, for every concave tariff

Both pinned source inventories have v = 104 ports, b = 8, and

```text
sum_r r (paid[r] - helpers[r]) = Lambda = 1720
                                   = 2*b*v + 56.
```

The 56 includes the local owned-copy debt. The helper targets are
independent source inputs. Their complete bill is retained at every
full call. The inputs are the main P104 package and PR5599 at
09dd0965711ca7eeb169057a420abab1c9052137. The latter source changes
helper inputs and includes PR5565's paid profile. Its native result
is inherited here; this package does not rerun its native construction.

For c_r = paid[r] - helpers[r], both exact profiles satisfy

```text
sum_r c_r max(r-j,0) <= 0  for every integer j >= 1.     (7)
```

The verifier checks the complete finite list. Beyond the largest
source rank, the sums are zero. Let g be any nondecreasing concave
tariff on the nonnegative integers, with g(0)=0 and g(1)=1. Its
successive slope drops a_j are nonnegative, and

```text
g(r) = r - sum_(j>=1) a_j max(r-j,0).
```

Only finitely many terms matter at each source rank. Equation (7) gives

```text
sum_r c_r g(r) >= Lambda.                              (8)
```

Also g(1+r) <= 1+r. There are n main targets per port and L-f thin
queries. The complete target-minus-paid moment is therefore at most

```text
v (n+R) - v(L-f) - Lambda*f
  = 104(f-1+R) - 1720f.                               (9)
```

For f = 0,1,2, the bound R <= 16f gives, respectively, -104, -56, -8.
For f >= 3, (5) gives

```text
moment <= (3016 - 1520f)/3 < -8.                       (10)
```

Thus the complete moment is at most -8 for every such tariff. In
particular, this holds for g(r)=r^(1-kappa), 0 <= kappa < 1. Adding
nonnegative compiler or ordinary-work costs cannot change this failure
of the necessary recursive moment inequality.

The same calculation gives an inventory design condition. Let a local
family have v ports, b>=1 transverse axes and net rank mass
Lambda=2bv+d. Suppose its paid-minus-helper hinge sums are nonpositive,
as in (7). If d>=v/2, no shortest caller with n>=4 can have a positive
complete concave moment. At f=0,1,2 the bounds are -v,-d,v-2d. For f>=3,
the bound is

```text
v*(4b/3-1) + f*(v*(1-2b/3)-d).
```

It decreases in f. At f=3 and d=v/2 it is v*(1/2-2b/3)<0.
Thus d<v/2 is necessary to reopen this shortest-query route while
keeping the hinge condition. P104 has d=56 and v/2=52. Changes to the
local paid distribution or helper endpoints that retain these two
conditions do not escape the obstruction. This is a necessary design
condition, not a construction when the inequality is reversed.

The n=4, f=2, L=5 factored word already recorded by Cinna Davis attains
-8 at the linear tariff. Its main jobs have ranks 1,1,17,17, and its
three thin queries remain charged. The verifier checks the whole
binary polynomial matrix, the four independent coefficient images,
and a separate interpreter. This shows that the numerical upper bound
is sharp in the declared model, rather than only a loose negative bound.

## 6. The two-field exception

For n = 2, every full projector is I_2. There are three queries. With
f <= 2, (9) and R <= 16f still reject the complete bill. With f = 3,
each main target has rank at most 25. Its best possible complete moment is

```text
208 * 25^t - 3 * sum_r c_r r^t.
```

Exact integer-root intervals make this quantity negative at t=499/500
for both sources. Its negative coefficients have lower rank than all
its positive coefficients. After division by the first positive rank
to the power t, it is increasing in t. It therefore stays negative for
every 0 < t <= 499/500. The two-field exception cannot improve kappa
past 0.002. This is separate from the sharper no-saving result for n>=4.

## 7. Joint axis cuts

There is also a necessary intersection cut. It can reject profiles that
pass every separate capacity test. Let S and T be the occurrence sets
of two axes x and y. Define

```text
delta_x = 2|S| + h_x - r_x,
delta_y = 2|T| + h_y - r_y.
```

These numbers are nonnegative. In the factorizations E_x=A_x B_x and
E_y=A_y B_y from Section 2, the rows V_S occur in B_x and the columns
U_T occur in A_y. Since E_x is an idempotent and its row space is
contained in the row space of B_x,

```text
rank(V_S (I-E_x)) <= rank(B_x)-r_x <= delta_x.
rank((I-E_y) U_T) <= rank(A_y)-r_y <= delta_y.
```

Decompose V_S U_T as

```text
V_S E_x E_y U_T + V_S(I-E_x)U_T + V_S E_x(I-E_y)U_T.
```

The target projectors commute and select their target axis sets. Hence
the number r_xy of independent main jobs that contain both axes obeys

```text
r_xy = rank(E_x E_y)
     >= rank K[S,T] - delta_x - delta_y.                (11)
```

This is a necessary cut for arbitrary query counts and includes the
stated idle terms. A negative right side gives no constraint. At full
capacity, both deltas vanish. The cut then forces target intersections
directly from the off-diagonal query Gram blocks.

## 8. A longer paired-stage obstruction

Consider a second, narrower family. Every call is full. There are
L=n+2=2m calls. Each of m independent stage blocks occurs exactly twice;
each block has eight axes and different blocks have disjoint axes. The
two calls in a pair need not be adjacent. All binary scalar bases and
all call orders remain allowed. There are no idles.

Let r_c be the number of main targets that contain stage block c.
Every word coefficient is a product of whole blocks. Constant boundary
bases cannot add new monomials, so each target contains a whole block
or none of that block. The count r_c is at most four.
Suppose first that every r_c=4. Write I-K=XY,
where X has two columns, Y has two rows and YX=I_2. For each two-call
index set S_c, (2) forces K[S_c,S_c]=0. Thus

```text
X[S_c,:] Y[:,S_c] = I_2.
```

Both two-by-two factors are invertible. Their product in the reverse
order is also I_2. Summing in c gives YX=m I_2, so m must be odd.
For any two distinct classes, K[S_c,S_d] has rank two. Equation (11)
therefore requires at least two common target coordinates for every
pair of stage blocks.

At full capacity, E_c=A_c B_c has rank four with four inner columns.
It follows that B_c A_c=I_4. In particular, E_c U_c=U_c and V_c E_c=V_c.
Use the common basis in which all E_c are diagonal. Every row of U_0
is nonzero, since U_0 V_0=I. No row can be supported in just one class:
U_0 X=0 and X[S_c,:] is invertible. Thus every main coordinate belongs
to at least two stage sets.

Let d_j count the stage sets that contain coordinate j. We now have

```text
n=2m-2,   2 <= d_j <= m,   sum_j d_j=4m,
sum_j binomial(d_j,2) >= 2*binomial(m,2)=m(m-1).        (12)
```

Only four units remain after assigning degree two to all coordinates.
Convexity makes the largest intersection sum by putting those units
on as few coordinates as possible. At m=5 this maximum is 19, below
20. For m>=6 it is

```text
binomial(6,2)+(2m-3)*binomial(2,2) = 2m+12 < m(m-1).
```

Even m already fails the parity condition. Thus full capacity is
impossible for every m>=4, or n>=6. For m=3, two disjoint three-query
units on four fields attain full capacity. Their three corresponding
stage pairs each reach all four outputs. This positive exact word
passes (2) and (11), and prevents an invalid extension of the shortest
query bound to all longer words.

At least one stage occurrence must therefore be lost for n>=6:

```text
sum_c r_c <= 4m-1.
```

The complete linear-tariff bound for either pinned P104 inventory is

```text
104*(n+8*(4m-1)) - 2m*1720 = 96m-1040.                (13)
```

It is negative for m<=10. The same bound holds for every normalized
nondecreasing concave tariff by (8). This rejects, in particular, the
fourteen-call/twelve-field candidate and the eighteen-call/sixteen-field
candidate for every such tariff. The former had a floating optimistic
crossing near .003393385 before the intersection cut. That crossing is
not a caller or a kappa claim.

For larger m, discrete concavity gives the sharper power-tariff bound

```text
M_m(t) <= 104*((2m-5)*17^t + 3*25^t) - 2m*sum_r c_r r^t. (14)
```

The verifier proves that this bound is negative at t=997/1000 for
m=4 and m=26. It is affine in m, so it is negative for all 4<=m<=26.
All negative coefficients have lower rank than all positive ones.
The sign-separation argument from Section 6 extends this rejection to
every 0<t<=997/1000. Therefore no paired-stage caller with 6<=n<=50
in this family can improve kappa beyond .003. At n=4, full capacity
forces all four jobs to contain all three stages. Its bill is twice
the two-field bill from Section 6. Any loss of capacity instead gives
the negative bound (13). At n=2, every full projector is I_2, and each
paired stage cancels. These smaller cases also fail beyond .003.

More queries, partially overlapping axis sets, mixed full/thin words,
paid idles or a nonbinary construction require a new complete test.
A common advancing operator remains a different route: it has
unbounded-order powers, so the involutive-axis proof does not exclude it.

## 9. The shortest obstruction also permits coupled ports

The shortest theorem is not limited to a tensor copy of one scalar
controller. Let each query have rank q, each full projector have rank
2q, and let the total main dimension be N=nq. Use L=n+1 calls. Allow
arbitrary binary scalar bases on all N fields, including across ports.
Write R_i=U_i V_i, where U_i has q independent columns, V_i has q
independent rows and V_i U_i=0. Then U V=I_N. The query Gram matrix
K=VU has zero q-by-q diagonal blocks. Its complement C=I-K has rank q.

Factor C=A B with A of size qL by q and B of size q by qL, and BA=I_q.
For each call block i, A_i B_i=I_q. Thus A_i is invertible and B_i=A_i^-1.
Rescale the query factors to U_i A_i and A_i^-1 V_i. This preserves R_i.
The rescaled Gram matrix has zero diagonal blocks and I_q in every
off-diagonal block. Also BA=L I_q=I_q, so n is even. This proves the
block simplex, rather than assuming it from separate ports.

A compatible rank-2q full projector factors as

```text
P_i = U_i B'_i + A'_i V_i,
B'_i U_i = V_i A'_i = I_q,   B'_i A'_i = V_i U_i = 0.
```

Choose A'_i as a right inverse of V_i inside the image of P_i, and use
B'_i as the coordinate map for U_i along that complement. The argument
of Section 2 now selects a qk-by-qk Gram block. For an axis used by k
calls, its rank is q*(k-(k mod 2)). Consequently

```text
r_x <= q*(k+(k mod 2)).                               (15)
```

The private-axis argument also extends. Replace each u_i,v_i by the
q-column/row blocks U_i,V_i. An interior private projector must contain
the two independent q-dimensional spaces U_s and sum_(j>s) U_j, and
the corresponding row spaces. Their pairing matrix is

```text
[0  (n-s)I_q; (n-s)I_q  0].
```

Even n-s is impossible; odd n-s gives the unique projector
`U_s V_tail + U_tail V_s`. The noncommuting interior pair and both
zero-pairing endpoint arguments in Section 4 apply to these blocks.
Thus at most two call positions have private axes.

The total main transverse rank therefore satisfies

```text
R <= 2qbf,   R <= q*(4bf+4b)/3.
```

There are nq target jobs and q(L-f) thin paid queries. With q=v=104,
b=8 and the same autonomous helper inventory per full call, the
complete price calculation in Section 5 is unchanged. Its sharp -8
bound covers arbitrary cross-port scalar codes at N=104n, L=n+1.
The proof also holds over characteristic-two extension fields.

This extension does not extend Section 8's complete paired-stage price
bound to arbitrary coupled ports. At L=n+2 the complement has rank 2q;
one lost target occurrence need not mean one loss on every port.
Different main counts with N not equal to q(L-1), mixed query ranks,
and main/helper mixing also need separate arguments. The general
rank and intersection cuts still apply after each rank-q query and
rank-2q projector are factored into compatible rank-one/rank-two terms.

## Credit and verification boundary

Cinna Davis supplies the simplex, private-projector obstruction, the
sharp five-query word, and the controller lineage. The new result is
the Gram-submatrix rank and intersection cuts, their sharp repeat
capacity, their use for arbitrary coordinate overlap, the paired-stage
obstruction, and the complete all-concave P104 bound.
The equality cuts in PR5588 motivated the search; passing those cuts
alone did not supply an endpoint. The scalar, native, helper, compiler,
precision and analytic sources retain their attribution in SOURCES.json
and the package README.

The written arguments prove the unbounded statements under their stated
algebraic hypotheses. The exact verifier checks finite instances and
discriminating controls. It is not a proof-assistant kernel or an
independent human review. No selected frontier is changed.
