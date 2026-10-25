# Literal complete-fiber low commit and old-cache retirement

The actual helper462/frame506 route's `low_type_commit` now has a physical
consumer on a complete array: it moves each old-low block G0 to G0S modulo q,
preserves every high/spectator position inside that block, installs the result
into the same source owner and erases the old cache and private storage.
All runtime instructions are local symbol operations and unit head moves.

[PROOF.md](PROOF.md) specifies the actual layout and universal loop invariants.
For T low types, D high coordinates, runtime Q,Z, V=T Q^D Z and K=TDb old-cache
bits, the commit costs at most `128(T+D+1)V+16K+16+128D` transitions and
`(D+8)V+2K+64(D+1)` visited cells. A separate literal initializer prepares the
complete old cache in at most `5K+16` transitions. Runtime extent multiplication
is performed by nested tape loops, not a host arithmetic instruction. Finite
compilation and repeated source scans are explicitly charged; these large
constants are not optimized or admitted P3 coefficients.

**This completes the physical low-commit consumer, not the entire physical
route.** Composition with the old-low carry frontend and high linear route is
proved under their named contracts. Complete high-leaf implementation, actual
per-fiber isolation and descriptor linking, the first-coordinate two-OLD-swap
repair, native/ROW callers and P3 remain open. The changed full-cache layout
costs K owned bits and must be bound by any caller replacing a single-cache
layout. No new kappa, supplier admission or selected-frontier change follows.
The selected conditional record remains PR5413, 0.003027288235.

## Reproduce

Standard-library Python 3.12:

```sh
python3.12 -I -B research/bit-full-fiber-low-commit/verify.py
python3.12 -I -O -B research/bit-full-fiber-low-commit/verify.py
python3.12 -B scripts/research_package.py --package research/bit-full-fiber-low-commit
```

Expected: `PASS_FULL_FIBER_LOW_COMMIT`. Ordinary replay is read-only and checks
[RESULT.json](RESULT.json); explicit `--write-result` regenerates it.
Both directions execute the complete 48-type GL2(F3) domain at Q=1 or 3 and
Z=1 or 2, including every high/spectator bit and translated tape origins.
An independent local interpreter agrees with the retained machine on small
complete cases; all eight inputs of a three-block bit example are exhausted.
Actual S8 source checks use q=3,5,7 and w=2,4. They bind the mathematical source
map, not a materialization of the enormous full GL8 payload. Six controls reject
invalid type tables, dimensions, cache bits, stale old data, short payloads and
zero extents. A K=1000, T=D=V=1 regression exceeds the superseded 8K
cache formula and passes the corrected 16K+16 charge. A separate copied
Git-free test rejects source changes in normal and optimized modes. The written invariants establish all-width correctness; bounded
fixtures are not presented as its proof.

## Source and scope

Scientific base `32890bc5de034ab8fc93ac88ead7279a6a416d04`, priority 7.
Canonical investigation: [Discussion4945](https://github.com/CrocSwap/integer-mult-bounds/discussions/4945#discussioncomment-19172863).
The root checked 342 open PR bodies and 4,736 Discussion records and the released
preceding complete-low claim before assignment. Local checks found the explicit
unfinished full-fiber obligation in `bit-low-carry-lowering`. Arbitrary diffs
and unpublished work remain outside overlap coverage. Only this new package
changes; predecessor bytes and the selected record remain untouched.

The contribution narrows the assigned full-route objective to a completed,
priced physical low-commit stage after checking that its actual high/carry and
first-coordinate supplier dependencies are not implemented here. This is a
useful completed stage rather than a claim that all P2 obligations are closed.
[TASK.json](TASK.json) preserves the scope and remaining work.

## Open next questions

Bind the actual per-low high/carry calls to the prepared full-cache layout,
including source-fiber isolation, every runtime descriptor, the two OLD swaps
for cell0 and installation/erasure at every call. Begin with the actual
helper462/frame506 source and the cell0 carry1/cell5 carry124 fixtures, then
price the entire composition using the new cache and commit constants. The
missing linked physical calls and P3 envelope block a full-route claim; more
low-permutation samples or a smaller block-rescan constant do not resolve them.

## Credit

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
David Arias PR2776 supplies the literal machine, assembler and paid converter;
Charles Bethin retains the unit-carry predecessor; JoyboyBrian PR4989/5019 and
the retained carry frontend supply the actual route, runtime shear and source
carry obligations. Preserve Chris R/Clear1nsight PR4957, ai-nanachi
PR4760/4814/4326, rohanarun PR185/199, Maxime Fleury PR204, Cinna Davis, zxv,
Jacob Alan Sussman, Mark/Matarener and the retained ordinary/ROW/native/tape
lineage. The new contribution is the literal complete-payload low consumer,
its installation/retirement proof and explicit source-layout cost. No
independent human or proof-kernel review is claimed.
