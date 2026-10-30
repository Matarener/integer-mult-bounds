# Rigidity of independent scalar-role recodings

This scoped written proof was produced by Nick Petalas. Apache-2.0.
The finite checker corroborates the statements; it is not their universal
proof or a proof-kernel certificate.

## 1. Exact contract

Let F be any field. Let G be a finite directed graph with at least two
vertices, no loops, and connected underlying undirected graph. An edge
e=(j,i) means that role i is updated from the distinct role j. Assign a
fixed coefficient b_e in F\{0} to each edge.

For every vertex v choose a bijection f_v:F->F with f_v(0)=0. These maps
are fixed throughout the program. The input to each gate ranges over all
of F^2, including arbitrary dirty values. Let Phi act on a state by applying
f_v to each scalar in role v. Require the conjugacy

```text
Phi ADD_{i<-j}(1) Phi^-1 = ADD_{i<-j}(b_e)                (1)
```

for every specified edge, where ADD_{i<-j}(b) updates x_i by b*x_j and
preserves every other coordinate. Equivalently,

```text
f_i(x+y) = f_i(x) + b_e*f_j(y)  for every x,y in F.       (2)
```

The maps need not be continuous, measurable, differentiable or polynomial.
Equation (2) is a gatewise requirement on independent values, not a finite
trajectory test. An instruction graph records required gate compatibilities;
its edges need not occur in every orientation or at every time.

## 2. Classification

**Theorem 1.** Equation (2) holds for every edge if and only if there are
nonzero weights s_v in F and one additive bijection H:F->F such that

```text
f_v(z) = s_v*H(z),              b_(j,i) = s_i/s_j.        (3)
```

Choose a root r and normalize s_r=1. Then H=f_r and every s_v is unique.
Equivalently, compatible maps exist exactly when the product of edge labels
along every undirected closed walk is one. Reverse traversal uses b_e^-1.

*Proof.* In (2) put x=0. Zero preservation gives f_i(y)=b_e*f_j(y).
Substitution into (2) gives f_i(x+y)=f_i(x)+f_i(y). Thus f_i is additive,
and f_j=b_e^-1*f_i is additive. Every vertex is incident with an edge,
because the graph is connected and has at least two vertices.

Starting at r, traverse any undirected path. The equality f_i=b_e*f_j
gives f_v=s_v*f_r, with s_v equal to the product of b_e or b_e^-1 on that
path. Each f_r is onto and nonzero, so two scalars multiplying f_r give the
same function only when the scalars agree. Therefore path products are
independent of the path; every closed-walk product is one. This proves
necessity, uniqueness and (3).

Conversely, closed-walk consistency defines the nonzero s_v by path
products, and makes every edge label s_i/s_j. Choose any additive bijection
H, for example the identity. Then

```text
s_i*H(x+y) = s_i*H(x) + (s_i/s_j)*s_j*H(y),
```

which is (2). This also proves the converse for every prescribed family
of the form (3). A spanning tree suffices to compute the weights; each
remaining edge is a scalar consistency check. No nonlinear search is needed.

The characterization applies separately to every nontrivial connected
component. An isolated vertex has no ADD constraint and may have an arbitrary
zero-preserving bijection. Strong connectivity is unnecessary.

## 3. One phase compatibility fixes the coefficient field

Now let F=C. Suppose, in addition, that one role r satisfies the unchanged
quarter-turn compatibility

```text
f_r(i*z) = i*f_r(z)  for every z in C.                   (4)
```

The role need not be the chosen root. From f_r=s_r*H and s_r!=0, (4)
implies H(i*z)=i*H(z). Additivity implies integer homogeneity and rational
homogeneity: n*H(z/n)=H(z) for every nonzero integer n. Hence

```text
H(a*z) = a*H(z)  for every a in Q(i).                  (5)
```

Thus H is Q(i)-linear. This is an algebraic conclusion; it does not assert
complex linearity or that H is multiplication by a complex scalar.

The distinction is real. On Q(i,sqrt(2)), the automorphism
H(a+b*sqrt(2))=a-b*sqrt(2), a,b in Q(i), is Q(i)-linear and bijective,
but is not multiplication by a scalar. A Q(i)-basis containing 1,sqrt(2)
extends this to a Q(i)-linear bijection of C by fixing the other basis
vectors. This existence example requires no computable encoding of arbitrary
complex numbers, and is not a proposed physical operation.

## 4. Consequence for Gaussian-dyadic native programs

Apply f_v pointwise to the scalar entries of each finite role array.
The same function is used at every address of that role. For every finite
matrix M with entries in Q(i), (5) and additivity give

```text
H(M*x) = M*H(x),
```

where H acts entrywise. This includes Gaussian-dyadic coefficients and
every finite tensor power of such a matrix. Multiplication by s_v also
commutes with M within role v. Therefore every one-role native instruction
M is unchanged by its role recoding f_v.

**Corollary 2.** Consider a fixed exact word of unit ADDs and one-role
Q(i)-matrix instructions. Suppose its ADD graph is connected, (1) holds,
and one role has (4). Replace the recoding f_v by the scalar recoding
z->s_v*z. The resulting recoded word has exactly the same native operators,
the same scalar ADD coefficients b_e, the same chronology and the same
all-input endpoint as with the original f_v.

*Proof.* Theorem 1 gives the ADD coefficients. The preceding commutation
identity gives the native operators. Thus the two conjugated words have
identical instructions. Equivalently, if A is the original whole linear
endpoint, D repeats s_v on every address of role v, and Phi is the nonlinear
pointwise recoding, then

```text
Phi A Phi^-1 = D A D^-1.                                (6)
```

Indeed H commutes with A entrywise, since the finite whole endpoint is a
Q(i)-matrix. This calculation also covers every finite array width and
tensor multiplicity. It does not infer a uniform physical implementation
from finite computations.

In particular, arbitrary dirty restoration x_v->x_v remains restoration,
zero owned fields remain zero, and all native paid labels are unchanged.
Every recoded word in this class has a scalar-gauge counterpart with the
same endpoint and native profile. Scalar gauges themselves are allowed
recodings, so the sets of attainable endpoints/profiles are equal.

This is a native-profile statement. Ordinary scalar coefficient costs,
encoding/decoding, precision, storage and movement retain their own costs.
If allowed coefficients are restricted, the counterpart uses exactly the
same b_e as the proposed recoded word. Boundary weights do not become free
physical instructions. No productive target or recursive invoice gain
follows merely from the conjugacy.

## 5. Boundaries and exact counterexamples

- Without zero preservation, translations on a sink survive. Over F5, take
  f_source(x)=x and f_target(x)=x+1. Equation (2) holds with b=1, but (3)
  fails at zero. An affine version would require a separate statement.
- Without connectedness, an isolated role can carry a nonadditive bijection.
  Independent nontrivial components may also use different additive maps.
- Additivity does not imply (4). Complex conjugation preserves ADD but sends
  i to -i. Over F9, Frobenius x->x^3 gives a finite counterpart.
- Phase compatibility does not imply additivity. The F9 checker enumerates
  every zero-preserving permutation and supplies phase-only witnesses.
- Pointwise recoding matters. Swapping two addresses is Q(i)-linear but
  does not commute with the address operator diag(1,2).
- Changing the recoding at different occurrences, changing a native
  instruction, using input-dependent coefficients, approximate identities,
  nonzero translations, or restricting reachable inputs changes the contract.
  General nonlinear circuits and finite-grid rounded implementations are
  outside the theorem.

The shared-map scalar condition in Cinna Davis's PR #4983 is a predecessor,
not a new claim here. The new application permits independent maps on every
role and changed edge coefficients, then identifies their complete residual
freedom and the Gaussian-native consequence. Cauchy's functional equation,
spanning-tree gauge consistency and linear-map commutation are classical.
