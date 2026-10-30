# Clifford Gram row-sum sharpness: independent scoped finding

**Status: submitted as [upstream PR #5714](https://github.com/CrocSwap/integer-mult-bounds/pull/5714) for independent review; not merged or selected-frontier approved.** This standalone note and verifier complement PR #5694. They do not claim to improve κ or certify a complete multiplication theorem.

- Repository: <https://github.com/CrocSwap/integer-mult-bounds>
- Pinned canonical `main` at the final checkpoint: `df0137efd35e11b4445734bf612bdd4c7ebc330c` (2026-10-26); priority revision **7**.
- The authoritative selected record at that checkpoint: `certificates/selected-result.json`, κ = `62009/20000000 = 0.00310045`. No selected result was changed.
- Direct subject: [kumagi PR #5694](https://github.com/CrocSwap/integer-mult-bounds/pull/5694), exact reviewed head `aa01976e51aa1731433a9e65443303a7c2f869ca`, `research/clifford-residual-count-bound/PROOF.md` §§1–4.
- Direct predecessor: [Ali Romman PR #5526](https://github.com/CrocSwap/integer-mult-bounds/pull/5526), head `45f7de73b168721cdf7ec8c1769b1b594493716a`, retained `research/clifford-pointwise-faithfulness/PROOF.md`; its independent audit is `research/clifford-pointwise-audit/AUDIT.md`. Classical symplectic residual forms and Pauli trace character orthogonality are prior art.
- Guide files read first from canonical main: `AGENTS.md`, `autoresearch.md`, `CONTRIBUTING.md`; handoffs #1166 and open PR overlap inspected. This was selected as an **explicit independent audit of a live handoff**, not a random new card. No task picker selection is claimed. Before attempted submission, canonical main, priorities, catalogue, selected record, PR head and PR comments were rechecked and unchanged. Overlap search was **targeted, not a complete cached/full-pagination scan**.

## The new result: uniform sharpness of the absolute row-sum method

Let \(N=2n\), \(V=\mathbb F_2^N\) with nondegenerate alternating form \(\omega(x,y)=x^TJy\), and

\[
c_{N,k}=\#\{S\in\mathrm{Sp}(V):\operatorname{rank}(S-I)=k\}.
\]

The fixed-nonsingular-residual-form argument of PR #5694 gives the upper estimate

\[
c_{N,k}\leq 2^{Nk-k(k-1)/2}.
\]

**Complementary lower estimate.** For \(1\le k\le N/2\),

\[
\boxed{\prod_{i=0}^{k-1}(2^{N-i}-2^i)\ \le\ c_{N,k}\ \le\ 2^{Nk-k(k-1)/2}.} \tag{A}
\]

To prove this, fix an invertible \(k\times k\) matrix \(B\) over \(\mathbb F_2\). By the source's residual reconstruction, ordered injective column matrices \(E\) obeying \(E^TJE=B+B^T\) correspond, after counting bases, to symplectic maps with displacement rank \(k\). After \(i\) independent columns \(e_0,\ldots,e_{i-1}\) have been chosen, the conditions

\[
\omega(e_j,e_i)=B_{j,i}+B_{i,j}\quad (0\le j<i)
\]

are \(i\) independent affine linear constraints. They leave exactly \(2^{N-i}\) solutions. There are at most \(2^i\) vectors in the preceding span, so at least \(2^{N-i}-2^i\) choices preserve injectivity. This is positive under \(N\ge2k\). Induction gives the lower product **for each fixed invertible \(B\)**. Since every admissible pair \((E,B)\) gives an \(S\) and every such \(S\) appears with precisely \(|\mathrm{GL}(k,2)|\) ordered bases, multiplying by \(|\mathrm{GL}(k,2)|\) and dividing cancels. No independence assumption between \(E\) and \(B\) is made.

Consequently, for fixed \(k\), as even \(N\to\infty\),

\[
\prod_{i=0}^{k-1}(1-2^{2i-N})\leq
\frac{c_{N,k}}{2^{Nk-k(k-1)/2}}\leq1,
\]

so the ratio tends to 1.

The PR #5526/5694 trace-lift argument gives the **exact** full-projective-Clifford Gram absolute row sum at \(f=2N+4=4n+4\):

\[
R_N=\sum_{k=1}^{N}2^kc_{N,k}2^{-k(N+2)}
=\sum_{k=1}^{N}c_{N,k}2^{-k(N+1)}.
\]

Each summand is nonnegative and bounded by \(2^{-k(k+1)/2}\). The latter is summable independently of \(N\), so dominated convergence for series applies to (A) and yields

\[
\boxed{\lim_{n\to\infty} R_{2n}
=\sum_{k\ge1}2^{-k(k+1)/2}
=0.64163256065515386629384\ldots.} \tag{B}
\]

Thus the **best possible uniform Gram lower constant obtainable by the absolute off-diagonal row-sum method alone** at the unchanged starting width is

\[
1-\sum_{k\ge1}2^{-k(k+1)/2}
=0.35836743934484613370615\ldots.
\]

The PR's certified rational \(\alpha=1491359/4161536=0.3583674393300935\ldots\) is within \(1.48\times10^{-11}\) of this limit. A rigorous gap certificate follows from the source's geometric upper tail \(T^+ =2670177/4161536\) and the finite sum \(T_8=\sum_{k=1}^{8}2^{-k(k+1)/2}\):

\[
0<(1-T_\infty)-\alpha <T^+-T_8
=\frac{129}{8727373545472}<1.48\times10^{-11}.
\]

**Interpretation:** tighter universal symplectic rank-count bounds cannot materially improve *this* uniform absolute-row-sum certificate. This is **not** a claim that the true Gram minimum eigenvalue reaches that limit. Phase-aware spectral arguments could give substantially better lower constants, and applying any improvement to a physical caller would require its own alphabet/state/cost audit.

## Independent review of PR #5694's requested implications

The following proof steps were checked algebraically, with no substantive gap identified within these explicit premises:

1. For \(W=\operatorname{im}(S-I)\), symplecticity gives \(\ker(S-I)=W^\perp\). The residual equation \(B((S-I)x,w)=\omega(x,w)\) is well defined. With \((S-I)x=Ea\), it is \(B^Ta=E^TJx\), requiring reconstruction by \(B^{-T}\), not \(B^{-1}\).
2. For fixed invertible \(B\), the successive pairing functionals \(\omega(e_j,-)\) are independent by nondegeneracy of \(\omega\) and independence of the \(e_j\), so the author's \(2^{N-i}\) upper count holds. Exactly \(|\mathrm{GL}(k,2)|\) ordered bases occur per \(S\), and the form is unique for each choice of basis. This justifies division by \(|\mathrm{GL}(k,2)|\).
3. Pauli signs on \(L=\ker(S-I)\) are characters; the perfect pairing makes \(V\to L^*\) onto with kernel \(L^\perp\) of size \(2^k\). This gives exactly \(2^k\) nonzero-trace projective lifts and normalized trace modulus \(2^{-k/2}\). The Gram and four-phase Parseval conclusions retain the PR's specified projective and fixed-coefficient hypotheses.

This check is **author-prepared**, not an accepted review, a formal-kernel proof, a complete external source audit, or an independent human mathematical peer review.

## Independently reproducible finite controls

Run from this directory with Python 3.10+ (standard library only); both modes passed with identical scientific receipts on Python 3.13.5 / Linux:

```sh
python3 -B verify.py
python3 -O -B verify.py
```

`verify.py` uses a method different from PR #5694: it constructs **every ordered symplectic basis** by choosing a hyperbolic pair within the symplectic complement of the previous pairs, then calculates the binary rank of \(S-I\). It imports neither the PR's Clifford gate enumerator nor its residual-form enumerator. Every basis represents exactly one symplectic matrix. It also independently scans all 65,536 literal \(4\times4\) binary matrices for the \(n=2\) oracle, checks the symplectic group orders and exact rank-one counts, the upper/lower count bounds at supported sizes, the rational tail certificate and a deliberately too-small tail-ratio negative control.

| n | \(|\mathrm{Sp}(2n,2)|\) | Rank histogram for \(k=0,...,2n\) | Exact \(R_{2n}\) at \(f=4n+4\) |
|---:|---:|---|---:|
| 1 | 6 | `[1,3,2]` | `13/32` |
| 2 | 720 | `[1,15,100,300,304]` | `37739/65536` |
| 3 | 1,451,520 | `[1,63,1932,28980,202944,608832,608768]` | `5366132533/8589934592` |

The original research has complete finite corroboration through \(n=2\). The \(n=3\) census is an additional complete exact control. First run on CPython **3.13.5 / Linux x86-64**, approximately six seconds for frame enumeration; this is not a hosted CI or signed source-bound replay. The written argument, not enumeration, supplies the all-\(n\) limit.

## Open next questions / remaining obligations

1. **Independent mathematical scrutiny:** check every line of the new fixed-\(B\) lower product and its correspondence-to-\(S\) under the source's finite symplectic conventions. A formal proof kernel would require a separately scoped effort.
2. **Spectral strengthening:** determine whether the actual full-group Gram minimal eigenvalue exceeds the diagonal-dominance bound uniformly. The present sharpness applies only to absolute row sums and does not exclude spectral cancellation.
3. **Application:** any claim for a QQ16 physical caller or the selected multiplication exponent needs its explicit alphabet, full retained dirty state, complete paid budget and remaining framework assumptions. Neither this work nor PR #5694 discharges those obligations.

Predecessor credit belongs to kumagi / PR #5694 for the nonsingular-form upper bound and certificate, Ali Romman / PR #5526 for the trace-lift and Gram/four-width framework, the `clifford-pointwise-audit` authors for earlier independent audit coverage, and the classical symplectic/Clifford literature. The lower product, limit observation and additional frame enumeration are complementary to those sources. **Substantial OpenAI assistance** was used for this derivation, computation and writing; no originality priority beyond the scoped repository comparison is claimed. The source project is Apache-2.0; this note and verifier are offered under Apache-2.0.

### Publication checkpoint

Publication base: canonical `CrocSwap/integer-mult-bounds` main `df0137efd35e11b4445734bf612bdd4c7ebc330c`, priority revision 7, selected conditional κ `62009/20000000`. On 2026-10-26 the fork `GosuBoy/integer-mult-bounds` had write access; the open PR #5694 was still at head `aa01976e51aa1731433a9e65443303a7c2f869ca`. No predecessor files, frozen sources, selected records, or historical certificates were modified. Only this package is proposed.