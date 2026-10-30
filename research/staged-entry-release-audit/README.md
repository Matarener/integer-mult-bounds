# Rank-two boundary for three staged entries

Independent mathematical audit of Rohan Arun's pending [PR4076](https://github.com/CrocSwap/integer-mult-bounds/pull/4076),
head `9744f9df268590295a9872b1952c695a678192b9`. Both providers' three delayed
entries have the same exact register-coefficient rank-two pre-cleanup defect:

```
δ417 = (h608+h609)/2       δ565 = h600/2
δ610 = −h608−h609         δ602 = −h600
```

Every other row is unchanged. Inputs are original independent helper fields.
All eight subsets compose additively without cross terms. All sixteen complete
subset/provider programs realize y←y+x and return all91 arbitrary dirty private
fields. The source prefixes are **not** equal; the generated projected cleanup
is essential. Partial subsets are algebraic diagnostics, without frame admission.
For D-dimensional fields the full defect rank is2D; no physical two-role saving
or new κ follows.

This adds a sparse staging/composition certificate to PR4076's binary ledger
and retained Sagar Thakrar/roger-sato interpreter replay. No predecessor Python
is imported. See [PROOF.md](PROOF.md) for the exact identity, algorithm soundness,
cleanup boundary and limits, and [CERTIFICATE.json](CERTIFICATE.json) for all subsets.

## Reproduce

Python3.12, standard library, from the repository root:

```
python3.12 -B scripts/research_package.py --package research/staged-entry-release-audit
```

Expected markers: `PASS_STAGED_ENTRY_RANK_TWO_DEFECT` (2 providers,16 subsets,
723 full-state blocks,28 rejecting controls), `PASS_NONCOMMUTING_STAGING_ORACLE`
(6 complete assignments) and `PASS_STAGING_ALGEBRA_CONTROLS` (6 groups), followed
by `PASS_REGISTERED_RESEARCH_PACKAGE`. Default checks write no package inputs.
The exact certificate can be regenerated explicitly with `verify.py --write`.

Exact canonical base: `bb4bccbf42844d2801487450727c2f63e10d1d0f`; priority6;
OS-random assignment seed69, adversarial audit track. Four source words are
retained byte-for-byte and checked by SHA256/Git-blob pins before execution.
`PINS.json` records their actual PR4076 paths/commit and byte/Git-blob identity.
`SOURCES.json` authenticates the committed local freeze at d39e1a8d, which is
in this publication history. The pending predecessor head is not an ancestor
of this branch; source-history preflight does not certify its ancestry. Original
source/blob equality was checked against the fetched exact PR head; replay uses
the retained authenticated bytes and does not fetch GitHub. The certificate does
not import or trust that PR's report histograms or checker outputs.

Overlap: refreshed latest100 open bodies, another100 updated bodies, previous
772-open-body snapshot,80 handoff comments and recent4075/4076 comments. Broader
Discussion/closed/code coverage is partial. The final refresh also found #4085 receiver sharing on helpers672/676; that is
a distinct construction, and this audit does not validate its updated claim.
Existing tensor tests caused that
candidate to be dropped. #3949 supplies staged-entry identities; #3969 checks
an older terminal/owner bridge; #3987 checks native phases; #3994 checks older
word error reserves. None is represented as evidence for the new defect factors.

## Open next questions

The smallest useful follow-up is an actual new entry with a nontrivial coupled
release: compute its boundary factors, require exact target/restored projection
and regenerated dirty cleanup, then price frames, source access and the complete
owner/numerical bill before native expansion. This package admits no frame,
owner fill, precision or multiplication supplier. Structured question: TASK.json.

## Credit

Rohan Arun/PR4076 supplies the actual new words and triple-entry construction;
Ross Richardson/PR3605, dataisfire/PR3734 and ChaloupeMusic/Erwan Secousses/PR3949
supply staged-entry mechanisms. Dugongue/PR3945 supplies terminal-width5 words;
Sagar Thakrar/PR3687, roger-sato/PR3693 and Arham Tahir supply preceding exact
semantics and contract work. The source/compiler and cleanup lineage remains
credited. Full retained PR4076 NOTICE.md is included as SOURCE-NOTICE.md.
New defect factorization, independent exact implementation, subset checks and
controls by Tekalign (`tekuuu`) with substantial OpenAI Codex assistance.
Apache-2.0; no independent human or formal-kernel review is claimed.
