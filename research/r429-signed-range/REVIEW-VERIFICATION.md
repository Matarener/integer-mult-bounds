# B04 source binding and verification review

**Disposition: pass for the stated fixed-witness and conditional scalar
claims, at the version identified in `CORE-SNAPSHOT.json`.**

This review covers the fixed signed R429 witness, its authenticated historical
replay, the two new independent checkers, and the complete receipt acceptance
mechanism. It was prepared separately with substantial OpenAI Codex assistance.
It is neither human acceptance nor a formal-kernel proof.

The reviewed package is bounded to one concrete 23-sign change among 47
quotient ADDs and the stated consequences of its fixed prefix and suffix.
The local integer interface, binary interface, scalar range and scalar defect
model are distinct claims. No sign search, native rounded supplier, general
sign optimum, improved paid rank profile or new multiplication exponent is
established.

## Source and receipt boundary

`verify.py` authenticates each registered input before returning its bytes.
Historical replay parses those same bytes and compiles only the explicitly
named top-level function definitions. The original imports, filesystem
constants, entrypoints and search loops are excluded. The selected definitions
were inspected: none uses a decorator or default expression to reintroduce
excluded original execution. Dependencies are explicitly supplied standard
library values and preceding authenticated functions. Function multiplicities
are checked, so missing and duplicate definitions or duplicate requests fail.

Compilation uses `dont_inherit=True, optimize=0`. Assertions inside extracted
functions and their nested functions remain active under an optimized parent
interpreter. New independent programs are executed from their authenticated
source bytes with `__name__="authenticated_review"` and their actual package
source path. Their main guards do not run during loading; the wrapper explicitly
calls `main` with declared inputs and a fresh external temporary output.
These programs import no producer implementation. There is no frozen module
import or bytecode-cache selection path.

Compression preserves two different bindings where an original uncompressed
input was wrapped for storage: the manifest authenticates compressed bytes and
`ORIGINS.json` separately authenticates the decompressed original bytes.
Neither a transport hash nor an unchanged JSON value alone substitutes for
the original byte binding.

The fixed scientific comparison set consists of:

1. `frozen/candidate/RESULT.json`;
2. `frozen/candidate/GROWTH.json`;
3. `frozen/historical/REPLAY.json`;
4. `frozen/reviews/integer/CHECKS.json.gz`;
5. `frozen/reviews/range/CHECKS.json.gz`.

Each fresh result is compared in full by canonical JSON serialization. This
retains integer/Boolean/float distinctions, list order and every nested field.
It does not select a convenient subset or compare only a status. Each stage
also requires its exact expected comparison set. A missing fixed receipt
fails; replay writes only a fresh temporary result and never regenerates the
fixed evidence. Root-level manifests, scripts and documentation are covered by
the separate core snapshot and repository publication checks.

## Mathematical coverage inspected

Both words have 651 public inputs: 111 sources, 111 targets and 429 arbitrary
dirty helpers. The private coordinate starts at zero. The independent integer
checker evaluates every public coefficient in both orientations and both
roundtrips. It reconstructs the binary source map from the original R438 word,
checks exact MOVE containment and rank, preserves physical endpoint frames,
and enforces immutable copied-source and private-snapshot lifetimes.
ERASE requires literal equality to the original unchanged copied value.

Thus the integer conclusion is the actual block map
`(x,y,h) -> (A_Z x, y+T_Z x+E_Z h, h)`, with private return and literal inverse.
The even helper block need not vanish and `T_Z` need not equal `A_Z`.
The binary reduction is separately the specified
`(x,y,h) -> (A x, y+A x, h)`.

The all-sign extension uses an exact forward prefix–quotient–suffix certificate.
The 47 ADD quotient lies on nine coordinates. Its fixed prefix reader `B`
contains no target or dirty columns and has an identity pivot minor; its
fixed suffix transfer is supported only on the nine source rows and three
target rows. The private coordinate is closed at both cuts. Consequently
`Delta A = U Delta Q B`, `Delta T = P3 L Delta Q B` and `Delta E = 0`.
The forward source and target rank bounds are at most 9 and 3 for the same fixed
47-gate sign family. The current determinant `det(Delta Q)=1024` and the
checked minors give exact forward ranks 9 and 3 for this witness. This is a written
linear-algebra implication of finite exact transfer data; it is not an
enumeration of all `2^47` assignments or an optimality theorem.

The range checker independently reconstructs the full sparse prefix rows and
all suffix destination columns of both actual 651-input words. Scalar sign
witnesses attain the local prefix maxima and the completed-output defect
constants. The controller uses the selected 1,499 ADD source code and its
literal inverse. Its historical 6,372-gate code has a different binary endpoint
and is not substituted into the range calculation. The abstract schedule is
checked on all eight formal bank columns in the free noncommuting polynomial
algebra over GF(2).

Every ordered controller factor and the current encoded helper magnitudes
enter the scalar recurrence. These are conditional coefficient upper bounds.
The exact atomic defect constant is
`max_r sum_i |(S_i e_dst(i))_r|`, which differs from summing per-event maxima.
COPY and ERASE use their stated linear assignment extension, including
`private <- 0` at ERASE. Setting the ERASE defect to zero does not prove
physically legal rounded cleanup. Native child interiors, error support,
perturbed prefixes, input lattices and finite-precision storage remain separate.

The comparison is mixed: forward prefix range and forward defect amplification
increase, while the inverse quantities decrease. The inverse MOVE/COPY
aggregate remains 1,239. Only the specified conditional controller range bound
and its stated terminal code extension improve; no global precision admission
follows.

## Controls and resolved review finding

Compact controls load the actual verifier and original selected functions.
Disposable fixture files live in external system temporary directories. They
cover changed and missing source, function selection, direct and nested
assertions, whole-module assertion retention, original-main exclusion,
compressed/original byte binding, typed receipts, list order and nested
omissions. The full five real receipts are positively compared, then each
undergoes a nested value mutation and omission.

The arithmetic control authenticates the original source first and executes
a noncommuting two-ADD source word on all 111 source columns. Replacing inverse
subtraction by addition reaches and fails the real
`signed source-code literal inverse` gate. It is not a hash rejection.
Removing that named gate makes the control fail because the faulty computation
is then accepted. An analogous check-deletion control tests the complete
receipt comparator. Unexpected acceptance is raised outside the caught
rejection branch.

Review found that the initial integer negative-control helper accepted any
`ValueError`. A failure while preparing a stale snapshot could therefore have
been counted as the intended ERASE rejection. This was corrected before the
final receipt: each exception control now requires its exact intended semantic
error. The compact controls positively check this helper and verify that an
unrelated exception fails its contract.

The integer checker also supplies actual-word faults for stale COPY state,
live source mutation, private mutation, wrong MOVE rank, inverse-sign error,
changed quotient sign, failed helper restoration, dirty-source contamination
and omitted compensation. The range checker supplies actual-event controls
for the adjoint direction, suffix order, COPY influence and error signs.
All mathematical mutations are applied after input authentication.
The reviewers' receipts identify the corresponding witnesses; transport
authentication failures are not counted as mathematical controls.

## Evidence and remaining integration boundary

`CONTROLS.json` records fresh compact execution under normal and optimized
CPython: 34 intended rejections and two check-deletion sensitivity tests in
each mode. Both runs positively compare all five fixed scientific receipts.
`CORE-SNAPSHOT.json` identifies the exact final package files inspected and the
control receipt digest. The compact suite deliberately does not rerun
the historical search or either complete independent mathematical replay.
Those full runs belong to their independent reviewer receipts and to the
parent's registered package verification.

The snapshot binds the integrated independent sources, receipts, documentation
and registered command manifest. Any change to those bytes requires a scope
refresh; receipt files that contain the snapshot itself are explicitly excluded
to avoid circular hashes. Repository source-history checks, read-only Git-free
export, publication and hosted CI remain separately reported by the parent.
