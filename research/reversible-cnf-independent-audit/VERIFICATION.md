# Verification record

Linux x86_64, Python 3.12.13, standard library only. Base:
`df0137efd35e11b4445734bf612bdd4c7ebc330c`. The four reviewed source files
are byte-identical to PR #5369 head
`18354f41de4dc7bfda4692e814cf1d91a6d619ef`; exact Git blobs and SHA256 pins
are in SOURCES.json.

The initial source-bound scientific run completed in 3.47 seconds before the
additional compact-label fixture. Every check uses explicit exceptions and
remains enabled under optimization. The source compiler and its unchanged
exact helper are executed; the source evaluator/verifier is not used as an
oracle. Independent endpoint arithmetic uses Fraction throughout.

The following completed successfully on 2026-10-26:

```sh
python3.12 -B scripts/research_selected_baseline.py
python3.12 -B scripts/research_package.py --package research/reversible-cnf-independent-audit --check-only
python3.12 -B scripts/research_package.py --package research/reversible-cnf-independent-audit
python3.12 -I -O -B research/reversible-cnf-independent-audit/verify.py
```

The baseline checks selected source bindings/metadata, not scientific supplier
admission. The complete scientific receipt from normal and optimized execution
matches RESULT.json. The registered run checks source pins and all declared
finite controls; the general-source and selected cold replays were not run.

The pre-submission main refresh retained the same base. The fresh overlap
snapshot at 09:55:16 UTC covered 7,676 HEAD notes plus the two new package notes,
395 open PRs and 5,058 Discussion records with complete reported pagination
and no warnings. No new competing §6 audit was found. This is reported search
coverage, not a claim of novelty or coverage of unpublished work.

The focused shared navigation test was also run to distinguish a known base
failure from this package:

```sh
python3.12 -B -m unittest discover -s tests -p test_research_current_status.py
```

It ran six tests and failed the two subcases of
`test_current_ci_section_matches_selected_record` for `review` and
`source_manifest`. The current section of docs/ci-verification.md lacks links
to the selected PR5599 review and certificates/frontier5599-source.json.
Those tests, the document, selected files and workflows are unchanged by this
contribution. Existing [PR #5703](https://github.com/CrocSwap/integer-mult-bounds/pull/5703)
supplies the shared document repair; no duplicate fix is included here.
This known planning failure is separate from the passing package replay.
Hosted status will be reported on the published PR.

Committed-byte/source-history and export checks also passed:

```sh
python3.12 -B scripts/check_research_commit.py --package research/reversible-cnf-independent-audit --check-source-history
python3.12 -B scripts/export_research_package.py export --package research/reversible-cnf-independent-audit --output /tmp/imb-20261026-next-cnf.tar
python3.12 -B scripts/export_research_package.py check /tmp/imb-20261026-next-cnf.tar
```

The deterministic export contains 16 package/input files. It was extracted
with the tar data filter into a fresh directory outside the checkout. An
absolute Python executable ran the direct verifier from `/tmp` with `-I -O -B`,
`PATH=/nonexistent` and empty `PYTHONPATH`. Its complete scientific receipt
matched the committed one without Git. In that disposable copy, changing
RESULT.json caused the expected receipt mismatch, and changing the pinned
compiler caused source-hash rejection before execution. Both transport
controls were separate from the eight semantic endpoint mutations.

After recording these results, final committed bytes were rechecked/exported
and the full isolated optimized replay repeated in a second fresh tree.
The canonical base and predecessor head were also reconfirmed immediately
before publication. No frozen predecessor file was changed.
