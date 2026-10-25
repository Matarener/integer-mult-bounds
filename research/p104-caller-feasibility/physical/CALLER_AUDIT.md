# Physical-caller decision for the PR3609 entrance

The new result closes a finite format obligation: the standalone entrance
accepts arbitrary original-grid physical fields with six added fractional
bits; the combined program needs seven internally and six at its required
outputs. Sufficient magnitude and native scratch capacities are proved in
`FORMAT_PROOF.md`. It does **not** identify an existing paid producer of the
required fields. Within the already failing PR3609 five-forward/four-dual
consumer model, adding preparation or routing costs cannot make the moment
feasible. The useful next step is a different complete consumer or cost law,
followed by one explicit producer-to-module boundary under its allowance.

## Exact interface now available for a caller

The standalone program uses 197 distinct physical banks, each containing 512
Gaussian coordinates: the 52 omitted X inputs at their actual singleton
frames; 38 omitted N and G2/G3/G9 at the empty frame; and all 104 Y inputs at
the empty frame. The Y banks are temporarily writable and restored before
the next source column is used. The 93 dirty output banks finish in F; Y
returns to its original values and empty frames. No additional Gaussian query
bank is allocated by this entrance. Arithmetic scratch, guards, native
workspace, and an address/controller implementation are still required.

For the full caller, retain the actual 4,027-event projection, the other 161
public fields, and all eight existing private-C zero/erase lifetimes. All 358
required endpoint frames are part of the contract. In particular, final Y
frames have dimension eight; their normalized restoration does not make them
empty-frame physical sources. Additional return adapters may be required by
a different upstream owner, and their bill is not supplied here.

The six-bit standalone format is a weaker sufficient arithmetic entrance than
the published 4B9 product condition. It is not a new source-module maximality
claim and does not require a free E9 encoder. A caller can supply arbitrary
mantissas in the explicitly refined representation, provided it pays for the
new bit positions, capacity, access and cleanup. That conditional possibility
is distinct from an actual owner/allocation construction.

## Finite conversion charges and their limits

Let an original signed mantissa use b magnitude bits and one sign bit. An
explicit scalar representation change stores `2^g*m` and changes the unit
from `2^-f` to `2^-(f+g)`. It preserves the represented number. A direct
arithmetic implementation performs g doublings per real component. The
following exact counts are additional conversion work, not part of PR3609's
887 entrance ADDs or its native tariff:

| Conversion | Real component words | Operations in this direct scalar implementation |
| --- | ---: | ---: |
| Standalone entry, guard 6 | 201,728 | 1,210,368 doublings |
| Optional standalone Y return to its original unit | 106,496 | 638,976 exact halves |
| Full-program entry, guard 7 | 366,592 | 2,566,144 doublings |
| Full outputs from guard 7 to guard 6 | 366,592 | 366,592 exact halves |

The optional Y conversion is exact because the standalone program returns
every Y mantissa unchanged. It is not a permission to compress arbitrary
dirty X/N/G outputs back to the input grid. The full-output one-bit
compression is exact by the all-output denominator proof; the required X0
witness prevents compressing the uniform output unit below six bits.

A bit-oriented converter can instead append g zero low bits in preallocated
owned slots. Visiting original magnitude bits from high to low prevents
overwriting an unread source bit. Per word this construction reads b original
bits, writes b shifted bits, and writes g low zeros; the sign is preserved.
It is an alternative to counting g arithmetic doublings, not an additional
free implementation. If the added cells contain borrowed dirt, that dirt
must be preserved and returned separately. Supplying zero padding and
headroom is therefore an ownership obligation.

The proved signed capacities are b+19 field bits and b+20 scratch bits for
the standalone prefix, or b+20 and b+21 for the full program. Compared with
the original b+1 signed words, these are 18 or 19 extra field bits per real
component. They include fractional refinement and magnitude headroom.
For example, the full 358-field public array alone uses
`366592*(b+20)` data bits under this fixed-slot convention. That count excludes
private C, arithmetic registers, delimiters, counters, routing stock and
control. The source does not provide their placement or movement price.

These scalar or within-slot bit counts do not establish a complete encoded
machine. A paid implementation must charge per-word carry/shift work, traversal
between actual field locations, phase permutations, loop/shape control, real
scratch supply and restoration. No universal tape distance, owner window or
controller cost is assigned zero. A producer that emits the refined format
directly must include its construction and zero-padding costs in its own bill.

## Named-source audit

The read-only entry audit used canonical main
`20ecf2891d80b5acf18d980b2164fb44ea7faa90` and the following exact source
boundaries. The statements describe the inspected documentation; they are
not a proof that no unpublished or uninspected caller can exist.

| Named candidate | What is actually supplied | Missing bridge to this entrance |
| --- | --- | --- |
| [p104-newton-source-contract](https://github.com/CrocSwap/integer-mult-bounds/blob/20ecf2891d80b5acf18d980b2164fb44ea7faa90/research/p104-newton-source-contract/README.md) and [tensor-Newton](https://github.com/CrocSwap/integer-mult-bounds/blob/20ecf2891d80b5acf18d980b2164fb44ea7faa90/research/p104-tensor-newton/README.md) | Exact source-local product domains and their conditional all-depth extension | Both explicitly leave actual input conversion, owners/routes and a favorable caller open. Their lattice index is inherited, not a new result here. |
| [Selected P104 port adapter](https://github.com/CrocSwap/integer-mult-bounds/blob/20ecf2891d80b5acf18d980b2164fb44ea7faa90/research/selected-p104-port-adapter/README.md), PR1746 | Exact selected-label map and eight-term decoder | Asymmetric-centre construction/reads, phase restoration, full supplier compilation and hosting remain unresolved. Label equality does not allocate the 197 fields. |
| [P104 source preconditioning](https://github.com/CrocSwap/integer-mult-bounds/blob/20ecf2891d80b5acf18d980b2164fb44ea7faa90/research/p104-source-preconditioning/README.md) | A scalar rank-four obstruction and one legal source shear for a different pooled correction model | Its prepared-X immutable-reader contract and retained channel are different. No map from that boundary to the present independent Gaussian inputs is given. |
| [P104 blockwise lifting](https://github.com/CrocSwap/integer-mult-bounds/blob/20ecf2891d80b5acf18d980b2164fb44ea7faa90/research/p104-blockwise-lifting/README.md) | A conditional exact XOR/backend reduction, including local cleanup and addressed gather/scatter | Both fast orientations, physical routing and a favorable actual backend remain premises. It is not a provider of this dirty-field interface. |
| [PR3590](https://github.com/CrocSwap/integer-mult-bounds/pull/3590), `5a607f77236bfc7caab957ce99f55377cd903980`; [PR3593](https://github.com/CrocSwap/integer-mult-bounds/pull/3593), `46c04613a19a5b7bd50d98e50bbc8ea8dc6275b0` | Owned-address header enumeration and a separate encoded Boolean header controller | These are useful control components, but neither outputs P104's Gaussian bank arrays, establishes their ownership, or proves the required packet/field consumer join. |
| [PR3605 conditional release](https://github.com/RossRichardson/integer-mult-bounds/blob/3efbb5de06a49ffeea6684482f2d3fe48cdca3fb/research/staged-644-660-conditional-release/README.md), `3efbb5de06a49ffeea6684482f2d3fe48cdca3fb` | A complete finite staged PR3133 owner/release binding and a stronger conditional numerical candidate | Its two source words have 632 live inputs and 91 private buffers. No mapping of those inputs, owner roles, coefficients or frames into this P104 caller is provided. Its paid 2,048-bit reserve cannot be transferred merely because a separate width estimate fits numerically. |
| [PR3610](https://github.com/CrocSwap/integer-mult-bounds/pull/3610), `4352496b3aa56ad17446ddbd1d78931f3d392996`; [PR3614](https://github.com/CrocSwap/integer-mult-bounds/pull/3614), `a6c3ae20abe0a15d781ee952e717d489552c9c66` | Native-channel flag-1 correction bills and an 18-entry forcing census | Different source/target charts and correction obligations; no P104 Gaussian-grid producer or general physical owner allocation is claimed. |

The canonical initial-reader and native-cache packages were also inspected:
one gives a scoped contact count, the other optimizes verifier memoization.
Neither adds the missing physical field boundary. The current-head audit is
bounded to these named sources and their metadata/README interfaces; it does
not cover every historical code diff, comment or unpublished construction.

## Recommendation and stopping rule

Retain the six/seven/six format theorem as a concrete improvement to the
caller specification. It removes a need to guess a large native guard and
separates input representation, storage range and output consumption.
It does not by itself justify a supplier build. Under PR3609's exact m=73,
W=832, five-forward/four-dual coverage assumptions, even the favorable native
relaxation fails. Nonnegative preparation, routing or controller charges can
only worsen that same inequality.

The strongest reopening test is consequently a named complete consumer with
a changed favorable allowance, together with one explicit physical source
mapping. Before construction, that mapping must state all participating
owners, initial/final formats and frames, mutable-source permissions, zero
stock, bounded primitive workspace, access/control costs and every required
return. This audit supplies the finite-format part of that table. The other
rows remain open rather than being manufactured from unrelated conditional
release or header-control results.
