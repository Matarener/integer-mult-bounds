# Independent audit of the multi-target CRT row join

**Scoped positive proof audit with finite exact corroboration; no new κ.**
PR #5496's current-row join composes across multiple right targets, including
mixed active/idle axes and a producer bank reused at growing or shrinking
widths, conditional on its inherited numerical Entry and ROM-producer
contracts. No defect was found in that implication. This is a separate
AI-assisted audit, not independent human or formal-kernel acceptance.

The audited source is JoyboyBrian's [PR #5496](https://github.com/CrocSwap/integer-mult-bounds/pull/5496)
at `a99afd7e0024af8367d5a2f6f4d2da57a1d13dd5`. Its published complete
joined fixtures have one active target at a time, and its h=4 four-axis
attempt did not complete. This audit adds the explicit target-loop
invariant, an exact retained-bank footprint, and executed multi-target
coverage. It does not redo the construction or present a larger parameter
sample as a universal proof.

[PROOF.md](PROOF.md) derives the all-admitted-parameter composition from
the two named source contracts. An idle target still consumes its entire
numerical record; the next active target therefore receives its own
offset. Every producer call returns to the same bank, with all old tails
blank, before the next target starts. Current padded coordinates are
queried, and the numerical whole-rotation field is never substituted for
one micro-row. The scope is one successful row invocation and its retirement.

For the unchanged producer's 52-role bank, including all four headers,
let P be the node's guide width and H its largest active target width.
The exact retained count is

```text
B(P,H) = 5 P 2^H (H^2+3H+1) + 2^H(4H-1) + 48P + 2H + 104.
```

Every role's extent is nondecreasing in h at fixed P; that proved property
allows a widest-target bound for this specific bank. The h=3 -> h=2 case
at P=11 still retains 9,086 cells; billing just the final target would count
3,084 and omit 6,002. The three other joined ports are counted separately
and exactly in the proof. These are finite-symbol tape cells, excluding
the numerical Entry and interpreter metadata. No program or recursive
invoice is changed.

## Evidence

[verify.py](verify.py) executes the unchanged join and unchanged numerical
and encoded-ROM producers. Its independent oracle searches the small CRT
congruences and exhausts the two-matching color constraints to reconstruct
canonical Beneš layers. It imports neither #5496's verifier nor the
retained Caller/CRT/Beneš reference implementations. Read-only observers
check the actual headers, every produced layer, selected ROM, bank identity,
heads, private work and historical tails before the caller disposes of them.

The frozen [RESULT.json](RESULT.json) contains nine actual caller cases and
13 complete producer invocations. Representative root-node results are:

| Case | Moduli; declared widths | Current state; global row | Right output |
|---|---|---|---|
| Two distinct offsets | `(5,7,3,2); (3,3,2,2)` | `(3,2,1,1); 4` | `(1,0)` |
| Shrinking bank | `(2,5,7,3); (2,3,3,2)` | `(1,4,7,3); 4` | `(6,3)` |
| Growing bank | `(2,5,3,7); (2,3,2,3)` | `(1,4,3,7); 4` | `(3,6)` |
| Leading idle target | `(2,5,3,7); (2,3,2,3)` | `(1,4,3,7); 2` | `(3,7)` |
| Trailing idle target | `(2,5,7,3); (2,3,3,2)` | `(1,4,7,3); 2` | `(3,3)` |

Other cases cover invalid left padding, an all-idle row with zero tape
work, and a nonroot node at the minimum guide `W=P=h+3=5`. All 63
numerical owned ports retire. The finite oracle independently checks 32
networks at all 236 input addresses. Seven execution mutations, two
algebraic discriminators, two storage controls and one typed-receipt control
pass. They detect stale offsets, wrong row selection, suppressed padded queries, omitted
layer/result disposal, skipped idle records, replacement backing, omitted
right prefixes, original/current-coordinate confusion, and boolean/integer
receipt confusion. The storage controls reject a last-target-only bill
and omission of the retained spool.

The adapter's tape actions are measured separately from the expensive
Entry and ROM calls and remain within the inherited `4096F` allowance.
This does not independently certify its full control-instruction constant
or the inherited arithmetic bill. Distinct backing identities and an
independent bank-plus-three-extras partition prevent alias double counting
and omitted producer storage.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3 -B scripts/research_package.py --package research/crt-multitarget-row-audit --check-only
python3 -B scripts/research_package.py --package research/crt-multitarget-row-audit
```

The registered replay runs normal and optimized Python serially, with a
300-second limit for each. Each concludes:

```text
PASS_CRT_MULTITARGET_ROW_AUDIT cases=9 producer_calls=13 controls=12 no_new_kappa=true
```

The normal replay compares the existing receipt and writes no evidence.
`--write-result` explicitly regenerates it. `--case growing_bank` selects
one diagnostic without claiming the complete package pass.

The audited pending source is vendored byte-for-byte, with its original
credit, paths, commit, Git blobs and hashes in [VENDORED.json](VENDORED.json).
The twelve scientific main-branch inputs are pinned in [SOURCES.json](SOURCES.json)
and declared in [VERIFY.json](VERIFY.json). The export also retains the
repository license and three original source notices. No pending Git object
or live GitHub access is required for direct replay. Generic provenance validation
still requires the package's main-branch Git history.

## Scope and remaining obligations

The base is `32890bc5de034ab8fc93ac88ead7279a6a416d04`, priority revision 7;
the task is `uniform-transfer-audit`, refined to this actual CRT caller.
[TASK.json](TASK.json) records selection and overlap. Coordination is in
[Discussion #4709](https://github.com/CrocSwap/integer-mult-bounds/discussions/4709),
following #5496's comment 19173182. JoyboyBrian's #5505 (cross-session
numerical bank reuse) and #5486 (fixed repair binary lowering) are
separate work.

The numerical and producer theorems, initial encoded input production,
uninterrupted whole-level updates, three-epoch key transport, production
geometry, binary numerical compilation, complete E(p,ell), native/outer
admission and the full multiplication theorem are not independently
validated here. No h=4 joined replay, Lean build or selected replay is run.
The selected record and all frozen predecessor files are unchanged.

## Open next questions

1. Connect this returned coordinate stream to a paid update of the actual
   axis-record source, then invoke the next row without host serialization.
   This would test the next physical caller boundary. Start with the
   five-row mixed h=3/h=2 example; the source ownership/update contract is
   the missing premise. PR5496 already identifies this task; it remains open.
2. Join one complete three-epoch exceptional key to these actual current-row
   inputs. Start with PR4716's two stale-offset discriminators and explicitly
   price each source-coordinate conversion and restoration. A proved
   single-row loop does not supply those changing-left-state descriptors.

The family decision is to stop after this audit; neither a larger ROM
sample nor a complete ordinary/outer run is justified by this result alone.

## Credit

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.

JoyboyBrian supplies #5496's join, #5092's ROM producer and #5053/#5219's
numerical components. Ali Romman supplies #5353's actual RowEntry.
Hiroki KUMAZAKI supplies the current-state CRT contract (#4716) and the
#4169/#4174 repair and mixed-width reservoir audits; Cinna Davis supplies
#4100's construction; ToikY supplies the explicit-width mixed caller
(#4195) and the Beneš arena refinement (#4192). Tekalign, Jose Manuel, Ryanson Jonathan, unpaidmoon, Douglas
Colkitt, John-Michael Smith and the retained source notices preserve the
physical/repair lineage. [vendor/NOTICE.md](vendor/NOTICE.md) identifies
the copied material. Apache-2.0. No independent human review is claimed.
