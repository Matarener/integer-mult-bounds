# Verification record

Environment: CPython 3.12.13, Linux x86_64, standard library only, 2026-10-25.
The working base is canonical main `32890bc5de034ab8fc93ac88ead7279a6a416d04`.
The publication refresh retained that main and the reviewed PR5408 head
`256126eeb1607c0bf52996c3d90490f2b786b94a`; relevant guidance, selected record
and predecessor source bytes had not changed.

The following checks passed:

```sh
python3.12 -B scripts/research_package.py --package research/fresh-stage-independent-audit --check-only
python3.12 -B scripts/research_package.py --package research/fresh-stage-independent-audit
python3.12 -I -O -B research/fresh-stage-independent-audit/verify.py
python3.12 -B scripts/check_research_commit.py --package research/fresh-stage-independent-audit --check-source-history
python3.12 -B scripts/export_research_package.py export --package research/fresh-stage-independent-audit --output /tmp/imb-fresh-stage-audit.tar
python3.12 -B scripts/export_research_package.py check /tmp/imb-fresh-stage-audit.tar
```

The committed-byte/source-history check is a transport/provenance check, not
mathematical acceptance. The export was extracted with Python's `data` tar
filter into a fresh directory outside the checkout. Using the absolute Python
interpreter path with `PATH=/nonexistent`, empty `PYTHONPATH`, and `-I -O -B`,
its exported `verify.py` passed without Git or predecessor evaluator imports.
The normal registered replay and optimized Git-free replay both compared the
complete receipt exactly. The package uses explicit exceptions, not Python
assertions, for proof-relevant checks.

The result includes the 5,824-versus-5,826 bare-inverse counterexample,
12,544 exact matrix-polynomial entries, 57,344 signed normalizer entries,
512 four-entry conjugated rows/columns, all 13 saved marker certificates,
all 16 negative-bank bindings, exact surviving coefficients, and the semantic
controls enumerated in README.md. The full all-length proof is the written
argument reviewed in REVIEW.md; the finite certificate is not a proof of
unbounded length by enumeration. No exponentially large tensor was built.

Submission overlap refresh completed at 05:05:08 UTC. It covered 369 open
PR bodies, 4,773 Discussion records and every one of the base's 7,402 tracked
local notes (plus this package's two then-untracked notes). All pagination
and local-inventory coverage fields were complete, with no warnings. The
relevant matches were the original handoff, its source completion, repeated-
stage follow-up #5412, and our own claim/pointer; no competing independent
review appeared. Arbitrary diffs and unpublished work remain outside coverage.

Substantial AI assistance includes separate automated proof review,
independently implemented marker relations, and an adversarial review of the
counterexample and its allowed instruction model. These are not independent
human review or proof-kernel acceptance. No source producer, native/compiler,
outer, selected cold, Lean or Docker replay was run. Hosted CI is separate
from this local record and is reported on the pull request.
