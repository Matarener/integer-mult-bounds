# Exact additivity for two anticommuting query types

This is a scoped algebraic proof. All fields, role counts and matrix sizes below
are finite. No physical Gaussian realization or complete multiplication theorem
is asserted.

## Model and theorem

Let K be any field of characteristic different from two. Fix a nonempty finite
list of positive integers d_c and the ordinary coefficient algebra

    A = product_c Mat_(d_c)(K).

The payload operator algebra is H = A tensor_K Mat_2(K). Write

    Q = I tensor [[0,1],[1,0]],   R = I tensor [[1,0],[0,-1]].

Thus Q^2 = R^2 = I, RQ = -QR, and H is the direct sum of the four left
A-modules A, AQ, AR, AQR. The result also holds in any faithful realization
of this algebra. Faithfulness means equality on all payloads distinguishes
these four A-coefficients. It is a hypothesis, not a finite-width inference.

A program has arbitrary independent source fields x_1,...,x_n and arbitrary
independent receivers y_1,...,y_m. Borrowed fields are arbitrary and must be
restored. Owned fields start at zero and must return zero. The allowed ordinary
instructions are finite A-linear maps on the fields, including accumulation
and clearing owned fields. One paid query applies Q or R to one whole field.
Each inverse has the same price, since both queries are involutions. Arbitrary
linear feedback, overwriting, retention and interleaving are allowed. The
ordinary algebra excludes Q and R and excludes choosing a different query type
in different components of one paid call.

For matrices A0,B,C in Mat_(m by n)(A), require the full endpoint

    x stays x,   y becomes y + (A0 + BQ + CR)x,

with every borrowed field restored and every owned field zero. There is no QR
coefficient in this target. Expand B and C in component c to scalar matrices
B_c,C_c of size (m d_c) by (n d_c), and define

    k_B = max_c ceil(rank_K(B_c)/d_c),
    k_C = max_c ceil(rank_K(C_c)/d_c).

**Theorem.** Every admissible program uses at least k_B queries of type Q and
at least k_C queries of type R. One program attains both bounds at once. Hence
the exact minimum total is k_B+k_C. For positive prices w_Q,w_R the exact
minimum charge is w_Q k_B + w_R k_C.

## 1. One-query rank lemma

Let E be a unital ordinary algebra and suppose the represented operator algebra
is the direct sum E + ET, with T^2=I and T e = sigma(e) T for an automorphism
sigma of E. Initially the ET-coefficient row of every arbitrary original input
and every zero owned field is zero. Ordinary E-linear instructions only combine
existing ET-coefficient rows. A T query creates one new such row, regardless of
whether it overwrites a field or uses a retained field.

Record the new row at each of the q query occurrences for this proof only.
Induction over instructions puts every final ET row in their E-linear span.
Therefore the final ET matrix factors through q E-rows. Restricting its columns
to the original source fields preserves that factorization. This argument
includes arbitrary receiver and borrowed inputs; it never assumes they vanish
in the actual program. Clearing is an E-linear map and preserves the span
statement. No runtime bank retaining all q rows is assumed.

For E = product_j Mat_(e_j)(K), any factorization through q E-rows expands to a
factorization through q e_j scalar coordinates in component j. Its component
rank is at most q e_j. Conversely, scalar rank factorizations, padded to q e_j
middle coordinates and assembled into e_j by e_j blocks, attain

    inner_rank_E(D) = max_j ceil(rank_K(D_j)/e_j).

This is ordinary finite-dimensional rank factorization. The proof of the
present theorem does not require replaying any predecessor implementation.

## 2. Count Q even when R is free

Enlarge the ordinary algebra, solely for a lower bound, to

    E_R = A + AR.

Its projectors (I+R)/2 and (I-R)/2 give the explicit isomorphism
E_R -> A times A, a+bR -> (a+b,a-b). Every original ordinary instruction and
every R query is E_R-linear. Q normalizes E_R by a+bR -> a-bR. Moreover
H = E_R + E_R Q is a direct sum. The one-query lemma thus applies to the
number q_Q of Q queries in the original program, with all R queries granted
for free in this relaxation.

The target's E_R Q coefficient is exactly B. Its two components are (B,B),
so its expanded ranks in both copies of component c equal rank_K(B_c).
Consequently q_Q >= k_B. The receiver identity and the A0+CR part are E_R-even
and create no extra odd coefficient. Restoration requirements remain in the
full endpoint.

## 3. Count R even when Q is free

Use E_Q = A + AQ and its projectors (I+Q)/2 and (I-Q)/2. Now H = E_Q + E_Q R,
and R normalizes E_Q by a+bQ -> a-bQ. The target's E_Q R coefficient is C,
embedded as (C,C). The same argument gives q_R >= k_C. These are simultaneous
inequalities for each original program, so their sum is a valid lower bound.
They are not alternatives between which a program may choose.

## 4. Attain both bounds with one owned query field

Choose component rank factorizations B_c=L_c V_c, padding each middle dimension
to k_B d_c. Reassemble the blocks to get B=L V through k_B A-rows. For row j:

1. In a zero owned field h, accumulate h = sum_a V_(j,a) x_a.
2. Apply Q once to h. Since Q commutes with A, h = sum_a V_(j,a) Q x_a.
3. For each receiver i, add L_(i,j) h to y_i.
4. Clear h to zero.

Repeat for every row, then do the same for a k_C-row factorization of C using
R. Accumulate A0x ordinarily. The original source bank never changes, receiver
values remain arbitrary, and borrowed fields are untouched. All owned storage
returns zero. The sequence uses exactly k_B Q queries and k_C R queries, and
only one owned query field at a time. Its routing operations still have cost;
only the query count is optimized here. If actual A coefficients require an
evaluator, its workspace and literal words must be charged separately.

## 5. A sharp sector accounting gap

Take A=K times K and n=m=1, B=(1,0), C=(0,1), A0=0. In the first component
only Q is needed, and in the second only R is needed. Each component alone has
query total one, but the complete contract needs two calls. Thus

    max_c (ceil(rank(B_c)/d_c) + ceil(rank(C_c)/d_c)) = 1

is not the correct global answer. The sum of the two maxima is two. A paid
operation that conditionally chooses Q in one component and R in the other
would change the alphabet and defeat this example. It is expressly excluded.

For a noncommutative packing example, take A=Mat_2(K), n=m=2 and
B=C=diag(E_11,E_11). Both expanded ranks are two, so the minimum is two calls,
one of each type. Matrix units pack the two same-type demands into one field;
they do not turn the two different query types into one call.

## Scope, novelty and remaining obligations

This answers the faithful anticommuting-involution specialization of RQ09 in
David Ganz's PR5803, at head 0acda5ab421d28b98fdf916968696c8f9453376f.
R03-R06 there supply the single-query inner-rank framework and noncommutative
matrix-block motivation. Ali Romman's PR5626 supplies the earlier faithful
ordinary-sector query compiler. Their algebraic methods and the classical
matrix-rank ingredients retain credit. The new step is the simultaneous
opposite-type relaxation, exact two-type tariff and sharp sector conflict
example. No worldwide novelty claim is made for classical Clifford algebra.

The theorem does not cover a nonzero QR target coefficient, characteristic two,
a nonfaithful payload action, ordinary maps outside A, nonlinear instructions,
selectable per-component query types, or queries on several fields at once.
It does not assert that actual Gaussian queries anticommute. Finding a lawful
native realization, physical coefficient words, input/output matchers, paid
movement, precision, restoration, stock, productive targets and a complete
signed invoice remains a separate task. The proof is informal; finite checks
corroborate it and do not discharge its universal quantifiers in a proof kernel.
