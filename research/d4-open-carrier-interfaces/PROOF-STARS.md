# Exact star normalizers for the eight A/B ports

This written proof completes the A/B part of the fixed twelve-port OPEN
normalization. The four exceptional C-port gauges remain covered by the
separate `PROOF-NORMALIZATION.md` and its frozen four-port checker. The
eight A/B ports here require only address involutions and translations;
their exact global phase is settled by the character calculation below.
No finite gauge search or all-caller claim is used.

Use the actual native conventions

```
C_v=((1+i)I+(1-i)X_v)/2,       F=X_33 F7,
T=F C_p^-1 C_q^-1,            J=F X_p,
S=F C_r^-1 C_p^-1.
```

The last formula is the OPEN source boundary for groups A and B only.
All values are arbitrary Gaussian dyadic arrays and products act
rightmost first.

## The address involution and its exact phase

For an actual orthonormal port triple `(p,q,r)`, set `w=q+r` over F2.
Then `w≠0`, `w·w=0`, and the binary matrix

```
R=I+w w^T
```

is an orthogonal involution. It fixes p and interchanges q and r.
We also write R for the exact phase-free address permutation
`|x> -> |Rx>`. Consequently `R C_v R^-1=C_(Rv)` exactly, not merely
projectively.

Put `epsilon=wt(w)/2+1 mod2`. For every binary x,

```
wt(Rx)-wt(x) = 2 epsilon (w·x)  (mod4).
```

If `w·x=0`, Rx=x. Otherwise the overlap `wt(w∩x)` is odd, so
`wt(x+w)-wt(x)=wt(w)-2wt(w∩x)` is `wt(w)-2` modulo four, proving the
formula.

The translation character `chi_x` is an eigenvector of F7 with
eigenvalue `i^wt(x)`: each C_e contributes 1 or i. Therefore the
character-weight formula gives the exact operator identity

```
R F7 R^-1 = X_(epsilon w) F7.
```

There is no undetermined constant phase: the zero-frequency character
has eigenvalue 1 on both sides. Conjugating the actual gauge yields

```
R F R^-1 = X_(R33+epsilon w) F7.
```

Since `R33=33+(w·33)w`, this equals F precisely when
`w·33=epsilon`. All eight actual rows satisfy that condition:

| Group | p | q | r | w | wt(w) | epsilon | w·33 |
|---|---:|---:|---:|---:|---:|---:|---:|
| A | 7 | 13 | 117 | 120 | 4 | 1 | 1 |
| A | 2 | 61 | 64 | 125 | 6 | 0 | 0 |
| A | 50 | 8 | 69 | 77 | 4 | 1 | 1 |
| A | 55 | 56 | 112 | 72 | 2 | 0 | 0 |
| B | 13 | 117 | 7 | 114 | 4 | 1 | 1 |
| B | 61 | 64 | 2 | 66 | 2 | 0 | 0 |
| B | 8 | 69 | 50 | 119 | 6 | 0 | 0 |
| B | 56 | 112 | 55 | 71 | 4 | 1 | 1 |

The exact phase correction is essential for the four epsilon-one rows.
For an epsilon-zero row the ungauged F7 already commutes with R; no
contrary rejection claim is made for those rows.

## Physical and logical normalization in both orientations

Choose `P=post=R`. Since R commutes with the actual F, fixes p and swaps
q,r,

```
R S R=T.
```

Thus the raw block `[[S,0],[J,T]]` normalizes to

```
F_K=[[T,0],[T K,T]],       K=T^-1 J R=C_q C_p^-1 R.
```

The actual input frames are `(C_p,C_q)` and the actual output frames
are `(F C_q^-1,F C_p^-1)`. The logical kernel is

```
A=C_q^-1 K C_p=C_p^-1 R C_p=R,
```

because R fixes p. Hence `H=A^-1=R`. At the two designated physical
cuts,

```
C_p H C_p^-1=R,
(F C_p^-1) H (F C_p^-1)^-1=R.
```

These are the same pre-X and post-Y corrections in both orientations.
The common-code block identities in the companion proof apply without
any claim that different ports' R operators commute.
The physical K is not an involution; logical A being an involution does
not justify replacing the physical K^-1 by K.

For the backward interface retain the full ordered corrections

```
AB=T K^-1 T^-1 K^-1,       BB=T AB^-1 T^-1.
```

Since `TK=F X_p R`, and F, X_p and R commute while `R²=I`,
`(TK)²=F²=X_127`. Using `T²=X_(127+p+q)` gives

```
BB=(TK)² T^-2=X_(p+q).
```

Conjugating `BB^-1` by `T^-1` gives AB. Translations commute with T,
so `AB=BB=X_(p+q)` exactly. The complete inverse wrapper is therefore

```
diag(I,X_(p+q)) diag(X_(127+p+q),X_(127+p+q))
    swap(F_K^-1)swap diag(I,X_(p+q))
       = [[T,-T K^-1],[0,T]].
```

All four displayed translations remain executed and paid. Here
`swap(F_K^-1)swap` is implemented by consistently exchanging the names
of the two banks in every inverse-word operand. It does not require
executing two additional raw swaps. Any physical routing needed to
realize that operand assignment belongs in a complete caller's bill.

## Literal cost at every chunk size

Every added wrapper in this eight-port family is a phase-free address
involution. For positive f let `N=2^(7f)` and tensor the base maps across
the f bit positions. The lifted R fixes a `6f`-dimensional binary
subspace, so its coordinate permutation consists of

```
(2^(7f)-2^(6f))/2
```

two-cycles. A nonzero lifted translation consists of `2^(7f-1)`
two-cycles. Enumerate every address x once, compute its partner sigma(x),
and perform a swap exactly when `x<sigma(x)`. No general cycle-discovery
search or destination array is needed.

Each arbitrary complex-value swap uses three signed ADDs and one
negation, with no extra complex field. Its one sum intermediate needs
at most one extra magnitude bit, and no extra denominator bits. The
address calculation takes `O(49 f N)` binary operations per map and
`O(f)` counter bits. These are explicit mathematical operation bounds,
not a physical-tape step claim.

Unfused forward normalization plus the common-code pre-X/post-Y spelling
uses four R maps. The wrapped backward spelling uses four R maps and
four nonzero translations: two normalizers inherited from the inverted
forward word, the common-code pair, AB, BB and the two T² maps.
At f=1 these invoices are 128 versus 384 coordinate swaps per port.
At arbitrary f they are respectively

```
2(N-2^(6f))       and       4N-2*2^(6f)
```

coordinate swaps. Multiply each by three for complex ADDs and by one
for negations. No Gaussian-unit phase multiplication is needed for
these address-only wrappers. Possible cancellations between adjacent
maps have not been used to claim a better bill.

The original carrier's native histogram and its own monomial adapters
remain separate costs. Zero added native rank is not zero arithmetic,
storage, address or physical access work.

## Registered finite replay and scope

`check_stars.py` independently reconstructs these eight R matrices from
the frozen geometry, executes all exact operator identities with the
authenticated compiler, and compares complete signed Pauli images plus
the phase-sensitive zero column. It checks the mod-four character
identity on all 128 characters per port, giving 1024 character checks.
Its eight lowered monomials per port are checked on all 128 addresses,
giving 8192 literal address checks. This last count concerns the
lowered monomial circuits, not independent complete native-history
simulations.

The checker executes a wrong output i phase, an omitted AB, and K
substituted for K^-1 for each port, plus an omitted invariant-F translation
for the four epsilon-one ports. Each must fail the intended production equality predicate.
Deleting that predicate's phase comparison accepts each global-i
defect. The complete control inventory is 28 rejected mutations and
eight executed phase-guard deletions.

Use fresh output paths and the supplied pinned files:

```
python3 -I -B check_stars.py --geometry frozen/geometry/D4-BUS-INPUT.json \
  --compiler frozen/compiler/clifford_exact.py --output /tmp/fresh-STARS.json
```

The written character proof, operator algebra and involution count stand
without the finite replay. The replay's normal and
optimized complete records must agree byte for byte. Tensoring the
proved identities establishes every positive f for these fixed ports;
it does not replace them by a four-term all-f decoder.

Together with the four C-port witnesses this closes normalization of
the selected twelve OPEN ports. It does not establish source widths
for all P112 ports, a globally routed caller, whole-helper ownership,
rounded precision, physical tape realization, or any new kappa bound.
