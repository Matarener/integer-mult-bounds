# Original-input joint map and complete conservative cleanup

Scientific pin: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.
This is a complete physical caller construction and an exact negative bill,
not a positive supplier or an exponent claim. All preceding-round sources
are imported read-only at their recorded hashes.

## Literal operator and input contract

Let q>=2, n=2q+2, k=2q+1, m=4q+4. The banks and independent original inputs
are `(a,t0,b1,k0,b2,C2,...,bq,Cq)`. No input is initialized, correlated,
discarded or assumed clean. Common plane0 and fresh planes1,...,k each have
2f bits. The old native planes N_i have N_i^2=-I, with one global i per
whole field. Write F_s=N_s...N_1 and N=N_0.

The phase-correct even-parity J is exactly the frozen native resource:
J_f=i^(f+1) Z U, J_f^2=-I. In the X-character description its address
translates the two common bits, its per-coordinate phase is
`1+parity(p0+p1)+parity(q0+q1)`, and its once-per-whole-field phase is i.
Equivalently J_f=i^(1-f) J_1^(tensor f). Put

```
Aop=N^-1 J,       P_s=S_(0,s),       B_s=P_s Aop.
```

At stage s, the actual source query is K_s=F_(s-1) J F_(s-1)^-1. Apply K_s,
deliver the source to its target, apply ADDRESS P_s to the source, and apply
fresh N_s to every other bank. The normalized box is exactly
`[[B_s,0],[J,I]]`. The source K_s has native arity2f and explicit selected
native recipes; it is not executed as three separately paid native queries.
Its native query adapters and f-dependent Gaussian unit are retained.

The common retarded frame is F_s. This frame convention is a mathematical
description of the full physical word, not a free transformation. The
prefix contains every fresh progress query on every bank. The actual public
output is F_k J x, which has native arity mf. No right endpoint gauge is
silently removed, and it is not replaced by the old E=N F_k.

## Base and exact all-q joint terminal map

Define S=a+sum_(r=1..q)b_r, A_r=a+sum_(l=r..q)b_l, and

```
Q1=J^-1 B1 J,
K=[[B2+Q1-I, I-B2], [Q1-I, I]].
```

The original-input base from the frozen handoff proof transfers algebraically
because it only requires J^2=-I and arbitrary invertible source codes:

```
u1=B3[J k0+(B1-I)(J t0+S)-A2],
v1=Krow1(t0,k0)+(2J-JB1-B2J)S.
```

The literal first-three-stage and scalar entrance word is in `joint_prefix.py`.
It includes the shared input J exposure and inverse, query3 continuation,
and the indispensable restoration of raw a from deeper b entrances.

For each nonfinal pair r=2,...,q-1 the alternative scalar handoff gives

```
u_r=B_(2r) u_(r-1),
v_r=-B_(2r+1)J v_(r-1)+(B_(2r+1)-J)A_(r+1).
```

The handoff is literal at a completed fresh cut: add V to the b accumulator
and the future c dirt, combine U with the next independent c difference,
query J on U, and perform the three bank swaps. The public b/c responses
are preserved and placed in their actual public slots. The event list retains
all bank swaps and all native continuations. There are q-1 continuations,
including query3, and no extra helper or private field.

Let D_r=B_(2r+1)J=P_(2r+1)N and

```
E_q=B_(2q) B_(2q-2) ... B4,
T_q=D_q(-D_(q-1))...(-D2),
Du=E_q B3 J=E_q P3 N,
R_r=D_q(-D_(q-1))...(-D_(r+1))D_r       (2<=r<q),
R_q=-D_q.
```

The exact terminal retarded carriers, in physical banks1 and3, are

```
U=Du Krow2(t0,k0)+E_q B3[(B1-2I)S+b1],
V=T_q Krow1(t0,k0)
  +T_q[(3J-JB1-B2J)S-Jb1]+sum_(r=2..q) R_r Jb_r.
```

Every C_r,r>=2 coefficient in these two rows is zero. Their independent
information is present in their already completed public outputs. Thus the
homogeneous H is `diag(Du,T_q)` times the swapped rows of K, and L is the
displayed original a/b reader map. No coupled H is credited as independent
helper stock. `JOINT-PREFIX.json` matches this entire original-input formula
against the literal physical prefix at q2/q3, including all Gaussian phase
residues and both inverse orders.

For the all-q reader proof put w_r=v_(r-1)+J A_r at the entrance to pairr.
Then

```
w_(r+1)=-D_r(w_r-Jb_r)                    (2<=r<q),
V=D_q(w_q-Jb_q),
w2=Krow1(t0,k0)+(3J-JB1-B2J)S-Jb1.
```

These equations prove the terminal formula by induction. Reverse recovery
has one final extraction followed by q-2 reverse steps, hence q-1 native
exposures in total. Each injection is the current completed public Jb_r.

## Joint affine cleanup: no separate native query for a public reader

All the following instructions are conjugated by the actual F_k cut. Let
`T=J S`, the sum of the current a/b public responses. First recover

```
z=Du^-1 U,
w_q=D_q^-1 V+Jb_q,
w_r=Jb_r-D_r^-1 w_(r+1)                  (r=q-1,...,2).
```

The physical D_r^-1 query is `-N_(2r+1) P_(2r+1)`, hence one native2
query plus ADDRESS/sign scans. A nonfinal reverse minus cancels that sign.
This identity is exact for every f. The final extraction is still charged.

The source-bound original-input formulas give

```
z=Krow2+(2I-Q1)T-Jb1,
w2=Krow1+(3I-Q1-B2)T-Jb1.
```

Consequently

```
p=w2+Jb1-2T,
q=z+Jb1-T
```

are exactly K(t0-T,k0). Every public reader is therefore implemented by
scalar ADD scans from the already completed public banks, and all those
source banks are restored unchanged. There is no public source-native
query, no promised correlated input and no prepared zero array.

The full K inverse is a two-query reversible word:

```
NEG(p); SWAP(p,q); q+=p;
B2^-1(q); p-=q; Q1^-1(p); q+=p.
```

It outputs (t0-T,k0). Add T to its first output, query J on both outputs,
and swap them back into the original t0/k0 bank slots. Every inverse here
is a unitary Clifford inverse or a reversible scalar instruction. No inverse
of a sum/nonunit operator is an implementation primitive.

`joint_tail.py` serializes this complete word. The native query definitions
are lowered to selected native children with literal monomial left/right
adapters and exact one-coordinate phase checks. Their all-f lift multiplies
by the displayed `i^(exponent*(1-f))`; the recipe is tensored bitwise.
Full physical forward and inverse events, all independent original columns,
and both literal inverse orders are checked, separately from the H/L formula.

## Complete tariff and its all-parameter rank proof

The prefix pays H2=n*k+q+2 and has prospective deficit2q. The tail pays

```
H2=q+1, H4=2, H6=1,
mass=2q+16.
```

The q-1 current-reader queries and two final J queries account for H2.
The B2^-1 and Q1^-1 queries have physical rank4 at F_k; they involve only
the three old planes0,1,2, so their one-coordinate calculation relabels to
every q and tensors to all f. The U-coordinate query F_k Du^-1 F_k^-1 has
rank6 for every q>=2, as follows.

Pull the ADDRESS product of E_q to the left. On one p or q component the
remaining polar form is the star at anchor1 with leaves
`{0,4,6,...,2q-2}` and anchor diagonal q-1 modulo2. Since P3N=N3P3 and E_q
fixes plane3, the polar form of F_k Du F_k^-1 becomes that star with leaf0
changed to3, plus the isolated diagonal at2q. Its star has rank2 and the
isolated diagonal has rank1. Thus each p/q component has rank3, giving6f.
Inverse Clifford B rank is the same. This proves the complete all-q invoice;
the finite q2/q3 selected-native lowerings are reproducible defect controls.

The complete bill simplifies to

```
H2=n^2+1, H4=2, H6=1,
mass=2n^2+16, stock=m*n=2n^2, D=-16.
```

All children are strictly smaller than the ambient and within the pinned
contraction cap for q>=2. The negative first moment already precludes a
positive moment from this direct invoice. This completed caller is useful
for exact whole-word retiming, not a solution to the positive saving goal.

## Limits and live obligations

This is an algebraic all-parameter proof with finite executable fixtures,
not a formal-kernel theorem. Literal precision, source/COPY costs, owner
allocation, storage, finite-tape realization and the independent BIT thread
are not discharged. Full native right input/output gauges are part of the
actual F_k J endpoint. Changing them requires a new complete word.

The separate fixed-prefix inverse-entry gate examines the unfactored
original-t/current-V coefficient and retains the actual F_k J target. It
must not be confused with the older factored helper gate. Any growing-in-f
scan-count escape or changed base/input/owner interface needs its own fully
charged transfer. No such escape is silently imported into this invoice.
