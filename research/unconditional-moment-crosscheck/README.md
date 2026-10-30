# Independent numerical cross-check of PR4100's exact-root and paid-power ledger

This package independently recomputes the finite arithmetic layer behind the
headline exponent of PR #4100 (`research/unconditional-batched-crt`, retained
head `337d04939571a637aeab54a0f58f54fde811663a`). It re-implements the
moment certificate from scratch — its own rational logarithm and exponential
interval enclosures, its own bill evaluator and root bisection — and imports
no code from the audited package or from `staged544-mixed-fourth-entry/vendor`.
Constants are transcribed from the prose of PR4100's `PROOF.md` ("Paid powers"
and "Time" sections); the child histogram and the conditional-exponent
benchmark are read from the pinned PR4088 `RESULT.json`
(`research/staged544-mixed-fourth-entry/RESULT.json`).

## What was checked (and what it established)

For the profile `{1:8060060, 2:2310120, 3:751813, 4:327210, 5:66425,
8:25920, 48:138492}`, width `m = 73` and comparison count
`W = 896 × 360 = 322,560`, with the stated candidate

```text
b = .001730979115670792472760579929302792893760378764
kappa = .00173097911567079247276057   (the 26-decimal-place truncation of b)
```

the independent enclosure proves the finite statements:

1. `bill(a) = Σ_r n_r (r/73)^(1−a) / W` satisfies `bill(b) < 1` with
   certified margin at most `-1.800e-48` and `bill(b + 1e-48) > 1` with
   margin at least `+1.030e-48`. The model root therefore lies strictly
   inside `(b, b + 1e-48)`; the 90-digit bisection localizes it to
   `b + 6.363e-49`, agreeing with the margin ratio `1.800/(1.800+1.030)`.
2. `bill(kappa) < 1` with margin at least `2.815e-26`; also
   `bill(a_eff) < 1` and `bill(q) < 1` for the package's `a_eff` and `q`.
3. All twelve paid-power slacks (`1 − kappa − power`) are strictly positive
   and all fifteen side-condition slacks are strictly positive, recomputed
   as exact rationals from the primitives stated in `PROOF.md`.
4. All five obsolete-route rejects (`old_Vd_crt`, `old_g_union_scans`,
   `old_per_record_d_chirp`, `old_theta_chirp_guard`,
   `no_group_gap_membership`) remain strictly negative at the claimed point.
5. The bootstrap constants reproduce exactly:
   `a1 = c(1−c) = .00173039532444` and
   `a2 = c(1−c²) = .001733394791695384296` for `c = 8667/5,000,000`, and
   `7^16 < 2^45`.
6. The exact gap over PR4088's published conditional exponent reproduces:
   `kappa − conditional_kappa = 5.700000000000000000001e-25 > 5.7e-25`,
   and the profile agrees with the pinned PR4088 `RESULT.json`.

Controls (all rejected): an inflated rank-1 count, a bracket shifted up by
`1e-12` (which excludes the localized root), a root claimed at or above
`b + 1e-48`, and an unrounded `kappa` equal to `b`.

## Scope — exactly what this is

This is a **finite numerical audit of stated arithmetic claims** at the
retained source heads. It confirms that PR4100's exact-root certificate,
paid-power ledger and headline comparison gap reproduce under a second,
independent implementation. It does **not** validate the all-size arguments:
the CRT total repair (audited separately in #4169), the free-algebra lift in
`COMPLEX.md`, the precision/conditioning and fixed-tape obligations, and the
physical caller/realization premises all remain open. Nothing here is a new
selected result, a supplier admission, or a change to the selected frontier.
The selected conditional κ remains `0.001672660197076918`.

## Related open work (numerically checked)

- **#4100** (audited predecessor): the claims reproduced here are its own
  stated numbers at head `337d049`.
- **#4088** (`staged544-mixed-fourth-entry`): source of the pinned profile
  and `conditional_kappa`; both agree with the values used by #4100
  (asserted in the verifier).
- **#4091 / #4170**: #4170 reports remaining headroom `1.140318244487202e-9`
  of the #4091 pooled ceiling over the retained #4088 fill. Agreement check:
  `0.00173097911567079247276057 + 1.140318244487202e-9 =
  0.00173098025598903696000259… ≈ 0.001730980256`, matching the #4091
  ceiling root quoted in the family record. The two audits study different
  objects (pooled fixed-inventory ceiling vs this article's moment ledger)
  and no number here contradicts #4170.
- **#4169**: audits the compact CRT repair inverse of the same #4100 head.
  Complementary proposition; no overlapping number.

## Reproduce

From the repository root, with Python 3.12:

```sh
python3.12 -B research/unconditional-moment-crosscheck/verify.py
```

Expected: `PASS_UNCONDITIONAL_MOMENT_CROSSCHECK` and the JSON receipt above.
Runtime is well under one second. The registered check is
`python3 -B scripts/research_package.py --package research/unconditional-moment-crosscheck`.

## Open next questions

1. Can the free-algebra lift in `COMPLEX.md` be stated as one quantified
   proposition at its actual caller and proved or falsified? (The numerical
   layer checked here says nothing about it.)
2. Does the localized root margin (`b + 6.36e-49`) leave any room for the
   chronological (non-pooled) fill to attain the #4091 pooled ceiling that
   #4170 measured as remaining headroom? This package does not answer it.
3. Is the localized model root (about `b + 6.4e-49`) attainable by a
   chronological (non-pooled) fill, or does it remain a pooled-inventory
   optimum, as #4170's remaining-headroom analysis suggests for the related
   #4091 ceiling? This package does not answer it.

Prepared by Nick Petalas with AI assistance. Apache-2.0. Predecessor
attribution is retained: the audited construction is PR #4100 by Cinna Davis
and its pinned lineage; the profile and benchmark come from PR #4088's
retained sources.
