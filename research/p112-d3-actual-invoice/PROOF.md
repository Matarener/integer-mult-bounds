# All d=3 actual invoices

Prepared by conorholds with substantial OpenAI Codex assistance. Apache-2.0.

## 1. Exact theorem

Work over a characteristic-zero field K with the 112 live E8 root lines P
obtained by deleting an orthogonal eight-line frame. Choose rational root
representatives. Their binary labels are ell(s)=(1,s mod 2L), of rank nine;
the eight excluded frame labels are z_i. Put

    C_h(s)=<r_s,h>,  C={C_h:h in K^8},
    U(q)=span_F2{ell(s):q(s)!=0},  w(q)=dim_F2 U(q).

Let S contain C with dim S=8+t, t in {2,3}. Let F be an ACTUAL basis of S.
For each q_j in F its restricted dual x_j is defined by the unique identity

    C_h = sum_j <x_j,h> q_j   for every h in K^8.

Assume every x_j is nonzero. A basis member is corrected precisely when
x_j is a nonzero multiple of a frame root f_i AND z_i belongs to U(q_j).
Count actual corrected members, with multiplicity, as n_c. Define

    I=sum_F w(q_j)-n_c,
    T=span_K{q in S:w(q)<=7},
    d=dim(C intersect T),
    r=dim T-|F intersect T|.

Here T uses ALL low S-words; it is not an arbitrarily chosen low subspace.
Assume d=3; both adapted r=0 and nonadapted r>0 are allowed.

**Budgeted theorem.** If sum_F w<=72 at t=2, or <=73 at t=3, then I>=65.
This theorem requires no root mark, minimum actual basis, adaptation, N8,
distinct corrected inside indices, or historical survivor-list completeness.

The result uses the written geometric and raw-shape theorems of PR3689 at
head `3193d1ea9a4fc5d178570a61e6019454b53c1db9`, merged for archival
intake on 2026-10-20 and marked partially reviewed in the central ledger.
[DEPENDENCIES.md](DEPENDENCIES.md) pins and itemizes that dependence;
finite replay does not validate the full predecessor or its E8 assembly.

## 2. Ledger and inherited reduction

Suppose I<=64. Write a=dim T and let cost(T) be the minimum sum of w over
bases of T. Set

    Sigma=sum_(F intersect T) w,
    eta=Sigma+8r-cost(T),
    c9=number of actual outside members with w=9.

Every outside member has weight eight or nine: a low member would belong
to T, and the labels are nine-bit. Completing the actual inside independent
family to a basis of T by r low words proves eta>=r. In particular it does
not prove that this inside family minimizes its own span.

PR3689 RAW-SHAPE proves, under precisely these raw budgets and I<=64:

* a=d+t, here a=5 or 6;
* every r>=2 branch is impossible;
* every nonadapted branch eta=r is impossible.

It also proves cost(T)>=29 at t=2 and >=30 at t=3. For r>0 the only surviving
possibility is r=1 and eta in {2,3}. The adapted r=0 branch is treated
separately in ADAPTED-T2.md and ADAPTED-T3.md. For this remaining nonadapted r=1 case there are six actual outside
members and

    Sigma=cost(T)-8+eta,
    sum_F w=cost(T)+40+eta+c9.

The raw budget gives cost(T)+eta+c9<=32 at t=2 and <=33 at t=3.
The minimum threshold profiles and all possible ACTUAL inside profiles are
derived in [T2.md](T2.md) and [T3.md](T3.md), using the intrinsic four-/five-
piece exclusions, not the source's normalized lists.

## 3. Common restriction lemma for the nonadapted r=1 remainder

Let L=span(F intersect T). Then dim L=t+2 and D=C intersect L has
dimension at least two by dim(C+L)<=dim S. If dim D>=3, set the two
largest actual inside coordinates to zero on D. A nonzero codeword remains
in the two/three smallest actual members.

For four positive weights totaling at most 24, their last two have combined
capacity at most 40. For five totaling at most 25, the last three have
combined capacity at most 41, using

    g(1..7)=(1,2,4,8,12,20,36).

The latter tails cannot contain a weight-eight member: writing the tail
a>=b>=c gives 3a+b+c<=25, whereas a>=8 gives at least 26. Both bounds
are below the code distance53. Hence dim D=2 and C+L=S.

Restriction to C is injective on Ann(L): a functional vanishing on both
C and L vanishes on S. The six actual outside coordinate functionals are
independent in Ann(L), so their restrictions x_j are independent. Thus
their corrected frame indices are distinct. If J is the set of these
indices, every normal of D is supported on the remaining 8-|J| frame axes.
This does NOT assert distinctness of corrected inside indices.

The restriction-injectivity core and extraction of coefficients of an
outside relation are formalized in [formal/OutsideRestriction.lean](formal/OutsideRestriction.lean).
[formal/FiniteOutside.lean](formal/FiniteOutside.lean) constructs the finite
scalar combination and derives its laws from individual coordinate maps and
biorthogonality. Instantiating the actual spaces and dimension bridge remains
written mathematics.

## 4. Residual cases

[T2.md](T2.md) excludes all four possible t=2 inside profiles:
8771, 9771, 8871, 8772. The genuinely new 8771 argument completes a
frame-difference support to its forced binary hyperplane and then uses the
12+12 sign split on the common frame neighborhood. The 8871 argument
uses actual coordinate kernels and matched-cut intersections. It permits
repeated corrected inside indices.

[T3.md](T3.md) excludes every remaining t=3 inside profile:
87711, 77721, 97711, 88711, 87721, 77722, 87541, 87631, 77731,
77641, 77551. Some of these are actual-profile lemmas already used in
PR3689; their needed hypotheses and proofs are restated explicitly, so
no unsupported replacement of the global threshold T by L occurs.

These contradictions exclude r=1, eta>1. Combining with the inherited
r>=2 and eta=r exclusions proves the budgeted theorem for EVERY r>0.
ADAPTED-T2.md closes every adapted t=2 profile using the two-flat union
lemma of DOUBLE-SEVEN.md. ADAPTED-T3.md and ADAPTED-T3-HIGH.md close every
adapted t=3 profile through inside sum 32 and every high-containing case;
MERGE.md handles inside sum 33 by reducing to the already proved t=2 theorem.
This proves the budgeted theorem for ALL r, in this order without circularity.

## 5. Marked and unmarked consequences

The PR3455 raw-count theorem gives n_c<=m-2 when an actual restricted dual
is a nonzero multiple of a live root; here m=8+t. If a marked invoice
had I<=64, its raw sum would be <=64+m-2=72 or73, contradicting the
budgeted theorem. Therefore the marked d=3 invoice is I>=65,
and I-epsilon_k>=64 for epsilon_k in {0,1}.

Without a mark, the general actual-basis bound n_c<=m-1 gives: I<=63
would imply raw sum<=63+m-1=72 or73, again impossible. Thus the
unmarked d=3 invoice is I>=64.

These statements extend the corresponding nonpivot branch of PR3455's
singleton-pivot consumer, with all its exact actual-rank, nonparallelity,
and pivot hypotheses retained. The free-pivot branch supplies its stated
nonzero marked coefficient; the paid-pivot branch pays the possible
rebate. They are not a proof of global rank/pivot normalization.

More explicitly, the consumer has 9+t actual terms, actual ranks (9,8+t),
nonzero pairwise nonparallel rows and a singleton live-root pivot. Its
recovered NONPIVOT actual basis must have d=3 as defined above, with either adaptation status.
Under those hypotheses its cost is at least 64. This paragraph does not
extend the conclusion to an arbitrary rank/pivot branch.

## 6. What remains

The d>=4 actual invoices, global branch coverage and full C1 remain open.
No selected frontier or kappa changes. The E8 geometric instantiation,
root-system/field transfer, actual basis construction, and complete invoice
assembly remain written mathematics, not Lean theorems. Exact finite checks
support their stated inputs; they do not exhaust arbitrary field
coefficients or arbitrary actual bases.
