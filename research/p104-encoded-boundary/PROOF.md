# A row-to-column encoding is a separate physical interface

## Scope and the actual source boundary

The pinned `notes/copied-centers-complex.tex`, subsection **Two-stage phase
endpoint and its paid correction**, specifies a forward scalar shear followed
by an inverse second shear. It gives physical data outputs
`A=-F y`, `B=F T^-2 x+E y`, a paid correction, phase/sign/bank wrappers, and
**distinct** auxiliary banks. `notes/structured-bulk-complex.tex` states the
completed all-role C contract. Those sources do not contain a chronological
P104 replacement with two adjacent completed P104 calls.

This audit therefore identifies the actual *stage boundary* and tests the
natural proposed P104 row/column interface at it. It does not claim to have
found the missing adjacent completed-call implementation. PR3954's positive
control says that a common completed C commutes with a fixed scalar bank
encoding. The new question is whether the same encoding is present on both
sides when the active fibers and source/target orientation change. It is not.

The row and column maps below are explicitly proposed contracts. In particular
`S A_c S` is the contract obtained by swapping the source and target roles of
the forward encoding; it is **not** a replay or admission of an inverse P104
word. An actual inverse caller may choose another encoding, whose compatibility
must then be derived separately.

## Fixed physical slots and exact transition

There are two data banks `X_(i,j),Y_(i,j)`, `0<=i,j<104`. Ordering each port
index by the eight pinned pivots followed by the 96 nonpivots, put

```
D = [I B; B^t B^t B-I],    H=diag(0_8,I_96),    J=I-H,
D^-1 = [ I-B B^t    B ] = [ -11I    B ]
       [ B^t       -I ]   [  B^t   -I ].
```

The canonical fixture gives `B B^t=12I`.
Define `D_r=D tensor I`, `D_c=I tensor D`, and likewise `H_r,H_c,J_r,J_c`.
This is a genuine change of which physical owners mix; it is not a permutation
of names inside an already matched interface.

Let `T_r,T_c` be diagonal families of invertible address operators, commuting
with their own H masks. For either axis `a`, define

```
L_a = [D_a H_a T_a; 0 I],
Pi_a = [J_a H_a; H_a J_a],
A_a = Pi_a L_a.
```

`Pi_a` swaps the X/Y slots at nonpivot ports of that axis. It records literal
PR3882 occupancy. Let `S=[0 I;I 0]` exchange source/target orientation. The
candidate reversed column encoding is `Abar_c=S A_c S`.

A physical handoff preserving the same underlying unencoded fields must be

```
K = Abar_c A_r^-1
  = S Pi_c L_c S L_r^-1 Pi_r.
```

No factors commute past each other in this formula. It is exact on arbitrary
address functions, regardless of the noncommutation of D with the chart family.
`K A_r=Abar_c` follows by adjacent inverse cancellation. Every map is extended
by identity on both disjoint dirty-helper banks. These identities preserve all
helper values, but do not execute their required completed F transformations
or supply an owner schedule. Fixed output slots remain the named X and Y slots.

On the common chart sector `T_r=T_c=I`,

```
A_r = [J_r D_r H_r; H_r D_r I],
A_r^-1 = [D_r^-1(J_r-H_r) D_r^-1 H_r; H_r J_r],
Abar_c = [I H_c D_c; H_c J_c D_c].
```

Consequently the four blocks of K are

```
K11 = D_r^-1(J_r-H_r) + H_c D_c H_r,
K12 = D_r^-1 H_r       + H_c D_c J_r,
K21 = H_c D_r^-1(J_r-H_r) + J_c D_c H_r,
K22 = H_c D_r^-1 H_r       + J_c D_c J_r.
```

Row and column operators commute only when they act on different port factors;
the displayed order within each factor is retained. These are interface
identities, not native rank-cost estimates.

## A physical constant-input counterexample

Take `X_(0,0)=2` and every other data field zero, with arbitrary dirty helper
values. Both index zero ports are pivots. Under `Abar_c`, this stays exactly
`X_(0,0)=2`: the column H mask kills that pivot source. Under `A_r`, the same
X field survives and **48** additional Y fields appear at nonpivot row indices
with column index zero, each equal to +1 or -1. This follows from the first
row of B having 48 signed halves. The verifier reconstructs the canonical E8
roots and punctures and checks the count and signs; it does not import PR3954's
matrix code.

This is not merely an artificial choice of globally identity native operators.
For the positive physical convention `C_u=((1+i)I+(1-i)X_u)/2`, every C_u,
its inverse, and F fix constant address functions (the zero Fourier character).
Thus the counterexample lifts to that actual invariant physical sector by
assigning the displayed constants to entire arrays. It disproves identity
handoff for these named encodings before endpoint phase wrappers. It does not
price a constant-sector operation as a native child or assert every orientation
or changed encoding has the same defect.

A common completed operator C applied on every data role commutes with both
common-chart encodings separately. Nevertheless `A_r != Abar_c`. Therefore
`C A_r=A_r C` does not imply `Abar_c^-1 C A_r=C`; the change of representation
still occurs. The independent checker includes both commutation identities as
positive controls and rejects identity handoff, omitted Pi and omitted reversal.

## Explicit formal word and complete cost decision

For one common-chart fiber, D factors as two triangular updates:

1. `u_J += B u_N`.
2. `u_N = B^t u_J - u_N`.
3. `u_N += w_N`.
4. Swap the 96 nonpivot source/target slots.

The inverse reverses those operations. There are 384 signed-half terms in each
B traversal. With temporarily writable donor arrays, each traversal halves
its donor bank, performs signed unit additions, and restores donors by doubling.
Thus either direction has 864 unit ADD/SUBs, 104 halves, 104 restoring doubles,
96 signs, and 96 explicit in-place slot swaps. This factor word uses no scratch
array. The signs and swaps remain separately charged operations. This is not
a new optimum or a comparison to PR3940/3943/3956's differently fused adapters.

Applying the inverse to 104 row fibers and the reversed encoding to 104 column
fibers gives a formal common-chart transition invoice:

| Operation | Count | Status |
|---|---:|---|
| Unit array ADD/SUB | 179,712 | Constructive exact scalar count |
| Array halve | 21,632 | Constructive exact scalar count |
| Restoring array double | 21,632 | Constructive exact scalar count |
| Nonpivot array sign | 19,968 | Constructive exact scalar count |
| Explicit slot swap | 19,968 | Constructive exact logical-slot count |
| Extra scratch arrays | 0 | For this factor word |
| Nonuniform chart transport, physical swap/routing and fixed-slot return | unknown | No native realization supplied |
| Dirty-helper completion, lifetime/holding, width/precision/control and recursive admission | unknown | Retained obligations |

Role reversal is expressed by choosing source and target operands in the column
word; it does not require two extra whole-bank exchanges. Its legal physical
availability is still an obligation. The finite invoice is **not** a physical
upper bound, since native chart changes and ownership have not been realized.

For the unchanged PR3954 scaffold, grant all new interface work zero cost.
The named hypotheses are 208 local calls, rank mass 2576 each, persistent
progress at most 2312 each, 104^2 data pairs, 72 helpers per fiber in two
disjoint banks, ambient rank 81, entrance rank one per data source, and native
rank tariff at least remaining persistent progress. Then

```
W = 2*104^2 + 2*104*72 = 36608,
remaining >= 81W-104^2-208*2312 = 2473536,
bill >= 208*2576+2473536 = 3009344,
capacity = 81W = 2965248,
excess >= 44096.
```

Adding K as external work cannot repair this failed gate. Unknown nonnegative
costs are not zero; zero is only the most favorable rejection relaxation.
For 0<=a<1 and every child rank r<=81, `(r/81)^(1-a)>=r/81`, so failure also
holds for the corresponding positive-saving moment. This is inherited gate
arithmetic under explicit hypotheses, not an independent proof of a global
coverage law. A changed owner schedule, merged operations or profile requires
a new complete ledger rather than a deduction of 44,096 units from this paper.

Decision: **narrow and stop implementation expansion**. The exact unresolved
item is an actual completed-call pair with one shared physical encoding and
legal helper/owner returns, or a priced changed transition that also changes
the failed complete gate. The current canonical source does not supply it.
