# Exact extreme-rank header densities

This is a scoped counting proof. The finite replay corroborates it; the replay
is not a proof for every dimension or a complete multiplication theorem.

Let F be a finite field of order q, let m >= 2, and fix a split rank-r
projector P0. For a header g in GL_m(F), put P = g P0 g^-1. Call g good
when every leading k-by-k principal minor of P is nonzero, for 1 <= k <= r.
This is the criterion in section 3 of the retained recursive closure.

Write

    T = q^(m-1) (q^m - 1)/(q-1),
    A = q^(m-2) ((q-1) q^(m-1) + 1),
    B = (q^2-q+1)^(m-1).

There are T rank-one projectors and T corank-one projectors. Exactly A
rank-one projectors and B corank-one projectors are good. Therefore the
complete-header good fractions are A/T and B/T, respectively. In particular,
the exact rank-one bad fraction is

    (2q-1)(q^(m-1)-1) / (q(q^m-1)) < 2/q.

The theorem includes every finite field. The retained caller uses odd prime q.
The executable census uses prime fields only.

## 1. Why a projector count is a header count

Every rank-r projector is conjugate to diag(I_r,0), by choosing image and
kernel bases. The stabilizer consists exactly of block-diagonal matrices
with blocks in GL_r(F) and GL_(m-r)(F). Thus every projector has the same
number |GL_r(F)| |GL_(m-r)(F)| of header preimages. Multiplication of g on
the right by any fixed owner chart or image/kernel basis is a bijection.
The fractions do not depend on P0 or that fixed chart.

This argument uses a complete GL header domain, with equal multiplicity per
header. It is a deterministic count over that domain. A uniformly random
header has the same fraction as a probability. An arbitrary subset need not.

## 2. Rank one

A rank-one projector has the form P = u v with u a nonzero column, v a row,
and v u = 1. Exactly q-1 pairs represent the same P, through
(u,v) -> (lambda u, lambda^-1 v). For each of q^m-1 choices of u, the
nonzero linear functional v -> v u has q^(m-1) solutions with value 1.
This gives T.

The good condition is P[0,0] = u_0 v_0 != 0. Normalize u_0 = 1, which
chooses one representative for each good P. Put z = (u_1,...,u_(m-1)).
When z = 0, v_0 = 1 and the other v coordinates have q^(m-1) choices.
When z != 0, choose any nonzero v_0, and solve

    sum_(i=1)^(m-1) u_i v_i = 1-v_0.

There are q^(m-2) solutions for each of q-1 nonzero v_0 values and each
of q^(m-1)-1 nonzero z values. Consequently

    A = q^(m-1) + (q^(m-1)-1)(q-1)q^(m-2).

The displayed closed form and bad fraction follow by expansion. The strict
bound follows since (q^(m-1)-1)/(q^m-1) < 1/q and 2q-1 < 2q.

## 3. Corank one

Write P = I-u v with v u = 1. Complementation bijects rank-one and
corank-one projectors, so the total is again T. Put x_i = u_i v_i.
Multilinearity of the determinant gives

    det(I_k-u_[0:k] v_[0:k]) = 1-sum_(i<k) x_i.

Indeed, a term with two columns from u v has two proportional columns and
vanishes; the constant term is 1 and the single-column terms are -u_i v_i.
Because sum_i x_i = 1, all these determinants are nonzero exactly when
all proper suffix sums x_(m-1), x_(m-1)+x_(m-2), ... are nonzero.

For a fixed coordinate product x, the number of pairs (u_i,v_i) is 2q-1
when x = 0 and q-1 otherwise. Process coordinates in reverse order. After
the first step, each nonzero partial sum has weight q-1. On the q-1
nonzero states, a further step has diagonal weight 2q-1 and off-diagonal
weight q-1. Each column sum is

    (2q-1)+(q-2)(q-1) = q^2-q+1.

Thus after m steps every fixed nonzero endpoint, including the required
endpoint 1, has weight (q-1)(q^2-q+1)^(m-1). Divide by the q-1 free
rescalings of (u,v). This gives B. Zero coordinates are included throughout.

## 4. Complete local-ring packets

Let q be prime, w >= 1, and R = Z/q^w. Reduction GL_m(R) -> GL_m(F_q)
is onto, and every fiber has q^(m^2(w-1)) elements: lift each entry
arbitrarily, and the determinant remains a unit exactly when its residue
is nonzero. A pivot or minor is a unit in R exactly when its reduction
is nonzero. Therefore every full high-header packet inherits its low
header's good/bad status, and the complete GL_m(R) fractions are unchanged.

For a fixed split projector over R, the same image/kernel-basis conjugation
argument gives a stabilizer GL_r(R) times GL_(m-r)(R). Combining the group
sizes shows that each residue projector has exactly
q^(2r(m-r)(w-1)) split-projector lifts. This also explains the local-ring
projector counts in the finite replay. No coefficient is truncated to its
low residue when executing the normalizer; only the admission test is low.

In the source, `prepare` forms P, reverses its columns to form P C, and
at stage k takes column m-1-k. These are the leading-principal pivots of P,
in the opposite column order. With earlier pivots units, the next pivot is
a signed ratio of consecutive leading minors, so the admission criteria
agree. The replay also compares the actual program's accept/reject result.

## 5. Exact boundary of the consequence

The retained complete packet model enumerates every low header with the
same number of high lifts for each request. Its per-request bad fraction
is a deterministic counting fraction, without a probabilistic assumption
about the payload or frozen ancestor values. Right-translated fixed charts
preserve that statement. It does not assert that one header works for every
request simultaneously, or that distinct requests have independent tests.

An adversarial low class can be entirely bad. For rank one, choose P0 with
image coordinate 0 and a header swapping coordinates 0 and m-1. Then P has
P[0,0] = 0. Every high lift of that header is bad. By contrast the identity
header is good. Hence no nontrivial density bound transfers to an arbitrary
header restriction merely because a complete-domain bound holds.

The selected profile has rank-one requests, so the exact rank-one fraction
can replace a worst-case generic bound in that part of a future audited bill.
Its intermediate ranks and the complete physical recurrence remain separate
obligations. Corank one is a general calibration family, not a claimed
selected request. This package changes no production invoice or frontier.
