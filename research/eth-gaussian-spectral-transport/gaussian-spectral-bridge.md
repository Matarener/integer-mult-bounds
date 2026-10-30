# A spectral bridge to the existing Gaussian tensor engine

This is a direct application to the matrix already specified in the project's GaussianTensorExecution source. It is an exact informal construction with a degree/denominator/exceptional-rank tradeoff. The cost of the exceptional modes is retained; no improved multiplication exponent is claimed without that bill.

## 1 The actual source matrix

The source's raw forward axis is

    C = [[i,1],[1,i]],       π=1+i.

Its inverse-axis numerator is [[1,i],[i,1]], whose product with C is 2i I=π^2 I. Thus the normalized forward axis A=C/π and normalized inverse axis are exact inverses. The recursive forward source applies C independently in all n tensor positions, so its normalized matrix is

    A_n = A tensor ... tensor A   (n factors).

This statement follows directly from the axisForward and forward definitions; it is not a new kernel audit or a physical implementation theorem. Their source comments already distinguish finite Gaussian arithmetic from tape layout and runtime.

Let X_j swap the two coordinates in tensor position j and put

    D_j=(I-X_j)/2,       W=sum_(j=1)^n D_j.

The D_j are commuting idempotents. The eigenvectors (1,1) and (1,-1) of X have normalized A eigenvalues 1 and i respectively. For ε in {0,1}^n, write χ_ε(s)=(-1)^(ε dot s), where s ranges over the n-bit coordinates. Then

    W χ_ε = |ε| χ_ε,       A_n χ_ε=i^(|ε|) χ_ε.

These 2^n Walsh vectors form a basis over Q(i). No assertion that their change of basis is free is used.

## 2 An exact central-weight interpolant

Choose integers n>=1, 0<=R<=n and 0<=a<=n-R. Define

    g(X)=i^a sum_(h=0)^R (i-1)^h binom(X-a,h),

where binom(X,h) is its ordinary rational polynomial.

**Theorem B1 (central Gaussian spectral replacement).** The degree of g is at most R, and g(j)=i^j for every integer j in [a,a+R]. Consequently g(W) agrees exactly with A_n on the direct sum of Walsh-weight spaces in that interval. The residual A_n-g(W) has rank at most

    t=2^n-sum_(j=a)^(a+R) binom(n,j).

**Proof.** At j=a+k, 0<=k<=R, the terms h>k vanish and the binomial theorem gives

    g(a+k)=i^a [1+(i-1)]^k=i^(a+k).

The displayed Walsh eigenidentities then give agreement on each stated eigenspace. All remaining eigenspaces together have dimension t, and the residual vanishes on their complement. QED.

The correction is completely explicit:

    A_n-g(W)
      =2^(-n) sum_(ε: |ε| outside [a,a+R])
          [i^(|ε|)-g(|ε|)] χ_ε χ_ε^T.

**Proof.** The Walsh vectors are pairwise orthogonal with squared norm 2^n. Their normalized rank-one projectors sum to I. Apply the eigenvalue formula term by term. QED.

This is an emitted factorization, not an assumed rank gadget. Some outside coefficients may vanish as well, so the stated rank bound need not be tight.

## 3 The low-degree bulk needs only R Gaussian denominator units

The preprint's swap construction interpolates (-1)^j and yields integer ordinary words. The actual Gaussian tensor requires the four-periodic sequence i^j instead. The following calculation gives its exact, different denominator bill.

For j>=0 define the elementary-symmetric ordinary operator

    E_j=sum_(S subset [n], |S|=j) product_(k in S)(I-X_k),
    E_0=I.

Since the D_k are commuting idempotents,

    binom(W,j)=2^(-j) E_j.

One proof is to apply both sides to every Walsh vector of weight k: both eigenvalues are binom(k,j). Using the polynomial Vandermonde identity gives

    g(W)=sum_(j=0)^R b_j E_j,

    b_j=i^a 2^(-j) sum_(h=j)^R
            (i-1)^h binom(-a,h-j).

Every binom(-a,k) is an integer. This includes a=0, where all positive k terms vanish.

**Theorem B2 (denominator debt R, not n).** Every c_j=π^R b_j is a Gaussian integer. Therefore the ordinary operator π^R g(W) has an explicit Gaussian-integer scalar/permutation program. In contrast, the literal normalized tensor expression A_n=π^(-n) C^(tensor n) carries n Gaussian denominator units.

**Proof.** Since i-1=iπ and 2=-iπ^2, the summand in b_j indexed by h has Gaussian valuation h-2j>=-j>=-R. Its only denominators are powers of 2. Multiplying by π^R therefore gives a Gaussian integer, and so does summing the terms. Each E_j is an integer combination of permutation products. QED.

The theorem describes an actual numerator grid. It does not assert that g(W)x itself is integral for every integral x, nor does it perform a forbidden exact division on such an x. Its output can be stored as the numerator π^R g(W)x with the declared π^(-R) grid. The full result A_n x and the correction still need their own exact output-grid accounting.

For an explicit coefficient-height bound,

    |c_j| <= (R+1) 2^R (a+R+1)^R.

Indeed |binom(-a,k)|<= (a+R+1)^R for k<=R, and each term after scaling has magnitude at most 2^(R/2-j) 2^(h/2) times that bound, at most 2^R times the bound. There are at most R+1 terms. Thus the real and imaginary integer coefficients have a bit-length bound

    B_c=2+ceil(log2(R+1))+R+R ceil(log2(a+R+1)).

This bound is conservative, finite and valid also at R=0.

## 4 Literal ordinary synthesis and its bill

Let x have 2^n Gaussian payload coordinates. Initialize owned arrays d_1,...,d_R to zero and keep d_0=x as a read-only original. Process k=1,...,n. For j=min(k,R),...,1 in DESCENDING order execute

    d_j += d_(j-1),
    d_j -= X_k d_(j-1).

After processing k, d_j is the elementary-symmetric sum over the first k positions applied to x. The descending order is essential: its source is still the previous-k value. At completion d_j=E_j x. Form the owned output

    G=sum_(j=0)^R c_j d_j = π^R g(W)x.

Gaussian-integer coefficient multiplication is an explicit repeated-doubling/addition word on real and imaginary parts, followed by the ordinary multiplication-by-i phase. Its word length is O(B_c) per coefficient. Permutation reads, actual scans or routing and all scratch are retained. One can preserve x and clear all other owned arrays under the declared owned-erasure contract.

**Theorem B3 (ordinary numerator compiler).** The above is an explicit uniform synthesis using O(nR+R B_c+1) whole-array linear additions/phases and routed permutation reads, with at most R+4 owned arrays including output and work storage. In coordinate operations its arithmetic count is O((nR+R B_c+1)2^n), before the actual operand-bit and movement charges.

**Proof.** The usual elementary-symmetric recurrence is E_j^(k)=E_j^(k-1)+(I-X_k)E_(j-1)^(k-1). The descending program implements precisely this recurrence. Count at most nR pairs of additions, then R+1 coefficient products and output additions. Binary synthesis of each coefficient uses O(B_c) operations, and the phase requires one additional ordinary operation per used coefficient. Arrays d_1,...,d_R, the output, a routed-permutation workspace and two coefficient work arrays suffice. Read x but never overwrite it. QED.

If the host supports only reversible owned additions, this description still requires the declared explicit owned clear or a charged reversal/uncompute, not free disposal. If a permutation has an expensive tape realization, charge that actual realization at every use. The numerical κ cannot be inferred from this count without its physical caller.

A simple maximum-norm bound is

    ||g(W)||_infinity <= (R+1) [sqrt(2)(n+a+R+1)]^R.

Indeed ||D_j||_infinity=1, so ||W||_infinity<=n. The product defining binom(W-a,h) has norm at most (n+a+R+1)^h, even after discarding the favorable h! denominator. Multiply by |i-1|^h=2^(h/2) and sum. The source operator has ||A_n||_infinity=2^(n/2), so the residual norm is at most that quantity plus the displayed bulk bound. These are valid intermediate/recovery bounds, not merely eigenvalue statements.

### Corollary B4 An actual lower-precision bulk computation

Let x be a Gaussian-integer input. Congruence of a fractional output means its class in Q(i)/π^p Z[i], with the declared numerator grid retained. Define the explicit integral numerator operators

    G_B=π^R g(W),
    G_T=π^n A_n-π^(n-R)G_B.

Both have Gaussian-integer entries by B2 and n>=R. For any p>=1, the response A_n x modulo π^p is determined by

    G_B x modulo π^(p+R),
    G_T x modulo π^(p+n).

**Proof.** The exact identity is π^n A_n x=π^(n-R)G_B x+G_T x. An error divisible by π^(p+R) in the bulk numerator acquires n-R further valuation units, hence changes this identity only by π^(p+n). Divide the resulting common numerator by π^n to obtain the response modulo π^p. QED.

Thus the emitted ordinary bulk uses n-R fewer Gaussian precision units than computing both integral numerators at p+n. This is a genuine precision saving for the actual normalized source family. The exceptional term still uses the full stated precision. G_T is an explicitly defined integer matrix, so it has a literal finite implementation; claiming that implementation cheap would require its complete actual word. Its small rank bound alone is not that implementation. Exact ordinary output decoding still needs the common height/grid rule in E2.

## 5 The exact exceptional-rank tradeoff

Let J be binomial(n,1/2). Then t=2^n Pr[J outside [a,a+R]]. If the interval contains n/2 and

    τ=min(n/2-a, a+R-n/2)>=0,

then

    t <= min(2^n, 2^(n+1) exp(-2τ^2/n)).

For completeness, if J is a sum of n independent fair bits, E exp(λ(J-n/2))=cosh(λ/2)^n<=exp(nλ^2/8). The inequality for cosh follows by integrating tanh u<=u. Markov's inequality and λ=4τ/n give Pr[J-n/2>=τ]<=exp(-2τ^2/n); use the same estimate on the other side. At τ=0 the trivial bound suffices. The integer interval's complement is contained in the union of the indicated tails.

Thus an interval of radius proportional to sqrt(n log n) has polynomially small exceptional fraction, while its bulk denominator debt is only O(sqrt(n log n)), rather than n. This is a positive joint degree/precision/rank statement for the actual Gaussian tensor family.

The correction formula above, however, is dense in general. A literal implementation reads every input coordinate for each exceptional Walsh measurement and scatters to every output coordinate: O(t 2^n) scalar incidences, plus coefficient synthesis, normalization and cleanup. The ordinary bulk also pays the nR factor. This package does NOT call a small exceptional fraction a cheap physical correction. Classical fast Walsh processing remains a competing exact implementation and must be compared honestly. Any useful gain must come from an actual structured consumer or shared source bank that makes the correction and caller bill favorable.

## 6 Direct next application

The preprint's construction now has an exact four-phase analogue for the source's Gaussian tensor, with no guessed matrix and no assumed oracle. The candidate use is a provider that consumes only specified summaries of A_n x, or a batch whose exceptional Walsh measurements are already available and can be shared. For that named consumer one must explicitly factor its required residual, synthesize the ordinary delivery over its real scalar ring, include all input versions and dirty outputs, and compare its full signed invoice. The sufficient compiler in [constructive-transport.md](constructive-transport.md) and the net-weight/exact-decoding rules in [endpoint-lowering.md](endpoint-lowering.md) specify those operations.

**Open next question.** Is there a literal current provider window whose required exceptional measurements are already represented by retained helper data, so that B1's correction has a new paid construction cheaper than the old whole transform? The first step is an exact equality between that window's actual response and the matrices above; rank similarity is insufficient. No such favorable helper realization is assumed by B1-B3.

## Attribution and evidence

The source inspected is Mathproof.External.IntegerMultBounds20261008.Matrix.GaussianTensorExecution, together with its CommunityPrecisionProfile companion. Their comments explicitly limit them to finite arithmetic/precision and exclude tape/runtime. The linked-tree records are precedents, not fresh kernel certificates. The new note supplies its own matrix, spectral, denominator, synthesis and tail proofs.

Credit OpenAI's pinned October 25, 2026 preprint for the concentrated swap-spectrum interpolation architecture; the Gaussian four-phase specialization and explicit numerator word above are the present application. Walsh diagonalization, Newton interpolation, elementary-symmetric recurrences and binomial concentration are classical. No worldwide novelty is claimed for these component facts. New text is Apache-2.0 with substantial OpenAI Codex assistance.

