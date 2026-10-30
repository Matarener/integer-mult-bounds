# Two-role construction, strict gain and scope

## The literal change

In PR3308's authenticated owner map, row 1514 is width 4, helper 74,
call `(stage=0, replica=9, time=3)`, hosted in bin `(9,6,50)`.
Row 1863 is width 5, helper 423, the same call, hosted in bin `(0,2,33)`.
The first bin has capacity 32 and free rank 1. The second has capacity 16
and free rank 2. Exchange their entire physical placements and compact each
bin's occupied prefix in stable old-offset order. `exchange()` preserves
stage, replica, time, helper and width for every row. Six rows differ, only
two of them in their hosting placement.

The resulting free ranks are 0 and 3. Actual source-event windows, active-pair
exclusion, one-helper-per-family-per-call, disjoint slices and prefix occupancy
are checked on all 69,120 roles by the retained source auditor and independently
by unchanged strict T16 admission. The actual chart count is derived as 10,008.
There is no assumed zero-cost new gate, source read, restoration or adapter.
This invokes exactly the inherited whole-helper hosting contract.

## Strict moment improvement

Let `p` lie strictly between zero and one. For positive `x,y`, strict
concavity of `t^p`, with its continuous value zero at zero, gives
`(x+y)^p < x^p+y^p`. Apply this with `x=1,y=2`. The replaced recursive
contribution is therefore strictly smaller:

```text
(3/73)^p + (0/73)^p < (2/73)^p + (1/73)^p.
```

Every other recursive child and paid charge is unchanged. Both moments retain
the same normalizing role count. This proves a strict complete complex moment
decrease without using a floating-point surrogate. It does not by itself give
the final headline; the exact supplier endpoints and outer witness do that.

For completeness of the bounded census, orient a swap so its first role has
width `wa > wb` and put `d=wa-wb`. If the original free ranks are `fa,fb`,
the new pair is `fa+d,fb-d`; feasibility requires `fb>=d`. Equal pair sums
and strict concavity show strict improvement exactly when `fa+d>fb`.
A full first bin has `fa=0` and cannot meet both conditions. Empty bins have
no role to exchange. Thus only occupied partial bins need be enumerated.
The implementation checks all such width/free-rank pairs, then every row pair
of different physical capacities, and tests the actual chronological and family
constraints. Equal-width swaps cannot change the paid profile. The 19,372
candidate pairs include eight legal choices. This proves only that named
finite domain on PR3308's map, not optimality among arbitrary owner maps.

## Full paid ledger

The actual eleven-stage replay, not the two-bin argument, supplies construction
admission. It checks 144 complete invocations and 69,120 helpers, native provider
content bindings, owners, parent lift, emitted controller, physical/prefix
invoice, both exact moment engines, both seven-step bootstraps and all 47
strict outer inequalities on each tariff path. The controls remain
69 admission, 12 bit, 6 independent T16 and 15 controller mutations.
The separately authored owner auditor adds its 11 controls.

The complete selected invoice object must match, including unknown future keys,
after excluding only `template_sha256`, `owner_audit_sha256` and
`controller_audit_sha256`. Those three identifiers bind the newly emitted
artifacts. Prefix 397 is paid at 512. The row coefficient stays 16,469 below
20,161. Actual physical stock stays 14,826 = 14,336 data/owner families + 480
helpers + 8 private centres + 2 coefficient fields. The independent T16
receipt's 14,850 is its conservative 504-helper allowance, not a conflicting
actual stock count. Copy, cleanup, restoration, compiler and coefficient charges
are retained in the whole-object comparison, never inferred from this short list.

The exact native complex endpoint is
`419106309171938950571/250000000000000000000000`.
The unchanged bit endpoint is
`1733427039589844234749/1000000000000000000000000`.
The complex side binds. The retained outer construction gives
`κ=836809769328269/500000000000000000`, strictly exceeding both selected
PR1094 and PR3308. The conservative complex surcharge control also improves.
`RESULT.json` records their exact differences and cap comparisons.

## Exact transport of generated receipt hashes

The hosted arithmetic report exposed two changed raw references: the full invoice
SHA256 and the dependent assembly SHA256. Every arithmetic report value and the
other five input hashes matched. Arithmetic success alone did not admit those
changed references. The original failing reports and immutable v3 evidence stay
unchanged. Actual hosted witnesses from run `39075529422` then proved that the
entire typed invoice object is identical. The literal byte difference is only
the ordering of ten `providers.gauge44.artifacts` mapping entries. The dependent
assembly differs only at its raw invoice reference. No gzip or decimal
portability assumption is used.

`transport.attest()` permits a serialization difference only after the ENTIRE
actual invoice equals the frozen invoice as typed canonical JSON, with no omitted
keys or values and with array order retained. Actual owner and controller bytes
must remain exactly fixed and match their declared live hashes. The ENTIRE actual
assembly must then equal the frozen assembly after replacing only
`input_sha256.fresh_invoice` by the independently recomputed actual invoice SHA256.
Every cost, cap, inequality, control, scope string and other input hash remains.

Only after these whole-input checks may the expected score rebind its two named
raw references. The construction report can rebind only its assembly/invoice
artifact references. The fresh immutable invoice reviewer runs on the actual
fresh score and copied scorer source. Its expected report rebinds only its two
top-level raw references and the three corresponding score-binding references.
The fresh reports still have to match those explicitly derived expected bytes.
No generic hash ignore or arbitrary hash replacement exists.

The registered run emits lossless bounded actual invoice, assembly, owner and
controller witnesses plus `TRANSPORT.json`. Unknown keys, changed charges or
inequalities, type changes, unrelated hashes, forged bindings and bad score or
review fields reject in normal and optimized tests. This is an integration
transport rule, not a new scientific supplier premise.

## Inherited obligations and engineering limits

The selected conditional scope remains intact. Source-bound reuse of selected
native artifacts is not a fresh full cold rebuild. All-size/compiler,
common-label/mutable-source realization, whole-call hosting, precision/tape,
exact recovery, analytic transfer and bit H1-H5 assumptions remain inherited.
No selected-frontier update, unconditional theorem or Lean proof is asserted.

The new Python loops have fixed role, source, archive and pair-count bounds.
Pair exhaustion fails closed; it cannot become an incomplete census success.
Input and decompressed JSON sizes are bounded. The full unchanged admission
subprocess has a 300-second timeout. Checks use exceptions and survive Python
optimization, except the unchanged strict predecessor intentionally requires
assertions enabled. Tests run the new construction controls in both modes.

Power-of-Ten deviations are limited to Python's managed allocation, the fixed
source-authenticated module loader, and unittest's bounded test dispatch. Their
live inputs are bounded; the loaders have fixed canonical paths checked before
execution. The retained predecessor modules are byte-identical and retain their
existing internal allocation and loop structure. Rewriting those frozen proofs
would expand the task and invalidate their evidence. Follow-up changes to those
modules need separate replay and repinning; this package does not weaken them.
The immutable v3 scorer also retains one unused `sys` import, reported by Ruff
F401. Its source must stay byte-identical to the independently checked digest,
so this nonbehavioral warning is recorded rather than hidden or silently edited.
All new integration/construction code passes the repository Ruff checks. The
scorer's next independently versioned release can remove that import and rerun
its source-bound reports; no such optional source churn is part of this freeze.
