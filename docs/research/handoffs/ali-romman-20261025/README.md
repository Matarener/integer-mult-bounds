# October 23–25 contribution handoff

This record closes the publication work for two research sequences and the
later native-history and odd-E8 investigation. It preserves the result
links, stop decisions, and the last small retained-history test.

No complete kappa increase was obtained in this investigation. At canonical
main `5e0052ca0aa3036a3afa8b0438927377c8d97d53`, the
[selected record](https://github.com/CrocSwap/integer-mult-bounds/blob/5e0052ca0aa3036a3afa8b0438927377c8d97d53/certificates/selected-result.json)
is `605457647/200000000000 = 0.003027288235`. Its five framework assumptions
remain. This handoff does not change that record or claim a new supplier.

## Delivered results

The [first sequence](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19148608)
contains ten results: one PR and nine self-contained Discussion proofs and
checks. The
[second sequence](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19151557)
contains ten results, six of which have focused PRs. Those indexes keep the
scope, proof, source credit, and verification limits of each result. A later
publication of the same result is not counted as another result.

Three later PRs supply native-map cancellation, a same-paid native inverse,
and an odd-E8 decoder with a scoped lift obstruction. The following ten PRs
were merged by maintainers before this handoff. All ten final-head hosted
runs report success. No unresolved inline review thread was present at the
closeout check.

| PR | Result | Exact package | Hosted check |
| --- | --- | --- | --- |
| [#5255](https://github.com/CrocSwap/integer-mult-bounds/pull/5255) | Sharp graph-support inverse norm | [Source](https://github.com/aliromman/integer-mult-bounds/tree/d63d8848442acc0bdc7b62578e12726c530af3fa/research/sharp-banded-resolvent) | [Success](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/39968325269) |
| [#5321](https://github.com/CrocSwap/integer-mult-bounds/pull/5321) | Lower local inverse-code tape bound | [Source](https://github.com/aliromman/integer-mult-bounds/tree/85b70f45078dfa9dc1f865b0fd0c4e8055ddd540/research/factored-code-tape) | [Success](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/39993985934) |
| [#5322](https://github.com/CrocSwap/integer-mult-bounds/pull/5322) | Inverse-pair error cancellation | [Source](https://github.com/aliromman/integer-mult-bounds/tree/38065821a76108dc512391b124ffb7b64feed93b/research/physical-pair-error-transfer) | [Success](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/39998296588) |
| [#5323](https://github.com/CrocSwap/integer-mult-bounds/pull/5323) | Exact rounded-code recovery state | [Source](https://github.com/aliromman/integer-mult-bounds/tree/f9c722011c61779b1b79e9e38c0aa749b933000d/research/inverse-code-recovery-tags) | [Success](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/39998305100) |
| [#5325](https://github.com/CrocSwap/integer-mult-bounds/pull/5325) | Restored Tensor error join | [Source](https://github.com/aliromman/integer-mult-bounds/tree/bea42af24ee9850949a4b48d329a7dc85de72b11/research/tensor-restored-error-join) | [Success](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/39994953330) |
| [#5333](https://github.com/CrocSwap/integer-mult-bounds/pull/5333) | Full local residual budget | [Source](https://github.com/aliromman/integer-mult-bounds/tree/720b7ecc76b605e4a3f9b90826f2544c6ba9e59e/research/physical-pair-full-residuals) | [Success](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/39996148971) |
| [#5341](https://github.com/CrocSwap/integer-mult-bounds/pull/5341) | Single crossing for fixed p16 partitions | [Source](https://github.com/aliromman/integer-mult-bounds/tree/b0edd31a04fe4705846df7673b4a0ec2442260d0/research/fragmentation-single-crossing) | [Success](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/39997680141) |
| [#5403](https://github.com/CrocSwap/integer-mult-bounds/pull/5403) | Native-map and scalar cancellation | [Source](https://github.com/aliromman/integer-mult-bounds/tree/ff78b33a8c5327199af63325b0d4ee80c65b429d/research/native-gauge-cancellation) | [Success](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/40034681556) |
| [#5411](https://github.com/CrocSwap/integer-mult-bounds/pull/5411) | Same-paid coupled native inverse | [Source](https://github.com/aliromman/integer-mult-bounds/tree/123ffa6aa7c1866ac60c67739841f71d95b3edf7/research/native-coupled-inverse) | [Success](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/40044877623) |
| [#5439](https://github.com/CrocSwap/integer-mult-bounds/pull/5439) | Odd-E8 decoder and separated-lift bound | [Source](https://github.com/aliromman/integer-mult-bounds/tree/e6d50e7ebd0bb1fd4f388930df78df696e56b404/research/odd-e8-direct-sum) | [Success](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/40105392037) |

[RETENTION.json](RETENTION.json) records the exact heads, hosted run IDs,
and the 77 package files. Every file has the same Git blob at its submitted
head and at the canonical main commit above. The main ledger still marks
these packages as partially reviewed. Archive intake and CI success do not
establish scientific acceptance or a complete multiplication theorem.

The separate [review of PR #5341](https://github.com/CrocSwap/integer-mult-bounds/pull/5341#issuecomment-6371583032)
reports an exact reproduction and proof check by James Reed, with Claude
Code assistance. Its scope clarification is now explicit in the PR body:
helper targets stay fixed; only their paid increments are partitioned.
No new validation claim is made by that wording change.

## Research that stopped

[EXPERIMENTS.md](EXPERIMENTS.md) records each tested family and the reason
to stop it. The broad negative screens remain exploratory. A time limit is
not an impossibility proof, and an abstract operator test is not a physical
lower bound. Public findings retain those distinctions.

The last new test is retained in [e-history](e-history/README.md). It uses
the small four-input, four-axis fixture of the original 112-root E adapter.
It does not test the actual 112-cubed or 120-cubed caller. Exact rational
elimination rejects the two missing targets even after all 76 one-axis
queries on the retained values are granted together. A changed spectral
control recovers all four targets. These scripts and source bytes are
preserved to make that finite test inspectable; they do not justify a
separate supplier or kappa claim.

At closeout, the exact history check and the spectral control were replayed
in normal and optimized CPython 3.12.13. All four runs passed. The scientific fields
match the saved receipt; elapsed time is excluded from that comparison.
No large caller, selected cold replay, compiler, outer admission, or formal
kernel was run for this handoff. No independent review of the last test is
claimed. [REPLAY.json](REPLAY.json) records the commands and results.

## Current continuation point

The original producer gap has advanced in related work. The merged
[PR #5464](https://github.com/CrocSwap/integer-mult-bounds/pull/5464), at
`d4b9151a160014370faeb7d080f87a06d88a1acb`, now contains full120 native K
and source-consuming E adapters as well as the retained112 construction.
Its
[current proof](https://github.com/thu-nmrc/integer-mult-bounds/blob/d4b9151a160014370faeb7d080f87a06d88a1acb/research/full120-e8-lowrank-e-native/author/PROOF.md)
and explicit invoice are the source for a new caller task. That work is
credited to THU New Media Research Center and its retained source authors;
it is not a result of this handoff. Its new package was not replayed here.

The negative bank still has the coded endpoint
`Q^-1 E3 E2^-1 E1 D123`. Decoding only the positive bank does not supply
the missing negative Gaussian outputs. The merged
[PR #5508](https://github.com/CrocSwap/integer-mult-bounds/pull/5508), at
`7e6824d560337e2b2e49da8b98727183491f6ecf`, excludes the actual112-root
postdecoder from its stated columnwise ordinary algebra. Paid decoders,
correlated histories, and changed targets are outside that obstruction.
The retained small fixture does not extend it to the full caller.

## Open next questions

1. Construct a paid negative decoder, or change the caller and its target
   inventory. Use the current full120 source and retain its exact order of
   Q and E. First state the full optimistic bill. Continue only if the bill
   can exceed the selected result. Then check every original return,
   helper, adapter, idle, COPY/CLEAR, route, precision, and storage cost.
2. If using the old coupled provider, change the source or the caller
   premise. The fixed-source guard and history tests below give specific
   stop rules. They do not exclude all other protocols.
3. For a proof review of a delivered package, use its exact head and its
   recorded open obligations. Do not treat an archival merge as an audit
   of the full theorem.

All reservations made by this investigation are released. Original claim
posts were updated as well as their completion replies. Dillon's
[answer to the control-definition request](https://github.com/CrocSwap/integer-mult-bounds/discussions/4930#discussioncomment-19161071)
is recorded as answered. No answer or reserved work is owed to this run.
These are continuation questions, not tasks assigned to another contributor.

## Evidence retention and credit

The complete local record contains the three original work directories,
their checkpoint notes, source inputs, scripts, receipts, failed attempts,
and publication checks. A file inventory and a verified archive preserve
them. A second pass through this run's tool history checked for missed
temporary inputs and claim posts. The local record is broader than this
public handoff. It does not certify every exploratory script or claim that
every search was rerun at closeout.

Credit remains with the source authors named by each linked package and
finding. In particular, retain Cao Yifan's native word; Dillon's provider,
normalizers and clarification; Dugongue's geometry; the compiler and
precision lineage; the THU New Media Research Center E adapters; and the
attributed parity-projector result used in the fixed-pattern finding.
Mark's [separate product-plane reproduction](https://github.com/CrocSwap/integer-mult-bounds/discussions/1587#discussioncomment-19168830)
confirms the two factor tariffs. It also explains why rank alone gives no
tariff floor. Neither factor is claimed optimal.

Prepared by Ali Romman with substantial OpenAI Codex assistance. No
subagents were used in this closeout. Apache-2.0. No other contributor's
PR was edited, merged, or closed by this closeout.
