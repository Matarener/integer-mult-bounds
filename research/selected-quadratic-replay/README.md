# Complete selected P104 replay with exact quadratic states

The complete selected scientific replay is 2.73x faster on this host: median
269.00 to 98.37 seconds across three alternating fresh processes per engine.
Every run has identical complete scientific stdout. The original range is
264.33..305.90 s; the new range is 80.89..175.99 s. Host load varies. This is a
verification speedup, not a faster physical multiplier or a new kappa.

Both original literal interpreters independently match all 17,651 distinct
state inputs from a fresh complete replay. Each comparison covers 9,037,312
amplitude entries, including every zero and denominator. CROSS.json records
the exact input trace digest.

The selected P104 verifier compiles 3131 native maps and checks 2923 distinct
frame pairs. Its compiler performs 32777 dense zero-state evaluations, and the
independent native checks perform 6264 sparse evaluations. This package uses the
archived PR 5704 exact quadratic-state engine at those two interfaces. It returns
the original full vectors and maps, so the caller's state checks stay intact.

A bounded cache stores only exact immutable state signatures, keyed by the full
circuit, width and initial basis. Numeric aliases reject before lookup. Every
new input is validated and evaluated. Returned mutable vectors cannot change
the cache. There is no persistent cache or stored scientific acceptance result.
The [proof](PROOF.md) explains the conversion, denominator, cache and integration.

## Reproduce

Python 3.12 and the standard library suffice. From the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/selected-quadratic-replay
python3.12 -B research/selected-quadratic-replay/run.py
python3.12 -B research/selected-quadratic-replay/benchmark.py --output /tmp/selected-benchmark.json
```

The registered verifier runs the complete selected result and then the
independent actual-state cross-check, serially. The benchmark runs six fresh
processes in literal/new/new/literal/literal/new order. It requires identical
complete scientific stdout and rejects a changed implementation between runs.
The extra adapter corpus and literal cross-check are separate from the timed
complete source replay. The two-command package audit includes extra literal
work; no speedup is claimed for that larger audit. OS caches can be warm and
host load can vary.

`binding.py` compares every derived syntax tree with the exact source plus a
small declared transformation. Three omitted scientific checks reject. The
original source files are unchanged. The derived compiler retains every
remaining assertion as an explicit failure, including under `-O`.

## Scope and evidence

The complete result retains all 13 helper cuts, rational independent-input rows,
dense reverse columns, exact native maps and global phases, every physical
contact, productive main and helper targets, query and idle costs, both moment
engines, compiler checks and all outer predicates. It retains the source's
wrong-input, wrong-output, wrong-phase, extra-target and unpaid-call controls.
Both the regenerated WORD and complete RESULT must equal the retained artifacts.

The adapter corpus checks 1522 states and 22700 amplitude entries. Cache controls
cover type aliases, changed matrices/gates/widths/initial bases, mutable outputs,
capacity and eviction. All 39041 source state requests still execute. The process
cache has 21073 hits and 17968 misses, with at most 8192 entries. The source covers
19988992 amplitude entries before the separate independent literal cross-check.

This changes verification capacity. The selected conditional kappa .00310045,
complete invoice, native construction and five framework assumptions stay the
same. No physical multiplier speedup, new kappa, independent human acceptance or
proof-kernel result is claimed. This opt-in package does not change the selected
frontier or its official reproduction command.

## Sources and attribution

Base 553d26d796fde9871ff2661a49ac7732e945410f; frozen priority 7 card.
The submission refresh at de5ec2e7a6074068452f45b1a191b5c72832df4a read
priority 8. Its verification tooling task still calls for measured speed gains
with exact coverage. This result does not repeat the completed admission audit. The selected source is
PR 5599 at audited head 09dd0965711ca7eeb169057a420abab1c9052137. The reused exact
engine is PR 5704 at daa4d9dbd102d2a3677afc5614c56466bd2cf3a2. All 31 live inputs
have Git blob and SHA256 pins in SOURCES.json. The source and engine notices
remain byte-exact. The [canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/5748)
records scope and plan changes.

The [NOTICE](NOTICE) retains construction, engine, native, controller, compiler
and classical stabilizer credit. New integration and checks: Ali Romman with
substantial OpenAI Codex assistance. No subagents. Apache-2.0.

## Open next questions

- Does the whole-replay speedup hold on Linux and another host? Run the same
  serial benchmark and compare exact stdout before making that claim.
- Can a newer reviewed P104 word use this integration? Begin with exact source
  pins and a complete syntax-tree binding. A passing older word is not evidence
  for a changed caller, bill or native phase.
