# A smallest binary carrier preserves the integer-shear target, but not its tariff

**Scoped representation and native XOR invoice; no supplier or new kappa.**
The least positive dimension of an F2-linear representation of the concrete
integer-shear group that distinguishes `B=X²Y²` from identity is **three**.
An explicit three-bit action sends B to the single XOR `b ^= c`. In this
carrier, the predecessor's four-label word shortens to two labels. Thus
preserving this nonidentity target does not preserve its formal call minimum.

This answers one finite-carrier part of [PR3937's handoff](https://github.com/CrocSwap/integer-mult-bounds/pull/3937#issuecomment-6260657318).
The original four-call theorem of [PR3905](https://github.com/CrocSwap/integer-mult-bounds/pull/3905)
remains valid in its formal group algebra. The new native boundary is already
encoded binary blocks. Converting arbitrary source-algebra data or a selected
multiplication caller into these blocks is **not supplied**.

## 1. Exact object and boundary

Retain the predecessor's integer matrices

\[
X=\begin{pmatrix}1&1\\0&1\end{pmatrix},\qquad
Y=\begin{pmatrix}1&0\\1&1\end{pmatrix},\qquad
G=\langle X,Y\rangle,\qquad
B=X^2Y^2=\begin{pmatrix}5&2\\2&1\end{pmatrix}.
\]

We minimize d over group homomorphisms `rho:G -> GL_d(F2)` with
`rho(B) != I`. Equivalently these extend linearly to unital algebra maps
`F2[G] -> M_d(F2)`. This is **module dimension**, not minimum dimension of
every possible algebra, nonlinear encoding or physical storage scheme.

The declared native module caller has two arbitrary dirty three-bit blocks:
`(a,b,c)` and `(p,q,r)`. Every elementary instruction `x ^= y`, with distinct
bit positions, costs one XOR. No operation is free, and no clean bit, erasure
or scratch is available. The desired endpoint applies `rho(B)` to the first
block and identity to the second. Inputs and outputs already use the specified
basis; conversion from a different caller remains an open obligation.

For the separate represented-label metric, the alphabet is exactly

\[
D_{N,g}=I_6+N\otimes(\rho(g)+I_3),\quad
g\in\{X,X^{-1},Y,Y^{-1}\},\quad
N\in M_2(\mathbb F_2),\quad \operatorname{rank}N=1,\ N^2=N.
\]

There are six such N and 24 allowed factors. Products of these factors are
counted; extra free endpoint transformations are not part of this metric.
The native XOR invoice below charges the actual gate lists and does not assign
one XOR to an opaque label call.

## 2. A genuine three-dimensional representation

Reduce the concrete integer matrices modulo 3, then act on the four projective
lines represented in order by `(1,0),(0,1),(1,1),(1,2)`. This is a group action
of the actual matrices, so no unproved presentation is being assumed. The
images of the four line indices are

\[
X:(0,1,2,3)\mapsto(0,2,3,1),\qquad
Y:(0,1,2,3)\mapsto(2,1,3,0).
\]

Let `e0,...,e3` be the standard basis of `F2^4`. Permutations preserve
`W={z:sum(z_i)=0}`, which has dimension three. Use the ordered basis

\[
w_0=e_1+e_3,\quad w_1=e_0+e_1+e_2+e_3,\quad w_2=e_1+e_2.
\]

Its vectors are independent and lie in W, so they are a basis. Restricting
the permutation action gives, with column vectors,

\[
U=\rho(X)=\begin{pmatrix}0&0&1\\0&1&0\\1&0&1\end{pmatrix},\qquad
V=\rho(Y)=\begin{pmatrix}1&0&1\\1&1&0\\1&0&0\end{pmatrix}.
\]

In particular

\[
U^3=V^3=I_3,\qquad
T=\rho(B)=U^2V^2=
\begin{pmatrix}1&0&0\\0&1&1\\0&0&1\end{pmatrix}\ne I_3.
\]

Thus T is exactly `b ^= c`. U and V do not commute. This gives an explicit
noncommutative algebra image escaping PR3937's commutativity hypothesis.

## 3. Why two binary dimensions cannot distinguish B

Every one-dimensional binary representation is trivial. For dimension two,
`GL_2(F2)` acts faithfully on the three nonzero vectors, hence is isomorphic
to `S3`. Its element orders are 1, 2 and 3, with a unique order-three subgroup.

In the concrete integer group let

\[
S=XY^{-1}X=Y^{-1}XY^{-1}=\begin{pmatrix}0&1\\-1&0\end{pmatrix}.
\]

Direct multiplication gives `S X S^-1=Y^-1`. For any homomorphism, the
images of X and Y therefore have the same order. If that order is 1 or 2,
their squares are identity, so the image of B is identity. If it is 3, both
images lie in the unique order-three subgroup and commute. Writing them
as U,V, the displayed relation gives `U² V^-1=U V^-2`, hence `UV=I` and
again `U²V²=I`. These cases exhaust `GL_2(F2)`.

The construction in section 2 and this obstruction prove the sharp answer
`d_min=3`. The verifier's enumeration of the six binary 2x2 invertible
matrices corroborates the argument; that enumeration is not the universal
proof by itself.

## 4. Exact label minimum and native invoice

Since U and V have order three,

\[
T=U^{-1}V^{-1}.
\]

Taking `N=E00` gives a two-factor realization of `diag(T,I3)` in the
represented alphabet. It is optimal in that exact alphabet: `rank(T-I3)=1`,
whereas every allowed one-call difference has rank
`rank(N)*rank(rho(g)-I3)=2`. The target is nonidentity, excluding zero calls.
This is not a new search over formal source words.

The following lists are chronological instructions on the first block:

| Map | Sequential instructions | XORs | Reason no shorter XOR list can implement it |
|---|---|---:|---|
| U | `c ^= a; a ^= c` | 2 | Two output coordinates change. |
| V | `a ^= c; c ^= a; b ^= c` | 3 | All three output coordinates change. |
| T | `b ^= c` | 1 | The endpoint is nonidentity. |

One XOR writes only one coordinate. Every coordinate whose output function
differs from its input must be written, proving these lower bounds. Reversing
each list implements its inverse at the same cost, with the same dirty-input
contract. The second block is untouched at every instruction.

Matrix products act rightmost first. The four-label source expression
`U U V V` therefore executes **V,V,U,U**, costing **10 XORs** if the four
labels are expanded separately. The shortened expression `U^-1 V^-1`
executes **V^-1,U^-1**, costing **5 XORs** before cancellation. Its literal list is

```text
b ^= c
c ^= a
a ^= c
a ^= c
c ^= a
```

The adjacent identical XOR pairs cancel, leaving exactly `b ^= c`. The
optimal direct native endpoint costs **one XOR**, has six arbitrary dirty
input/output bits, no scratch, no reset, and no spectator restoration work.
The raw 10/5 bills are not claimed to be native optima.

If a scalar role must literally contain an arbitrary matrix in `M3(F2)`, use
left multiplication column by column. Two roles then contain **18 dirty bits**;
the raw four/two-label lists cost **30/15 XORs**, while the direct endpoint costs
**three XORs**, one per column, and leaves the spectator's nine bits untouched.
The three changed output bits make that direct bill optimal in the same XOR
model. This is a different boundary from the six-bit module action, stated
explicitly rather than identifying a vector with an arbitrary matrix scalar.

## 5. Faithfulness and decision

The source algebra is not faithfully encoded. For example `X³ != I` as an
integer matrix, but `rho(X³)=I`. The nonzero formal element `[X³]+[I]` is in
the algebra-map kernel. This very alias changes `X²` into `X^-1` and explains
the four-to-two label shortcut. We do not construct a lossless encoder from
arbitrary source data or charge its unknown cost as zero.

[PR2599](https://github.com/CrocSwap/integer-mult-bounds/pull/2599) already
distinguishes group detection from faithful group-algebra action, using sharp
full-stream width thresholds and norm aliases. Its retained proof is credited,
not reproved. [PR2620](https://github.com/CrocSwap/integer-mult-bounds/pull/2620)
answers one GL2 width-one monomial-cost question with a different action and
alphabet. [PR2010](https://github.com/CrocSwap/integer-mult-bounds/pull/2010)
uses the full formal `F2[SL2(F3)]` with different labels and a mixed triple.
None is replaced by this target-specific minimum dimension and XOR invoice.

**Expansion decision: stop here.** A target-preserving noncommutative image
exists, but its label and native tariffs do not preserve the source minimum.
No larger formal-word search follows from this image. Any multiplication
application needs a new source-data/consumer contract, storage and conversion
costs, complete restoration, and the full supplier/recurrence inequality.
No selected supplier admission, all-size multiplication result or new kappa
is supplied.

## 6. Evidence and reproduction

The universal dimension theorem and native cost lower bounds are written
proofs. `verify.py` authenticates five retained inputs and checks exact integer
relations, the genuine finite quotient action and its products, the W-basis
maps, small-dimensional controls, all 24 paid factors, and complete dirty
endpoints. `test_verify.py` supplies independent semantic and damaged-input
controls. Exact recorded checks, environments and unrun obligations are in
`EVIDENCE.json`; no independent human or formal-kernel review is claimed.

```sh
python3.12 -B scripts/research_package.py --package research/sl2z-binary-carrier
```

The package is standard-library-only and standalone source exports can run
`python3.12 -I -B verify.py` and `python3.12 -I -B test_verify.py`. Original
relative links in retained source readmes refer to their source repositories.
`SOURCE-ORIGINS.json` binds those exact bytes and credits to their original
commits; no pending source commit must be fetched to replay this package.
`SOURCES.json` separately binds the task catalogue and selected-record provenance.
The orientation baseline command failed on absent selected inputs in the sparse
checkout, so selected bindings/full cold replay are unverified and unclaimed.

## Open next questions

Can a **target-specific, lossless source-data encoding and consumer** preserve
the useful operation and its complete price? First name a payload subspace,
injective encoder/decoder and legal caller for this same target, then prove
the commuting diagram and price conversion, storage, all dirty roles and return.
Stop if the target already has the one-XOR direct implementation in that model.
The finite image here supplies no such encoding. See the structured question
and stopping rule in `TASK.json`.

## Credit

- **1337isnot1337 / OpenAI Codex (macbook-02)**, PR3905,
  `b27bf4c72a822b21f483e08cb3241ad9d165b66f`: integer shears, target and
  valid four-call formal minimum; its verifier is retained unchanged.
- **ToikY with OpenAI Codex**, PR3937,
  `5ee1c9cee717e682db01bff4c398b87011a135a2`: commutative caller obstruction
  and released noncommutative-carrier handoff; retains eumemic/huxint and
  PR3914's distinct A5 perfectness context.
- **ywz65 with OpenAI Codex**, PR2599,
  `cfafdd633cf4e2e534704ec3ddd684cb0c32734f`: formal/full-stream faithfulness
  distinction, credited regular-orbit method and source notices. PR2620's
  distinct finite-caller analysis is also prepared for ywz65 with Codex.
- **Cinna Davis / 1337isnot1337 with OpenAI Codex**, PR2010,
  `125ed77d114e0db0cb2c684494c7a5c90f559d60`: distinct formal quotient work,
  linked above. No new general representation-theory method is claimed.

New target-specific proof, invoice and checks by **ToikY with substantial
OpenAI Codex assistance**, including separate AI implementation/review.
Apache-2.0. Frozen predecessors and the selected frontier are unchanged.
