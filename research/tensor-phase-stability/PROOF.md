# Sharp recovery from tensor-square and tensor-cube tests

Let A and B be unitary operators on the same nonzero finite-dimensional
complex Hilbert space. All norms below are operator norms. Suppose

    ||A^(tensor 2) - B^(tensor 2)|| <= epsilon,
    ||A^(tensor 3) - B^(tensor 3)|| <= epsilon,    0 <= epsilon <= 2.

Write a = arcsin(epsilon/2) in [0,pi/2] and

    epsilon_* = 2 sin(pi/5) = sqrt((5-sqrt(5))/2).

Then the best possible dimension-independent bound is

    ||A-B|| <= F(epsilon),

    F(epsilon) = 2 sin(a/3)             if 0 <= epsilon < epsilon_*,
                 2 sin(pi/3 + a/3)      if epsilon_* <= epsilon <= 2.

Every value of the envelope is attained by scalar unitaries, including in
any fixed positive dimension. The weak inequality belongs to the second
branch. At the threshold a scalar fifth-root phase attains

    F(epsilon_*) = 2 sin(2pi/5) = sqrt((5+sqrt(5))/2).

The left limit is 2 sin(pi/15). Thus the sharp envelope has a jump. This
is a scoped analytical theorem, not a source-word or multiplication theorem.

## Reduction to one phase

Put U = B* A. Unitary invariance and tensor multiplicativity give

    ||A-B|| = ||U-I||,
    ||A^(tensor j)-B^(tensor j)|| = ||U^(tensor j)-I||, j=2,3.

For each eigenvalue z of U, the tensor power has eigenvalue z^j by taking
the same eigenvector in every factor. Consequently |z^2-1| and |z^3-1|
are at most epsilon. The spectral theorem gives
||U-I|| = max_z |z-1|. It suffices to solve the scalar problem. Conversely,
U=zI attains any scalar feasible value in every positive dimension, so
this reduction loses nothing in the dimension-independent optimum.

## Exact feasible arcs

Conjugation preserves all three distances. Write z=exp(i theta) with
0 <= theta <= pi. The width-two constraint is

    |z^2-1| = 2 sin(theta) <= 2 sin(a),

so theta lies in [0,a] or [pi-a,pi]. The width-three constraint is

    |z^3-1| = 2 |sin(3theta/2)| <= 2 sin(a),

so theta lies in

    [0,2a/3] union [2pi/3-2a/3, 2pi/3+2a/3].

These formulas include the endpoints a=0 and a=pi/2. No other interval
meets [0,pi]. The largest feasible point in the first width-two interval
is at most a. Its first width-three component ends at 2a/3.

The second width-two interval meets the second width-three interval
exactly when

    pi-a <= 2pi/3+2a/3, equivalently a >= pi/5.

The first width-two interval can meet the second width-three interval
only if a >= 2pi/5. It therefore cannot create another component below
the threshold pi/5. The second width-two interval cannot meet the first
width-three interval, since that would require a >= 3pi/5.

For a < pi/5 the largest feasible theta is therefore 2a/3. It is
feasible because 2a/3 <= a. For a >= pi/5 the largest feasible theta is
2pi/3+2a/3. It is at most pi, belongs to [pi-a,pi], and exceeds every
point in [0,a]. Since |z-1|=2 sin(theta/2) increases on [0,pi], the two
claimed branches follow. Choosing the displayed largest theta proves
attainment. At a=pi/5 it is 4pi/5, giving a nontrivial fifth root of unity.

## Exact algebraic certificates

The squared threshold s_*=(5-sqrt(5))/2 is the smaller root of

    s^2 - 5s + 5 = 0.

For rational s in [0,4], s<s_* exactly when s<5/2 and s^2-5s+5>0.
There is no rational equality case. The verifier handles equality
separately in Q(sqrt(5)), rather than rounding the threshold.

Write T=F(epsilon)^2 and s=epsilon^2. The triple-angle identity yields

    T(3-T)^2=s,   0 <= T <= 1,   on the low branch;
    T(T-3)^2=s,   3 <= T <= 4,   on the high branch.

Each polynomial is strictly increasing on its stated interval, except
for an endpoint derivative equal to zero, which does not affect unique
root selection. Both range over [0,4]. Exact rational bisection therefore
encloses T without trigonometric evaluation. The Q(sqrt(5)) witness has
cos(theta)=-(1+sqrt(5))/4 and T=(5+sqrt(5))/2. Its square and cube defects
both have square s_*. Chebyshev's identity T5(cos(theta))=1 checks its
fifth-root phase algebraically.

## Consequences and scope

Exact agreement at widths two and three forces A=B and hence agreement
at every positive tensor width. Width two alone does not suffice, as
A=-B shows. These exact facts are elementary; the new application here
is the full sharp error envelope and its fifth-root threshold.

Approximate agreement at two finite widths does not supply a uniform
small error over every width. For example, scalar phases approaching
one pass arbitrarily tight tests while some later tensor powers approach
phase minus one. A separately specified all-width error budget remains
necessary. No claim is made about every noisy chart being a tensor power
of one fixed unitary. Nonunitary, independently rounded and projective-only
comparisons are outside the hypotheses.

The source of the question is unpaidmoon's PR #5837, head
764e7bd6d615d92019445bec92e2a473af021878, which gives a width-two sign
counterexample. DLamdata's PR #5894 separately reports that the selected
native checker already fixes absolute phase using its |0> image. This
package neither audits those claims nor asserts missing phase coverage.
It supplies a quantitative diagnostic for comparisons where the stated
two tensor operator-norm premises have actually been established.

Classical spectral theory and elementary trigonometry supply the method.
No general literature priority is claimed. This proof and its verifier
were produced by Nick Petalas. Independent human and formal proof-kernel
review are unclaimed. Apache-2.0.
