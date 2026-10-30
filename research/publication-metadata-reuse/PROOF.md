# Acceptance equivalence and implementation limits

Assume the same stable working tree, publication commit and ordinary successful
Git object reads as the original check. Both implementations inventory the same
regular committed files, compare every working byte, and complete the blob
iterator's final Git-status check before returning success.

The original check then calls `publication_sources()`, which reads the size and
bytes of `commit:package/SOURCES.json` through two additional Git processes.
The candidate retains that same immutable blob from the existing inventory
comparison. It retains its bytes only when their size is at most the existing
16 MiB metadata limit. For an oversized blob it retains only its size, then
rejects after the complete comparison iterator finishes. A missing metadata file
still rejects only when history checking was requested.

Both paths check the missing/size conditions, parse the same JSON bytes and call
exactly the same metadata/history validator. Therefore successful runs have
identical complete result dictionaries and the same declared pin acceptance.
The standalone `source_history()` still authenticates its own metadata through
`publication_sources()`. The new internal helper is called only with JSON from
these committed-byte boundaries.

Malformed JSON is parsed after the complete byte comparison, as before. Working
metadata drift and a final blob-reader failure still precede parsing. All
metadata shape, row/count limits, exact commit IDs, raw ancestry, shallow history,
replacement/graft isolation, retained Git errors and timeout checks are unchanged.
The candidate no longer performs the two duplicate Git reads, so failures injected
only into those removed operations have no counterpart. This is an acceptance
argument on successful immutable reads, not an identical subprocess trace claim.
Concurrent checkout mutation remains outside the original stable-checkout contract.

Eight new tests use actual committed fixture bytes. They cover no metadata refetch,
the standalone reader, drift before parsing, malformed committed JSON, final-reader
failure before parsing, committed versus later working bytes, exact size bounds,
absence of cross-call caching and explicit older publications. Existing history,
byte, execute-mode and replacement tests remain in the registered suite. Finite
controls corroborate the argument; they are not a proof-kernel formalization.

## Code constraints

The additional retained payload is at most 16 MiB, local to one call, with no new
loop or subprocess. The original blob reader still allocates each complete blob;
its existing allocation is outside this change. Python runtime allocation is a
managed-runtime deviation from fixed allocation. Existing input bounds, finite
file inventories and Git timeouts apply. The now 58-line check function is kept
as one inventory/comparison transaction; splitting it would introduce a second
owner for the captured metadata. No recursive call is added. Explicit `require`
checks remain active under optimized Python.

The optional benchmark loads one fixed, pinned historical Python module through
importlib. This bounded baseline-loading exception adds no dynamic dispatch to
the production preflight. It times complete `check()` calls and requires full
result equality for every sample. Profile measurements are not included among
the reported timing samples. Timing numbers do not predict a mathematical replay
or physical multiplier speedup.

No selected cold replay, Lean, Docker, physical multiplier or supplier admission
was run. Independent human and formal proof-kernel review are unclaimed.
