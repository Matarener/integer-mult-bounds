# Literal pair invoice and bridge boundary

This audit compares the selected gauge44 pair in replica 0 with literal
`F_0; B_1_2` from the QQ16 packet. The selected calls are `calls[0]`
(stage 0, forward) and `calls[4]` (stage 1, backward), not the first two
serialized calls. The intervening calls concern other replicas. The next
same-replica ordinary bridge is execution event 6, source event 3, after
the pair-1 idle transition. It applies, at every one of the 112 ports,

```
X_0 += X_1
Y_1 -= Y_0.
```

Here the subscripts name global pair banks. Each bank has 112 ports.
Thus both legs and the selected A/T ports remain part of the caller's
observation. The inherited signed bank semantics are bound to the pinned
`global_k.py` controller by AST checks: its pure four-pair recipe matches
all eighteen preterminal events of the selected recipe, and the signed
bridge branch performs exactly the two updates above. Source `exchange`
and selected `terminal(pairs=4)` remain explicitly different terminal
conventions. Hosted execution event 6/source event 3 matches recipe event
2. This authenticates inherited signed controller semantics; it does not
execute the physical complex bridge. The bridge has 224 complex ADDs, or 448 real-component
additions. The conservative typed dyadic ADD compiler used for the local
scalar invoices instead charges 1,792 real primitives. These are different
accounting conventions, explicitly separated in the receipt. The unchanged
bridge appears on both sides of a valid replacement comparison.

## Local words

All counts below come from the literal event lists. `center` events are
counted as native children as well as `climb` and `native_line` events.
In particular, the selected word's eight rank-eight centre calls must not
be omitted from its baseline.

| Component | Selected forward | Selected backward | QQ16 F0 | QQ16 B1_2 |
|---|---:|---:|---:|---:|
| Native child calls | 3,494 | 3,494 | 3,494 | 3,510 |
| Sum of native child ranks | 5,586 | 5,586 | 5,530 | 5,546 |
| Scalar macros | 19,693 | 19,693 | 21,025 | 21,401 |
| Private CLEAR macros | 16 | 16 | 32 | 32 |
| Scalar real-primitive allowance | 198,766 | 198,814 | 211,210 | 214,986 |

The receipt names each of the sixteen candidate removed centre events
by orientation, source index, rank and canonical event digest, and each
introduced line by its flattened QQ16 index, rank and digest. These are
candidate substitutions, not accepted deletions. Owner-map counts come
from literal `cover_map` events; native-wrapper counts come from the left
and right recipes of each literal `native_line` event.

The QQ16 pair removes sixteen rank-eight centre children and introduces
thirty-two rank-one children. Its native call count increases by 16 while
its rank sum decreases by 96. It also adds 3,040 scalar macros, including
32 CLEARs, and 28,616 scalar real primitives. The QQ wrappers contain 528
explicit owner maps and 64 native line wrapper maps. The invariant rank
32 of the data-map discrepancy is not one of these native resource counts.

The retained #4015 decoder word independently counts as 224 rank-one
native lines, 448 native wrapper maps, 352 owner maps, 2,816 ADDs, 416
CLEARs, and scalar allowance 26,944. It uses the 224 owned output fields;
its zero additional query-field count does not mean zero output storage
or zero private workspace. Its predecessor's private bound, physical
allocation and rounding obligations are not re-proved here.

Even the raw component subtotal QQ16 plus this decoder, less the selected
pair, has **240 additional native calls, native rank sum +128, and scalar
allowance +55,560**. This is not yet a replacement budget: the decoder
recovers the original pair inputs, whereas the selected caller requires
its selected pair outputs at the next bridge. A connection from those
recovered inputs to that endpoint, with native frames, owner paths and
stock, remains to be supplied. Restoring an input does not erase the
selected pair's output computation from the ledger. If those 224 outputs
must later be returned zero, a separate terminal contract would add their
cleanup after legitimate use; this audit does not assume that contract.

Only after endpoint compatibility and comparable child tariffs are proved
could these counts enter a screen such as

```
16 C8 > 256 C1 + 55,560 S + conversion + repair + cleanup + movement + precision.
```

Here C8 and C1 would need common-unit tariffs for the removed rank-eight
and introduced rank-one children, and S is the tariff for a scalar real
primitive. Native wrappers must be included exactly once in those tariffs
or charged separately; cover maps need their own tariff. This is a
conditional bookkeeping expression, not a proved inequality, a global
lower bound, or a claim that one decoder per pair is the actual caller
incidence. Without those contracts the exact count ledger is the result.

## The selected-only endpoint repair does not survive owner dependence

The constant-owner, constant-payload test makes the QQ16-versus-selected
pair difference appear supported only on A union T. That observation
suggests a repair touching those sixteen ports. The independent replay
here tests this exact restricted proposal using a larger legal input
space: payload is constant, but values depend on the full cover owner.
It evaluates the literal F0 word and every B1_2 prefix event, preserving
each actual `out(d)=in(d*g)` owner map from the packet.

For input X at port 0 equal to one on owner I and zero on other owners,
with all other inputs zero, the QQ16 source Y at ordinary port 1 has value
**-1/2 at owner I**. The selected pair's corresponding Y is zero.
Consequently, the next bridge produces +1/2 in pair-1 Y at that ordinary
port under QQ16, versus zero under the selected pair. A postpair repair confined
to the sixteen selected output ports, preserving ordinary fields and the
pair-1 target inputs of this bridge, cannot change this observation.
The witness is admissible under the declared independent-cover module
interface. Its reachability from a particular outer integer-multiplication
input has not been proved. The failure concerns all-permitted-state
postpair selected-only repairs; it is not a universal impossibility on
an arbitrary restricted reachable-input subspace.
All 96 ordinary Y rows have a nonzero owner-dependent residual for the
symbolic input X at port 0. If every owner map is intentionally collapsed
to the identity, all 96 residuals vanish. This control identifies the
precise premise lost by the constant-owner test.

The source-Y comparison does not assume a full nonconstant formula for
the selected pair. The independent sparse scalar replay checks all 712
local input columns of both backward cores: each Y endpoint is the same
Y input, with no other-input dependence, on the constant-payload character.
The selected forward word at stage 0 is the same-port unit shear.
At a provider invocation indexed by local owner d, port p enters and exits
at physical owner d*rho_p; conjugating a same-port identity by that route
leaves it an identity. Constant payload also makes every payload phase
and translation trivial. Thus the source-Y endpoint survives the actual
owner lift on this restricted test space. No analogous all-character or
full X-endpoint statement is inferred from it.

The implemented test uses full 73-column matrices, checks that its witness
owners are orthogonal, and retains the exact rational coefficient and
row digest. It does not import the primary pair verifier. The package's
main verifier authenticates the common pinned inputs before calling this
audit.

## Budget status

The selected and QQ16 local invoices are exact literal counts. The failed
selected-only repair and unchanged full bridge are also explicit. A
successful general correction, its native realizations, physical ownership
and release, recursive precision, head movement, bit cost, and actual
source-caller incidence are not established. A proposed invocation fraction
is not a funded budget. No global multiplication constant changes here.
