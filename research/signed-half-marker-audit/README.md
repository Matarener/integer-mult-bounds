# Independent literal-marker audit of PR6092

PR6092's stated local tariff is realizable: a width-independent finite
transition table executes the retained unary word in either direction in
exactly **2L+2 local two-tape steps**, returning both heads and both Boolean
accumulators, with unchanged program and resident coin. This corroborates
zxv's construction at `39df190f3a8a04cccb88ef1a6ca9aad39ed0364d`; it is not a
new half kernel or an admission of the whole caller.

[AUDIT.md](AUDIT.md) gives the marker chronology, macro invariant, signed
range proof and limitation matrix. The independent machine consults only a
literal scanned program symbol, scanned data bit and fixed finite control.
It does not use `len(word)` as a successful termination condition or infer a
free return from an address. A host watchdog can reject a nonreturning mutant;
only the left-marker transition can report completion.

The new reusable artifact is the explicit finite transition table plus
independent rejection controls. The source already had an indexed tape
simulator, gate/integer comparisons and a written signed proof; those are
credited predecessor evidence, not rediscovered novelty.

## Replay

```sh
python3.12 -B scripts/research_package.py --package research/signed-half-marker-audit
python3 -B scripts/check_research_commit.py --package research/signed-half-marker-audit --check-source-history
```

The direct `python3 -B research/signed-half-marker-audit/verify.py` command also
works in the official package export without Git or network. The replay uses
only Python's standard library, authenticates the four retained source files
with SHA256 and Git blob hashes, and compiles the authenticated kernel bytes
without importing bytecode. It exhausts 496 signed half round trips at W=2..6,
checks 32 extrema round trips at W=8,16,32,64, and independently tests 640 gate
macro placements/payloads. Every half is compared to an integer formula and
source gate endpoint. Five mutants must fail. Normal and optimized commands
use explicit checks, not removable assertions.

The generated program is used verbatim from the source compiler. Program
hashes are checked against its frozen RESULT wherever that width is present.
Only the small subset needed for this audit is retained under `predecessor/`;
PREDECESSOR.json records the pending repository/head, exact paths and blobs.
No dependency on the pending PR's Git ancestry or network survives export.

## Open next questions

Bind one actual reached PR6066 half site to paid coin delivery, clean workspace
and a caller guard; first derive those three obligations at event52 or event89.
They are absent from this local macro contract and block whole-caller use.
Separately, independently verify the charged program preparation algorithm:
this audit checks its emitted words and local per-call invoice, not a literal
finite-tape compiler or a sharp setup bound. See TASK.json for structured scope.

## Credit and limits

Prepared by JoyboyBrian with substantial OpenAI Codex assistance. The signed
kernel, arithmetic proof and original tape invoice are zxv's PR6092; PR6066
supplies its stochastic ABI. Retain Nick Petalas/PR6026, Ali Romman/PR5599 and
the source's complete predecessor lineage. Reversible Boolean gates and ripple
carry identities are classical. Apache-2.0; the retained files are unchanged.

No new kappa, global microstate reversibility theorem, sampler, native MOVE,
whole-prefix physical execution, clean-work allocator, human or proof-kernel
acceptance is claimed. The all-width result is a written argument; finite
checks corroborate its implementation and cannot replace that quantifier.
