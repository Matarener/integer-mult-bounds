# Actual caller packet and encoded descriptor boundary

Chris R, with substantial OpenAI Codex assistance. Apache-2.0. The retained
physical controller, encoded Count operations, gather/scatter and recursive
capsule implementation are credited to Jose Manuel and their source lineage.

## The cut must respect complete cover sweeps

The selected mechanism's producer boundary is the **complete bank after the
QQ16 replacement of the first B1 sweep**, before the next source idle sweep and
bridge. It is not one local F0/B1 group. The selected producer and decoder have
cover-wide barriers and owner maps; completing a single 704-packet gather does
not complete those operations. The central continuation proof must identify
and justify that global program boundary.

The compiler here is a building block at the actual gathered-group boundaries
inside such a global program. Its interface is an actual retained `Machine`
with `mode == 'group'`, nonempty `group`, `bank.state == 'gathered'`, and closed
scalar/leaf/monomial scratch. It does not infer a global cut from those local
conditions. It does not assert that a QQ16 recovery invocation appears in the
unchanged selected binding.

The four boundaries relevant to this component are:

1. Producer entry: an admitted complete physical parent bank, with encoded
   root and current-node descriptors. The root's row padding, numerical grid,
   arbitrary dirty helper values and initial ownership are inherited or proved
   by the integrated producer contract, not fabricated by this compiler.
2. Prepared native entry: a current owner packet acquired by the actual
   `BankPackets.gather` path, then the decoder's owned copy and signed right
   wrapper, together with the encoded child descriptors below. The decoder
   owns its output/private banks; the original current bank remains borrowed.
3. Completed native return: the exact retained C endpoint returns the same
   complete rectangle. Two numerical interfaces are distinguished below. The
   installed fine-grid route retains the actual source quantum and width, using
   the new full-pipeline range/divisibility argument. Both positive and negative
   calls use identical physical geometry; their right/left monomials, including
   the negative XOR, remain paid work.
4. Continuation exit: the new current values are written to the required fixed
   source owner ports, every cover sweep is committed, both subsequent source
   bridge legs run, and all protected decoder/compiler storage is retired.
   Packet construction alone proves none of these semantic exit conditions.

## Encoded compiler and complete packet preservation

`packet.py:PacketCompiler.compile` takes the actual source Count roles. No
packet length, row count or width is decoded into a Python integer. Binding
constants (dimension, maximum child rank, families, cover cardinality) are
finite source program constants. Count arithmetic is executed under its own
fixed 64-tape scratch scope; the caller scope must be suspended and empty.

Write n=73, m=48, L=14336 Gamma in the selected source. Let the actual parent
have e=n lambda after remainder processing, R rows, spacing K and suffix A.
The compiler checks with encoded arithmetic:

* lambda=`columns` is positive, e=n lambda, and e<=root_width;
* prefixes, unused rows, K, guard, physical component width, coefficient count
  and root_width are positive; residue<K;
* division of the actual R by the actual fixed L has zero remainder and its
  quotient equals the actual stored `unused` field U;
* the child stock L^D0(lambda) divides U, where D0(x)=0 for x<n and
  D0(x)=1+D0(m floor(x/n)) otherwise.

The last test is an encoded loop: copy lambda, repeatedly divide by n and
multiply by m while it is at least n, multiplying a stock Count by L once per
iteration. Then divide U by stock and check zero remainder and positive
quotient. This direct check prevents an arbitrary caller from importing the
conditional stock conclusion of #4129. It does not create absent stock or
justify uncharged padding. Actual root reservation/padding is the source path
which supplies stock; failure is a rejection, not a repair.

The compiler writes fourteen independently owned encoded descriptor tapes:

```
width = columns
rows = unused
after = parent.after + (n-1) columns spacing
all other INPUTS fields = copied current parent field
```

In particular, `component_bits` is the actual H_b, `compact_bits` is the address
reserve H_g, `guard` is G, and `root_width` is d. They are not interchangeable.
The compiler neither derives nor changes the numerical quantum, and its width
metadata does not establish an entry-range bound. There are two admissible
numerical interfaces. The original #4129 coarse bridge retains its own
completed-grid, low-zero and sign-extension projection obligations and charges
any fine/coarse conversion. The selected installed route instead retains the
actual source grid q_s=2^(-p-Delta), Delta=2^210000 d, and the actual physical
H_b=p+2Delta+3 throughout producer, decoder, reconstruction and return. Its new
full-pipeline bound in `cost.py` and `COST.md` first bounds ideal intermediate
values and denominator debt, including native interiors, within that global
reserve; exact bit execution then follows under the retained arithmetic
contracts. This route needs no coarse downprojection. Neither interface is
proved merely by copying the component-width descriptor.

The real current owner packet has

```
[prefix][unused row][front][H_g][H_g][before]
[73 lambda K][after][H_g][back][coefficient][real/imag H_b bits].
```

Its rank-one reinterpretation changes no bit:
`73 lambda K + after = lambda K + (72 lambda K + after)`.
Every prefix, row, coefficient and spectator survives, including arbitrary
correlations. The descriptor bytes match the unchanged `prepare_child(...,1)`
implementation. Right/left monomial execution still has its own numerical,
compact-layout and closed-engine prerequisites.

The direct stock test does not replace the all-depth source argument. If the
root supplies L^D0(d) and every source child has width at most
m floor(e/n), monotonicity of D0 preserves the necessary quotient stock at each
node. At rank one, D0(lambda)<=D0(73 lambda)-1. The encoded compiler checks the
specific current instance, while that argument explains its reachable domain.

## Paid acquisition, lifetime and invoice

The actual `Machine.next_group` calls `BankPackets.gather` with encoded
`prefixes`, `unused`, `row_bits`, scanning the complete current bank and copying
exactly the source-bound family/cover keys. Reusing its gathered packets does
not incur another full-bank gather, but that original gather remains in both
same-boundary invoices. The proposed global decoder may need different or
additional gathers; each must be charged by the integrated schedule. No
logical 2^(73 lambda) size replaces the complete physical packet volume.

The compiler owns exactly fourteen descriptor tapes plus 64 fixed scratch
tapes. Default construction allocates **no original-value snapshots**. An
optional `capture` operation exists for the explicitly rejected/alternative
producer-snapshot route and the physical preservation fixture. It allocates a
fixed requested number of tapes, copies all bytes with retained `copy_symbols`,
and preserves the source. It cannot be treated as free retained input. The
selected recovery path does not use it.

Let A(f;args) be the actual read+write+move invoice of a retained encoded
operation f, including its borrowed Count scans and scratch retirement. The
complete descriptor price is the sum of the calls in `compile`: positive and
comparison scans; encoded copies/products; exact parent division; every D0
loop comparison/division/multiplication; exact child-stock division; all
fourteen descriptor copies; temporary Count closure; and final descriptor
retirement. The D0 loop runs exactly D0(lambda) iterations. This is an
executable constructive invoice, not an assertion that binary arithmetic is
free or a replacement by a host integer calculation. The whole module costs
this invoice once per descriptor lease, plus each actual gather, wrapper,
conversion, native call, copied output and retirement charged elsewhere.

For an optional snapshot of s packets of actual bit volume V, add s complete
preserved `copy_symbols` calls and s eventual `Tape.clear` calls. No credit for
original F0/B1 work follows from these copies. The fixed compiler inventory is
additional to the caller, decoder output/private banks, separate native
Machine and wrapper ordinary inventory.

## Executable evidence and rejection controls

`fixture()` is invoked only after the central verifier authenticates the
retained source. It uses the unchanged actual `Machine`, `BankPackets`,
`prepare_child`, recursive execution, return, scatter and commit implementation.
A local subclass inserts the compiler at an actual `next_group` return; it
changes no numerical source operation. An observer compares all fourteen
compiled descriptor byte streams with the actual first child capsule.

The reduced geometry is n=2, maximum rank=1, two prefixes, four parent rows,
two coefficients, and 64 nonconstant signed complex values. Fixture setup uses
host integers to construct a small input tape; this is explicitly a test oracle,
not the claimed encoded producer/compiler. The entire parent executes after
the test, preserving the borrowed source and all original descriptors.
Wrong quotient rows, wrong active width and out-of-range residue are rejected
before a live compiler lease is published. Compiler and optional test snapshots
are eventually erased. Read/write/move deltas for the successful compiler,
optional copies and their retirement are recorded, separately from failed
control runs and unchanged producer execution.

This fixture tests actual physical construction, not an endpoint double, but
it does not execute the selected O73/GL64 program or prove current-value/frame
reconnection. Those remain separate integrated proof and fixture obligations.

## Reuse and open questions

The current root plan and row-padding implementation already supply encoded
reservation and stock. #3055 Compact support is inherited through the physical
controller and receives no new integration claim. Sagar Thakrar's #3607 address
refinement is compatible evidence for the unchanged source reserved-axis and
padded-core partition; its endpoint-double fixture is not our actual C
execution. #4129's exact C endpoint and source backend hypotheses remain
inherited. Its coarse-format projection theorem is relevant only if that
coarse interface is used; the installed fine-grid route has the additional
full-pipeline numerical proof described above. Its prepared input theorem is
not relabelled as this caller's semantic installation.

The decisive remaining question is whether the full producer/recovery/G/bridge
schedule is correct on current owner-dependent payloads at complete cover
boundaries and whether its actual removed work pays the additional native,
map, any required interface conversion, copying and storage costs. A compiler pass alone cannot answer
that question or justify publication significance.

## Whole-family entry at the completed producer fence

`compile_global(parent, field, expected_event)` closes the additional cover
serialization obligation for the full-bank route. It accepts only the actual
completed-event source state: parent active in group mode, no current group,
bank closed, event equal to the fixed selected fence, subgroup and PC zero,
and cover cursor equal to the actual cover cardinality Gamma. The caller must
bind `expected_event` to the completed final QQ16 B macro in the finite global
program. A successful local-group test cannot supply that fence.

The lifecycle acquisition uses the actual `BankPackets` implementation with
fixed `(families=parent.families, covers=1)`. Its encoded row extent is
`Gamma * parent.row_bits`, its row count is `parent.unused=U`, and its prefix
count is P. Selecting `(family,0)` therefore returns the whole family in order

```
original prefix, cover, unused row, complete within-row packet.
```

No cover is removed or treated as a free spectator. For the independent
native invocation the first two fields combine into an encoded prefix count
`P_native=P*Gamma`, with `rows=U`. The child width and suffix remain lambda and
`after+72 lambda K`. Every other input descriptor, including the actual H_b,
H_g, K, G, residue and d, is copied from the parent. Hence the native entry
contains exactly `P*Gamma*U` complete rows.

Before publishing descriptors, the compiler recomputes the complete row size
from the encoded source fields:

```
A = front + 3 H_g + before + 73 lambda K + after + back
row_bits = 2^A * coefficients * 2 H_b
field_bits = (P Gamma) * U * row_bits.
```

It compares the first formula with the actual parent's derived `row_bits`,
then validates the entire acquired field using an encoded countdown: exactly
`field_bits` binary symbols followed by blank. It restores the borrowed head
on success and rejection. The parent quotient and child-stock checks are the
same encoded checks described above. The global service additionally computes
`fixed_power(parent.width,1000,parent.root_width)` and requires its result to be
at least the root width. This is a fresh **post-remainder** admission check.
The original node's nonleaf test occurs before it removes a remainder, so its
success does not imply this service condition. A caller that passed at width
73 lambda+r may fail after removal to 73 lambda; that domain is rejected here
until a separately proved service contract applies. This construction supplies the complete
native packet geometry from an actual whole-family acquisition, rather than
assuming a prepared rank-one payload.

The extra bill includes the encoded capped 1000th-power nonleaf test and its
comparison/retirement, followed by prefix multiplication, row-size reconstruction,
comparison, field-size products, entire binary scan and countdown retirement.
All these operations are executed, and their source/owned tape actions are
included in the compiler's recorded setup invoice. They are additional to the
separately charged `BankPackets.gather` and actual child execution; the latter
is excluded from the compiler meter to avoid silently reporting a partial
native bill. Final descriptor retirement is measured separately.

The installed decoder does not use this auxiliary whole-family descriptor
block as its native capsule. It receives `service_descriptors` with prefixes P,
rows448 Gamma U and width73lambda, then gathers each owner separately. Actual
`prepare_child(target,1)` supplies prefixes P, rows U, widthlambda and the
extended suffix. The paid auxiliary P Gamma block is closed by PacketCompiler.
The following independent whole-field fixture instead executes one complete
whole-family native call using P Gamma prefixes; it tests that geometry without
claiming the installed per-owner calls use it. Costs retain per-owner packet
volume `v=P U row_bits` and Gamma invocations.

`global_fixture()` executes the actual cover-two parent through both cover
groups, acquires one whole family with actual `BankPackets`, calls the encoded
compiler, runs a separately closed actual rank-one C `Machine` on the complete
family, and resumes the original parent to its completed endpoint. The fixture
uses two original prefixes, two covers and two coefficients, giving four native
prefixes and 32 nonconstant complex values in the acquired family. It checks
the C child against an independent exact address oracle and the final entire
parent against a two-axis oracle. Wrong producer fence, short acquired field
and insufficient actual child stock are rejected. A separate exact boundary
control sets the reduced parent's root width to `3**1000`: the pre-remainder
width 3 could pass the source test, while its post-remainder width 2 fails the
new service test. This rejection preserves descriptor and field bytes/heads,
erases compiler temporaries and restores the fixture's original root Count
before the successful execution. All parent descriptor bytes
and current-bank values are preserved, and compiler/acquisition/child storage
is retired. This closes a physical acquisition/descriptor composition for
reduced geometry; full QQ16 producer and reconnection semantics still require
the central integrated argument and source-bound schedule.
