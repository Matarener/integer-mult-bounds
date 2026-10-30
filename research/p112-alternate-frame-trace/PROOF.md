# A trace obstruction for every split of the alternate frame

**Result.** The alternate common frame defined by anchor axes `[6,1,11]`
cannot extend the fixed asymmetric anchor to groups3 and4 while satisfying
all mandatory whole-group tariffs. This holds for every rational split of
that frame, including all rank strata and dense coefficients. The three
self-rectangle caps with masks34,22,28 imply the contradiction `0=-4`.

This finishes the interrupted October18 argument. It does not rule out other
common source/reader complements, other anchor matrices, or all rational
decoders. It changes neither the334 baseline nor the296 target.

## Frozen data and precise scope

Use the ordered physical groups `[1,2,27,28,3,4]`, indexed from zero when
forming subset masks. `FIXTURE.json` defines the first four groups' explicit
12 by12 asymmetric anchor A. This is new local research data, not a published
predecessor theorem. The verifier checks its rank8, four own-group identities,
and all225 nonempty anchor rectangle inequalities against the pinned P112
physical labels. It also regenerates the complete saturated-rectangle flags
and verifies that the independent replay's retained flag equations span the
same constraints. The old local receipt hashes are provenance only.

Factor the rank-eight anchor as `A=UV` by its first independent row/column
minor and append a zero ninth coordinate. Take H0 to be the span of source
rows6,1,11 of U and K0 the span of reader columns6,1,11 of V, in that order.
Their pairing is I3. These are group27 axis0, group1 axis1, and group28 axis2.
The combined new-pair reader space is `ker H0`; its source kernel is K0.
They are complementary. Let X be the script's exact basis matrix for
`ker H0`; the first six rows of `[X K0]^-1` form Y, so `YX=I6`.

The theorem concerns every decomposition of this fixed combined pair into
two three-dimensional groups with own combined block I6. A simultaneous
change of the six combined coordinates is harmless. It does not vary H0 or
K0. The result also does not presume a rank-preserving lift of the entire
physical binary matroid.

The three authenticated physical caps are:

| Mask | Physical groups | Self-rectangle rank cap |
|---:|---|---:|
|34|2,4|4|
|22|2,27,3|6|
|28|27,28,3|7|

## All admissible projectors, with no omitted boundary case

Saturated anchor rectangles impose one reader covector and one source vector
on each new group. The verifier regenerates these flags from every anchor
rectangle and the actual binary tariffs. In the combined six-dimensional
coordinates, write them as `a3,a4` and `b3,b4`. Their pairing is

```
       b3  b4
a3     -2   0
a4      0   1 .
```

Let P be the reader projector onto group3 along group4, with the dual source
splitting. Own-block I6 implies `P^2=P` and `rank P=3`. The flags require

```
a3 P=0,   P b3=0,   a4 P=a4,   P b4=b4.
```

Use the basis `[b4, basis(ker a3 intersect ker a4), b3]`. The middle space has
dimension four. The four flag equations fix the first row and column of P
to those of the identity, and its last row and column to zero. Thus the
complete family is

```
P = diag(1,Q,0),     Q^2=Q,     rank Q=2,
```

with Q an arbitrary rational4 by4 matrix. Conversely every such Q yields
the required flags and rank-three projector. This step uses no coordinate
patch, nonzero parameter assumption, symmetry, or coefficient restriction.

After the same basis change, let L and R be the anchor source and reader
frames in these six coordinates. They are retained literally in the receipt.

## Cap34: a complete rank-one parameterization

Let B denote physical group2, let `E=diag(1,0,0)`, and put

```
A3 = Q[0:3,0:3],
T  = A3 diag(1/2,1,1),
B1 = E+T.
```

The literal frames give `L_B P R_B=T` and `L_B R_B=I3-E`. Group4 uses the
projector `I6-P`. Eliminating its own I3 block in the mask34 self rectangle
therefore gives rank `3+rank B1`. Cap34 is exactly `rank B1<=1`.

Over Q every matrix of rank at most one is `B1=u v^t`, including the zero
matrix. This is an exact parameterization, not a sampled family. Set

```
r = (B1)00,       s = (B1)11+(B1)22.
```

## Cap22 and the complementary projector minor

Let C denote group27. Eliminate group3's own I3 block in the mask22 self
rectangle. Subtract the B block rows from the C block rows, and then the B
block columns from the C block columns. Two rows and columns become zero.
The remaining four by four matrix is

```
S4 = [ I3-T     T e0  ]
     [ e0^t T   -T00  ].
```

Hence cap22 implies `det S4=0`. With `B1=u v^t`, exact polynomial expansion
gives

```
g22 := det S4 = 1-r-s.
```

Since Q is a rank-two idempotent, `I4-Q` also has rank two. Its top-three
principal minor must vanish. Using
`A3=(B1-E)diag(2,1,1)`, the rank-one determinant identity gives

```
gI := det(I3-A3) = 3-2r-3s = 0.
```

In particular these two equations force `r=0,s=1`. Therefore
`Q00=-2`, `Q11+Q22=1`, and, since `trace Q=2`, `Q33=3`.

## Cap28: the required trace is zero

Groups27 and28 form an anchor own block I6. Put
`Z=R_{27,28} L_{27,28}` in the six combined-pair coordinates. Its first row
and column vanish. Its middle four by four block is

```
W = diag(3/2,1,1,0).
```

The only remaining entries of Z touch the last coordinate, which P kills.
Consequently exact symbolic multiplication gives

```
P-PZP = diag(1, Q-QWQ, 0).
```

For completeness, factor `P=F G`, where F is an image basis and `GF=I3`.
Eliminating the anchor I6 block from mask28 leaves `I3-GZF`. Multiplication
by the injective F and surjective G preserves its rank and yields `P-PZP`.
Thus the mask28 rank is

```
6 + rank(P-PZP) = 7 + rank(Q-QWQ).
```

Its cap seven forces `QWQ=Q`. Idempotence and cyclic trace then imply

```
trace((W-I4)Q)=0.
```

But `W-I4=diag(1/2,0,0,-1)`, and the forced diagonal values give

```
trace((W-I4)Q) = (1/2)(-2)-3 = -4.
```

This is the contradiction.

## A compact exact certificate

Instead of separately solving for r and s, use `trace Q=2` to eliminate
Q33. For every `B1=u v^t` the following identity holds:

```
trace((W-I4)Q) + 7 det(S4) - 2 det(I3-A3) = -4.
```

Each term on the left is forced to vanish by the preceding necessary
conditions. The verifier checks the identity in the polynomial ring over Q
in six independent variables `u0,u1,u2,v0,v1,v2`; it performs no coefficient
sampling and no polynomial-ideal search. It also verifies the literal frame
identities over sixteen independent entries of Q before imposing idempotence.

## Verification and limits

From the workspace root, run:

```
python -I -O -Werror -B research/p112-alternate-frame-trace/verify.py
```

The stdlib-only replay passed in approximately0.31seconds and compares the recomputed result to
`RESULT.json` without modifying it. All checks survive optimized Python. It
reconstructs the frozen geometry and flags, verifies the three physical caps,
and checks the complete symbolic certificate. Two targeted mutationsâ€”changing
the mask28 diagonal coefficient and reversing a certificate signâ€”destroy the
identity and are rejected. The older two-cap witness remains valid evidence
that masks22 and34 alone are insufficient; the new contradiction uses cap28
as well.

This excludes the full alternate common-frame family, not merely the earlier
14-defect fixture. It does not exclude other H0,K0 choices. No further
research direction is tested in this verification.

An independent agent completed a separate standalone reconstruction and
symbolic proof, importing no producer algebra. Its normal and optimized
replays passed; it also retained the old two-cap witness as a positive
control. See `independent.py`,
`INDEPENDENT-PROOF.md`, and
`INDEPENDENT-RESULT.json` in this directory.
