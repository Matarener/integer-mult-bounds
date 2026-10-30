# Independent selected-row and proof review

The code `review.py` imports no author scanner, arithmetic representation,
constructor, prior verifier or pricing engine. It authenticates the exact
published WORD, then propagates only the named rows backwards using ordinary
`fractions.Fraction`. It does not repeat the full all-cut census.

Normal and optimized Python 3.12 runs agree byte for byte and reproduce:

- Prefix cut 24096, role 93: `{86:-65536,93:-65536}`, l1 = 131072.
- Suffix cut 24297, public output 205: every one of the submitted 111 terms,
  l1 = 135415/4.
- All eight nonzero injected-owned COPY responses. In particular the error
  in owned role 735 immediately before COPY event 13491 reaches public output
  112 with coefficient 1. Assignment-COPY would discard that error.
- Endpoint norm exponents 14/18; actual native-interior prefix/suffix exponents
  20/27. Extremal native cuts are independently recorded in RESULT.json.
- Service K = 25312 with `ceil(log2(K LambdaS)) = 30`, and literal butterfly
  K(f) = 21688 + 5894 f.
- Maximum absolute scalar coefficient 65537/2 and dyadic denominator 65536.

## Review of exhaustive scanner logic

I read the full author `check.py`. The implementation represents dyadic rows
as one integer numerator dictionary and a shared power-of-two denominator.
The OR of absolute numerators computes the common trailing-zero factor;
the exact dyadic rescaling and cancellation arithmetic are correct. No
floating values occur in the scientific scan.

In the forward scan exactly one logical row changes at a scalar/ownership
event. Comparing that row with the prior maximum covers every cut. MOVE is
logical identity with a changed physical chart. The reverse scan stores
columns of the public-output response matrix. Pulling an ADD d += c s changes
only source column s by c times destination column d. Updating the exact
row sums over the union of changed column supports therefore maintains the
actual matrix infinity norm. INIT/CLEAR zero only their owned columns.
COPY retains its owned column, consistently with its declared actual ADD
implementation. Endpoint checks independently agree in the two directions.

This is algorithm/proof review plus independent named witnesses. Exhaustive
maximality of the constants relies on the author's all-cut run and this
reviewed recurrence; it was not independently recensused here.

## Spectator-independent coordinate bound

Use the maximum absolute real/imaginary component over roles and addresses.
Each normalized C gate has induced norm at most 2 in this norm. Native
P/D/X/phase monomials are coordinate permutations and factors ±1/±i, with
norm 1. The exact canonical frame and its inverse have norm <=N^dim(F),
N=2^f. Tensoring is realized by f per-column copies of the literal gates;
no Euclidean-to-coordinate dimension factor or spectator-volume factor is
introduced.

At completed cuts `G = Phi_current A Phi_initial^-1`, so the actual entrance
maximum 5 and current maximum 9 give `||G|| <= LambdaP N^14`. The suffix
factorization gives `||S|| <= LambdaS N^18`. A native recipe has one rank-r
Gaussian factor with monomial ends. Applying the actual per-MOVE dimensions
to its partial prefixes/suffixes gives the recorded N^20/N^27 bounds. These
are conservative coordinate bounds; they do not assert attained growth.

For completed services, suppose each returned scalar/native job has absolute
coordinate error <=delta, including exact dyadic arithmetic followed by a
single rounding. Then total final public error is at most
`25312 LambdaS N^18 delta`. With a literal butterfly implementation the bound
is `(21688+5894 f) LambdaS N^27 delta`. Input/output rounding are charged as
two additional layers. The completed-service bound assumes the retained
recursive-child output-error ABI. The explicit butterflies give a different
precision witness whose runtime is not charged by the recursive invoice.

COPY is the chosen implementation `owned += source` immediately after exact
INIT-zero. It agrees with the original clean trace, while arbitrary injected
owned residuals remain in the perturbed computation. Erasure is confined to
owned storage. Replacing this derivative by assignment would be invalid.

The +35-bit arithmetic allowance is a conservative local guard for exact
dyadic products, denominator alignment and an ADD before final rounding.
**It is not by itself a global integer-range/overflow proof.** LambdaP bounds
exact prefixes, while LambdaS bounds final public error; neither alone bounds
all perturbed intermediate states. A fixed-width implementation additionally
needs an all-interval growth bound, or explicitly wider/unbounded integer
parts. A crude finite product of scalar `(1+|c|)` factors can provide such a
separate bound, but that was not computed in this independent report.

Under these stated interfaces the flat norm/error implication is sound. It
does not close native recursive internal precision, the full 265-axis caller,
the uniform compiler, global physical stock/tape bounds, the five framework
premises or scientific adoption. This is independent AI-assisted review,
not independent human or proof-kernel acceptance.

Prepared for thu-nmrc with OpenAI Codex assistance. Apache-2.0. Cinna Davis,
Ali Romman, Cao Yifan, zxv, native/compiler contributors and retained P104
source authors keep all upstream construction and native-chart credit.
