# Actual encoded Gaussian coefficient audit

This scoped source-relative proof establishes directed growth/decay enclosures
and a two-target-ulp endpoint bound for the actual encoded Exponentials routine,
for every P,F>=1, rational 0<=f<=F and nonnegative binary scale. It derives
Taylor early/fixed tails, repeated-squaring width, reciprocal direction and
final rounding from the actual policy. [PROOF.md](PROOF.md) also proves the
actual Axis weight, kernel, wrapped cross-cell and normalized diagonal arguments
fit the prepared bound. Positive rounded weights and global rowgap remain
separate obligations.

An oracle using positive arcsine for pi and alternating decay series was frozen
before observing source outputs. The adapter runs unchanged encoded Axis and
isolated boundary calls, recording raw data under no_decode and decoding only
after execution. Each source interval must contain the entire finer oracle
interval; simple overlap is insufficient. This is independent-algorithm
checking by the same AI-assisted contributor, not independent human review.

## Reproduce

Python3.12, standard library only, from repository root:

```sh
python3.12 scripts/research_package.py --package research/encoded-gaussian-directed-coefficient-audit --check-only
python3.12 -I -B research/encoded-gaussian-directed-coefficient-audit/verify.py --oracle-only
python3.12 scripts/research_package.py --package research/encoded-gaussian-directed-coefficient-audit
```

The two actual source commands have 240-second bounds. Source inputs and the
frozen oracle are authenticated before imports. RESULT.json is mandatory and
compared as complete typed JSON. The original source and nested archives remain
unchanged; source-history and export checks use explicit input base32890bc.

Actual finite replay passed with 19 Axis calls and 10 isolated calls,
including P=1, growth/decay, scale513 and four domain rejections. All
source intervals contain the independent finer intervals.

## Resumed source review

The unpublished two-commit result was resumed on canonical main
`721c03822c421b7f7fcbb2598993b947c4d88419`, priority revision 8, after
[reclaiming its released discussion](https://github.com/CrocSwap/integer-mult-bounds/discussions/3664#discussioncomment-19233742).
All thirteen scientific inputs still match their frozen blobs; the original
revision-7 card and selected-record pins remain historical provenance.
A source review rechecked the encoded Machin signs and tail, Taylor early/fixed
exit, squaring/reciprocal rounding and Axis half-tie/wrapped argument domains.
It found no required scientific change. This is same-contributor review.
The publication still requires both registered actual-source replay modes;
metadata or oracle-only checks do not establish their success.

The overlap refresh covered 341 open PRs, 5,722 discussion records and 8,348
local notes. The normalized host scalar audit uses a different backend;
PR4449's across-cell repair assumes an exponential contract. Neither is repeated
here. The Tensor accuracy package's production-page admission remains separate.
These coverage figures are a snapshot, not a novelty certificate.

## Limits

This audits the encoded physical backend, distinct from the normalized host
Gaussian.exponential scalar audit. No global old-H coefficient composition,
ideal gap, LU, online solve, Core headroom, tensor/CRT or new kappa is claimed.
Original setup, rational arithmetic, scans and storage remain paid; a final
shift by huge sigma costs its scan, not just log(sigma). Oracle and observer
memory are verification overhead.

## Open next questions

Compose actual weight-ratio/cross-cell errors into the production original-H
perturbation bound, retaining positive rounded-weight admission, and bind the
ideal matrix rowgap. This scalar enclosure result alone does not establish it.

## Credit

JoyboyBrian with substantial OpenAI Codex assistance, Apache-2.0. Credit Jose
Manuel/jmbarrancoml PR3851 for the physical producer and original precision
proof, the retained physical-ring Machin runtime and Gaussian lineage, and
the distinct prior normalized scalar-backend audit. Frozen notices remain.
