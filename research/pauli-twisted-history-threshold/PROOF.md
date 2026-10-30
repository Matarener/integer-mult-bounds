# Sharp paid-history threshold for the phase-complete Pauli alphabet

Let K=Q(i), X=[[0,1],[1,0]], Z=diag(1,-1), and
G=<iI,X,Z>. This is the 16-element group of actual matrices
{i^c X^u Z^v: 0<=c<4, u,v in {0,1}}. Its projective quotient has
four classes. At each positive width f define P=X^tensor f,
C=Z^tensor f and R=span_K{I,P,C,PC}. Ordinary operations are left
actions from R, arbitrary K-linear row combinations, COPY and CLEAR.
Scalar coefficients, word lengths and choices may vary with f.

Begin with ordinary combinations of N independent whole-field inputs,
including every independent dirty input, and zero scratch. A paid call
acts on one actual current field and returns one additional K-linear row
(not assumed linearly independent of earlier rows) at
the same capacity. It may depend on earlier paid outputs and need not
commute with R. Conceptually retain all actual paid rows after overwrites
or clears. No freely supplied nonordinary initial observation is allowed.

For q distinct input owners v_j, request H_j w_vj up to ordinary initial
backgrounds, where H_j=(a_j I+b_j X)^tensor f and
a_j b_j (a_j^2-b_j^2) != 0. Correctness is on the entire independent
input space. Then every such program has at least q paid returns for
every f>=2. At f=1 all targets are ordinary and zero returns suffice.
If each H_j is an available paid primitive, q direct calls attain the
bound for f>=2. Without this last hypothesis this is a lower bound,
not a supplier construction or an attainable native-call count.

## 1. Exact phases and actual algebra

The lift of i^c X^u Z^v is i^(cf) P^u C^v. In particular,
PC=(-1)^f CP, P^2=C^2=I. Phases merge into K scalars; the algebra is
the actual matrix image, not the untwisted group algebra of four labels.
For positive f the four matrices I,P,C,PC are independent. To see this,
use the X-eigenbasis of each tensor factor: P is diagonal with entry
(-1)^k on a binary string of weight k, and C maps each string to its
complement. The diagonal supports I,P are disjoint from the complement
supports C,PC; within each pair both parities occur. Thus dim R=4.
R is commutative at even f and noncommutative at odd f.

For one target write l+=a+b and l-=a-b. Both are nonzero. In this basis
H is diagonal with entry t_k=l+^(f-k) l-^k. For 0<=k<=f-2,

    t_k - t_(k+2) = 4ab l+^(f-k-2) l-^k != 0.             (1)

The basis change is an exact invertible common conjugation, used only
in the proof; it is not granted as a free physical instruction.

## 2. Odd widths at least three: full module separation

Suppose A H belongs to R, where A=alpha I+beta P+gamma C+delta PC.
The diagonal entries of AH on parity epsilon are
(alpha+beta epsilon)t_k. An ordinary matrix has a constant diagonal
coefficient on each parity. Compare k=0,2 in even parity and k=1,3 in
odd parity. By (1), alpha+beta=alpha-beta=0, hence alpha=beta=0.

At row complement(s), column s, the remaining entry is
(gamma+delta (-1)^(f-k))t_k. Ordinary complement entries are constant
within each input parity. The same two comparisons give
gamma-delta=gamma+delta=0 at odd f, hence gamma=delta=0. This uses
characteristic zero, invertibility of l+,l- and f>=3. Therefore

    R intersect R H = {0}.                               (2)

This proof allows coefficients in the full actual R. It does not
pretend its odd-width matrix blocks are one-dimensional characters.

Represent current fields as rows in End_K((K^2)^tensor f)^N. Let I0=R^N.
After m returns t_1,...,t_m, every available field belongs to
M=I0+sum_j R t_j: ordinary operations preserve it, and each paid
call adjoins its actual output row. Thus dim M <=4N+4m. Each target
generates R H_j e_vj, of dimension four because H_j is invertible.
Equation (2) separates it from the ordinary row at that owner, and
distinct owners separate the q modules from one another. Consequently
dim M >=4N+4q and m>=q. A growing finite N or finite word length
cancels at each width independently.

## 3. Even widths at least two: one actual character suffices

Now P,C commute. Set E=(I+P)(I+C)/4. It is a nonzero idempotent,
EP=EC=E, so ER=K E. This assertion would be false at odd widths.
In the same tensor eigenbasis, on every even-weight string s,
E has entry 1/2 at (s,s) and at (s,complement(s)); odd-weight rows
are zero. Complements are distinct at every positive width.

The diagonal entries of EH at weights zero and two are t_0/2 and
t_2/2. Both corresponding entries of E are 1/2. Their difference is
2ab l+^(f-2), nonzero by (1). Hence EH is not a scalar multiple of E,
including at f=2. This does not require R intersect RH to vanish.

Project all history rows on the left by E. Initial projected history
is the direct sum of K E at each independent owner. Since ER=K E,
each actual paid return can enlarge this projected span by at most
one dimension. Each requested EH_j e_vj adds one new dimension modulo
initial history; distinct owners make these q directions independent.
Therefore m>=q. This projection is an analysis of information already
available, not a free additional paid call or an assumed field split.

## 4. Sharp threshold, scope and predecessor distinction

At f=1, R=M_2(K) and h_j=a_j I+b_j X is ordinary. This proves the
width-one exception. With H_j available, one call on each original
owner gives the matching upper bound. Calls can preserve originals
by the allowed ordinary COPY; independent dirty inputs are not used
as zero scratch. No claim is made about a more restricted paid alphabet.

PR5446's general projective-coset theorem gives only f>=2p-1=7 here.
PR5450 proves threshold two for the smaller R=span{I,X^tensor f}.
Its projector (I+P)/2 does not have one-dimensional ER for the enlarged
group: the extra C direction survives. The even-width projector and
odd-width full module argument above discharge that missing implication.
The history-dimension method and classical Pauli/character algebra are
credited, not claimed as new general theorems.

Free initial paid history can invalidate the count. Repeated owners
cannot each be charged; projectively ordinary targets such as 2X cost
zero despite lying outside the finite G. If a=0 or b=0 the target is
ordinary; if a=+/-b the invertibility and comparisons used in the odd
case fail. Changing geometry, cross-column ordinary operations,
multiple independent outputs per call, nonlinear input-dependent
programs and approximation are excluded. This standalone theorem does
not establish a charge at a cached physical caller boundary, a new
recursive profile, precision/tape costs, or an integer-multiplication kappa.

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
Predecessor credit: Chris R / Clear1nsight and PR5425/5446's retained
history authors; Ali Romman's PR5450; classical tensor-power separation,
finite group representation theory and the retained native/compiler lineage.
