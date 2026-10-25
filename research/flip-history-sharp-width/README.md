# Sharp width for the bit-flip history example

For the bit-flip family below, the exact standalone paid-return threshold is
width two. Width one permits zero paid returns. Every width at least two needs
at least one paid return per independent target owner. This answers the small-width
question for a stated family in PR5446. The complete kappa calculation is unchanged.

## Theorem

Let K have characteristic different from two. Put X=[[0,1],[1,0]] and
J=X tensor-powered f times. Ordinary actions form R=span_K{I,J}, together with
arbitrary scalar row combinations, copies and clears. Start with ordinary
combinations of N independent input fields and zero scratch. Include independent
dirty inputs among those N coordinates. Target q distinct coordinates v_i by
H_i=h_i tensor-powered f times, where h_i=a_i I+b_i X and

```
a_i b_i (a_i^2-b_i^2) != 0.
```

Each paid call returns one actual new row at the same capacity. Its input can
use earlier responses. The paid map need not commute with R. Any finite number
of ordinary instructions and arbitrary coefficients at this width are allowed.
Then m>=q for every f>=2. If each H_i is an available paid primitive, q calls
attain the bound. At f=1 each target lies in R, so its relaxed paid count is zero.
This is a call-count optimum only with that explicit paid-primitive hypothesis.

## Proof

Set E=(I+J)/2. Then EJ=E, so ER=K E. Project the full history on the left by E.
Every actual paid return adds at most one dimension to this projected history,
including when its input uses earlier paid returns. Conceptually retain all paid
rows after overwrite or clear.

In the X eigenbasis, let lambda_plus=a+b and lambda_minus=a-b. On a tensor
with k minus signs, H has eigenvalue lambda_plus^(f-k) lambda_minus^k.
The k=0 and k=2 vectors both belong to the +1 eigenspace of J. Their eigenvalue
difference is

```
lambda_plus^f - lambda_plus^(f-2) lambda_minus^2
    = 4 a b lambda_plus^(f-2) != 0.
```

Thus EH is not a scalar multiple of E for every f>=2. Initially the projected
history lies in the direct sum of K E on each independent input coordinate.
Each of the q targets adds one independent direction modulo that initial space.
Distinct owner coordinates make these directions independent even if their h_i
are equal. After m returns the quotient dimension is at most m, hence m>=q.
This proof works separately at every width. It needs no common finite word or
uniform coefficient rule across widths. For f=1, h_i=a_i I+b_i X is ordinary.
These observations prove both the threshold and the stated attaining count.

For the source example a=(1+i)/2 and b=(1-i)/2, h squared is X and h is
invertible. The theorem therefore supplies the sharp threshold two for the
square-root-of-X example that defeats a width-one charge in the predecessor.
The predecessor's general guard 2p-1 gives three when p=2. Its tensor-class
independence theorem is unchanged: at width two the full ordinary and target
spans can intersect, while the +1 character already forces the paid count.
For example (I-J)H is an ordinary scalar multiple of I-J at width two. Requiring
complete coset-span separation would miss this sharper call-count argument.

## Evidence and reproduction

```sh
python3.12 -B scripts/research_package.py --package research/flip-history-sharp-width
```

The standard-library verifier uses exact pairs of rational numbers for Q(i).
It builds literal Kronecker matrices, projects their complete rows with E, and
uses rational Gaussian elimination. It also checks both eigenvectors directly
against each matrix. Separate scalar calculations test the displayed identity
through width 64. Owner checks use full block rows for one through four input
coordinates. Controls retain free monomial targets, duplicate owners, an already
cached target and the zero-charge width-one case. The registered normal and
optimized modes use explicit exceptions. The written proof supplies the
all-field and all-width statement; these finite checks corroborate it.

## Scope, overlap and sources

This is a sharp special-family result for the smaller-width handoff in
[PR #5446](https://github.com/CrocSwap/integer-mult-bounds/pull/5446). Read its
[pinned pointwise theorem and width-one example](https://github.com/Clear1nsight/integer-mult-bounds/blob/0d0bcf3fa261c9591e7e60ed5926c6e04d360f9e/docs/research/standalone-history-scalar-ceiling/proofs/pointwise-lemma-v1.md).
That source gives the general finite ordinary-group history method. This proof
uses a one-dimensional character to cover a width where full span separation
fails. It does not replace the source's general group theorem.

The ordinary alphabet and geometry are fixed. Cached nonordinary observations,
multiple outputs per paid call, dependent target coordinates and characteristic
two fall outside this theorem. It does not assert an extra charge at a physical
parent boundary. It supplies no full native caller, physical cost, precision,
stock, compiler admission or new kappa. The physical-history result in
[PR #5447](https://github.com/CrocSwap/integer-mult-bounds/pull/5447) has a different
source and task. Exact source objects and base context are in SOURCES.json.
The overlap pass searched the full tracked note inventory and recent live PR
and Discussion records; unposted work and arbitrary historical diffs remain
outside coverage.

## Open next questions

For a specified larger finite ordinary group, find one small character component
that detects all target owners at a practical width. First compute its projected
ordinary and target spans. The missing component and physical source binding
are the blockers. A charge at a cached caller boundary requires its actual
initial observation module and cannot use the standalone hypothesis silently.

## Credit

Chris R / Clear1nsight and the retained PR5425/PR5446 authors supply the history
method, scalar-width distinction and concrete example. Classical involution
characters and tensor eigenvectors supply this proof's algebra. No predecessor
code is imported. Ali Romman with substantial OpenAI Codex assistance; Apache-2.0.
No independent human review or proof-kernel acceptance is claimed.
