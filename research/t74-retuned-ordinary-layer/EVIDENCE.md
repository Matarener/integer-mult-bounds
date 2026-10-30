# Local evidence and reproduction boundary

Hiroki KUMAZAKI, with substantial OpenAI Codex assistance. Apache-2.0.
Recorded 2026-10-18 on Linux x86_64, CPython 3.12.13, standard library only.
Source base: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority revision 6.

The following completed successfully:

```sh
python3.12 -B scripts/research_package.py --package research/t74-retuned-ordinary-layer --check-only
python3.12 -B scripts/research_package.py --package research/t74-retuned-ordinary-layer
python3.12 -I -Werror -B research/t74-retuned-ordinary-layer/verify.py --suite rate
```

The registered launcher supplied fresh private bytecode namespaces and ran
both suites with `-I -O -Werror -B`. Normal and optimized rate receipts were
identical. The metadata PASS is not mathematical acceptance.

## Rate and source receipt

- `PASS_RETUNED_T74_RATE` and `PASS_COMPLETE_ORDINARY_BACKEND_IDENTITY`.
- Complete profile: 666 calls, 66,304 families, 2,394,506 positive children,
  rank mass 4,816,512. Both independent exact engines returned the common
  outward 30-place enclosure recorded in PROOF.md.
- `tau=332353/332929`, `sigma=998271/1000000`, stopped-leaf exponent
  `998272729/1000000000`, final exponent `998273/1000000`.
- Seven rate controls reject the direct ordinary-moment substitution, one
  extra rank-one child, the old ordinary profile, earlier stopping, an
  unpaid leaf penalty and absent internal/reservation logarithmic margins.
- The independent rational toy tree explicitly enumerates 31 internal nodes
  and 125 leaves; costs are 61 and 250. Its three controls expose the reversed
  inequality, omitted leaves and changed strict-threshold behavior.
- The exact PR3562 proof/interface bytes match their original Git blobs and
  SHA256. All 35 files in its exact backend export manifest occur unchanged
  in the authenticated T74 controller archive closure. This compares bytes;
  it does not independently prove PR3562's all-size ordinary theorem.

## Factory receipt

- `PASS_RETUNED_T74_FACTORY` and `PASS_RETUNED_T74_FACTORY_BINDING`.
- Whole native constructor AST equals the retained constructor after changing
  exactly the `Profile` keywords to `(1,577)`. Both comparisons use the same
  interpreter; no cross-version AST serialization hash is an acceptance pin.
- Public production entry-point recorder traces T74 binding, catalogue,
  specifications, topology, native binding, mode-zero compilation, ordinary
  construction and the root receiving the same native object.
- Nine controls reject the old profile, invalid production prime/type,
  changed capacity, fixture-only index floor, wrong downstream native,
  non-ordinary object, root-native substitution and stale private binding.
- Reduced direct root: four packets, digest
  `4fced21f9e114bff265815a79dfe0b02e2989a195c87a6c5a16b7041193fd760`.
- Reduced fast root: one packet, five entries and five returns, digest
  `75b19b9d75e245f1720eaccc048c366a7a68cf7741805e908b0a2222067d4b40`.
- Ordinary `run` call counts are exactly `[0,0]`. These root fixtures check
  installed retuned object identity, normalized endpoints, borrowed source
  and descriptor preservation, balanced returns and owned cleanup. They do
  not execute the selected ordinary branch, full T74/O73/GL64, or production
  precision guard. The production construction test uses explicit recorders.

## Publication checks

The focused PR and canonical Discussion carry the publication commit and
post-commit receipts. Reproduce the byte/history and export checks with:

```sh
python3.12 -B scripts/check_research_commit.py --package research/t74-retuned-ordinary-layer --check-source-history
python3.12 -B scripts/export_research_package.py export --package research/t74-retuned-ordinary-layer --ref HEAD --output /tmp/t74-retuned.tar
python3.12 -B scripts/export_research_package.py check /tmp/t74-retuned.tar
```

From the Git-free extracted export, run both `verify.py --suite rate` and
`verify.py --suite factory` commands with a fresh bytecode cache prefix.
The two pending PR3562 context files and exact manifest are already retained;
no cached PR Git object or network fetch is required for these checks.

Independent all-size scientific review, complete native/refinement premises
and the outer error/packing/multiplication transfer remain open. Same-session
Codex peer review is not independent human or formal verification.
