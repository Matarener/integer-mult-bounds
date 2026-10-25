# Integer labels and XOR scatter in one checked export boundary

`integer-xor-scatter-v1` composes PR3100's exact-integer label contract with
PR3273's XOR-normalized scatter contract. It retains PR3273's full symbolic
check before export. The result is an opt-in compiler-boundary repair; it does
not change the selected supplier, frozen inputs, or kappa.

## Why this composition is needed

The two underlying defects and their individual repairs are already known:

- Nick Petalas's PR2977 found that the checker counts scatter occurrences
  modulo two while the exporter tests membership. PR3273 supplies the
  `xor-scatter-v1` normalizer and checks its complete exported action.
- `josecarlosgonzalezroque-design`'s PR3100 found that the checker applies
  `int(a)` to label coordinates while export uses `Fraction(a)`. Its
  `integer-labels-v1` guard is composed with PR2992's simple-support wrapper.

PR3273's actual public boundary still admits PR3100's fractional-label witness:
changing `lines[0][1]` from `0` to `0.5`. Its symbolic checker sees the original
integer geometry, while export retains the fractional coordinate. Correct
scatter counts do not detect the resulting geometry discrepancy.

This package supplies the missing composition. It accepts occurrence-based
scatter lists, including cancelling pairs, while rejecting noninteger label
encodings before delegation. The contribution is the combined executable
boundary and its integration controls, not discovery of either underlying bug
or a new normalization theorem.

## Contract and implementation

The schema is `integer-xor-scatter-v1`. It first applies PR3100's authenticated
`validate_labels`: `v` is a positive exact integer, `h` is the integer 8,
`lines` has exactly `v` rows of length `h`, and every coordinate has Python type
`int` after JSON parsing. Booleans, strings, fractional numbers, and integral
float spellings such as `0.0` are rejected. Integer typing does not establish
E8 geometry; the full symbolic check is still required.

It then delegates to PR3273's authenticated XOR boundary on a private snapshot.
That boundary reduces each row's slot occurrences modulo two, runs the full
symbolic checker on the normalized word, and exports only after that check
succeeds. COPY/ERASE pairs remain charged per retained slot; aliases and unused
slots are not coalesced. Its emitted invoice checks are retained.

The input is limited to 5 MiB both compressed and decompressed. The inherited
XOR limits remain: at most 256 targets, 4096 helpers, 256 retained slots,
4096 occurrences per row and 65536 occurrences overall. These are implementation
limits, not mathematical bounds. The API is
`execute(mode, input_path, output=None, root=ROOT, scratch=None)`.

The wrapper authenticates and privately snapshots the predecessor validator,
XOR implementation, its source manifest, and the delegated checker/exporter.
The original input is parsed and label-validated before its snapshot is passed
to XOR validation. Thus replacing the original input after validation does not
substitute unchecked label data. Publication inherits the XOR wrapper's
existing-output protection; copying the output files is not a filesystem
transaction. A copy failure can leave a partial new output directory.

For exact integer coordinates, `int(a)` and `Fraction(a)` represent the same
number. For each retained slot with occurrence multiplicity `m`, the scatter
normal form preserves its characteristic-two coefficient `m mod 2`. These two
predecessor arguments concern different fields and apply to the same private
word snapshot. The full symbolic checker remains responsible for the other
word, frame, endpoint and interface conditions. No claim of complete JSON
schema validation follows from these two contracts.

## Reproduction and evidence

From the repository root:

```sh
python3 -B scripts/research_package.py --package research/integer-xor-scatter-boundary
python3 -I -O -Werror -B research/integer-xor-scatter-boundary/verify.py
```

Use the new entry point with a candidate word:

```sh
python3 -I -B research/integer-xor-scatter-boundary/boundary.py check WORD.json.gz
python3 -I -B research/integer-xor-scatter-boundary/boundary.py export WORD.json.gz OUTDIR --scratch SESSION_SCRATCH_DIRECTORY
```

`OUTDIR` must be new. Check mode takes no output path. The receipt reports
`schema`, `input_occurrences`, `normalized_scatter_terms`, and, in export mode,
the inherited exported invoice.

[RESULT.json](RESULT.json) records the finite regression results. The controls
exercise the public wrapper, exact selected export preservation, cancelling
scatter pairs, the fractional-label counterexample, and their combination.
An integer-coordinate mutation that violates the original geometry must still
be rejected by the full checker, demonstrating that the type guard does not
replace semantic validation. The registered commands and their bounded input
closure are in [VERIFY.json](VERIFY.json); exact predecessor pins are in
[SOURCES.json](SOURCES.json).

The scientific base is canonical main
`6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority revision 6. This package
performs no fresh native C++/Boost replay, nonempty kernel/owner/donor admission,
complete selected cold replay, physical hosting or routing, precision/tape
transfer, all-size multiplication proof, or supplier-moment improvement.
PR3326's native results belong to that predecessor and are not silently
extended to this successor. Hosted CI and independent human review are separate
from local automated verification.

## Overlap and attribution

The initial `find_overlap.py` refresh had no usable remote snapshot because
`gh` was unavailable. Public GitHub API searches subsequently covered all
results for XOR scatter (11), scatter/nonempty (6), scatter/donor (23), and
PR3100 references (4), supplemented by local sources and visible portions of
Discussions 2976 and 1166. No matching combined integer-label/XOR repair was
identified. Further API searches hit the unauthenticated rate limit. This
coverage excludes arbitrary diffs, hidden discussion comments and unpublished
work; absence of a match is not proof of novelty. [TASK.json](TASK.json)
records the scope refinement and coverage.

Credit Nick Petalas for PR2977's mismatch and PR3273's XOR boundary;
`josecarlosgonzalezroque-design` for PR3100's label witness and validator;
Arham Tahir for PR2992's simple-scatter boundary; and kumagi/Hiroki Kumazaki for
PR3004's parity/count analysis. Retained-alias qualifications and native
controls belong to Sricharan Vagvala/PR3128, James Reed/PR3099, and
commdata2338/PR3210/PR3222. PR3326 supplies the separate genuine-Boost native
composition audit. eumemic and DreamingOfClouds retain the selected word/checker
lineage, Dylan Crow the exporter/native lineage, and Douglas Colkitt the
selected bindings and review framework. All source notices remain unchanged.

Prepared for Pierre with substantial OpenAI Codex assistance in research,
implementation, automated adversarial review, verification and writing.
Apache-2.0; no independent human or proof-assistant review claimed.

## Open next questions

1. Should a named successor supplier adopt this combined boundary? First bind
   its producer and consumer to the schema and source manifest, then replay its
   complete symbolic/export/native chain. Maintainer adoption and the complete
   supplier obligations remain open; this opt-in wrapper changes no production
   caller.
2. Does it compose with a named nonempty kernel, owner and donor construction?
   PR3326's native fixture uses empty ownership inputs. First pin a concrete
   fixture and enumerate live-source, ownership, bank and complete invoice
   obligations. Fresh native and physical accounting are required before
   claiming that stronger result.
