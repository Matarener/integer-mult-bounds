# An integer-shear target and its inverse share no paid call

**Scoped exact minimum in a formal register model. No new κ, supplier or
selected-frontier change.**

This contribution was produced by Nick Petalas. Apache-2.0.

## Question

PR [#3905](https://github.com/CrocSwap/integer-mult-bounds/pull/3905)
(1337isnot1337, `research/sl2z-four-call-native-target`, head
`b27bf4c72a822b21f483e08cb3241ad9d165b66f`) fixes the shear group

$$
G=\langle X,Y\rangle\leq\mathrm{SL}_2(\mathbb Z),\qquad
X=\begin{pmatrix}1&1\\0&1\end{pmatrix},\quad
Y=\begin{pmatrix}1&0\\1&1\end{pmatrix},
$$

the paid labels $\mathcal A=\{X,X^{-1},Y,Y^{-1}\}$, scalar ring
$\mathbb F_2[G]$, and the one-call factor
$D_N([g])=I_2+([g]+[e])N$ with $N$ a rank-one idempotent in
$M_2(\mathbb F_2)$. It proves that $\mathrm{diag}([B],[e])$, with
$B=X^2Y^2=\begin{pmatrix}5&2\\2&1\end{pmatrix}$, costs exactly four calls.

Its Open next question asks whether the two-role endpoint

$$
T=\mathrm{diag}([B],[B^{-1}])
$$

can share paid factors across roles and cost fewer than the eight calls of
the coordinate-projector word.

## Result

**The exact minimum is eight calls.** Cross-role sharing saves nothing.

The lower bound holds in a larger class than #3905's: any $\mathbb F_2$
frames $N$ (any rank, unit cost), arbitrary interleaved scalar maps, finite
clean or dirty workspace, and any change to workspace. The upper bound uses
only #3905's rank-one idempotents, two roles, no workspace and no cleanup.

### Lower bound

Over $\mathbb F_2$, $I+([g]+[e])N=(I-N)[e]+N[g]$. So every #3905 factor
is a gate of Ali Romman's merged
[`research/group-subproduct-cover`](../group-subproduct-cover/README.md)
(PR [#5394](https://github.com/CrocSwap/integer-mult-bounds/pull/5394)).
Its cover theorem ([PROOF.md](../group-subproduct-cover/PROOF.md), section 2)
states that, with the label set fixed, the paid count of a diagonal target
equals the least $k$ for which one word $w=(g_1,\dots,g_k)$ over the labels
has every target label in its ordered subproduct set

$$
S(w)=\{g_1^{b_1}\cdots g_k^{b_k}: b_j\in\{0,1\}\}.
$$

We cite that theorem and do not re-prove or audit it. The new step is the
cover number of $\{B,B^{-1}\}$ over $\mathcal A$. The verifier builds
$S(w)$ for **every** word of length $0$ to $8$ (87,381 words in total).
No word of length at most seven has both $B$ and $B^{-1}$ in $S(w)$.
Therefore every circuit for $T$ needs at least eight paid calls.

The census also records:

- $B$ and $B^{-1}$ each have exactly one four-letter word, `XXYY` and
  `yyxx` (lower case is the inverse label), and no shorter one.
- Exactly 124 words of length eight cover both targets.
- In 54 of them, some subproduct mask for $B$ and some mask for $B^{-1}$
  share a position. Positions can be shared at length eight, but never at
  a lower length.

### Upper bound

With $P=E_{11}$ and $Q=E_{22}$, both rank-one idempotents,

$$
D_P([X])^2D_P([Y])^2\,D_Q([Y^{-1}])^2D_Q([X^{-1}])^2
=\mathrm{diag}([X^2Y^2],[Y^{-2}X^{-2}])
=\mathrm{diag}([B],[B^{-1}]).
$$

The verifier checks this as an equality in $M_2(\mathbb F_2[G])$ and on 16
explicit dirty columns.

### Complete bill in the stated model

| Item | Count |
| --- | ---: |
| Paid factors (labels `X X Y Y y y x x`) | 8 |
| Scalar roles | 2, both arbitrary dirty inputs |
| Scratch roles | 0 |
| Copy, reset, restore or cleanup calls | 0 |
| Uncharged address updates | 0 |

## Evidence

`verify.py` uses the standard library only. It checks:

1. #3905's factor equals the #5394 gate for all six rank-one idempotents of
   $M_2(\mathbb F_2)$ and all four labels (the 24 legal factors);
2. the complete ordered-subproduct census above;
3. the eight-call identity and dirty columns;
4. eleven controls: each of the eight single-factor deletions fails, the
   reordered word `XYXY` fails, the pair $\{B,X^2\}$ is found to share one
   four-letter cover (so the census detects sharing when it exists), and
   40 random five-factor circuits with arbitrary $\mathbb F_2$ frames and
   interleaved scalar matrices keep all support inside $S(w)$.

A second cover-number routine in the same script (breadth-first over the
sets $S(w)$, separate from the census loop) agrees: no cover at length seven, a cover at length eight.

## Reproduce

From the repository root, with CPython 3.12:

```sh
python3.12 -W error -B research/sl2z-inverse-pair-cover/verify.py
python3.12 -W error -O -B research/sl2z-inverse-pair-cover/verify.py
python3.12 -B scripts/research_package.py --package research/sl2z-inverse-pair-cover
```

Expected marker (about one second per run):

```text
PASS_SL2Z_INVERSE_PAIR_COVER legal_factors=24 census_words=87381 max_both_cover_below_8=0 length8_both_covers=124 overlapping_mask_covers=54 geodesics=1+1 minimum_calls=8 controls=11 no_new_kappa
```

## Claim type and limits

This is a **scoped exact minimum**: a finite certificate (the census)
combined with a cited written theorem (#5394's cover theorem). The census
is complete for its stated alphabet and lengths; the lower bound for
arbitrary frames and workspace rests on the #5394 proof, which is not
re-checked here.

It is not a supplier, native implementation or complete multiplication
theorem. Group labels are formal basis elements. Native conversion of the
shear action, its physical cost and any recursive moment are unpriced; see
the commutative-carrier obstruction (#3937), binary carrier (#3947) and
moment results (#4126, #4146) for those questions. The result holds only
for the four-label alphabet: a larger alphabet can change the cover number.

## Open next questions

1. **Higher powers.** Is the paid count of $\mathrm{diag}([B^k],[B^{-k}])$
   exactly $8k$ for every $k\ge 2$? A cross-role saving for a higher power
   would be the first sharing gain for an inverse pair here. First step: a
   pruned census for $k=2$ up to length 15, or a general no-sharing lemma
   from the shortest words for $B^k$ and $B^{-k}$. Blocker: the naive census
   grows as $4^L$.
2. **One added label.** Does the eight-call minimum survive if the order-four
   element $S=XY^{-1}X$, or any single extra label, joins the paid alphabet?
   First step: repeat the census over five labels through length seven.
   Blocker: each added label needs its own native price; a formal count is
   not a supplier.

## Credit

- 1337isnot1337: model, single-target four-call theorem and this open
  question (PR #3905, cited, not audited).
- Ali Romman / aliromman: the ordered-subproduct cover theorem in
  `research/group-subproduct-cover` (PR #5394), used for the lower bound.
- The register-model lineage credited by #3905 (PRs #288 and #203) is
  retained.
