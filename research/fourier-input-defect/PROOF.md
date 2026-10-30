# The exact input-dimension price of a mismatched Fourier layout

This scoped proof was produced by Nick Petalas. It changes the second-input
contract of Hanson Sun / bbMisk's PR #1477. Its full-input convolution criterion
and Ross Richardson's unweighted PR #940 are predecessor results, not claims
rechecked here. The cycle argument below is classical weighted-permutation
linear algebra. The contribution is the exact maximal-input contract, its
sharp codimension and the resulting unequal-layout convolution construction.

## 1. Contract

Let G be a finite abelian group of order N with a nondegenerate symmetric
character pairing chi. Use the predecessor's normalization

    F^-u(y) = (1/N) sum_x chi(-y,x) u(x),
    F^+u(x) = (1/N) sum_y chi(x,y) u(y).

Then F^+ F^- = I/N. Let tau be any permutation of G.
Let alpha and beta be fixed unit complex functions, and put h=alpha beta.
Use read permutations P_tau g(y)=g(tau(y)). Consider

    B(u,v) = F^+ [ (D_alpha F^-u) . (D_beta P_tau F^-v) ].

Here . is coordinatewise multiplication and convolution * is unnormalized.
The first input u is unrestricted. The second input v ranges over a complex
linear subspace V. The question is which V satisfy

    B(u,v) = (u*v)/N^2                 for every u and every v in V.   (1)

Only the second forward read map and the two forward weights change. The
first forward read map and the final Fourier map stay in their standard
charts. No free physical implementation of any change is assumed.

## 2. The maximal space and its exact dimension

For a permutation cycle C define H_C=product_(y in C) h(y). Write b(tau,h)
for the number of cycles with H_C=1, including singleton cycles. Define

    K = {g in C^G : g(y)=h(y)g(tau(y)) for every y},
    V_max = (F^-)^-1 K.

**Theorem.** Equation (1) holds if and only if V is contained in V_max.
Moreover,

    dim_C V_max = b(tau,h),
    codim_C V_max = N - b(tau,h).                                  (2)

Every allowed dimension up to b is attained by a subspace of V_max. Thus
(2) is the exact number of independent complex input dimensions that must
be removed for these fixed maps and weights. It is not a paid-call count.

**Proof.** The convolution theorem in the stated normalization gives

    F^+ [(F^-u).(F^-v)] = (u*v)/N^2.

Since F^+ is invertible, (1) is equivalent, at each y, to

    (F^-u)(y) [ h(y)(F^-v)(tau(y)) - (F^-v)(y) ] = 0.               (3)

Choosing u=delta_0 makes every first factor 1/N. Consequently (3) for all
u is equivalent to F^-v belonging to K. This proves both directions and
the maximality assertion. An arbitrary subset of inputs also satisfies
(1) precisely when it is a subset of V_max.

On a cycle C=(y_0,...,y_(ell-1)) with tau(y_j)=y_(j+1), set g(y_0)=c.
The equations determine

    g(y_j) = c / product_(k=0)^(j-1) h(y_k).

Closing the cycle requires c=H_C c. If H_C differs from one, c=0. If
H_C=1, c is arbitrary and contributes exactly one complex dimension.
Cycles have disjoint support, so their dimensions add. Fourier inversion
preserves dimension. This proves (2). For each balanced cycle, the above
vector with c=1, zero off C, gives an explicit basis vector g_C of K;
the vectors N F^+g_C give an attaining basis of V_max. QED.

The formula recovers full-input rigidity in this fixed chart. Dimension N
is possible exactly when every cycle is a singleton and its phase is one,
that is, tau=id and h=1 pointwise. Nonconstant alpha remains possible when
beta=alpha^-1. This does not address the predecessor's separate contract
in which the same weighted routine also determines the inverse map.

## 3. Translation layouts become character-level sparse inputs

Let tau(y)=y+b and let h(y)=lambda be constant of modulus one. If b has
order d, every permutation cycle has length d. The theorem gives

    dim V_max = N/d if lambda^d=1, and 0 otherwise.                 (4)

More explicitly,

    V_max = {v : supp(v) is contained in
                 {x in G : chi(b,x)=lambda}}.                     (5)

Indeed, on the time coordinate delta_x, translation of its negative-sign
Fourier character multiplies it by chi(-b,x). The kernel equation is
lambda chi(-b,x)=1, equivalently chi(b,x)=lambda. Those time coordinates
form a basis, so they prove (5). Nondegeneracy makes x -> chi(b,x) a
character of order d. Its image is all d-th roots, and each level has
N/d points, also proving (4) directly.

For a concrete nonzero-output construction, take G=(Z/4)^2 with the usual
pairing, b=(1,0), and lambda=i. Then

    V_max = {v : v(x_0,x_1)=0 whenever x_0 is not 1},
    dim V_max = 4, codim V_max = 12.

For every arbitrary sixteen-coordinate u and every such four-coordinate
v, reading the second negative Fourier spectrum at y+(1,0), multiplying
that forward product by i, and applying the unchanged positive Fourier
map computes (u*v)/256 exactly. The bound is sharp for this fixed wrapper:
no five-dimensional complex linear second-input space works. Alpha and
beta may split the factor i arbitrarily, as only their product occurs.

This permits unequal read maps on a quantified sparse-input contract. It
does not permit the same change on arbitrary second inputs, and it does
not prove that the sparse representation or shifted reads are free.

## 4. Evidence and limits

The proof above is the unbounded finite-dimensional claim. The accompanying
verifier independently realifies I-D_h P_tau over Q and computes its rank,
constructs the cycle basis, and compares literal Fourier products with
direct convolution over Gaussian integers. Its Fourier transforms are
unnormalized, so it checks F_raw^+(F_raw^-u . F_raw^-v)=N(u*v).
Its finite domains and rejection controls are specified in README.md.

No selected framework assumption is discharged. Arbitrary changes to the
final map, restrictions coupling the two operands, approximation, nonlinear
address maps on actual tapes, native realization, input preparation,
ownership/restoration, physical movement, precision, stock, complete cost,
supplier admission and the multiplication theorem are outside this proof.
Independent human and formal proof-kernel review are unclaimed.
