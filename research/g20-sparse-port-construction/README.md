# Sparse bases for every G20 port

All 111 actual G20 line/complement interfaces have shorter explicit route
words. The eight coordinate lines need only a signed swap, or no operations.
The 103 four-coordinate lines use a three-butterfly tree. This replaces the
fixed dense bases in PR5801; it does not change the source projectors.

Under PR5805's single-cover contract, the 7,548 actual route markers use
**53,448 ADDs and 21,012 scales**, down from 202,640 and 73,916. Every
coefficient count decreases or stays zero. Thus the saving is strict for
**every positive assignment of the same coefficient-specific tariffs**.
The reduction is 202,096 local operations, or 25,666,192 named kernel calls
 times f squared in the declared N=127f cover. No common unit price is assumed.

The package also emits a determinant-one, scale-free alternative: 53,448
ADDs, of which 21,012 have coefficient plus or minus 1/4. It wins over the
tree exactly when

```
C_ADD(1/4) + C_ADD(-1/4)
  < C_ADD(1) + C_ADD(-1) + C_SCALE(2) + C_SCALE(1/2).
```

This condition compares the complete words in both directions. It is the
same for each four-coordinate port. Choose the cheaper word when the
physical tariff is known; both words meet the exact same interface.

## Construction and proof

A signed swap uses three ADDs. It sends e_0 to plus or minus e_p, where p
is the first support index. A line does not prescribe its overall sign.
For four support indices a,b,c,d, let s_i be the desired sign relative to a.
Apply rotations on (a,c), then (a,b) and (c,d). Each rotation is

```
x <- x - s*y; y <- 2*y; y <- y + s*x.
```

Its matrix is [[1,-s],[s,1]]. The first rotation creates two equal-magnitude
entries; the last two create the required four. The latter two disjoint
rotations multiply the Euclidean metric on this support by 2. The first
rotation therefore leaves its two source columns orthogonal, and all other
columns remain orthogonal to the desired line. Three pair rotations are
minimal in this spreading-tree family: each can increase support by at most
one. The earlier four-butterfly Walsh choice is unnecessary. No global
minimum over arbitrary rational bases or elementary words is claimed.

For the scale-free word, write v=(1,s_b,s_c,s_d) on the support. First use
three lower shears L with first column v. Then use three upper shears U
with coefficient -s_j/4 from the first coordinate to coordinate j.
The other columns of LU are e_j - s_j*v/4, which are orthogonal to v.
Both shear products have determinant one. The same signed swap places the
central coordinate. This word requires no scale primitive.

The emitted words use RIGHT products. They are derived from the column
construction with the correct factor order. Every inverse is the literal
reverse-and-inverse word. For each source projector P and central Q, the
checker verifies P W = W Q and W^-1 P W = Q over exact rationals. It checks
all complement columns, not just the first vector. In physical address order
it also checks D^-1 H_P D = H_Q, with D=diag(W,J W J) and J the eight-axis
reversal. A second dense elementary product checks the row-word executor.
These are algebraic implementation checks, not independent human review.

## Actual incidence and limits

The frozen 317,004-event source stream is joined to all core boundaries and
owner banks. Each port uses each direction 34 times. ENTRY uses W^-1 and
RETURN uses W under the declared cover update h=gS. Return restores every
arbitrary cover entry. There is one cover word per marker; no extra factor
for paired address halves is charged. The eight active axes can be embedded
at each source stage ordinal and tensored with I_f; other axes are fixed.

The source interface and native claims are retained dependencies. This
package changes the basis, not target ranks or the paid query profile. The
source modulus guard gcd(q,12)=1 and all five framework assumptions remain.
Physical head placement, coefficient preparation, tape/ROW implementation,
cache COPY/CLEAR, carry, low-type commit, padding, borrowing, compiler and
complete multiplication costs remain open. The positive symbolic tariff
saving is not an admitted BIT saving or a new kappa. The selected frontier
is unchanged. The old global word has not been recompiled with these bases.

## Reproduction and evidence

Python 3.12 and the standard library suffice:

```sh
python3.12 -B scripts/research_package.py --package research/g20-sparse-port-construction
```

The registered commands run under normal and optimized Python. The direct
verifier is Git-free. It authenticates all source data, regenerates both
complete catalogues, checks 222 port constructions and the exact marker join,
then compares the full RESULT.json. Controls reject a wrong basis with a
coherent inverse, an odd scale and a wrong route owner. SOURCES.json pins
PR5798, PR5801 and PR5805 inputs. Frozen source bytes are unchanged.

## Open next questions

Implement one named physical ROW kernel and use its actual tariff to choose
between the two words. Bind the complete physical route, including the cache,
carry, type, padding and restoration terms. The first finite fixture is port
8 and its paired 16-coordinate action. These missing costs block a complete
BIT/outer claim. TASK.json records this handoff.

## Credit

Ali Romman with substantial OpenAI Codex assistance; no subagents. ToikY's
PR5801 supplies the dense-word comparator; PR5805 supplies the single-cover
contract and event join. PR5798 supplies the exact interfaces. Retain
Dugongue, ai-nanachi and all G20/native/ROW predecessor credits in NOTICE.
The tree and shear identities are standard linear algebra. New work is their
source-wide construction, exact verification and complete tariff comparison.
Apache-2.0. Claim and handoff: Discussion5804.
