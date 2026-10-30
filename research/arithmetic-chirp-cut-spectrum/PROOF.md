# Exact cut spectrum of an arithmetic chirp

This scoped written proof was produced by Nick Petalas. Apache-2.0.
The finite verifier corroborates identities below; it does not establish their
unbounded quantifiers or provide independent human or proof-kernel review.

## 1. The endpoint and its declared cut

Let N=L H with positive integers L,H, and let a,b be integers. Define

    U |x> = exp(2 pi i (a x^2+b x)/N) |x>,   0 <= x < N.

Use the tensor identification x=u+L v, where 0<=u<L and 0<=v<H.
This specifies the physical order. It is not an optimization over reorderings,
encodings, side information, extra input promises or alternate endpoints.

A transfer representation with bond D at this cut expresses U as a sum of
at most D products A_j tensor B_j. Position-dependent and width-dependent
tables are allowed. Thus any lower bound here also applies to the fixed-table
physical transfer contract of zxv's PR #5441. We do not assume that a small
bond prices a physical native implementation, tape movement or dirty returns.

Put

    g = gcd(2a,H),   Q = H/g,   L = q Q+t,   0 <= t < Q.

The convention gcd(0,H)=H includes constant and linear phases.

## 2. Complete spectrum

**Theorem.** The nonzero squared operator-Schmidt coefficients of U at this
cut, before normalization, are

    H(q+1), repeated t times;
    Hq,     repeated Q-t times, omitting zero values.

In particular its cut rank is exactly min(L,Q). Its squared Hilbert-Schmidt
norm is N. After division by sqrt(N), the squared coefficients are the
positive numbers (q+1)/L and q/L with the same multiplicities. All integers
a,b, all factorizations N=L H, and either sign of a are covered.

**Proof.** In the orthonormal diagonal matrix bases |u><u| and |v><v|, the
coefficient matrix of U is the L-by-H matrix

    C[u,v] = zeta_N^(a(u+Lv)^2+b(u+Lv)).

All other entries of the operator realignment are zero. Therefore C and
that realignment have the same nonzero singular values. Expand the square:

    C[u,v] = zeta_N^(a u^2+b u)
             * omega^(u v)
             * zeta_N^(a L^2 v^2+b L v),
    omega = exp(2 pi i 2a/H).

The exterior factors are diagonal unitaries, so they preserve singular
values. The middle matrix K[u,v]=omega^(u v) has omega of exact order Q.
Since Q divides H, character orthogonality gives

    (K K*)[u,w] = H if u=w mod Q, and 0 otherwise.

Partition the L rows by their residues r modulo Q. Each nonempty class
gives H times an all-ones block of size c_r, with one eigenvalue H c_r.
There are t classes of size q+1 and Q-t classes of size q, omitting empty
classes. This proves every stated multiplicity and the rank formula.
The sum of eigenvalues is H sum c_r=H L=N. The coefficient b occurs only
in the exterior unitary factors and cannot affect the spectrum. End proof.

The proof is also an explicit orthogonal factorization. Write

    K[u,v] = sum_(0<=r<Q) 1_(u=r mod Q) omega^(r v).

The nonzero left vectors have squared norms c_r and disjoint supports.
The right vectors have squared norms H and are mutually orthogonal.
Restoring the two exterior phases supplies an attaining rank decomposition.
This uses classical character orthogonality, not a new Fourier theorem.

## 3. Sharp error at one cut

Let lambda_1>=...>=lambda_R>0 be the normalized squared coefficients in
Section 2, R=min(L,Q). For 0<=D<=R the least squared relative
Hilbert-Schmidt error among operators with cut rank at most D is

    E_D^2 = sum_(j>D) lambda_j.

This is the classical best low-rank approximation theorem applied to the
realignment, which preserves Hilbert-Schmidt norm. The explicit orthogonal
factorization above attains the bound by retaining the D largest classes.
It is a statement about one cut. It does not assert simultaneous optimal
approximation at every cut or optimal operator-norm approximation.

For completeness, the lower bound follows by projecting onto the column
space of any proposed rank-D approximant. That projection has rank at most
D and can retain at most the sum of the D largest eigenvalues of C C*.
The complementary squared norm is the displayed tail. Truncation attains
it, so no unproved numerical SVD premise enters the argument.

If an N-by-N approximant V instead satisfies ||U-V||_2<=epsilon, then

    ||U-V||_F^2/N <= epsilon^2.

Consequently its cut rank D necessarily satisfies E_D^2<=epsilon^2.
This necessary operator-norm bound need not be sufficient. No positivity,
diagonality or unitarity is required of V.

## 4. Binary order has a flat spectrum

Let N=2^n, n>=1. Define the finite integer

    nu = v_2(gcd(2a,2^n)),    1 <= nu <= n.

At the cut after the k least significant bits, including k=0,n,

    Q_k = 2^max(n-k-nu,0),
    R_k = 2^min(k,max(n-k-nu,0)).

Both L=2^k and Q_k are powers of two. If L<=Q_k every nonempty residue
class has size one. If L>=Q_k, Q_k divides L and every class has size
L/Q_k. Thus all R_k normalized squared coefficients equal 1/R_k.

The exact minimum peak bond, among arbitrary position-dependent matrix
product operators in this bit order, is

    R_peak = 2^floor((n-nu)/2).

Indeed the maximum of min(k,max(n-nu-k,0)) is floor((n-nu)/2).
Each cut rank is necessary. It is also sufficient simultaneously for an
exact representation: successive exact singular decompositions of the
diagonal phase vector give a tensor train with these unfolding ranks.
Copying each physical bit to equal input/output indices turns that train
into an MPO with the same bonds. This is the standard exact tensor-train
factorization argument, and is not a uniform fixed-table construction.

At any one cut, the sharp squared relative Hilbert-Schmidt error is

    E_D^2 = max(0,1-D/R_k).

For every operator-norm error epsilon<1, an MPO therefore needs

    D >= ceil((1-epsilon^2) R_k)

at that cut. The same necessary bound with R_peak applies to its peak bond.
For odd a, nu=1, so R_peak=2^floor((n-1)/2). Width 65 requires exact
peak bond 2^32. This example is encoded arithmetic, not a materialized
2^65-entry computation. Fixed error below one still forces exponential
growth. Reversing the complete bit order retains the same cuts with their
sides exchanged. Arbitrary permutations of bits are outside this result.

## 5. Scope and relevance

The new step is the arithmetic chirp's exact spectrum, including nonflat
mixed-radix cuts and the valuation-sensitive binary consequence. PR #5441
supplies the repository's transfer contract and earlier robust half-swap
and binary dot-product examples. Its executables and results are not
replayed or independently audited here. Crosswhite and Bacon supply the
classical automata/MPO correspondence. Character orthogonality, exact
tensor factorization and best low-rank approximation are background facts.
Global literature priority for chirp Schmidt decompositions is unclaimed.

This result rejects a bounded-bond representation of this particular
arithmetic phase in the declared order. It does not reject a short circuit
for the same phase, a different data order, a changed representation or a
consumer that needs fewer entries. Jon Tyson's operator-Schmidt analysis
of the QFT is related arithmetic background, and Chen and Lindsey's
compressible reindexed QFT illustrates why endpoint and order matter.

No selected native primitive or actual all-size caller has been identified
with this full phase endpoint here. That binding, allowed reorderings,
the complete paid/productive invoice, coefficient preparation, storage,
precision, native realization and dirty restoration remain open. No
selected framework assumption, supplier admission or new kappa follows.

## References

- zxv, [PR #5441](https://github.com/CrocSwap/integer-mult-bounds/pull/5441),
  `11fedb46fa199283f78282187c10aea432d8b0bb`, retained on the package base.
  Its README and proof are pinned as provenance in SOURCES.json.
- Gregory M. Crosswhite and Dave Bacon,
  [Finite automata for caching in matrix product algorithms](https://arxiv.org/abs/0708.1221).
- Jon Tyson, [Operator-Schmidt decomposition of the quantum Fourier transform
  on C^N1 tensor C^N2](https://arxiv.org/abs/quant-ph/0210100).
- Jielun Chen and Michael Lindsey, [Direct interpolative construction of the
  discrete Fourier transform as a matrix product operator](https://arxiv.org/abs/2404.03182).

The retained native recipe, physical transfer, compiler and phase lineage
credited in PR #5441 remains predecessor work. No predecessor credit is changed.
