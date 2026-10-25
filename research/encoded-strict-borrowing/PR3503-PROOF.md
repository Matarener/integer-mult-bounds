# Exact strict-volume padding and least borrowing

Fix integers q>=2, w>=1, m>r>=1, b>=1 and Q>=1. Keep w fixed throughout
one invocation. Let D(n)=0 for n<m and D(n)=1+D(r floor(n/m)) otherwise.
The prescribed NODE reserve is S_0=1 and S_d=Q b^d for d>=1.

This result changes the covering premise in Nick Petalas's PR3486. Its exact
proof is retained in comparison/PR3486-PROOF.md. That predecessor requires
R=q^k>=S_D(n). It does not claim optimality for the padding volume condition
studied here. We retain its fixed-width geometry and actual-body depth.

## 1. The exact padding condition

For positive integers R,S, put Rprime=ceil(R/S)S. Then

    Rprime < 2R  if and only if  S < 2R.                 (1)

Necessity follows from S<=Rprime. For sufficiency, if R<S, Rprime=S<2R.
If R>=S, rounding gives Rprime<R+S<=2R. Equality S=2R is excluded. In
particular Rprime>=R and Rprime is the least positive multiple of S that
can hold all R genuine rows. If it fails the volume bound, every larger
multiple fails too. Thus (1) is exact for positive compatible-row padding,
with the given strict factor-two volume budget.

Jose Manuel's PR2786 planner, retained inside PR2808's canonical archive,
requires a completed stock group and rejects R<S before reading payload.
The present opt-in planner keeps that exact code on R>=S. On the new domain
S/2<R<S, it returns padded=S and added=S-R using canonical Count tapes.
It checks the strict inequality before payload access. No frozen module or
default caller is changed. The implementation bounds input Counts to 4096
bits; the theorem itself has no such cap.

The successor complete function uses the retained transform in both directions
and the same distinct-output, canonical-head and zero-added-output checks.
Assume the callee borrows and preserves its complete padded input, returns a
distinct output, restores its heads, preserves each prefix and fresh-row ordinal,
and applies the required Boolean permutation within each row. Each added row
then remains zero. Restriction returns the required genuine rows, in their
original order, and erases the temporary padded/returned tapes. This argument
does not require R>=S. Zero-output checks alone do not prove the semantic
row-pointwise callee premise.

## 2. The exact borrowing predicate

Put

    n(k)=floor((e-k)/w),
    U=min(floor((e-1)/2),e-mw),
    T_d=min{j>=0:2q^j>S_d}.

There is an admitted plan in this model exactly when some integer k in [0,U]
satisfies k>=T_D(n(k)). The upper bound expresses strict borrowing fit 2k<e
and n(k)>=m. Equation (1) proves the remaining equivalence.

The child map is nondecreasing and strictly contracts every internal width.
Strong induction therefore shows that D is finite and nondecreasing. The
reserve S_d, including d=0, and T_d are nondecreasing. As k increases, n(k)
and T_D(n(k)) are nonincreasing. Hence the predicate is monotone. If U<0,
or U fails, no plan fits. Otherwise bisection on [0,U] returns the least
admitted integer k. Each iteration halves the search interval, rounded up.
minimum.py validates monotone exact threshold tables and implements this
decision with at most e.bit_length()+1 iterations. The caller must supply
the mathematical certificate that each table entry is the exact T_d.

This is a conditional optimization of a prescribed reserve and volume budget.
It does not optimize over other atom widths, storage formats, volume budgets,
or callee implementations.

## 3. At most one borrowed radix digit is saved

Let L_d=min{j>=0:q^j>=S_d}, the covering-constrained threshold. Then

    max(0,L_d-1) <= T_d <= L_d.                        (2)

The upper bound is immediate. If j<=L_d-2, then q^(j+1)<S_d, while
2q^j<=q^(j+1) because q>=2, so j is not admissible. The case L_d=0 is
also immediate. The strict boundary matters, for example q=2,S_d=2^h
has T_d=L_d=h, not h-1.

Every covering-feasible k remains feasible. If the strict optimum is k,
and k+1<=U, monotonicity and (2) show that k+1 is covering-feasible.
Therefore, when both optima exist, they differ by at most one. A strict plan
at k=U can instead have no covering-feasible successor. For example set
q=2,m=2,r=1,w=1,Q=3,b=1,e=3. At k=1 the body has n=2 and S=3;
Rprime=3<4 and 2k=2<3. Covering requires k>=2 and no plan fits. This is a
tiny genuine enlargement of the fit domain, not a new asymptotic cutoff.

## 4. A source-bound selected-prime example

Retain David Arias's selected m=64,r=42 caller and Nick Petalas's PR3246
NODE reserve

    q=2^127-1, Q=9475, b=28416 N H,
    N=|GL_64(F_q)|, H=q^(4096(w-1)).

The replay checks the standard Lucas-Lehmer certificate for this prime,
with prime exponent 127 and 125 iterations ending at zero. Define

    P=product_(i=1)^64 (1-q^-i), C_d=9475*28416^d.

Independent-column counting gives S_d=q^(4096wd) C_d P^d. Product and
Bernoulli inequalities give 1>P>1-1/(q-1) and
P^d>1-d/(q-1). Thus, for multiplier c in {1,2}, exact integer comparisons

    C_d < c q^h,
    C_d (q-1-d) > c q^(h-1) (q-1)                  (3)

certify the least exponent for q^j>=S_d when c=1, or c q^j>S_d when c=2.
The covering upper inequality is stronger than necessary and is strict in all
consumed cases. No floating logarithm or materialized GL64 stock is used.

The inverse depth thresholds satisfy a_1=64 and
a_(d+1)=64 ceil(a_d/42). Exact recurrence gives

    a_85=315043551193419392,
    e=630087102387535114, w=2,
    k_strict=696330, n_strict=a_85, ell_strict=0, D(n_strict)=85,
    k_covering=696331, n_covering=a_85-1, ell_covering=1,
    D(n_covering)=84.

The original width rule is still exactly w=ceil(e^(17/10000))=2, certified
by 1<e^17<=2^10000. At d=85, (3) certifies T_85=4096*2*85+10 and
L_85=4096*2*85+11. Equivalently the exact S_85 lies strictly between
R=q^696330 and 2R. Every smaller k has n(k)>=a_85 and fails its threshold.
At k+1 the depth drops to 84, and the covering plan fits. This proves the
one-digit improvement at the existing selected parameters. The large width
is arithmetic evidence, not a payload execution or performance measurement.

## 5. Consumer and cost boundary

Tekalign's PR3264 proof and Jose Manuel's PR2899 Ordinary.fitted supply the
conditional consumer path. Keep the genuine other high field R in the gap;
only the call's fresh-row field becomes Rprime. Pass all Rprime fresh rows
to each completed C0 call. Restrict immediately after each return, before the
intervening ADD or high-field exchange. Sequential calls reuse the reserve.
Since Rprime is a multiple of S_D(n), the same NODE quotient/Q guards apply.
Pointwise restoration and fresh-field ownership remain premises.

The actual ordinary wrapper also requires a nonempty high field R>1. The
selected witness has k>0 and satisfies that condition. Generic toy guard plans
with k=0 are arithmetic plans only; they are not asserted to fit that wrapper.

The new-domain planner uses a constant number of Count tapes and O(log S)
binary scans. Its payload padding/restriction uses the retained row scans on
volume Vprime<2V. The existing complete bill still includes both C0 calls,
all children, ADD/sign/high-field/remainder passes, acquisition, initialization,
restriction, routing and erasure. A one-digit borrowing improvement does not
remove any of those charges or improve the inherited asymptotic exponent.

The current implementation exposes a row adapter only. The complete selected
borrowing selector is a bounded host-integer specification. We do not install
an Ordinary callback, execute a selected GL64 payload, or prove uniform physical
setup/C0 costs. A real consumer still needs its source refinement, full-cover,
completed leaves, fresh fields, pointwise row/spectator restoration, ownership,
precision/tape and outer-transfer obligations. No supplier, new kappa, selected
frontier change or complete multiplication theorem follows.

## Evidence scope

The written arguments supply the unbounded claims. The primary bisection
census and separate direct stock/padding enumeration agree on all 8192 small
cases. Literal frozen Count execution covers 1152 row plans, and five complete
rowwise-reversal fixtures cover all 258 independent Boolean basis inputs.
Those fixtures have a synthetic completed rowwise callee; they do not execute
the actual physical C0. Failure controls check strict equality, malformed
outputs, borrowed-source preservation, returned-output erasure and optimized
public CLI rejection. RESULT.json records the exact arithmetic and digests.
