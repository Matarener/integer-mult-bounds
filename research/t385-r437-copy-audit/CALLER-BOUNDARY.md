# Where the complete-stream implementation handoff reaches actual code

This is a source inspection, not execution or independent validation of
PR2809's universal refinement proof. The inspected files are pinned as
provenance at canonical main `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.
Jose Manuel / jmbarrancoml supplied the physical lowering of David Arias's
PR2753 caller. Their notices and the selected primitive/parking lineage remain.

## A concrete wrapper already exists

In `research/selected-bit-physical-caller/macro_code.py`, `compile_node`
handles a local COPY event by emitting, in order:

1. Copy the current staged center to the permanent `copy_source` role.
2. Execute one residual on `copy_source`, using that event's request and the
   current common low class.
3. Transfer its completed output to the local private role.

At ERASE it emits a clear of that private role at the original guarded
position. No helper-label projection appears in this wrapper. The source
`LocalState` validates the event lifecycle during compilation; the wrapper
is not a free-standing license to clear arbitrary persistent state.

`macro_machine.py` implements COPY by committing the source tape to the named
destination. Its `commit` clears the destination, appends the entire source,
and rewinds the destination. It clears the returned source only if that
source is a temporary `Lease`; a staged permanent source role is preserved.
MOVE transfers between fixed roles; CLEAR calls that role's tape clear.
These operations make explicit the complete source clone, owned output and
linear disposal that a cost audit must retain. They do not support charging
an unspecified dirty-input projection as if it were the whole source.

The source proof, section 3, describes that same source-clone/residual/private
sequence. Section 5 inventories scratch inside atomic blocks, and sections 6–7
supply the parent parking/return argument. This is an existing proposed
implementation path, not an assertion that nobody has written a caller.

## What the reduced execution actually covers

`macro_local_checks.py` observes the copied source before the residual,
compares the copied output against an independent address permutation, and
checks that the original source is unchanged **before** later XOR cancellation.
The published complete GL2(F3) fixture checks 96 COPY endpoints, 192 MOVE and 384
IDLE residuals on 31,104 bits. Its source proof explicitly says it has no
internal child. A separate GL2(F2) fixture tests recursive control; the selected
junction probe is not a complete selected GL64 payload.

This session did not rerun those fixtures or independently review the whole
parametric proof. The repository's current physical-contract map also keeps
PR2809's universal refinement pending despite archival incorporation and
later ordinary-backend compositions. Reduced fixtures and source archival
status should not be turned into an R437 implementation/admission certificate.

## Precise next implication

The new R437 checker establishes the exact-function endpoint and guards of
R437's actual rank-seven requests. The concrete wrapper above is structurally
compatible with a universal complete-stream residual. The unclosed step is
an exact-source binding and proof that its rank-seven residual/caller:

- accepts R437's current source/owner/chart data and all arbitrary helper
  functions, including the newly occurring input 340;
- preserves its borrowed source and returns the transformed complete output;
- charges source clone, all routing/adapters, child execution, transfer and
  complete disposal under the retained volume-normalized tariff;
- restores child scratch and parking state within the actual full reserve;
- satisfies the admitted numerical format, exceptional-class and recovery
  conditions on the required all-size domain.

The available source-level compiler/primitive proof may be the route to those
claims, but this finite application audit does not independently validate it.
No second recursive uncompute is forced by the existing wrapper: it transforms
an owned clone and later clears owned output. Conversely, clear is a real tape
operation and its linear cost and scratch lifetimes remain part of the bill.

A useful next audit should start with `compile_node`'s COPY branch,
`Machine.commit`/COPY/CLEAR and the bound residual plan, then connect one
actual R437 request to the general primitive and lease/return arguments.
Repeating the GL2 endpoint fixture alone would leave that implication open.
