# Validation and exact scope

2026-10-19, canonical base20ecf2891d80b5acf18d980b2164fb44ea7faa90.

The owner ran the normal replay, package metadata/pin check, the independent
optimized F2 control and the Git-free failure controls successfully. A separate
same-session Codex adversary challenged the algebra before replaying all four
registered commands against frozen scientific files:

| Command | Result | Elapsed |
|---|---|---:|
| verify.py normal isolated | PASS, digest a65726b130461a663ff79772c4d4b35837aa7adb07676ca58daeda3d2632c16a |1.802s|
| verify.py optimized isolated | Same PASS/digest |1.676s|
| test_package.py | Read-only Git-free export and four rejection controls PASS |6.788s|
| independent_f2.py optimized isolated |16960 products; exclusion, full-width escape and quotient equality toy PASS |1.313s|

The reviewer compared before/after SHA256 of PROOF.md, verify.py, RESULT.json,
independent_f2.py and test_package.py: all unchanged.
Reviewed PROOF.md SHA256:
`11efd1acd5c0d0638f26ab8922cf8a7d6eecf5585d87e68b6b9566ecf5e2110d`.
RESULT.json SHA256:
`22a53a2ef7f77500b7fbd7d68643c268899735a530f27964f57f064f21cc5a5d`.

The reviewer found no remaining substantive issue in the serial affine domain.
During development the review corrected an overstrong exact-rank phrase to an
invertible-minor lower bound, made diagonal ancestor weights explicit, and
strengthened the necessary total width from59 to115 and finally121. The package
contains only the final proof and final121-rank receipt. The independent checker
uses explicit exceptions so optimized Python cannot disable the checks.

This is independent same-session AI review, not human or formal-kernel approval.
The all-GL64/split-projector production premise and compiler census are inherited
at pinned heads. No full physical source/producer/CALL/RETURN/stock/precision
replay, selected cold replay or improved kappa is asserted. Parent publication
will separately authenticate exact Git objects, export and hosted CI; those
results are not retrospectively claimed in this local receipt.
