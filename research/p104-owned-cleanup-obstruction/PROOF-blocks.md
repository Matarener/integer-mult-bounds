FIXED-DELIVERY OWNED BLOCKS: A SCOPED RECURSIVE-MOMENT FLOOR

Status: source-bound proof with exact finite checks. No new kappa is claimed.

Source and reproducibility
--------------------------
The source is PR5569 head af9f091ac6f30c6eaacb9c27777bfbe2d0e5ffdf,
research/p104-priced-handoff/WORD.json.gz. Its compressed SHA256 is
12224e9a13a49c830b304338a8d31610fb43da15d1a650537733c27f7864310f.
The registered verify.py calls check_lifetimes.py using Python's standard
library. It imports no predecessor verifier and compares a committed receipt. This audit checks exact rational
scalar rows, frame nesting, local rank tariffs and two-sided boundaries. It is
not a substitute for the source's native character and complete funding replay.

Definitions and permitted replacements
--------------------------------------
Let H_d(t)=d^t for 0<t<=1 (in the source, t=1-kappa). A public MOVE ascends to a
containing frame and a private owned MOVE descends to a contained frame. A MOVE
of positive dimension difference d is charged H_d. Rational ADD, SCALE and COPY
must act at the same current frame. A new owned field starts at zero. CLEAR may
erase an owned field, under the source's inherited owned-erasure assumptions.

A fixed-delivery replacement for one block has exactly the same public roles,
entry and exit frames, and public scalar map. It may use arbitrarily many new
zero-initialized private fields and arbitrary rational linear operations. It
may change its internal contacts, order and factorization. It leaves all
private fields zero or cleared at its exit. It cannot read or modify external
public roles, carry workspace across the boundary, change productive targets,
or claim new productive credit. These are substantial restrictions; the result
does not rule out a better complete word or cross-block sharing.

Theorem (uniform delivery star)
-------------------------------
Suppose the public boundary has independent coordinates v,x_1,...,x_m. The
source v starts and ends at dimension a. Each x_j starts at dimension zero and
ends at one common dimension b frame, where a>b>=1. The required map is

    v -> v,          x_j -> x_j+c_j v,          c_j != 0.

Under the permitted replacement model, every replacement pays at least

    m H_b(t) + H_(a-b)(t).

This theorem is useful when a literal implementation attains the floor. It
does not assert that arbitrary given frames admit such an implementation.

Proof. Each physical public recipient has to ascend from dimension0 to b.
If its ascents have ranks d_1,...,d_k, their sum is b; because
sum_i d_i^t >= (sum_i d_i)^t, its paid moment is at least H_b(t). Summing these
disjoint public moves gives m H_b(t).

At least one final recipient contains a nonzero v coefficient. Expand its
coefficient through the chronological linear circuit. There is a nonzero
dependency path from the source entry to that recipient exit: zero INIT and
CLEAR cannot create the v coefficient, and cancellation of several paths
cannot leave a nonzero coefficient when there were no contributing paths.
Along this path scalar operations preserve frame dimension; public MOVEs have
nonnegative dimension change and owned MOVEs have nonpositive dimension
change. The path starts at dimension a and ends at dimension b. Its total
owned descent rank is therefore at least a-b. If these descents have ranks
r_1,...,r_l, their tariff is at least

    sum_i r_i^t >= (sum_i r_i)^t >= (a-b)^t.

These owned moves are disjoint from the public moves charged above. All other
paid events have nonnegative tariff, proving the bound. Auxiliary dimension,
number of fields, rational coefficients, internal cancellation and uncompute
strategy do not change this argument. END PROOF.

Application to the eight literal lifetimes
------------------------------------------
Intervals below are zero-based and half open. All seven uniform stars have
a=8,b=1, source unchanged, owned exit zero, and independent actual prefix rows.

owned  interval         source  recipients                 coefficient  tariff
735    [13377,13388)     173     704,705,706                +1/2         3H1+H7
736    [13388,13399)     151     707,708,733                +1/2         3H1+H7
737    [13399,13408)     146     709,732                    -1/2         2H1+H7
738    [13408,13424)     133     159,203,148,710,734        varied       5H1+H2+H3
739    [13424,13439)     256     712,713,714,715,716        +1/4         5H1+H7
740    [13439,13454)     92      717,718,719,720,721        +1/4         5H1+H7
741    [13454,13469)     9       722,723,724,725,726        +1/4         5H1+H7
742    [13469,13484)     240     727,728,729,730,731        -1/4         5H1+H7

For each of the seven stars, the literal cost attains the theorem. Therefore
even a changed internal scalar word cannot lower that block's raw recursive
paid moment, at any 0<t<=1, within the stated boundary model. Separate local
replacements cannot improve their combined 28H1+7H7. This combined statement
does not allow any private work to cross the fixed boundaries.

The theorem does NOT give the observed cost for738. Its recipient entry/exit
dimensions are 7->7,6->6,2->3,0->1,0->1. Its public tariff is3H1 and its owned
tariff is2H1+H2+H3, delivering at levels7,6,3,1,1. The elementary dimension-path
argument only gives3H1+H7. No tight arbitrary-replacement bound for738 is claimed.
For example, attempting to deliver148 at its entry frame467 and then continue
down to frame597 fails because frame597=[82] is not contained in
frame467=[45,194]. This rejects that one template only.

Why the local target map is forced by these two-sided cuts
---------------------------------------------------------
For a block let P be the matrix of its public entry rows on independent
original scalar symbols, and S the fixed suffix map from its public exit
coordinates to all final public coordinates. Let T be the literal local map
and R a proposed local map. When the replacement cannot access external
coordinates and leaves those coordinates unchanged, full-word equality is

    S (R-T) P = 0.

The checker verifies that P has full row rank and S has full column rank for
all eight blocks. The ranks are4,4,3,6,6,6,6,6, respectively. Thus a right inverse
of P and a left inverse of S imply R=T. This is an elementary finite-dimensional
linear algebra fact; it is not attributed as a new external theorem.

The checker also verifies that retired owned coordinates have no subsequent
public effect, but their required zero exit is an independent condition. The
absence of public suffix influence does not authorize leaving private garbage.
Each block has an omitted-delivery negative control that demonstrably changes
at least one final public scalar output.

Important independence caveat
-----------------------------
In the actual source, register173 is a helper, not a live main register.
Its prefix row has118 nonzero original coefficients and its information also
occurs in external registers. The verified row rank says the listed local
coordinates are linearly independent; it does not say their information exists
nowhere else. This is why outside side-information reuse is explicitly outside
the fixed-delivery theorem. In particular, this theorem does not prove that
the literal COPY producer is globally optimal.

Scope of the result
-------------------
The seven tight floors concern raw recursive paid moments for fixed local
public boundaries and unchanged productive targets. They do not establish a
new complete bound, exclude lower ordinary scalar compilation costs, certify
new credits, or rule out shared multi-block construction or changing the
global public schedule. The eighth lifetime is deliberately left unresolved
by the stronger changed-internal-word claim. See PROOF-loss-space.md for a
separate global but non-additive preparation bound.

Prepared for flyingviper with substantial OpenAI Codex assistance and
independent agent checks. Apache-2.0.
