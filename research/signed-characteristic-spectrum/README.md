# Exact signed-connector tariffs over coefficient rings

This is a scoped proof with a finite certificate. For the canonical signed
three-source connector below, the minimum is **12 calls in characteristic two,
13 in characteristic three, and 14 in characteristic zero or at least four**.
The statement covers every nonzero unital coefficient ring, including composite
characteristics and rings with zero divisors. It is uniform over finite free
modules, arbitrary fixed linear maps and arbitrary dirty data.

The new result transfers the characteristic-zero obstruction to every
characteristic at least four and proves the exact fixed-price envelope there.
It also lifts the characteristic-three construction from F3 to every ring of
characteristic three. The predecessor words and obstruction remain credited.
There is no new kappa, supplier admission or complete multiplication theorem.

## Interface and theorem

Let R be a nonzero unital ring. Use seven distinct arrays x0,x1,x2,y0,y1,y2,z
in a finite free R-module of any positive rank. The six fixed R-linear maps
Ai,Bj need not commute or be invertible. The only permitted operations are

```text
Bj^s: z  += s Bj(xj)
Ai^s: yi += s Ai(z)                  s = +1 or -1
```

The word is independent of data and of the particular maps. Sources are immutable,
outputs are not read, and z must restore. Initial outputs and z are arbitrary.
Every complete call preserves its source and other data, restores private scratch
and returns required heads. No scalar multipliers, transfers, extra connectors,
role changes, direct products or other data operations are available. A minus
sign subtracts an increment; it does not invert Ai or Bj.

The required final update is

```text
M = [[1,1,1], [1,1,-1], [1,-1,0]]
yi += sum_j Mij Ai(Bj(xj));   xj and z unchanged.
```

A word must work for every choice of arrays and maps over R. Specialized maps
or a particular module on which R acts nonfaithfully can have cheaper words;
those are not this uniform problem. The zero ring is excluded.

Let cF > 0 be the complete fixed price of operator F, equal for its two signs,
and let S be the sum of all six prices. Then the exact minimum query bill is

```text
char R = 2:             2 S
char R = 3:             2 S + min_F cF
char R = 0 or >= 4:     2 S + 2 min_F cF.
```

Setting all prices to one gives the three call minima above. The prices include
child execution, source/coefficient access, private restoration, required routing,
frame adaptation and head returns. Admission, coefficient preparation and root
selection/control remain additional costs. If those depend on the word, this
formula is the query bill, not an optimum for the combined implementation.

## Proof

Write u_j = Bj(xj). After the source calls at a boundary t,

```text
z = z_initial + sum_j q_t[j] u_j.
```

For output i, let d_i be the signed sum of its readouts and let
C_ij = sum over its readouts at t of s*q_t[j]. Linearity gives exactly

```text
yi_final = yi_initial + d_i Ai(z_initial) + sum_j C_ij Ai(Bj(xj)).
```

Thus integer coefficient identities q_final=0, d=0, C=M, reduced in R,
are sufficient. They are also necessary for uniform correctness: use the free
rank-one module R, identity maps, isolate one initial source or z, and set
unwanted maps to zero. The map Z -> R, n -> n*1_R, has kernel zero in
characteristic zero and cZ in finite characteristic c. No division, field
hypothesis, lack of torsion elsewhere in R, or absence of zero divisors is used.

**At least two calls per operator.** Every row and column of M is nonzero.
An absent Bj cannot contribute its column and one occurrence cannot restore z.
An absent Ai cannot update its row and one occurrence cannot cancel initial z.
All six operators therefore occur at least twice in every characteristic.

**The 12-call obstruction transfers without modular aliasing.** In characteristic
zero or at least three, two signed calls can have signed sum zero only when their
signs are opposite. At exactly 12 calls each source therefore enters once and
leaves once, so q_t[j] is either zero or one fixed sign epsilon_j. Each Ai has
two opposite readouts, and its desired row must be a signed difference between
two visited q vectors. Every coordinate of that difference is in {-1,0,1}.
The difference from a required entry in {-1,0,1} is in {-2,-1,0,1,2}.
It vanishes in R exactly when it is the integer zero for all characteristics
zero or at least three. Consequently a 12-call word here would be a 12-call
word for the same integer target in characteristic zero.

Ross Richardson's [PR944](https://github.com/CrocSwap/integer-mult-bounds/pull/944)
proves that no such paired path covers all three rows. This is an explicitly
used predecessor theorem, not a new obstruction census. The graph proof in
[the retained rigidity note](../nonunit-signed-connector-rigidity/PROOF.md)
is another account of that same obstruction. This transfer excludes 12 calls
in every characteristic zero or at least three. In characteristic two the two
signs coincide and the no-alias implication fails, as it should.

**Characteristic three is the only three-occurrence exception.** Three signs
sum to one of -3,-1,1,3. This sum cannot vanish in a nonzero ring of characteristic
zero or at least four. In those characteristics every operator's count is either
two or at least four. Since all counts equal to two was excluded, some operator
has at least four calls. This proves both the 14-call lower bound and the
weighted bound 2S + 2 min_F cF for words of any length. In particular, the proof
does not assume all restoring counts are even in finite characteristic.

martinxxx9's [PR1088](https://github.com/CrocSwap/integer-mult-bounds/pull/1088)
supplies six integer 14-call words, each repeating a chosen operator four times
and every other operator twice. Their coefficient identities hold over Z,
so they hold over every R. Choosing a cheapest operator attains the bound.
This proves the new characteristic-at-least-four result, including all composite
characteristics, without an infinite search over moduli.

In characteristic three, the support bound and 12-call exclusion imply that
some operator pays at least one extra call. Sagar Thakrar's
[PR1349](https://github.com/CrocSwap/integer-mult-bounds/pull/1349) supplies a
13-call word with any chosen operator tripled. Its coefficient residuals are
integer multiples of three, so it works over every characteristic-three ring,
including F3[epsilon]/(epsilon^2). This proves 2S + min_F cF beyond F3 itself.
The word and the F3 optimum are predecessor results; the ring lift is the extension.

In characteristic two the following 12-call word attains two calls of each
operator. At its positive reads the source prefixes are (1,1,0) and (1,1,1).
The required signs +1 and -1 agree in R, so these are exactly the target rows.
The first reads subtract the independent initial dirt and the final source
calls restore z.

```text
A0- A1- A2- B0+ B1+ A2+ B2+ A0+ A1+ B0- B1- B2-
```

The binary support-floor phenomenon is already part of PR944/PR934. This word
makes the characteristic boundary explicit; it is not claimed as a new binary
connector construction. Together these cases prove the stated spectrum.

## Finite evidence and reproduction

From the repository root, use CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/signed-characteristic-spectrum/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/signed-characteristic-spectrum/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/signed-characteristic-spectrum
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/signed-characteristic-spectrum --check-source-history
```

Expected scientific marker: `PASS_SIGNED_CHARACTERISTIC_SPECTRUM`.
The verifier checks 238 short signed-count cases, 10,935 no-alias cases and
24 exact rational price cases. The 13 literal witnesses comprise the binary
word and the six credited repairs in each of the other cases.

A separate dense interpreter executes 2,190 word/input cases. Each checks the
forward action, inverse action and dirty round trip on all 28 scalar basis
inputs plus two dense dirty inputs. The matrices represent two-dimensional
modules over (Z/cZ)[epsilon]/(epsilon^2), or Z[epsilon]/(epsilon^2) at c=0.
The tested characteristics are 0,2,3,4,5,6,7,8,9,10,12,15,16. The operators
include noncommuting maps. This exercises nonfield rings and independent dirty
coordinates rather than treating scalar identity maps as the only realization.

The 199 controls consist of 84 query omissions and 84 sign flips in the six
14-call words over characteristic four, 30 uses of the six ternary words in
wrong characteristics, and the binary word incorrectly used in characteristic
three. Every control fails its named target identity. No count includes an
unexamined failure classification.

[RESULT.json](RESULT.json) is generated from these checks and binds every
package file other than itself and all four live predecessor inputs by SHA256.
An optional `--write-receipt /new/external/path.json` generates a fresh candidate
outside the checkout and refuses overwrite. The default replay compares the
recomputed receipt with the committed one. No predecessor executable is imported.

## Limits and implementation obligations

The universal statement is the written scoped proof with the explicitly cited
PR944 paired-path obstruction. Executed modular cases corroborate the extension;
they do not enumerate every ring or certify a complete multiplication theorem.
Independent human and formal proof-kernel review are unclaimed. No new supplier,
selected cold replay, physical port installation, stock, precision, fixed-tape
compiler or outer analytic admission is supplied. The selected frontier is unchanged.

The Python implementation uses dynamic allocation with finite fixed domains:
words have at most 14 queries, banks have 28 scalar coordinates, there are 30
input banks, 13 characteristics and 13 witnesses. All loops have finite explicit
bounds or iterate authenticated, bounded package files. Each function is under
60 lines. Explicit exceptions enforce the invariants even under `-O`.
This is the managed-runtime deviation from fixed preallocation in Power of Ten;
there is no recursive execution or child process. Standard-library execution
with warnings as errors is the registered diagnostic surface.

## Open next questions

1. Determine the exact characteristic-dependent tariff when the two signs of
   an operator have different prices. This matters because a physical interface
   can price inverse calls differently. Start with the six credited repairs and
   a count-vector lower bound. Additional restoring words may be needed, and
   the equal-sign envelope here does not settle that problem.
2. Find a source-bound supplier seam with this exact signed 3x3 demand and all
   six complete prices. Begin with one literal 14-call word and a full port,
   frame, restoration and precision ledger. No compatible selected caller has
   been identified here, so no downstream kappa claim follows.

## Credit and provenance

This extension was produced by Nick Petalas. Ross Richardson supplies PR944's
characteristic-zero target, interface and obstruction and PR934's binary
predecessor. martinxxx9 supplies PR1088's six weighted repair words. Sagar
Thakrar supplies PR1349's F3 words and minimum. Charles Bethin's retained
nonunit rigidity note supplies the cited alternate graph proof of the inherited
obstruction.
CubeJerry/PR889 and Chafik Boukhalfa/PR628 retain the signed fanout and dirty
product-commutator lineage in the predecessor notices. No predecessor credit
line or package is changed. Apache-2.0.

The scientific base is `12fa8c5c844be21bfefb38a19503fbd867a11244`, priority
revision 7. The earlier [released characteristic handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19080030)
proposed the short signed-count observation but published no verified result.
This package completes that question and extends the coefficient domain to
unital rings. Its [claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19080558)
was posted before the proof package was developed. Sources are pinned in
[SOURCES.json](SOURCES.json); [TASK.json](TASK.json) records the scope change
from an added operation to a coefficient-domain theorem.
