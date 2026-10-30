# Analytical ordinary admission for the twenty-one-improvement BIT word

Dugongue, with substantial OpenAI Codex assistance. All arguments here are informal mathematics using a stored predecessor certificate. No numerical pricing, mathematical program, source replay, solver, Lean check or external search was run. The conclusion is conditional ordinary BIT saving, not a complete multiplication exponent.

## 1. Actual word and retained source premises

The native constructions in [partial-retirement.md](partial-retirement.md), [snapshot-fusion.md](snapshot-fusion.md), [bit.md](bit.md) and [bit-refinement.md](bit-refinement.md) compose on the retained PR5512 G20 body. They give four target-debited partial-helper retirements and seventeen target-preserving full-helper fusions, fifteen of which are new in this release. The complete eighteen-call controller therefore has

    P_new = P_old -378 H1 -378 H3 +306 H4,
    T_new = T_old -72 H4.

All forty local owned fields are initialized and returned to zero. All surviving original inputs remain arbitrary. SOURCE versions, receiver outputs, full helper endpoints, outer rho routes, thin stages, complete matchers and spectators have their stated unchanged physical meaning.

The predecessor PR5512 records

    W = 11238,
    C0 = 0.00348398,
    C_L = 0.0034839853304,
    C_U = 0.0034839853305,

and its old signed moment F(C) is positive at C_L. Its tested ratios are

    alpha0 = P_(1-C0)/T_(1-C0) < 1,
    gamma0 = P_(1-C0+1/5)/(17^(1/5) T_(1-C0)) < 31/32,
    delta0 = W*18/(17^C0 T_(1-C0)) < 19/20.

These are retained predecessor statements, not freshly evaluated quantities. The full profiles are stated in [assembly.md](assembly.md). Write

    F_new(C) = F(C) +378 g(C),
    g(C) = 1+3^(1-C)-4^(1-C).

## 2. A quantitative concavity lemma without numerical pricing

**Lemma 1.** For 0 < C <= 351/100000,

    g(C) > (219/100) C.

**Proof.** The identity

    log((1+x)/(1-x)) = 2 sum_(j>=0) x^(2j+1)/(2j+1)

follows by integrating the geometric series on a compact subinterval of (-1,1). Positive truncation and a geometric tail at x=1/3 give

    56/81 < log 2 < 25/36,
    69/100 < log 2 < 7/10.

At x=1/2, retain three terms and bound every remaining denominator below by seven. This gives

    log 3 < 1+1/12+1/80+1/336 < 11/10.

For C in the stated interval, exp(-u) >= 1-u and the positivity of the logarithms imply

    g'(C)
      =4^(1-C) log 4 -3^(1-C) log 3
      >=4 log 4 -4C(log 4)^2 -3 log 3
      >111/50 -(196/25)C
      >=111/50 -(196/25)(351/100000)
      >219/100.

Since g(0)=0, integration proves the claim. These are rational comparison bounds for logarithms, not decimal root calculations. QED.

## 3. Rank-mass dominance proves convexity of the old moment

**Lemma 2.** For every cutoff u, the old productive rank mass above u is at least the old paid rank mass above u:

    sum_(k>=u) T_k k >= sum_(r>=u) P_r r.

Consequently F is convex on [0,351/100000], and for C>=C_L in that interval,

    dF/dC > -217000.

**Proof.** The complete old rank-mass surplus is 753, as recorded by PR5512. For u<=4, no productive rank has yet been removed; deleting paid ranks can only improve the surplus. For 4<u<=8, the only removed productive mass is 72*4=288, whereas at least the 25227 paid rank-one mass has been removed. The tail surplus is still positive.

For u>8, all low paid jobs and both low productive ranks are absent. Pair each remaining paid rank 14,21,28,35,42,49,56 with the productive rank one higher, with the same multiplicity 444. Pair paid rank 63 with productive rank 64, each of multiplicity 222. Each target in a pair has greater rank and rank mass, so its weighted tail dominates at every cutoff. The additional 222 productive rank-127 jobs only increase the tail. This proves dominance without evaluating a fractional moment.

For 0<=C<=351/100000 the function

    h_C(x)=x^(-C)(log x)^2

is nonnegative and nondecreasing on [1,127], since

    h_C'(x)=x^(-C-1) log x (2-C log x)>=0.

Here log 127<5 follows from 127<2^7 and log 2<7/10 in Lemma 1. Integrating h_C' against the nonnegative rank-mass tails yields

    d^2F/dC^2
      =sum_k T_k k h_C(k)-sum_r P_r r h_C(r)>=0.

Thus F is convex. Because F(0)=753 and F(C_L)>0, convexity bounds its derivative at and to the right of C_L below by the secant slope:

    dF/dC >= (F(C_L)-753)/C_L > -753/C_L > -217000.

The last inequality follows from C_L>0.00348 and 217000*0.00348>753. QED.

This dominance argument uses the complete old inventories, not a claimed monotonic relation between isolated query ranks. It is the additional analytical mechanism that avoids a very weak absolute derivative bound.

## 4. An explicitly funded test and both tail contractions

Set

    C_test=3497/1000000=0.003497,
    U=6993/2000000=0.0034965,
    B=437/125000=0.003496.

**Theorem 3.** At C_test the new complete native profile has

    F_new(C_test)>1/32.

Its source first-moment, second-moment and completion ratios are all strictly below one.

**Proof of the first moment.** Since C_L>0.0034839, Lemma 2 gives

    F(C_test)>-217000*(0.003497-0.0034839)>-2843/1000.

Lemma 1 and the exact rational comparison

    378*(219/100)*(3497/1000000)>289/100

give 378 g(C_test)>289/100. Consequently

    F_new(C_test)>289/100-2843/1000=47/1000>1/32.

Since the new productive moment is below 2^21,

    alpha_new(C_test)<1-2^-26.

The positivity is a proved inequality, not output from an interval engine.

**Proof of the tails.** At the predecessor's C0 put t0=1-C0 and s0=t0+1/5. Then 7/6<s0<6/5. The exact integer comparisons

    3^7>(7/2)^6,
    4^6<(16/3)^5

give 3^s0>7/2 and 4^s0<16/3. Therefore the entire paid second-moment change is favourable:

    P_new,s0-P_old,s0
      =18[-21(1+3^s0)+17*4^s0]
      <18[-21*(9/2)+17*(16/3)]<0.

This accounts for all 306 added H4 jobs. The productive t0-moment decreases by 72*4^t0<288. Its old value T0 satisfies

    T0>7614*8^(2/3)=4*7614>30000.

Since W_new=W-72<=W, the old source guards imply

    gamma_new(C0)<(31/32) T0/(T0-288)<99/100,
    delta_new(C0)<(19/20) T0/(T0-288)<99/100.

Both rational expressions decrease as T0 increases; substitute 30000 and multiply positive denominators to prove the displayed strict bounds.

Let epsilon=C_test-C0. Its exact value is positive and below 14/1000000. Each target rank is at most 127, paid moments decrease with C, and 17^C in the completion denominator increases. Thus either tail ratio grows by at most 127^epsilon. Since log 127<8,

    epsilon*log 127<1/8000,
    127^epsilon<1/(1-1/8000).

The elementary inequality exp(x)<=1/(1-x) on 0<=x<1 suffices. Consequently both new ratios at C_test are bounded by the explicit rational

    theta=(99/100)/(1-1/8000)<1.

This proves all three strict compiler guards without evaluating any transcendental moment. QED.

## 5. Fresh finite compiler constants and owned stock

The following is a conditional use of the same constructive native, all-column, mixed-target batching, fixed-tape, precision and ordinary-cover framework as PR5512. It does not prove those inherited physical hypotheses anew.

Put a=1-2^-26. Choose v to be the first positive multiple of 1024 satisfying

    a^v +4 theta^v <1/2.

This is a finite integer definition, not an executed search. The source chronological product completes each small target on its SAME independent owner at 18^v and splits each paid job at 17^v. Their charged contraction is at most the displayed expression. The source separation guard is 17^64<18^63; the ambient bound remains 127<256.

Set

    t=1-C_test, z=1-U, z0=(t+z)/2,
    h=1/64, d0=z0-t,
    R0=d0*(5+8h)*v+1+8v*(1-z0),
    H0=8192v+ceil(R0/(h*d0))+1,
    H1=floor(H0*(1-z0)/(z-z0))+1,
    N=2^H1.

Then d0>0 and the inherited guards hold directly:

    H0>=8192,
    H0*h*d0>R0,
    H1*(z-z0)>H0*(1-z0).

The source constructive integer batching gives a finite independent-row unit with leaf-to-row ratio below N^(1-U).

For explicit replacement finite majorants, let R be one plus the sum of the complete finite record, matching-step, role-incidence, descriptor, paid/target-job and owned-field counts, and the encoded bit lengths of every fixed coefficient, numerator, denominator, matching matrix entry and native descriptor in the changed base word. In particular R dominates coefficient and matcher heights as well as counts. This is the length of its specified finite encoded construction, not a mathematical census run here. Define

    D0=2^((R+1024)^4),
    K=2^(4v(R+1024)^4),
    J(n)=(n+1)^4 K^(4n+4),
    A(1)=K^4,
    A(n)=(J(n)+2)^4 (A(n-1)+2)^(4n+8).

The source description/height induction with these enlarged base constants bounds rows, leaves, suspended instances and fixed descriptions. Reserve at most 40 A(N) owned arrays, distinct for simultaneous instances. No owned field is counted as an independent row. The earlier twenty-four-, seventeen- or eleven-array bounds are not reused.

Put

    T_arith=(2N+2)^4 (A(N)+2)^2,
    H=(D0+2) 4^(T_arith+1).

Choose an odd prime q greater than max(2^45 N^5,2^(2H)) avoiding the finitely many compiled denominator and rank-witness primes. Every new H4 geometry is one of the source's actual frames 506 through 509, with its supplied two-sided matcher; geometry 507 is the original G20 helper-464 shadow matcher. Both fixed routing directions and all matching constants are charged.

A conservative multiplier in retained primitive invocations is

    F=40(D0+1)^4 (q+2)^(32(N+1)^2) (A(N)+2)^8.

Multiply it by the positive maximum retained primitive/backend coefficient when bounding machine time. It includes the new snapshots, delayed reader copies, clears, source preservation, head returns, parking and routes. No new unit-cost dense address primitive, Word RAM substitution or old cancellation-growth bound is assumed. These are finite constants fixed before the final input size grows; the source eventual-threshold proof absorbs them at a fresh threshold.

## 6. Acyclic ordinary completion

Use the retained whole-cover loss

    epsilon_cover=2^-36+10^-20,
    L=U-epsilon_cover.

The prime guard 2^45 epsilon_cover>256 is immediate. Also epsilon_cover<10^-9 and U-B=5*10^-7, so L>B+4*10^-7. This cover loss is not discarded. The source regular-cover/bad-class costs, whole-row matcher and borrowed-stock proof are retained with the new reserve and constants.

Start from the completed PR4814 backend b0=1737729/500000000. Put rho=1/100 and Q=10^12. Freeze successive completed algorithms by

    a_j=(1-rho)L+rho*b_(j-1),
    b_j=(ceil(Q a_j)-1)/Q.

The strict lower grid gives 0<a_j-b_j<=1/Q. At every backend call the finite level decreases; at every native coarse call the atom count decreases. There is no self-fallback. Stop at the first b_j>B. If none of the first five suffice, the elementary recurrence bound gives

    b_6 >= L-rho^6(L-b0)-(1-rho^6)/(Q(1-rho))
        > L-3*10^-12 >B.

Thus at most six finite levels suffice, without evaluating any b_j numerically. For each level let K_j be at least sixteen times the sum of its F-scaled positive retained primitive constants, its new reserve/adapter/stock bounds and the frozen completed preceding-backend coefficient. Enlarge it to include any additional finite base description. With

    eta_j=min(rho-a_j,1-rho-a_j,a_j-b_j)>0,

enlarge its eventual threshold to dominate

    ceil((32K_j/eta_j)^(ceil(8/eta_j)))+2^(ceil(8/eta_j)),

the previous backend threshold to power ceil(2/rho), and all finite base/stock thresholds. The standard source logarithm bound absorbs the positive coefficients. All borrowed arrays and digits are restored before their parent resumes. The resulting completed ordinary algorithm supports the weaker exact saving B.

## 7. Conclusion and attribution

Under the retained framework premises, the actual twenty-one-improvement word admits conditional ordinary BIT saving 0.003496. Its new native contribution is the fifteen source-specific target-preserving fusions, including compensated-reader cancellations and eight paid SOURCE refinements. This certificate is deliberately conservative and not a newly optimized crossing.

It does not prove ordinary BIT saving above 0.0035, a profitable Gaussian supplier there, or whole multiplication κ ≥ 0.0035. The exact profile improvement and complete analytical component admission are the positive result; the missing threshold is not inserted as an assumed gadget.

Retain ai-nanachi PR5512; Ali Romman PR5421; compact436/PR4326 and PR4760/PR4814; DreamingOfClouds PR589; eumemic PR555; Cinna Davis's native/ROW/controller/cover lineage; rohanarun PR185/PR199/PR204; zxv and Jacob Alan Sussman's compiler, mixed-target and precision work; all source notices; and the prior four-retirement/two-snapshot proofs. New text is Apache-2.0, with substantial OpenAI Codex assistance. The offline source pin is `5e0052ca0aa3036a3afa8b0438927377c8d97d53`.

