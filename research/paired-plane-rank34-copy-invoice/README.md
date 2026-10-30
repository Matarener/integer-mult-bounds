# PR3335 rank-34 factors: full-port copy invoice

**Scoped cost audit; no new kappa.** The literal 34-channel scalar fit in
[PR3335](https://github.com/CrocSwap/integer-mult-bounds/pull/3335), head
`1d46df8b5aeac49d165cae58c1dd1036666bb789`, satisfies its new plane mask.
Under the retained **full-port one-total pairing-rank tariff**, its copy charge
is **224**, not 34, 68, or 112. This already exceeds the proposed plane-port
coverage allowance at zero saving. It does not invalidate PR3335's algebraic
rank improvement from 49 to 34.

This answers the copy-pricing part of PR3335's explicit native-cost handoff.
The new contribution is the exact source-bound invoice on its new matching and
factors, with a separately implemented mask/endpoint/rank check. The general
integral floor and the earlier direct native price of 224 are predecessor
results, not new theorems here. A complete native word is not supplied.

## Exact result

The certificate is retained byte for byte at
[predecessor/PR3335-CERTIFICATE.json](predecessor/PR3335-CERTIFICATE.json).
Its labels come from the selected1094 replay archive, with both the compressed
input and its DATA-PHASES member authenticated before parsing. No predecessor
Python implementation is imported.

SOURCES.json pins the vendored copy at retention commit
`5685c6288205e463e4ca28355fc3a3458da27334`, an ancestor of this contribution.
Its `upstream_certificate` records the original PR head, path, Git blob and
SHA256. The retained bytes were compared with that exact fetched upstream blob.
Registered replay needs this contribution's Git history; it does not require
a separate fetch of the unrelated PR3335 commit. Direct replay authenticates
the retained fixture by SHA256 and runs without Git.

| Literal support size | Channels | Full-port rank per channel | Copy charge |
|---|---:|---:|---:|
| 2 | 8 | 4 | 32 |
| 3 | 8 | 6 | 48 |
| 4 | 18 | 8 | 144 |
| Total | 34 | | **224** |

The final factors form four two-plane, four three-plane and nine four-plane
orthogonal classes, with two channels per class. These are the **final support
classes**, not the twelve disjoint eight-frames in the discovery construction.
The receipt prices the shipped factors rather than the search narrative.

The independent scalar check verifies all 12,544 entries, including the 11,440
forced entries, and rechecks the predecessor's 17-plane forced `I_34` witness.
For `K = sum_t 1_S_t 1_S_t^T`, the correction `Z = I-K` has 280 nonzero
entries, all on orthogonal-plane pairs. Thus `K+Z=I` is valid under the retained
free-correction mask. A scalar interpreter checks all 224 source/dirty-target
input columns. This establishes the abstract scalar endpoint, not a legal
physical schedule for acquiring, delivering or restoring its totals.

## Why a shared scalar total carries a larger port space

Port i has the whole plane `E_i`, with Gram matrix `I_2`. For a scalar factor
`a_t b_t^T`, the retained tariff is

```
L_t = sum_{i: a_it != 0} E_i,
R_t = sum_{j: b_jt != 0} E_j,
rho_t = rank_F2(pairing on L_t x R_t),
C = sum_t rho_t.
```

This is the contract stated in
[the retained full-port proof](../support-balanced-port-floor/PROOF.md), section 1.
It prices complete port spaces, including a matched partner's direction even
when that partner is absent from the scalar support. Counting only the labels
named in the support gives the wrong interface.

For each shipped support S, distinct touched planes are pairwise orthogonal:
otherwise its all-ones block would violate the required off-diagonal zero.
A support contains at most one port from each plane. The `|S|` planes are
therefore a nondegenerate orthogonal direct sum of dimension `2|S|`.
Both scalar factors have support S, so `L_t = R_t` is this sum and
`rho_t = 2|S|`. Since the supports partition all 112 ports,

```
C = sum_t 2|S_t| = 2*112 = 224.
```

Consequently regrouping this *disjoint 0/1 support-partition construction*
into fewer channels cannot lower its copy tariff, for any valid Gram-I2
matching. This elementary specialization is consistent with Philippe Van
Velzen's stronger, prior 2-integral floor. It is not a floor for arbitrary
rational or complex decoders.

As an additional check of that prior bound's source binding, expand each scalar
entry `K_ij` by the 2-by-2 pairing of the bases of `E_i,E_j`. The complete binary
224-by-224 expansion is exactly `I_224`. Every factor's expanded rank is its
full-port pairing rank, so the displayed factors saturate the existing
integral lower bound. See also
[Sagar Thakrar's retained explanation](../kport-group-scalar-endpoint-audit/README.md)
of the expansion and normalization hypotheses. We do not reprove a general
2-adic gain theorem or claim that all rational factors obey the integral floor.

## Conditional coverage decision

Grant the proposed two-unpaid plane contract and ideal hosting with zero extra
charges. Retain `m=73`, `W=896`, `N=9`, as in
[the earlier direct payload audit](../paired-plane-native-payload/README.md).
The complete coverage-law mass, including data/helper/idle work, is

```
mass = 71 W + 224 N = 65,632,
capacity = 73 W = 65,408,
moment(a=0) = 293/292 > 1,
deficit per call = 2(896/9) - 224 = -224/9.
```

For children of ranks at most m and a nonnegative saving a,
`(r/m)^(1-a) >= r/m`. Hence this optimistic bill already fails for every
nonnegative saving under that coverage law. No choice of idle packing or
additional nonnegative acquisition/restoration charge can fix this bill.
This does not admit the changed coverage law or claim that an alternative
decoder, multi-array primitive or different source/consumer contract fails.
The tariff itself is not an emitted native child histogram.

**Expansion decision:** stop native construction on these literal factors for
this target; preserve the useful rank-34 result and seek a changed decoder or
physical contract before another dependent construction round.

## Reproduce and evidence

From the repository root, standard library only, Python 3.12:

```sh
python3.12 -I -B research/paired-plane-rank34-copy-invoice/verify.py
python3.12 -B scripts/research_package.py --package research/paired-plane-rank34-copy-invoice
```

Expected final marker: `PASS_PAIRED_PLANE_RANK34_COPY_INVOICE`.
[RESULT.json](RESULT.json) records every channel rank and the complete scoped
receipt. The registered replay also runs with `-O`; acceptance does not use
assertions. `--output NEW.json` recomputes a receipt and refuses an existing
output path. Normal replay is read-only.

All 34 full-port pairing ranks and the line-only comparison are checked with
two implementations: XOR pivot elimination and a finite-set image/kernel
cardinality calculation. Eleven controls reject duplicate matching ports,
overlapping supports, a forbidden same-plane cross-entry, a missing free
correction, lost target dirt, singleton-label underpricing (112), one rank-two
charge per channel (68), changed predecessor/archive/member bytes, and a
type-confused receipt.

Exact scope: selected label extraction; literal matching/support/clique data;
integer scalar fit and free correction; all source/dirty-target columns;
full-port binary tariffs; integral expansion; conditional zero-saving bill.
**Unrun obligations:** native operator/compiler lowering; actual source
acquisition and correction chronology; private-array lifetimes/restoration;
physical routing/hosting; precision/tape; all-size interfaces; both complete
suppliers and outer theorem; selected cold replay. Hosted CI and independent
human or formal-kernel review are not claimed.

## Task, overlap and credit

Scientific base: canonical main
`6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority revision 6. The live
handoff was checked before retrieving card `coverage-law-change`. Scope is
declared **changed** in [TASK.json](TASK.json): a focused cost audit of an
already-proposed plane contract rather than another replacement construction.
The card's known-working ceiling control passes; the new zero-saving screen
uses the changed law explicitly and does not apply the incumbent ceiling
outside its hypotheses.

Entry overlap used complete pagination: 257 open PRs (including drafts) at
2026-10-17T22:28:57Z and 2,181 Discussion records at 22:29:36Z, plus relevant
main packages. PR3335 supplies the matching/rank result and asks for this cost
follow-up; PR2203 supplies the direct native 224 bill on the old matching;
PR2532 and the full-port proof preserve the integral/full-span rules.
Pre-submission refresh at 2026-10-17T22:37:04Z covered 258 open PRs
and 2,187 Discussion records, with main unchanged. It revealed a
[near-simultaneous same-question claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1587#discussioncomment-19007604).
This checker was implemented independently; the concurrent audit is explicitly
credited, and publication is coordinated in the existing thread. The
[concurrent block-rank audit](https://github.com/CrocSwap/integer-mult-bounds/discussions/1587#discussioncomment-19007618)
asks a different question and excludes this tariff scope. The query does not
cover every diff or prove novelty. The current status is maintained in
[the canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1587#discussioncomment-19007603).

Credit Matarener/Mark and Claude for PR3335's rematching and exact rank 34;
thakrarsagar/Sagar Thakrar for PR2484 and PR2532; ywz65 for PR2471;
Cinna Davis/1337isnot1337 for PR1825, PR2126 and PR2118; Adam Gall for PR1889;
ctoth's team for the plane endpoint, coverage law and naive charge;
Philippe Van Velzen for the prior one-total integral floor; Jeremy Diviney
for PR2203's native payload accounting; and the retained Chafik Boukhalfa,
Ali Romman, icekylinx, Rohan Arun, Jeremy Kothe and Hao Yan construction lineage.
The previous Arham Tahir full-port proof is a cited definition/precedent,
not an independent reviewer of this result.

Prepared for Arham Tahir with substantial **OpenAI Codex** assistance.
Apache-2.0. Frozen sources and the selected frontier are unchanged.

## Open next questions

Can a different, genuinely non-2-integral decoder on these rematched planes
achieve the required full-port tariff? This matters because integral channel
compression alone still costs 224. Start with exact rational source/reader
factors and even-denominator gain, check their whole scalar mask, and price
their complete plane spans before native lowering. The blocker is the missing
lower-cost factorization; acquisition, restoration and physical/all-size
admission would remain additional obligations. No new matching search or
further construction round is reserved. Structured fields are in TASK.json.
