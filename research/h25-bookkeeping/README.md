# Complete H25 bookkeeping qualification

The three bookkeeping changes reduce median complete wall time by **20.9459%** and CPU time by **20.9302%** against fresh runs of PR5995's native C configuration. The fixed BCCBBC sequence retains the slower C3 sample and passes the declared 15% and within-arm-range noise gates. This result applies to the frozen historical H25 caller with its full retained observations in the recorded local environment.

| Metric | Native baseline median | Combined median | Saving | Larger within-arm range |
|---|---:|---:|---:|---:|
| Wall seconds | 27.168587597 | 21.477875710 | 5.690711887 | 3.594607136 |
| CPU seconds, including compiler children | 27.09 | 21.42 | 5.67 | 2.14 |

Individual complete pilots motivated integration; their percentages are not added and are not separately qualified factors. See `evidence/validation/COMBINED-GATE.json` and the independent final evidence review.

## Changes and retained contract

* Build 2,300 invocation-private operand sets instead of repeating 21,160,000 tail set constructions. Both original pairwise loops and all 10,580,000 intersections remain. A private one-use lease surrounds the authenticated CLI; unsupported state uses literal original fallback without replaying the prefix. Cleanup clears private sets even when a traceback survives.
* Deduplicate identical guard function records and construct failure messages only on failure. All distinct predicates, closure reads and native-entry freshness checks still execute at their original boundaries before arithmetic or fallback. There is no saved PASS.
* Encode admitted complement records through one checked, stateless native call. Original snapshots, exact types, arbitrary-width JSON fallback, immediate hash updates and counters remain. All 238,685 records and 55,839,507 canonical bytes retain their original identity and prefixes. New encoder-entry freshness is checked at every original native boundary.

Every candidate process pays both cold native builds, all old independent dense/source/type/width/fallback controls, the complete new control union, admission/source checks, conversions, retained witnesses and serialization. The full original assertion-on CLI and real upstream source verification remain. Certificate, stdout, lossless typed return, ordered witnesses/ranks and complement observations match the original anchor. The engineering driver has its own digest; the original driver digest is separately authenticated as reference identity.

The immutable `payload/` preserves all v4 bytes and its stage manifest. Publication checkouts use regular Git modes; wrappers restore measured readonly permissions only in new external copies. The two admitted Fraction source hashes identify the recorded local runtime and the retained official CPython 3.12.15 reference. Unknown source hashes are rejected. Hosted interpreter/profile receipts must be checked separately.

## Reproduction and delivery status

Requirements: Linux, CPython 3.12, `/usr/bin/python3.12`, GNU time, an existing C compiler and Python headers. No dependency installation is required.

```sh
python3.12 -B scripts/research_package.py --package research/h25-bookkeeping
# Optional one fresh complete replay, retaining new external evidence:
python3.12 -B research/h25-bookkeeping/replay.py C /tmp/h25-bookkeeping-new-evidence
```

The registry runs finite normal/O, one complete combined C correctness replay and canonical transport. Root `replay.py B` selects the **PR5995 native C baseline**, and `C` selects the combined candidate. Historical commands inside `payload/baseline/` retain their old meanings and are not this package's entry points. Local evaluation/index scripts are labeled historical audit sources.

One parent serial queue performed the experiment: 180s/command, 1 GiB sampled process-group RSS, 600s initial and 1500s total round allowance. All 22 original attempts total 332.099907814s, including the 2.822723142s optimized fixture failure. Its two assertion-only callback expectations were repaired without changing the adapter; fresh normal/O passed. Earlier sources, all receipts and all six samples remain. Publication wrappers use 150s inner/180s outer limits and add source authentication/copy/cleanup costs; their correctness runs do not establish another performance factor. `VALIDATION.json` distinguishes pending/final delivery checks from the completed local performance result.

## Credit and scope

Chris R / Clear1nsight with substantial OpenAI Codex and user-requested Astra xhigh research, implementation and independent source/evidence review; parent alone executed compiler/scientific work. Credit PR5995, PR5929 and original CrocSwap/P104 authors and notices, with the adjacent native/GMP/FLINT precedents PR5168/5382/2853/3143 retained in predecessor evidence. New contribution code is Apache-2.0; the unmodified CPython Fraction reference retains its author notices and `CPYTHON-LICENSE.txt`.

This is finite engineering evidence for the complete frozen historical caller. It establishes no bare-CLI factor, selected-frontier change, all-size C safety theorem, new kappa or performance transfer. The separate PR5864 objective and paused mathematics/feeds/automations remain separate.

## Open next questions

Another caller or runtime requires its own authenticated source/output contract, independent controls and complete paid comparison. Independent reproduction on another host is useful; hosted correctness does not establish a hosted speed factor. At package preparation, exact-head hosted validation and the observed child Fraction profile remain pending; publication readbacks record their eventual disposition. TASK.json gives the bounded first steps and blockers.
