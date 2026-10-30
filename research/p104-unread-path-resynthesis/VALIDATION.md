# Validation

Python 3.12. The primary complete replay passed with --write. It regenerated
WORD.json.gz, WITNESS.json and RESULT.json. The registered normal and optimized
commands also passed. Every mathematical check and rejection control in
verify.py ran in each mode.

```sh
python3.12 -B scripts/research_package.py --package research/p104-unread-path-resynthesis
python3.12 -B scripts/check_research_commit.py --package research/p104-unread-path-resynthesis --check-modes
python3.12 -B scripts/export_research_package.py export --package research/p104-unread-path-resynthesis --output /tmp/p104-unread-path-export.tar
python3.12 -B scripts/export_research_package.py check --check-inputs /tmp/p104-unread-path-export.tar
```

The scientific commit is 92e5b3dacbcadd585e68e6fc7b63665471513784. Its
23 package files pass the committed-byte and mode check. The official
export and input-integrity checks pass.

A separate read-only, Git-free export passed under -I -O -B with empty PATH
in 136.953 seconds. All 24 exported files, including the export manifest,
kept their bytes and modes. Its archive SHA256 is
`e09abfb69287950597fa024f68e256232929dc485d2119eae5bc10447fb22acc`.
This run checked the actual complete operator, native, physical caller,
price, compiler and outer calculation. It did not only inspect saved PASS
text. The publication update changes this report, the overlap timestamp
and attribution text; the complete runtime and all mathematical inputs
and receipts are unchanged.

Full-history ancestry mode was not run in the shallow checkout. Hosted
scientific CI and independent human acceptance are separate. The shared
priority-8 assignment-test failure is known from predecessor PRs; this
package does not modify the shared tests or claim that hosted replay passed.
