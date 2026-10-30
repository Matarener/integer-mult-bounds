# Route-marker binding under one declared ROW-cover model

This joins the exact G20 route records from Ali Romman's PR #5798 at
`eaa9cc8c15d8e994d7b81b0cda3f6dd63b0db826` to the frozen RIGHT words of the
preceding `g20-normalizer-dyadic-words` package. The source already supplies
the complete endpoint/marker audit and its full finite bill. The new statement
is a marker-to-word join with an explicit conditional direction convention.
It neither recertifies the whole source nor identifies a physical marker ABI.

## Three actions that must be kept distinct

For one port write `Q=diag(1,0,...,0)` and let W and W^-1 be the authenticated
eight-dimensional normalizers. The inherited native interface gives
`P = W Q W^-1`. The preceding package's words have exact RIGHT products W
and W^-1; ADD[i,j,a] updates row coordinate j from coordinate i. In particular,
executing such a word on a cover row v means vW or vW^-1, respectively.

The identities here are rational. Dyadic words also remain invertible over
odd-modulus local rings under the admitted unit-P2 contracts, because their
scalings are signed powers of two. This does not widen native admissibility:
the inherited native theorem retains its sufficient guard `gcd(q,12)=1`,
its own modulus/prime hypotheses and all framework assumptions. Matrix algebra
alone supplies neither admission for every odd composite nor physical tariffs.

Native address operators instead act on column vectors. For a physical
16-coordinate address x define `d_i=x_i-x_(15-i)`, i=0,...,7. The source map
H_P is

```
x_i      <- x_i      - (P d)_i,
x_(15-i) <- x_(15-i) + (P d)_i.
```

In the paired ordering `(x_0,...,x_7; x_15,...,x_8)` its matrix is
`[[I-P,P],[P,I-P]]`. Let J reverse eight coordinates. Applying W to both
paired halves is `diag(W,W)` in that paired ordering, and therefore

```
D_W = diag(W, J W J)
```

in the physical contiguous ordering `(x_0,...,x_15)`. From `P W = W Q`, block
multiplication gives `H_P D_W = D_W H_Q`, hence
`D_W^-1 H_P D_W = H_Q`. These are identities of native column-address maps.
For function transport `T_M F(x)=F(M^-1 x)`, the corresponding pullback rule
is `T_M T_N=T_(MN)`; it must not be silently read as row-word execution.

## Conditional ROW direction and restoration

The chosen ROW-cover model is the retained row-route convention: a single
invertible cover matrix g is updated on the right to `h=gS`; an available
local projector P then acts globally with projector `h P h^-1` and returns
the complete cover h and exposed spectators unchanged. This restoration is
an inherited native/ROW contract, not a consequence of matrix conjugacy.
Desired global projector Q therefore requires

```
S = W^-1,
h P h^-1 = g W^-1 (W Q W^-1) W g^-1 = g Q g^-1.
```

Under this declared model, an ENTRY marker selects the frozen inverse_word,
and a RETURN marker selects forward_word. The returning cover is exactly
`g W^-1 W = g`, on arbitrary cover entries. Neither word is transposed or
silently reversed: each is executed in its certified RIGHT chronological
order. A return word is the literal reverse-and-inverse of its entry word.

The stage embedding and tensor lanes preserve this identity. Use the selected
eight active indices for that thick-stage ordinal, extend W by identity on
the other 119 ambient coordinates, and tensor with I_f for f>=1. For N=127f,
each factor is applied to all N cover rows and f lanes at its certified
source/destination addresses. Thus all inactive cover coordinates remain
unchanged, and the inverse pair restores the full chosen cover.

This is **one** GL-cover word for one owner-marker. The global projector
`g Q g^-1` already determines both native paired halves through the formula
for H above. Executing two independent words on two physical address halves
would be a different lowering. It is not an additional factor of two in this
single-cover model. Distinct owner banks in the stream remain distinct routes.

## Discriminating exact source examples

Port 2 has W equal to twice the permutation with
`e_0 -> e_2 -> e_1 -> e_0`. Hence `P=e_2 e_2^T`. Using forward_word at ENTRY
would give `W P W^-1=e_1 e_1^T`, whereas the correct inverse entry gives Q.
This separates the two direction choices on actual source data.

Port 1 has W equal to twice the swap of coordinates 0 and 1. Its P selects
coordinate 1. The correct physical D_W maps both paired coordinates together.
The naive contiguous `diag(W,W)` instead gives
`D_naive^-1 H_P D_naive e_0 = e_14`, while `H_Q e_0=e_15`.
Thus omitting the reflected second-half ordering is a real operator error,
even though the isolated eight-dimensional W product remains correct.

## Exact incidence versus assumed execution semantics

Each authenticated route record contains stage, physical owner, port and
ENTRY/RETURN phase. The finite join must check its complete source position
against CALLS, including the appropriate source/target bank, every port,
phase block, and the absence of paid route markers at stage zero. A program
identifier must bind the actual frozen word and its certified port matrix,
not merely agree with an aggregate count or an unrelated catalogue index.

The retained nonzero stages contribute `17*2 banks*111 ports*2 phases=7,548`
markers. Under the single-cover interpretation above this is 7,548 selected
word instances, with 3,774 in each direction. The marker fields themselves
do not encode right-multiplication, a physical head map or this ENTRY ABI.
Accordingly the incidence join can be exact while the direction-to-physical-
execution implication remains explicitly conditional.

A coefficient histogram must be rebuilt from the selected actual words.
For each selected word every local ADD or SCALE produces `N*f=127*f^2`
named cover-kernel calls. Each port uses both words in two banks over 17
nonzero stages, so a histogram already combining both directions is multiplied
by `34*N*f`, without a second paired-half multiplier. The preceding 7,992
catalogue cross-product instances are a different inventory. Their operation
counts are not an already admitted budget for these source markers.

The coefficient counts can form a positive symbolic tariff expression under
the named primitive contracts. Actual P2 tape movement, coefficient preparation,
head placement, complete low-cache COPY/CLEAR, carry correction, low-type
commit, padding, return workspace and their prices remain unknown. Unknown
costs are not zero. No absorption into the source's finite fee, new kappa,
ordinary compiler, native admission or selected-frontier change follows.

The inherited all-address native identities and full caller audit remain
authenticated dependencies. This conditional join does not replace them or
establish that the physical PAID_PORT_ROUTE implementation follows the chosen
single-cover model.

Credit: Ali Romman and retained G20/native/controller contributors for the
source data and paired-address interface; ToikY with OpenAI Codex assistance
for the preceding RIGHT factor words; JoyboyBrian and Chris R/Clear1nsight
for the retained ROW/P2 interface and its explicit implementation obligations.
This scoped proof/audit was prepared by ToikY with substantial OpenAI Codex
assistance in separate primary, oracle and review contexts. Retain NOTICE and
all predecessor credit. Apache-2.0.
