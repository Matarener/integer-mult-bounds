# A receiver-only obstruction to the direct frame-520 deletion

This contribution was produced by Nick Petalas. The input word and root-relay
construction are DreamingOfClouds's PR #6144, at
`4f3b67e7c37ae270da9584033132866d0cf63e42`, with Ali Romman and the retained
P104 lineage. The new result is the separating input for the attempted edit
below, together with its receiver-only impossibility consequence.

## Exact model and attempted edit

Use the retained symbolic scalar convention. Every public input has an
independent coordinate `x_r`. An ADD replaces a row by a linear combination
of rows at the same chart. A MOVE transports its represented row and changes
the chart. INIT and CLEAR concern owned fields. These are the algebraic
conventions of the predecessor's finite word; no new physical primitive is
introduced here.

All event ordinals in this paragraph are zero-based in the pinned PR6144 word.
The function `proposed` in `verify.py` defines the entire attempted edit:

1. Remove events 12888, 12932, 12933 and 12934, which move helper 497 through
   519/520 and give it the register-48 and register-228 reads.
2. Before event 12918, move 497 directly from 3 to 737 and add register 228
   there with coefficient 1. Register 228 is still at 737.
3. Remove events 13484, 13485 and 13486. Before event 13487, move owned 772
   directly from 529 to 737 and add it to 497 with coefficient -4.
4. Replace event 15459 by the move of 497 from 737 to 914.

All other events, boundary charts and fields are unchanged. The edited word
has 22,815 events. Its moves and scalar meetings through the cut considered
below are legal. Its operator is incorrect; it is not offered as a supplier.

The old register-48 read is the linear form

`V = x_48 + x_32 + x_98 + x_85`.

Before original event 15647, `ADD 145,161,-1/2,914`, the edited and original
rows differ only in fields 497 and 161. Their differences are respectively
`-V` and `V/2`. This comparison is over all 799 symbolic input coordinates,
including the formal owned entries before initialization. It checks the
effect of the new edit, not the correctness of the predecessor's theorem.

## Allowed repairs and theorem

Freeze the edited prefix through original event 12934 and the chart trajectory
of every field. Freeze every nonreceiver scalar event. Between the cut after
that prefix and the cut immediately before original event 15647, allow any
finite homogeneous linear operations on receiver 161, using any fields
currently at its exact chart. Coefficients may be arbitrary constants;
repeated reads, replacements of its existing scalar operations and SCALEs
are allowed. No workspace, source mutation or changed receiver MOVE is allowed.

**Theorem.** No such repair gives receiver 161 its original PR6144 row at the
specified consumer cut, for all inputs.

Take the separating input

`x_32 = 1, x_5 = -1, x_r = 0 for r not in {32,5}`.

The exact finite certificate in `RESULT.json` establishes the following facts:

- The edited receiver is zero at the start of the repair window.
- At every cut in the window, every other field at receiver 161's chart is
  zero on this input.
- There is no ADD or COPY reading 161 into another field in the window.
- The original required receiver value at the consumer cut is `-1/2`.

There are 2,712 cuts, including the entry and consumer cuts. The verifier
checks 241,377 coframed donor occurrences. It inspects every cut, including
ones without an existing receiver operation. Between consecutive cuts no
frozen event changes a donor's value or chart, so extra receiver operations
at arbitrary times have the same donor menu as a checked cut.

Because the frozen program never reads the receiver into another field in
the window, changing receiver operations cannot change the donor values.
Induct on the frozen events and any interleaved repair operations. The
receiver starts at zero. A homogeneous linear operation on zero arguments
leaves it zero, and moving a zero row leaves zero. Thus it is still zero at
the consumer cut. It cannot equal the required `-1/2`. This proves the theorem.

Equivalently, the coefficient functional `row[32] - row[5]` annihilates the
receiver's initial row and every available donor row, but evaluates to `-1/2`
on the desired row. This is an exact linear separation certificate, not a
failed coefficient search.

## Consequence and boundaries

The direct rerouting cannot be completed by adding or resynthesizing scalar
compensation only on receiver 161 in this window. A successful construction
must change an additional source, trajectory, earlier prefix or consumer
contract. In particular, crediting the saved moves without delivering `V/2`
to the consumer is invalid.

This does not exclude removing frame 520 by another construction, repairing
outside this window, or accepting and compensating a different value at the
145/161 consumer. It does not address removing frame 737. No complete paid
invoice, new kappa, native implementation, full predecessor replay, supplier
admission, proof-kernel acceptance or complete multiplication theorem is
claimed. The five selected framework assumptions remain.

## Verification design and bounded code

The checker authenticates the exact upstream compressed word before decoding
it. One pass evaluates the separating input and checks every common-chart
donor. A separate sparse symbolic interpreter compares all input coefficients
at the consumer cut. Five false-claim controls reject a changed source anchor,
the wrong witness sign, two unavailable reads and a wrong root-read coefficient.
The checks use explicit exceptions and also run with optimization enabled.

The code has no recursion or asynchronous work. Source dimensions fix 799
fields, 1,093 charts of dimension at most 9 and 22,818 events; all loops and
collections are bounded by these inventories. The two symbolic states contain
at most 799 squared coefficients each, and no per-cut state is retained.
Each function is shorter than 60 physical lines.

Power-of-ten rule 3 has a managed-runtime deviation: Python allocates integers,
Fractions, dictionaries and parser objects during replay. The source byte pin
and fixed inventories bound live state; this is a terminating exact checker,
not a steady-state service. Rules 8 and 9 retain the standard JSON decoder
and five finite zero-argument control callbacks. They never evaluate source
code, load plugins or dispatch to external jobs. Follow-up for a constrained
runtime would replace these with fixed arrays and direct control invocations;
the present package does not claim fixed-allocation execution. Warnings-as-errors
and normal/optimized execution supply the available Python diagnostics.
