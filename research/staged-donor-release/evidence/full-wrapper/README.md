# Default full-wrapper execution

The default `full_replay.py` command passed end to end during PR preparation on
2026-10-18. Both changed native providers and all seven admission stages ran
fresh, including preparation and the entire original release. The scientific
wrapper and inputs are unchanged from commit
`74afc9ff5cb437d3112c6279216d10250775cd98`; `PINS.json` binds their exact hashes.
The older execution, repair and preparatory reuse remain preserved under
`../complete/` and are not replaced by this run.

`RESULT.json`, `STAGES.json` and `ENVIRONMENT.json` are readable terminal records.
`RECEIPTS.tar.gz` retains the nested native, discovery, verification, strict
admission, invoice and outer records plus stage logs. Every member is listed
with its SHA256 in `PINS.json`. These records can be inspected without Git or
rerunning the heavy pipeline. The package's bounded verifier authenticates the
archive, exact endpoint, source bindings and complete stage coverage; it also
rejects inconsistent freshness, missing-stage, native-source and endpoint
receipts. This checks stored evidence, not a fresh heavy replay.

Reproduce the full run with the Python and dependency versions in
`ENVIRONMENT.json`, from the repository root and with a fresh output directory:

```sh
python3.12 -B research/staged-donor-release/full_replay.py --work /tmp/fresh-staged-release
```

Authenticate the retained run with the standard-library checker:

```sh
python3.12 -B research/staged-donor-release/wrapper_evidence.py
```

The wrapper still reuses authenticated unchanged parent/native ancestry.
A no-reuse retained-parent cold run and hosted CI have not been run. This is
later execution evidence, not a new independent review or a discharge of the
inherited all-size and theorem-level assumptions. The prior independent reviews
remain scoped to their exact recorded commits.
