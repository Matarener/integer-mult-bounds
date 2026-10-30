# Verification record

Scientific source commit: `86875c8044044d1ebae2689d13e871d4b0dc4424`.
Base: canonical main `df0137efd35e11b4445734bf612bdd4c7ebc330c`.

Python 3.12.13, macOS arm64, standard library. Registered normal and
optimized replay both passed on 2026-10-26. Expected markers were
`PASS_G20_AFFINE_HISTORY_ORDINARY_003484629984` and
`PASS_REGISTERED_RESEARCH_PACKAGE`. The live input and metadata check passed.

The checks include the complete local and global native contracts described
in README.md, a separate global event interpreter, two exact moment engines,
positive finite compiler fees and three semantic failure controls. The
committed-byte check passed for 162 files. The committed package export and
its integrity check passed; direct replay from the extracted export passed
without a Git checkout or network.

The first registered run found a JSON comparison mismatch: integer invoice
keys in memory must become string keys when serialized. The verifier now
compares the actual JSON representation with the committed JSON result. The
scientific word, invoice and interval results did not change. An initial
export launch used the archive file as a directory; extraction corrected the
launch. These execution errors are not mathematical counterexamples.

Full-history ancestry mode was not run in this shallow checkout. Hosted CI,
independent human review, a proof-kernel theorem and a full uniform multiplier
were not run. The retained framework assumptions remain. This package
improves the BIT component over its pinned PR5512 input; it does not set a
new best whole multiplication kappa.
