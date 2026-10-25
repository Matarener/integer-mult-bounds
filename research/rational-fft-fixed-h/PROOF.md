# Fixed-H lowering of the retained rational FFT

I bind the actual rational FFT producer from PR4205 to Vlado's retained
six-H word and Beneš compiler. I retain both source algorithms and add
the gate connection, precision allocation and storage contract below.
I use classical LDU factorization and norm perturbation methods.

## Domain and result

Let the complete field have size $N=2^m$. Select an ordered list $I$
of $n=2^d\le N$ distinct addresses. Let $F_I$ act as the normalized
DFT on that ordered list and as identity on the other coordinates.
Take a rational $R\ge\max(1,\|x\|_2)$, target integer $t\ge1$,
and complex rational input on the $2^{-F_0}$ grid, $F_0\ge0$.
I use Euclidean norms and their induced operator norms throughout.

For $n\ge2$, define

\[
L=d+1,\quad J=L(16m+5),\quad M=L(8m+3),\quad h=L(8m+2),
\qquad K=2^{14}.
\]

I use $J$ for primitive stages, $M$ for diagonal stages and
$h$ for whole-field Hadamard stages. I preserve the source's
possibly empty bit-reversal layer. I choose

\[
P=\max\{3,\ t+\lceil\log_2(8d(R+1))\rceil\},
\]
\[
\boxed{F=\max\left\{F_0,
t+\lceil\log_2(16MK^2(R+1))\rceil,
t+\lceil\log_2(16KJN)\rceil\right\}.}                 \tag{1}
\]

I use the retained phase contract: its rational unit phases have
component height at most $2P+12$ and error at most $2^{-P}$,
with the stated certified interval enclosures. I authenticate the
unchanged producer and oracle before execution. This contribution does
not independently reprove the interval backend's universal correctness.

I prepare exact rational diagonal references, round their components to
the $F$-grid, and round after **each** emitted diagonal or $H_0$ stage,
where
\[
H=\begin{pmatrix}1&1\\1&-1\end{pmatrix},\qquad H_0=H/2.
\]
With nearest component rounding, including its stated upward tie rule,
I obtain
\[
\|\widehat y-F_Ix\|_2<\tfrac34\,2^{-t}.              \tag{2}
\]
The same statement holds for the original producer's stored adjoint and
target $F_I^*$. I retain finer incoming grids. Coefficient records,
data records and arithmetic temporaries require
\[
O(F_0+t+\log N+\log R)
\]
bits per signed component. I give explicit widths below.

For $n=1$, I retain the empty source plan and return the input exactly.
I make no bit-zero Hadamard call when $N=1$. I use
$F=\max(F_0,1)$ for the empty-program record; all three errors are zero.

## Rational butterfly and its stored adjoint

The frozen producer emits
\[
B=\begin{pmatrix}a&bw\\b&-aw\end{pmatrix},\qquad
a^2+b^2=|w|^2=1,\quad a,b\ge\tfrac12.
\]
Its splitter approximates $e^{i\pi/4}$ with component-l1 error at most
$2^{-P}\le1/8$, which implies the last inequalities. I also check them
before lowering each actual gate. The older `gateword('fft',w)` has
endpoint $H\operatorname{diag}(1,w)$; it is a different matrix.

Write $U(q)=\left[\begin{smallmatrix}1&q\\0&1\end{smallmatrix}\right]$,
$L(q)=U(q)^T$, and $D(s,t)=\operatorname{diag}(s,t)$.
For $q\ne0$, the retained `u3` executes
\[
D(1/c,1),H,D(-3,1),H,D(2,1),H,D(-c/8,-1/6),
\qquad c=4q/5.
\]
I can verify its endpoint without a symbolic backend: the middle
product $HD(2,1)HD(-3,1)H$ is
\(\left[\begin{smallmatrix}-8&-10\\0&-6\end{smallmatrix}\right]\).
The two outside diagonals therefore give $U(q)$.

Set $r=b/a$, $s=rw$. Both parameters have modulus between $1/2$
and two. Then
\[
B=L(r)D(a,-w/a)U(s).
\]
I call the unchanged `u3`, `D` and `canonical` functions on
`u3(s) + [D(a,-w/a)] + reversed(u3(r))`. In execution order the
seven diagonals of $D_0,H,D_1,H,\ldots,H,D_6$ are

| Index | Diagonal entries |
|---|---|
| 0 | $5a/(4bw),1$ |
| 1 | $-3,1$ |
| 2 | $2,1$ |
| 3 | $b^2w/(100a),-w/(36a)$ |
| 4 | $2,1$ |
| 5 | $-3,1$ |
| 6 | $5a/(4b),1$ |

Thus I keep six Hadamards, rather than concatenating three generic
six-H words. For the stored adjoint I reverse and conjugate this raw
word. Conjugating only $w$ in the forward butterfly would put the
twiddle on the wrong side. I compare the exact word endpoint with the
actual frozen gate matrix before routing it.

All raw diagonal moduli are at most three, and their reciprocal moduli
are at most 400. For any contiguous raw-word segment, multiplication
of factor norms gives the direct allowance
$(5/2)^2\,3^2\,2^2\,(\sqrt2)^6=1800$.
For inverse segments, I use $\|H^{-1}\|=1/\sqrt2\le1$, the two
outside inverse bounds $8/5$, and the middle inverse bound 400.
Their product is 1024; the other inverse diagonal norms are at most one.
These estimates also hold for the reversed conjugate word.

Replace each raw $H$ by $H_0$, and double its immediately following
diagonal. In the resulting word any contiguous segment differs from
the corresponding raw segment by a scalar in $\{1/2,1,2\}$.
Consequently 4096 bounds its direct and inverse norms.
Native diagonal moduli are at most six. For stored phase-component
height $2P+12$, the displayed formulas and $1/w=\bar w$ give
reduced component height at most $8P+64$, including compensation.
All rational divisions belong to coefficient preparation.

## Complete routing and inactive pairs

I extract nine unchanged functions from the pinned tensor source:
`benes`, `D`, `u3`, `id2`, `id3`, `canonical`, `gateword`,
`matching_permutation`, and `local_layer`. I substitute exact rational
scalar operations for the needed `s` operations and compile the
untouched function AST with assertions enabled. I execute no SymPy
imports or unrelated source tests.

The source sends input $i$ to output $p[i]$. An oriented pair
$(a,b)$ goes to $(2j,2j+1)$. I preserve this order and complete
unused addresses with full identity words. All-one diagonal padding
would give $H^6=8I$, not identity. The completed native identity word
can still incur data-rounding error; I charge those sites below.

For completeness, I retain the source's Beneš induction. Regard the
input pairs and output pairs as vertices of a bipartite graph, with one
edge per wire. Each vertex has degree two. Alternating colors around
its even cycles give one edge of each color at each pair. The first
switch sends color $c$ to parity $c$; the final switch restores the
required output order. Each color induces a permutation of $N/2$
pairs, which the source routes recursively. Its two parallel subnets
have equal depth and a common bit at each layer. From depth one at
$N=2$, induction gives $2m-1$ switch layers. Reversing the layers
inverts the route because each switch is an involution.

Each source switch layer executes $H,D(1,\pm1),H,D(1/2,1/2)$.
After native compensation it executes
$H_0,D(2,\pm2),H_0,I$. Its completed map is a permutation, and
its exact prefixes and inverse prefixes have norm at most $\sqrt2$.
The retained identity and swap central words have smaller envelopes
than the butterfly word above.

The left route, central word and right route therefore contribute
$8(2m-1)+13=16m+5$ primitive stages per logical layer, including
$8m+2$ Hadamards and $8m+3$ diagonals. I retain adjacent diagonal
stages and their distinct rounding sites. These counts apply even to
the empty bit-reversal layer of the two-wire FFT.

Every completed original matching layer is unitary, including its
inactive coordinates. Its incomplete central prefixes are direct sums
of bounded two-wire prefixes; its routing prefixes have the bound just
proved. Hence $K=2^{14}$ bounds each exact prefix, inverse prefix and
suffix of the entire lowered FFT. The same argument handles its stored
adjoint. I do not multiply this allowance once per completed FFT layer.
For arbitrary exact segments, $K^2=2^{28}$ suffices.

## Coefficient perturbation and data rounding

Put $u=2^{-F}$. Component rounding changes a diagonal entry by at
most $\varepsilon=2u$ in complex modulus. Therefore each complete
diagonal operator changes by norm at most $\varepsilon$, independent
of the number of entries. Only the $M$ diagonal stages have this
coefficient perturbation.

Let $P_j$ denote the exact native prefix through stage $j$, and
let $\Delta_j$ denote a diagonal perturbation. In exact-prefix
coordinates the perturbed step is $I+T_j$, where
\[
T_j=P_j^{-1}\Delta_jP_{j-1},\qquad
\|T_j\|\le K^2\varepsilon.
\]
Equation (1) implies
$MK^2\varepsilon\le2^{-t}/[8(R+1)]<1/2$.
I use $\prod(1+\|T_j\|)\le e^{MK^2\varepsilon}<2$ and
$e^v-1\le2v$ for $0\le v\le1/2$.
At the completed endpoint, $P_J$ is unitary. Thus
\[
\|\widehat U-U\|\le2MK^2\varepsilon.                  \tag{3}
\]
Perturbed prefixes and suffixes have norm at most $2K$, and
perturbed arbitrary segments have norm at most $2K^2$.

I now charge rounding after each primitive stage. At most $N$ complex
entries change, so $2Nu$ is a sufficient Euclidean allowance at each
site. Propagating those residuals through the perturbed suffixes gives
\[
\|\widehat y-Ux\|_2
\le4MK^2uR+4KJNu.                                     \tag{4}
\]
This includes routing, inactive words and the normalized Hadamard
outputs. I do not assume exact restoration of idle data after rounding.

For the original FFT, the splitter matrix differs from the ideal
normalized splitter by at most $2^{-P}$ in operator norm, and its
diagonal unit twiddle differs by at most $2^{-P}$. Each butterfly
layer therefore differs by at most $2\,2^{-P}$. Telescoping the
$d$ unitary layers gives
\[
\|U-F_I\|\le2d\,2^{-P}.
\]
Taking adjoints preserves the same estimate. I obtain the full bound
\[
\boxed{\|\widehat y-F_Ix\|_2
\le2d\,2^{-P}R+4MK^2uR+4KJNu<\tfrac34\,2^{-t}.}      \tag{5}
\]
Each of the three allocations in (1) pays its corresponding term.

The original rational FFT and its stored adjoint form a unitary pair.
The two new dyadic-coefficient programs generally do not form an exact
inverse pair. Inverting an expanded quantized word requires reciprocals
of its actual stored factors; lowering the original adjoint is a
different operation. I claim the two approximation bounds in (5).

## Magnitudes, words and native-call boundary

The same prefix argument bounds actual states by
\[
2KR+4K^2JNu\le A:=4K(R+1).
\]
Let $I_b=\lceil\log_2 A\rceil+2$. Nearest rounding can increase a
coefficient modulus slightly, but the resulting modulus is below seven.
The following signed widths suffice:

| Record | Component bits |
|---|---:|
| Rounded coefficient | $F+5$ |
| Stored data | $F+I_b$ |
| Arithmetic temporary | $2F+I_b+6$ |

For a complex diagonal product I form its four real products and two
component sums before rounding. Their magnitudes are below $16A$,
and their values lie on the $2F$-grid. A Hadamard sum followed by
division by two lies on the $F+1$-grid, which the $2F$-grid contains
because $F\ge1$. These bounds prove the stated word allowance.
The verifier observes these mathematical component temporaries; it
does not trace the implementation internals of Python's `Fraction`.

The reference implementation performs $4MN$ real diagonal products,
$hN/2$ pair Hadamard operations and $JN$ complex roundings. I retain
the source's stage counts. I keep table generation, storage and movement
distinct from these arithmetic counts and make no fixed-tape cost claim.

If a physical native call supplies an additional absolute Euclidean
error at most $\sigma$, measured after its caller's scaling, then
the extra endpoint error is at most $2Kh\sigma$. The choice
\[
\sigma\le2^{-t}/(8Kh)
\]
pays this from the remaining quarter-budget. The additional state term
$2K^2h\sigma\le K2^{-t}/4$ also fits inside $A$.
For $h=0$, no such call occurs. A physical consumer must establish its input-domain, complete
record and spectator conditions as well as this error allowance.
The present verifier executes exact arithmetic $H_0$ followed by the
declared grid rounding; it does not invoke a physical T74 supplier.
Across $g$ tensor axes, raw-H restoration requires $2^g$, rather
than the single-axis factor two used here.

## Evidence and attribution

I retain the published arithmetic and FFT producer unchanged, with
original commit and byte provenance. I authenticate the source compiler
before extracting its functions. I compare exact complete native and
retained FFT endpoints on arbitrary signed complex vectors, and complete
basis matrices for fields through size eight. I also compare a direct
Fourier interval formula using the declared phase backend.

The finite cases cover fields through 64 wires, arbitrary wire order,
partial active fields, the stored adjoint, large input radius, singleton
programs and a 512-bit incoming spectator. I check sixteen standalone
butterfly words and their exact contiguous-segment and inverse envelopes.
I retain explicit controls for compensation, orientation, idle words,
source assertions, precision, source corruption and typed receipts.
These checks corroborate the quantified proof; they are not a proof kernel.

I credit Vlado Vojdanovski for `u3`, the fixed word format, Beneš routing
and FFT schedule; Chafik Boukhalfa for certified rational phases; and
the classical Fourier, LDU and perturbation methods. I preserve our
PR4205 producer's attribution and the separate PR4178 tensor precision
protocol. I add the connection to the actual rational butterfly and
its complete fixed-grid FFT execution contract. I claim no worldwide
priority for the underlying mathematical methods or new multiplication
exponent. Physical delivery and the complete tensor/outer theorem remain open.

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance.
Internal analysis agents belong to the author process. Apache-2.0.
