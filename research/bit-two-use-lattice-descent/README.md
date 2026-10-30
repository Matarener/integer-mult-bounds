# Two-use lattice descent excludes one eight-call bit candidate

**Scoped negative result; No new κ.** The profile
`(A,B,P,Q,R,S) = (1,3,0,1,1,2)`, with `R=2A` and `S=P/2`, cannot realize
the four-target endpoint below, for **any finite number of restored dirty
registers**, any ordering, and any free address-independent binary mixing.
This resolves the specific example in open question 2 of
[JosieElliston's pending PR6111](https://github.com/CrocSwap/integer-mult-bounds/pull/6111),
at head `961b749fa40a1117d0746064528d2dfa290c57e0`.

The candidate passes determinant, bounded subset-support, and every first-order
character-rank inequality on its actual address lattice. The new step is to
contract its two half-frame calls, then use a character on the smaller lattice.
No scalar-word search is needed. The all-width conclusion rests on the written
proof; the executable supplies exact, finite regression evidence.

## Model and source boundary

Use the rational address matrices

\[
A=\begin{pmatrix}1&0\\0&0\end{pmatrix},\quad
B=\begin{pmatrix}0&0\\0&1\end{pmatrix},\quad
P=\tfrac12\begin{pmatrix}1&1\\1&1\end{pmatrix},\quad
Q=\tfrac12\begin{pmatrix}1&-1\\-1&1\end{pmatrix}.
\]

Thus `A+B=P+Q=I`, and set `R=2A`, `S=P/2`. Each allowed label is positive
rank one. The group algebra is `F2[Λ]`, where
`Λ=ZA+ZB+ZS` is a free abelian rank-three lattice. Rational frame entries
are not reduced modulo two. Write `[F][G]=[F+G]`. On `w>=4` registers a
paid call is

\[
E_F(N)=I+([F]-1)N,\qquad N\in M_w(\mathbb F_2),\quad N^2=N,\quad
\operatorname{rank}N=1.
\]

The target is the complete matrix

\[
T_w=\operatorname{diag}([A+P],[A+Q],[B+P],[B+Q],1,\ldots,1).
\]

Every register starts arbitrary; all extra registers must be restored. Free
maps are matrices in `GL_w(F2)`, independent of the address. Equality means
equality of every formal coefficient, not equality at a finite address size.

The model and endpoint are inherited from Cinna Davis's PR2085/2112 through
[Nick Petalas's PR2910 note](../bit-fifth-frame-determinant-obstruction/README.md).
**Its fifth frame is different:** we use that note for the four old labels,
endpoint and operation model, not its five-frame exclusion theorem. PR6111
supplies the concrete question; neither its seven-call theorem nor pending
PR6089's classification is assumed. No predecessor executable is imported.

## Two-use descent lemma

Let `H` be an index-two subgroup of an abelian address lattice `Λ`. Call an
exponent *even* if it lies in `H`, and *odd* otherwise. Suppose a word has an
even endpoint, exactly two paid calls with odd labels `s,t`, and all other
paid labels in `H`. Free binary mixing may occur anywhere. Then its two odd
calls can be replaced by one call with label `s+t` without changing the
endpoint, register count, or intervening even calls and free maps.

The replacement is a legal paid call in a proposed alphabet only if `s+t`
is admitted there. A zero sum gives the identity. The lemma is an algebraic
reduction, not a claim that arbitrary summed frames have a native tariff.

**Proof.** Write the two odd calls and everything between them as

\[
U=E_s(N_1)\,M\,E_t(N_2),\qquad M\in M_w(\mathbb F_2[H]).
\]

The outer factors and their inverses are even: `E_h(N)^{-1}=E_{-h}(N)`
for `h in H`, and free binary maps are constant. Removing those factors
therefore shows that `U` is even. These inverses are used in the proof only;
no inverse calls are inserted in the replacement word.

Put `C=I-N1` and `D=I-N2`. Idempotence gives `CN1=N1C=DN2=N2D=0`.
Since monomials commute with matrices, the block expansion is

\[
U=CMD+[t]CMN_2+[s]N_1MD+[s+t]N_1MN_2.
\]

The middle two terms are the odd part. Multiplying their zero sum on the
left by `C` and on the right by `N2` isolates `[t]CMN2`; multiplying on the
left by `N1` and on the right by `D` isolates `[s]N1MD`. Monomials are
units, so `CMN2=N1MD=0`. It follows that

\[
M=CMD+N_1MN_2,\qquad N_1M=MN_2,
\]

and hence

\[
U=CMD+[s+t]N_1MN_2=M E_{s+t}(N_2).
\]

This leaves `M` unchanged and uses the same rank-one projector `N2` in the
new call. It applies to every finite width. The projectors need not be equal
when `M` contains free mixing. If all free maps have first been normalized
away, augmentation `M -> I` implies `N1=N2`. No such normalization is needed
for the contraction itself. ∎

## Exclusion of the candidate

Here `H=ZA+ZB+ZP` is the index-two subgroup of `Λ=ZA+ZB+ZS`. Every old
label, `R=2A`, and every target exponent lies in `H`; only `S` lies outside.
There are exactly two `S` calls. The lemma replaces them by one `P` call,
giving the seven-call profile

\[
(A,B,P,Q,R)=(1,3,1,1,1).
\]

For completeness, the character-rank obstruction is as follows. An additive
`χ:H -> F2` induces `[F] -> 1+χ(F)ε` in `F2[ε]/(ε²)`. Free binary maps
can be moved to the right by conjugating the paid projectors. Conjugation
preserves rank and idempotence. Augmentation of the target is `I`, so the
final free map is `I`. Comparing first-order coefficients now gives

\[
\sum_{i:\chi(F_i)=1}N_i
=\operatorname{diag}(\chi(A+P),\chi(A+Q),\chi(B+P),\chi(B+Q),0,\ldots,0).
\]

Choose `χ(A)=χ(B)=0`, `χ(P)=1`. This is a character on the free basis of
`H`, and `Q=A+B-P` gives `χ(Q)=1`, while `χ(R)=χ(2A)=0`. Only the one
`P` and one `Q` calls contribute. The left side has rank at most two and
the right side has rank four. Contradiction. ∎

This character does **not** extend to `Λ`: there `P=2S` forces `χ(P)=0`.
That is why contracting before applying the character adds information.

## What the original checks miss

The candidate's determinant sum is
`A+3B+Q+2A+2S=4I`, the target determinant exponent. Literal enumeration of
all 256 subsets of its eight labelled occurrences finds target support
multiplicities `1,1,3,3`. In basis `(A,B,S)`, the eight characters give:

| character | detected calls | target rank |
|---|---:|---:|
| 000 | 0 | 0 |
| 001 | 2 | 0 |
| 010 | 4 | 2 |
| 011 | 6 | 2 |
| 100 | 2 | 2 |
| 101 | 4 | 2 |
| 110 | 4 | 4 |
| 111 | 6 | 4 |

All satisfy the necessary inequality. These checks are not sufficient for
realizability; this example is a concrete counterexample to treating them
as sufficient. It is not a counterexample to PR6111, which explicitly left
realizability open.

Even the full first-order matrix equations are jointly consistent. At width
four, assign `A,R,S,S` to coordinate projector `E00`, the three `B` calls
to `E11,E22,E33`, and `Q` to `E33`. This one assignment satisfies all eight
character equations. Its exact product is not the target; both polynomial
engines check that distinction. Thus the contraction uses information beyond
simply solving the initial first-order equations together.

## Reproduce and evidence

From repository root, with Python 3.12 and the standard library:

```sh
python3 -I -B research/bit-two-use-lattice-descent/verify.py
```

Expected: `PASS_BIT_TWO_USE_LATTICE_DESCENT ... descent_rank=2<4`.
The verifier recomputes and compares every field of [RESULT.json](RESULT.json).
It never rewrites the receipt. Normal and optimized modes have explicit
checks rather than Python assertions. Replay takes a few seconds.

- Exact rational matrices and integer lattice coordinates independently check
  the determinant and target support; all eight raw characters and the joint
  first-order projector witness are checked.
- Every ordered triple of rank-one binary projectors at widths two and three
  is tested in `E_S(N1) E_(2S)(K) E_S(N2)`: 216 and 21,952 cases. Exactly
  12 and 196 have even endpoints; each contracts as claimed. A separate
  entry-wise polynomial-set engine checks all 216 width-two products.
- The block expansion and contraction are checked on 9,120 matrix-unit cases:
  every projector pair at widths two and three, and equal-projector pairs at
  width four. The labels `-3S,5S` test unequal odd labels and negative exponents.
- Both coefficientwise engines check the direct eight-call construction and
  a nine-call subdivision with separated `S` calls, at widths 4, 5 and 7,
  directly and with explicit free mixing. All 12 endpoints pass; extra dirty
  registers are restored. The nine-call profile differs from the excluded one.
- Controls detect a noncommuting middle, unequal normalized projectors, a
  single odd call, a non-idempotent, all nine single-call deletions, both
  `S->P` corruptions, and source-byte mutation. Positive controls include
  inverse-pair cancellation and a free middle map intertwining unequal
  projectors. CLI tests reject altered receipts and pins in normal and
  optimized mode and accept an isolated source export with an empty `PATH`.

The finite domains are exhaustive only as stated above. They are regression
checks for the displayed algebra, not a formal proof of its arbitrary-width
statement. Both implementations were prepared in this contribution; no
independent human review or proof-kernel verification is claimed.

Base: `721c03822c421b7f7fcbb2598993b947c4d88419`.
[SOURCES.json](SOURCES.json) pins the canonical model note, task catalogue and
selected record. The live model note has Git blob
`608a24af8bc3d27ee1554c94872601bb3a409f67` and SHA256
`fa3f0f951146caa5b1eb7b7417175eb7a380cae8674e4a470407517dac40f227`.
The pending PR6111 README is context only, pinned at the head above and blob
`98eb6718d0ae424c129cf08b186fd2a5593ca783`; it is not needed to run or prove
this result. No external download or predecessor code is needed for replay.

## Scope and cost gate

This is a changed-scope side result under `bit-new-register-model`; [TASK.json](TASK.json)
records the OS draw 19, diversification seed, three candidates, local claim,
overlap limitations and refresh decisions. PR1974's three-register rational
`3x3` theorem and PR2027's two-register nonabelian `GL3(F2)` census do not
cover this four-target rational `2x2` endpoint at arbitrary restored width.

The optimistic bill is already eight paid calls with all scalar mixing free,
equal to the direct endpoint cost. The proposed profile cannot realize even
that relaxed bill. No native address implementation, source-access schedule,
storage saving, recursive profile or physical caller is constructed, and no
conversion from formal calls to native cost is asserted. The selected
conditional result remains `781451/250000000`; its five inherited framework
assumptions are unchanged. No supplier or selected-certificate cold replay
is claimed or needed for this isolated algebraic result. `upstream/` is untouched.

## Open next questions

1. Which other eight-call survivors in PR6111 admit an index-two quotient
   with exactly two odd occurrences? This could prune its open list without
   searching scalar words. First extract each exact candidate lattice and
   character, contract only when the summed label is priced, and rerun
   support/rank conditions. This package does not classify those survivors.
2. What can replace two-use descent when four calls occupy the odd coset?
   The two cross blocks no longer isolate in the same way. A first step is
   a small exact four-odd-factor example with an even endpoint, including
   realizable subdivision controls. There is no claimed four-use reduction
   or justification for a larger search here.

## Credit

Prepared for **@CubeJerry** with substantial **OpenAI Codex** assistance;
new proof application, code and prose are Apache-2.0. The classical idempotent
block decomposition and dual-number rank method are not claimed as new.
Credit JosieElliston/Claude for PR6111's concrete unresolved candidate;
JoyboyBrian (PR6104) for the two-frame question; apoursh (PR6089) for the
one-frame work and subdivision motivation; Nick Petalas (PR2910) for the
determinant model note; Cinna Davis (PR2085/2112) for the endpoint and model;
Philippe Van Velzen for the earlier eight-call floor; and their retained BIT
lineage. The contribution resolves one pending example rather than repeating
their lower bounds or claiming a literature-priority result.
