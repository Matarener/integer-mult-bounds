# A separate 2n floor for the odd-chunk quartic carrier

Let A have all four eigencharacters of `z^4+1`. Allow unary A/A inverse on
bank fields and arbitrary scalar rational or Gaussian constant bank GL
bridges. The target applies A squared to n independent public fields and
restores any additional independent dirty helper fields exactly. Then
`k>=2n`. The bound is sharp. This proof uses no z=1 or z=−1 character.

After pulling constant bridges to one side, the word is a product of
`I+(z^eps_j-1)u_jv_j^T`, eps_j=±1, with the same constant source directions
at every character. Its target has the form

```
W(z)=C^-1 diag(z^2 I_n,I_h).
```

C is an arbitrary invertible constant; it cannot be normalized using an
unavailable augmentation character. With U,V the column/row directions,
L the strict chronological interaction matrix, and
`D(z)=diag(z^eps_j-1)`, the exact product identity is

```
W(z)-I=U G(z)V,     G(z)=(D(z)^-1-L)^-1.
```

All queried coefficients are nonzero at the four actual characters.
Choose characters z,w with `z^2=+i`, `w^2=-i`. The difference

```
W(z)-W(w)=C^-1 diag(2i I_n,0_h)
```

has rank n. Its column and row spaces factor through U and V, so each of
U,V has rank at least n. This step retains the arbitrary final bridge and
all dirty helpers; a single character need not have that rank.

Now choose an opposite pair z,−z. Their targets are equal, while

```
G(z)-G(-z)
 =G(z)[D(-z)^-1-D(z)^-1]G(-z).
```

The middle diagonal has entries `-2z/(z^2-1)` for forward calls and
`+2z/(z^2-1)` for inverse calls. Every entry is nonzero. Thus this
k-by-k difference is invertible. Equality of the two targets implies

```
U [G(z)-G(-z)] V=0.
```

The image of the invertible difference times V lies in ker U. Therefore
`rank V<=k-rank U`, and `k>=rank U+rank V>=2n`.

For the actual common1/fresh1 carrier,
`A_f=(U_f tensor I)SWAP`, `U_f=H_p^(tensor f)`, `U_f^2=(-i)^f I`.
At odd f its fourth power is−I. The written derivation in
the companion-theorem section of `SCOPE-REVIEW.md` proves that all four
primitive eighth-root characters occur for this displayed formula. The historical native arities
`A_f^+/-:f`, `A_f^2:2f` are inherited carrier premises; their physical
lowering is not replayed or admitted by this package. Conditional on that
invoice, `m=2,W=n,H={1:k}` has `D=2n-k<=0` for this odd-f carrier.
No scalar-GL shortcut exists in this stated query model.

The root and stabilizer lanes independently reviewed the rank argument.
`quartic_opposite_gate.py` checks the full quartic coefficients, exact
inverse of the opposite-character difference, literal query/word inverse,
sharp2n construction and a missing-call defect. The written proof is the
all-n result; it is not a finite exhaustive search or formal kernel proof.

Operator-valued ADDRESS/Pauli bank bridges can mix these characters and
are outside this scalar model. A general variable-support native supplier
or a primitive-scan lower bound is also outside it.
