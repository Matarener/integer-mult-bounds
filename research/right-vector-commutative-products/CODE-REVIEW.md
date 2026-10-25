# Separate static review and root integration check

A separate OpenAI Codex reviewer inspected the retained source contract,
PROOF.md, engine.py, oracle.py and both core payloads. No concrete correctness
defect was found. It checked the common-row/column unit condition, componentwise
unit choice in the three-factor word, all-finite-field quadratic-extension
argument and the delta-two deduction. The BFS review covered the complete
descriptor domain, sound singular-factor filtering, paid/free distance
certificate, arbitrary-input witness interpreter and independent column ranks.
The oracle's one-factor literal-image classification and projective/two-factor
test were also checked.

The reviewer flagged that BFS witnesses use execution order while oracle words
use algebraic product order. README now explicitly distinguishes them. Neither
algorithm or frozen core payload was changed for this documentation fix.
It also required that prime-field software evidence remain separate from the
quantified all-finite-field proof. Physical costs and broader algebra targets
remain outside scope.

The root independently read the proof and implementations, and compared every
one of the 216 cost/delta records between the two actual core payloads. Full
normal/optimized, public-byte, cold and hosted replay records are separate
handoff evidence. Static reviewers did not rerun scientific suites. This is
separate AI review, not independent human acceptance or formal verification.

The integration review also identified that only the optimized command initially used -W error. The normal manifest command now explicitly uses that flag, and the root reran the normal warning-strict command before sealing. Earlier core/normal outputs remain preserved unchanged.
