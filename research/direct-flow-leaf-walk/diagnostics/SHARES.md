# Diagnostic: share and depth stability through N ≈ 1.2·10⁹

This addresses the "stability of the shares" caveat in the README and in `SATURATION.md`. Run it with
`python3.12 -B leaf_share.py 2 9` (about 2 minutes). It uses the package flow, copied as
`overlap_flow.py`, at the start and near the end of each level.

| G | N | leaf share of exit potential | boundary depth | source depth |
| --- | --- | --- | --- | --- |
| 2 | 3,026 / 14,822 | 0.885 / 0.917 | 1.845 / 1.900 | 2.438 / 2.345 |
| 3 | 15,126 / 74,112 | 0.923 / 0.904 | 1.914 / 1.773 | 2.390 / 2.440 |
| 4 | 75,626 / 370,562 | 0.918 / 0.902 | 1.798 / 1.904 | 2.438 / 2.521 |
| 5 | 378,126 / 1,852,812 | 0.921 / 0.910 | 1.818 / 1.873 | 2.425 / 2.502 |
| 6 | 1,890,626 / 9,264,062 | 0.914 / 0.911 | 1.851 / 1.845 | 2.458 / 2.480 |
| 7 | 9,453,126 / 46,320,312 | 0.915 / 0.906 | 1.830 / 1.864 | 2.453 / 2.490 |
| 8 | 47,265,626 / 231,601,562 | 0.908 / 0.908 | 1.867 / 1.853 | 2.482 / 2.487 |
| 9 | 236,328,126 / 1,158,007,812 | 0.911 / 0.910 | 1.861 / 1.839 | 2.483 / 2.474 |

The leaf share, the boundary-exit depth and the source depth all settle, at about 0.91, 1.85 and 2.48,
while the leaf depth keeps growing (README). This supports the stable-share assumption behind the
asymptotic cap of about 0.00257. It is finite evidence, not a proof.
