# Uniform R437/OQ4 owner transport and packet separation

The source is the unpooled current R437/OQ4 catalogue at PR3647 commit
`a24f9ff95c12fd0b6792e3f710569237efd72db2`, through the PR3967 adapter.
Its ordered request digest is
`cbfea55f5cd0b74a2a0d4292ad0139d2b5bb73127951127698030bc90c73c532`.
This proves the **owner transport interface**, not the complete source supplier.
The local residual's functional contract remains an explicit premise.

Nick Petalas/PR2989 already gives the general separation and conditional ordering
arguments for the old selected source, with chart invertibility retained. The
new exact coverage here is the current R437 chart determinant certificate and
its changed owner inventory. The following interface arguments apply those
principles to these certified matrices; they are not claimed as new general
routing theorems.

The mathematical pairing is the right action of a matrix group on its low/high
fibres, with disjoint writable subobjects in a typed packet interface. It yields
an actual source condition needed by the complete emitter: the original Driver
checks owner-packet uniqueness, while `compile_node` does not repeat that guard.
The source-specific theorem below discharges that condition uniformly.

## 1. Source certificate over the dyadic rationals

Let D=Z[1/2], d=64. The actual current source has 1,235 distinct chart labels.
The verifier reconstructs each chart from its source geometry and support label,
compares it to the reused catalogue matrix, and computes its determinant by an
independent exact elimination. Every entry belongs to D. Every determinant is
+1 or -1 (236 and 999 labels respectively). Hence each chart sigma belongs to
GL_d(D), with inverse in D by the adjugate identity. This is a certificate over
D; it is not an inference from tests at q=3.

For every pair of distinct roles sharing one family in a canonical call, the
verifier exhibits an entry of sigma_a-sigma_b equal to +1/2, -1/2 or -1.
There are 5,619 such pairs over the nine calls. The explicit 32-fold owner
replication is checked at every role, giving 179,808 pair instances over all
288 calls. These differences are units in D and remain nonzero modulo every
odd prime. `RESULT.json` records the inventory and canonical witness digest;
the verifier regenerates every witness rather than trusting that digest.

Consequently all charts are invertible over R=Z/q^w Z for **every odd prime q
and w>=1**, and same-family charts are distinct over F_q. This includes the
five changed stage-six owner routes; old source ordinals are not substituted.
This removes the chart-invertibility premise only; any separate source-prime
assumptions of projectors, split bases or numerical normal forms remain.
The theorem is restricted to the authenticated unpooled source. A cross-replica
owner construction must supply its own inventory and separation witnesses.

## 2. Typed low/high chart action

Let L=GL_d(F_q), N=|L|, H=q^(d^2(w-1)). For ell in L, let
F_ell be the set of raw matrices g in GL_d(R) reducing to ell. Each fibre has
H elements and has the canonical enumeration g=ell+q X, with each entry of X
in {0,...,q^(w-1)-1}; ell denotes its entrywise canonical representative.
Invertibility holds because a matrix over this local ring is invertible exactly
when its reduction is invertible.

For an actual chart sigma, right multiplication is the bijection

    rho_sigma : F_ell -> F_(ell sigma mod q),   g -> g sigma mod q^w.

Its inverse is rho_(sigma^-1), so no invertibility of the high-digit matrix X
is required (the complete raw header g is invertible). If d0 is a chosen common low, the owner's native low is
ell=d0 sigma^-1 mod q. Thus every matching native high fibre is transported
bijectively to the common fibre. As d0 ranges over all L, the native low also
ranges over L exactly once. Neither low-class cardinality nor a uniform bad-low
fraction changes under this right translation.

This is precisely the `compile_owner` direction: it returns native ell,
forward `(ell,sigma,d0)`, and backward `(d0,sigma^-1,ell)`. Supplying the common
low as the native low, or applying sigma twice, changes the map.

The high key must include the carry:

    Y=(canonical(g sigma mod q^w)-canonical(d0))/q.

The numerator is entrywise nonnegative and divisible by q, and 0<=Y_ij<q^(w-1).
A linear map on high digits alone generally omits the constant low-to-high
carry. `routes.high_key` multiplies the complete raw header first and performs
this exact quotient. This is needed even when every input high digit is zero.

## 3. Owner-key separation for every common low

Fix a call and d0 in L. Its writable owner key is

    K(role)=(owner.family, d0 sigma_role^-1 mod q).

Different families give different keys. If roles a,b have the same family and
equal native lows, cancellation by the invertible d0 gives sigma_a^-1=
sigma_b^-1, hence sigma_a=sigma_b modulo q. Section 1 supplies a nonzero unit
entry in their difference, a contradiction. Therefore K is injective for every
common low, every admitted q and every replica. This proves the exact predicate
`Driver.local` calls `disjoint complete owned low packets` for the current
source, even though the complete emitter omits that dynamic assertion.

This conclusion requires invertible common low. A singular low may annihilate
a chart difference. It also requires the source chart witnesses; distinct role
numbers or distinct rational chart labels alone are insufficient.

## 4. Complete fibre route, arbitrary dirty payload and residual equivariance

A packet is an ordered sequence indexed by (old-prefix occurrence, high lift,
payload-bit position). Old-prefix occurrences retain multiplicity even when
their serialized values agree. Let C>=1 be their number and b>=1 the fibre
length. A route permutes only the high-lift index, separately in each occurrence;
it neither coalesces prefixes nor changes any payload bits.

The functional refinement of `route_cube` follows these loop invariants:

1. Odometer enumeration decorates each of the H source rows with the exact
   target high key Y and copies all b payload bits. Section 2 gives one copy of
   every target key.
2. Each `partition` is a stable binary partition of all H complete decorated
   rows. It copies every key and every payload bit once into one bucket and
   concatenates buckets 0 then 1. It preserves equal-key internal order.
3. The cursor scans the fixed-width binary key from least to most significant
   bit. Coordinates are visited in reverse lexicographic order. Stable radix
   sorting therefore leaves keys in the Odometer's lexicographic order.
4. The final pass checks every expected key and removes only decoration. Its
   H rows are exactly the pushforward by rho_sigma. At w=1, H=1 and the sorting
   loop is skipped; the same conclusion holds.

`route_packet` repeats this operation for each of the C physical prefix
occurrences. Its source is rewound; completed temporaries are cleared. These
are invariants of the cited source loops under the existing binary word,
Counter, Matrices, tape and allocation contracts. This note does not separately
reprove those primitive contracts or their machine tariff.

Now let P be the actual local residual's base projector. In a routed row d=g
sigma, the common residual acts with d P d^-1. The native action is

    g (sigma P sigma^-1) g^-1 = (g sigma) P (g sigma)^-1.

Thus forward route, completed common residual and inverse route commute with
the native conjugated residual. This equality is valid over R and for each row;
equality of the address permutations gives equal pullbacks on **every Boolean
payload function**, including nonlinear or correlated dirty helpers. It does not assume that a source contains only a named clean
summand. For COPY the runtime uses the actual permitted common source code;
this equality does not introduce a forbidden native COPY code.

An IDLE source is already native and retains its family chart in its preparation.
The actual rank26 and rank42 sources consequently remain native sources; they
are not converted by relabeling the rank7 common COPY code. Conjugation preserves
rank after reduction, so the old rank34 IDLE code cannot be transported into
the current rank26 or rank42 source by any invertible change of chart. Equal
numeric code widths or stable source ordinals supply no version-portability law.

## 5. Gather, local call and chronological scatter

For fixed d0, Section 3 gives disjoint writable packets inside the family array.
Gathering all roles from that array and routing each yields the staged local
state. Let F be **any completed local map** on those staged packets, satisfying
its declared source, target, private-buffer and restoration contract. Inverse
routing and scattering each result into the **latest** family state implements
exactly the simultaneous replacement of those disjoint packets by F's outputs.
Proof: after k scatters, precisely the first k selected packets have changed;
all others retain their previous contents. Disjointness makes the next step
preserve this invariant. It is independent of values or correlations of bits.

This supplies a commuting square between native family state and staged state,
conditional on F. It does not prove F or execute all GL64 classes. Subsequent
common-low invocations remain chronological; this lemma does not authorize
reordering different invocations, whose selected packets may overlap.

A counterexample is retained in the verifier: scattering two disjoint returned
packets into their original stale snapshots loses the first change. Thus
`Machine.commit`/`Driver.commit` reading the latest family is a substantive
premise, not merely an implementation convenience.

## 6. Complete transport invoice and retained obligations

Let G,S,R be **completed** gather, scatter and route tariffs at this node,
including their setup, temporary output, ownership transfers and disposal of
replaced/temporary streams. They may be nonuniform; the following expression
uses the maximum over the actual charts and source roles. Write N=|GL64(F_q)|.
The current complete compiler has

- 189,792 N local gathers and the same number of local scatters;
- 379,584 N routes, counting both directions;
- 63,936 N native-IDLE gathers and the same number of native-IDLE scatters.

Hence its complete owner/IDLE transport charge is bounded by

    C_transport <= 253728 N (G+S) + 379584 N R.

Equivalently there are 507,456 N whole-family scans. The verifier derives these
numbers from all 659 owners in 288 calls and all 1,998 canonical IDLE requests,
not from the 903,456 paid residual count. A paid child count alone is not a
transport count. Under a primitive convention excluding commit/disposal, add
those charges explicitly to G,S,R before using this expression.

For C old-prefix occurrences, H high lifts, fibre b and Vp=CHb, a full family
has N Vp bits. The inherited sequential implementation gives completed gather
and scatter O_q(N Vp+setup), and route
O_q(J Vp+CH(poly(w)+J^2)), J=O_q(w), when its binary arithmetic, allocation and
cleanup contracts hold. No H=1 or controlled-payload simplification is used in
the counts. Converting this into O_q(w V) additionally needs the actual node
volume, root/history/stock coupling and allocation/visited-cell reserve.
Those premises are not supplied here. In particular erased scratch is not a
bound on all backing cells visited across repeated calls.

The complete ordinary caller still pays residual children and their preparation,
clones, XORs, private-result consumers/disposal, global bridges and exchanges,
fresh-row routing, ordinary wrappers, normalization and numerical reserves.
This transport lemma sets none of them to zero. It supplies an independently
reviewable source/transport implication to their full invoice; it is not a
complete multiplication theorem or a frontier update.
