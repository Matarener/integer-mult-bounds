# Exact fibre `O(wV)` invoice for PR2753 `route_cube`

**Partial, conditional implementation bill. No new supplier, kappa, or H2 admission.**

Prepared by Wentao Li with substantial AI assistance. Apache-2.0.

## Result

On the pinned PR2753 owner-route primitive `routes.route_cube` (vendor bytes
unchanged from head `7dba5452a4071a856a0b11cebdcd2d3b6bcd7659`), fibre payload
`copy_bits` writes are exactly

| Regime | Partition calls | Fibre `copy_bits` writes |
| --- | ---: | ---: |
| `cap > 1` | `d² L` | `(2 d² L + 2) V` |
| `cap = 1` (`w = 1`) | `0` | `2 V` |

Here `M = q^w`, `L = bit_length(M)+1`, `cap = M/q`, `H = cap^(d²)`, `V = H F`.
For every checked `w >= 2` fixture this is at least `2 w V`, matching the
stated `O_q(wV)` route charge on this reached primitive. See [PROOF.md](PROOF.md).

This answers open question 2 of
`docs/research/selected-bit-caller-storage-map.md` for the **route** path only:
an exact checkable work lower bound on the retained decorated-key cube, under
complete-prefix order as implemented. It does not claim that every correct
router needs `Ω(wV)`, does not replace the routine by an H2 primitive, does
not price ordinary leaf `atom_swap`, and does not change the selected decimal
`0.001672660197076918`.

## Reproduce

Python 3.12, standard library, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/pr2753-route-cube-owv-fibre --check-only
python3.12 -B scripts/research_package.py --package research/pr2753-route-cube-owv-fibre
```

Direct gates (including `-O` via `need()`):

```sh
python3.12 -I -B research/pr2753-route-cube-owv-fibre/verify.py
python3.12 -I -O -B research/pr2753-route-cube-owv-fibre/verify.py
python3.12 -I -B research/pr2753-route-cube-owv-fibre/independent.py
python3.12 -I -B research/pr2753-route-cube-owv-fibre/test_package.py
```

Expected: `PASS_PR2753_ROUTE_CUBE_OWV_FIBRE`,
`PASS_INDEPENDENT_PR2753_ROUTE_CUBE_OWV_FIBRE`,
`PASS_PR2753_ROUTE_CUBE_OWV_FIBRE_PACKAGE_TESTS`.

## Soft overlap

| Predecessor | Difference |
| --- | --- |
| `binary-digit-cost-audit` | Exact digit/atom-swap bills; same bitstream bytes, not `route_cube`. |
| `selected-bit-fast-primitives` | Faster H2 replacement; does not invoice the retained cube. |
| `high-route-prefix-cost` | Wrapper bill on the later high-route path. |
| `linear-sign-total-traffic` | Sign only; leaves route/leaf binding open. |
| `selected-route-live-volume` | Storage peaks, not fibre time. |

Estimated soft overlap ≈ 0.35 (complementary invoice, not a retarget).

## Open next questions

1. Can an exact total-traffic invoice (key appends, `high_key` numerical work,
   Counter drains) replace the fibre-only lower bound? Start by metering
   `append_word` and Counter lifetimes on the same fixtures. Fibre
   `copy_bits` already matches `O(wV)`; full tape traffic would sharpen
   bootstrap constants.
2. Does the ordinary leaf `atom_swap` path admit a similarly exact matching
   `Ω(wV)` invoice without retargeting `binary-digit-cost-audit`? First compare
   PR2753 `bitstream.atom_swap` byte-identity with that audit. Soft-overlap is
   high if retargeted; this package closes only `route_cube`.

## Credit

David Arias (PR2753) stated the `O(wV)` route/leaf baseline and supplied the
recursive caller. Jose Manuel (PR2697/PR2809) supplies the routes/bitstream
lineage and physical caller that retains those routines. Nick Petalas
(PR2708) proved route live-volume storage for the same decorated cube.
Arham Tahir (`linear-sign-total-traffic`) closed the linear-sign traffic and
recorded this route/leaf follow-up. This package adds only the exact fibre
invoice and matching `Ω(wV)` lower bound on pinned `route_cube`.
