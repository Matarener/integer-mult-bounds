# Mixed-provider complex construction with external complete spectators

Written construction, 2026-10-19. This supplies the all-size complex assembly
for the literal PR4088 head 72d7efc181edb21806a878f174847c96dd410ab0.
PROOF.md composes it into multiplication. Its source bindings and the
ordinary primitive are written constructions, not a new Lean theorem.

## Domain and avoiding an expensive reservation pass

Let the total binary address length be n=Theta(p), let h<=p^epsilon,
epsilon<1 be fixed, and let the coefficients have O(p) bits. A requested
layer acts on h specified binary coordinates of the complete address cube.
All other coordinates are spectators and their values are arbitrary.
The goal is C tensor h, where C=[[1+i,1-i],[1-i,1+i]]/2.

Unlike the older fixed-spacing reservation, reserve only unselected bits.
There are enough: h polylog(p)=o(p). Put G=4ceil(log2 p)+6 and K=128G.
Reserve q row bits, three hG-bit dirty control fields and a log2(p)^2-bit
payload field, all disjoint from the selected bits. Here q=O(log(h+2))
is fixed by the row-stock calculation below, before removing any fields.
Place the row field before the selected region, two control fields before
it, the third after it, and the payload field at the actual address suffix.
Place the selected bits at spacing K in a region of length hK. This is a
partial coordinate bijection involving O(h log p+log2(p)^2) positions;
extend it on the union of its domain and image and fix the complement.

../capped-phase-fusion/SUPPORT-ROUTER.md proves this sparse coordinate permutation using two
matchings, three XOR shears per matching, residue colors and the compact
gadget. Its retained ordinary-interchange premise is supplied here by
BIT.md with a=a2. The compact all-size algebra and
total repair are explicit in PR2250's PROOF sections1-4: S and T are
bijections, S=T on the T-invariant good set, so TS^-1 permutes exactly
the bad holes; full LSD radix order makes every reinsertion succeed.
This is not an assumption that a computed full address key is cheaply sorted.

For the support router itself, before its polynomial control work, choose
an untouched contiguous log2(p)^2-bit gap and exchange it with the actual
suffix. Such a gap exists because the support has k=O(h log p+log2(p)^2)
positions and p/(k log2(p)^2) tends to infinity. The suffix is fixed under
the conjugated permutation. Its complete values supply a superpolynomial
payload. All control reservoirs are chosen in the remaining prefix.
The finite initial range where these checked inequalities fail uses the
elementary algorithm and enlarges the uniform asymptotic constant.

After placement, the complete suffix gives record size at least
p*2^ceil(log2(p)^2). This pays every fixed polynomial control preparation
in the complex monomial compiler. Each original coefficient still has
O(p) bits; a long record is a stream of those coefficients. Nothing is
replicated or initialized. The placement and its inverse cost
O(V h^(1-a2) polylog(p)+V polylog(p)).

## Source binding and endpoint

The four literal providers are THREE/base, THREE/extra, FOUR/base and
FOUR/extra in PR4088. They have 632 live registers and 91 private dirty
buffers. Use the exact native recipes, entrance and terminal wrappers,
forward or dual program and cleanup belonging to the selected provider.
The full 723-column symbolic checks and native recipe checks establish
their one-column common-label identities. The fixed dispatch selects FOUR
exactly when (109t mod324)<109 among the 3240 chronological calls.

For any module and any scalar ADD u+=cv, the identity
T(u+cv)=Tu+cTv proves the eventwise label invariant. Native warp events
also retain their unary operator symbols in the conjugated shadow. The
source's exact semantics is a matrix over the free group algebra of those
symbols, not merely a scalar endpoint checked in one numerical realization.
Its entries are sums of scalar multiples of reduced operator words. The
complete 723-column certificate cancels those words formally.

Evaluate each unary generator G at G tensor f, and every scalar coefficient
at the same scalar times identity. This defines a representation of that
free group algebra: products and inverses map correctly, and addition is
module addition. Every certified free-word cancellation therefore survives.
Replace each canonical frame label T by T tensor f; the native directed
recipe identities supply the corresponding frame changes. This is the
eventwise conjugation proof with an operator-valued shadow.

In particular each listed initial correction c G_word x is implemented
by a private copy, the unary product G_word tensor f and the declared
scalar ADD; undo that unary product and subtract the copied source to
clear the work. If several terms combine to (G_word-I)x, they remain
separate terms, yielding G_word tensor f-I rather than
(G_word-I) tensor f. The expanded native program and its private-buffer
contract specify the exact correction terms. They add no
unpriced child: every unary warp in this correction is a fixed monomial.
An affine offset repeats in all columns; a constant monomial phase i^a
becomes i^(fa). A role SCALE or bridge sign stays scalar. This proves
the native lift on arbitrary correlated live and private data, including
the actual warp/correction events in the four mixed providers.

Every rank-r native transition executes its right monomial, one proper
C tensor rf child, and its left monomial. Row additions over F2 express
the fixed-dimensional affine monomial; PR2250 sections5-6 implement each
addition across all f columns with the compact primitive, and implement
the quadratic phase as exact Gaussian sign/swap operations. No linear
combination of unary operators is tensorized as a whole.

The owner fill supplies every 3240*408 ordered call/helper role. Its exact
windows, unique source family/port in each call, offsets and widths give
distinct complete packets and disjoint hosted phase slices. The exact
Z4 identities at all112 ordered ports and the eight-stream scalar
controller identify the completed global operator. Their unary phase
polynomials add over columns, so they hold for every positive f. At each
deadline retain the actual residual axes AND its translation, including
zero-rank residues with a nonzero translation. Apply the final orthogonal
defect correction X_delta after the terminal exchange, with
delta_i=(wt(row_i(g))-1)/2 mod2. The identity
P_g C_all P_g^-1=C_all X_delta follows by expanding Hamming weight modulo4.

Thus the full core is C tensor 73f on every family and cover packet;
helpers are arbitrary, row labels return, and every spectator is fixed.
This argument uses the exact mixed fill, not an older fill with the same
histogram. The input words, recipes, fill and exact replay artifacts remain
the immutable PR4088 sources; the ordinary/outer historical admission CLI
is not being represented as freshly executed.

## Common cover, fresh rows and fixed tapes

Set W=322560 and Gamma=2^1296 product_{i=1}^{36}(2^(2i)-1).
This is |O(73,2)|: the all-one vector has norm1 and its perpendicular space
is symplectic of dimension72. Count successive symplectic pairs.
Define D(e)=0 for e<73 and D(e)=1+D(48floor(e/73)) otherwise.
Every child r floor(e/73), r<=48, decreases D, and two levels halve e.

Reserve q=ceil(log2((W Gamma)^D(h))) row bits. Pad their complete range
to R=ceil(2^q/(W Gamma)^D(h))*(W Gamma)^D(h), a factor less than two.
At a node, split the fresh row stock into W families, a full Gamma cover
field and the remaining divisible stock. A child receives the latter
stock, the complete compact controls and suffix payload. It receives no
buried ancestor parameter or private external scratch. All its row padding
was done once at the root; no product of per-level padding factors occurs.
The endpoint fixes every row, so padded zero rows return to zero and may
be removed before the inverse placement.

For each common cover value gather the declared distinct provider packets,
retaining their original copies until the word finishes. Apply the native
entrance view, execute the literal word, invert the exit view and replace
the original packets. The cover has fixed finite cardinality independent
of p. Its enormous enumeration and the finite dispatch can be encoded in
finite control, or regenerated using encoded counters with a fixed bound.

Serialize inactive streams, descriptors, return labels and scalar state
at child boundaries. A fixed number of work tapes suffice: depth-first
children reuse roles and return an owned output with erased local work.
Their payload volume is V/(W Gamma); the parked ancestor volumes form a
geometric series. The work inventory can be any fixed sufficient number
of packet slots for the four words (for example W+1024); it changes the
implementation constant, not W in the recursive moment. Original input
preservation and output replacement are charged sequential scans.

## Exact coefficient simulation

First define the well-founded computation over Q[i]. An incoming array of
height t lies on 2^-(P+t)Z[i] and has magnitude at most2^t. A completed
C tensor u child raises height by at most u. There is a fixed constant S
bounding total completed child widths divided by f across all calls and
cover values, and a fixed constant E bounding all scalar dyadic operations
and finite prefix growth. The complete coefficient scan in
check_composition.py reduces signed fractions first and confirms that all
four words have only denominators1,2,4,8; negative stored denominators
encode signs, not a failure of the dyadic-grid property. Neither depends on e, p or coefficient values.

Only one child is unfinished. The additional height obeys
A(e)<=A(48f)+Sf+E, with an elementary linear bound at leaves. Since
73-48>0, induction gives A(e)<=C e for a fixed C. The source finite
dyadic coefficients and finite event words make S,E effectively computable;
they need not equal the earlier R480 numerical allowance.

Use one common grid of P+ceil(Ch) fractional bits and ceil(Ch)+O(1)
integer/sign bits at every descendant. Every exact division discards zero
bits by the height invariant. Completed-child cancellation restores the
stronger divisibility without truncation. Because h<=p^epsilon, this is
O(p) bits per component. COPY, ADD, fixed dyadic Gaussian multiplication,
sign, exact shift and CLEAR are charged linear scans of these words.

For H0=[[1,1],[1,-1]]/2, put D=diag(1,i). The exact identity is
H0=((1-i)/2) D C D. Tensor diagonals are phases from address weight modulo4.
The scalar ((1-i)/2)^h is a power of two times a unit phase, with a possible
factor1-i according to parity. It needs only fixed sign/add/shift scans,
not h repeated passes or a general large-integer multiplication.

## Time

The exact paid histogram is
{1:8060060,2:2310120,3:751813,4:327210,5:66425,8:25920,48:138492}.
Let b=.001730979115670792472760579929302792893760378764;
the rational interval certificate gives mu_(1-b)<1 for
mu_x=sum_r(H_r/W)(r/73)^x. Put q=b-10^-28, a_eff=(b+q)/2,
eta=10^-32 and tau=1-a_eff. Then mu_tau<1 and a2>a_eff>q.

Stop at width max(73,h^eta). At each internal node, all adapters,
monomials, packet scans and parking cost O(V e^(1-a2) polylog(p)),
bounded by O(V e^tau polylog(p)). The strict tau moment sums this to
O(V h^tau polylog(p)). The strict (1-b) moment bounds the sum of leaf
volumes times leaf work by O(V h^(1-b+eta*b)). The exact ledger verifies
(1-eta)b>q. Root placement and elementary bounded remainders have at most
the internal cost. Hence the complete layer costs

    O(V h^(1-q) polylog(p))

after retaining any desired smaller positive gap for the displayed logs.
The source bindings and their checks are recorded in SOURCES.json and
AUDIT.md. This is an all-size mathematical construction, not a claim about
simulator wall-clock speed or a
physical run of the full orthogonal cover.

## Gaussian call sites

The Gaussian application calls this construction only on complete
binary rectangles with enough unselected address space. Its compiled
layers use h=O(p^beta) or O(p^epsilon), both o(p/polylog(p)), so the
domain is available on the full array, including all coarse spectators.
GAUSSIAN.md's complete-array construction retains all coarse spectators
at these calls. PROOF.md supplies the outer error and exact recovery.
