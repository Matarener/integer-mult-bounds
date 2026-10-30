# Order seventeen and the sharp rank-eight response cap

Prepared by apoursh with substantial OpenAI Codex assistance. Apache-2.0.
The upper bound and Bell-spectator method are credited to Nick Petalas's
[PR6192](sources/pr6192-PROOF.md), head
`91df334ccd2a4bc9959e311f118ac8aaf967ffc2`; its Pauli-character step retains
Ross Richardson's credit. The new contribution is the explicit order-17
matrix, signed-generator certificate and rank-eight specialization.

## 1. Conventions and the four-qubit construction

Index the computational basis by integers `x=sum_j 2^j x_j`, with bits
`j=0,1,2,3`. Matrix products act rightmost first. Let

```text
Hg = (1+i)/2 [[1,1],[1,-1]],  S = diag(1,i),
A  = [[0,0,0,1], [0,0,1,0], [0,1,0,1], [1,0,1,1]],
U  = i S_3 CZ_03 CZ_12 CZ_23 Hg^(tensor 4).
```

All factors are Gaussian-dyadic unitaries normalizing the Pauli group;
therefore U is a Gaussian-dyadic Clifford. Because `Hg=e^(pi i/4)H`,
its fourth tensor power is `-H^(tensor 4)`. Consequently every matrix
entry is given explicitly by

```text
U[x,y] = (-i/4) i^(x_3)
         (-1)^(x_0 x_3 + x_1 x_2 + x_2 x_3 + sum_j x_j y_j).
```

The prefactor `-i` is part of the assertion. Replacing U by iU preserves
Cliffordness but changes its seventeenth power to iI and destroys Phi17.

Here is a complete integer certificate specification. Set `G=4U`, let
`P_0=I16` and `P_(j+1)=P_j G`, all over Gaussian integers. Exact
multiplication gives

```text
G G* = 16 I16,
P_17 = 4^17 I16,
sum_(j=0)^16 4^(16-j) P_j = 0,
Tr(G) = -4.
```

These are equalities of all 256 entries, not sampled vectors or floating
point residuals. `independent.py` evaluates exactly this unreduced integer
recurrence. `verify.py` separately reduces a common denominator after each
Gaussian matrix operation, and checks all powers U^j for j=0,...,17.
It additionally finds denominator four and trace -1 for every j=1,...,16.
Thus U has exact order 17 and satisfies the actual whole-bank primitive
relation `Phi17(U)=I+U+...+U^16=0`. Exact order follows because 17 is prime
and U is not the identity, as its trace is -1 rather than 16.

This is a complete finite certificate backed by explicit arithmetic, not
a formal-kernel verification or an extrapolation to unknown matrices.

## 2. Signed Pauli action

Use `X^x Z^z` in that order and Hermitian representatives
`P(x,z)=i^(sum_j x_j z_j) X^x Z^z`. Write binary labels as columns
`(x_0,...,x_3,z_0,...,z_3)`. Direct conjugation gives

```text
U X_j U* = Z_j,
U Z_j U* = i^(A_jj) X_j product_k Z_k^(A_kj).
```

Each displayed image is the positive Hermitian representative. Both
checkers verify all eight generator equalities as full complex matrices,
including their phases. Hence the induced binary symplectic map is

```text
S_U = [[0,I4],[I4,A]],
row masks = [16,32,64,128,129,66,164,216].
```

Its order is 17, its native upper-right block is `I4` of rank four,
and `rank(S_U-I8)=8`. For the last claim, a vector in its kernel has
`x=z` and `Ax=0`. A is invertible: `Av=(v3,v2,v1+v3,v0+v2+v3)`
vanishes only for v=0. Thus the kernel is trivial. These facts are also
checked over F2 without using floating point ranks.

## 3. Eight-qubit saturation

Let D be the four active qubits and E four identity spectators. Put

```text
V = (product_(j=0)^3 CNOT(j -> j+4)) (Hg^(tensor 4) tensor I16),
W = V^-1 (U tensor I16) V.
```

V and its inverse are Gaussian-dyadic Clifford circuits. Polynomial
evaluation commutes with tensoring an identity and with conjugation, so

```text
Phi17(W) = V^-1 (Phi17(U) tensor I16) V = 0.
```

This identity is on all 256 coordinates; the spectators need not be
initialized. It does not assert that their state is restored by a caller:
W generally couples the two registers. The proof avoids an unnecessary
dense 256-dimensional power computation by using the already certified
16-dimensional identity and these exact algebraic operations.

To compute the native block, order labels as `(x_D,x_E,z_D,z_E)`.
For input Z label `(d,e)`, V sends `(0,0,d,e)` to `(d,d,e,e)`.
The embedded active map sends this to `(e,d,d+Ae,e)`.
Applying V^-1 gives output X label

```text
(d+(A+I)e, d+e).
```

Therefore `B_W=[[I,A+I],[I,I]]`. If it kills `(d,e)`, the second
equation gives d=e and the first then gives Ae=0, so d=e=0.
Thus its rank is eight. Both checkers also build V from its individual
binary Hadamard/CNOT actions, perform the complete conjugation and
recover this block. The primary checker verifies symplecticity, order
and defect rank eight. Additional identity spectators preserve both
the polynomial relation and native rank eight for every M>=8.

## 4. Why eight is the cap

This is the n=17 specialization of Petalas's theorem, not a new general
upper-bound argument. A whole-bank Gaussian-rational Clifford T on M
qubits satisfying Phi17(T)=0 has characteristic polynomial `Phi17^t`,
where `t=2^(M-4)`. Indeed Phi17 is irreducible over Q(i), since
`[Q(zeta68):Q(i)]=phi(68)/2=16`. Thus M>=4 and `Tr(T)=-2^(M-4)`.

On the fixed space K of its binary Pauli action S_T, the signs of
Hermitian Pauli conjugation form a character. Their sum is the trace
of the adjoint action, namely `|Tr(T)|^2=2^(2M-8)>0`. A character
sum is either zero or |K|, hence `dim K=2M-8` and
`rank(S_T-I)=8`. The native B block is a submatrix of S_T-I, so
its rank is at most `min(M,8)`. Section 3 attains eight for every
M>=8. Four is the least possible active width; eight is the least
ambient width that can have an 8-by-8 full-rank native block.

The complete cited proof, including the character argument and its
classical field-degree source, is retained in
[the predecessor document](sources/pr6192-PROOF.md). Its pending status
does not imply maintainer acceptance. The concrete identities above
are checked independently of predecessor executable code.

## 5. Boundaries and failure controls

Finite order alone is insufficient. U tensor U has order 17, but

```text
Tr(Phi17(U tensor U)) = 16^2 + 16(-1)^2 = 272 != 0.
```

Other controls show that removing a CZ edge or omitting one polynomial
term fails Phi17; identity spectators without V leave native rank four;
an asymmetric proposed phase matrix is not symplectic; and the ordinary
companion matrix of Phi17 satisfies the polynomial but is not unitary.
These distinguish actual hypotheses rather than testing only that the
code can reproduce its own constants.

The displayed W uses 12 H-type factors (including inverse Hg), eight
CNOTs, three CZs, one S and a scalar phase i. This is only an algebraic
factor inventory. Whether those factors are native, how they align with
an actual producer/consumer, and their complete paid and target bill
are not established. There is no ownership/restoration certificate,
new supplier, new kappa or full multiplication theorem here.
