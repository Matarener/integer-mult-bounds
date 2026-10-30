# A physical reference route for QQ16 cover maps

A full-cover transfer can be implemented by an explicit four-tape finite-control
program on a tagged stream, with arbitrary dirty exterior, returned heads and
three restored clean work buffers. The same program works at four independent
supplied tape origins, at exactly the same cost. This supplies one explicitly priced
movement contract. It does **not** claim a favorable complete supplier invoice,
a new κ, or a change to the selected frontier.

For an n × n invertible binary right-action matrix g, translation δ and λ
address layers, let d = n² + nλ. Let D be a nonempty finite matrix-owner set
closed under g and g⁻¹, M = |D|, N = 2^(nλ), S = MN, payload width B,
and L = d + B + 2. The declared entry is one lexicographically tagged record
per actual (owner,address), with three blank work windows of SL + 2 cells.
No ghost owners or a vector-valued replacement for matrix owners are used.

[PROOF.md](PROOF.md) constructs and proves a route for

    output(a,z₁,…,zλ) = input(a g,z₁ XOR aδ,…,zλ XOR aδ)

in at most

    S [(2d + 2)q + (32d + 32)L] + 64(d + 1)

literal cell actions, where q = n nnz(g⁻¹) + nλ [1 + wt(g⁻¹δ)]. Reads,
writes, parity updates and unit head moves are individually charged.
Tag relabeling followed by stable streaming radix partitions implements the
permutation; there is no random-access sort, head reset or payload register.
The program is nonuniform in n, λ, g and δ, uniform in M, B and valid data.
The four-tape footprint is at most 4(SL + 2). Tags and work buffers are paid
entry requirements, not free layout conversions.

## Literal source application and evidence

The frozen B1 word has 528 cover-map uses with 512 distinct labels. Independently
represented binary matrix calculations give Σ multiplicity·q = 5,451,056.
For n = 73, λ = 1, B = 2W, the resulting **conditional per-owner upper bill**
for only those calls, including one handoff per call, is

    2^73 (182578176 W + 552230342688) + 182578704.

Here W is the **stored** bit width of one real component, including sign and
format bits. Identifying it with a numerical guard parameter requires a separate
encoding proof. Owner-set closure and the tagged ABI at every call remain premises. This does
not run the complete B1 word or supply a physical caller. The numerical grid,
entry conversion, arithmetic, retention, consumer, idle continuation and
all-size compiler are separate obligations. Three buffers are required here;
PR3270's one-buffer numeric storage estimate cannot be reused unchanged.

`router.py` is a cell-metered controller. `oracle.py` independently represents
matrices as dense rows and computes expected push/pull semantics. `verify.py`
checks all six GL(2,2) maps and four translations, a two-layer case, a complete
GL(3,2) owner cover, and two thin zero-owner layouts with one-bit payloads.
Mutation/rejection controls cover wrong translations, wrong radix direction,
singular maps, invalid translations and an exterior move. [RESULT.json](RESULT.json)
records the exact finite outcomes. The universal tape/cost result is an informal
proof; successful finite tests are not formal verification of that theorem.

## Reproduce

Registered replay requires Python **3.12**; the direct verifier also works on
later Python versions. Standard library only, from repository root:

```sh
python3.12 -W error -B scripts/research_package.py --package research/qq16-tagged-cover-routing --check-only
python3.12 -W error -B scripts/research_package.py --package research/qq16-tagged-cover-routing
```

For a Git-free copy, retain this directory and the declared input at
`research/joint-query/certificate.json.gz`, then run:

```sh
python3 -W error -B research/qq16-tagged-cover-routing/verify.py
```

Verification is read-only by default. `--write NEW_EXTERNAL_PATH` writes a fresh
receipt and refuses to overwrite one. Normal replay compares source constants,
finite cases, controls and code hashes with the committed receipt; the Python
version is reported separately and may differ. The source certificate is hash-checked
before decompression. [SOURCES.json](SOURCES.json) pins exact Git provenance;
[VERIFY.json](VERIFY.json) declares the only live external input. No predecessor
Python package is imported. The scoped Lean algebra project is separate
from the mandatory standard-library replay; see its exact status and commands in
[VALIDATION.md](VALIDATION.md).

## Reuse, overlap and credit

The MathProof DAG and Lean tree supplied the absolute unit-move model, finite
footprint frame principle, and cost-preserving tape embedding, plus independent tape-origin relocation. [PRECEDENTS.json](PRECEDENTS.json)
records the exact canonical and public portable sources and their evidence
boundaries. These guided the dirty-exterior and spectator-tape contracts; they
are not claimed to certify this new controller. No canonical DAG was changed.

The full-cover semantics and words are Ali Romman's joint-query construction.
PR3270 supplies the exact F0/B1 numeric grid but leaves physical routing unpriced;
PR3303 already extends its grid to all depths. PR3241 supplies local paid scalar
access, not this full-cover permutation. PR3339 identifies distinct consumer/idle
obligations. Concurrent PR3374 (Wentao Li) supplies a complementary partial F17
arithmetic bill while leaving maps and movement unpaid; it is credited without
substituting its completed-entry width for all producer interiors. [OVERLAP.md](OVERLAP.md) gives exact heads and coverage limitations.
[NOTICE.md](NOTICE.md) preserves the broader predecessor credit.

This session answers a changed part of `joint-query-controller`, priority
revision 6, at main `6f100d4bb5083f8c35d96fd95a539811c62f245c`.
[TASK.json](TASK.json) preserves the original card, scope change and checkpoints.
No claim of first use or exhaustive historical coverage is made.

## Open next questions

1. Bind one actual caller to this tagged layout and three clean buffers. First
   prove its owner-set closure and charge tag preparation; no such entry caller
   is supplied here.
2. Compare one complete paid supplier invoice including arithmetic, retention,
   F17 consumption, idle continuation and all-size compilation. The isolated
   routing polynomial is insufficient to decide that comparison.

Relevance, first steps and blockers are also structured in TASK.json. Stop here
before further construction expansion. New work is Apache-2.0 and was prepared
with substantial OpenAI Codex assistance; no independent human review is claimed.
