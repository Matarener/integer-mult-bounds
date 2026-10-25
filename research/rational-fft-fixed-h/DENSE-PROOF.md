# Conditioned Toeplitz programs on fixed Hadamard stages

I extend the completed FFT connection to the actual stored full Toeplitz
program and its stored inverse at PR4205 head
78c72e563173f3822fcb4efed9ceeccf05630258. I retain its source and proof
bytes unchanged in [full_source](vendor/full_source/PROVENANCE.json).
I use Vlado Vojdanovski's existing zero-safe words and routing algorithm.
I add the nonunitary amplification argument and bind its parameters to
the admitted root, coefficient preparation and executed stages.

## Generic domain

Take a field of $N=2^m$ coordinates and an ordered program of $L$
matching layers. In each layer, allow disjoint one-wire nonzero scalars,
upper or lower shears, invertible diagonal pairs, swaps and the rational
unitary butterflies or stored adjoints from [PROOF.md](PROOF.md).
The caller supplies exact rational bounds $\Pi,E_0,R\ge1$ such that:

- Every original logical prefix and its inverse has norm at most $\Pi$.
- The exact stored endpoint $U$ has norm at most $E_0$.
- The incoming vector satisfies $\|x\|_2\le R$ and has complex components
  on the $2^{-F_0}$ grid, for integer $F_0\ge0$.

I use Euclidean vector norms and induced operator norms. These premises
concern linear maps with the stored coefficients and unrounded data.
The rounded execution itself is nonlinear.

For $N\ge2$, I retain
\[
J=L(16m+5),\qquad M=L(8m+3),\qquad h=L(8m+2),
\]
for the primitive, diagonal and whole-field Hadamard stage counts.
For $N=1$, I execute each scalar or idle layer as one diagonal:
$J=M=L$ and $h=0$. I make no bit-zero Hadamard call.
Put
\[
\Gamma=2^{\lceil\log_2(\Pi^2)\rceil},\qquad
C=2^{14}\Gamma\Pi.
\tag{1}
\]
At a logical layer boundary, $A_j=P_jP_{j-1}^{-1}$ gives
$\|A_j\|,\|A_j^{-1}\|\le\Pi^2\le\Gamma$. Since the layer is a
direct sum, each scalar and its reciprocal has modulus at most $\Gamma$,
and each shear parameter has modulus at most $\Gamma$.

For target integer $t\ge1$ and $L>0$, I choose
\[
F=\max\left\{F_0,\
t+\left\lceil\log_2(16E_0MC^2(R+1))\right\rceil,\
t+\left\lceil\log_2(16E_0CJN)\right\rceil\right\}.
\tag{2}
\]
I prepare the exact reference words, replace each $H$ by $H_0=H/2$,
double its following diagonal, then round the diagonal components to
the $F$ grid. I round the data after each emitted stage, including
routing and idle words. I retain distinct adjacent diagonal stages.
I prove the following error against the stored logical endpoint:
\[
\|\widehat y-Ux\|_2
\le 4E_0MC^2\,2^{-F}R+4E_0CJN\,2^{-F}
<\tfrac12\,2^{-t}.
\tag{3}
\]
For $L=0$, I return the input, choose $F=\max(F_0,1)$, and incur zero
error. I give the connection to the exact Toeplitz root below.

## Zero-safe shear and scalar words

For an upper shear parameter $v$, set $c=2\Gamma+1$ and $z=v+c$.
The reverse triangle inequality gives
\[
\Gamma+1\le |z|\le3\Gamma+1,
\]
so the retained construction can call its nonzero helper twice, even
at $v=0$. In execution order it uses the seven diagonals
\[
(-5/(4c),1),\quad(-3,1),\quad(2,1),\quad
(c/(8z),-1/6),\quad(-3,1),\quad(2,1),\quad(-z/10,-1/6)
\tag{4}
\]
with a raw $H$ between neighbors. The two helper endpoints compose
as $U(z)U(-c)=U(v)$. Reversing the symmetric factors gives the
ordinary transpose $U(v)^T$, hence the lower shear. I do not conjugate
the complex parameter.

I bound contiguous segments by products of factor norms, replacing
factors smaller than one by one. In (4), the middle diagonal has
norm at most $1/4$ and inverse norm at most 12. The last diagonal
has norm at most $(3\Gamma+1)/10\le\Gamma$, and inverse norm at most
six. The first inverse diagonal has norm at most $3\Gamma$.
Together with $\|H\|=\sqrt2$ and $\|H^{-1}\|=1/\sqrt2$, I obtain
raw segment bounds $288\Gamma$ and $216\Gamma$ for the direct and
inverse maps. The same bounds hold after word reversal, because
ordinary transposition preserves the spectral norm.

After the $H_0$ compensation, a contiguous segment differs from its
raw counterpart by a scalar in $\{1/2,1,2\}$. Thus $1024\Gamma$
bounds the native shear segments and their inverses. For a diagonal
pair, the source appends three complete two-H identity words;
the raw segment and inverse bounds are $8\Gamma$, and the native
bounds are $16\Gamma$. Swaps and idle pairs have smaller bounds.
For rational butterflies and their stored adjoints, I use the 4096
bound from PROOF.md. Therefore
\[
4096\Gamma
\tag{5}
\]
bounds each native central word segment and its inverse.

The compensated diagonal entries have modulus at most $6\Gamma$
and reciprocal modulus at most $200\Gamma$. I complete each mixed
layer's unused wires in pairs, using its actual singleton scalars
and identity values on idle wires. I preserve the oriented order
of each existing two-wire gate. All-one diagonal padding would
multiply the inactive pair by eight, so I use complete identity words.

The source routes input $i$ to output $p[i]$. Its $2m-1$ switch
layers have unitary completed endpoints and native prefix/inverse
norms at most $\sqrt2$, as proved in PROOF.md. I use the reversed
switch schedule for the return route. Within a logical layer,
the central word and the two routes contribute less than
$2^{14}\Gamma$ to a partial prefix or inverse prefix. The completed
earlier logical program contributes at most $\Pi$. Equation (1)
therefore bounds exact compiled prefixes and their inverses by $C$.
I do not multiply the fragment allowance once per logical layer.

## Nonunitary endpoint and rounding

Let $P_j$ be the exact compiled prefix. An exact suffix is
$UP_j^{-1}$, so I must retain its bound $E_0C$.
For a rounded diagonal perturbation $\Delta_j$, put $u=2^{-F}$
and $\varepsilon=2u$. Component rounding implies
$\|\Delta_j\|\le\varepsilon$, regardless of the field size.
In exact-prefix coordinates,
\[
T_j=P_j^{-1}\Delta_jP_{j-1},\qquad
\|T_j\|\le C^2\varepsilon,\qquad
v:=MC^2\varepsilon<1/2.
\]
For any consecutive subproduct of the factors $I+T_j$, its norm
is at most $e^v<2$ and its distance from identity is at most $2v$.
Multiplying back by the endpoints gives:
\[
\|\widehat U-U\|\le2E_0MC^2\varepsilon,\quad
\|\widehat P_j\|\le2C,\quad
\|\widehat S_j\|\le2E_0C,\quad
\|\widehat P_{b:a}\|\le2C^2.
\tag{6}
\]
Here the hatted maps use rounded coefficients and unrounded data.
The segment assertion follows by writing the segment in the same
exact-prefix coordinates; it does not require inverting a rounded
prefix.

Each data rounding changes at most $N$ complex entries, with
Euclidean error at most $2Nu$. I propagate those residuals through
the perturbed suffixes in (6). I obtain (3), including the errors
from the completed identity words. In (2), the first precision
term pays strictly less than $2^{-t}/4$, because $R/(R+1)<1$;
the second pays at most $2^{-t}/4$.

I retain a discriminating counterexample to omission of $E_0$.
Take $q=2^{16}$ and the three two-wire logical layers
\[
\operatorname{diag}(q^{-1},q),\quad U(0),\quad
\operatorname{diag}(q^2,q^{-2}).
\]
The logical prefix and inverse-prefix bound is $\Pi=q$ and the
endpoint is $U=\operatorname{diag}(q,q^{-1})$, with $E_0=q$.
Use $\Gamma=q^2$, $c=2q^2+1$, and the upper word for the zero shear.
After its first central diagonal, the exact prefix is
\[
P=\operatorname{diag}(-5/(4cq),q).
\]
Consequently
\[
\|UP^{-1}\|=\frac{4cq^2}{5},\qquad
\frac{\|UP^{-1}\|}{C}
=\frac{32}{5}+\frac{1}{5\cdot2^{28}}>1.
\tag{7}
\]
The corrected bound $E_0C$ covers this suffix. I check the actual
retained word and routing prefix at this cut. This example refutes
the attempted unit-endpoint extension; it does not contradict the
completed FFT result.

## Connection to the retained full program

I admit an exact rational Toeplitz matrix $T$ of dyadic size $N$.
The retained admission routine checks its Toeplitz shape, inverts
each leading principal section and obtains component row/column
envelopes $\lambda,Q\ge1$. These imply
$\|T\|\le\lambda$ and inverse norm at most $Q$ for each leading
section. An invertible full matrix with a singular leading section
does not meet this admission.

I invoke the unchanged full allocation and actual recursive plan
at target $t$ and radius $R$. I bind their matrix, budget, wire
order and both stored plans. Let $\chi=\lambda Q$,
$\mathcal B=256N^3\chi^{12}$ and $a=3N-2$.
The retained [FULL-PROOF.md](vendor/full_source/FULL-PROOF.md),
equations (12) and (14), gives
\[
\|\widetilde T-T\|,\|\widetilde T^{-1}-T^{-1}\|
\le e=2a\mathcal B^3\eta,\qquad
\Pi=2\max(1,\lambda,Q)\mathcal B\mathcal H.
\tag{8}
\]
Here $\mathcal H$ is the retained generator/scalar fragment bound.
The source field execution_bound supplies $\Pi$ for stored logical
prefixes, suffixes and their inverses, in either direction.
I retain that author-proved dependency rather than interpret the
source's rounded-data amplitude field as an operator norm.

I use $E_0=\lambda+e$ for the forward program and $E_0=Q+e$ for
its stored inverse. I compile that inverse's actual reversed gate
schedule. Nonunitary scalar leaves require reciprocals, so a global
adjoint would give a different endpoint.

The retained choice
$\eta=2^{-s}$, with
$s=t+\lceil\log_2(4a\mathcal B^3(R+1))\rceil$, implies
\[
eR\le\frac{2^{-t}R}{2(R+1)}<\tfrac12\,2^{-t}.
\]
I add this operator defect times $R$ to (3), obtaining
\[
\boxed{\|\widehat y-T_I^{\pm1}x\|_2
\le eR+4E_0MC^2uR+4E_0CJNu<2^{-t}.}
\tag{9}
\]
For the declared ordered physical wires $I$, I write $T_I$ for
the conjugate of $T$ by that coordinate permutation. The forward
direction uses $T_I$ and the reverse uses $T_I^{-1}$. This identification
preserves the norms and applies the exact root to the intended wire order.
I discard the predecessor's data-rounding allowance for this purpose;
the new stage schedule incurs the rounding term in (9).
I authenticate the source bytes and preserve source assertions under
optimized Python. Runtime seals reject changes to the admitted root,
request bounds, logical plans, prepared pages and native precision contract.

## Widths, setup and remaining physical obligations

Using the segment bound in (6), I bound actual states by
\[
2CR+4C^2JNu
\le 2CR+\frac{C2^{-t}}{4E_0}
<A:=4C(R+1).
\]
Put $I=\lceil\log_2 A\rceil+2$ and $g=\log_2\Gamma$.
Rounded coefficient moduli are below $7\Gamma$. I allocate signed
component widths $F+g+5$ for coefficients, $F+I$ for data and
$2F+I+g+6$ for temporaries. The four real diagonal products and
their two sums have magnitude below $16\Gamma A$ and lie on the
$2F$ grid. Hadamard sums and their halves lie on that grid too,
because $F\ge1$. I observe mathematical component temporaries,
without asserting bounds on Python Fraction's internal operations.

For an input gate component height $b$, the fixed rational formulas
use a constant number of additions, multiplications and divisions.
Define height as the maximum bit length of the reduced numerator and
denominator. For rational values I use
$h(xy),h(x/y)\le h(x)+h(y)$ and
$h(x+y)\le h(x)+h(y)+1$.
For a nonzero complex value of component height $H$, I write it as
$(A+iB)/D$ with $|A|,|B|,D<2^{2H}$; its reciprocal
$D(A-iB)/(A^2+B^2)$ has component height at most $4H+1$.

For the shear, $h(c)=g+2$ and $h_{\mathbb C}(z)\le b+g+3$.
The coefficient $c/(8z)$ therefore has component height at most
$4b+5g+17$, or $4b+5g+18$ after native compensation. The other
coefficients in (4) have smaller bounds.
For a butterfly, I recover its unit phase from an actual gate entry
divided by the real splitter, obtaining component height at most
$2b$. Using $1/w=\bar w$ in the formulas of PROOF.md, I bound the
largest compensated entry by $5b+8$. Reversal and conjugation
preserve these bounds. Scalar words need $b+1$; routing and idle
constants need at most two. Hence I obtain
\[
h_{\rm prepared}\le
\max(4b+5g+18,5b+8,b+1,2)
\le5b+5g+18<32(b+g+8).
\]
For reverse execution, I measure $b$ on the actual stored inverse gates.
This allowance concerns prepared reference entries. It does not
price the preceding exact elimination, phase setup, table storage
or coefficient delivery.

The source has polylogarithmic logical depth and polynomial $\Pi$
in $N,\lambda,Q$. Thus the online signed widths are
$O(F_0+t+\log N+\log\lambda+\log Q+\log R)$.
I restrict this simplified bound to the retained full compiler;
the generic allocation (2) also depends on $\log L$.
I count $4MN$ real diagonal products, $hN/2$ pair Hadamard operations
and $JN$ complex roundings. Physical native-root invocation,
tensor admission, coefficient movement and complete tape cost remain
separate obligations.

If a future caller introduces additional error $\sigma$ after each
Hadamard stage's scaling, (6) gives the additional endpoint term
$2E_0Ch\sigma$. The current source allocation does not reserve the
FFT proof's quarter-budget for it. Such a caller must either use the
actual remaining margin in (9) and recompute the state allowance,
or strengthen the source and native allocations before adding that term.
I make no physical-call guarantee here.

## Evidence and credit

I execute the retained full fixture types in both directions:
complex, tiny and large scalars; complex near-identity matrices through
size eight; indefinite matrices; a half-shift Gaussian; unequal
subtrees; and a size-16 identity. I compare complete rounded outputs
with the same stored logical program and with separate exact matrix
and inverse references, including reversed wires and a 512-bit
incoming grid. I check complete exact native basis maps through
size two and for the mixed generic fixtures.

I also check zero and tiny complex shears, oriented mixed layers,
idle and empty programs, contiguous word segments and their inverses,
the counterexample (7), and calibrated admission and mutation controls.
The finite receipt corroborates the written argument within those
cases. I retain the earlier FFT receipt unchanged.

I credit Vlado Vojdanovski for the full circuit, zero-safe words,
Beneš routing and preceding stability structure; Chafik Boukhalfa
for certified phases; and the original rational-generator and Gaussian
contributors named in the retained archive. I use classical LDU,
Schur-complement and perturbation methods. I add this actual full-plan
connection, endpoint-sensitive native error budget and execution
contract. I claim no worldwide mathematical priority or new selected
multiplication exponent.

Jose Manuel (jmbarrancoml), with substantial OpenAI Codex assistance.
Internal source-analysis agents belong to the author process.
Independent assessment of the quantified proofs remains open.
Apache-2.0.
