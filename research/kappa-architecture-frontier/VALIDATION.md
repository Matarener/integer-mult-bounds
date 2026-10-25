# Validation and remaining obligations

Executed locally on 2026-10-25, macOS, CPython 3.12.8, standard library.
The default `python3` here is 3.11.11: the registered launcher correctly
refused it before scientific execution. The registered runs below use
`python3.12`. Direct standalone checks also passed under 3.11.

## Executed scientific checks

```sh
python3.12 -B scripts/research_package.py --package research/kappa-architecture-frontier --check-only
python3.12 -B scripts/research_package.py --package research/kappa-architecture-frontier
python3.12 -B research/kappa-architecture-frontier/verify.py --price research/kappa-architecture-frontier/EXAMPLE-PROFILE.json --C 0.0034
```

Metadata/pins and all three registered commands pass serially. The first two
commands freshly reproduce the entire RESULT.json under ordinary and optimized
Python. They verify four complete source histograms, six universal ceiling
gates with lower witnesses and all-larger-saving derivative gates, thirteen
universal ratio-minimum gates, 912 finite mask comparisons, elementary power/log
identities, concavity controls and rejection of a proposed ceiling below an
actual positive P104 witness.

The third registered command performs **14 rejection controls** in disposable
normal/optimized copies. Changed source bytes, a forged Git tree, and a false
admission receipt are rejected end-to-end. The missing-query, missing-idle,
fake-helper and consistently changed local/global-cost cases deliberately
isolate arithmetic from source authentication; they prove the accounting and
old-ceiling gates reject even when the harness bypasses the stronger origin
check. There is no authentication-bypass mode in the accepting CLI.

An additional independently expressed 90-digit Decimal check corroborated 30
power enclosures, including ranks 145 and 65536. Decimal arithmetic is not an
acceptance engine or a proof of its own rounding error.

## Source and claim coverage

ORIGINS.json retains raw Git commits and compressed raw trees, with every object
hash and exact path edge independently checked. All thirteen retained source
extracts are authenticated without Git or network. Standard SOURCES.json pins
canonical-base provenance; pending source heads are bound through the separate
origin proof and are **not** claimed as publication ancestors. No cached PR
branch is required at runtime or for the standard metadata check.

The last canonical fetch still returned
`32890bc5de034ab8fc93ac88ead7279a6a416d04`; the strongest retained P104 PR5551
was still open at `1123635a6f63f23638df9459c994160e5e649d30`. The overlap
snapshot covered 410 open PRs and 4,833 Discussion records with complete remote
pagination. Sparse local note coverage was incomplete and explicitly reported;
relevant existing and pending packages were additionally read through exact
Git objects. This is not an exhaustive novelty or literature certificate.

The full selected/native/outer replays, all-history suites, Lean and Docker were
not run. No finite program here verifies the universal written proof, proves a
native lower bound over all factorizations, or discharges the five inherited
framework assumptions. No hosted CI, independent human review or frontier
promotion is claimed. The initial PR description was prepared locally;
publication status is tracked in README.md.

## Committed transport and offline export

The committed-byte preflight passed on scientific commit
`83d5c58c9556065c95556cfc645cf7bd89fcd44a` for all 28 package files.
The official exporter and archive checker both passed:

```sh
python3.12 -B scripts/check_research_commit.py --package research/kappa-architecture-frontier
python3.12 -B scripts/export_research_package.py export --package research/kappa-architecture-frontier --ref 83d5c58c9556065c95556cfc645cf7bd89fcd44a --output /tmp/kappa-architecture-frontier-83d5c58c9.tar.gz
python3.12 -B scripts/export_research_package.py check /tmp/kappa-architecture-frontier-83d5c58c9.tar.gz
```

The exported archive SHA256 is
`c741d2d29a36fccd43a089e79b0a8ff3ff0b2bc1a6f4ee7ef82393decccefd87`.
Its 28 payload files plus export manifest were made read-only. With empty PATH,
no Git checkout and no network calls, `/opt/local/bin/python3.12 -I -B` and
`-I -O -B` both passed the fresh checker. A source-byte mutation was rejected;
after restoring it, every file hash and mode matched the pre-run census.
No archive container hash determines mathematical equality: the complete typed
scientific receipt is compared independently. Later validation-only prose does
not alter the scientific code, source inputs or expected results at this commit.
