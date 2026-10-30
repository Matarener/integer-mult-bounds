# Exact direct selection for the production low-code compiler

## Claim and source boundary

For every admitted odd prime q, 1≤d≤64 and positive integer R, the new
`LowCodes` returns exactly the same radices, size, code width, GL_d(F_q)
lexicographic ranks, inverse ranks and `(request, common, matrix)` codes as
the retained source, on its well-typed valid domain. The public `rank`,
`unrank`, `encode` and `decode` methods and the `Constraints` class execute
unchanged source bytes; only constructor admission and the two row methods
are replaced. The proof below applies to every prime, although the executable
constructor accepts only primes≤257 or a verified power-of-two certificate.
The actual selected q*=213·2^80+1 is admitted without trial division.

This is an **offline finite compilation** result. Python integer arithmetic,
source extraction and array access are charged in the compilation model below;
they are not free operations on runtime tapes. No recursive call, rank,
label, payload operation, paid histogram, source count or selected frontier
changes. No new κ follows, and no signed-invoice edit is proposed.

The exact live consumer ancestry is `production_native.build_native` →
`Catalogue(q)` → `LowCodes(q,64,len(requests))`. The physical controller's
cohort loads the Gaussian leaf's PR3087 archive; its nested PR3055, PR2899 and
PR2809 archives contain the low-code module and actual catalogue/route
consumers. `source_binding.py` authenticates the declared inputs, opens only
regular uniquely named archive members, and compares the low-code,
catalogue, route and oracle bytes against separately declared live pins.
It compiles authenticated source bytes, so a stale `.pyc` is not evidence.

The `Catalogue.low_classes` and `compile_route` definitions used by the
verifier are AST-extracted **unchanged complete definitions** from those
source bytes. The route uses the original oracle arithmetic; no payload
engine is replaced by a mock. The fixture instantiates a legitimate fixed
integral shear, not the entire selected chart catalogue. This demonstrates
real consumer compatibility at the exact q* and d=64, but does not execute
`build_native`, compile its complete macro tuple, or run a physical payload.
The historical R480/T16 controller is not the newer selected PR5413 supplier.

## Retained counting invariant

This paragraph recalls Jose Manuel's `selected-source-packets/PROOF.md`,
“Finite low codes without a GL64 lookup table”, rather than claiming a new
GL ranking construction. Suppose r<d independent rows have been chosen.
They span q^r vectors. For a coordinate prefix, the source `Constraints`
row-reduces equations on the r span coefficients. If consistent with b pivots,
exactly q^(r-b) coefficient vectors match the prefix. Otherwise none do.
Independent rows make the coefficient-to-vector map injective.

At column j (zero based), let T=q^(d-j-1) be the total completions for one
fixed next symbol. `next(j)` returns a reduced coefficient row, rhs h, and
possibly a new pivot. Since all row entries and elimination are modulo q,
0≤h<q. Write E=r-b.

* If the prefix is already inconsistent, the excluded count e(v)=0.
* If there is a new pivot, e(v)=q^(E-1) for every v∈[0,q).
* If there is no new pivot, e(v)=q^E for v=h and 0 otherwise.

These are exactly the unchanged `Constraints.excluded` cases. Each
admissible next-symbol interval has length c(v)=T-e(v). They are nonnegative
for independent preceding rows. In the new-pivot case a reachable prefix with
positive admissible completions has c(v)>0; a zero c cannot contain the
supplied admissible rank. In the no-pivot case q^E≤T: the remaining d-j-1
coordinates must distinguish the q^E coefficient solutions. These facts
justify every division in `select_symbol` on valid inputs.

## Closed prefix counts and direct inverse

Let P(v)=Σ_{u<v}c(u), for 0≤v≤q. The replacement computes exactly:

1. Inconsistent prefix: P(v)=vT.
2. New pivot: P(v)=v(T-q^(E-1)).
3. No pivot: P(v)=vT-q^E·1[v>h].

Thus `vector_rank` adds exactly the same source summand that its old
`for smaller in range(value)` loop accumulated, before calling the unchanged
`choose`. Induction over columns gives identical state and row rank.

To select the unique nonempty interval containing a residual rank k, the
first two cases use `divmod(k,T)` and `divmod(k,T-q^(E-1))`. The quotient is
the symbol and the remainder is its interval offset.

For the third case put e=q^E. The exceptional interval is
[hT,(h+1)T-e), possibly empty. For k<(h+1)T-e, ordinary `divmod(k,T)` selects
the correct symbol: this includes all intervals before h and the retained
part of h. For k≥(h+1)T-e, add e before `divmod`; this restores the deleted
e positions and selects exactly one of the symbols h+1,…,q-1. This also
works when T=e, when the h interval is empty and must be skipped. The
result always satisfies P(v)≤k<P(v+1) and returns k-P(v).

Starting with 0≤k<q^d-q^r, induction over columns therefore follows the
identical source symbol and `choose` state. At the end the residual rank is
zero and the prefix is outside the preceding span, just as the source
requires. No q-sized symbol loop is used in either replacement.

For row r there are q^d-q^r choices. The unchanged mixed-radix methods rank
these choices in row order, so the entire GL bijection and its order are
preserved. Finally the unchanged encoding is
`(2*request+int(common))*size+rank(matrix)`; size, tag, width and inverse
decoding are therefore identical. This is an all-size argument; the complete
finite differential tests are corroboration, not its premise.

## Certified prime admission

The selected witness 7 is already in PR2234 and the controller's
`check_prime.py` Proth certificate. We reuse it. The new general certificate
checks q=h·2^k+1, h odd, F=2^k with F²>q, 1<a<q,
a^(q-1)=1 mod q, and gcd(a^((q-1)/2)-1,q)=1.

For every prime divisor ℓ of q the multiplicative order of a mod ℓ divides
q-1=h2^k, but does not divide h2^(k-1). Its 2-adic valuation is therefore k.
Consequently F divides ℓ-1, so ℓ≥F+1>√q. A composite positive q has a prime
divisor≤√q, a contradiction. Hence the checks prove q prime. For the selected
q, the retained congruence 7^((q-1)/2)=-1 mod q implies both witness checks;
213<2^80 gives F²>q. The verifier evaluates the integer equalities directly.
No probable-prime assumption, floating-point computation or trial scan up
to q is used for this case. Small-field admission trial-divides only to
floor(√q), under the explicit q≤257 bound. The certificate object type and
its requested-q binding are checked; a caller-supplied object returning q
cannot substitute for a certificate.

## Compilation work and storage

Use a classical arbitrary-precision bit model. Set L=ceil(log2(q+1)) and
B=d²L+ceil(log2(2R+1))+2, which bounds the whole code and mixed-radix
intermediates. This is a model upper bound, not a measured CPython CPU bill.
With schoolbook multiplication/division of b-bit integers costing O(b²),
modular inverse by Euclid may conservatively be bounded by O(L³).

There are exactly d² next-symbol positions per full rank or unrank. At a
position with r preceding rows, `Constraints.next` scans at most r basis
rows, each of length r, costing O(r²) field operations. `choose` normalizes
one r-entry row using a modular inverse and sorts at most r pivots. Summed
over positions this is O(d^4 L³) bit work. Powers q^e with e≤d at O(d²)
positions can be recomputed by repeated squaring in
O(d^4 L² log(d+1)) bit work. The unchanged mixed-radix loop performs O(d)
multiplications/divisions on at most B-bit integers, costing O(dB²).
Constructor radices/product fit within these bounds. Thus the deliberately
conservative total is

    O(d^4 L³ log(d+1) + d B²)

per constructor/rank/unrank/encode/decode operation, with the certificate
adding O(L³) bit work. The return code itself can require Θ(d²L+log R) bits;
we do not charge it as one fixed-size machine word. The inequality covers
the original d≤64 domain and also states the natural dimension dependence.

The retained rows, constraint basis, radices and temporary coefficient
vectors occupy O(d²L) bits; the full code/product occupies O(B). Schoolbook
arithmetic can use O(B) temporary bits, giving O(d²L+B) peak mathematical
working storage, including input/output matrices. No cache grows with the
number of calls. This is not Python allocator/RSS reclamation or a literal
fixed-tape space bound.

In contrast the source constructor tests q-2 trial divisors for a prime.
Its old vector rank loops Σ_{ij}m_ij times and unrank inspects
Σ_{ij}(m_ij+1) symbols for a returned matrix m. These are source-loop
counts, not timings or field-operation counts. Dense selected-field codes
make them field-sized; the new exact interval formulas still visit only
d² positions. The verifier reports both old counts and instrumented new
position counts for actual q*GL64 examples. Source interval counting,
Gaussian elimination and big-integer costs are all still paid above.

## Remaining obligations

The compiler does not enumerate or store all GL64 classes, remove
`compile_node`'s eager outer macro tuple, prove a regional instruction
emitter, discharge every selected denominator/chart condition, change the
finite-control runtime into a uniform RAM, or prove its tape-cost refinement.
The full `Catalogue` request preparation, complete factory, runtime directory
producer, recursive parking, error/precision and outer multiplication
contracts remain separate. Finite source equivalence does not by itself
make the complete source factory practical. No independent human or
formal-kernel review is claimed.
