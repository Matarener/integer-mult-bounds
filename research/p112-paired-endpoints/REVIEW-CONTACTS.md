# Independent review of the fixed order-three geometry and contacts

Verdict: **PASS within the stated finite and isolated-contact scopes.** No
mathematical correction remains. This review read the complete source and proof,
checked the construction and costs independently, and inspected the final
receipt. It did not rerun the full geometry audit or dynamic program.

The reviewed sibling files, relative to `../c02-geometry/`, are:

| File | SHA256 |
| --- | --- |
| `check.py` | `c4a1ba764dbe4af2ae823d46d183199bc2cb15bbbf56d6d8ece4962b4e09c790` |
| `PROOF-GEOMETRY.md` | `0174ece475f2722fa7d9b9ccae2699efcfa2ecfb80a9980aa173c721e2e0554f` |
| `GEOMETRY.json` | `3f9bd282f180b4149a5af7a95983a83d2d15261c659afddff2972170c5b5ad1d` |
| `SOURCE-INVENTORY.json` | `9c6b8a8652e26d618bdadab61f96f8896d15d56c0bf4bdf9a9683a149d72995a` |

The independent endpoint implementation reviewed alongside these files is
`check.py`, SHA256
`e0c5d6e5b7ce81dc78afcb82904b1729adf4458a0ce48f33147520ca604aef04`,
with `CHECKS.json`, SHA256
`197d67b7201c39248b142aa3d6633fbbe23ce4300e7ba31c65f08834ce5d420e`.
All 112 ordered endpoint contracts agree as arrays, including their ordered
seven-vector complements. Their canonical digest is
`2765fa3074ba08133d8dbf1810c76e6d744127b4024d7933e1fe73d84e86389f`.
Canonical serialization uses sorted keys and compact separators with no
trailing newline. This comparison is stronger than rowspace agreement.

## Actual phases and native ranks

The character phase definition
`phi_U(x)=wt(P_U x) mod 4` is compatible with the chosen signed Gaussian
direction factors. For an orthonormal basis, binary orthogonality makes
cross-intersection terms even, so the weight identity modulo four gives the
product of direction phases. Every factor fixes the uniform character; thus
this establishes the global phase as well as the binary action.

The polar form of this phase is the orthogonal projector `P_U`. For nested
nondegenerate subspaces `U subset V`, the difference of the projectors has
rank `dim(V)-dim(U)`. The proof correctly applies this rank statement when the
orthogonal complement is alternating: the complement need not itself admit an
orthonormal basis. The source does not silently replace that complement by an
unavailable list of odd basis vectors.

After Walsh conjugation, this polar form is the native Clifford B block.
The complete phase arrays are evaluated on all 512 characters. The 12
compiler-lowering representatives additionally check their actual Clifford
action and Gaussian convolution coefficients, including global phase.
The proof distinguishes these representative lowerings from the complete
all-edge phase/rank argument. It does not say that all 5,824 contacts were
separately optimized or lowered by the native compiler.

## Partner map and all-edge minimal contact dimensions

The checked relations `O^3=I`, orthogonality of O, and
`O+O^2=I+cc^T` imply the displayed transpose relation. For each norm-one port
p, they give `p perpendicular O p`. Orthogonality preserves all port Gram
entries. The retained deterministic orthonormal completion, including its
alternating-remainder guard, yields the exact historical contracts.
There is no assumption that O permutes the retained port set.

For a legal edge, put `p=p_s`, `q=O p_s`, `p'=p_t`,
and `q'=O p_t`. From `p dot p'=0` and the O identity,
`p dot q' + q dot p'=1`. A contact subspace must be nondegenerate,
contain p and q', and lie in `q perpendicular intersect p' perpendicular`.

The three stated minima follow in this precise contact class:

* When `p=q'`, one dimension suffices.
* When p and q' are distinct and perpendicular, their Gram matrix is the
  identity, so two dimensions are sufficient and necessary.
* When they are distinct with `p dot q'=1`, their two-dimensional span is
  degenerate with radical `p+q'`. A nondegenerate contact therefore needs at
  least three dimensions. The emitted third vector pairs nontrivially with
  this radical, and the additional characteristic-vector constraint ensures
  the required orthonormal completion beginning with q'.

The finite search certifies the needed third vector for every edge in the
last case. The counts 104, 2,912 and 2,808 sum to 5,824. The lower bounds
concern this nondegenerate contact-subspace class; they are not lower bounds
for arbitrary arithmetic circuits or shared-helper constructions.

## Arbitrary helper dirt and literal physical return

For coefficient `a in {+1,-1}`, the initial physical fields are arbitrary:
`x=T_p X`, `y=T_q' Y`, and `h=T_q' H`. Let
`A=T_L T_p^-1` and `B=T_L T_q'^-1`. The proposed chronological word is:

1. Apply `y -= a h` before the target and helper leave their common q' frame.
2. Apply A to the source and B separately to target and helper.
3. At L, perform `h += x`, `y += a h`, and `h -= x`.
4. Apply the actual helper return `B^-1=T_q' T_L^-1`.
5. Move source and target from L to their stated outgoing caps.

After step 3 the helper is B times its original physical value, so step 4
is essential. It is not permissible to call step 3 alone a literal helper
restoration. Direct substitution gives the complete physical block matrix

```
[ T_(q perpendicular) T_p^-1                 0                         0 ]
[ a T_(p' perpendicular) T_p^-1  T_(p' perpendicular) T_q'^-1          0 ]
[                  0                        0                         I ].
```

This includes every source, target and helper column. The production
phase-array predicate checks all three physical outputs for both signs at
every edge, rather than assuming a zero entering helper. Equality on all
characters is an exact operator proof because the finite Fourier transform
is invertible. For rank one, the direct ADD uses the coincident source and
target frames; the third arbitrary field is an untouched spectator.

## Complete local invoices and limited scheduling theorem

For rank r equal to two or three, the source and target preparations cost
two rank `r-1` transitions, their exits cost two rank `8-r` transitions,
and helper preparation plus literal return cost two more rank `r-1`
transitions. Thus the complete native rank histogram is
`{r-1:4, 8-r:2}`, with mass `2r+12`, namely 16 or 18.
The four signed ADDs are exactly the precompensation, gather, delivery and
gather reversal. The coefficient restriction to unit signs is needed for
that scalar bill. Rank one costs two rank-seven transitions and one
signed ADD, with mass 14.

These transition ranks are not helper storage widths: a helper is an
entire arbitrary 512-coordinate field. Each native transition still
requires its two monomial adapter legs. The generic paid in-place cycle
bound is an explicit upper bound, not a claimed minimal scan cost or
physical tape implementation. No distinct-adapter count is amortized into
a free operation.

For the source-batched screen, the recurrence tries every possible first
vertex and restricts the remaining mask to its outgoing zero neighbors.
The coloring bound is sound because every valid sequence is a clique in
the compatibility graph and every color class is independent. Pruning
only when the color bound cannot improve the incumbent preserves the
exact maximum. The receipt's maximum eight and its length-eight witness
refer to the fixed matrix `M_st=p_s dot O p_t`, with the stated
triangular-zero condition. They do not bound all possible physical
interleavings or changed access models.

## Separate historical terminal screen

The final addendum explicitly changes the helper terminal to
`Q_s perpendicular`. Orthogonality of O gives
`Q_t subset Q_s perpendicular` on every legal edge. Consequently the
chosen actual phase transition has native rank seven. It does not
return that helper to its original physical value.

Under the separately stipulated one-helper-per-nondirect-edge model, the
arithmetic is correct:

```
5720*7 + 224*7 = 41608,
9*41608 - 65*896 = 316232 > 0.
```

This fails the old zero-rate capacity before other charges. The fixed
65-dimensional normalization, `896/9` productive-call rate, and separate
helper premise are necessary hypotheses. This calculation gives neither
a universal sharing obstruction nor an incompatibility with the
different, literally restored isolated contacts.

## Source and acceptance-control boundaries

The source authenticates the captured compiler bytes and executes those
bytes with optimization explicitly disabled. Its full phase values are
the production equality data; digests only identify retained values, and
the collision guard rejects unequal arrays sharing an identifier.

The controls mutate actual candidate operators or invoices, including
omitted helper return, omitted precompensation, wrong delivery sign,
global-i phase, and a cancelling ADD pair. A cancelling pair passes the
endpoint predicate but fails the same complete-invoice predicate used by
the accepted candidate. The rejection oracle is outside the branch that
catches the intended production error. Each named check deletion then
demonstrates loss of that detection. These are not merely recorded
inequalities against a hand-constructed bad output.

This review approves the source/proof correspondence and the bounded
mathematical claims. It does not certify a simultaneous many-edge
supplier, compatibility of caller frames, a 65/56-dimensional program,
rounded-error bounds, ownership, physical tape cost, hosted CI, a formal
kernel proof, or a multiplication exponent.
