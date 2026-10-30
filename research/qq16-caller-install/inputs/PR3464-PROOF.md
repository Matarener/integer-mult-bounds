# Parent-return refinement for the original physical complex controller

This is an independent, source-relative proof of the successful recursive
call/return boundary in Jose Manuel's
[PR 3385](https://github.com/CrocSwap/integer-mult-bounds/pull/3385), exact head
`7e5a187214126d31afc241a8f89f4a652352b58c`. The audited operations are
`Machine.prepare_child`, `enter_child`, `return_node`, and the `Parking`
codec. The original selected R480/T16 binding is fixed throughout.

The conclusion is conditional on the callee returning its specified complete
packet and closing its primitive scratch. It does not establish that
arithmetic endpoint, the complete controller's cost bound, root normalization,
an outer multiplication theorem, or a changed T74 binding.

## 1. Representation and precise claim

A well-formed role has a finite dense word over

\[
\mathcal B=\{0,1,3,5,6,7,8,9,10,11,12,13\},
\]

followed by blank cells. Its canonical head is at the first body position.
An owned origin marker may be `LEFT` or erased: `Machine.origin` explicitly
rearms an erased marker before parking. Equality of role contents below means
equality of this entire dense word. It does not require identical trailing
blank allocation, nor preservation of an erased marker; restored roles have
the canonical `LEFT` marker and body-origin head.

The fixed parked inventory is, in source order:

1. `current`, `header`, the fourteen `INPUTS`, and four `DERIVED` roles;
2. all 704 bank packet roles;
3. all eight private packet roles.

Thus the selected binding has 732 parked roles. The capsule, protected output,
parking stack, and reversing port are separate fresh tapes. The source
constructors allocate distinct roles; `Parking` also checks their identities.
The indexed packet accessor selects one of the 712 packet roles, including
private targets, without accessing a different role.

At a successful call boundary assume:

- the bank is gathered for the current group, its selection corresponds to
  that group's distinct keys, and the current PC names the actual child
  instruction `(target,rank)`; its temporary scratch and output are closed;
- Count descriptors are well formed, copied borrowed inputs are preserved by
  the inherited Count operations, and the child descriptor checks succeed;
- all owned role words and heads satisfy the representation above; the capsule
  and protected output are available, and `primitive_boundary` succeeds;
- the stack is a sequence of the encoded ancestor frames below, with its head
  at the blank top, and the reversing port is empty at its origin;
- the finite binding stays unchanged, reconstructs the same group from its
  event/subgroup/cover coordinates, and the saved values fit the source's
  finite header bounds;
- the callee returns a well-formed complete packet of the prescribed extent,
  restores the recursive boundary conventions, and closes its primitive and
  bank scratch. Descendants use this same controller and codec; other
  primitives respect their declared disjoint ports and do not write the
  parking stack or reversing port. A successful descendant return obeys this
  same contract.

Then the source operations resume the same parent at its next instruction.
They replace exactly the designated packet with the child's returned word,
restore every other parent role word except the consumed header, and restore
the parent's logical bank view. Older parked frames remain unchanged. The
capsule and protected return port are empty after the child handoff completes.
These claims hold at arbitrary finite nesting depth.

The finite checker exercises this theorem on concrete states; its finite
coverage is not the justification for the arbitrary-depth statement.

## 2. Exact stack codec

For a body symbol `s`, let `bits4(s)` be its four binary digits in
least-significant-first order. For the fixed role words `w1,...,wk`, define

\[
E(w_1,\ldots,w_k)=
\operatorname{bits4}(w_1)\,13\;
\operatorname{bits4}(w_2)\,13\;\cdots\;
\operatorname{bits4}(w_k)\,13\;12.
\]

The frame consists only of binary digits and the two delimiters. A body
symbol equal to 12 or 13 is encoded into four digits, so it cannot be
confused with a delimiter. Empty roles have an immediate role delimiter.
If the role words contain `B` symbols altogether, the frame length is
exactly `4B+k+1`, hence `4B+733` for the original selected binding. This is
an encoding-length identity, not a complete time or physical-space invoice.

`park` begins at the blank top of an existing stack prefix. It writes exactly
this frame, clears each consumed body symbol, and leaves every role at its
body origin. It neither reads nor modifies the older stack prefix. The final
stack head is the blank immediately following the new frame; the reverse
port remains empty.

`restore` first removes the final frame delimiter and then processes the
roles in reverse order. For each role it removes the role delimiter and
copies the preceding binary run, in reverse order, into the reversing port.
The scan stops at the preceding role/frame delimiter or `LEFT`, and leaves
that preceding delimiter untouched. Reading the reversing port backwards
therefore recovers the original bit order. Each four digits decode exactly
one original symbol; the code clears the digits while decoding and appends
the symbols in their original order to the restored role.

After the last role the stack head is the blank immediately after the
unchanged older prefix. The reverse port is empty at its origin and all
restored roles are at their origins. Thus `restore` is a left inverse of
`park` on every admitted tuple of role words, independently of their lengths
or contents. Induction on the number of stacked frames proves arbitrary
finite nesting. In particular, no frame length or buried ancestor payload
has to be retained in Python control.

`FiniteFields.write/read` provides the same elementary round-trip fact for
the bounded header: each value uses its prescribed fixed bit width, and
`read` checks both its bound and the exact end of the header. These checks
are used on the intact header preserved by the codec. They are not an
authentication theorem for arbitrary corrupted headers; a different valid
header can, for example, name another occurrence of an identical child
instruction.

## 3. Child descriptors and conservation of packet extent

At an active parent group write `d` for the fixed matrix dimension, `f` for
`columns`, and `K` for `spacing`. After the source's remainder-leaf step,
the active width is `e=df`; any removed left chunks have been added to
`before`. Write `a` for `after` and `U` for the exact positive `unused`
row quotient. For a child of rank `r`, `prepare_child` sets

\[
e'=rf,\qquad a'=a+(d-r)fK,\qquad R'=U.
\]

Every other `INPUTS` descriptor is copied unchanged. In particular,

\[
e'K+a'=eK+a.
\]

`shape` depends on the address exponent

\[
\texttt{front}+3\,\texttt{compact\_bits}+\texttt{before}
 +eK+\texttt{after}+\texttt{back},
\]

and multiplies its power of two by twice `component_bits` and by
`coefficients`. The equation therefore preserves the entire within-row
extent, including every spectator field. With unchanged `prefixes` and
child row count `U`, the child input has exactly the extent of one gathered
parent packet. The check `0<e'<e` supplies strict descent. These are integer
identities for arbitrary admitted descriptors, not only for fixtures with
zero front/back/before fields.

The target's complete word is copied to the capsule before the parent is
parked. All unchanged descriptor encodings are copied verbatim. The three
changed descriptors are constructed by the actual Count operations above;
the proof needs their exact numerical meanings, not an invented requirement
that arithmetic preserve an unrelated padded encoding.

## 4. Simulation of one successful call and return

`prepare_child` saves the parent root flag, event, subgroup, cover index,
next PC, target and rank in the header. The saved PC is the current PC plus
one: the interpreter deliberately does not also increment the PC on this
child branch. Its temporary Counts are closed in `finally`.

`enter_child` checks primitive closure, rearms all parked origins, and
applies the codec. It then transfers the capsule's current packet and input
descriptors into the now-empty active roles, consuming the capsule. All
other active role words are empty. It clears the transient bank view and
group, sets the root flag false and starts the child at its node state.
The suspended parent state is represented by the encoded stack frame,
whose older prefix was not touched. The active child owns its separate
copy of the selected packet and input descriptors.

At successful child return, `return_node` first moves the complete child
`current` word to the separate protected output. It clears all active
parked roles and then restores exactly one parent frame. The output is not
a parked role, so neither clearing nor restoration overwrites the child
result. Reading the restored header recovers the saved control state, after
which the header is cleared.

The binding reconstructs the same parent group from the saved finite
coordinates. The code checks that `pc−1` is a child instruction with the
saved target and rank. It then transfers the protected output into exactly
that packet role, clearing the saved old target and consuming the output.
Every other restored role word is unchanged. Finally it reconstructs the
selection by enumerating the group's distinct keys, sets the bank source to
the restored `current` role, marks the bank gathered, and resumes group mode.
These are exactly the original bank-view data, with the intended single
packet replacement.

Combining this one-frame simulation with the codec induction proves the
claim for arbitrary finite nesting. The positive strict decrease of child
width supplies the recursive well-founded measure; no proof of a callee's
arithmetic is obtained merely from that decrease. At the root, the separate
root-return branch clears the active owned roles, requires an empty stack,
and returns the protected output without popping a nonexistent parent.

## 5. Source boundary and limitations

The unchanged principal sources are retained as
[machine.py](inputs/pr3385/machine.py),
[parking.py](inputs/pr3385/parking.py),
[bank_packets.py](inputs/pr3385/bank_packets.py), and
[selected_binding.py](inputs/pr3385/selected_binding.py).
`SOURCES.json` records their exact pinned origin and the broader authenticated
runtime closure. The inherited Tape, Count, marker and ownership operations
remain part of that source-relative boundary; the checker does not replace
them with a new physical implementation.

This proves preservation and restoration on successful admitted states.
It does not promise rollback after arbitrary malformed tapes, primitive
failures or private-state corruption. Nor does it prove the original global
gather/scatter endpoint, every scalar/native endpoint, root normalization or
rounding, the production guard width, or a complete physical invoice.

Credit for the controller and the original refinement argument remains with
Jose Manuel (`jmbarrancoml`), PR 3385, including its attributed dependency
chain. The codec source explicitly builds on PR 2809's fixed-role protocol.
This package contributes the independent successful parent-return proof and
its separate controls, not a new controller implementation.

Copyright 2026 Sagar Thakrar. Written with substantial OpenAI Codex
assistance. Licensed under the Apache License, Version 2.0.
