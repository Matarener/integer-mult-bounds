# Implementation source gates

This file preserves the first incremental source decisions. Current exact hashes, the approved P1 control repair, later pilot admissions and combined-stage obligations are in `IMPLEMENTATION-REVIEW.md` and `IMPLEMENTATION-REVIEW.json`.

Source review only. The parent alone may compile or run under the serial queue. Passing this gate means the source is suitable for the next finite qualification; it does not mean it compiled, passed controls, improved performance or satisfied integration.

## P2 — ADMIT SERIAL FINITE EXECUTION

Reviewed `guard_candidate.py` SHA256 `320435ec4125544f2b2aedf74f21469b232d08683fe76f0913607516254bbd29` and `guard_controls.py` SHA256 `514e3d08793323cf216c7a1f76cafdc8dbba4ab4656e64167c788985f9e63291`.

The guard preserves original constructor state, original slot checks, predicate and short-circuit ordering, exception messages, empty-cell/attribute exception propagation, and constructor `self.check()`. The only record change is first-occurrence identity deduplication. The factory captures original backend primitives and does not alter its input backend by itself.

The controls are behavioral perturbations, not a duplicate implementation oracle. They retain an independent untouched backend, create four source bindings, and restore/reuse them. Stable calls prevent an always-rejecting guard from passing. Mutations cover each distinct function's code/defaults/keyword defaults, captured cell rebinding/deletion, global and builtin slots, class/native dispatch, and first-failure precedence. Held-guard, native-eligible, wide fallback and callback-container entry paths compare exact outcome type/message, prefix, counters and callback logs. Same-code distinct functions are separately checked. The suite uses explicit requirements under normal and optimized interpreters.

The proposed 237 mutation pairs × 7 actions plus 14 stable action pairs are finite and reuse four source loads rather than generating a new expensive source binding per mutation. Shared builtins and native entries are restored in finally; the parent must serialize execution. No source blocker found. The full pilot requires successful parent finite results first. Added P3 owner/entry checks remain a separate integration gate.

## P3 — C/ADAPTER SOURCE ACCEPTED, CONTROLS PENDING

Reviewed `trace_encoder.c` SHA256 `57d6f0f71d5bfd2145397ac0159837d32990b276fead2ec1b1d6854d8913bd7e` and `trace_adapter.py` SHA256 `4bdb401271ffd049c52eff0edc28d8d604a11faf66fec419555a82cbd3b32d60`.

The C method matches the documented positional [METH_FASTCALL signature](https://docs.python.org/3.12/c-api/structures.html#c.METH_FASTCALL). Exact container/int admission precedes unchecked item macros; no callback-capable coercion or GIL release appears. Unsigned conversion checks the error indicator and clears only overflow for fallback, matching the [integer API](https://docs.python.org/3.12/c-api/long.html#c.PyLong_AsUnsignedLongLong). Every append checks capacity; partial buffers never escape. The only successful result allocation copies the stack buffer into a new bytes object according to the [bytes API](https://docs.python.org/3.12/c-api/bytes.html#c.PyBytes_FromStringAndSize). No owned temporary references require cleanup and no borrowed argument references are retained.

Canonical key order/punctuation/newline are correct by inspection. Adapter input unpacking, output validation, one count read, literal JSON fallback and hash/byte/count order agree with the original supported contract. The adapter exposes encoder owner/entry metadata but does not itself enforce the parent's pre-arithmetic freshness check. Controls and integrated freshness source remain pending; no full P3 execution gate yet.

## Integration decisions reviewed

An explicit fork of the original driver is appropriate if it records its own digest, the pinned original driver digest and exact transformation/inverse evidence while comparing unchanged scientific observations. Never claim the original driver bytes executed.

Keep `backend.ComplementTrace` original. The old finite suite uses a single imported observer class for both oracle and candidate traces; replacing it before import would compare two candidate encoders. Parent agreed to construct the candidate full trace explicitly and run new P3 controls against the original observer. Existing comparison imports can remain in their original location.

P1 implementation and the integrated driver remain pending source review.
