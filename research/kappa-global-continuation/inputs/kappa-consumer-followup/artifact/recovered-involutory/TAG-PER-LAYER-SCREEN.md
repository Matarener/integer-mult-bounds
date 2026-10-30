# A tag bit per tensor layer: volume and complete-cost screen

The proposed lift needs one independent tag coordinate in each of lambda tensor
layers. A single global bank label supplies only one bit. Replacing the required
lambda bits by that one bit is not a valid all-size tensor identity.

## Fresh tags

Two full input banks have volume 2F. An uncompressed space with one new tag bit
per layer has volume 2^lambda F, so its volume relative to those two banks is
2^(lambda-1). A two-child implementation in which both C_(7 lambda) children
scan that expanded space costs, relative to two original C_(8 lambda) calls,

\[
2^\lambda\frac{H_7(b)}{H_8(b)},\qquad
H_r(b)=r(73/r)^b.
\]

This exceeds 7/4 already at lambda=1 for 0<b<1, and then grows exponentially.
An implementation touching only selected sectors needs a separate exact
supported-domain lowering; the dense invoice cannot be charged as if the
added address space were absent.

The authenticated PR3734 package uses 323069 physical families for 1321920
literal roles. The local word has 91 owned cleanup buffers. These are finite
counts independent of lambda; the helpers also carry arbitrary state that must
be restored. Even the unrealistic grant that every family is blank cannot
absorb an unbounded 2^lambda expansion. No unpriced blank address dimension is
provided by that inventory.

## Reusing a spectator coordinate

Using an existing address coordinate as the tag avoids new volume, but it uses
an existing payload coordinate containing arbitrary input. Every sector must
remain correct. Two C_(7 lambda) passes over the same full input volume cost
2H7, which exceeds one H8 by a factor greater than 7/4. Relabelling an existing
coordinate does not turn either full-volume pass into a half-volume pass.

The ordinary complete split is

\[
C_{8\lambda}=C_{7\lambda}\otimes C_\lambda.
\]

Its full-volume recursive cost is H7+H1. Since 0<1-b<1,

\[
7^{1-b}+1>8^{1-b},
\]

so this complete split is strictly more expensive than H8. Implementing the
remaining C_lambda directly instead takes order lambda scalar work per
coefficient, which cannot be hidden in a fixed number of linear scans in a
strict logarithmic-exponent improvement.

## Conditional half-volume gates

A finite diagram may contain a transform selected by a tag bit, with operator
I direct_sum C7. Its tensor lift is

\[
(I\oplus C_7)^{\otimes\lambda}
=\bigoplus_{s\in\{0,1\}^{\lambda}} C_{7|s|},
\]

with the relevant identity spectators retained. There are binomially many
strata. This is not one C_(7 lambda) selected by a global half-space. A scalar
butterfly on a global bank label is cheap at one layer; if it acts on every new
tag bit after tensorization it becomes the missing C_lambda operation and
requires its own cost.

The JSON companion records numerical illustrations at the user's provisional
b=0.001730578437266246818740. Here H7+H1-H8 is approximately
0.005242935240698832, and 2H7/H8 is approximately 1.750404448189823075.
The inequalities above, rather than these decimal illustrations, establish
the sign for the whole interval 0<b<1.

## Scope

These calculations exclude the specified dense tag expansion, the two
full-volume H7 replacement, and the ordinary H7+H1 split as sources of a
saving. They do not exclude every typed partial-observation contract. A new
candidate must give its literal finite operator, all tag-sector semantics,
tensor lift, supported-domain footprint, and total child-volume invoice.
No such cheaper complete lift was constructed here.

The source family and role counts are in the recovered authenticated
`pr3734/PROOF.md`; the buffer count is checked from both canonical modern
words by `modern_native_component.py`. The moment convention is the retained
`research/rank7-coupled-586-588-carrier-fold/tools/root.py` convention. New
screen by OpenAI Codex under the user's direction; Apache-2.0.
