# PR3335's rank-34 fit: complete-plane copy tariff 224

**Scoped independent audit and cost obstruction. No new supplier or kappa.**

This public supplement accompanies independent feedback on concurrent
[PR3345](https://github.com/CrocSwap/integer-mult-bounds/pull/3345), reviewed head
`529959bb00abd01664b7109d2e40574ecb0c8da1`. That PR is the single submission
for the literal invoice. The additional result here is the arbitrary-weight
orthogonal-local floor and native drop/entry checks. The independent scientific
implementation and receipts are retained at commit
`fd37c0fe841d814f2bdcc178d58888ec47dc86a3`; no duplicate invoice PR is opened.

[PR3335](https://github.com/CrocSwap/integer-mult-bounds/pull/3335), exact head
`1d46df8b5aeac49d165cae58c1dd1036666bb789`, supplies a valid rematching of the
112 selected P112 ports with strict scalar fitting rank 34. This package
independently confirms that result, then answers part of its native-cost handoff:
the **34 published scalar totals have complete-plane pairing tariff 224**.
Seventeen distinct native drop recipes still require 34 payload occurrences.
Rational reweighting within mutually orthogonal plane groups cannot reduce
this tariff below 224.

This is an application of the inherited full-port, one-total tariff, not a new
general plane-decoder lower bound. Philippe Van Velzen's earlier 2-integral
floor, ctoth's naive cost 224, and Jeremy Diviney's native payload accounting
retain their priority. What is added is exact coverage of the new PR3335
certificate, independent scalar checking, its complete per-channel invoice,
native drop checks and an explicit boundary for fractional local reweightings.

## Scalar fit and the old obstruction

Labels are extracted from the authenticated selected1094 replay archive.
Each matched pair spans a nondegenerate binary plane `E_p` with Gram matrix
`I2`. Both scalar ports in the pair carry that entire plane. The strict mask is

```text
K_ii = 1;
K_ij = 0 if i != j and E_owner(i) is not orthogonal to E_owner(j).
```

The published 34 disjoint supports partition the ports. Their indicator outer
products give `K`; one representative per support gives an `I34` minor, so
its rank is exactly 34 over every field. The published 17 pairwise
nonorthogonal planes force `I34` inside every fitting matrix, establishing the
matching lower bound. The checker reconstructs all 11,440 forced entries and
both minors without importing PR3335/PR2484 code.

The old PR1889 parity-lift objection does **not** reject this new scalar fit.
For example, labels at ports `(0,7)` are `(11,21)`: their binary dot product
is one, but the new scalar coefficient is correctly zero. All 6,608 such
off-diagonal old binary-target ones are zero in the new fit. In total the
binary matrices differ at 6,888 entries. PR3335 is not a parity-preserving lift
of the old `B0` factorization; its exact scalar fit is preserved by this audit.

## Complete-plane invoice

For a scalar total with target support `A` and source support `B`, use the
inherited tariff

```text
L = sum_(i in A) E_owner(i), R = sum_(j in B) E_owner(j);
rho(A,B) = rank_F2(pairing restricted to L x R).
```

Each published support `S` selects one port from each of `k` mutually
orthogonal distinct planes. Thus its complete plane span has Gram matrix
`I_(2k)` and its one-total tariff is **2k**, although the original singleton
labels alone have pairing rank k.

| Support size | Scalar totals | Complete-plane rank per total | Rank mass |
|---|---:|---:|---:|
| 2 | 8 | 4 | 32 |
| 3 | 8 | 6 | 48 |
| 4 | 18 | 8 | 144 |
| Total | 34 | | **224** |

[RESULT.json](RESULT.json) lists every support and complete plane basis.
`check_native.py` lowers the canonical private drops for all 17 distinct spans
with the retained Clifford compiler. A separate Gaussian interpreter checks
their signed Pauli actions and exact global phases. The highest-rank drop is
also checked on all 512 input basis columns. Each recipe is used for two
independent scalar totals: charging distinct recipes once would incorrectly
give 112. The correct occurrence count gives 224.

All 112 local conversions from an old line entrance `C_q` to the rematched
canonical plane entrance have rank one, with exact native operator checks.
This is a conditional migration cost for those old entrances, not an extra
112-unit charge imposed on every possible changed template. It is not added
to the favorable rejection screen below.

## A local reweighting floor, including rational cancellation

Allow any finite scalar factorization over any field,
`K = sum_t c_t a_t b_t^T`, with nonzero terms. Coefficients, signs, supports
and denominators are unrestricted, subject to one support hypothesis:
**within each term, the distinct planes touched by its source and target
supports together are pairwise orthogonal**. Different terms may use different
groups; supports need not be identical, and both ports of a plane may occur.

Write `A_t,B_t` for the sets of planes touched by the two factors. Orthogonality
and nondegeneracy make the complete pairing block diagonal, hence

```text
rho_t = 2 |A_t intersect B_t|.
```

For each plane p, the strict scalar mask forces `K[p,p] = I2` on its two
ports. Each term contributes rank at most one there, and contributes zero
unless `p in A_t intersect B_t`. If `n_p` counts these terms, rank
subadditivity gives `n_p >= 2`, regardless of cancellation. Consequently

```text
sum_t rho_t = 2 sum_p n_p >= 2 * 56 * 2 = 224.
```

The published fit attains this bound. This short proof closes arbitrary local
reweightings in the stated support class, not arbitrary asymmetric or signed
Gram decoders. For a concrete even-denominator control, replace each pair of
published totals u,v on one plane group by

```text
(u+v)(u+v)^T / 2 + (u-v)(u-v)^T / 2 = uu^T + vv^T.
```

The exact rational checker reconstructs the same scalar fit on all 17 groups;
the two independent totals still cost 224. A signed asymmetric cost-zero
cross-term cancellation is also accepted. A cancelling term touching two
nonorthogonal distinct planes is explicitly outside this proof's hypothesis.

## Favorable coverage decision and limits

Grant the retained plane-port law, ideal hosting and zero additional costs:
`m=73, W=896, N=9`, with rank mass `71W + C N`. At C=224,

```text
mass = 65632; capacity = 73W = 65408;
moment(a=0) >= 65632/65408 = 293/292 > 1;
deficit per call = 2W/N - C = -224/9.
```

For `0 < r <= m` and `a >= 0`, `(r/m)^(1-a) >= r/m`. Thus this tariff
already prevents positive saving under that coverage model, before gathering,
distribution, free-entry repairs, cleanup, routing or precision are charged.
The mass formula and one-total tariff are premises, not a constructed supplier.
The earlier naive implementation has the same failing mass; its discovery is
not claimed here. Do not launch another construction round confined to this
orthogonal-local class as a route to a favorable native bill.

No full native implementation of the rank-34 fit is supplied. Native evidence
covers its individual private drops and old-entry conversions; it does not
implement a complete COPY tree, dirty-target endpoint, borrowed-helper
restoration, chronological owners, physical gathering/consumer, all-size
compiler, precision/tape, bit supplier or analytic transfer. No selected cold
replay, hosted-CI result, formal-kernel or independent human review is implied.

## Reproduce and sources

Python 3.12 or later, standard library only, from the repository root:

```sh
python3.12 -I -O -B research/paired-plane-rank34-copy-audit/verify.py
python3.12 -I -O -B research/paired-plane-rank34-copy-audit/check_native.py
python3.12 -I -O -B research/paired-plane-rank34-copy-audit/check_controls.py
python3.12 -I -B scripts/research_package.py --package research/paired-plane-rank34-copy-audit
```

Default checks are read-only and compare exact receipts. Sixteen control groups
include separate coordinate-vector plane reconstruction and dense binary
elimination, wrong full-plane/singleton mask, false clique, undercounted tariff,
rational half weights, signed asymmetric cancellation, changed support class,
source corruption, typed receipt corruption, overwrite refusal and a Git-free
export. Three additional native controls reject wrong phase, half rank and
deduplicated payload charges. Explicit `--output NEW.json` creates a fresh
receipt and refuses an existing path.

[VENDOR.json](VENDOR.json) authenticates the byte-for-byte PR3335 certificate
by its original Git blob and SHA256. That committed export is sufficient for
cold replay; no unmerged predecessor commit must be present in Git's object
store. [SOURCES.json](SOURCES.json) binds main inputs and scientific baseline
`6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority revision 6.
[TASK.json](TASK.json) records handoff selection, scope change and checkpoints.
Frozen predecessors and the selected record are unchanged.

## Open next questions

A cheaper decoder under the same tariff must use at least one term whose
combined source/reader supports touch nonorthogonal distinct planes, or change
the physical copy contract. First produce an exact scalar fit with all complete
plane spans priced, and a favorable full bill; scalar rank alone is insufficient.
Such a fit would still need actual native gathering, endpoint repairs, cleanup,
hosting, precision and a compatible consumer. No such fit is supplied here.
The structured question and blockers are in TASK.json.

## Credit

Mark / Matarener, with Claude via Claude Code, retains PR3335's matching,
supports, rank-34 result and discovery credit. Credit Cinna Davis / PR1825 and
PR2126 for paired planes and identity fits; 1337isnot1337 / PR2118 for the earlier
local rematch; Adam Gall / PR1889 for the scalar mask; ywz65 / PR2471 and Sagar
Thakrar / PR2484 for the earlier rank bounds and clique method. Philippe Van
Velzen's [2-integral floor and tariff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1587#discussioncomment-18927273),
ctoth's [plane contract and naive 224 invoice](https://github.com/CrocSwap/integer-mult-bounds/discussions/1587#discussioncomment-18914510),
Jeremy Diviney / PR2203's independent-payload accounting, Josie Elliston /
PR1808's budget screen, Arham Tahir / PR2879's principal-block method, and
Sagar Thakrar / PR3232's signed-Gram support charging are predecessors.
The native compiler/interpreter retain Chafik Boukhalfa / PR1991, Ali Romman /
PR1862, icekylinx and retained campaign attribution. Selected labels and geometry
retain Rohan Arun, Jeremy Kothe, Hao Yan and their supplier lineage's credit.
The near-simultaneous Arham Tahir / Codex investigation published PR3345's
literal invoice independently; this supplement credits and corroborates it.

Arham Tahir, with substantial OpenAI Codex assistance in proof, implementation,
checking and writing. No subagents or independent human review. Apache-2.0;
the retained predecessor certificate is unmodified under its original license.
