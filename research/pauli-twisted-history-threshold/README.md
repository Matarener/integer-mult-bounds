# Full-Pauli paid history has sharp width threshold two

The standalone one-return-per-owner lower bound survives enlarging the ordinary
alphabet from `{I,X}` to the full phase-complete Pauli group `<iI,X,Z>`.
For targets `(aI+bX)^tensor f` with `ab(a^2-b^2) != 0`, width one costs zero
in this ordinary model; every width at least two requires at least q new
single-row paid returns for q distinct independent input owners. The matching
q-call upper bound requires each requested target operator to be an available
paid primitive. This is a scoped algebraic result, with no new kappa.

The [uniform proof](PROOF.md) accounts for the actual phase factor
`(X Z)^tensor f = X^tensor f Z^tensor f` and
`X^tensor f Z^tensor f = (-1)^f Z^tensor f X^tensor f`.
At even widths, a one-dimensional character detects all requested owners.
At odd widths at least three, the proof uses full ordinary/target module
separation. The one-character argument from the smaller alphabet does not
survive unchanged: its projected ordinary span has dimension two here.

This answers the larger-group next question in
[PR5450](https://github.com/CrocSwap/integer-mult-bounds/pull/5450).
[PR5446](https://github.com/CrocSwap/integer-mult-bounds/pull/5446)'s general
projective-group theorem gives only width at least seven when p=4. Its valid
general proof is not repaired or replaced. At width two the full ordinary
and target spans intersect in dimension two, so demanding disjoint full
spans would miss the sharp bound. [SOURCES.json](SOURCES.json) records exact
immutable proof citations and hashes of the inspected UTF-8 text.

## Verification

```sh
python3.12 -B scripts/research_package.py --package research/pauli-twisted-history-threshold
# Git-free direct commands, from any directory:
python3.12 -I -B /path/to/package/verify.py
python3.12 -I -O -B /path/to/package/verify.py
python3.12 -I -B /path/to/package/check_modular.py
python3.12 -I -O -B /path/to/package/check_modular.py
python3.12 -I -B /path/to/package/test_mutations.py
```

All commands use only the standard library and explicit checks active under
optimization. The first engine uses exact Gaussian rationals and literal
Kronecker matrices, cross-checked against an independent Hamming-distance
entry formula. [RESULT.json](RESULT.json) records 24 complete tensor cases,
all 64 actual phase-group lifts across four widths, 18 full owner/history
checks, 366 scalar identities and 13 boundary controls. The source
square-root-of-X target is included. Owner rows retain an independent dirty
coordinate and check that duplicate owners or a supplied cached target cannot
be charged again. Other controls cover ordinary scalar multiples, singular
targets, zero coefficients, invalid widths and using the even projector at
odd width.

The separate `check_modular.py` imports no primary-engine code. It constructs
the operators directly from bit indices and uses independent modular Gaussian
elimination: 512 complete target cases over F5 and F13, eight phase twists,
eight projectively ordinary controls and 3,072 nonzero separation identities.
These finite-field checks exercise the algebra; they are not physical Q(i)
input tests. Neither executable proves the all-width theorem: that reasoning
is in PROOF.md. Separate peer review and any limitations are reported with
the publication rather than inferred from a PASS marker.

Six additional semantic mutants run in disposable files under optimized Python,
with receipt comparison disabled. They must fail at named predicates when
width-dependent phase is dropped, the odd algebra is made commutative, the
smaller projector is reused, the target coefficient sign changes, singular
targets are accepted, or a cached target is charged again. These controls
change no frozen source and cannot pass merely because RESULT.json differs.

The package has no external executable input and imports no predecessor code.
Public proof citations are not Git-object replay dependencies, so the
predecessors' unmerged commits are not needed for cold execution. The only
Git provenance pins are the task catalogue and selected record at the
canonical base. The official committed exporter therefore needs no
`--input-ref`; it preserves the unchanged package manifest. Source-history
validation checks those declared provenance pins, not the availability or
truth of the cited external proofs. The new argument is self-contained.

## Scope and coordination

The full initial state is independent, with only ordinary observations and
zero scratch. Ordinary coefficients and finite word lengths may vary with
width; paid calls may have feedback and need not commute with ordinary maps.
Each call returns one actual transformed whole-field row at fixed capacity.
The proof explicitly retains every paid output after overwrite or clear.
It assumes neither a free arbitrary matrix coefficient nor multiple outputs
from one call. A common eigenbasis is a proof device, not a free instruction.

No actual parent-cut observation ledger is supplied. Cached paid history,
dependent owners, noninvertible targets, cross-column ordinary operations,
nonlinear programs, multiple-output paid calls and approximate recovery need
different arguments. Physical phase/compiler admission, recursive profiles,
precision, storage, tape cost and the selected frontier remain outside this
result. It does not certify a complete multiplication theorem.

[Discussion5476](https://github.com/CrocSwap/integer-mult-bounds/discussions/5476)
is the canonical investigation. The base is
`32890bc5de034ab8fc93ac88ead7279a6a416d04`, priority revision seven.
The scope change from the historical uniform-transfer card is explicit in
[TASK.json](TASK.json). Initial overlap covered 342 open PRs and 4,736
Discussion records with complete pagination, plus the latest released
handoffs; public cached prose does not exclude unpublished work.
PR5449's general finite history quotient and PR5447's physical input kernels
are separate scopes. No physical application is inferred from either.

## Open next questions

Bind this lower bound to one actual versioned physical cut, including every
cached observation and owner. Without that ledger the standalone hypothesis
cannot justify another caller charge. A further target-family extension needs
one justified physical target and a concrete cost consequence; this proof
does not classify arbitrary Pauli-nonordinary matrices. See TASK.json for the
first steps and blockers.

## Credit

Chris R / Clear1nsight and the retained PR5425/5446 authors supply the
paid-history argument and general projective separation. Ali Romman's
PR5450 supplies the smaller bit-flip specialization and larger-group handoff.
Classical Pauli representation theory, involution characters, tensor-power
separation and the retained native/helper/compiler/analytic lineage retain
their credit. No predecessor implementation is imported.

JoyboyBrian, with substantial OpenAI Codex assistance in proof, exact
implementation, controls and writing. Apache-2.0. No independent human or
formal-kernel acceptance is claimed.
