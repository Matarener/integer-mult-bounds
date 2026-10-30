# Validation

Preparation uses Python 3.12.14 on macOS. The verifier uses only the standard
library. Source graph and helper counts are rebuilt from the pinned complete
centre-free word. The proposal copy is authenticated before use.

The scientific checks are exact integral capacity/conservation/cut checks,
literal rank counts, rational inequalities, and six corrupted-certificate
controls. No optimizer is imported during verification. Discovery used the
minimum-flow routine in PR5698; a successful optimizer return is not the proof.

Registered normal and optimized checks, committed-byte comparison, source
export and Git-free replay are recorded after execution below. No hosted CI,
independent human review or proof-kernel acceptance is inferred from those
checks. The checkout is shallow; full-history ancestry is not claimed.

No new native all-column, phase, precision, stock, tape or outer admission is
run. The result is a price rejection even with a free correct ordinary decoder.
It is not a complete supplier or a new kappa result.

## Executed checks

At scientific commit `c4cfb6aac99933fb6dd5454f4ad18b89bc9aa377`:

- Registered normal and optimized checks passed.
- The committed-byte check passed for all 16 package and declared input files.
- Official export creation and archive integrity checks passed.
- The extracted Git-free source passed optimized scientific replay with empty
  PATH and a working directory outside the checkout.
- An actual changed byte in the exported compressed source was rejected by the
  source hash guard before the graph or certificate checks ran.
- `git diff --check` passed.

The first transport attempt treated the exported archive as a directory and
failed before running the verifier. The archive was then checked, extracted
with Python's data filter, and replayed successfully. That packaging error is
separate from the scientific result.

The final canonical refresh still resolves to
`df0137efd35e11b4445734bf612bdd4c7ebc330c`. Final documentation records these
checks; no scientific source, certificate or verifier changes follow them.
