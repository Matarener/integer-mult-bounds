# Exact denominators of skew-path Cayley blocks

Produced by Nick Petalas. Apache-2.0.

## Claim and source boundary

This is a scoped written algebraic proof with finite exact corroboration.
It sharpens the arithmetic separation step in Ali Romman's
[PR #5339](https://github.com/CrocSwap/integer-mult-bounds/pull/5339), source
head `26fe40cbca6972a0e392e9248a9cb8a84368530b`. The predecessor supplies
the complete rational register grammar and the funded error implication in
its proof, sections 1 and 2. Those results are premises here. Its scientific
replay is not the deliverable and was not rerun.

The new result is the exact common denominator of each labelled path matrix,
including its necessary cancellation, and the resulting smaller sufficient
precision. It does not settle the predecessor's native-compatible execution
question or discharge a selected multiplication-framework assumption.

## 1. One connected block

Let K be the skew adjacency matrix of an n-vertex path. Its upper
off-diagonal entries are +1 and its lower ones are -1. Put

    O = (b I - a K)^(-1) (b I + a K),

where a,b are positive coprime integers. Let den(O) be the least positive
integer h for which hO is an integer matrix. Define

    D_0 = 1,  D_1 = b,
    D_n = b D_(n-1) + a^2 D_(n-2).

Then, for every n >= 1,

    den(O) = D_n / gcd(D_n, 2b).                         (1)

The same formula holds for O inverse. Signs on individual path edges do not
change it. One optional closed form is

    D_n = sum_(0 <= k <= floor(n/2)) binom(n-k,k) a^(2k) b^(n-2k).

These continuant and path-matching identities are classical. The exact
cancellation and its application to this witness interface are the step
established here; global literature priority is unclaimed.

### Proof of the denominator formula

Write M=bI-aK. Expansion along the last row gives det(M)=D_n. The recurrence
and positive a,b show D_n>0. Modulo a it gives D_n congruent to b^n.
Consequently gcd(D_n,a)=1.

Since bI+aK=2bI-M,

    O = 2b adj(M)/D_n - I.

Every numerator is divisible by h=gcd(D_n,2b). Hence multiplying O by
D_n/h gives an integer matrix. This proves that den(O) divides D_n/h.

For n>=2, the far-corner cofactor has absolute value a^(n-1). This follows
by successively expanding the minor obtained by deleting the last row and
first column. It is triangular along the unique path. Thus the off-diagonal
corner entry of O has absolute value

    2b a^(n-1) / D_n.

Its reduced denominator is exactly D_n/gcd(D_n,2b), because a and D_n are
coprime. Any common denominator must clear that one entry. This proves (1).
For n=1, K=0 and O=I; (1) gives b/gcd(b,2b)=1 as required.

Real skew symmetry gives O inverse = O transpose, so the denominator is
unchanged. For arbitrary signed unit path edges there is a diagonal matrix
S with entries in {+1,-1} such that K_signed=S K S. Conjugation by S
changes only entry signs, preserving the least common denominator. This
completes the proof.

## 2. Label runs and primitive scaling

The source uses t=A/B in reduced form and

    O_label(t) = (I-t K_label/2)^(-1) (I+t K_label/2).

Set g=gcd(A,2B), a=A/g and b=2B/g. Apply (1) to these coprime parameters.
Applying it directly to A,2B without cancelling g can give a false answer.
For example t=2/9 has a=1,b=9. A two-vertex block has denominator 41,
whereas the unscaled expression incorrectly gives 82.

Edges not carrying the selected label are absent in K_label. Its connected
components are the consecutive runs of selected edges, together with
isolated vertices. A run of ell edges has n=ell+1 vertices. The matrix and
its Cayley transform are block diagonal in these components. Therefore

    Q_label = lcm_(components c) [D_(n_c)/gcd(D_(n_c),2b)]       (2)

is the exact denominator of the entire label matrix and its inverse.
An isolated vertex contributes 1. Repeated component sizes contribute once
to the least common multiple. Distinct component denominators need not
divide one another, so replacing the lcm by a maximum is unsound.

At t=1/4, runs of two and one edges have denominators 33 and 65. Their
joint denominator is 2145. Two separate two-edge runs have denominator 33,
rather than 33 squared. These are denominator statements, not physical
component-sharing or free native-call claims.

## 3. The complete register lattice and separation

Retain the source grammar over Q. Every role is returned. Assignments read
old source values. Instructions are rational linear assignments, applications
of named O_label or its inverse, and

    dst += c O_label^(+/-1) src,

including src=dst. Across both programs, let C be the product of the positive
reduced denominators of every scalar-coefficient occurrence, exactly as in
the predecessor. Let the q named-call occurrences have labels a_1,...,a_q.
Define

    H = C product_(j=1,...,q) Q_(a_j).                      (3)

For every integral input bank, every returned difference coordinate has
denominator dividing H. Equivalently, the full rational linear bank map
has entries in H^(-1) Z. No role is assumed to be clean or discarded.
For inputs with common denominator U, replace H by UH.

To prove this, maintain a common denominator on each program side. At a
linear instruction multiply by the product of that instruction's scalar
denominators. At an application multiply by Q_label. At a query multiply
by Q_label and the coefficient denominator. The old destination and source,
including an alias, use the denominator before this multiplication. Unchanged
registers can be represented with the enlarged denominator too. Induction
proves the claim for each side. The product of the two side denominators
clears their difference and is (3).

In particular the predecessor's selected integral basis input satisfies

    f != 0  implies  |f| >= eta_new = 1/H.                  (4)

The integer H is a valid common denominator, not necessarily the least
denominator of a complete program. Compositions, cancellations and unused
directions can reduce it. Matrix-level sharpness in (1) does not imply
that (3), (4), or the final numerical precision is sharp.

## 4. Smaller sufficient grid with the same error contract

Use the predecessor's exact bank gains beta_i>=1 and entry-error gains
gamma_i. Write G=product beta_i, Gamma=max gamma_i, and m for the combined
instruction count. An empty product has G=1, and Gamma=0 when there are no
instructions. The cited error implication is

    |fhat-f| <= E 2^(-p),   E=m G (Gamma G+1),

for entrywise truncation of forward tables toward zero, transposed tables
for inverse calls, and one toward-zero data truncation per new coordinate.
All old-value and scalar-gain hypotheses remain in force. The only change
required in that implication is the sufficient choice

    2^p >= 4 max(1,E) H.                                  (5)

Equations (4) and (5) give error at most eta_new/4. Threshold eta_new/2
therefore distinguishes a zero selected endpoint from a nonzero one.
A zero at this input/output/parameter tuple is not a universal identity test.

For the original reduced A/B, each exact Q_label divides
det(2B I-A K_label). The predecessor bounds that determinant by (3B)^d.
Thus (3) never exceeds its coarse C(3B)^(dq). No claim asserts that H
divides that coarse numeric upper bound.

### A strict, fully specified fixture

Take t=1/4 and a path of nine vertices. Its eight edge labels, in spatial
order, are a,b,a,b,a,b,a,b. Each label has four two-vertex components, so
Q_a=Q_b=65. On one role apply b,a,b,a,b,a,b,a in chronological order.
Compare with the empty program. On input e_8 the coordinate-zero difference
is (16/65)^8. Reaching vertex zero in eight calls requires taking the
leftward edge at every call, so there is exactly one contributing route.

Here C=1, q=m=8, G=9^8, Gamma=9, and

    E=8*9^8*(9*9^8+1)=133417453941706320.

The old H bound is 12^72 and the new one is 65^8. The least integer p
satisfying each version of the same sufficient inequality is respectively
318 and 108. The reduction is exactly 210 fractional bits. The verifier
executes both dyadic grids and checks every returned coordinate against the
cited error budget. This is an explicit local guard improvement, not a
least-precision result or a performance measurement.

## 5. Scope and credit

The written proof covers every finite signed path and the stated rational
register grammar. Finite corroboration covers only the enumerated domains.
No source scientific census is rerun, and no predecessor theorem is audited.
No native Clifford binding, production precision policy, complete physical
cost, stock, tape, recursive compiler admission, new kappa, selected-frontier
change or complete multiplication theorem is established. Independent human
and formal proof-kernel review are unclaimed.

Credit Ali Romman #5339 for the separation/error consumer and #5315 for the
rational orthogonal witness, Krzysztof Wojt #5262 for the complete inverse
compiler and shortest-word theorem, zxv #5235 for the retained certificate
lineage, and all predecessor notices for dirty-echo/tensor/phase and
rational-series work. Cayley transforms, continuants, adjugates and integer
lattice separation are classical. The exact-denominator specialization,
precision refinement, proof and verifier were produced by Nick Petalas.
