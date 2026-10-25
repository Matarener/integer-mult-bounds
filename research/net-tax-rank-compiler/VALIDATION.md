# Validation of the structural rank compiler

Validated on 2026-10-21, macOS arm64, Python 3.12.8. Scientific code at
`638f4fb6035abb2562f25d9fb7b570d9f2354108`; later validation metadata does
not change the certificate machinery or mathematical receipt.

- Registered metadata/source pins and the bounded package replay pass.
- Seven exact benchmark certificates pass, including the original native
  rank parameters and two separate source profiles.
- Nine mathematical tests pass: formal net-gap accounting, literal split
  taxes, completion bounds including equality, rational interval reference
  points, convex order, coefficient identities, independent Newton-difference
  reconstruction of Bell coefficients, and capped mass perturbations.
- Nine invalid witnesses are rejected, including degree 23, removal of
  tensor concentration, understated full paid costs and invalid log bounds.
- Six literal flows from the unchanged authenticated Sussman oracle agree
  exactly with independent `(G+1)`-fold paid-histogram convolution.
- Committed-byte preflight passes for all 24 package/input files.
- The committed export passes transport/inventory integrity. Its direct
  verifier passes under `python3.12 -I -O -B` with no Git checkout and
  `PATH=/nonexistent`. Mutating a pinned source or its output receipt is
  rejected in that export.
- Separate user-requested Sol 6.1 xhigh agents audited the mathematical
  bounds and source/consumer binding. One audit recovered Bell coefficients
  through ordinary iid moment convolution and Newton differences, avoiding
  the implementation's Bell recurrence.

Reproduction:

```sh
python3.12 -B scripts/research_package.py --package research/net-tax-rank-compiler
python3.12 -I -O -B research/net-tax-rank-compiler/verify.py
python3.12 -B scripts/check_research_commit.py --package research/net-tax-rank-compiler
```

The optional `--check-source-history` preflight is **unavailable** because
this checkout is shallow; it requests full Git history. This is not a
passing ancestry check. Exact committed input bytes and Git-free direct
replay were checked separately; no full-history fetch was attempted.

Canonical main was refreshed at 22:39 UTC and remains
`2a13eb1827784206202db90e5dc8327cf8a250db`; relevant guidance is unchanged.
Overlap checking covers 310 open PR bodies and 3,301 discussion records,
with complete remote pagination. Local coverage is sparse: 23 of 5,739
HEAD note paths were searched. This is not a novelty certificate.

Native and outer producer suites were not rerun. Their authenticated source
receipts and conditional obligations are explicitly inherited. The new
uniform saving supplies the retained outer point by monotonicity. No
winning word, full productive width, physical count, precision constant,
new κ or selected-frontier update is certified by this replay.

The initial validation was local. The user authorized PR submission on
2026-10-22; no Discussion participation is requested.
