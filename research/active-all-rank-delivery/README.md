# Sharp all-rank floor for fixed immutable delivery

**Every rank-1 through rank-9 mixture costs at least 8H8** in the fixed immutable-channel contract from [PR5808](https://github.com/CrocSwap/integer-mult-bounds/pull/5808). This holds for every `Hr = r^q H1`, `0 < q <= 1`, with arbitrary rational payloads, unlimited chronological scatter and joint noise cancellation. More than eight channels cost strictly more than `8H8 + H1/5`. Eight exact clean directions attain the quotient floor.

This closes the rank-8/rank-9 gap left by PR5808. The result is a source-bound obstruction, not a new kappa or a general lower bound for changed native words. The fixed immutable delivery strategy cannot save its removed eight H8 calls. A new construction must change a stated hypothesis.

## Exact evidence

The retained census checks 22,585 events, 641 roles, 1,002 charts and 8,298 chart/response pairs. The new certificate has 48 coordinate-basis cuts, 22 response-span cuts and one channel-count row. For nine or more channels with rank eight excluded, its exact dual value is

    1441100759 / 20000000 = 72.05503795.

Thus their integer rank mass is at least 73. The rank-nine chart has the full 112-dimensional response space. Replacing each rank-eight response by a rank-nine response increases its rank charge by one and preserves the algebraic correction. With at most seven rank-eight channels, the original rank mass is therefore at least 66. With eight or more rank-eight channels, the required price floor already holds.

[PROOF.md](PROOF.md) gives the complete channel-count cases and an exact polynomial argument for every concave power. It uses no sampled powers. [RESULT.json](RESULT.json) contains all cut incidence hashes and the eight clean witnesses. The checker also uses a separate integer determinant for every coordinate basis. Seven semantic rejection controls, joint-noise cancellation and the eight-channel boundary are checked.

## Reproduce

```sh
python3.12 -I -B -W error research/active-all-rank-delivery/verify.py
python3.12 scripts/research_package.py --package research/active-all-rank-delivery
```

Replay needs only the Python standard library. It authenticates the unchanged source archive and the retained response code. It also runs from a read-only Git-free export under `-O`, with empty PATH. Normal replay does not write a receipt. `--record` is the explicit generation command. SciPy and modular arithmetic were used only for discovery; neither is part of verification.

[SOURCES.json](SOURCES.json) records exact source blobs and hashes. The copied response code is byte-identical to PR5808. Full Git ancestry was not checked in the shallow checkout. Committed bytes, modes and a sealed source export were checked.

## Limits

The source word, scalar program, native actions and public boundaries stay fixed. Each channel keeps one chart and one scalar combination of the original eight modes. The model grants gathering, scatter, storage and helper restoration, but retains the restored-Y condition. The common-fixed-vector native specialization remains a predecessor premise. The sharp witness is in this granted quotient; PR5745 retains the separate physical eight-H8 construction and its extra ordinary costs.

Moving charts, changed payloads, feedback-dependent data and changed native words are outside the theorem. No compiler, precision tape, physical native implementation or outer analytic assumption is discharged. The selected frontier is unchanged.

## Open next questions

Test a moving chart, a changed payload dependency or a changed native word only after a new complete invoice and scope check. Audit the common-fixed-vector native premise at the intended caller. [TASK.json](TASK.json) gives the first steps and blockers.

## Credit

Prepared by Ali Romman with substantial OpenAI Codex assistance; Apache-2.0. PR5808 supplies the unchanged response census and lower-rank certificates. Credit flyingviper / PR5755 for the restored-Y invariant and rank-one census, PR5745 for temporal delivery and eight-H8 attainment, PR5720 for the active-mode proposal, Cao Yifan, Cinna Davis, Dugongue and every author in the unchanged source archive. The new contributions are the coordinate-basis dual, the rank-nine replacement proof and the complete all-power floor. No predecessor construction credit is claimed.

The source manifest pins replay inputs to copies in this publication history.
Its `retained_predecessors` records keep each original head, path, blob and
SHA256, plus its exact retained file or archive member. Each source was checked
byte-for-byte before this rebind. This removes an unavailable side-commit
dependency from clean CI; no source bytes or scientific checks are changed.
