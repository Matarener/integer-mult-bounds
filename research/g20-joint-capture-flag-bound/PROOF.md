# A flag bound for simultaneous first-read captures

Jerry Chen (@CubeJerry), with substantial OpenAI Codex assistance. Apache-2.0.

## Statement and scope

Fix the PR5708 word pinned in `SOURCES.json`. The 415 retained helpers are
non-owned wires with index at least 222: 413 have target rank 8, and
`P = {465, 684}` have target rank 4. Let `t = 1-C` be the **local BIT** moment
exponent and assume `99/100 <= t <= 1`.

Choose **any subset H** of helpers. Remove each chosen helper's independent
public input and target credit, hold it zero before its first ADD-source use
(dropping incoming writes and making its own queries free), and inject one
arbitrary native-linear payload immediately before that first read. Afterwards
keep the word's operations, making a query free only when its payload is zero.

Native-linear means a finite F2 sum of terms `M x_i`, with M a native invertible
address transformation, as in PR6113's payload model. It does **not** mean an
unrestricted linear operator that need not preserve constant functions.
Payloads use retained independent inputs. Grant injection, source access,
scalar operations, frame preparation, storage, final erasure and restoration
zero cost, and relax retained endpoint equations. These choices favor capture
under the inherited nonnegative-charge contract. There are no new contacts,
changed words, noncoordinate input contracts, later reinjections or jointly
extended dead intervals. The census checks that no helper has a paid query
after its last source read, so final erasure gives no additional query saving.

Let Δ be saved paid t-moment minus lost target t-moment and let d8 count the
chosen rank-8 helpers. Then

\[
\Delta\leq-\frac5{128}4^t d_8\leq0.
\]

The first inequality is strict if d8>0. For subsets of P alone it is only a
non-improvement bound, consistent with the predecessor's neutral helper 684.
No new κ. This is a written proof with an exact finite certificate, not a
formalization of the multiplication theorem or enumeration of payload guesses.

## 1. Necessary parity equations

A native address permutation fixes the constant-one function. Evaluation on
constant input functions therefore sends a finite F2 sum of native terms to
the parity of its input labels: ADD becomes XOR, Q/ZERO_Q preserve the row,
and ERASE zeros it. This is the augmentation homomorphism of the native
operator algebra. Native zero implies projected zero; the converse is unused.

Original owned inputs are zero. The census temporarily gives them independent
labels and checks that none appears in any of the 2,846 paid query rows, so
discarding those labels changes none of the certificate rows. Every paid row
is nonzero. Frame chronology, query ranks and the published paid profile are
checked, but native operator identities and endpoints are not reproved.

## 2. First reads give a graph kernel

Let V have the 637 original non-owned input labels as basis. Before helper h's
first source read, its label x_h has never left that wire. Its projected base
value is `x_h + a_h`, with no still-unread helper label in a_h.

Process captures chronologically. Define L to fix retained inputs. At h's
capture set `L(x_h)=f_h=w_h+L(a_h)`, where w_h is its projected injected payload.
All labels in a_h are retained or belong to earlier captures, so f_h uses
retained inputs only. Outside a chosen helper's held-zero prefix, its modified
projected value is L of its base value. Indeed, a held-zero helper has no
outgoing ADD, so dropping its writes affects no other wire; the capture
equation establishes agreement at first read, and subsequent operations
preserve it. This induction holds for every subset and payload.

Thus `R=ker L` has basis `{x_h+f_h : h in H}` and projection R→coordinates H
is an isomorphism. Every removed query outside an owned held-zero prefix has
its base row in R.

Partition helpers into P, F, O. P is the two partial helpers. F is the 180
rank-8 helpers with an early own rank-2 query. O is the other 233 rank-8
helpers. The census checks at most one early own query per helper, of rank 1
or 2, and none for P. Write dP=|H∩P|, and similarly dF,dO. The graph property
implies

\[
\dim R=d_P+d_F+d_O,\quad
\dim(R\cap\{v_P=0\})\leq d_F+d_O,\quad
\dim(R\cap\{v_P=v_F=0\})\leq d_O.
\]

Indeed, projection onto H is injective and the indicated coordinates vanish;
zeros on retained helper coordinates can only lower these dimensions further.
These stronger bounds distinguish cheap partial targets and costly early
frees; an unweighted |H|-only bound does not use them.

## 3. Cover early cross-helper effects

Grant held-zero-prefix savings separately, at most `2^t dF + dO`. This even
grants an H1 to each of O's 111 helpers without an early query. Other removed
queries must contain a helper label, since L fixes non-helper inputs.

An early query on an unchosen helper can disappear through a *different*
chosen helper. Keep an early query in the token census whenever its row
contains another helper label. These three events (zero-based) qualify:

| Event | Destination | Rank | Helper-label support |
| --- | ---: | ---: | --- |
| 6231 | 467 | 1 | 274, 467 |
| 6291 | 297 | 1 | 297, 465 |
| 6510 | 464 | 1 | 323, 464 |

Other early own queries can be omitted: if their destination is chosen they
are already granted free; otherwise L fixes their nonzero row. Double counting
a cross-helper query in the free allowance and token bound is harmless for an
upper bound. This leaves **2,216 eligible queries and 1,945 distinct rows**.
PR6113's printed census had 2,213: the three-query difference is intentional
coverage, not a claim that its numerical pair results are false. A negative
control omits event 6291's tokens and must fail exact coverage.

## 4. The finite flag certificate

For query ranks r=1,2,3,4,5,6 use respectively m(r)=17,33,49,64,80,96 copies
of the row. Throughout the stated interval, `r^t <= m(r)4^t/64`. For r<4,
`(r/4)^t` is largest at t=99/100; integer inequalities
`r^99 64^100 <= 4^99 m(r)^100` certify the claim. For r>=4 use
`(r/4)^t <= r/4 = m(r)/64`. No floating-point acceptance is used.

`PARTITION.json.gz` partitions all **64,274 tokens into 108 colors**:

| Colors (zero based) | Count | Allowed rows |
| --- | ---: | --- |
| 0–63 | 64 | unrestricted |
| 64–91 | 28 | zero on P |
| 92–107 | 16 | zero on P and F |

Each color is F2-linearly independent. Rows are reconstructed from the word;
every token multiplicity and flag is checked, and independence is checked by
both highest-pivot and lowest-pivot elimination. IDs are the increasing integer
order of distinct eligible rows. The witness suffices; no optimality or search
completeness claim is made about the discovery algorithm.

An independent set meets a subspace in at most its dimension. Summing the
three graph-kernel dimension bounds across colors yields

\[
\text{non-prefix savings}\leq4^t
\left(d_P+\frac{92}{64}d_F+\frac{108}{64}d_O\right).
\]

This single certificate covers all `2^415` ownership sets. They are not
enumerated, and 108 is not asserted to be the minimum number of colors.

## 5. Optimistic complete budget

Lost target credit is `4^t dP + 8^t(dF+dO)`. Add prefix savings and subtract
that debit:

\[
\Delta\leq4^t\left[
\left(\frac{92}{64}+2^{-t}-2^t\right)d_F+
\left(\frac{108}{64}+4^{-t}-2^t\right)d_O\right].
\]

Exact integer powers establish, on the full interval,
`2^t > 127/64`, `2^(-t) < 65/128`, and `4^(-t) < 33/128`.
For example the first is checked at the lower endpoint by
`2^99 64^100 > 127^100`; the reciprocal inequalities are checked similarly.
Both coefficients are strictly below -5/128:
`184+65-254=-5` and `216+33-254=-5`. This proves the statement. Charging actual
setup, source reads, frame changes, copies, erasure, restoration or recursive
children cannot reverse this failed optimistic budget if they add nonnegative
charges without changing the stipulated word or contract.

## Limits and evidence status

This closes the larger-set question for **individual first-read schedules on
this exact word**, including both partial helpers. Joint deadness can permit
later capture after a helper has influenced other wires; then a single entry
substitution need not apply. Changed words, other input subspaces, unrestricted
non-native-linear payload operators and other exponents remain outside scope.

The projection implication and triangular argument are written mathematics,
not Lean proofs. Seven deterministic payload/subset fixtures exercise the
lemma but do not prove it. Two row representations and opposite elimination
pivots reduce implementation dependence; they are not external peer review.
The native/adjoint endpoint and complete caller were not replayed. No recursive
supplier was built, and the selected theorem's native, owned-erasure, compiler,
precision/tape and analytic-recovery assumptions remain unchanged.
