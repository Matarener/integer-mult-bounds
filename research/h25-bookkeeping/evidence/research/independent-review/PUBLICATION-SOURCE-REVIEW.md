# Independent publication envelope source review

**SOURCE_ADMIT_SERIAL_DELIVERY_CHECKS.** No remaining source blocker was found in the reviewed parent guard and five publication wrappers. This admits bounded delivery validation; it does not assert runtime success or create performance samples. Review used source reads, exact hashes and AST parsing only, without scientific imports, compilation, transport decoding or execution.

## Exact reviewed sources

| File | SHA256 |
| --- | --- |
| `publication_guard.py` | `c1722dabdfbd4c50b2e5a8bc8988dc3f1e02ec76b924361e432afce552abc33d` |
| `archive_support.py` | `eee90f3815f4bd90eb96152bc461ec968ffb91d47c990e77712e74f6677c51be` |
| `replay.py` | `50901fc7de6bbb39067e46d27f653a80b4f9f47c762a3a6c597727d8d6fc4883` |
| `verify.py` | `f0a5e3ab9c9521f02ef33bba0508bc75cc5b49c1e117f203ff02af614444ee11` |
| `verify_full.py` | `2fa8b3c0bd28c6162fb08190241b1d3195e48616986cf3309e293402fc5c0c2e` |
| `check_artifacts.py` | `03d89a1df701305d37289de9a6bda4ac485da83ca43459d41de2bd4f78a50445` |

The five wrapper hashes match `publication/wrapper-source/SOURCE-READINESS.json`. The scientific stage remains `558eebbc1dc65e42bbcb3ffd9973f8bc86641a3539493ecc1d53d8077c39cdbc`; its unchanged runner remains `b74366a925dd44c0e95a7ad87aa1505cbdcad9fefcb9360d77d6459679f102be`.

## Parent guard and resolved findings

The guard uses the existing nonblocking campaign lock and sums all retained outer receipts, including failures. It permits only registered finite, optimized finite, full, canonical and registry jobs. Package bytes/modes are inventoried before and after, each attempt receives a fresh evidence directory, and delivery receipts explicitly set `performance_sample=false`.

Two source findings were repaired before any reported delivery execution. First, unconditional root-PID re-admission could bypass generation tracking during cleanup. The final code captures the unreaped child immediately after creation, before any poll/wait can release its PID, then retains and compares start-time identities. Second, a final output burst could bypass live output-cap polling and trigger unbounded reads. Final file sizes now enforce STOP for oversize output; retained stdout/stderr and package files are hashed in bounded one-MiB blocks.

Process traversal includes observed descendants in nested sessions. Cap handling signals their groups, rejects signalling the parent's own group, and performs final kill/wait cleanup. The outer threshold is 180 seconds or the remaining campaign allowance, followed by up to two seconds of graceful termination; the inner scientific timeout is 150 seconds. RSS enforcement is sampled at one GiB, with the usual limits of polling rather than kernel memory containment. This is a guard for the fixed awaited command tree, not a general daemon-containment proof.

## Wrapper contracts

Authentication checks the fixed stage identity, exact 160 declared payload files plus STAGE.json, every protected manifest entry, and the Python/C code census. Publication files may all arrive as Git `100644`. Only the new external copy receives declared file modes, readonly stage metadata and readonly directories. Package modes are neither assumed readonly nor modified.

The copied runner is source-loaded after its exact hash check; only `HERE` and `TIMEOUT=150` are overridden. The runner still authenticates its own source and copied stage. Normal and optimized verifiers select the appropriate complete old/new finite union; full/replay jobs require assertions. B selects the original native baseline and C the combined adapter. Full outputs must match the historical anchor. The external one-job inner ledger supplements the existing parent campaign ledger and does not reset its accounting.

Wrapper/support/checker modules are compiled from authenticated source bytes with distinct module names. The canonical wrapper invokes the unchanged inherited checker and its own distinct support, avoiding an import alias collision. No new transport or scientific implementation is generated.

Evidence paths and temporary bases must be external to the package/repository before writes. Successful temporary verification workspaces are removed only after checks, with a matching ownership marker; only nonsymlink private directories become writable for removal. Explicit replay preserves successful evidence. Exceptions retain workspaces and attach their location.

## Required execution evidence

Parent must freeze a complete CODE-SOURCES manifest, then validate normal finite, optimized finite, full assertion-on correctness and canonical transport under the guard. Confirm readonly Git-free execution and a Git-export-style 100644 package, external writes, successful cleanup, failure retention, unchanged sources and campaign receipts. Hosted results must name the actual `/usr/bin/python3.12` child and its Fraction digest; the outer interpreter version alone is insufficient. These delivery checks do not replace the six already-qualified local samples or establish hosted performance, a selected-frontier change or a new kappa result.
