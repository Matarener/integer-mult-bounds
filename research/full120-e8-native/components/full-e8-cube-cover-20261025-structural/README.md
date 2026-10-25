# Full120 E8: a new15-cube native inventory with actual physical normalizers

The actual P112 geometry extends to all120 projective E8 roots by appending
2e_i for i=0..7, with binary labels7,25,42,52,76,82,97,127. The full set is
closed under every one of its120 root reflections. The 14 original cubes
generate an orbit of9450 eight-root cubes. Every cube in this orbit passes
the actual binary native geometry test, and an exact cover partitions all
120 roots into15 cubes. The eight additional roots are mixed into seven
new blocks; they are not assumed to form an involutory isolated block.

COVER.json contains all exact root/reflection/orbit/cover data. The complete
real mode Gram is60I, so C=MM^T/4 has eigenvalue15 on eight modes. For the
new block native K, K^2=I, KM=-M and KC=CK=-C. Thus A=I-C has eigenvalues
1 and-14, A^-1=(A+13I)/14, E=K+C/14 and E^-1=K+C.

NORMALIZERS120.json preserves the `mode_columns`, `ports[*].q` and
`ports[*].K_word` consumer interface. It adds the explicit `cover15`
partition, which must replace grouping by four-coordinate root support.
All120 Weyl lifts are ordinary binary P matrices preserving weight modulo4,
and commute exactly with full R9. Each of the eight new normalizers is one
old normalizer followed by one such actual P. All32 new forward frame
wrappers are emitted as literal ordinary P/D/X/phase words, with absolute
phase checked.

The generic native rank profile for this actual base inventory is120
children of each H2,H3,H5,H6, with240 arbitrary original main fields.
The complete phase-native F/B word is separate work in
`/tmp/full-e8-native120-20261025-structural`.

The odd3 geometry has120^3=1,728,000 owners and modal rank22,016, reducing
the modal ratio from5/343 to43/3375. Its nonzero C spectrum is225/2 on
21,504 modes and-1350 on512 modes. Global physical cube geometry and a
phase-complete n25 representative are separate work in
`/tmp/full-e8-odd3-native120-20261025-structural`.

There is no terminal E decoder, complete productive caller, new kappa,
scientific adoption or selected-frontier change in this package.

Read-only reproduction, Python3.11+ standard library:

```
python3.11 orbit_cover.py
python3.11 -O orbit_cover.py
python3.11 normalizers120.py
python3.11 -O normalizers120.py
```

All four normal/optimized checks pass. Default commands compare semantic
receipts and do not write. `--write` is explicit author mode.

Credit the retained E8/P112 root data, Dugongue's PR4929 coded source, the
coded-native-caller normalizers and original Clifford/compiler lineage,
and Ali Romman's odd-E8 direct-sum framework. New material uses substantial
OpenAI Codex assistance. Apache-2.0; no independent human or kernel review
is claimed.

## Open next questions

- Install the explicit15-cube partition in the actual phase-native source;
  verify all240 independent main columns, paid paths and inverse-transpose.
- Verify the entire15^3 family in one global I25 coordinate chart and emit
  a phase-complete product cube containing the added roots.
- Retain the uncancelled terminal code E. A paid decoder or changed target
  caller remains necessary before any improved multiplication bound.
