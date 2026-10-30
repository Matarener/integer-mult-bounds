# Whole-word cross-check of RETIMED and DELAYED releases

The published RETIMED and DELAYED words pass a direct exact computation of the
complete local operator, with all 632 live inputs and 91 private buffers treated
as independent symbols. The 723-register forward matrix equals the independently
computed reverse pull-back entry for entry. The dual operator, cleanup boundary,
literal inverse cleanup, frames and invoices also pass for both providers.

This answers [PR3687's Open question2](https://github.com/CrocSwap/integer-mult-bounds/blob/f798838eb8ede4178e94f240e7b7e54b3f80c82d/research/staged-644-660-independent-audit/README.md#open-next-questions)
by **reusing Sagar Thakrar's unchanged independent interpreter**. It is an
additional complete computation, not a new interpreter or the first proof of
retiming on arbitrary dirty states. There is no new kappa or selected-frontier
claim, and no native Gaussian, owner-journal, root or whole-wrapper audit here.

## Sources and existing coverage

The immutable bytes and original paths are in [SOURCES.json](SOURCES.json).

| Object | Pinned source | Coverage here |
| --- | --- | --- |
| STAGED base/extra | Ross Richardson, PR3605 `3efbb5de06a49ffeea6684482f2d3fe48cdca3fb` | Positive control |
| RETIMED base/extra | roger-sato, PR3642 `044d24f12e74f228dd462c07ae2d7f3ea35e2be9` | Complete local word |
| Identical RETIMED copies | Rohan Arun, PR3653 `607a09ff441c79b215a8127a81f4cc70021d0d9b` | Byte identity, hence the same word result; no T488 journal claim |
| DELAYED base/extra | zxv, PR3682 `431e6c6023ef352c41696469de7fb614cd4ded8c` | Separately serialized complete local word; no T360 journal claim |
| Retained `audit_core.py` | Sagar Thakrar, PR3687 `f798838eb8ede4178e94f240e7b7e54b3f80c82d` | Reused without changes |

PR3642 already independently checks two three-register commuting swaps, cleanup
reorderings and the changed frame invoice. PR3682's `reviews/lead1/check.py`
independently checks the crossed scalar commutators, reconstructs the delayed
word and literal cleanup, and derives donor invoices. Its proof applies to full
arbitrary dirty states and implies the inverse-transpose equality. Those results
are predecessors, not missing proofs that this package claims to originate.

PR3687 checks the STAGED words globally. Its author also reports a
[local-only, unshipped RETIMED forward/dual/frame check](https://github.com/CrocSwap/integer-mult-bounds/discussions/3606#discussioncomment-19018866),
explicitly without the pull-back, cleanup, reconstruction or mutants. This
package publishes the complete direct global cross-check for both literal word
families, including the reverse calculation and required-outcome controls.
PR3677's arithmetic on the published retimed histogram and PR3681's inherited
fresh-bootstrap replay address different scopes.

The retained interpreter re-implements Arham Tahir's frame-bill and free-word
contract. Its original notice is preserved. It is independent of the audited
construction/native interpreters, **not independent of all preceding audits**.
No builder, native evaluator, cleanup generator or frame optimizer from the
audited constructions is executed.

## Exact claim and method

In the retained BORROW-WORD contract, live sources, targets and helpers map as
`(x, y, h) -> (x, y+x, h)`; all 91 private buffer symbols return unchanged.
The dual has the corresponding `(x-y, y, h)` live endpoint. Every live input and
buffer is independent, and warps are free invertible symbols. The proof uses
exact rational coefficients and free-word inverse cancellation. It does not
instantiate a native Gaussian or Clifford matrix.

For each of the six complete words, the verifier checks:

- the forward and dual live endpoint, live-input contributions to buffers,
  buffer-to-live leaks and the buffer self-map;
- the full 723 by 723 forward matrix against the reverse pull-back, including
  every free-operator coefficient;
- the forward and reverse cleanup boundary: targets already have their required
  values, designated restored helpers equal their independent inputs and those
  helper inputs do not leak into other live registers;
- the exact reverse-derived cleanup, inherited scalar/access hygiene and full
  chronological binary-frame invoice.

The expected interface comes from the retained semantic contract, not a
construction author's PASS receipt. Complete JSON reconstruction is a separate
control. Starting from STAGED, RETIMED swaps the two adjacent same-pivot releases
at old B591/B641 and raises the delayed donor gate to its next rank4 frame.
DELAYED moves those donor releases before the first pivot producer at old
B1045/B1085, with warp positions reconstructed from chronological events. The
reconstruction keeps all other fields and derives the literal inverse cleanup.
These are the credited local prose recipes, checked against the exact published
words; the global calculation then evaluates those words directly.

| Word | Local profile | Helper widths | Rank mass |
| --- | --- | --- | --- |
| STAGED | `{1:2439,2:726,3:224,4:102,5:20,8:8}` | `{4:26,5:2,6:18,7:52,8:97,9:213}` | 5135 |
| RETIMED and DELAYED | `{1:2437,2:724,3:226,4:102,5:20,8:8}` | unchanged | 5135 |

Each donor640/656 has exactly the local delta `{1:-1,2:-1,3:+1}`; no other
register's invoice changes. [RESULT.json](RESULT.json) records the complete
deterministic findings for both providers and all controls.

## Required-outcome controls

Each changed word has nine controls, 36 in total. For both pivots, omitting the
donor release, flipping its sign, or moving it across its first producer fails
the actual forward endpoint. The literal inverse cleanup is regenerated before
these tests, so a stale cleanup or source hash cannot cause their rejection.

The remaining three controls distinguish operator equality from format and bill:

- Restoring the old STAGED cleanup **passes the complete semantic checks**. Its
  inverse shears commute, but it fails literal reverse-order canonicality.
  This is a format rejection, not an incorrect-operator finding.
- Restoring the old rank2 release frames leaves the operator valid. RETIMED then
  regains the STAGED bill and fails the claimed profile. In DELAYED the donor has
  already climbed, so its old frame fails chronological containment.
- Changing only the declared profile fails agreement with the computed invoice.

The two frame-control outcomes are intentionally different: RETIMED and DELAYED
are different chronological words even though their endpoint and paid profiles
agree. No failure was found in either published positive word.

## Reproduction and source closure

Python 3.12, standard library only. A direct run takes about 12 seconds on the
recorded macOS 27 arm64 / CPython 3.12.14 environment. Run from the repository root:

```sh
python3.12 -I -W error -B research/retimed-word-independent-audit/verify.py
python3.12 -I -O -W error -B research/retimed-word-independent-audit/verify.py
python3.12 -B scripts/research_package.py --package research/retimed-word-independent-audit
```

Expected terminal status: `PASS_RETIMED_AND_DELAYED_WHOLE_WORD_AUDIT`. The direct
verifier recomputes everything and compares the output with RESULT.json; it does
not treat that file as proof input. `--write` deliberately regenerates the
receipt. The registered hook runs the audit normally and under `-O`, with 120
seconds allowed per command. Checks use explicit exceptions.

The package alone can be copied outside Git and replayed by its `verify.py`.
All six compressed source words and the original interpreter are retained.
Before executing the interpreter or parsing words, the verifier authenticates
the exact nine-mapping inventory, its fixed source commits, and each retained
file by byte length, SHA256 and Git blob ID. Missing, duplicate or extra
mappings fail before the interpreter executes. The two PR3653
mappings intentionally refer to the same retained RETIMED files. The immutable
gzip inputs are preserved byte for byte; generated words are compared as full
JSON values, not recompressed container bytes.

Foreign source commits are provenance labels for the retained snapshots, not
Git objects needed at replay. The only generic Git provenance pins are the
canonical main `20ec` selected record and revision 6 task catalogue. The complete
source bytes, not a contributor's cached unmerged Git objects, supply the audit.

## Limits

The binary-frame and BORROW-WORD contracts are inherited. This local calculation
does not certify native Gaussian phases, actual recursive precision or tape,
physical hosting, the 91-buffer allocation, source windows, owner journals,
prefix/outer release, root arithmetic, all-size/compiler hypotheses or a formal
multiplication theorem. Existing full-wrapper evidence is separate; it was not
repeated here. In particular the shared `span(429,30)` entrance residual still
needs the independent native phase audit requested in PR3687 OQ1.

## Open next questions

[TASK.json](TASK.json) gives first steps and blockers for that native audit and
for a consumer-specific journal/window obligation. Read current claims before
taking either; this package makes no universal claim that all such work is open.

## Credit

Sagar Thakrar's PR3687 supplies the unchanged evaluator and explicit handoff;
Arham Tahir supplies its earlier contract/frame-audit lineage. Ross Richardson
supplies PR3605's STAGED words, following dcharb78/PR3133, Marius-Paul Dumitrean/
PR2979, Jeremy Kothe and the credited native word lineage. Credit roger-sato's
PR3642 local retiming proof, Rohan Arun's PR3653 composition, and zxv's PR3682
DELAYED construction and independent local structural argument. Their existing
scientific and source attributions remain unchanged.

Prepared by roger-sato with substantial OpenAI Codex assistance for investigation,
implementation, execution, independent agent review and writing. Review date:
2026-10-19 JST. No human or formal-kernel verification is claimed. Apache-2.0.
