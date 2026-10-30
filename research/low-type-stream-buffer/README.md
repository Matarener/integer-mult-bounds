# Exact payload storage for one-pass child batching

This contribution was produced by Nick Petalas. Apache-2.0.

For n repeated input cycles, L low types and s symbols per type per cycle,
one forward input pass that emits complete child batches sequentially needs
exactly

    (n-1)(L-1)s

alphabet-symbol equivalents of retained payload information. The lower bound
permits arbitrary lossless encodings and charges payload-dependent controller
state. An explicit schedule attains it with literal symbol slots. Claim type:
scoped written proof with finite corroboration. See [PROOF.md](PROOF.md).

This answers one restricted version of the physical-dispatcher question in
[Ali Romman's PR #5829](https://github.com/CrocSwap/integer-mult-bounds/pull/5829),
at head f1e522fc26371617ed60dea3c4609d422d491d2e. Its whole-high batch address
contract is the cited predecessor, not an audited deliverable. At its depth j,
put n_j=T*(L*H)^(D-j-1) and s_j=H^(j+1)*R. The new storage term is
((L-1)/L)*(1-1/n_j)*V_j. The L=2,H=2,T=1,D=2,j=0,R=1 fixture
requires exactly six retained symbols for a sixteen-symbol parent.

This is an explicit linear-storage term for the stated interface. It does
not refute the predecessor's O(V_j) premise or prove that a physical caller
must use this interface. Multiple writable child streams, rereads, random
access and changed traversal orders are outside scope. Unbounded integer
or exact-complex cells do not have unit information capacity in this model.
Physical movement, numerical precision, native execution, cleanup and the
complete supplier bill remain open. No new kappa or frontier change is claimed.

## Reproduction

From the repository root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/low-type-stream-buffer/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/low-type-stream-buffer/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/low-type-stream-buffer
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/low-type-stream-buffer --check-source-history
```

Any CPython 3.12 path can replace the local interpreter path. Direct success
prints PASS_LOW_TYPE_STREAM_BUFFER. The verifier checks complete domains
declared in its functions, independent prefix and scheduling oracles, actual
payload outputs, cut-state injectivity and rejection controls. It can write
a generated receipt with --receipt /absolute/path/outside/package.json;
the receipt binds all six package files by SHA256. No generated evidence
is stored in this package. Independent human and formal proof-kernel review
are unclaimed.

The source manifest pins the task and selected record as historical provenance.
The PR #5829 contract is a cited mathematical premise, recorded separately
with its exact head, paths and hashes; it is not a runtime or Git-history
dependency. No pending predecessor code is imported or fetched during replay.

## Open next questions

- Can the final compiled template emit into multiple independently writable
  child streams while retaining complete arbitrary-input return and a smaller
  local buffer? Start with the sixteen-symbol fixture. Physical stream count,
  head placement, return order and a complete movement bill are the blockers.
- What time and storage bill does a literal fixed-tape implementation of the
  attaining one-pass schedule incur? Start by charging the six-slot fixture's
  retained-chunk reads and releases. A source-bound dispatcher and its cleanup
  contract are still required.

Credit Ali Romman for PR #5829's whole-high batch address contract and open
dispatcher question, Mason Hale for its recursive-allocation predecessor,
and the retained BIT/compiler/cover authors credited there. Streaming
permutation cuts and the elementary information-counting method are classical.
The new contribution is the sharp buffering result for this declared interface,
its delayed-cover substitution, attaining schedule and standalone corroboration.
