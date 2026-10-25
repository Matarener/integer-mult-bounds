# Lean formalization of the compiler census

**Kernel-checked model and finite-data theorems; not an end-to-end formal
verification of the Python compiler or integer multiplication.**

## Main statement

`CompilerAudit.Result.selected_compiler_model` quantifies over every `N : Nat`
and every key-indexed block budget `blocks : Key -> Nat`. It proves, for the
explicitly defined selected trace and allocation model:

```
distinct source keys       = 28278 * N
retained wrapper IDs       = 904896 * N
direct operation references = 1809792 * N + B
```

Here `B = ((Selected.word N).map blocks).sum`. Repeated visits to a key receive
the same budget in this composed model, matching stable source-plan emission.
`Retention.lean` separately proves the allocation/reference results for an
arbitrary list of per-visit budgets, including zero. Neither statement prices
native instructions, memory bytes or the block operations themselves.

This is not a proof that merely defines the totals by those formulas. `Visit`
constructs the ordered list by group, replica and the appropriate LOW/request
nesting. `Retention` constructs begin/block/finish operations, allocates a new
ID at each visit, and defines retained IDs from references in those operations.
The cardinalities and reference count are proved from those constructions.

## What Lean checks

| Module | Formal result |
|---|---|
| `Visit.lean` | Generic word length, support and per-key multiplicity, with both loop orders; a wrong-order witness with unchanged length/support |
| `Retention.lean` | Fresh IDs, begin/end ID lists, exact retained support, and `2 * visits + sum budgets` references |
| `Composition.lean` | Composition of ordered visits with fresh allocation; wrapper/key ratio and strict inequality under positivity |
| `SelectedData.lean` | Generated data, not a theorem: the actual 19 interval descriptors |
| `Selected.lean` | Pairwise interval separation, no duplicate IDs, coverage of `[0,28278)`, and selected coefficients, without enumerating 28,278 IDs in the proof |
| `Result.lean` | The concrete combined theorem above, with no hypotheses besides its `N` and `blocks` parameters |

The first complete qualification checked 60 declared theorems. Their reported
axiom dependencies were subsets of Lean's standard `propext`, `Classical.choice`
and `Quot.sound`. No custom axioms, unfinished proofs or `native_decide` are used.
The checker also asserts the exact expected type of the main theorem; printed
names alone are not its acceptance criterion.

## Source correspondence and remaining premises

`extract_census.py --check` reruns the original authenticated Python metadata
census and compares the JSON certificate and generated Lean data byte for byte.
It checks all 121 public live inputs and binds the relevant audit-module bytes.
The interval compression is accepted only when it reconstructs every ordered
request-ID list exactly. Lean then proves the partition/count facts about those
intervals. See [CERTIFICATE-CONTRACT.md](CERTIFICATE-CONTRACT.md).

**This is an executable source-data bridge, not a verified Python parser or
semantic refinement theorem.** Applying the Lean result to the original source
still relies on:

- Correct Python extraction and correspondence of the audited loop/allocation
  code to this model; hashes bind bytes, not their semantics.
- Request positions that emit residuals being independent of the LOW value,
  identical request-ID sequences across replicas, and stable metadata/plans.
- A repeatable, bijective identification of the actual LOW classes with indices
  below `N`, plus the inherited prime/source admissibility hypotheses.
- Successful complete source compilation. Neither the Python checks nor these
  symbolic proofs materialize the selected GL64 instruction word.

The machine's numerical callbacks, full runtime behavior, GL64 rank/unrank
algorithm, safe wrapper interning, native installation/space/traffic, selected
stock, precision and outer multiplication theorem are not formalized here.
The selected frontier is unchanged.

## Reproduce explicitly

Prerequisites: Python 3.12, Lean **4.34.1** (compiler commit
`5045d0056413266e57c625dcd7c365b10e377c52`) and mathlib at
`d13f23b723b8a846827a245b89c10fc7d3f11612`. All transitive revisions are locked
in `lake-manifest.json`. Keep that lockfile; do not update it during reproduction.

From this directory, with the toolchain installed, dependency acquisition is an
explicit setup step (it may use the network):

```sh
lake exe cache get
lake env python3.12 check.py --output /absolute/fresh/lean-check
```

Alternatively use an already configured `LEAN_PATH` containing the pinned
mathlib/dependency build directories, and pass `--lean` and `--leanchecker`
with the exact compiler/checker paths. The qualification used existing local
libraries read-only; it did not install or rebuild historical dependencies.
Use your Python 3.12 launcher if its local name differs from `python3.12`.

`check.py` never runs dependency update/install commands. It compiles all owned
modules into a fresh external directory, audits every declared theorem's axioms,
checks the exact main-theorem type, and replays each leaf module separately with
`leanchecker`. It uses the **same Lean kernel**, not an independent verifier;
imported library environments and the toolchain remain trusted dependencies.
Do not run `leanchecker` without an explicit module target: that selects a broad
prefix. The supplied script uses serial leaf targets and 180-second child limits.

The replay must reject three false propositions (missing finish reference, wrong
replica count and wrong request count), an altered certificate, and a wrong loop
order in the generated Lean data. It saves full diagnostics and `RESULT.json`
outside the source tree. A successful exit and result file—not this README or an
expected-output file—establish that a particular replay passed.

The repository's ordinary `VERIFY.json` remains a Python-only hook; it does not
automatically run Lean or acquire its dependencies. The portable source export
contains this project but no cached libraries or compiled `.olean` evidence.

## Attribution

The original compiler, logical caller, catalogue and preceding audits retain
all credits and notices in the parent README and frozen source exports. The
formalization was prepared with substantial OpenAI Codex, GPT 6 Astra and Claude
Opus 5.5 assistance. Separate AI source review is not human review or a substitute
for executing the checker. Lean and mathlib contributors supplied the proof
assistant and imported library results. New files retain Apache-2.0 licensing.
