# Exact common-frame normalization at four fixed h7 ports

This is a local exact operator result. The finite witness consists of the four
C ports of the frozen D4 carrier geometry, with source labels
`p=(117,64,69,112)` and paired target labels `q=(7,2,50,55)`. It supplies
normalizers and inverse-orientation wrappers for these four ports. It does
not admit a routed recursive caller, prove an optimum over gauges, or change
a multiplication exponent.

The scientific source pin is
`20ecf2891d80b5acf18d980b2164fb44ea7faa90`. The pinned exact Clifford compiler
has SHA256
`2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962`.
Source hashes and the distinction between frozen witness input and fresh
verification are recorded in `frozen/reviews/normalizer/SOURCE-INVENTORY.json`.

All products below use conventional matrix order: the rightmost operator
acts first. Every source and target value is arbitrary in the Gaussian
dyadic vector space. The normalization uses no promise of zero input or
restricted source support. The carrier's own arbitrary-input construction,
reverse-carrier profile and the four-helper bus restoration are separate
obligations; this proof starts from its explicit two-bank boundary.

## A split-Lagrangian criterion in every dimension

Use binary phase-space coordinates `(x,z)`. The computational Lagrangian is
`Z={(0,z)}`. The native full transform has binary symplectic action

```
F = [ I I ].
    [ 0 I ]
```

Thus `W=F^-1 Z={(z,z)}` and `Z,W` are transverse Lagrangians. A Pauli
translation multiplying F, such as the actual gauge `X_33 F7`, does not
change this binary action. Write `L(U)=U^-1 Z` and let `r(U)` be the rank
of the X block of the images of Z, namely the native Bruhat rank. Then

```
dim(L(U) ∩ Z) = n-r(U),
dim(L(U) ∩ W) = n-r(U F^-1).
```

For the second equality, apply F to the intersection: its image is
`L(U F^-1) ∩ Z`.

Suppose for one `0≤d≤n` that S and T satisfy

```
r(S)=r(T)=n-d,
r(S F^-1)=r(T F^-1)=d.
```

The dimensions of the two intersections of L(S) with Z and W sum to n.
Since Z and W are transverse, these intersections therefore give a direct
sum decomposition of L(S); the same holds for L(T). Under the perfect
symplectic pairing between Z and W, the W summand is exactly the annihilator
of the Z summand: containment follows from isotropy and equality from
dimension.

Choose any invertible binary B mapping `L(T)∩Z` to `L(S)∩Z`, and set
`G=B^-T`. Define

```
P_binary = [ G        0    ].
           [ G+G^-T   G^-T ]
```

It preserves Z and W. Its restrictions are B on Z and the pairing-dual G
on W, so it maps L(T) onto L(S). Consequently

```
post = T P^-1 S^-1
```

preserves Z: S^-1 sends Z to L(S), P^-1 sends that to L(T), and T sends
L(T) to Z. Hence post is a monomial Clifford. P and `F P F^-1` are
monomial too.

There is an explicit exact Clifford lift of P. Let `Perm(G)` send
`|x>` to `|Gx>`, and put

```
Q=I+G^-T G^-1,                 P=Diag(Q) Perm(G).
```

Q is symmetric. Choose the diagonal phase

```
i^[Σ_j Q_jj x_j + 2 Σ_(j<k) Q_jk x_j x_k].
```

Its symplectic action is `[[I,0],[Q,I]]`, so the lower-left block of P is
`QG=G+G^-T`. This also fixes an exact phase representative. The other
normalizer is defined by the exact product `post=T P^-1 S^-1`, retaining
its actual phase. A binary rank test establishes monomiality, while the
exact product establishes

```
post S P=T
```

without a hidden scalar. This argument proves all-dimension existence under
the stated rank hypotheses. It does not assert that the inverse-orientation
AB and BB below are monomial for every member of this family.

## The four exact witnesses

In the h7 chart let the core be `(a,b,c)=(7,13,117)`, radical basis
`(5,53)` and dual basis `(30,96)`. D is the real four-point Walsh transform
on the radical coordinates, with the pinned compiler's positive-native
phase corrected by `-i`. Set

```
V_C=D C_a C_b,    F=X_33 F7,
S=V_C C_p^-1,    T=F C_p^-1 C_q^-1,    J=F X_p.
```

The native one-direction operator is
`C_v=((1+i)I+(1-i)X_v)/2`, so `C_v²=X_v` exactly. All translations and
all these C operators commute. The four ports satisfy the preceding
hypotheses with `n=7,d=2`; the checker recomputes ranks `(5,5,2,2)`.

The witnesses reuse the frozen successful address matrices. Rows are
binary bit masks:

| p | q | G rows |
|---|---|---|
| 117 | 7 | 76,109,57,64,22,100,41 |
| 64 | 2 | 55,35,53,72,122,58,98 |
| 69 | 50 | 45,118,104,61,62,12,42 |
| 112 | 55 | 4,6,67,79,31,111,43 |

The checker reconstructs Q from G, checks every frozen monomial recipe
against its exact native history, and replays each history and its lowered
recipe on all 128 computational basis vectors using a second, sparse
Gaussian-integer interpreter. Thus it checks 4096 basis columns across
eight monomials at each of four ports. Complete signed Pauli images plus
the phase-sensitive zero state are also compared. The binary Pauli action
alone would leave a global phase undetermined.

The old bounded search is provenance for these four witnesses. Its trial
counts and rejected gauges are not used as a lower bound and are not
rerun to rediscover already supplied matrices.

## Physical kernels, logical kernels and both orientations

The raw carrier has physical boundary

```
[ S  0 ]
[ J  T ].
```

Putting P on source input and post on source output yields

```
F_K = [ T   0 ],       K=T^-1 J P=C_q C_p^-1 P.
      [ TK  T ]
```

The actual input frames are `D_X=C_p,D_Y=C_q`, and the actual output frames
are `E_X=F C_q^-1,E_Y=F C_p^-1`. They satisfy
`T D_X=E_X` and `T D_Y=E_Y`. Stripping these frames gives the logical
forward shear

```
[ I 0 ],              A=C_q^-1 K C_p=C_p^-1 P C_p.
[ A I ]
```

K, P and A are distinct operators. In particular, A need not be monomial
or an involution.

Let `H=A^-1`. The same logical pre-X and post-Y correction works in both
orientations:

```
diag(I,H) [ I 0 ] diag(H,I) = diag(H,H) [ I 0 ],
          [ A I ]                     [ I I ]

diag(I,H) [ I -A^-1 ] diag(H,I) = diag(H,H) [ I -I ].
          [ 0  I   ]                      [ 0  I ]
```

These are direct block multiplications; no commutation between different
stage codes or involution assumption is used. In both orientations the
physical pre-X correction at C_p is

```
C_p H C_p^-1=P^-1,
```

and the physical post-Y correction at `F C_p^-1` is

```
(F C_p^-1) H (F C_p^-1)^-1
    =F X_p P^-1 X_p F^-1
    =X_p (F P^-1 F^-1) X_p.
```

They are monomial because P and its common-F conjugate are monomial. This
derivation explains the two actual cuts; directly executing the logical H
on the physical X bank generally implements a different operator. The
checker includes that wrong-chart mutation at all four ports.

## An exact inverse-orientation wrapper

Take the literal inverse of F_K and exchange the two bank roles. Its matrix is

```
R = [ T^-1  -K T^-1 ].
    [ 0      T^-1  ]
```

The required physical backward alphabet is

```
B_K = [ T  -T K^-1 ].
      [ 0   T      ]
```

Define, with the displayed order preserved,

```
AB=T K^-1 T^-1 K^-1,       BB=T AB^-1 T^-1.
```

The complete wrapper is

```
diag(I,BB) diag(T²,T²) R diag(I,AB) = B_K.
```

Indeed its upper-right magnitude is
`T² K T^-1 AB=T K^-1`; its Y diagonal is `BB T AB=T`, and its X diagonal
is T. This explicitly includes all four extra bank maps: AB on input Y,
T² on each output, and BB on output Y.

For these four witnesses, AB and BB have rank zero, and their full phases
are retained in the literal monomial recipes. This is a finite verified
property of the four selected G matrices. Furthermore

```
T²=X_(127 xor p xor q),
```

which is respectively `X_13,X_61,X_8,X_56`. It is a paid translation, with
no positive native rank. The checker verifies this exact identity too.

With the same frames as above, B_K strips to
`[[I,-A^-1],[0,I]]`. The previously proved pre-X/post-Y H corrections
therefore apply to this orientation as well. Inverting the carrier's native
queries preserves their Bruhat ranks, but its actual histogram is owned by
the carrier replay, not reestablished by this normalization proof.

## Literal monomial implementations and costs

Each rank-zero recipe is lowered to a concrete map

```
|x> ↦ i^φ(x) |Gx xor b>,
```

where φ is a Z4-valued quadratic polynomial and includes the actual global
phase. The lowered recipes contain only address permutations,
translations, quadratic phases and scalar Gaussian units. They contain no
native C query. Their displayed unsimplified native histories are used
only to verify the lowerings; executing those histories for free would be
an invalid cost claim.

For one f-fold tensor register let `N=2^(7f)`. There are two explicit
literal implementations, with different resource contracts.

1. With a distinct destination array, evaluate the address and phase for
   each source coordinate, then write its phase-multiplied value at that
   destination. This uses N coordinate writes, at most N Gaussian-unit
   multiplications and `O(49 f N)` binary address/phase operations. The
   destination array must be counted.
2. Without an extra complex array, phase each coordinate in place and
   rotate each cycle of the address permutation. Enumerate possible cycle
   leaders in increasing address order; accept one only if traversal finds
   no smaller address. For a cycle
   `(x,σx,...,σ^(l-1)x)` use pivot swaps
   `(x,σx),(x,σ²x),...,(x,σ^(l-1)x)`. This sends each old value to its
   required successor. It uses `N-c` swaps where c is the number of cycles,
   hence at most `N-1`. A swap of arbitrary complex values a,b can be
   implemented by `a+=b; b=-b; b+=a; a-=b`: three ADDs and one negation,
   with no scratch complex field. Cycle discovery costs at most
   `O(49 f N²)` binary address operations and `O(f)` address-counter bits.

The receipt emits every base-chart cycle and pivot swap and verifies its
complete symbolic arbitrary-input map. The all-f cycle argument applies
to every bijection, so it is not an extrapolation from four sampled values.
Neither cost model is an admitted finite-tape supplier or an uncharged
storage convention. Gaussian unit phases add no denominator bits, but the
native child's precision and the full rounded caller still need their own
contracts.

Relative to an already available raw C-port forward carrier, normalization
adds P and post, and the common-code spelling adds pre-X H and post-Y H:
four monomial maps. The inverse construction starts with the inverse of
that normalized carrier, adds AB, BB and the two T² maps, and then the two
common-code maps. Counting the inverse carrier's two normalizers gives
eight monomial maps. These are unfused upper bounds for these wrappers,
not a complete arithmetic bill for all original carrier adapters.

## Tensor lift, restoration and limits

For every positive integer f, tensor every native and monomial operator
columnwise across f bit positions. Tensor products preserve composition,
inverse and equality, so all four exact local identities and their
backward wrappers hold on the resulting `2^(7f)` dimensional registers.
The lifted monomial address is the product address permutation; its phase
is the sum modulo four of the f coordinate phases. The literal
implementations just described remain valid.

This is an all-f operator proof from fixed base identities. It does not
expand a four-term base decoder and charge it as four terms at general f;
such an expansion could have `4^f` support. There is no dirty helper in
this normalization layer to restore. Arbitrary source and target inputs
are retained by the declared invertible maps.

A routed multistage caller still has to establish its actual cuts after
all previous codes, retain the ordered product of common H factors, and
pay its terminal decoding or prove its absorption. Source access, whole
helper owners, global stock, native precision, rounded cleanup and
physical head movement remain separate obligations. In particular,
monomiality at the isolated C_p and `F C_p^-1` cuts does not establish
monomiality at every accumulated caller chart.

## Executed controls and evidence scope

At each port the checker executes nine malformed operators through the
same production equality or rank acceptance predicates: a global i error,
omitted output normalization, omitted full-F gauge, omitted common chirp,
omitted AB, omitted BB, omitted T², K substituted for K^-1, and logical H
executed directly at a physical X cut. Each rejection must arise from its
intended signed-Pauli, phase or rank predicate.

The global-i defect preserves every signed Pauli image. Executing the
same equality predicate with its phase comparison deleted accepts it.
This is an actual check-deletion experiment at the exact-operator equality
predicate, not a claim that deleting one line would make the entire package
accept every other defect. Four such deletions plus 36 rejected mutations
give 40 executed control records.

Normal and optimized Python must produce byte-identical complete receipts.
The pinned compiler is executed from the authenticated bytes with
`optimize=0`, so its internal assertions are retained under an outer `-O`.
Fresh finite replay, written all-dimension reasoning and all-f tensor
reasoning remain distinct; no formal-kernel proof is claimed.
