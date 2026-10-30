# Native cache/context helper: preconstruction review

**Recommendation: proceed to a bounded native-helper feasibility gate, with Fraction arithmetic and the Python trace unchanged.** Prefer a vectorcall Event and authenticated member-descriptor reads over repeated `PyObject_GetAttrString`. The target is Python key/context/cache bookkeeping, not a second rational engine. This review approves neither an unseen implementation nor a performance claim. No compiler, arithmetic experiment, native module or replay was run by this reviewer. Only local headers and primary CPython documentation/source were inspected.

The user explicitly requested C. Parent owns implementation and the only scientific runner. Keep kappa work, other feeds and publication paused. The supported environment is the actual CPython 3.12 ABI and compiler used for the cold build; do not describe a full-C-API extension as `abi3` merely because some individual calls belong to the Stable ABI.

## Recommended API boundary

- Cache is fresh for each trace and owns the exact Python miss callback, immutable snapshots of the weight/token metadata, authenticated Fraction descriptors/type, dictionary and fixed-capacity FIFO ring. Snapshotting means copying the metadata structure into owned tuples, not merely retaining the original mutable list. Standard Fraction objects remain under the predecessor's stable/immutable-value premise.
- Event owns a strong Cache reference and captures q plus its two canonical key components. Its three positional inputs are old, v and source-site i. Cache should not retain every Event; avoid a reverse Event ownership cycle or an event-history list. Direct score addition stays disabled for the first native nomination.
- Enable vectorcall on the Event type, store its function pointer at the declared offset, extract positional count with `PyVectorcall_NARGS`, reject unsupported keywords/arity, and give `tp_call` identical behavior through `PyVectorcall_Call`. Do not misuse the arguments-offset flag. Call the Python miss callback with `PyObject_Vectorcall` and five arguments. Keep the GIL throughout. [Python 3.12 call protocol](https://docs.python.org/3.12/c-api/call.html).
- A certified exact member descriptor may be read through `Py_TYPE(descriptor)->tp_descr_get(descriptor, operand, (PyObject *)fraction_type)`. Retain descriptor ownership and check a non-null function pointer. This uses the descriptor protocol rather than a Fraction-layout cast. Preserve the preceding property/slot/getattribute binding and per-trace freshness checks, because bypassing a changed public getter would change semantics. The documented slot has the three-object descriptor-get signature. [Type slot reference](https://docs.python.org/3.12/c-api/typeobj.html#c.PyTypeObject.tp_descr_get).

The CPython 3.12 member-descriptor implementation performs its owner/type check and delegates to `PyMember_GetOne`; its object-valued member path returns a strong reference. Accordingly, each successful integer slot read must either transfer its reference into the new key tuple or be decremented on every exit path. These source links explain the API behavior; they are reference material, not substitutes for the installed-runtime/ABI binding. [Descriptor implementation](https://github.com/python/cpython/blob/3.12/Objects/descrobject.c), [member implementation](https://github.com/python/cpython/blob/3.12/Python/structmember.c).

## Ownership rules that must be explicit in the C review

| Item | Required ownership |
| --- | --- |
| Cache metadata, callback, descriptor and type fields | Owned references, released on clear/deallocation |
| Event Cache/q/q-numerator/q-denominator | Owned references; an Event remains safe if the caller drops its Cache variable |
| Fresh seven-element key | One local owned reference until insertion/return cleanup |
| Each FIFO ring entry | Its own owned key reference, independently of dictionary ownership |
| Dictionary hit | Borrowed from `PyDict_GetItemWithError`; return a new reference |
| Successful Python miss result | New reference; dictionary insertion retains its own reference, and the caller receives an owned reference |

Use `PyDict_GetItemWithError`, distinguishing a missing key from a pending exception. Ordinary `PyDict_GetItem` can suppress hash/equality errors. `PyDict_SetItem` does not steal its value reference. Check every dictionary API return value. [Dictionary API](https://docs.python.org/3.12/c-api/dict.html).

Fill only newly allocated tuples with `PyTuple_SET_ITEM`, whose reference transfer must be accounted for. Never use unchecked tuple item/size macros before establishing exact container shape and index bounds. Any borrowed metadata object remains valid only while its owning container is retained. [Tuple API](https://docs.python.org/3.12/c-api/tuple.html).

Decrementing a reference can run Python finalization. Restore internal invariants before releasing old objects, clear pointers before decref, and make partial-construction cleanup safe. Do not infer ownership from apparent reference counts or immortal integers. [Reference-counting API](https://docs.python.org/3.12/c-api/refcounting.html).

## FIFO and exception contract

Preserve the exact seven-component key order and Python integer objects. Do not narrow numerators/denominators to C integers, use raw hashes as identities, or change collision resolution. Hits return the existing result and do not move the FIFO position. A miss first invokes the unchanged Python computation; a computation failure must not evict or cache anything. Successful full-cache misses evict the oldest entry before inserting the new one, matching the parent order.

Maintain explicit `head`, resident `count` and fixed ring capacity. On successful eviction, remove the corresponding dictionary key and ring reference together and update the head/count consistently. If the later insertion fails, leave a consistent smaller cache and propagate the exception; do not leave a ring entry for a dictionary insertion that never succeeded. Do not temporarily exceed the capacity to simplify rollback. Counters should follow the parent's successful and exceptional transitions, and C counters must not invoke signed-overflow undefined behavior.

Calling Python on a miss creates a reentrancy boundary. The known compute function is pure in the supported runtime, but native objects should not become memory-unsafe if an injected callback reenters them. Prefer a small busy/closed guard and reject reentrant mutation; alternatively document and enforce a callback restriction sufficient to prove non-reentrancy. Preserve the original callback exception and return `NULL`; do not convert it to a miss, cache a failure, retry, or continue with a pending error. Cover recursive callback handling and reset the guard on every failure path.

The optimization domain must establish valid internal i/metadata bounds before unchecked access. Inherited malformed-word/missing-weight cases must select original behavior or preserve its exception type/message/order. A stronger pure entry condition such as sufficient metadata length may safely select original fallback; it must not reject an input the original accepts. Separately, direct calls to the exposed C API with invalid types, huge/negative indices or malformed descriptors must raise Python exceptions, never read invalid memory.

## Native object lifecycle

Cache and Event contain references to Python containers/callables. Support cyclic GC with complete traversal of owned references and an appropriate clear/deallocation path, unless a strictly enforced acyclic graph is actually proved. Callback closures can otherwise create cycles even if Cache does not own Events. Initialize all owned pointers before tracking; untrack before clearing/deallocation, and pair the allocation/free APIs correctly. [Cyclic-GC requirements](https://docs.python.org/3.12/c-api/gcsupport.html).

Prefer non-subclassable types with no writable native fields. Prevent public creation or reinitialization of uninitialized Event/Cache instances, or require an initialized-state check on every entry. A cleared or partially constructed instance must not dereference null fields. Heap-type deallocation must also handle its type reference correctly. Keep mutable cache data out of module globals; only authenticated loaded code/types may be reused in a process. Do not claim subinterpreter or free-threaded support without a separate design.

## Smallest meaningful coverage gate

Retain all prior finite comparisons and controls, including the compact-key/slot binding gates actually used by this candidate. Add focused native checks for:

1. Capacities 0/1/2/full, FIFO wraparound, equal-value keys, deliberate integer-hash collision, unchanged token identity and fresh traces/Events.
2. Identical outputs/counters and Python callback invocation count: exactly one call per successful miss, none on a hit, and no cached exception.
3. Invalid arity/keywords/type/index/descriptor and partial-construction rejection, Event surviving deletion of the caller's Cache reference, and bounded create/drop/GC lifetime behavior.
4. Callback failure/reentrancy, cleanup after failure, full-cache failure ordering, output/statistics isolation, and unsupported/stale binding selecting original execution.
5. One bounded finite subprocess with CPython's debug allocator/development checks, plus source review of every allocation/error/deallocation branch. This is memory-safety validation for new native ownership; it is not a replacement for scientific comparisons.

Only then perform the parent's fixed native/Python cache micro screen. A promising result permits one original/parent/native actual audit with unchanged complete output/type/witness digests and exact calls/hits/misses/evictions/tokens. No complete qualifier is justified by micro timings alone.

## Cold-build and acceptance accounting

Compile and load inside every fresh complete candidate process, in a fresh owned temporary directory, without installing anything system-wide. Record C source hash, compiler/version/flags, interpreter version/SOABI/extension suffix and build/load outcome. Preserve build failures and unsupported environments; do not silently claim native coverage through fallback. A loaded immutable module may be reused within that one complete process, but every trace still gets fresh mutable Cache/Event state.

The complete wall and CPU bill includes compilation, linking, loading, binding, all finite/native controls, metadata preparation and the scientific trace. `time.process_time()` alone excludes compiler/linker child CPU; use the existing process-group/resource accounting that includes children. Ensure a feasibility model does not either omit the build or double-count the same within-process build. A fresh complete B/C comparison remains the authority for the user's at-least-15% wall **and** CPU threshold. The C design creates a new plausible cost target, not an admitted saving.
