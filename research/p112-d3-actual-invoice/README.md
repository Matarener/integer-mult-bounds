# P112: the complete d=3 actual invoice

This package closes **both adapted and nonadapted d=3 branches** for t=2
and t=3 in PR3154's actual-basis contract. It builds on
[PR3689](https://github.com/CrocSwap/integer-mult-bounds/pull/3689), pinned at
`3193d1ea9a4fc5d178570a61e6019454b53c1db9` and merged for archival intake
on 2026-10-20. The central ledger marks that predecessor partially reviewed;
its written raw-shape, intrinsic and geometric results remain load-bearing
dependencies rather than scientifically accepted inputs.

Let T span ALL S-words of binary support rank at most seven, with
C contained in S, dim S=8+t and d=dim(C intersect T)=3. For the actual
basis F, count actual corrections with multiplicity and set I=sum_F w-n_c.

| Claim | Result |
|---|---|
| Raw weight budget 72/73, t=2/3, either adaptation status | I>=65 |
| An actual dual is a live-root multiple | I>=65; after rebate<=1, >=64 |
| No root mark | I>=64 |
| Singleton-pivot consumer | Corresponding exact-rank branch, d=3 nonpivot basis |
| d>=4, global normalization and complete C1 | Open |

No N8, minimum actual basis, distinct arbitrary inside correction indices,
or normalized-list completeness is assumed. The proof retains corrected
weight-nine members and fixed actual coordinate maps throughout.

Start with [PROOF.md](PROOF.md). The arguments divide as follows:

* [T2.md](T2.md) and [T3.md](T3.md) close the nonadapted r=1,eta=2/3
  residues; PR3689 supplies the other nonadapted reductions.
* [ADAPTED-T2.md](ADAPTED-T2.md) closes all fifteen adapted t=2 profiles.
  The last three families close using the new full-root union lemma,
  excluded-frame-point capacity reductions, and actual coefficient kernels.
* [ADAPTED-T3.md](ADAPTED-T3.md) closes all ten all-low t=3 profiles through
  inside sum 32. [ADAPTED-T3-HIGH.md](ADAPTED-T3-HIGH.md) transfers all twenty
  high-containing candidates to fifteen explicitly justified actual-profile
  arguments, without substituting another space for the global T.
* [MERGE.md](MERGE.md) closes inside sum 33: nine corrections force a
  same-axis pair. Merging lowers raw weight, never increases the invoice,
  and produces a t=2 actual basis with d=2 or3. The t=2 proof is completed
  first, so this reduction is not circular.

The reusable new geometric result is [DOUBLE-SEVEN.md](DOUBLE-SEVEN.md):
any two binary flats of rank at most seven contain at most 68 FULL E8 root
lines in their union. Each distinct excluded frame label lowers the live
bound by one. Distinct maximal 36-root sections have intersection counts
6,10,12,20 and union at most 66. A disjoint mixed 36/32 construction proves 68 is the sharp full-root
union bound. This is not invoice sharpness. These are analytic quadratic-character-sum deductions,
corroborated by exhaustive finite checks rather than inferred from a
coefficient grid.

[DEPENDENCIES.md](DEPENDENCIES.md) separates inherited written theorems,
new arguments and recomputed finite inputs. [VERIFY.md](VERIFY.md) gives
executable and partial Lean coverage. Full E8 instantiation and invoice
assembly remain written mathematics. This does not change kappa or the
selected frontier.

## Reproduce

From the repository root with Python 3.12 and the standard library:

```sh
python3 scripts/research_package.py --package research/p112-d3-actual-invoice --check-only
python3 scripts/research_package.py --package research/p112-d3-actual-invoice
```

The replay authenticates inputs and exact package bytes, checks all stated
integer profiles, all 43,180 affine six-sections, all 14,794,080 maximal-
section pairs, the frame-cut and G4 inputs, and actual-basis controls.
flat_union.py reuses frame_pair_geometry.py's E8 model. A separate canonical
quadratic implementation imports no E8 model and must agree on both spectra
and the derived universal union bound.
It is not a formal proof over arbitrary actual bases or coefficient fields.

## Open next questions

* **d>=4:** begin with the smallest raw-shape survivor and derive its actual
  correction constraints. A T-level invoice still cannot automatically be
  transferred to an arbitrary actual basis.
* **Formal bridge:** instantiate the Init-only finite outside-restriction
  theorem with actual vector spaces, coordinate functionals and C+L=S.
  The E8 geometry and full case assembly remain additional obligations.
* **Global consumer normalization:** the singleton-pivot consequence retains
  exact actual-rank and nonparallelity hypotheses; broader rank/pivot
  branches need separate arguments.

## Credit

Prepared by conorholds with substantial OpenAI Codex assistance, including
GPT-6.1 SOL agents at xHigh reasoning. Internal AI reviews are not
independent human review. Apache-2.0.

DreamingOfClouds's PR3154 supplies the actual-basis contract and handoff.
conorholds's PR3689 supplies the d1/d2 invoices, intrinsic geometry and
partial d3 raw-shape argument; PR3455 supplies the correction count and
consumer; PR3166 supplies the matched two-axis input. Nick Petalas's
PR3269/3300 supply capacities and PR3171 the coordinate-kernel/root-plane
method. The four-six composition retains DreamingOfClouds's PR2816 and
Nick Petalas's PR3171 lineage. The E8 model retains David Arias's and the
pinned source packages' existing credits. No predecessor or selected result
is changed.
