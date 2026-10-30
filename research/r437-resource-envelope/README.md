# R437 checkpoint resource envelope

This package proves an exact checkpoint-component cost and lifetime visited-cell
law for the unchanged physical caller codecs used by the R437/OQ4 adapter. It
also prices the elementary capsule/grant/header scans. The complete production
preparation and full caller reserve remain open.

The useful distinction is between **sum over call occurrences** for time and
**maximum weighted active path** for parking backing. Empty final storage does
not erase visited cells; repeated siblings reuse backing but repeat scans.
The proof pairs amortized complexity with a weighted depth-first pebble schedule.

For one stream frame with R canonical roles and L body symbols, the complete
read/write/move invoice is `(61L+23R+14, 26L+6R+2, 52L+20R+10)`.
After adding the retained numerical codec, the auxiliary checkpoint action
count is `139L+51R+32S+23B+72p+C_0+C_1+59`. Every call occurrence pays it.

A call stores `A=2+R+4L+p+S` parking cells. Across an arbitrary finite completed
call forest, parking plus shared-port backing is exactly
`max_active_path sum A + max_record_bits + 3`, including erased visited cells.
[PROOF.md](PROOF.md) states all boundary premises, derives the counts, includes
complete capsule-copy/adoption, grant and header scan costs, and isolates the
remaining production term Pi instead of treating it as free.

PR3967 at `32af060614fefa9729c86370524c2e72265acd76` reports 29097 canonical
roles for R437 source `a24f9ff95c12fd0b6792e3f710569237efd72db2`. Our empty-body
calibration executes that many actual codec records. It is explicitly a
parameter calibration, not a new R437 catalogue reconstruction or valid
full-volume residual. The theorem applies to any finite R. At depth d, chronological Program bodies alone contribute the explicit quadratic term derived in PROOF.md; the admitted root/history absorption remains a separate premise.

## Reproduce

```sh
python3 -B scripts/research_package.py --package research/r437-resource-envelope
```

Python 3.12 and the standard library suffice. The registered commands check
pinned canonical inputs, exact receipts, optimized execution and Git-free
source-corruption controls. The narrow loader runs unchanged component code;
it deliberately does not initialize the complete selected compiler. The
append_tape and history-extend primitives are extracted from authenticated ASTs.

[RESULT.json](RESULT.json) records 397 random complete calls in 32 forests,
65 calls in the sibling fixture, the 29097-role empty calibration and primitive
scan checks, a three-grant checkpoint and 20 literal history extensions. The proof is a source-bound mathematical derivation; finite checks
are evidence, not formal-kernel verification. No whole GL64 payload, production
ordinary/native/router cohort, selected cold replay, Lean or Docker was run.

## Coordination and scope

Explicit donor assignment refines `selected-stock-envelope`: one actual physical
caller component is bounded, rather than rerunning selected cutoff arithmetic.
Main `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority revision 6, is the frozen
base. The shared investigation claim is
[PR3967 comment](https://github.com/CrocSwap/integer-mult-bounds/pull/3967#issuecomment-6262146714).
The local overlap helper found related PR2753/2769/physical caller work; remote
coverage failed because gh is unavailable. Live GitHub search and the parent's
Discussion1166/2319 and R437 checks supply partial overlap coverage. Existing
PR2769's numerical invoice is credited and retained; the new result is the
stream invoice, paired lifetime maximum and actual preparation-scan join.

## Open next questions

- Bind each canonical, scratch, handoff and output role's maximum extent to the
  complete current-source producer. Start at `prepare_child`, then cover each
  atomic primitive between cuts. This is needed for a whole-caller visited-cell
  coefficient; the existing conditional logical ledger does not instantiate
  those maxima by itself.
- Bound Pi in equation (6), including directory/program production and full
  root-coupled history evaluation. Start with one source-bound child constructor
  and retain original-width stock and prefix multiplicity. Another controlled
  returned payload will not close this obligation.
- Review whether a cheaper equivalent codec can reduce empty-role overhead
  without introducing unbounded role maps or changing restoration identity.
  Start with the fixed R delimiter term and a complete alternate invoice.
  This is an optional future mechanism, not part of the present proof.

Credit Jose Manuel / jmbarrancoml, ywz65, David Arias, Nick Petalas and retained
Word/record/continuation authors; ai-nanachi, zxv, Ali Romman, Sagar Thakrar and
R437/native/selected lineage. Immediate predecessors: PR3936/3950/3967. Complementary logical-backing results by Ross Richardson / PR2874, Kumagi / PR2882 and Nick Petalas / PR2708 are credited without importing them as a whole physical reserve.
Detailed provenance and precise reuse are in PROOF.md and SOURCES.json.
New work by Chris R / Clear1nsight with substantial OpenAI Codex assistance.
Apache-2.0; no source or frontier record is changed.
