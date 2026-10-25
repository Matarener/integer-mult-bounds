# Adaptive continuation: portability and bounded replay review

This is a read-only dependency review of the production scripts as retained in
the adaptive continuation. No frozen scientific source or evidence was edited.
The earlier global and boundary manifests already cover all 15 external files
needed by the bounded adaptive checks listed below. Preserve the repository
directory layout when extracting the archive.

## Exact external dependency closure for bounded checks

All paths below are relative to the repository root. The complete adaptive
scope, including its pinned PR3815 source, native source snapshots, native
artifacts and receipts, is assumed to be included.

```text
research/complex-local-word-ceiling/ceiling.py
research/kappa-global-continuation/invoice-analysis/invoice.py
research/kappa-global-continuation/invoice-analysis/evidence/RESULT.json
```

Under
`research/kappa-global-continuation/inputs/kappa-consumer-followup/artifact/live-source/research/staged544-producer-return/`:

```text
owner_audit.py
PROOF.md
inputs/ORDER.json
inputs/DISPATCH.json
inputs/NATIVE-base.json.gz
inputs/NATIVE-extra.json.gz
inputs/PLAN.json.gz
inputs/TEMPLATE.json.gz
inputs/PROFILE.json
words/BORROW-WORD-43base.json.gz
words/BORROW-WORD-43extra.json.gz
```

The remaining file is
`research/kappa-global-continuation/inputs/kappa-consumer-followup/artifact/integer-mult-bounds/research/pr3190-independent-operator-audit/vendor/DATA-PHASES.json`.
The repository LICENSE and NOTICE should also remain with the archive.

The inventory above was compared with the exact `repository_dependencies` and
`files` closures in the prior manifests: all 15 paths are present. No additional
outside-scope code is imported by the bounded path. Each current native run has
all 18 compiler source files bound by its `RESULT.json`; the source bytes total
128,313 per provider. Those in-scope snapshots must remain with the native
artifacts because `native_owner_invoice.py` authenticates them directly.

## Bounded verification order

Run inside a disposable extraction because most checkers regenerate their
receipts. The arithmetic interfaces require Python 3.11 or later, with assertions enabled. These checks need
only the Python standard library; the retained outer ledger optionally uses
gmpy2 as an accelerator. The optimization/discovery scripts using SciPy are
not part of this path.

From the repository root, the constructive finite gates are below. Replace
`REBUILD_WORDS` by a fresh directory. Compare its two decoded word payloads with
the retained candidate payloads; keep the retained compressed candidates in
place for their already-bound native receipts. See the compression limitation
below.

```sh
python3 -B research/kappa-adaptive-continuation/native-alternatives/construct.py --out REBUILD_WORDS
python3 -B research/kappa-adaptive-continuation/architecture/review_receiver.py
python3 -B research/kappa-adaptive-continuation/native-alternatives/verify.py
python3 -B research/kappa-adaptive-continuation/check_clock.py --out research/kappa-adaptive-continuation/CLOCK-REVIEW.json
python3 -B research/kappa-adaptive-continuation/global-budget/review_pr3815.py
python3 -B research/kappa-adaptive-continuation/global-budget/native_owner_invoice.py --base-local research/kappa-adaptive-continuation/native-alternatives/native-base/native/local --extra-local research/kappa-adaptive-continuation/native-alternatives/native-extra/native/local --out research/kappa-adaptive-continuation/global-budget/receiver-sharing
python3 -B research/kappa-adaptive-continuation/global-budget/receiver_packing_ceiling.py
```

The native verifier above binds retained complete native proofs; it does not
rerun those large all-column and phase computations. The owner/invoice gate
does freshly check all 1,321,920 finite helper rows and the two exact price
engines. Neither gate replaces complete supplier admission.

The separately retained outer arithmetic copy is self-contained:

```sh
python3 -B research/kappa-adaptive-continuation/global-budget/admission-review/outer/check_ledger.py
python3 -B research/kappa-adaptive-continuation/global-budget/admission-review/outer/independent_check.py
```

It reads only its adjacent `B.json`, `../new/SPEC.json` and `../CLAIM.json`.
The harness should bind these copied inputs to the current physical invoice and
the source adaptation receipt before interpreting these as the matching outer
arithmetic gates. These commands do not repeat source reconstruction.

For the architectural exclusions, add the following, replacing
`REBUILD_GEOMETRY` by a fresh directory. Compare its decoded geometry and result
with the retained geometry before running the price certificates against the
retained files.

```sh
python3 -B research/kappa-adaptive-continuation/architecture/seven_geometry.py --out REBUILD_GEOMETRY
python3 -B research/kappa-adaptive-continuation/global-budget/p3_certificate.py
python3 -B research/kappa-adaptive-continuation/architecture/pair_count_certificate.py
```

The last certificate requires the receiver review and current receiver-sharing
PRICE already present. `changed_inventory_screen.py`, `profile_prices.py` and
`discovery_summary.py` are optional exact screening or discovery-binding checks.
No repeated numerical optimization is needed to reconstruct the selected word.

## Runtime fixtures without full extraction

Authenticate the PR3815 `REPLAY-INPUTS.tar.gz` and its `REPLAY-INPUTS.json`, then
extract only member `source/code/audit_allcold.py` into a fresh temporary
directory. Its exact SHA256 is
`fa3488b62efdf8a0c37de0ca0caba587b4b036c5f068e002eb04c71c12b9e9b4`.
Pass that temporary file to:

```sh
python3 -B research/kappa-adaptive-continuation/runtime-repair/fixtures.py --audit-script TEMP/audit_allcold.py --out TEMP/FIXTURES.json
```

This bounded path checks the exact source transformation and isolation failure
modes. The source-bound independent review is `REVIEW-SYMMETRIC.json`. A whole
runtime audit additionally requires the prepared admission tree and its large
hosted inputs; `replay_audit.py --admission ... --out ...` is not a compact check.

## Portability restrictions and full replay

No literal workspace-specific absolute path was found in the adaptive
production Python scripts. Current replay logs and command receipts contain
historical absolute paths; these are provenance, not reusable commands. Replay
commands must be generated from the new extraction location.

Binary regeneration has an additional concrete runtime dependency. The retained
candidate words and geometry were written with Python 3.12.14, zlib 1.3.2 and
gzip OS byte 3. The inspected standard-library implementation delegates
`gzip.compress(..., mtime=0)` directly to zlib. Those compressed bytes need not
be identical under another runtime or platform, even when the decoded canonical
JSON is identical. Authenticate the retained binary artifacts first, reconstruct
into fresh temporary directories, and compare decoded canonical payloads. Keep
the original compressed artifacts for downstream receipts that pin their exact
SHA256. Strict binary regeneration requires a matching producing environment;
the arithmetic's Python version requirement alone does not guarantee it.

`native_owner_invoice.py`, `review_receiver.py` and the explicit-profile mode
of `profile_prices.py` record inputs relative to their repository root. Keep
their supplied input files inside that root. Relocating the entire repository
is supported; arbitrary outside-root input locations can fail `relative_to`.

`admission/receiver_share.py` and `admission/review_receiver_share.py` import
`audit_core` and `audit_verify` from the reconstructed original source. They are
extension modules installed into `source/new/borrow` by `run_candidate_release.py`;
they are not standalone commands from their retained adaptive directory.
`global-budget/review_admission.py` similarly requires a separately prepared
`--work` tree and a fresh `--out` directory. The independent bounded receiver
review and retained outer copies above avoid that reconstruction requirement.

The native README's optional direct fresh-native command uses the external
`research/gmx-t74-borrow43-handoff/new/fastnative` directory. To support that
exact command, include `run_native.py`, `common.py`, `stage.py`, `PINS.json`, and
the complete `vendor/` tree. The loader checks its exact vendor inventory, so
unused-looking vendor files cannot be pruned. Full native execution also needs
NumPy, with the retained driver specifying version 2.2.6. This optional external
dependency can be avoided by using `run_candidate_release.py`, which extracts
the self-contained driver from the in-scope PR3815 replay archive.

POSIX fork isolation provides the runtime adapter's memory savings. Platforms
without `fork` use the original pickle-copy fallback and may have different
memory requirements. The `resource` import is optional. Its `max_rss_kib`
diagnostic uses Linux units; macOS reports a different unit. No scientific
predicate or result depends on that diagnostic.
