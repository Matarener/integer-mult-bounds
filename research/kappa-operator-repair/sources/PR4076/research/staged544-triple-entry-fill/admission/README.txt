Complete admission for the staged-entry derivative (helpers 608, 609, 600)

full_replay.py extends PR3945's admission/full_replay.py. It downloads (or takes via --archive) the pinned
predecessor archive (research/staged544-producer-return/REPLAY-INPUTS.tar.gz at fa041037, 756 members checked).
It then reconstructs PR3945's exact 666-file closure, asserting PR3945's manifest
3d2ee0175b0cd8aec80c12fef82c2da3a3a54785ca9113140762fd5c41979608, using PR3945's own terminal applier and review
and its three literal source patches (byte-identical copies in pr3945/, see pr3945/SOURCES.json).

On top of that closure it makes six additions:
  new/borrow/staged_entries_applier.py, new/borrow/staged_entries_review.py,
  new/borrow/staged3/PRE-{base,extra}.json.gz (PR3945's words),
  new/borrow/staged3/RECORD-{base,extra}.json (our literal records).

It then makes these modifications:
  - the BORROW-WORD-43 words are replaced by ours;
  - new/BORROW-PROVIDERS.json gets the new widths and profiles;
  - new/rebuild_borrow.py gets one appended chain step;
  - terminal_review.py now reads PR3945's words from staged3/PRE;
  - verify.py gets one added review.

The result is a 672-file closure. The inherited admission engine gets exactly PR3945's adaptation: source-profile
commit, manifest and file count, plus frozen-SPEC mutation counts. Both native providers run fresh. The complete
admission then runs on owner/FILL.json.gz, covering owners, parent lift, rebind, discovery (bind, emit, audit, invoice,
assembly, admission, bit, independent), outer ledger and independent outer check, and release.

Memory: the discovery audit (audit_allcold with mutation controls) needs about 6 GB per shard, and --jobs sets the
shard count. The recorded run used --jobs 1 on an 8 GB Linux host (Python 3.12, numpy, scipy, sympy 1.14.0,
mpmath 1.3.0). Runs on 6 GB, and with 4 shards on 8 GB, were killed by the memory limit during audit. That is an
environment limit, not a check failure.

authenticate.py checks the retained evidence in evidence/ against the package files with the standard library only.

The mathematical claim remains conditional on the inherited uniform/all-size, source/hosting,
precision/tape/recovery, analytic and BIT obligations. No formal kernel or independent human review is claimed.
