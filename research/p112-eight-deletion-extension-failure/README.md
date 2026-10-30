# Quadratic extension on P112 fails at eight deletions

**Finite exact certificate; no new κ.** The global quadratic-extension
threshold left open by
[PR5697](https://github.com/CrocSwap/integer-mult-bounds/pull/5697) is
exactly **7**.

## Result

Use the doubled E8 root lines, FRAME0 and P112 of Josie Elliston's
[PR1650](https://github.com/CrocSwap/integer-mult-bounds/pull/1650). For
X in P112 let L = P112 minus X and let M_L be the incidence matrix of all
orthogonal eight-line frames contained in L. Global quadratic extension
means ker(M_L) is exactly the 35-dimensional space of restrictions of
ambient trace-zero quadratics.

PR5697 proves extension for every |X| <= 7. This package shows that it
fails for some |X| = 8. The maximum threshold is therefore exactly 7.

Each of the 1260 frames avoiding FRAME0 has eight lines, and every P112
line lies in 90 of them. For a line l, the other lines share 10 such frames
with l (51 lines) or 15 (8 lines). Call those eight the heavy octet X_l.
Every live frame through l meets X_l, so deleting X_l isolates l.

The 112 lines produce 14 distinct octets, and they pair off. Deleting one
octet isolates exactly the eight lines of its partner octet. For each of the
14 octets, exact rational elimination gives:

| Quantity | Value |
|---|---:|
| live lines | 104 |
| live frames | 648 |
| rank of M_L over Q | 62 |
| dim ker(M_L) | 42 |
| dim of quadratic restrictions to L | 35 |
| dim of (quadratics + isolated-line indicators) | 42 |

The kernel is seven dimensions larger than the quadratic restrictions, so
extension fails. The excess is fully explained: the eight isolated-line
indicator vectors and the quadratics span the whole kernel.

The PR1668 eight-deletion fixtures recorded in PR5697 keep extension
(rank 69). Those are D failures with extension intact. The octets here
are extension failures. Eight deletions therefore contain both kinds.

## Claim type and limits

- Finite exact certificate for 14 explicit deletion sets: exact rational
  ranks, with no modular or floating-point step.
- The threshold value 7 combines this certificate with PR5697's theorem for
  |X| <= 7. That theorem is cited, not rechecked here.
- No classification of all eight-deletion failures, no new rigidity floor,
  decoder, supplier, invoice or κ. The selected frontier is unchanged.
- Author-checked only. Independent human and proof-kernel review are unclaimed.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
python3.12 -B research/p112-eight-deletion-extension-failure/verify.py
python3.12 -B scripts/research_package.py --package research/p112-eight-deletion-extension-failure
```

Expected status: `PASS_P112_EIGHT_DELETION_EXTENSION_FAILURE` (about 15 s).
The verifier pins and authenticates the PR1650 geometry source
`research/complex-rank8-rigidity-p105/verify.py`. It also runs controls. All
seven-subsets of one octet isolate nothing and have the PR5697 rank
|L| - 35. A damaged octet fails to isolate its line.

## Open next questions

1. Classify all eight-deletion failures of global extension up to the FRAME0
   stabilizer. A greedy eight-set found during this work isolates one line
   and has kernel 37. It is not one of the octets, so isolation by a heavy
   octet is not the only shape. First step: extend the PR1650 orbit cover to
   eight deletions and run the exact global rank test on each representative.
2. Find the maximum kernel excess over 35 at eight and nine deletions. Nine
   is the uniform injectivity limit (|X| <= 9). No search beyond the
   octets is claimed here.

## Credit

Produced by Nick Petalas. Geometry, FRAME0 and the frame enumeration are Josie
Elliston's PR1650. The extension theorem through seven deletions and
the open question are Ali Romman's PR5697, which builds on Josie
Elliston's PR1668, Andrey Mas's PR1560 and Nick Petalas's PR5238.
Apache-2.0.
