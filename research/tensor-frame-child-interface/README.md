# Tensor-frame child: factorwise repetition fails the pinned moment

**Scoped separation; no new κ.** At the #4088 mixed profile and its pinned
lower root endpoint, one child of rank `r*f` inside width `73f` keeps the
scalar moment negative, and `f` copies of each scalar child make that moment
positive for every integer `f >= 2`. The pinned native recipe records are
still the scalar histograms. This does not accept #4100 and does not change
the selected frontier.

## Scope and evidence

Card `uniform-transfer-audit`, scope **refined** to the frame/child coordinate
left open by the free-word audit #4184. The caller is the #4088 histogram in
`research/staged544-mixed-fourth-entry/RESULT.json`, not a new profile.
[PROOF.md](PROOF.md) gives the two bills and the series tails. `verify.py`
recomputes the enclosures with the standard library and checks both recipe
reports. The receipt status is `PASS_TENSOR_FRAME_CHILD_GAP`.

Source commits, Git blobs and SHA256 pins are in [SOURCES.json](SOURCES.json).
The selected record and catalogue are historical provenance. The three
`--source` files are live inputs and must match their pins.

The scalar moment at the pinned endpoint is about `-3.843e-14`. The factorwise
bill at `f = 2` is greater than `56052`, and its derivative in `f` is greater
than `68435`, so every larger integer `f` is worse. The single-child bill is
`f^(1-k)` times the scalar moment.

## Reproduce

From the repository root, with Python 3.12:

```sh
python3 scripts/research_package.py --package research/tensor-frame-child-interface --check-only
python3.12 scripts/research_package.py --package research/tensor-frame-child-interface
```

The verifier does not import the predecessor moment engine, the native runner,
or the #4184 checkers. A direct run is:

```sh
python3 -B research/tensor-frame-child-interface/verify.py
```

## Open next questions

**Question:** What tape-action and child count do the left and right monomials
of one actual #4088 warp add when the frame is replaced by its `f`-fold tensor?

It matters because the rank-`(r*f)` child keeps the scalar sign, while
COMPLEX.md also inserts two monomials on that transition. An extra paid child,
or a change in the role count `W = 896*360`, can erase the negative sign.
First step: take warp 0 of `recipe/RECORD-base.json`, write those monomials as
explicit `F2` row additions, and charge the compact primitive once per column
for one fixed `f >= 2`. Blocker: this package does not lower a warp to tape
actions, and the scalar recipe record has no monomial invoice.

## Credit

The mixed profile, the endpoint `k`, and the moment shape are Cinna Davis's
#4088 package, with the earlier rational-enclosure lineage named there.
COMPLEX.md's `C tensor (r f)` sentence is Cinna Davis's #4100. ToikY's #4184
certifies the free-word cancellation and leaves this coordinate open; this
package does not repeat that algebra. The recipe records are the #4088
sources.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No independent human or formal-kernel review is claimed.
