# Sharp native-only tariff for the omitted endpoint adapters

## Exact object

The two unchanged PR2586 inputs on canonical main define 5,398 events,
358 initial public banks and eight private lifetimes. PR3446 defines a
terminal-history projection and PR3462 supplies its normalized scalar endpoint
completion. This package reconstructs the projection from the original word.
It does not import either pending package or assume their executable results.

Let L consist of Y22 through Y32, Y63 through Y103, D27 through D31,
G27 through G31 and Q7. Observe each ADD through event 4516 with its source
in L and target outside L and outside the private C bank. Retain the complete
syntactic histories of those 675 events and of their targets and L at the final
cut. Whenever a retained history reads a public input, retain that input bank's
terminal history. Whenever it includes a private allocation, retain its erasure
history. Iterate to a fixed point. Histories retain old target values, signs,
transports and source reads even when coefficients cancel.

The replay obtains 4,027 events and 265 initial banks. The selected-event digest
is `66113bcd513a17eac24f43944a8759bdae1bb2a85e2b9900122f281c5c676dc8`,
as in PR3446/3462. None of the selected events targets any of the 93 omitted
public banks. Each omitted bank therefore stays in its initial physical frame.
All original transport occurrences, ADD frames, private lifetimes and final
frames are checked against the native archive before adapters are constructed.

There are 52 omitted X banks, each with a one-dimensional initial frame,
and 41 empty-frame banks, the 38 N banks and G2, G3, G9. Every one has the
same full nine-dimensional final frame. All bank names and the exact source
and target frames are in ADAPTERS.json. The 41 banks with zero normalized
scalar residual in PR3462 still require these chart changes.

Write J_f for the source's Delta chart. The adapter on bank b is exactly

    U_b = J_final(b) J_initial(b)^(-1).

It takes the physical payload J_initial(b) q to J_final(b) q for every
complex 512-vector q. No zero-payload or divisibility assumption is used.
This concerns exact complex arithmetic. Finite-precision execution and actual
recursive realization are separate obligations.

## Exact constructive certificate

The retained Gaussian Clifford compiler on main synthesizes each adapter as

    M_left C_r M_right,

where each M is an explicit affine binary permutation with a Gaussian-unit
quadratic phase, and C_r is the product of the r standard binary C factors.
All monomial coefficients, offsets and phases are included in ADAPTERS.json.
There are 53 distinct recipes: one shared rank-nine empty-to-full recipe and
52 rank-eight singleton-to-full recipes. They occur on 93 distinct banks.
The profile is exactly `{8: 52, 9: 41}` and the total rank is 785.

The separate unchanged PR3416 checker constructs Delta charts by enumerating
all 512 addresses and a completed binary basis, rather than using the compiler's
matrix inversion and Clifford synthesis. It derives each wrapper's Pauli
conjugation and checks its address and phase identity on every computational
column. It compares the recipe and requested chart map on all 18 signed Pauli
generators and on the complete 512-entry image of the zero computational vector.
Both the tableau and this exact dyadic Gaussian anchor are hashed in the
receipt. A separate bounded binary elimination routine in verify.py computes
the rank used below from the requested map, not from the compiler's declared
rank. All 53 exact comparisons and ranks pass.

These checks imply equality on every vector. The ratio of two invertible maps
with identical signed Pauli action commutes with every binary X and Z. The Z
operators first force it to be diagonal and the X operators force all its
diagonal entries to agree. Thus the ratio is scalar. The nonzero exact anchor
fixes that scalar to one. Equality of unsigned tableaus alone would not fix
either Pauli signs or global phase.

The checker is a separate implementation from the compiler. It is reused
source evidence, not independent human acceptance or formal kernel review.
Its original bytes, source head and hash are retained in inputs/ORIGINS.json.
No pending Git object is needed at runtime or during a source-only replay.

## Tariff model and lower bound

The following optimality statement is scoped to bank-local Clifford words.
Each of the 93 banks is adapted separately on its nine binary axes. Allow any
finite sequence of affine quadratic-phase monomial Cliffords and paid native
calls of positive ranks t between one and nine, with arbitrary intermediate
frames. A paid call has the form M_left C_t M_right. Monomial operations have
zero cost in this native-only tariff. No operation couples different banks or
uses an extra bank. This is the literal adapter alphabet being priced, not a
lower bound for all physical completion programs.

For a signed binary Pauli tableau, write its linear symplectic part in blocks

    (x', z') = (A x + B z, C x + D z),

and set rho(U) = rank_F2(B). A monomial Clifford has B = 0, since it takes
every diagonal Z operator to a diagonal Pauli. The standard C_t has a rank-t
B block. Multiplication by an invertible monomial on either side preserves
the B rank, since the relevant A and D blocks are invertible. Consequently
every paid rank-t call has rho exactly t.

For any two Cliffords U,V, block multiplication gives

    B_(UV) = A_U B_V + B_U D_V,
    rho(UV) <= rho(U) + rho(V).

The rank computation in the certificate gives rho(U_b) = 8 on every omitted
X bank and 9 on every other omitted bank. Hence any admitted word for bank b
has sum of its paid ranks at least rho(U_b). The direct recipes attain these
values, proving the sharp total rank mass 52*8 + 41*9 = 785.

More strongly, fix any real s with 0 < s <= 1 and charge a rank-t call t^s.
Subadditivity of x^s on nonnegative reals gives

    sum_j t_j^s >= (sum_j t_j)^s >= rho(U_b)^s.

The direct recipe attains equality for every bank simultaneously. Thus the
sharp total tariff, for every such s, is

    T(s) = 52*8^s + 41*9^s.

At s = 0 every positive-rank call costs one. Each requested map has nonzero
B rank and so cannot be monomial alone. At least one call per bank is necessary,
and the same recipes attain the sharp total 93. Thus the formula also holds
at s = 0. Under rank normalization by nine, the corresponding native-only
bill is 52*(8/9)^s + 41. Any supplier role-count normalization and every other
charge must still be applied by its actual caller.

This lower bound prices only the adapter segment after a bank's required
normalized endpoint value has been produced in its initial chart. A scalar
completion that instead changes charts while computing, cross-bank coupled
Cliffords, broader operations or a different consumer is outside its hypotheses.
The result must not be charged again if an actual completion already performs
these same maps.

## Cost ledger and stop decision

The original omitted program has 473 transport events, interleaved with scalar
operations and signs. Its transport histogram is recorded as context only.
It is not an adapter implementation to which 93 standalone calls can be
substituted without separately proving the scalar endpoint completion.
No runtime speedup or full-word cost reduction follows from the count.

The previously unknown endpoint-native entry is now constructively priced
and optimal within the stated bank-local alphabet. This is one paid component.
The normalized rank-eight correction in PR3462 is a separate proposed module,
including its one restored dirty helper and weighted scalar updates. Its actual
common-frame readouts, scalar expansion, source restoration, adapters between
those reads, routing/ownership, numerical precision, idle and cleanup charges,
consumer and complete supplier moment are unknown here. Monomial wrappers also
have real implementation costs outside this tariff.

Stop after this local result. The unchanged-profile supplier stop is retained.
A further construction needs one actual paid caller and a complete obligation
ledger, with unknowns explicitly marked, before another family expansion.
No new supplier, multiplication exponent or selected-frontier change is claimed.

## Open next questions

Can one actual caller realize the normalized scalar completion and its
common-frame readouts while paying this adapter profile? Begin with the actual
dimension-eight retained Y endpoints and the listed omitted-bank endpoints.
State every conversion, dirty restoration and consumer action, and price all
of them together. Missing ownership, numerical execution or a favorable complete
invoice blocks supplier admission. The current result supplies no reason to
launch another local matching or unpriced compiler search.
