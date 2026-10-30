# Validation

The package was prepared on canonical main
`de5ec2e7a6074068452f45b1a191b5c72832df4a`, with priorities revision 8.
The selected result remained0.00310045. The source PR5751 is pinned at
`8483f9a679d06c1e270141dbc686a7e76e7a7522`.

The public Discussion and open-PR checks separated the retained-copy work from
the paid-meeting construction, R22 block composition and noncommuting caller work.
The overlap tool also searched its cache. Its remote snapshot was from
October 26 at 16:51UTC; the sparse local note inventory was incomplete.
No-match results are not a novelty certificate.

Python 3.12.13 on macOS was used. Replay needs only the standard library.
Discovery used exact integer-capacity graph cuts with PyMaxflow 1.3.2. Discovery
choices are stored in PLAN.json; the optimizer is not part of the proof replay.

The registered normal and optimized commands check all retained output fields.
The completed commands and their results are below.
The full-history preflight is not claimed in this shallow checkout.
Independent acceptance and hosted scientific CI are not claimed.

## Completed scientific checks

```sh
python3.12 -W error -B research/p104-retained-native-copy/verify.py --write
python3.12 -B scripts/research_package.py --package research/p104-retained-native-copy --check-only
python3.12 -B scripts/research_package.py --package research/p104-retained-native-copy
```

The primary replay passed. The registered normal and optimized replays both
passed and reproduced every WORD, WITNESS and RESULT field. Expected markers:
`PASS_P104_RETAINED_NATIVE_COPY_KAPPA_00312192127` and
`PASS_REGISTERED_RESEARCH_PACKAGE`.

The checks cover 789 public and dirty owned input columns, 622,521 coefficients,
2,925 native maps with exact phases, 1,118 helper normalizers and 208 main adapters.
They check all 18 caller occurrences, two rational moment engines, completion,
compiler, 54 strict outer inequalities and four functional checks. Nine explicit
word/caller/invoice controls and the native phase control are rejected.

The exact raw crossing is (0.00312192130450, 0.00312192130451). Certified upper
bounds for alpha, gamma and delta are respectively
0.999999999969984119802576312583,
0.975826192284422696653482356627 and
0.949234740902898217233390415077.

GitHub Markdown rendering preserves the README title, four headings, code
block and source links. Canonical main was refreshed before publication.
Its selected record and revision-8 guidance were unchanged.

## Publication checks

The committed-byte and export commands are:

```sh
python3.12 -B scripts/check_research_commit.py --package research/p104-retained-native-copy
python3.12 -B scripts/export_research_package.py export --package research/p104-retained-native-copy --ref PUBLICATION_COMMIT --output /tmp/retained-native-copy.tar
python3.12 -B scripts/export_research_package.py check /tmp/retained-native-copy.tar
```

For the portable check, extract that exact archive into a new directory. Make
all extracted files and directories read-only. Run the direct verifier with
an absolute Python path, `-I -O -B`, an empty PATH and no Git directory.
Compare every payload hash and file mode before and after the run.
The PR records the publication commit, export hash and result of this later check.
It also records the current hosted CI status. These publication checks do not
establish independent scientific acceptance.
