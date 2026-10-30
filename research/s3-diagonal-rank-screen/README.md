# Sharp floors for the 216 diagonal S3 targets

**Finite screen in one nonabelian alphabet; no new kappa.** The selected
record is unchanged.

## Scope

Chooser seed `69b1df962b206506adae7d9b1954dd8f` drew `r437-carrier-integration`
on priority revision 7, base `12fa8c5c844be21bfefb38a19503fbd867a11244`.
That card's compiler, caller and stock obligations are already open in #4176
and #4183, and #4147 already gives the reverse coefficient 1123650. This
package takes the next suggestion, `bit-new-register-model`, at the screening
question left by open #3893.

The paid alphabet is the same one: labels `s = (1 2)` and `t = (2 3)`, and
the 28 rank-one idempotents are not needed for the coordinate words below.
The two-dimensional representation is the one stated in that PR,

```text
rho(s) = [[1, 1], [0, 1]],    rho(t) = [[1, 0], [1, 1]].
```

A coordinate word writes one register at a time. Its length is the sum of the
generator lengths. The representation rank of a diagonal target is the sum of
`rank(rho(g) + I)`. Equality makes that coordinate word sharp.

## What is established

Generator length and represented rank agree on five of the six group elements.
They disagree only on the transposition `(1 3) = (2, 1, 0)`, which has length
3 and represented rank 1.

Eight diagonal S3 targets, those whose three labels all lie in the two length-two elements, have representation rank 6 and a six-call coordinate word. One hundred twenty-five of the 216 diagonal targets match in the same way.

The other 91 targets each contain `(1 3)`. Their generator bill exceeds the
rank bound by 2 for every copy of that label, so this comparison does not
prove those bills sharp. The published target `diag(s, t, st)` remains one of
the 36 sharp floors of 4; its four-call word is rechecked here and is not
claimed as new. The new maximum is 6, on exactly the eight targets with every
label in `{st, ts}`.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/s3-diagonal-rank-screen
```

Expected marker: `PASS_S3_DIAGONAL_RANK_SCREEN matched=125 floor6=8 gap=91`.

## Limits

No shared-word search for `(1 3)`, no native implementation, and no transfer
to the rational-frame three-register theorem. The selected baseline was not
run in this partial checkout. No selected-frontier change is claimed.

## Open next questions

Can a shared word shorter than length 3 write `(1 3)` on one register in this
same paid alphabet? A one-register word cannot, because the reduced generator
length is 3. A first step is to allow one specified scratch register and
search length 2. No such scratch contract is pinned here.

## Credit

The alphabet, representation and four-call target are from the open package
`research/bit-s3-three-register-rank-target-seed57b2` (#3893). The
three-register rational-frame bound is the catalogue starting point and is
not replayed. Riquelme Soares (@hevlyo), with substantial AI assistance in
the classification and write-up. Apache-2.0. No independent human review is
claimed.
