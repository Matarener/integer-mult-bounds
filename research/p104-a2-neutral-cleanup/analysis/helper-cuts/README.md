# The composed P104 word has no additional common-chart ZERO→FULL split

**LOCAL-ONLY, exact finite fixed-word exclusion; no new κ claim.** The scientific input is the PR5643 A2 word composed with PR5644's three late-contact deletions, supplied by the coordinating agent as `../../WORD.json.gz`. Exact compressed SHA256: `e94809cecf9e9cba56dd7a8a11ff1edeedc4c34013ff6caebdaf3b021351cf8c`. The parent owns the full native/caller/compiler verification of that composition.

This tests the previously unfinished joint multi-channel cut question for all 411 independent helper roles with initial chart 3 (ZERO) and final chart 127 (FULL). It permits arbitrary rational combinations of every role coframed at a proper intermediate chart; it therefore contains the dyadic dual-pair/unit-ideal search as a relaxation. It does not change the word, add charged boundary transports, combine different initial/final chart groups, or create a new owned-erasure contract.

## Exact result and coverage

The scan checks 8,847 event/chart states at 7,253 distinct event cuts, with all actual coframed cohorts of sizes 1 through 16. Nothing is omitted by a cohort-size bound. Only 18 states have both a nonzero admissible prefix-functional space and a nonzero admissible suffix-direction space. At each, both image spaces have dimension one and their exact boundary pairing is zero. Every other state has an empty prefix or suffix space. The complete pairing matrix is therefore zero at every covered cut, even over Q. There is no hidden multi-channel dyadic unit ideal to complete in this domain.

`ALL-EVENT-CUT-SCREEN.json` records the word hash, all 411 boundary roles, a hash of the enumerated event/chart/cohort inventory, dimension census, and the exact coframe/boundary witnesses for all 18 nontrivial states. The state-inventory SHA256 is `d0a8a54552223d6d7e10cb850c82edadd4d006ee0836295b6354e40cff3784bf`.

## Why this is a complete screen within the stated boundary

At a cut let E be the current roles in one proper intermediate chart, P the actual scalar prefix, S the actual suffix, and G the 411-role boundary group. Row elimination computes all a supported in E for which c=aP is supported in G, then removes zero/dependent c images. Column elimination computes all b supported in E for which d=Sb is supported in G, again retaining a basis of boundary images. These are homogeneous exact-rational kernels of the unwanted boundary coordinates. Elementary elimination spans each full kernel; the second elimination retains the full boundary image space.

Every legal old-input/fresh-suffix channel split must have c·d=1, in addition to the internal pairing and native/chart conditions. A zero pairing matrix between the two full rational boundary image spaces makes that necessary equation impossible. Null-prefix or null-suffix image directions cannot change c·d and need not be retained. This is stronger than failure of a particular pivot test; no dyadic basis compiler can make a zero rational pairing into one.

All scalar ADD, SCALE and COPY events are explicitly considered on their chart. MOVE, INIT and CLEAR events are considered on each chart they touch after the membership change. Any chart untouched by an event has identical prefix rows and suffix columns: the event updates only its operands, all in another chart. Thus its latest recorded event/chart state has exactly the same two spaces and pairing. Initially no proper-chart role carries a G input, so the prefix space is zero before the first touched event. This compresses repeated unaffected states without omitting any cut/chart pairing. COPY is handled explicitly; no invertibility assumption about COPY is used.

## Reproduce and independently check the nontrivial witnesses

```sh
python3.12 -B scan_all_cuts.py ../../WORD.json.gz
python3.12 -I -O -B check_report.py ../../WORD.json.gz
```

Both use only Python's standard library. The independent check propagates each saved prefix functional backwards through the prefix and each suffix direction forwards through the suffix, checking the declared boundary images and all 18 zero pairings. This uses a different chronological direction from the discovery scan for the prefix evidence and directly executes each suffix vector. It also checks source hash and census totals. This check does not independently rederive completeness of every empty kernel; that claim follows the explicit elimination algorithm and its argument above.

## Significance and open next questions

The pending dyadic basis-completion algorithm in [PR #5611](https://github.com/CrocSwap/integer-mult-bounds/pull/5611) removes an individual-unit-pivot limitation, but it cannot help where the full boundary pairing matrix is zero. On this frozen composed word, the large ZERO→FULL group is not a remaining free helper-split opportunity.

A mixed initial/final boundary group is a different construction question. Its bases cannot be freely mixed at their distinct boundary charts; the necessary native boundary transports and changed productive credits must be priced before using a union-group kernel as a claimed improvement. No such charged construction is supplied here. Changed words or changed boundary contracts can reopen this direction.

Credit [Ali Romman](https://github.com/aliromman) for the helper-cut interface, source P104 construction and dyadic basis completion; the PR5643/PR5644 source notices retain the full native/helper/controller/compiler lineage. Prepared for [zxv](https://github.com/zxv) with substantial OpenAI Codex assistance; Apache-2.0. No new native or outer replay was run in this scoped investigation.
