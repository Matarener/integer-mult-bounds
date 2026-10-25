# Sixteen groups are necessary when eleven original P112 frames are retained

Among even orthonormal partitions of the literal selected P112 labels that keep
at least eleven of PR3356's thirteen full frames as complete groups, the minimum
is exactly **sixteen groups**. A fifteen-group construction must change at least
three original frames. This proves a sharp local obstruction behind PR3370's
previous unproved SAT reports; its sixteen-group upper witness is unchanged.

Both independent checkers exhaust all 78 possible 24-port repair domains. None
has a cover by four or fewer even orthonormal groups. The bitset checker tests
complementary unions of two groups. The second checker uses explicit binary
coordinates and a separate cover search. Their complete counts and proof are in
[RESULT.json](RESULT.json) and [PROOF.md](PROOF.md). The controls include 36 complete
small-domain oracles and positive and failing cover fixtures.

For the two-support-per-group query recipe this gives a sharp **32-support**
minimum within this retained-frame class. It is not an arbitrary-fitting-rank
lower bound. Unrestricted fifteen-group attainment, non-colouring fits and
physical realization remain open. There is no new kappa or selected-frontier
change. A complete supplier, source access, frames, restoration, hosting,
precision/tape, all-size/compiler and outer-transfer proof are not supplied.

## Reproduce

From the repository root, with Python 3.12 or later:

```sh
python3 -B scripts/research_package.py --package research/p112-even-group-attainment
```

The registered replay runs both complete checks and all controls in ordinary
and optimized Python. No solver, numerical library or pending Git object is
required. The only live input outside this package is
`research/adaptive-kernel-demotion/inputs/DATA-PHASES.json`, pinned to canonical
main `6f100d4bb5083f8c35d96fd95a539811c62f245c`. SOURCES.json pins the catalogue,
selected record and that live input. SOURCE-EXPORT.json authenticates exact
retained PR3356 and PR3370 certificate bytes. No predecessor code is imported.

Direct proof commands also work in a Git-free export with that same directory
layout and live input:

```sh
python3 -I -W error -B research/p112-even-group-attainment/verify.py
python3 -I -W error -B research/p112-even-group-attainment/independent.py
python3 -I -W error -B research/p112-even-group-attainment/controls.py
```

Optimized commands add `-O`. Every proof obligation uses an explicit exception,
so optimization does not remove it. Reproduction reads committed evidence and
writes no package files. Source/publication-byte checks, the portable export and
meaningful corruption controls are recorded in VALIDATION.md. The selected full
cold replay is outside this changed scope and was not rerun.

## Scope change and next decision

This takes the current P112 handoff under `complex-rank-shape-decoder`, narrowed
to exact finite query grouping. It does not claim the card's complete native
profile or five-percent ceiling gate. PR3370's published one-total full-plane
tariff remains 224. The local exclusion identifies which source frames a future
construction must disturb; it does not justify treating unpriced physical costs
as free or starting a new supplier search campaign.

Construction pilots did not find a fifteen-group partition. Their UNKNOWN or
unproved UNSAT statuses are not used in the proof. In particular, a three-frame
pilot remains incomplete. See PROOF.md for its precise domain and outcomes.

## Open next questions

- Can a fifteen-group partition change at least three of the original frames?
  This would meet PR3373's reported global construction-class lower bound and
  improve the exhibited query interface. Start with the exact literal labels
  and a 32-port three-frame-plus-tail domain. The local two-frame exclusion is
  proved here; the larger pilot's 133 unknown cases and 61 unrun cases remain
  open, and its 92 unproved UNSAT reports are not certified exclusions.
- Can a changed fitting matrix or physical contract lower the complete native
  bill? First specify the scalar factors, the source/reader planes and a paid
  consumer with restoration. A smaller group count alone does not reduce the
  inherited full-plane charge or admit a supplier.

## Sources and credit

The thirteen-frame certificate is Nick Petalas's PR3356, exact
`a91a44a049cd6114d0edaea714914b64f90c601d`. The sixteen-group repair, its rank 32
interface and its earlier negative solver reports are Tekalign's PR3370, exact
`4cae85b18712b85a39905e51bde17346ccc5b805`. Nick Petalas's PR3373 supplies the
current handoff and global fourteen-frame result; this local proof does not
import or replay its exhaustive search. Matarener/Mark's PR3335 supplied the
preceding rematching and packing question.

Credit ctoth, ywz65, Sagar Thakrar, Cinna Davis, Adam Gall, Jeremy Diviney,
Philippe Van Velzen and the retained E8/P112/compiler/supplier lineage.
[Canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/1587#discussioncomment-19008359).
Apache-2.0. Finite computational proof; independent mathematical review is open.
