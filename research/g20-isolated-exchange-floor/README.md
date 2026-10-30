# G20 isolated exchanges: an exact six-ADD floor

**Scoped negative result; no new kappa.** General invertible binary bases
within two-wire banks do not reduce an isolated bank exchange below six ADDs.
The complete 36-map shortest-distance histogram is `{6:2, 7:8, 8:24, 9:2}`.
All maps have explicit shortest words. A separately implemented checker
validates the complete GL(4,2) distance-label certificate.

This answers a restricted part of the released PR5840 general-GL2 question.
Its actual 38-ADD boundary has fourteen chain ADDs and four isolated bank
exchanges. Keeping that factorization and counting every ADD, the two-sided
76-ADD boundary is optimal. This is **not** a minimum for arbitrary 32-wire
circuits or general bases before the entire boundary.

## Reproduce

Python 3.12 and its standard library suffice; no solver, Git or network is
needed by the direct verifier. From the repository root:

```sh
python3 -B scripts/research_package.py --package research/g20-isolated-exchange-floor
```

Expected: both normal and optimized commands print
`PASS_G20_ISOLATED_EXCHANGE_FLOOR`, with 20160 states, 241920 directed
edges, 36 endpoint maps, minimum 6, floor 76 and five rejected controls.
Direct standalone replay:

```sh
python3 -I -B research/g20-isolated-exchange-floor/verify.py
```

To regenerate without touching committed evidence, choose a nonexistent
scratch directory:

```sh
python3 -B research/g20-isolated-exchange-floor/generate.py --output work/exchange-regenerated
cmp research/g20-isolated-exchange-floor/distances.bin work/exchange-regenerated/distances.bin
cmp research/g20-isolated-exchange-floor/CERTIFICATE.json work/exchange-regenerated/CERTIFICATE.json
```

The exact proof, complete model and limitations are in [PROOF.md](PROOF.md).
`distances.bin` classifies all 65536 binary matrices; `CERTIFICATE.json`
contains all 36 attaining words. Verification uses independent column spans,
right-multiplication graph edges and literal truth tables, while generation
uses row-addition BFS. No predecessor verifier or search code is imported.

## Sources and research record

Base: `de5ec2e7a6074068452f45b1a191b5c72832df4a`, priority revision 8.
Seed **16** was drawn once using OS randomness (`secrets.randbelow(100)`),
assigning the BIT supplier track. [TASK.json](TASK.json) records the three
candidates, changed scope, completed coverage, stop rule and overlap limits.
The run is exhaustive and deterministic; the seed selected the research
scope and is not an enumeration parameter.

Source: [PR5840](https://github.com/CrocSwap/integer-mult-bounds/pull/5840),
head `6a043d0fc0199ee5b24c61f883f1943eaf6424be`. Only its controller is
vendored, unchanged, with Git blob and SHA256 in [SOURCES.json](SOURCES.json).
The source was retrieved using GitHub's contents API at that exact commit;
the verifier checks its frozen SHA256. The pending PR commit is not required
in the offline Git store. Registered provenance pins bind the task catalogue
and selected record at the base; source retrieval and mathematical validation
are separate evidence. [CLAIM.md](CLAIM.md) retains the advance local claim:
Discussion posting was denied once by the integration. No reservation issue
was opened.

The central ledger records #5679/#5708 as partially reviewed. Their archived
ordinary BIT proposals and newer PR titles do not replace the selected
conditional kappa .00310045. This work changes no frontier or supplier budget.
Native, owned-erasure, compiler, precision/tape and analytic assumptions remain.
Full physical caller/native replay, Lean, Docker and repository-wide historical
tests are outside this scalar certificate's scope. See [VALIDATION.json](VALIDATION.json)
for the actual commands and execution evidence; no full theorem or human
scientific acceptance is asserted.

## Open next questions

Can a joint word share a chain ADD with an exchange, or use cross-component
gates to beat 76? The first useful step is one strictly shorter exact boundary
pair, checked against the original target diagonal; then rebuild all native
source descriptors and the complete caller invoice. The present proof freezes
precisely those interactions, so it cannot decide that question. Details and
blockers are in TASK.json. Do not repeat this complete isolated four-wire
enumeration with a new seed.

## Credit and license

Ali Romman supplied PR5840 and the released question. Preserve PR5834,
PR5807/5828, PR5708/5671, ai-nanachi PR5512, Dugongue, ToikY and the retained
native/controller/compiler/BIT lineage; [NOTICE](NOTICE) retains the source
notice. New complete finite certificate and independent checker: Charan .,
with substantial OpenAI Codex assistance. No subagents. Standard BFS and swap
identities are not new. Apache-2.0, following the repository license.
