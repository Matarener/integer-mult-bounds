# Completed output handoffs without payload copies

This opt-in specialization changes two completed boundaries in the retained
PR2915 `C1 -> B1 -> C0 -> A0` implementation. The preceding C0 execution, native
child sequence, source maps and numerical parameters are unchanged. The changed
interface permits a **finite permutation of internal tape-role bindings** at a
completed output handoff. It does not identify two live buffers or assert that
moving a payload between two fixed physical tapes is free.

## Named expense and new contract

PR2899 `Ordinary.execute_plan` obtains a completed scratch lease, calls
`role_parking.transfer(result, self.output)`, and ends the old lease. PR2915
`Adapter.swap` then copies that ordinary output into a parent scratch lease,
rewinds the result and clears the ordinary output. Both outputs are distinct
from the borrowed input; the new implementation preserves that property.

At either boundary let L be one live scratch lease, with slot s in a fixed pool,
and let O be the separate ordinary output role. Require:

- the lease is active and registered at s, with the correct physical binding;
- O is not a tape of that pool, and the two role origins have LEFT immediately
  before their current heads;
- at publication O is empty; at adoption the newly acquired L is empty and the
  ordinary execution is closed;
- the completed result has the inherited dense BODY alphabet. The replacement
  retains `transfer`'s rejection check as a read-only scan before publication.

Exchange the physical role bindings of O and L, updating **both** the pool's
slot table and the lease's physical view. The slot number, lease object and
liveness relation do not change. At publication O now denotes the completed
result and L denotes the empty old output; the original `result.clear()` ends
that empty lease. At adoption the parent lease denotes the completed result,
and O denotes the empty old parent role, ready for native rearm.

Every premise is checked before the transposition. Marker checks restore their
one-step head movement even on rejection. The dense scan also restores its
source head. Arbitrary interrupted native computations still have the inherited
source's limited recovery contract; this is a successful completed-call result.

## Why this is a fixed-tape operation

Let R be the total number of physical stream roles of the fixed compiled parent
pool, ordinary pool and ordinary output. R depends on the compiled source and q,
not on payload width or recursion depth. Replace the original finite control Q
by `(Q, pi)`, where pi is a permutation of those R physical roles, together with
the already finite pool-slot liveness state. An instruction on logical role j
executes on physical role pi(j). A completed handoff changes pi by one
transposition. No payload cell moves, no physical head is reset and no numerical
address is decoded by that control transition.

This is an explicit finite-control refinement: at most R! permutation states
per original control state suffice. It can be large, but is a fixed compilation
allowance of the same kind as the inherited F_q. The Python tuple/reference
updates in `exchange.py` represent that finite selector; they are not a unit-cost
claim about arbitrary RAM pointers or an infinite collection of tape addresses.
Their host implementation is O(R), and their compiled control overhead is O_q(1).
The complete tape-I/O invoice below charges every actual head move/read/write.
An exhaustive emitted R!-state transition table and formal proof-kernel check
are not supplied.

The transposition acts only on the completed lease and the separate empty role.
Every other active lease keeps its physical role, bytes and head. A stale ended
lease remains inactive; its repeated clear is a no-op and cannot erase a new
borrower. Updating only `lease.physical` while leaving `pool.tapes` unchanged
would violate the ownership invariant: that explicit mutant is rejected by the
inventory check. Role identity is not inferred from numerical payload data.

The opted-in source sites have no remaining use of a stale output alias: after
publication the old local `destination` is unused, and `execute_plan` returns
the current `self.output`; after adoption the replacement `swap` does not clear
the old `returned` alias. Subsequent rearm, finish, allocation and cleanup read
the updated role tables. Other ordinary instances retain their original transfer
function. Context exit restores the original module binding even on exceptions.
The C0/A0 bindings remain suspended/restored exactly as in PR2915, so the change
does not introduce a circular backend call.

This internal role contract is necessary. A consumer that insists on the result
in a particular immutable physical output tape must still pay a transfer to it.
The selected outer fixed output contracts and other transfer sites are not
changed. The public opt-in adapter still returns a distinct owned parent lease.

## Exact local cost and complete recurrence

Let V be the number of BODY symbols returned by the completed ordinary call.
Count literal physical tape reads, writes and unit head moves across the two
handoffs, from the completed inner result at its origin through the owned parent
output at its origin. Include acquisition and ending the inner lease. Direct
counting of the retained `transfer`, `append_tape`, `rewind` and `clear` loops,
and of the new validation/origin checks, gives:

| Operation count | Retained boundary | Exchanged boundary |
|---|---:|---:|
| Reads | 12V + 18 | 2V + 13 |
| Writes | 4V | 0 |
| Unit head moves | 10V + 24 | 2V + 16 |
| Total | 26V + 42 | 4V + 29 |

The exact saving is **22V + 13 physical tape operations**. The new linear term
is validation, not an uncharged copy. Eight literal fixtures, including empty
and record-alphabet bodies, independently meter these coefficients. The dense
BODY check and owned final-output erasure remain present; output erasure occurs
when the parent consumes that lease and is common to both executions.

For one actual B1 call write its complete old physical cost as

    A_old(V,E) = A_core(V,E) + H_publish_old(V).

Here A_core includes parameter selection, padding, both fitted C0 roots or the
elementary fallback, all child returns, numerical scratch, restoration, private
erasure, and every other source operation. No part of A_core is discarded.
For the enclosing C1 swap, let J be its unchanged encoded setup and closing cost.
Then, on the same admitted input and native branch,

    S_old = J + A_core + H_publish_old + H_adopt_old,
    S_new = J + A_core + H_publish_new + H_adopt_new
          = S_old - (22V+13).

These equalities use the source's tape-I/O model. In a model also charging finite
control, add an explicit constant `c_R` per exchanged boundary; there are no
width-dependent control or hidden numerical-word charges. On the Python host,
the finite selector's O(R) cost is included in measured wall time.

For an enclosing C1 recursion tree, count each complete B1 invocation as one
whole local primitive interval, including all its C0 descendants. Keep those
full local bills L_u and the unchanged recursive C1 child calls. At node u let
H_u be its reached opted-in completed B1 handoffs. In tape-I/O units the recurrence is

    T_new(u) = L_old(u) - sum_(h in H_u)(22V_h+13)
               + sum_(v child of u) T_new(v).

Only handoffs actually contained in L_old are subtracted; a handoff is never
counted again in its child's toll. All other recursive children and restoration
terms remain. Telescoping subtracts the stated saving once per reached handoff.
Equivalently, apply the single-call formula without changing any C0 child cost.
With finite-control charges add `2c_R |H_u|` explicitly. The inherited asymptotic
bound `O_q(V(n+w^(1-a1)))`, with `a1=169711/10^8`, remains valid. This is a lower
linear boundary expense, not a new exponent or an alteration of the paid child
histogram.

No new physical stream roles or numerical words are allocated. At each exchange
the set of physical tapes, their backing and all cell contents are unchanged;
only the role permutation changes. The omitted parent copy also avoids its
temporary second payload. Future high-water backing may be distributed among
different roles, so an unchanged per-role byte high-water mark is not claimed.
The fixed R-role bound and inherited `O_q(V_root)+F_q` total-space form remain;
their original compiler, stock and root-coupling premises are still required.

## Evidence and scope

Complete q=3/5 route fixtures retain every original independent address column,
borrowed input, low carry, dirty occupied lease and head check. They audit the
entire union of parent/ordinary physical roles after every native handoff.
The first 486-bit route falls from 284,709 to 263,273 physical operations; its
four 243-symbol native handoffs account for exactly `4*(22*243+13)` saved steps.
An identity-high route has no native handoffs and is unchanged.

The fitted test executes two genuine C0 roots under original A0 bindings, then
checks all 1,024 source columns, parent numerical objects, distinct output,
cleanup and the complete physical inventory. The saved handoff is only one
component of that much larger run. This is not selected GL64 payload execution,
a full selected supplier replay, an independent proof of the inherited all-size
caller, or an implementation of the separately claimed complex controller.

Credit Jose Manuel/jmbarrancoml PR2809/2899/2915, David Arias PR2753,
Nick Petalas PR2808, the fixed-role/ordinary and PR2157 factor lineage, and the
retained high-cube accounting work. Tekalign, substantial OpenAI Codex assistance.
Apache-2.0. The finite-control argument remains subject to independent review.
