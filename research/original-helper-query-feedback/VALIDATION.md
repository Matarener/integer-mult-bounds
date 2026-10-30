# Validation record

The publication base is `32890bc5de034ab8fc93ac88ead7279a6a416d04`.
The scientific source payload and PR5388 bank bytes match the saved experiment.
No predecessor input was edited.

## Executed checks

Python 3.12.14 on macOS ran the following commands successfully:

```sh
python3 -I -B research/original-helper-query-feedback/verify.py --emit
python3 -B scripts/research_package.py --package research/original-helper-query-feedback --check-only
python3 -B scripts/research_package.py --package research/original-helper-query-feedback
```

The registered replay ran both normal and optimized wrappers. Both produced
`PASS_UNCODED_FORWARD_EARLY_QUERY_FEEDBACK` and matched the complete typed
`RESULT.json`. The metadata command produced
`PASS_PACKAGE_METADATA_AND_PINS`; that token is not mathematical acceptance.
The scientific replay was also run under Python 3.14.7 before final receipt
and invoice packaging.

A separate temporary export contained the nine scientific package files and
nine declared live inputs. It had no Git directory, an empty PATH and read-only
files and directories. The absolute Python 3.12.14 interpreter ran the verifier
normally and with `-O`. Both passed, and all 18 file hashes stayed unchanged.
[PORTABILITY.json](PORTABILITY.json) records the two executions. This export
preceded addition of these validation records; the scientific files are the
same files used by the registered replay. No network or external executable
was needed by the direct verifier.

A separate complex-geometry AI worker reviewed the three feedback identities,
the induction for reused source/destination coordinates, operator-valued source
substitution and the `R S(Q) xi` return. That was a written/code review, not an
additional execution or independent human review. It found no issue within
that scope.

The committed-byte preflight and committed-package export integrity check also
passed. The strict `--check-source-history` option stopped because this shared
repository has shallow Git history. It did not report a source-byte mismatch.
The package commit has the declared base as its immediate Git parent, and all
live inputs are already present at that base. The standalone export tests above
do not require Git history. Full-history preflight remains unrun.

## Coverage and omitted checks

The replay checks all 632 original columns, 226 arbitrary owned columns,
112 replacement cuts, 358 source first departures, five overlapping shears,
the empty sequence, 112 exact-phase query equations, 32 completion equations
and seven semantic mutations. The inherited Clifford module is compiled with
assertions active in both wrapper modes; the new checks use explicit errors.
The completion invoice is reconstructed from the source ranks and compared
with the shared signed-invoice checker. It is uniformly worse for every
strict power tariff in the declared no-feedback comparison.

The native physical adapter implementation, all-width implementation theorem
and source cost convention remain inherited. The finite replay does not prove
a backward interface, complete caller, terminal decoder, autonomous target
credit after feedback, precision/compiler funding, BIT transfer or a new kappa.
No selected-construction cold replay, hosted CI, Lean proof or Docker build ran.
