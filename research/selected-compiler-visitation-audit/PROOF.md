# Successful-path visitation and retained-object count

## 1. Domain and inherited premises

Use the authenticated public `selected-bit-physical-caller` sources recorded in
SOURCES.json. Set `cat = Catalogue(q)`, `topology = SelectedTopology(cat)` and
`binding = SelectedBinding(Specifications(cat))` with fresh specifications.
Consider one complete successful `compile_node(topology, binding, mode=0)`.
No source functions are patched, and no foreign callback mutates the topology
or source records during emission. The pinned LOW enumeration and rank/code
bijection are assumed to hold for an admissible prime `q >= 3` (not an
arbitrary prime power).
Set `N = product_{k=0}^{63}(q^64 - q^k) = |GL64(F_q)|`.

The result is conditional on completion: it does not establish all-size route,
plan or allocation success, or practical feasibility of materializing the word.
`N` is symbolic. The executed selected census constructs q=7 metadata only; it
never enumerates its LOW vocabulary or invokes its compiler/factory/route path.
The small full emitter tests use the separate original GL2(F3) fixture.

## 2. Project the public source, not a guessed schedule

In `macro_code.py`, the local-cover branch loops over replicas, then LOWs, then
local events. `LocalState.accept` sends only op0/MOVE and op2/COPY to the residual
helper, with `common=True`; XOR and ERASE emit no residual. The idle branch loops
over replicas, then request IDs, then LOWs with `common=False`. Bridge/exchange
branches make no residual-factory calls.

The census executes the original `SelectedTopology.call`, `idle_family` and
`LocalState.accept/finish` on every replica's metadata. For each chronological
group it checks the request kind, stage, local position or idle group, the
common/native view, uniqueness, and equality of the ordered request-ID lists
across all replicas. The groups disjointly exhaust `range(len(requests))`.
Their actual chronological sizes, including the empty final idle, are

```
2920, 2920, 222, 2920, 222, 2920, 222, 2920, 222, 2920,
222, 2920, 222, 2920, 2920, 222, 222, 222, 0.
```

There are `rho=32` replicas and `R=28278` requests: 26199 MOVE, 81 COPY and
1998 IDLE. The metadata traversal covers 7,843,392 local events; this number is
not a native/numerical execution count. Source binding, not an independent
implementation of the selected mathematical construction, supplies the fixed
metadata. The q-independence is visible in `Catalogue.__init__/_bind`: the fixed
WORD/HOST/GEO data determine requests before `LowCodes(q,64,R)` is constructed.
The request-building methods and `SelectedTopology`/`LocalState` do not consult
q. This does not establish q-dependent template or route admissibility.

Let `G_j` be these disjoint ordered request groups. For every request and LOW
class, exactly one view is selected by the request kind. Thus the full word
visits exactly `M=RN` different `(request, view, LOW)` keys, not the full `2RN`
syntactic view range. Each key is visited once per replica of its group, hence
exactly rho times. The total factory calls are `T=rho RN=904896N`.
Neither local LOW-major order nor idle request-major order alters these totals;
it does alter the word. That is why matching totals alone is insufficient.

## 3. Keys, cached plans, instances and references are different

The default `SelectedBinding.residual` calls `Specifications.bind` and
`Specifications.plan`, then directly returns a newly constructed frozen
`Residual(spec.code, plan, identifier, common, low)`. There is no `Residual`
wrapper cache on that path. **There are source-record and plan caches**; this
argument neither removes nor overlooks them.

For each of its T calls, the compiler appends the returned instance to both a
`residual_begin` operation and a `residual_end` operation, and to every emitted
`block` operation for that residual. It never drops those operations before
returning `Code(tuple(operations), staged)`. All T different instances therefore
remain live together in that returned Code. Repeated visits to the same source
key create distinct wrapper objects. The binding constructor admits an ambient
specification through `bind`, not through `residual`, so it adds no wrapper to T.

There are exactly `2T+B` direct operation-tuple references to these wrappers
in `Code.operations`, where `B` is its number of `block` operations. This is not
the total number of Python references or the transitive size of plans, routes,
matrices, or arbitrary host objects. Nor is it a native storage lower bound. In particular, q is fixed in the
predecessor's asymptotic contract; this count does not contradict its q-dependent
fixed-overhead term or establish a uniform selected producer-stock coefficient.

The tests separately run the unmodified public factory method on a declared
Specifications receiver fixture: equal-key calls produce equal-valued but
nonidentical wrappers. This checks allocation behavior only, not the source's
numerical plan validity. The compiler trace's test-only binding likewise does
not replace a selected-endpoint proof.

## 4. The direct setup/runtime boundary

`Machine.__init__` receives already supplied programs. `Machine.run` fetches
`self.programs[self.mode].operations[self.pc]` and dispatches that operation.
All pinned Machine methods are checked for absence of direct compiler,
`binding.residual` and sync calls. Recursive dispatch changes state/program
position; it does not itself call the emitter.

This syntactic direct-call statement is deliberately limited. Runtime hooks
include `check_stock`, `validate_residual`, `incoming`, `coefficient` and
`child_program`; callbacks operate over specifications. Foreign observers or a
surrounding application can do other work. No transitive zero-cost theorem or
recompilation frequency is claimed. A wrapper-sharing optimization is also not
proved: `Machine.geometry` uses `owner is definition`, so any change must preserve
its actual lifetime/observation contract rather than merely numerical equality.

## 5. Verification versus proof

The grouped-word count is the elementary argument above. Bounded arithmetic
histories, an independent counted-word oracle, input corruptions, AST mutations
and two genuine tiny compiler traces, including their exact block/reference
identities inside each residual interval, catch specified implementation mistakes;
they do not promote the inherited bijection/admissibility premises to theorems.
All source hashes and replay inputs are explicit, and normal/-O runs must return
the identical complete scientific receipt. No assertions carry acceptance.
The [Lean supplement](lean/README.md) checks the explicitly defined counting
and allocation model and the selected interval partition. Its connection to
Python execution remains a source/extraction argument, not a kernel-checked
refinement. No full selected instruction word, native execution, new supplier
admission or improved exponent is claimed.
