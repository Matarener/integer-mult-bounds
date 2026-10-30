# Conditional kappa 0.00310626335 from three helper cleanups

This construction raises complete conditional kappa from
**0.00310440546 to 0.00310626335**, a gain of **0.00000185789**
(about **0.05985%**) over
[PR #5627](https://github.com/CrocSwap/integer-mult-bounds/pull/5627).
This is a small gain. The requested large improvement is not established.
The selected frontier is not changed by this package.

Three exact helper relations remove scalar contacts on main roles 55, 49
and 80. Each role can then replace an H1+H5 path with H6. The local paid
delta is `-3 H1 -3 H5 +3 H6`. All independent inputs, productive targets
and owned operations stay fixed. The complete caller saves 54 paid calls.

Read [PROOF.md](PROOF.md), [WITNESS.json](WITNESS.json),
[RESULT.json](RESULT.json), [SOURCES.json](SOURCES.json), and
[VALIDATION.md](VALIDATION.md). The constructor checks every relation before
it emits the new [word](WORD.json.gz).

| Complete quantity | Value |
| --- | ---: |
| Paid calls | 66,492 |
| Productive targets | 12,958 |
| Rank-mass surplus | 760 |
| Public inputs / helpers per full call | 743 / 535 |
| Owned roles / lifetimes / peak | 9 / 11 / 2 |
| Local events | 25,448 |
| Raw crossing | (0.00310626336369, 0.00310626336370) |
| Tested saving | 0.003106263355 |
| Claimed conditional kappa | 0.00310626335 |

The complete cost includes helpers, native maps, input/output normalizers,
main adapters, scalar bases, COPY/CLEAR, allocation, routes, thin queries,
whole idles, compiler completion and rounding. Two rational interval engines,
all compiler conditions and all 58 outer conditions pass. The ordinary BIT
contract stays at 0.0034. The fixed-invoice ceiling is the raw crossing above;
it is not a ceiling over constructions.

## Reproduce

Use Python 3.12 and its standard library, from the repository root:

```sh
python3 -B scripts/research_package.py --package research/p104-neutral-helper-cleanup --check-only
python3 -B scripts/research_package.py --package research/p104-neutral-helper-cleanup
```

The registered command runs normally and with `-O`. Expected markers are
`PASS_P104_NEUTRAL_HELPER_KAPPA_00310626335` and
`PASS_REGISTERED_RESEARCH_PACKAGE`. Direct replay needs no Git or network:

```sh
python3 -I -W error -B research/p104-neutral-helper-cleanup/verify.py
python3 -I -W error -B -O research/p104-neutral-helper-cleanup/verify.py
```

Normal replay is read-only. `--write` regenerates the word and receipt.
The verifier authenticates the exact source archive and all 36 payload files
before it imports source code. It checks all 565,504 endpoint coefficients,
2,916 signed native maps, the complete physical caller and the full cost.
Controls reject a false cancellation, wrong cut, missing input basis,
missing owned erasure, extra target credit and unpaid query. The native,
controller and pricing checks retain their own controls.

## Source and credit

The consumed source is [PR #5627](https://github.com/CrocSwap/integer-mult-bounds/pull/5627)
at `ed4dc88a09a7d201971f6603b8c2074e95dd9c32`:
[source proof](https://github.com/aliromman/integer-mult-bounds/blob/ed4dc88a09a7d201971f6603b8c2074e95dd9c32/research/p104-helper-subspace-splits/PROOF.md),
[source word](https://github.com/aliromman/integer-mult-bounds/blob/ed4dc88a09a7d201971f6603b8c2074e95dd9c32/research/p104-helper-subspace-splits/WORD.json.gz),
and [source notices](https://github.com/aliromman/integer-mult-bounds/blob/ed4dc88a09a7d201971f6603b8c2074e95dd9c32/research/p104-helper-subspace-splits/NOTICE).
Its official self-contained export is retained. Reproduction does not require
a cached unmerged Git object. The exact word, caller and all shared proof
engines are unchanged source inputs. The derived pricing file changes only
the declared claim, comparison and paid count; its byte-level derivation is checked.

Ali Romman supplied the new three relations with substantial OpenAI Codex
assistance. The same assistant performed the author checks; no subagents or
independent scientific review. The helper-boundary method extends
[PR #5602](https://github.com/CrocSwap/integer-mult-bounds/pull/5602).
The source package supplies the complete composition of
[PR #5601](https://github.com/CrocSwap/integer-mult-bounds/pull/5601),
[PR #5605](https://github.com/CrocSwap/integer-mult-bounds/pull/5605),
[PR #5612](https://github.com/CrocSwap/integer-mult-bounds/pull/5612),
[PR #5606](https://github.com/CrocSwap/integer-mult-bounds/pull/5606)
and [PR #5599](https://github.com/CrocSwap/integer-mult-bounds/pull/5599).
Its notices credit flyingviper's relays, Scratch-net's prepared helper,
Pierre-Loic Doulcet's cascade, Joel Pulikkan, DreamingOfClouds, thu-nmrc,
Gareth Davidson, David Arias, Cinna Davis, Jacob Alan Sussman, zxv and
Cao Yifan, with the earlier geometry, BIT and analytic sources.
All notices remain in the retained export and pricing module. Apache-2.0.

The discovery first passed on
[PR #5613](https://github.com/CrocSwap/integer-mult-bounds/pull/5613) at
`32f23af8790cc3c435bb1f495d861332b4f000e3`. That source has the same signed
moment but 72 more H5 paid calls and 72 more H5 targets. It is comparison
evidence, not the consumed input. Its counts are not combined with this receipt.

## Coordination and limits

The frozen research base is canonical main
`6cf7a683f447b9f1e2333791907fd92be5009a63`, priority revision 7.
The [canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5125#discussioncomment-19154639)
records the source pins, live overlap checks and released finite screens.
The separate Discussion5600 main-port retirement campaign is excluded.
The final publication checkpoint is recorded in `VALIDATION.md`.

The five selected assumptions remain: native implementation at all widths,
owned erasure, uniform compiler closure, precision/tape cost and analytic
recovery. The helper endpoint contract also remains. The huge uniform word
and complete rounded multiplier are not materialized. This package does not
claim independent acceptance, a proof-kernel theorem or global optimality.

## Open next questions

An independent reviewer can check the three prefix relations and transport
products, then replay the full package. Further coordinated bases may remove
more scalar contacts, but the larger exploratory screens have not produced
a new complete gain. A new construction must first check current claims and
must include every changed target and paid operation. [TASK.json](TASK.json)
records the next bounded question and its blockers.
