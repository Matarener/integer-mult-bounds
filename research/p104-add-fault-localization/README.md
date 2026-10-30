# Exact ADD-coefficient localization for P104 scalar endpoints

This contribution is produced by Nick Petalas. It adds a diagnostic capability
and a scoped correctness proof with finite evidence. No new kappa is claimed.

DreamingOfClouds's [PR5568](https://github.com/CrocSwap/integer-mult-bounds/pull/5568)
asks whether `tk check` can identify the event behind a wrong ADD value. Its
scalar endpoint check reports the affected output rows. This package supplies
a standalone exact diagnostic that returns every single ADD coefficient
replacement restoring the complete declared scalar endpoint. It leaves the
predecessor toolkit and all published words unchanged.

The source-bound demonstration changes event 0 of the retained PR5561 word
from `ADD 112,704,-2` to `ADD 112,704,-1`. The diagnostic reports exactly one
repair, event 0 with replacement `-2`. Applying it restores every scalar output
as a function of every arbitrary public input, including dirty helpers. This
demonstrates the new diagnostic; it is not an audit of PR5561's result.

## Contract and result

For a fixed rational linear program, let F be its current complete endpoint
matrix and T the required matrix. At ADD event i, let p_i be its source's
prefix input row and q_i its destination's suffix output column. The exact
coefficient-change identity is

```
T - F = delta * q_i * p_i.
```

The diagnostic checks a necessary-and-sufficient row/column proportionality
test for this identity. It computes the full repair set with two forward
passes and one reverse pass, without keeping a full matrix for every event.
[PROOF.md](PROOF.md) states and proves the contract, including singular COPY,
INIT and CLEAR operations. Prefix/suffix rank-one sensitivity is prior
mathematics. The contribution is this coefficient-repair diagnostic and its
P104 application, not the sensitivity identity itself.

Outputs distinguish `localized`, `rank_exceeds_one`, `no_single_add_repair`
and `already_matches`. Several repairs can be compatible with the same
observed endpoint. All are returned, and the historical fault is then
ambiguous. A zero residual cannot reveal a fault overwritten by COPY/CLEAR
or one reading an identically zero source.

The P104 command observes all public and eight owned outputs, with arbitrary
public inputs and initially zero owned inputs. It uses the toolkit's endpoint
`y_(s+112) += x_s` on each declared live port. Each repair also reports whether
its coefficient is nonzero, dyadic and satisfies `abs(c)+1 < 2^16`.

## Reproduce

From the repository root, using CPython 3.12 and the standard library:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/p104-add-fault-localization/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/p104-add-fault-localization/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/p104-add-fault-localization
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/p104-add-fault-localization --check-source-history
```

The direct marker is `PASS_P104_ADD_FAULT_LOCALIZATION`. The verifier generates
the mutation in memory, computes its complete repair set, applies the repair
in memory and checks the complete repaired endpoint. Ordinary replay writes
no files. `verify.py --emit` emits the generated hash-bound receipt to stdout;
normal execution recomputes and compares every field of [RESULT.json](RESULT.json).

To diagnose another candidate under this same P104 scalar endpoint contract:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -I -B research/p104-add-fault-localization/diagnose.py /path/to/candidate.json.gz
```

The command prints JSON suggestions and never modifies the candidate. Running
it on the unchanged pinned word prints `already_matches`. Frame and ownership
checks must still be run separately before adopting a suggestion.

## Finite evidence

The verifier enumerates every word of one through four ADDs on two roles,
with both directions and coefficients in `{-1,1}`. For each event, it applies
each of three nonzero rational coefficient changes. An independent oracle
replays scalar basis inputs through the whole program for every possible
repair event and compares the complete repair sets. Each returned repair is
also applied and replayed directly. This oracle builds no prefix/suffix tables.
The domain contains 340 words and 3,756 injected faults, with 7,740 compatible
repairs returned across those cases. The additional singular-operation fixtures
cover 21 faults, including 12 endpoint-invisible cases.

Separate controls exercise COPY, zeroing, zero SCALE, negative and fractional
scales, MOVE, invisible faults, two indistinguishable repair events, a rank-two
residual, a rank-one residual with no ADD repair, a nondyadic semantic repair,
malformed programs and resource-bound rejection. [RESULT.json](RESULT.json)
records the enumerated counts and transcript hash. Finite tests corroborate
the written proof; they do not establish it by extrapolation.

## Scope, implementation and limits

This answers a verification-tool question from PR5568. The `replay-runtime`
card is explicitly changed from speed to diagnostic capability. No performance
comparison or speedup is claimed. The selected source-binding orientation
passed at canonical main `3f0152a32eeebac0df11946dbd50cabe5a7f7839`, priority
revision 8, with selected kappa `781451/250000000`. No frontier change follows.

The single-fault model changes one ADD coefficient. Wrong operands, several
faults, changed chronology, native phases and frame faults are outside its
completeness claim. A repair suggestion proves only the declared scalar map.
It does not prove legal owned erasure, zero-before-COPY, native action,
precision, tape cost, a paid caller, compiler closure or supplier admission.
Independent human and formal proof-kernel review are unclaimed.

Code has no recursion or dynamic evaluation. Functions stay below 60 lines.
Every loop ranges over bounded roles, events, input coordinates or the fixed
finite verification domains. The diagnostic caps roles at 1,024, events at
26,000, input files at 16 MiB, input coefficient sizes at 256 bits and stored
linear-map fractions at 4,096 bits. Exceeding a limit raises an error and returns
no partial diagnostic. Normal and optimized warning-strict registered runs
are the recurring diagnostics. No configured Python static analyzer was found
for this scoped package; no repository-wide analyzer configuration is changed.

Power-of-Ten rule 3 deviation: CPython allocates managed dictionaries and exact
fractions during replay. The scope is this bounded offline diagnostic and its
fixed verification domain. At most three role-by-coordinate tables, including
the supplied target, are live in a pass, each with at most 1,024 squared entries,
with input, candidate and result records each bounded by 26,000 events.
Stored map fractions are checked explicitly; the ratios and repair formulas
have finite size bounds derived from these coefficients. Library allocations
are not claimed allocation-free or independently instrumented. A larger-domain
implementation must establish new capacity limits before raising these guards.

## Open next questions

- Which coefficient events in one frozen P104 word have indistinguishable
  complete repair signatures? Start by grouping normalized nonzero signatures
  and retaining zero signatures separately. This package supplies one diagnostic
  example, not a complete P104 fault-class census.
- Can the owning legality checker consume these suggestions while preserving
  every frame, ownership and native obligation? Start by checking one reported
  candidate through that verifier. A scalar repair alone cannot certify it.

## Related open work and credit

[PR6170](https://github.com/CrocSwap/integer-mult-bounds/pull/6170) packages a
larger P104 designer toolkit, including the same endpoint-only localization
limitation in its retained oracle. This package adds a separate exact
single-coefficient diagnostic; no pricing or word improvement is compared.

DreamingOfClouds retains PR5568's tooling and question. Ali Romman retains the
PR5544/5545 word/verifier line and PR5392; thu-nmrc retains PR5551; the PR5553,
PR5561 and GamingPuzzled / PR5472 handoff and retime lineage remain credited.
The original compressed word is consumed unchanged and hash-pinned.

Credit woklerx's [PR1017](https://github.com/CrocSwap/integer-mult-bounds/pull/1017)
R439 omission atlas and Sagar Thakrar's PR762 fault-testing precedent for the
earlier prefix/suffix fault model. Their source circuits, results and code are
not rechecked or imported. The P104/native/helper/caller/compiler contributors
retain their results. New proof application and code are produced by Nick
Petalas. New material is Apache-2.0.
