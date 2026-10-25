# Arbitrary-support skew gate: independent review

No mathematical defect found in the fixed-interface rank tariff or its
unitary support-length extension with the explicit implementation premise.
The final root proof is pinned at
`8893ff2446e4b12e4ab7fcde917177133b10dca7a9a1230aba161301be029585`.
See `REVIEW.md` for the derivation, boundaries and phase conventions.

`AUDIT.json` independently checks36 retained wider-support fixtures, q=2,3:
every default original column, both literal inverse orders, physical
chronological J_s ranks, two-sided transport isolation, full current
Du-deletion defect, all-f Gaussian phase identities, complete literal
N/J/Q inventory and saved two-site bills. It adds14 rank-extreme tests at
q=2..8, including d=-2k and the sharp d=2,w=0 case. Stale full/prefix/tail
metadata and the old two-plane transport convention are defect-sensitive
controls. Normal and optimized Python pass.

The phase-correct dynamic identity
`F_(2t)^-1 P_(2t) J_(2t-1) N_(2t-1)=B_(2t)F_(2t-2)^-1`
uses no commutation of J. It implies
`L=-N_(2q)...N3`. The complete bound is
`M>=A+2q+(n+1)d+w>=n*r`, because `w+r>=m`.
Negative d does not invalidate this inequality. Charged nonmonomial U is
allowed by counting nu(U)+nu(V), with the sites kept separate.

The arbitrary-unitary extension uses lambda=max(log2 maximum row support,
log2 maximum column support). It is inverse invariant for unitaries,
monomial invariant and product subadditive. Its cost conclusion requires
each separately charged unary implementation to have charge at least
lambda, e.g. native/physical-monomial compositions. It does not silently
cover free coupled-bank ADD path sums or cross-boundary native fusion.
Parent stock still requires the intended admitted flat/native target;
equal-volume full-bank normalization is necessary for the moment corollary.

The caller's separate all-q suffix A/B induction was read and found sound
for its pinned repeating topology. Its initial executable proof pin was
stale after the final root wording change and was reported to both authors;
that is a provenance repair, not an operator defect. The final derivative
and its status are recorded in `SOURCE-PINS.json` and `VALIDATION.json`.

Reproduce from this directory:

```
python3.12 -B audit_arbitrary_skew.py
python3.12 -B -O audit_arbitrary_skew.py
python3.12 -B lambda_controls.py
python3.12 -B -O lambda_controls.py
python3.12 -B validate_review.py
python3.12 -B -O validate_review.py
```

All source dependencies are read-only. No frozen prior reviews, source
artifacts, primary checkout, BIT files or publication resources were edited.
No all-q selected supplier/controller, recursive transfer or new kappa is
claimed. Changed scalar topology, extra coupled sites, changed owner/input/
output contracts and separately unpriced helper/ADD paths remain outside.
