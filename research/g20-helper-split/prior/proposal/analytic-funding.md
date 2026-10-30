# Conditional ordinary BIT saving 0.003503 from deferred helper inputs

Dugongue, with substantial OpenAI Codex assistance. All arguments here are informal mathematics using a stored predecessor certificate. No numerical pricing, mathematical program, source replay, solver, Lean check or external search was run. The conclusion is conditional ordinary BIT saving, not a complete multiplication exponent.

## 1. Actual word and retained source premises

The retained constructions in [partial-retirement.md](partial-retirement.md), [snapshot-fusion.md](snapshot-fusion.md), [predecessor-protected-reader.md](predecessor-protected-reader.md) and [predecessor-source-refinement.md](predecessor-source-refinement.md) give the preceding exact G20 program. [bit.md](bit.md) then retires nine further independent helper inputs by explicit late binding at common physical frames. Every retirement removes H1+H7 and debits H8. It does not assume that a counterfactual helper entrance is computed at runtime.

The complete eighteen-call controller now has

    P_new=P_old-540 H1-378 H3+306 H4-162 H7,
    T_new=T_old-72 H4-162 H8.

All forty-nine local owned fields receive paid initialization and return zero. All surviving original inputs remain arbitrary. The SOURCE versions, main physical endpoint, remaining helper endpoints, whole-job matchers, outer rho routes, complete ROW and spectators retain their supplied source meaning. No surviving main input is erased when its temporary value is made zero: its information was copied into a newly owned helper and is recovered by the retained suffix.

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

    F_new(C)=F(C)+378 g(C)+162 j(C),
    g(C)=1+3^(1-C)-4^(1-C),
    j(C)=1+7^(1-C)-8^(1-C).

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

**Lemma 1b.** On the same interval 0<C<=351/100000,

    j(C)>(11/4)C.

**Proof.** Keeping the first two terms of the log-2 expansion and bounding every remaining denominator below by five gives

    log 2<56/81+1/540<347/500.

The integral for log(1-x) gives log(1-x)<-x-x^2/2 for 0<x<1. Therefore

    log 7=3 log 2+log(1-1/8)
         <3*(347/500)-1/8-1/128<39/20.

Also 207/100<log 8<21/10 by Lemma 1. Using exp(-u)>=1-u on the positive term and 7^(1-C)<7 on the negative term yields

    j'(C)=8^(1-C) log 8-7^(1-C) log 7
         >291/100-(882/25)C
         >=291/100-(882/25)(351/100000)>11/4.

Since j(0)=0, integration proves the claim. The comparisons are explicit rational inequalities, not a numerical price calculation. QED.

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

    C_test=0.003504,
    U=0.0035035,
    B=0.003503.

**Theorem 3.** The actual changed complete profile has F_new(C_test)>1/32. All three source compiler ratios are strictly below one there.

**Proof of the first moment.** The retained endpoint has C_L>0.0034839. The convexity/secant estimate of Lemma 2 gives

    F(C_test)>-217000*(0.003504-0.0034839)>-437/100.

Lemmas 1 and 1b and an exact rational comparison give

    378 g(C_test)+162 j(C_test)
      >[378*(219/100)+162*(11/4)]*(3504/1000000)
      >89/20.

Consequently

    F_new(C_test)>89/20-437/100=2/25>1/32.

The productive moment is below 2^21, so

    alpha_new(C_test)<1-2^-26.

This is a proved strict moment above 0.0035 for the complete changed native word, not an optimistic isolated deletion.

**Proof of the tails.** At C0 let t0=1-C0 and s0=t0+1/5. As in the predecessor analytical admission, 7/6<s0<6/5, 3^s0>7/2 and 4^s0<16/3. The full paid second-moment change is

    P_new,s0-P_old,s0
      =18[-21(1+3^s0)+17*4^s0]-162(1+7^s0)<0.

The last negative term charges exactly the nine extra local retirements. The productive t0-moment loss is

    72*4^t0+162*8^t0<288+1296=1584.

Using C0<1/100 and log 8<21/10,

    8^t0=8 exp(-C0 log 8)>8[1-(1/100)(21/10)]>7.

Hence the old productive moment T0 exceeds 7614*7>53000. The new independent count is W_new=W-72-162=11004. The old strict guards imply

    gamma_new(C0)<(31/32)T0/(T0-1584)<999/1000,
    delta_new(C0)<(19/20)T0/(T0-1584)<999/1000.

Both expressions decrease in T0. Substituting 53000 and multiplying positive denominators proves the final rational inequalities. No removed target or completion term is omitted.

Let epsilon=C_test-C0. Its exact value is positive and below 21/1000000. Since log 127<5,

    epsilon log 127<1/8000,
    127^epsilon<1/(1-1/8000).

The paid moment decreases as C increases, every productive rank is at most 127 and the 17^C completion denominator increases. Thus this factor bounds either tail ratio's possible growth. Both tail ratios at C_test are bounded by the rational

    theta=(999/1000)/(1-1/8000)=7992/7999<1.

This proves the complete first- and higher-moment admission guards. QED.

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

The source description/height induction with these enlarged base constants bounds rows, leaves, suspended instances and fixed descriptions. Reserve at most 49 A(N) owned arrays, distinct for simultaneous instances. No owned field is counted as an independent row. The earlier forty-, twenty-four-, seventeen- and eleven-array reserves are not reused.

Put

    T_arith=(2N+2)^4 (A(N)+2)^2,
    H=(D0+2) 4^(T_arith+1).

Choose an odd prime q greater than max(2^45 N^5,2^(2H)) avoiding the finitely many compiled denominator and rank-witness primes. Every new H4 geometry is one of the source's actual frames 506 through 509, with its supplied two-sided matcher; geometry 507 is the original G20 helper-464 shadow matcher. Both fixed routing directions and all matching constants are charged.

A conservative multiplier in retained primitive invocations is

    F=49(D0+1)^4 (q+2)^(32(N+1)^2) (A(N)+2)^8.

Multiply it by the positive maximum retained primitive/backend coefficient when bounding machine time. It includes the new snapshots, late bindings, delayed reader copies, clears, source preservation, head returns, parking and routes. The unexecuted counterfactual helper entrances are correctness parameters, not runtime states or new arithmetic primitives; coefficient and precision bounds cover the actual finite program. No new unit-cost dense address primitive, Word RAM substitution or old cancellation-growth bound is assumed. These are finite constants fixed before the final input size grows; the source eventual-threshold proof absorbs them at a fresh threshold.

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

Under the retained native/physical, constructive compiler, ordinary-cover/backend, precision, fixed-tape and analytic framework premises, this actual complete BIT word admits ordinary saving B=0.003503. In particular it supplies a component saving strictly above 0.0035. The old predecessor interval is used as retained evidence; no new numerical root or optimization is claimed.

This does not prove whole multiplication κ ≥ 0.0035. A compatible complete funded Gaussian supplier and the actual outer assembly are still required. The result here closes the requested BIT component threshold, not those separate obligations.

Retain ai-nanachi PR5512; Ali Romman PR5421; compact436/PR4326 and PR4760/PR4814; DreamingOfClouds PR589; eumemic PR555; Cinna Davis's native/ROW/controller/cover lineage; rohanarun PR185/PR199/PR204; zxv and Jacob Alan Sussman's compiler, mixed-target and precision work; all source notices; and the prior four-retirement/two-snapshot proofs. New text is Apache-2.0, with substantial OpenAI Codex assistance. The offline source pin is `5e0052ca0aa3036a3afa8b0438927377c8d97d53`.

