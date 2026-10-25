# Signed-connector tariff with sign-dependent prices

This is a scoped proof with a finite certificate. It answers the first open
question of [#4233](https://github.com/CrocSwap/integer-mult-bounds/pull/4233):
the exact minimum bill of the canonical signed three-source connector when the
two signs of an operator have different prices, over every nonzero unital
coefficient ring. The new ingredient is an explicit family of (10+c)-call words
in characteristic c, one for each operator, in which that operator is called c
times with one sign. There is no new kappa, supplier admission or complete
multiplication theorem.

## Interface

This is the interface of #4233 and Ross Richardson's
[PR944](https://github.com/CrocSwap/integer-mult-bounds/pull/944). Let R be a
nonzero unital ring of characteristic c (c = 0 or c >= 2). Seven distinct arrays
x0,x1,x2,y0,y1,y2,z live in a finite free R-module; the six R-linear maps Ai, Bj
are arbitrary and need not commute. The only operations are

```text
Bj^s: z  += s Bj(xj)
Ai^s: yi += s Ai(z)                  s = +1 or -1
```

Sources are immutable, outputs are not read, z must restore, and initial outputs
and z are arbitrary. The word is fixed in advance and must give

```text
M = [[1,1,1], [1,1,-1], [1,-1,0]]
yi += sum_j Mij Ai(Bj(xj));   xj and z unchanged
```

for every module, choice of maps and dirty data over R.

Each operator F has two positive complete prices, p_F^+ for F^{+1} and p_F^- for
F^{-1}. They may differ. Write

```text
sigma_F = p_F^+ + p_F^-,     mu_F = min(p_F^+, p_F^-).
```

## Theorem

The exact minimum bill is

```text
c = 0:    sum_F sigma_F + min_F sigma_F
c >= 2:   sum_F b_F + min_F (u_F - b_F),   where
          b_F = min(sigma_F, c mu_F),   u_F = min(2 sigma_F, c mu_F).
```

Special cases:

- c = 2 gives 2 sum_F mu_F, because c mu_F <= sigma_F always.
- With equal sign prices p_F, it gives #4233's 2S + min p in characteristic
  three and 2S + 2 min p in characteristic zero or at least four.
- With every p_F^- huge, it gives sum_F c p_F^+ for every c >= 2. In
  characteristic zero there is no word without minus calls.

Prices exclude admission, coefficient preparation and root control. If those
depend on the word, this formula is the query bill, not a combined optimum.

Uniform prices p^+ = 1 and p^- = 3 give the following bills, all checked by
`verify.py`:

| characteristic | 0 | 3 | 4 | 5 | 8 |
|---|---:|---:|---:|---:|---:|
| bill | 28 | 18 | 24 | 25 | 28 |
| optimal profile | one (2,2) | all (3,0) | all (4,0) | one (5,0) | one (2,2) |

## Proof

**Count profiles.** Let operator F occur n_F^+ times with sign +1 and n_F^-
times with sign -1. #4233's coefficient identities are necessary and sufficient
for uniform correctness: use the free module R, identity maps, and one isolated
initial array. They give q_final[j] = n^+ - n^- = 0 for Bj and the dirt
coefficient n^+ - n^- = 0 for Ai, in R. Hence n_F^+ ≡ n_F^- (mod c), and
n_F^+ = n_F^- when c = 0. #4233's support lemma gives n_F^+ + n_F^- >= 2.

**Dominance.** Let (a,b) be a feasible profile other than (1,1). If a = b, then
a >= 2 and (a,b) dominates (2,2) componentwise. If a ≠ b, then c ≥ 2,
|a-b| >= c and the larger count is at least c, so (a,b) dominates (c,0) or
(0,c). A profile's cost is monotone in its counts, so it costs at least

```text
(1,1): sigma_F,   (2,2): 2 sigma_F,   (c,0) or (0,c): >= c mu_F.
```

So every operator costs at least b_F, and an operator with profile other than
(1,1) costs at least u_F.

**The all-(1,1) profile is impossible when c = 0 or c >= 3.** Every operator
then has one call of each sign, so this is a 12-call word with each source
entering and leaving once. #4233's no-aliasing argument shows that the
coefficient identities then hold over Z: each relevant difference lies in
{-2,...,2}, and no nonzero element of that range is 0 mod c. PR944 proves that no
such integer word exists. `verify.py` independently re-enumerates all 720
paired source paths as a control.

**Lower bound.** Let c = 0 or c >= 3. Some operator F has a profile other than
(1,1), so the bill is at least sum_{G≠F} b_G + u_F >= sum b + min(u - b). For
c = 0, b = sigma and u = 2 sigma. For c = 2, u = b, so sum b is the bound. The
argument applies to words of any length.

**Conversion lemma (new).** In characteristic c >= 2, (c-1) consecutive copies
of F^{s} act exactly as one F^{-s}. No read or source call lies between them,
so the action is unchanged at every other boundary. Replacing the single minus
call of a (1,1) operator by c-1 plus calls gives profile (c,0). Replacing the
plus call gives (0,c). Negating every sign also preserves M: q changes sign and
so does every read sign. This turns (c,0) into (0,c) and leaves (1,1) operators
as they are.

**Anchored words (new).** For every operator F and every c >= 2, the following
template, with `X+*` meaning X+ repeated c-2 times, has F at profile (c,0) and
all other operators at (1,1). Its length is 10 + c.

```text
B0: B1- A1- A2+ B2- A0- B1+ B0+ A1+ B2+ A0+ B0+* A2- B0+
B1: B1+ A0+ B1+* A2+ B0- A1- B1+ A2- B2- A0- B0+ A1+ B2+
B2: A2- B1- B2+ A1- B2+* A0- B0+ B2+ A2+ B1+ A1+ A0+ B0-
A0: A0+* B2+ A0+ A1- B2- B1+ A2- B0+ A0+ A1+ B1- A2+ B0-
A1: A1+ B2+ A1+* B0+ A2+ B1+ A1+ A0+ B0- A2- B2- B1- A0-
A2: A2+ A1- B2- A0- B0+ B1+ A1+ B2+ A2+ A0+ B0- A2+* B1-
```

Every coefficient is affine in c, so the template is correct in every
characteristic c >= 2 exactly when the constant part of each residual is zero.
`verify.py` checks this symbolically. For B0, the reads give rows
(1,0,0) - (0,-1,-1) = (1,1,1), (1,0,-1) - (0,-1,0) = (1,1,-1) and
(0,-1,0) - (c-1,0,0) = (1-c,-1,0) ≡ (1,-1,0). For an output, for example A0,
c-2 reads at the clean start plus reads at (0,0,1) and (1,1,0) sum to (1,1,1).
The c reads cancel the dirt because c ≡ 0. At c = 3 these are 13-call words with
a tripled operator, the same length as Sagar Thakrar's PR1349 words.

**Upper bound.** Let c >= 2.

1. If some F has c mu_F <= sigma_F, start from F's template. Flip all signs when
   p_F^- < p_F^+. Then convert every other operator G with c mu_G <= sigma_G to
   its cheaper sign. The bill is sum b.
2. Otherwise every b is sigma. Let F minimize u_F - sigma_F. If 2 sigma_F <= c
   mu_F, use martinxxx9's PR1088 14-call integer word that repeats F as (2,2).
   It is correct over every ring. Otherwise use F's template, with signs flipped
   when needed.

When c = 0, use PR1088's word for the F with the smallest sigma_F. Each
construction attains the lower bound, which proves the theorem.

## Finite evidence and reproduction

From the repository root, with CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/signed-sign-price-envelope/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/signed-sign-price-envelope/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/signed-sign-price-envelope
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/signed-sign-price-envelope --check-source-history
```

Expected marker: `PASS_SIGNED_SIGN_PRICE_ENVELOPE`. Each verifier run takes
about 6 seconds and checks the following:

- **468 template cases.** The six templates and their global flips are checked
  for each c in 2..40: profile, length 10 + c, and correctness modulo c. The
  symbolic affine residual of each template is also checked to be zero.
- **69,984 conversion cases.** For c in 2..9, the base words are the six
  templates and the six PR1088 words. Every assignment of keep, (c,0) or (0,c)
  to their (1,1) operators gives a correct word.
- **720 paired source paths.** A control re-enumerates PR944's obstruction:
  no word with each operator once per sign meets the integer target.
- **793 price cases.** There are 61 price vectors in 13 characteristics
  (0, 2..10, 12, 15, 16). Each case compares the closed formula with a direct
  optimum over count profiles and builds a literal word, which must be correct
  and cost exactly the formula. The vectors are unit prices, one heavy sign, a
  uniformly heavy minus sign, one structured vector and 40 seeded random
  rational vectors. All four construction branches occur.
- **4,320 dense cases.** Templates and flips run on 28 basis inputs and two dense
  dirty banks over (Z/cZ)[epsilon]/(epsilon^2), for the 12 nonzero listed
  characteristics, with noncommuting maps. Each case checks the forward action and the
  dirty round trip. The dense code is adapted from #4233's verifier.
- **798 negative controls.** Deleting any one query from a template, for c in
  3..9, breaks it. So does running it in characteristic 0, c+1 or 2c+1.

[RESULT.json](RESULT.json) is generated by `--write-receipt /new/path/outside`.
It binds every other package file and both live inputs by SHA256. The default
run recomputes the receipt and compares it with the committed one.

## Limits and obligations

The all-characteristic statement is the written proof above. It relies on
PR944's integer obstruction, and the verifier repeats that obstruction only as a
720-path control. The finite cases corroborate the proof but do not enumerate
all rings. The verifier checks the count-profile reduction only on the listed
price vectors. #4233 is an open, unmerged PR by the same author. This package
restates and uses its necessity, support and no-aliasing lemmas, and does not
import its files. No independent human or formal proof-kernel review, supplier
caller, physical port installation, stock, precision or fixed-tape compiler
admission is supplied. The selected frontier is unchanged.

Power of Ten: Python allocates dynamically, but every domain is finite and
explicit. Words have at most 196 queries, c is at most 40 and there are 61 price
vectors. There is no recursion and no child process. Each function is under 60
lines, and explicit exceptions keep every invariant active under `-O`.

## Open next questions

1. Determine the sign-dependent envelope for the other members of PR1088's
   288-matrix signed/permuted orbit. Row and column sign changes move minus
   prices between operators, so the anchored templates must be redone for each
   orbit class.
2. Locate a physical caller in which inverse child calls really cost more than
   forward calls, and price one anchored word with every port, frame and
   restoration charge. The (c,0) words show that in characteristic c >= 3 a
   connector can avoid inverse calls entirely, at c calls per operator.

## Credit and provenance

Produced by Nick Petalas. Ross Richardson's PR944 supplies the interface, the
canonical target and the paired-path obstruction. martinxxx9's PR1088 supplies
the six (2,2) repair words, read from its committed certificate. Sagar Thakrar's
PR1349 supplies the characteristic-three 13-call predecessor. #4233 supplies
the equal-sign envelope, the coefficient-ring lemmas and the open question
answered here. The new parts are the conversion lemma, the six anchored template
families, the dominance reduction and the closed envelope.

The scientific base is `12fa8c5c844be21bfefb38a19503fbd867a11244`, priority
revision 7. The [claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19081069)
was posted before the package was written. Sources are pinned in
[SOURCES.json](SOURCES.json). Apache-2.0.
