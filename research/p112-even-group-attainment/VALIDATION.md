# Validation and reproduction limits

Canonical base `6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority revision 6,
was refetched before submission with no changed guidance or selected record.
The contribution is confined to this new research package.

Local ordinary and optimized registered checks pass on CPython 3.12.15,
Darwin arm64. The registered command is:

```sh
python3 -W error -B scripts/research_package.py --package research/p112-even-group-attainment
```

It runs six commands, with a 120-second limit each. Both complete proof checks
and the controls are rerun with `-O`. Markers are
`PASS_P112_TWO_FRAME_OBSTRUCTION`, `PASS_P112_INDEPENDENT_REPAIR`,
`PASS_P112_REPAIR_CONTROLS` and `PASS_REGISTERED_RESEARCH_PACKAGE`.

The separate algorithms exclude every one of the 78 repair domains. Primary
per-case counts are preserved in RESULT.json. The separate cover search visits
9653 unique states in total, at most 985 in one case, and exhausts its worklists
normally. No capacity timeout is interpreted as an exclusion. Controls cover
36 complete small powerset/minimum-cover domains, nine explicit rejection
fixtures and two direct complementarity fixtures.

A Git-free filesystem export containing this package and only its single live
selected input passes the same six direct commands on CPython 3.14.8. This export
uses no source repository, pending commit, solver or network service. Five
actual optimized CLI controls reject source-byte corruption in each checker,
a false result receipt and omission of a retained certificate pin in each
checker. Every mutation is restored before the export's final replay. The
source export was also checked byte-for-byte against the canonical GitHub API
at both exact public source commits.

Ruff 0.17.1 checks E,F,I,UP,B,C4,SIM,RUF and formatting, with no cache:

```sh
ruff check --no-cache --target-version py312 --select E,F,I,UP,B,C4,SIM,RUF research/p112-even-group-attainment
ruff format --check --no-cache research/p112-even-group-attainment/verify.py research/p112-even-group-attainment/independent.py research/p112-even-group-attainment/controls.py
```

Exact publication-byte/source-history preflight is required before pushing:

```sh
python3 -B scripts/check_research_commit.py --package research/p112-even-group-attainment --check-source-history
```

The declared Git source pins resolve to the main ancestor. Both pending
predecessor certificates are committed package bytes authenticated by
SOURCE-EXPORT.json, rather than imports from the shared object cache. The
publication preflight covers declared Git pins; the separate canonical API
byte check and Git-free replay establish the retained-certificate path.

The larger construction pilots are deliberately outside mathematical evidence.
The compact coloring run returned UNKNOWN; the stopped set-cover run and
bounded swap search produced no witness. The three-frame repair pilot covered
225 of 286 cases, returning 92 unproved UNSAT statuses and 133 unknown statuses.
Those 92 reports, the 61 unrun cases and every unknown remain uncertified. No
three-frame or global fifteen-group exclusion follows.

The selected full cold replay, new physical native calls, full invoice,
hosting/restoration/precision admission, all-size/compiler implications, both
suppliers, outer transfer, independent human review and proof-assistant
verification are unrun or outside scope. No selected-frontier change is made.
