# Rational certificates for complete Gaussian funding

## The complete inventory

Let P_r and T_k be nonnegative integer multiplicities of every paid and productive positive-rank Gaussian job of one actual complete finite program. All removed productive targets have been debited. Set

    F(C)=sum_k T_k k^(1-C)-sum_r P_r r^(1-C).

Keep actual main jobs, helper jobs, boundaries, idles, thin queries, newly paid warps and scratch-query copies in their proper places. Owned scratch is not productive. The following theorems apply to a full signed inventory, independently of how it was nominated.

## Entropy and curvature give a sufficient funding test

Define

    M=sum_k T_k k-sum_r P_r r,
    S=sum_r P_r r log r-sum_k T_k k log k,
    L=sum_r P_r r (log r)^2.

**Theorem 1.** For every C>=0,

    F(C)>=M+C S-(C^2/2)L.

In particular, strict positivity of the right side is sufficient for complete first-moment funding at that C.

**Proof.** F(0)=M and F'(0)=S. For x>=0,

    F''(x)=sum_k T_k k^(1-x)(log k)^2
                   -sum_r P_r r^(1-x)(log r)^2 >=-L,

because k>=1, the productive sum is nonnegative, and r^(1-x)<=r. Integrate this lower bound twice, or use Taylor's integral remainder. QED.

This does not assume convexity, rank-mass tail dominance or a measured old root. It is a universal sufficient test and may be conservative.

**Corollary 2.** If M=0, S>0 and L>0, every 0<C<2S/L has F(C)>0.

**Lemma 3.** The entropy slope S is the logarithm of an explicit positive rational:

    exp(S)= product_r r^(P_r r) / product_k k^(T_k k).

Thus the sign of S can be certified by comparing two integers. A quantitative lower bound for S can be certified by rational logarithm bounds without evaluating F.

**Proof.** Apply additivity of log to the finite products. QED.

This gives a cheaper screening quantity for downstream searches. A positive slope alone is not sufficient at a specified positive C: M and the curvature term remain in the certificate.

## Produce logarithm bounds with rational arithmetic

For any integer a>=1 choose m with 2^m<=a<2^(m+1), and set q=a/2^m and z=(q-1)/(q+1). Then 0<=z<1/3 and

    log a=m log 2+2 sum_(j>=0) z^(2j+1)/(2j+1).

At z=1/3 the same series gives log 2. For N>=1, its positive tail is bounded by

    0<=remainder<=2 z^(2N+1)/((2N+1)(1-z^2)).

**Lemma 4.** These finite expressions supply rational bounds l_a<=log a<=u_a to arbitrary precision, with l_1=u_1=0.

**Proof.** Integrate the geometric series for 1/(1-z^2). Bound every denominator in the omitted tail below by 2N+1 and sum the resulting geometric series. Its tail tends to zero uniformly for 0<=z<=1/3. Scaling by the integer m gives the result. QED.

A certificate can list N and the resulting rational endpoints. A checker needs integer and rational arithmetic only. Optimizer output is not trusted as a logarithm bound.

With such bounds, set

    S_lo=sum_r P_r r l_r-sum_k T_k k u_k,
    L_hi=sum_r P_r r u_r^2.

The exact rational inequality M+C S_lo-(C^2/2)L_hi>0 proves Theorem 1's strict funding condition whenever C is rational.

## Certify all three stated source guards

Suppose the supplied compiler contract for this actual caller uses

    alpha=P_(1-C)/T_(1-C),
    gamma=P_(1-C+1/5)/(c^(1/5) T_(1-C)),
    delta=W b/(c^C T_(1-C)),

where c>1, b>0 and W is a proven upper bound for the actual completion-field count. These are the retained source forms; a different caller convention requires its own formulas. W must include all declared completion jobs. A helper becoming rank zero does not justify reducing W without a source-specific proof.

Take rational C>=0 and rational nonnegative log bounds l_a,u_a for every used rank and for c. Choose positive rational A_r with

    A_r^5>=r^6,

and positive rational h with h^5<=c. Define

    D=sum_k T_k k(1-C u_k),
    U1=sum_r P_r r[1-C l_r+(C u_r)^2/2],
    U6=sum_r P_r A_r[1-C l_r+(C u_r)^2/2].

**Theorem 5.** The exact rational inequalities

    D>0,
    D-U1>0,
    h D-U6>0,
    (1+C l_c)D-W b>0

suffice for alpha<1, gamma<1 and delta<1 at this C. The second line may instead be replaced by the positive entropy-curvature certificate above.

**Proof.** For x>=0,

    1-x<=exp(-x)<=1-x+x^2/2.

The lower bound is the tangent-line inequality. The upper bound follows by integrating the second derivative bound exp(-x)<=1 twice. Thus T_(1-C)>=D. For each paid rank,

    exp(-C log r)<=1-C l_r+(C u_r)^2/2.

The right side is positive, since replacing l_r by u_r only decreases it and 1-x+x^2/2>=1/2. Consequently P_(1-C)<=U1. Also A_r>=r^(6/5), so P_(1-C+1/5)<=U6. Finally c^(1/5)>=h and c^C=exp(C log c)>=1+C l_c. Substitute these bounds into the three positive-denominator ratios. Strictness comes from the displayed rational margins. The alternative first-moment certificate proves T_(1-C)>P_(1-C) directly. QED.

Every fifth-power test here is an integer comparison after clearing positive denominators. Higher-order exponential bounds can tighten a failed certificate, but failure of these sufficient inequalities is not evidence that the candidate itself fails.

## A useful frozen target for downstream validation

One proposed strict test is

    C_star=219/62500=0.003504.

It lies above 0.0035 and leaves room for an inherited ordinary-transfer loss. The test is a target, not an established new Gaussian exponent. A contributor must instantiate the complete program, all three guards, fresh ordinary and precision constants, actual source embeddings and outer hypotheses before selecting a final ordinary saving. The fixed BIT value 0.003503 and a positive Gaussian local gain alone do not prove whole multiplication κ ≥ 0.0035.

## Why this certificate is useful for a large search

The search may nominate thousands of exact coframe assignments, but only a successful complete witness and its strict margins need enter a PR. The certificate provides a separate route to validate that winner without trusting its search code, wall-clock budget or floating-point objective. For an unfunded local supplier, report a proved local inequality or transformation instead of presenting its positive relative gain as an absolute exponent.

The elementary logarithm and signed-moment framework has retained predecessors in the BIT admission and Gaussian supplier notes. The additional result here is a uniform entropy-curvature certificate and a rational test for all three complete source guards. Preserve the analytical and compiler credits in README.md.
