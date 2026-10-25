# Validation and publication review

The mathematical package was checked at
`d82a679985888b703f689833c2b12780a8243382`, based on canonical
`12fa8c5c844be21bfefb38a19503fbd867a11244`.

The standalone runner executed all ten checks in [REPLAY.json](REPLAY.json)
in normal and optimized Python, first in the owned checkout and then in a
Git-free export of the committed package: 40 fresh check invocations in
total. All mathematical receipt bytes agreed. The final committed export
included a formatting-only correction made after the checkout replay.
The original export's source-manifest SHA256 was
`8bcedf654ca08fadabe1cd56c54684b813f4d89e83d4b8883983173f2b416dac`.
Run logs and process-cleanup receipts were retained locally; the mathematical
receipts and checkers are included here for independent reproduction.

The publication review rederived the finite-branch argument and narrowed two
summary phrases: the earlier-cut search has COPY rank at most four, and the
main floor concerns total COPY-plus-MOVE rank. It also added explicit next
questions and refreshed overlap/credit references. These publication changes
leave all mathematical proof files, executable checkers, scientific inputs
and fixed mathematical receipts byte-identical to the verified package.
The source inventory is updated to authenticate the revised documentation.
This reuses the matching mathematical replay evidence; it does not report
those executions as newly repeated during publication.

[The separate review](independent/REVIEW.md) distinguishes independent finite
checks from written all-parameter arguments. Its
[validation record](independent/VALIDATION.json) includes normal/optimized
Python 3.14 and a minimal Git-free Python 3.12.12 check, plus disabled-guard
controls. The independent checker does not execute producer modules.
This is independent **agent** review, not independent human or formal-kernel
certification.

From the repository root, reproduce with CPython 3.12 or later:

```sh
python3.12 -I -B research/bit-copy-path/verify.py --output /tmp/bit-copy-path-check.json
```

Use a fresh output path. The expected final marker is
`PASS_ACTUAL_BIT_COPY_PATH_SCOPED_OBSTRUCTION_NO_NEW_KAPPA`.
This package uses its own explicit replay format and standalone verifier.
The predecessor's complete historical suite, selected supplier cold replay,
physical compiler admission and full multiplication theorem are not covered.
Hosted CI status is reported separately on the PR. κ and the selected
certificates remain unchanged.

Apache-2.0. Prepared for Ross Richardson with substantial OpenAI Codex assistance.
