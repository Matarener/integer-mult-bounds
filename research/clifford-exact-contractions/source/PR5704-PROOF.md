# Exact phase replay with polynomial state storage

## Statement and input contract

For each nonnegative integer n, the engine accepts a computational basis input
and a finite valid circuit in the retained gate grammar:

- `P(G)` maps x to Gx for an invertible binary matrix G.
- `X(b)` maps x to x xor b.
- `D(Q,alpha)` multiplies x by i^q(x), where Q is symmetric,
  alpha_i mod2=Q_ii, and q(x)=sum alpha_i x_i+2 sum_(i<j)Q_ij x_i x_j mod4.
- `phase(a)` multiplies the whole state by i^a.
- `C(v,s)`, for s=+1 or -1, is `((1+s*i)I+(1-s*i)X(v))/2`.

The result is a canonical exact description of **every** output amplitude,
including absolute global phase and zero amplitudes. No floating-point value,
random choice, vector expansion or acceptance-result cache is used in the
engine. The finite tests and benchmark are separate from this all-width proof.

For two valid retained Clifford objects, equal full Pauli tableaus and equal
canonical zero-input states decide equality of the complete operators. The
objects must have tableaus derived from their circuits by the retained exact
constructors. An arbitrary user-supplied tableau is outside that contract. The
engine validates the state circuit grammar itself; it does not accept a phase
claim based only on a reported rank or a zero-input column.

This is an implementation of classical stabilizer and quadratic-form methods.
Dehaene and De Moor describe their binary linear and quadratic foundations in
[Physical Review A 68, 042318 (2003)](https://doi.org/10.1103/PhysRevA.68.042318).
Phase-sensitive stabilizer representations also appear in
[Bravyi et al., arXiv:1808.00128](https://arxiv.org/abs/1808.00128).
No new general simulation theorem or optimal complexity is claimed here.

## 1. State invariant

Keep independent binary columns A_1,...,A_r in F2^n, an offset b, and a phase
polynomial

`q(z)=q_0+sum a_j z_j+2 sum_(j<k)b_jk z_j z_k mod4`.

Keep a nonzero exact Gaussian-dyadic scalar `s=(u+i*v)/2^d`. The state is

`sum_(z in F2^r) s*i^q(z) |b+A*z>`.

Since the columns are independent, every support point has exactly one
parameter z. The representation therefore has no unresolved sum of amplitudes
at one output. Every support amplitude is nonzero. Start with r=0, b equal to
the supplied basis input, q=0 and s=1.

A polynomial is stored by its constant, linear and even quadratic coefficients.
A Boolean XOR has the exact lift

`x_1 xor ... xor x_k = sum x_i -2 sum_(i<j)x_i*x_j mod4`.

An affine constant one replaces that expression by one minus it. Twice a
product of affine forms needs only their product over F2. These formulas prove
`affine`, `product` and `substitute` in quadratic.py. The result remains a
polynomial of degree at most two with even quadratic coefficients. Repeated
variables use x_i^2=x_i; no term of degree three survives modulo four.

## 2. Ordinary gates

For P(G), replace each column A_j by G A_j and b by G b. Invertibility preserves
independence. For X(v), replace b by b+v. For a global phase, add its exponent to
q_0. For D(Q,alpha), substitute the affine output coordinates b+A z into its
phase and add the result to q. The formulas in section 1 give every new
coefficient. These updates preserve the full state invariant exactly.

The implementation checks matrix sizes, binary ranges, permutation rank,
diagonal symmetry, parity lifts and gate arities. Global phase exponents are
integers reduced modulo four. Invalid translation-root signs are rejected.

## 3. Translation-root update and exact elimination

Let C(v,sigma) be the next gate. Introduce one Boolean variable t and use

`C(v,sigma)|x> = ((1+sigma*i)/2) sum_(t=0,1) i^(-sigma*t)|x+t*v>`.

Multiply the scalar by `(1+sigma*i)/2`, append v to A, and add `-sigma*t` to q.
If v is outside the old column span, these columns are independent and the
update is complete. In particular, this case cannot occur when r=n.

Otherwise find the unique c with A c=v. Set the old parameter to `u+c*t`.
The output becomes b+A u and no longer depends on t. Affine substitution gives

`q'(u,t)=q_*(u)+a*t+2*t*L(u)`,

where L is a binary linear form. The remaining sum over t is exact.

If a is odd, then

`1+i^(a+2L)=(1+i^a)*i^(-a*L)`.

Multiply the scalar by 1+i^a, add the lifted phase -a L, and remove t. There is
no support restriction. Both a=1 and a=3 are included; their Gaussian factors
are conjugates. This is where discarding a scalar phase would give a wrong
operator even when the Pauli tableau is unchanged.

If a is even, then

`1+i^(a+2L) = 2 if L=a/2, and 0 otherwise`.

Multiply the scalar by two and restrict u to that affine equation. When L is
nonzero, choose one of its coordinates as pivot, express it through the other
coordinates and its constant, substitute in q_*, and update the output columns
and offset by the same substitution. The remaining columns are independent:
an injective map A stays injective on an affine hyperplane. The support rank
decreases by one. The generic constant-equation branch either has no
restriction or is inconsistent. An inconsistent state is rejected; it cannot
arise from a valid unitary circuit and a nonzero input.

Thus every completed update has at most n support variables. The temporary
expression has at most n+1. The program divides a common power of two from u
and v whenever d permits. This changes no amplitude and keeps the exact
scalar in a unique reduced dyadic form.

Each allowed gate is unitary. For C, the involution X(v) has eigenvalues +1
and -1, on which C has eigenvalues 1 and sigma*i. Hence the invariant state
never vanishes and `2^r*|s|^2=1`. Scalar numerator and denominator bit lengths
remain polynomial in n; they do not grow with the number of processed gates.

## 4. Canonical certificate and operator equality

Compute the unique reduced binary basis of the support space in the specified
pivot order. During elimination, retain each basis vector's coordinates in the
old parameter space. Reduce b so that all pivot coordinates are zero. This
chooses the unique offset representative of the affine support. The retained
coordinates give an invertible affine change of parameters; substitute it into
q. Absorb its constant phase into the Gaussian scalar, then reduce the dyadic
scalar again.

The resulting tuple gives width, reduced offset, ordered support basis, all
nonconstant phase coefficients, the Gaussian numerator and denominator. It is
canonical. Indeed, the support fixes its basis and offset; the amplitude at
parameter zero fixes the scalar. The remaining phase values fix every linear
coefficient by evaluation on a unit vector and every quadratic coefficient by
evaluation on a pair. Conversely, equal tuples give equal amplitudes at every
point, including all points outside the support. The `amplitude` function
solves for a support coordinate and returns the exact amplitude or zero.

The complete operator comparison also retains the full signed Pauli tableau.
If U and V have the same tableau, V^-1 U commutes with every Pauli X_j and Z_j.
Commutation with all Z_j makes it diagonal in the computational basis;
commutation with all X_j makes all its diagonal values equal. Thus it is a
scalar multiple of identity. Equality of the nonzero zero-input states makes
that scalar one. Both tests are necessary. An input Z gate leaves the zero
column unchanged but changes the tableau. A global i phase leaves the tableau
unchanged but changes the state. The verifier includes both controls.

## 5. Polynomial resource bound

At most n support columns and O(n^2) phase coefficients are live. The dictionary
encoding uses n-bit masks for those coefficients, so O(n^3) bits is a conservative
storage bound for the state, apart from the read-only circuit and Python object
overhead. Each affine phase substitution uses at most O(n^4) elementary integer
and bit operations. Matrix work and canonical reduction fit that bound. Charging
linear cost for an n-bit operation gives the conservative bound O(m*n^5) bit
work for m gates, plus canonicalization. This is not an optimized stabilizer
simulation bound. It is a polynomial bound, unlike an explicit 2^n-entry state.

The executable checks full-support examples at widths 16,32,64. The largest has
2^64 nonzero amplitudes, represented by 64 support columns and 2048 phase terms.
Exact inverse insertion, complete circuit inversion and absolute-phase controls
pass. This is finite corroboration of the representation; the induction above
provides the all-width statement. No exponential vector is built in these
large checks.

## 6. Explicit integration and retained obligations

The consumer is the complete actual restricted-C construction of PR5698,
head 024e43cdd1b942059c87446a76235c3f0b681c34. Its32 files are frozen under source/.
The prior table evaluator and its notices from Charles Bethin PR662 are frozen
under tables/. All35 retained files are authenticated before source import.

`replay.py` derives from PR5698 physical.py. It changes only the source root and
passes an explicit equality function at the three state-comparison sites.
`verify_source.py` derives from its full verifier. It forwards that function and
uses the retained source artifacts. The new public runner compares the complete
returned dictionary to the byte-exact source RESULT.json. There is no monkey
patch, modified class, hidden acceptance cache or change to a source file.

`binding.py` derives the permitted syntax trees from the frozen text and checks
the entire two integration modules. All chronology, helper debit, query-cap,
paid-profile, cut/flow, real-power, tail, native-normalizer and rejection checks
remain. Docstrings and comments are not executable proof obligations. The
standalone source CLI is replaced by a wrapper that checks the same complete
result and rejects unknown arguments. Registered replay checks the integration
binding; an omission of a source check is a rejecting control.

The ordinary engine tests use the retained literal-vector evaluator and the
credited table evaluator as separate representations. They compare every
amplitude at every tested basis input and circuit prefix, including zeros and
denominators. `cross.py` additionally compares every actual native state used by
the complete source replay against the literal vector. It then requires the
same complete source result, including all old failure controls. The source
positive result and mathematical construction keep their original credit.

The benchmark runs the original source verifier for its literal baseline. The
table and quadratic engines run the same explicitly derived proof with different
equality functions. Every process authenticates the same sources and returns
the same complete scientific result. The alternating runs start fresh Python
processes; operating-system caches are not flushed. The benchmark is a local
verification-time result, not a measured speedup of integer multiplication.

## 7. Scope and attribution

The new contribution is an exact implementation, complete source integration,
coverage binding, adversarial checks and same-fixture measurement. The state
representation and elimination methods are classical. Charles Bethin PR662
retains its gate-table optimization credit. BigCactusLabs PR702 and Joshua
Snider's cold-wrapper quadratic certificate retain their distinct finite
amplitude/phase audit credit. The current coframe construction is Ali Romman
PR5698, built on Dugongue PR5687, Cao Yifan, Cinna Davis and the retained native,
phase, source, helper, ROW, controller and compiler lineage. All frozen notices
remain unchanged. New code and proof: Ali Romman with substantial OpenAI Codex
assistance; no subagents. Apache-2.0.

No native construction, recursive query, productive target, field route,
precision bound, physical tape/stock invoice or compiler threshold changes.
The source's local rank deficit remains1680. Its missing funded complete
Gaussian caller and inherited uniform/native assumptions remain open. No new
ordinary saving, whole kappa, selected-frontier change, independent human
review or proof-kernel acceptance follows from faster exact verification.
