# FULL-target caller accounting and the fixed three-seed pressure gate

Scientific pin: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.
This note separates an exact formal bank identity, conditional caller invoices,
and an all-parameter necessary moment obstruction. It supplies no complete
native supplier, owner allocation, rounded implementation or new κ.

Write v = 111 for the number of E8 ports and h = 429 for the ordinary helpers
of the changed local word. Reserve N for the common-axis involution; N is not
the number of ports.

## The direct diagonal topology has zero deficit

The source-bound FULL-target local word has child histogram

`{1:1406, 2:1342, 3:79, 4:44, 5:93, 6:11, 7:9}`

and rank mass `5097 = 15v + 8h`. This includes all v rank-one cap-to-FULL
target lifts. Its physical two-bank block is

`[[S,0],[S,T]]`, with source progress rank7 and target progress rank8.

At common FULL, v additional ordinary ADDs cancel the cross term and give
`diag(S,T)`. These ADDs are not included in the emitted 12,932-ADD shear word.
They have no new recursive rank charge in this invoice, but their scalar work,
access, precision effects and physical implementation still have to be paid.
The local native/frame realization is inherited from the source-bound local
proof; this caller calculation does not independently reprove it.

Assume a direct caller with the following contract:

- L calls, L public banks, and two distinct active banks per call;
- one common axis and seven disjoint fresh axes per call, so `m = 1+7L`;
- each public bank is a source once and a target once in two distinct calls,
  providing its one common-axis N when targeted; thus each bank has exactly
  L−2 inactive stages;
- every inactive fresh interval is completed, and the h helpers per call are
  legally hosted inside these public idle regions with exact restoration;
- public stock is `W = vL`, with no additional unpriced stock or progress.

This is a conditional topology for integer L ≥ 2. The existence of legal
hosting is a separate premise; the arithmetic identity does not assert it for
any L. There are L² bank-stage pairs, of which 2L are active. Hence the raw
inactive fresh rank volume is `7v L(L−2)`. A legally hosted width-eight helper
occurrence replaces eight units of this raw idle volume, so the ideal total is

`Q = L(15v+8h) + 7vL(L−2) − 8hL
   = vL + 7vL²
   = Wm`.

Thus `D = Wm−Q = 0` for every L under this contract. Dropping the v target
lifts from each call changes Q to `Wm−vL` and creates the spurious deficit vL.
The apparent saving is exactly the omitted cost. A nonzero number of genuine
sub-parent-rank children gives positive pressure at every primitive exponent
a > 0, so this zero-deficit invoice cannot satisfy a strict supplier moment
test. Further charged work without new admitted progress cannot rescue it.

The helper subtraction is conditional on legal physical hosting. Even the
aggregate necessary inequality `7vL(L−2) ≥ 8hL` requires L ≥ 7 at these v,h.
That condition is not sufficient for chronological whole-helper ownership.

### Distinction from the retained full-target schedule

James Reed's [PR3850](https://github.com/CrocSwap/integer-mult-bounds/pull/3850),
inspected at `8f97d229d208e5fce7b42e6a1f1b8bf3cf522950`, audits the retained
pure recipe of Gonzalo-Mier's PR3772. That recipe has K bank pairs,
`L = 2K+1` calls, and `2K = L−1` public banks. Its per-pair idle ranks sum to
`7L(K−1)`, charged on both members of each pair. Thus its public idle rank
volume per port is `14L(K−1) = 7L(L−3)`.

For its rank7/rank8 full-target local profile, the deficit per port and replica
is

`(1+7L)(L−1) − 15L − 7L(L−3) = −1`.

This gives the reported `−111·32 = −3552`. The direct diagonal topology above
has L public banks and idle volume `7L(L−2)`, giving zero instead. These are
different complete invoices, and neither supports a generic claim that every
FULL-target caller has the same deficit. PR3850's stated execution domain is
K = 1,...,24; this review inspected its pinned source and derives the displayed
accounting identity, but did not replay its producer or Householder charts.

## Exact seeded bank algebra

Work over the ring `A = F₂[N]/(N²−1)`. For each ordered bank pair define

`F(x,y) = (x,y+Nx)`,
`B(x,y) = (x+Ny,y)`,
`F_new(x,y) = (x,x+Ny)`.

These are interface assumptions about the local calls at matched fresh-prefix
cuts. The identities below hold for arbitrary bank inputs. They do not require
clean data banks or specialize N to the identity.

Three old calls followed by exchange obey

`(x,y) ->F (x,y+Nx) ->B (Ny,y+Nx) ->F (Ny,Nx)
         ->exchange (Nx,Ny)`.

The equality uses only characteristic two and N² = 1. With eight arbitrary
initial banks `x_0,...,x_7`, use these three calls on banks0,1, then apply
`F_new` from bank0 to each bank j = 2,...,7. The result is

`(Nx_0, Nx_1, N(x_0+x_2), ..., N(x_0+x_7))`.

Six terminal CNOTs from bank0 to banks7,6,...,2 cancel each x_0 term and leave
`N·I_8` on all eight arbitrary inputs.

F, B, exchange and CNOT are involutions. The new call generally is not:

`F_new^(-1)(x,y) = (x,N(x+y))`,
`F_new²(x,y) = (x,(1+N)x+y)`.

The original producer's unused `inverse_event` helper has a stale comment
calling every primitive involutive. Its executed inverse loop correctly
replaces `new_F` by `new_F_inverse`; the checked inverse identity is sound.
The distinction must be retained when implementing or describing this word.

The independent checker uses the faithful regular representation

`a+bN -> [[a,b],[b,a]]` over F₂.

Its injectivity follows directly from the diagonal entry a and off-diagonal
entry b. Therefore equality of the resulting16-by-16 binary matrices proves
the ring identity, including its nontrivial characteristic-two behavior. The
checker constructs elementary matrices independently, compares all16 saved
prefixes, verifies each primitive's actual inverse, and composes the literal
reverse-inverse word back to identity. Omitting the middle seed B or the last
terminal CNOT changes an actual input/output matrix entry; explicit witnesses
are recorded.

A useful control is

`CNOT ∘ F_new = diag(I,N)`.

This leaves the raw source unchanged. It cannot be credited with common-axis N
progress on both arbitrary raw inputs. The seed supplies the encoded source
`Nx_0`; a different caller must supply or pay for its own input normalization.

## Fresh factors and changed idle windows

Let `G_0,...,G_8` be invertible fresh factors commuting with one another and
with N. Each active call advances its two banks by its stage G_s. Before a
call at stage s, both participating banks must have the same cumulative fresh
prefix `Gamma_s = product_(u<s) G_u`; an inactive interval must be explicitly
completed before that bank participates again. After the nine stages, complete
all remaining fresh intervals before the terminal CNOTs.

The actual eight-bank schedule has these windows:

| Bank | Active stages | Fresh idle query ranks |
|---|---|---|
|0|0–8|none|
|1|0,1,2|42|
|2|3|21,35|
|3|4|28,28|
|4|5|35,21|
|5|6|42,14|
|6|7|49,7|
|7|8|56|

The independent checker tracks formal Laurent monomials in all nine G_s,
with N exponents modulo two. It inserts each preceding idle interval at the
actual first required cut, checks both active prefixes match, advances each
active bank, and inserts each trailing interval before terminal decoding. The
endpoint is exactly `Gamma_9 N I_8`. Reversing every local primitive and every
fresh factor gives identity again. This is an exact formal computation, not a
finite Fourier sample or an assumption that unmatched prefixes may be stripped.

The idle ranks total378 per port. Counting width-eight slots separately within
these intervals gives

`5 + 6 + 6 + 6 + 6 + 6 + 7 = 42` per port,

or4662 aggregate slots. The three old and six new calls require
`3·438 + 6·429 = 3888` helper occurrences. This aggregate comparison is only
necessary capacity information. It does not assign a helper to an eligible
chronological window, establish frame compatibility, or justify reuse of an
old nineteen-event owner witness for this changed schedule.

Native admission at the changed cuts remains open in this caller note. In
particular, each local source/target interface must act as the assumed F, B or
F_new after the actual chart and common-past pullback, restore arbitrary helper
dirt, and permit the listed copied/frame operations. Formal fresh commutation
alone does not construct that native binding.

## Historical D15 and the later D33 ceiling

Each old R438 seed has complete histogram

`{1:1322, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:18}`,

mass5121, maximum rank7, and excess63 over its `14v+8·438` progress. The frozen
seeded-star algebra receipt used six earlier fanouts with private excess3.
Its optimistic common-axis budget was therefore

`2v − 3·63 − 6·3 = 15`.

The later FULL-target compensation word has the same proposed bank interface
and zero private excess, while retaining all target lifts. Substituting this
word into the **assumed** caller interface removes18 units of excess and gives

`2v − 3·63 = 33`.

The old receipt is correct for its historical private3 premise; its D15 must
not silently become the invoice of the changed zero-private construction.
Nor does the improvement to33 certify native substitution at the changed cuts.

For the explicit L9,n8 schedule, m = 64 and W = 8v = 888. The ideal mass is

`3·5121 + 6·5097 + 111·378 − 8(3·438+6·429)
 = 56799`,

whereas `Wm = 56832`; their difference is33. Replacing5097 by5100 restores
the historical difference15. The subtraction of hosted helper mass remains
conditional on legal ownership; padding, fallback and additional storage are
not discarded as unexplained free progress.

## All-L pressure obstruction under the D33 premise

Let H[r] be the complete child histogram of any completed candidate invoice,
with nonnegative multiplicities, stock W, and positive ranks `r ≤ m`. Define

`D = mW − sum_r rH[r]`,
`P(a,m) = sum_r rH[r]((m/r)^a−1)`.

The moment test `sum_r H[r](r/m)^(1−a) < W` is equivalent to `P(a,m) < D`.
Assume integer `L ≥ 3`, `m = 1+7L`, three unchanged old R438 seed profiles,
the complete-invoice ceiling `D ≤ 33`, and `a ≥ 1/500`.

Every omitted child's pressure is nonnegative because a ≥ 0 and r ≤ m.
For the retained seed children, r ≤ 7 and m ≥ 22. Hence

`P(a,m) ≥ sum_(three seeds) rH[r]((m/r)^a−1)
         ≥ (3·5121/500) ln(22/7)`.

For x > 1, writing z = (x−1)/(x+1), the positive atanh series gives
`ln(x) > 2(z+z³/3)`. At x = 22/7, z = 15/29, so

`P(a,m) > (15363/500)·2(15/29+(15/29)³/3)
         = 21108762/609725
         = 33 + 987837/609725
         > D`.

This is a strict exact rational lower certificate for every L ≥ 3 and
a ≥ 1/500, not a finite parameter sweep. The complete D ceiling is a premise;
nonnegative omitted pressure alone cannot establish it if a changed caller
adds new stock or progress credit. The exponent is primitive a. No unproved
outer map from a to a final multiplication κ is used by this theorem.

Dropping one seed, relaxing the seed rank ceiling from7 to8, or raising the
deficit ceiling from33 to35 makes this coarse witness insufficient. The checker
records those exact inequalities. They do not prove that a changed moment
passes, that a changed caller exists, or that any native supplier is admitted.

## Scope and provenance

The direct D0 identity is conditional on its direct n=L topology and hosted
invoice. The eight-bank construction is an arbitrary-input formal algebra
identity with explicit fresh-factor cuts. The all-L theorem excludes completed
invoices retaining three unchanged seeds, the declared arity and D≤33.
These results do not exclude changed seed words, shared operations, different
common-axis progress, different complete deficits, or different callers.

Chronological owner allocation, local-to-caller native binding, arbitrary dirty
restoration in those bindings, rounded error propagation, all-size recursion,
source/coefficient access, physical tape implementation and head return remain
separate obligations. The local integer prefix bound874 is not a rounded
precision theorem. Exact finite replays and this written all-L argument are
not formal-kernel evidence or independent human review.

Underlying E8/R438 geometry, scalar interface and transported word retain
their original PR555/543/545/510 lineage and Sagar Thakrar's transport credit;
the R429 source deletion retains Ali Romman's credit. The recursive-interface
lane supplied the FULL-target local construction, direct accounting, and
three-old-call seed with new-call fanout. The shared-helper algebra lane
supplied the frozen eight-bank word. The later budget lane supplied the exact
three-seed pressure certificate. This review independently reconstructs the
matrix and fresh-factor algebra and checks the stated invoices. It is prepared
with substantial OpenAI Codex assistance, under Apache-2.0.
