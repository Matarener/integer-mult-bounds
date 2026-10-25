# Exact warp0 entrance cap with adaptive native frames

This source-bound negative audit of [Dugongue PR3929](https://github.com/CrocSwap/integer-mult-bounds/pull/3929) proves the unique maximal entrance at zero-based warp0. It does not produce a new kappa or a physical supplier.

Freeze PR3929 at `0c0e31cf12e8f4f07e8419a6d33ae85129fb5a01`, its literal BASE-WORD, A/cut and earlier B prefix, scalar operations/coefficient/order, native maps/order, register inventory and terminal caps. Scalar frames must contain their original floors; later native boundaries may enlarge compatibly with their fixed maps. Warp0 is array index zero, lender243 at B916: eight other native events occur earlier chronologically.

## Result

The original entrance U0=span(261,133,85,45) has dimension4. The maximal legal entrance is C0=U0+span(7), with RREF basis (258,130,82,42,7), dimension5. Exactly two of the374 superframes containing U0 are legal: U0 and C0. All372 others fail fixed terminal caps. A backward capacity proof and independent forward enumeration of all31 quotient lines agree. This excludes all larger entrance subspaces even when later native boundaries adapt; it does not exclude larger scalar frames within C0.

The canonical least-join completion has complete rank profile `{1:2467,2:711,3:223,4:103,5:20,8:8}`, versus baseline `{1:2440,2:725,3:224,4:102,5:20,8:8}`. Its difference is `27 H1-14 H2-H3+H4`, a strict loss for every tariff r^q, 0<q<1, by the exact factorization in PROOF.md. It changes32 scalar frames and one native boundary, pays one identity climb, and keeps the native inventory unchanged.

Least frames are not least price: the retained PR3929 published nonminimal completion has the same entrance/boundary subspaces and is strictly cheaper than the canonical completion for all these power tariffs. The verifier checks original-frame floors and paired scalar records, then proves canonical-minus-published `-H1+2H2+3H3-3H4` has capped sums (1,3,3,0). Both remain losing examples against the baseline. An explicit min(rank,2) countercontrol prevents extending the first loss claim to every concave tariff.

## Reproduce

Python3.12, standard library only, no network or Git required inside the package:

```sh
python3.12 -I -O -Werror -B research/warp0-entrance-cap/verify.py
python3.12 -I -O -Werror -B research/warp0-entrance-cap/independent.py --word research/warp0-entrance-cap/source/inputs/BASE-WORD.json.gz --check research/warp0-entrance-cap/INDEPENDENT-RESULT.json
python3.12 -I -O -Werror -B research/warp0-entrance-cap/test_cli.py
```

`verify.py` uses point-set joins and full forward billing; `independent.py` uses separate binary Gaussian elimination, backward intersections/preimages and its own forward suffix walk. The independent checker imports neither primary nor retained executable code. `RESULT.json` and `INDEPENDENT-RESULT.json` are compared in full, rather than trusting PASS strings. `ORIGINS.json` authenticates retained bytes and Git blobs; SOURCES.json binds selection provenance. The source compiler and exact binary action replay validate forward, dual and cleanup-boundary algebra on arbitrary dirty inputs. None is a new native phase calculation.

## Scope and predecessor credit

Credit Dugongue PR3929 for transported frames, compiler and the published control; dataisfire PR3734, zxv PR3682, Ross Richardson PR3605, Jeremy Kothe, Sagar Thakrar PR3687, Arham Tahir PR3693 and the retained source lineage. Original notices are copied byte-for-byte. New material is Apache-2.0, prepared for ToikY with substantial OpenAI Codex assistance, including separately implemented AI verification; no independent human or proof-assistant review is claimed.

This audit preserves the inherited temporary centre-descent accounting convention and restore[191] unchanged. It certifies frame feasibility and the stated symbolic profiles, not a fresh native phase proof, physical invoice, complete owner/idle allocation, outer recurrence or supplier admission. The selected record remains unchanged. PR3890 and PR3926 are separate preserved contributions.

## Open next questions

Optimize larger legal scalar frames inside C0, or name a changed map/word/endpoint/event before another search. Any promising profile still needs exact transported-native phase recipes, all idle/hosting/cleanup costs and a complete physical caller. The current canonical loss does not close these obligations or establish global price optimality.
