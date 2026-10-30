# Negative logarithm bounds reach the historical proof producer

**A false numerical certificate and proof-text implication, with a tested
proposed guard. No selected-result failure or new kappa is claimed.**

At canonical main `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, the actual
`scripts/certify.py` helper accepts `certify_network(46, 36, -1000)` and labels
499001 an exponential lower bound. The unchanged `scripts/make_patch.py`
consumer also accepts this input and emits:

```tex
gives $m<e^{-1000}$ and hence $\log m<-1000$
```

Here `m = 46^3 = 97336`. This implication is false. The package reproduces both
the complete helper result and the actual six-file proof proposal without
writing any proposal into `upstream/` or changing the production helpers.

## Missing implication and exact counterexample

For `L > 0`, every term of `exp(L) = sum L^j/j!` is positive. Every finite
partial sum is therefore smaller than `exp(L)`. The helper's successful check
`partial_sum > m` then implies `exp(L) > m`, hence `log(m) < L`. This is the
justification used by the proof producer. It needs the sign premise.

For `L = -1000`, the helper stops after three terms because

```text
1 - 1000 + 1000^2/2 = 499001 > 97336.
```

This partial sum is not a lower bound for the exponential. Independently of
the helper, `exp(1000) = 1 + 1000 + ... > 1`, and the exponential addition
law gives `exp(-1000) = 1/exp(1000) < 1`. Thus

```text
exp(-1000) < 1 < 97336 < 499001.
```

More generally `exp(L) <= 1` for `L <= 0`, with equality at zero, so no such
`L` can upper-bound `log(m)` for these networks, where `m > 1`. The subsequent
tests `eta_b > L * 2^-k` and `eta_c > L * 2^-k` also become vacuous on this
fixture because both actual deficits are positive and the right side is
negative. No floating-point evaluation of an underflowing exponential is
used as evidence. This is an elementary real-analysis argument and exact
rational counterexample, not a formal-kernel proof.

## Tested guard and coverage

[proposed-guard.patch](proposed-guard.patch) adds the necessary `log_bound > 0`
requirement at the start of `certify_network`. The replay verifies the exact
patch text, compiles the proposed source in memory, and calls the real proof
producer against it. The patch is **not applied to production**.

The bounded replay establishes:

- The unmodified helper accepts the negative fixture, and the actual producer
  emits the false implication while returning all six proposal files.
- The proposed guard rejects `-10000`, `-1000`, `-1`, `-1/2` and `0` at the
  helper boundary and before the producer yields its first file.
- All three published positive cases `(h,k,L) = (100,50,20)`, `(100,42,14)` and
  `(46,36,12)` retain exactly equal helper certificates and all proposal text.
  An exact `Fraction(12)` positive input also remains accepted.
- The positive but insufficient bound `L = 1` still fails the original
  exponential comparison; positivity alone does not cause acceptance.
- Altered source bytes are rejected. The recorded receipt is compared byte
  for byte, preserving Boolean and integer claim types.

[RESULT.json](RESULT.json) contains the reproducible helper receipts and
SHA256 digests of all 18 positive proposal files. Authenticated source bytes
are compiled directly, avoiding source-adjacent `.pyc` substitutions.
The script checks every declared live input before running either version.

## Reproduce

Standard-library Python 3.11 or later suffices for the direct audit. The
registered runner uses Python 3.12. From the repository root:

```sh
python3 -I -B research/network-log-domain-audit/verify.py
python3 -I -O -B research/network-log-domain-audit/verify.py
python3 -I -B research/network-log-domain-audit/test_verify.py
python3.12 -B scripts/research_package.py --package research/network-log-domain-audit
python3 -B scripts/research_package.py --package research/network-log-domain-audit --check-only
```

Expected marker: `PASS_NETWORK_LOG_DOMAIN_AUDIT`, including
`production_guard_adopted=0`. Four CLI test groups build a temporary Git-free
copy, verify unchanged normal/optimized replay, and reject corrupted source,
a forged production-adoption receipt and a weakened proposed patch. They also
check that replay leaves the complete copied file tree byte-identical.
Normal replay is read-only; `--emit` prints a fresh receipt. Both registered
commands have 30-second limits. Local registered replay passed with CPython
3.12.14; direct normal/optimized replay and CLI controls also passed with
CPython 3.11.6. This package does not run a selected cold replay, generate a
supplier or alter the frontier.

## Open next questions

Adopt the guard in a separately reviewed successor of the historical numerical
helper, retaining exact replay of its historical consumers. Start with this
two-line patch and the negative proof-producer fixture, and inventory its
live hash consumers before changing any source binding.

One concrete adoption dependency is
`research/rational-containment-performance/SOURCES.json`: its
`scripts/certify.py` row is an immutable `usage: input` pin, also declared by
that package's `VERIFY.json`. A direct source edit fails that old package's
metadata check. `certificates/ternary-side.json` additionally records the same
helper hash. The replay checks both observations. These are verified examples,
not an exhaustive consumer inventory; historical archived source copies and
any downstream receipts must retain their own provenance. This package leaves
all such files unchanged, so a passing audit does not mean production adopted
the guard. New hash bindings need their affected checks and review.

## Scope, overlap and credit

This is an explicitly **changed** `supplier-boundary-audit` task: from the
selected scatter boundary to a historical numerical-certificate/proof-producer
boundary. The seed audits already have follow-ups (#3346 for scatter export,
#3333 for the corrected census); this result does not repeat those checks.
The observed false inequality is useful independently of the selected frontier.
[TASK.json](TASK.json) records the scope change and bounded overlap search.

[SOURCES.json](SOURCES.json) pins base-commit Git blobs and SHA256 values for
the helper, consumer, their upstream files and the named adoption-boundary
records. The catalogue and selected record are historical provenance only.
No conclusion about every supplied parameter, the selected multiplication
construction, hosted CI or independent human acceptance follows from this
audit. Existing positive inputs are not alleged to be invalid.

Credit Douglas Colkitt and repository contributors for the retained numerical
certificates and patch producer, and the authors of the pinned OpenAI integer
multiplication manuscript for the underlying statements. The original source
and license notices remain in place. Prepared for **roger-sato**, with
substantial **OpenAI Codex** assistance in investigation, implementation,
verification and writing. New contribution: Apache-2.0. No independent human
or proof-assistant review is claimed.
