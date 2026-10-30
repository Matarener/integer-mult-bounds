# Exact P104 coefficient reduction; no new kappa

This package removes **117 events** from the full word of
[PR6144](https://github.com/CrocSwap/integer-mult-bounds/pull/6144), at
`5ec9b6dafc1ec54e2c0ca0771e8ed032f7888417`. It removes 114 ADDs and one unused
INIT/COPY/CLEAR lifetime. The word falls from 22,818 to 22,701 events.
All 3,449 native MOVE records remain identical and in the same order. All public boundaries and productive targets remain identical.
**The complete recursive invoice is unchanged. There is no kappa gain.**

The contribution is an exact source edit, a formula for changes to several
scalar coefficients, and a check of the complete endpoint. The formula includes
the effect of an earlier change on a later source value. A derivative relation
alone does not establish that the finite edit is valid. See [PROOF.md](PROOF.md).

Three passes give 28 compatible coefficient edits. Two further discovery
passes made no change. The result uses the original 770 public inputs and 29
owned register labels. Owned lifetimes fall from 31 to 30; peak occupancy stays
13. Every COPY still has a zero owned destination. The removed lifetime had
no reader and no native MOVE.

## Replay

Use Python 3.12 and its standard library:

```sh
python3.12 -I -B research/p104-common-response-resynthesis/verify.py
python3.12 -I -O -B research/p104-common-response-resynthesis/verify.py
python3.12 -B scripts/research_package.py --package research/p104-common-response-resynthesis
```

The default replay is read-only. It authenticates the retained source bytes,
applies every guarded edit, checks frames and ownership, and checks all 799
input columns against the required endpoint. A separate transpose checks the
same endpoint in the other direction. It then compares the native stream,
helper profiles and all boundary data. The [receipt](RESULT.json) records the
counts and rejection controls. [CERTIFICATE.json](CERTIFICATE.json) records the
three passes and the hash of the reconstructed final word.

The source word uses the archive manifest format. The verifier checks its
SHA256 and Git blob ID. These bytes matched the exact PR6144 head locally.
The hosted checkout cannot resolve that fork-only head. Thus hosted replay
checks the retained bytes, but does not check their publication ancestry.

The registered result does not depend on a solver or on the discovery files.
The optional `--write-result` argument writes the mathematical receipt; it does
not write or change the retained input.

## Cost result and limits

The local paid profile remains
`{1:2215,2:457,3:496,4:99,5:164,6:8,7:9,8:1}`.
The local helper profile remains
`{1:14,2:8,3:4,4:107,5:14,6:2,7:9,8:19,9:385}`.
Thus the complete PR6144 caller has the same recursive paid and target
histograms if this word replaces its local word. This equality follows from
the unchanged interface and native stream. It does not require a root search.

Discovery also tested new scalar gates between fields already in one frame.
Four of seven resulting candidates passed exact endpoint checks; none gave a
paid-cost gain in the tested frame assignments. The frame solver reported zero
gain for each coefficient pass. Those modular catalogs and rounded solver
results are local-only discovery evidence. They are not part of this package's
certificate, and they do not prove an optimum over other circuits or frames.

No new native map or phase identity is asserted. The original native maps and
caller remain predecessor premises. This replay does not run the old complete
caller, precision, compiler, BIT or outer suites. It does not establish a wall
clock speedup, independent scientific acceptance or a multiplication theorem.
The five framework assumptions remain. The donor's requested large kappa
improvement remains unmet.

## Coordination and credit

The base is canonical main `3f0152a32eeebac0df11946dbd50cabe5a7f7839`.
The selected frontier is unchanged. The
[canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/5600#discussioncomment-19209322)
records the scope and its release. The complete overlap cache covered 312 open
PRs and 5,854 Discussion records through October 28, 2026 at 23:34 UTC. Later
live checks read PR6167, PR6168 and Discussions 1166, 1167, 5593 and 5645.
Unpublished work and arbitrary diffs remain outside that coverage.

[PR6167](https://github.com/CrocSwap/integer-mult-bounds/pull/6167) has the newer
conditional claim 0.003128645. Its retained-operand edit is separate. This
package does not claim that gain and does not claim composition with it.

DreamingOfClouds retains credit for PR6144, including Claude Opus 5.5
assistance. PR6030, PR5907, PR5827, PR5811, PR5802, PR5786 and the earlier P104,
native, helper, caller, compiler and BIT contributions retain their credit.
See [NOTICE](NOTICE). New work is by Ali Romman with substantial OpenAI Codex
assistance; no subagents. New work is under Apache-2.0.

## Open next questions

A new coefficient edit must remove or change an actual paid native path, or
change a legal productive target, before another construction round is useful.
Start with an explicit different gate topology and a complete signed invoice.
Then check the finite coefficients, every input column, ownership and native
phases. [TASK.json](TASK.json) records this question and the missing obligation.
