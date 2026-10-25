# Independent reconstruction of PR4441's complete complex invoice

**The declared finite invoice reproduces. No accounting discrepancy was found
in the checked scope.** This package independently derives the paid transition
and helper-width profiles of
[PR #4441](https://github.com/CrocSwap/integer-mult-bounds/pull/4441) at
`5f9d871c6bd1b9e34db5a7ea5ef08a908e94db39`, then reconstructs the complete
query-thinned controller invoice. It claims no new kappa or supplier admission.

| Quantity | Before helper retiming | After helper retiming |
| --- | ---: | ---: |
| Paid calls per full native invocation | 3,554 | 3,363 |
| Productive helper rank mass per invocation | 3,301 | 3,434 |
| Paid rank mass per invocation | 5,157 | 5,290 |
| Complete controller productive fields | 11,560 | 11,560 |
| Complete controller paid calls | 72,902 | 69,273 |
| Complete productive rank mass | 258,271 | 260,798 |
| Complete paid rank mass | 257,471 | 259,998 |
| Rank surplus | 800 | 800 |

Each of 19 full invocations removes 191 paid calls, totaling **3,629**. The
local paid-count changes by rank are `{1:-234, 2:-198, 3:+221, 5:+20}`.
Both productive and paid mass increase by 133 per invocation. This changes
the rank distribution without creating an unpaid rank-mass gain.

## What is independently checked

`audit.py` imports no predecessor implementation. It uses binary Gaussian
elimination to check all 1,159 frame bases and nested transitions. From the
literal native programs it collects a separate chronological contact path for
each of 632 persistent roles, in both orientations. It binds every one of the
117 entrance, 42 exit and 395 scalar-frame patches to its original location.
The 17,253 persistent-only scalar gates have the stated inverse-transpose
correspondence. Unmodified warp contacts are retained. The resulting per-role
bills agree between orientations; 319 role bills change.

The empty patch is a positive control: contact-derived costs equal the source's
explicit climbs. All eight complete owned-center paths remain charged at rank
eight, using the predecessor's unsplit-center convention; the stored native
file expresses each as two adjacent rank-three/rank-five events.

A second implementation replays the entire controller as sparse rational
Laurent row expressions on all 34 formal input coordinates. It executes the
actual right boundary, 164 physical events, and left boundary, separately
checks the two boundary programs against their matrices, and derives the
diagonal monomials. It counts **19 full calls, 16 copied query shears, 16 whole
idle events, 96 additions and 17 signed swaps**. Each query is charged 112
rank-one jobs; the idle events cost 3,584 jobs. Main output ranks come from the
replayed monomials, not the stored diagonal or invoice. The expected receipts
are compared only after reconstruction.

These are separately written checks after reading the source formats and
proof; they are not a blind replication or independent human review. The
source author's existing native, phase and numerical checks are not relabelled
as this package's independent evidence.

## Why the surplus is conserved

Let `d(f)` be the dimension of a frame. For one persistent role, sum the paid
ascending transitions along its chronological path. Fixed warps can change
frame dimensions without belonging to that sum. Telescoping therefore gives

```
paid rank mass = d(final) - d(start)
                 - sum_over_fixed_warps(d(warp_out) - d(warp_in)).
```

The checker verifies this equality separately for every role in both
orientations. Subtracting the old and new equations cancels all fixed warp
jumps and main endpoints. The remaining change is exactly the change in helper
boundary widths: 133. The eight center jobs, query shears, main diagonal and
idle bill are unchanged. Multiplication by 19 gives 2,527 added rank mass on
each side and leaves the complete surplus at 800. This identity is about
accounting under the stated frame contract, not physical operator correctness.

## Sources, replay and failure controls

Base: canonical main `2a13eb1827784206202db90e5dc8327cf8a250db`, priority
revision 7. [SOURCES.json](SOURCES.json) pins the two native input files already
on main, plus historical catalogue/selected-record provenance.
[snapshot/MANIFEST.json](snapshot/MANIFEST.json) binds the exact five exported
PR4441 files to their public commit, original paths, Git blobs and SHA256s.
The source README and attribution are retained unchanged. These snapshots are
committed with this audit: replay needs neither an unmerged Git object nor a
network fetch. The two main inputs were also checked byte-identical at the
audited PR head. Snapshot hashes authenticate retained bytes; their association
with the public commit was checked at acquisition, not by a network call during
every replay.

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/fresh-helper-invoice-audit --check-only
python3.12 -B scripts/research_package.py --package research/fresh-helper-invoice-audit
```

Direct replay, also supported from a Git-free package export containing its two
declared inputs:

```sh
python3.12 -B research/fresh-helper-invoice-audit/verify.py
python3.12 -O -B research/fresh-helper-invoice-audit/verify.py
```

[RESULT.json](RESULT.json) contains all derived profiles and **13 rejection
controls**: duplicate helper boundary, wrong original scalar frame, omitted
scalar retiming, omitted helper exit, incompatible contact frame, equal-rank
distinct spaces, dependent frame basis, missing query, missing idle, unsigned
swap, wrong boundary coefficient, unearned productive stage, and altered source
bytes. Acceptance uses explicit exceptions and remains active under `-O`.

Validation on CPython **3.12.0**, Windows 11 x64 (`10.0.26300`): metadata/pins
and both registered commands passed. The committed-byte preflight and a
15-file export integrity check passed at `6ffff4e474b97e9fcc1e13164676e372a9d3af80`.
Both direct modes also passed from that export in a fresh directory with no
Git checkout or predecessor Python modules. That commit contains the complete
scientific code and inputs; the subsequent change only records validation and
concurrent-work context. The optional full-history ancestry preflight was not
run in this shallow checkout. The prescribed selected baseline was attempted
but its unrelated source inventory is incomplete in the sparse checkout;
neither it nor the full selected cold replay is claimed as passed.

## Limits

The 632-role analysis checks frame paths and tariffs, not the full native
operator on 632 arbitrary input columns. Native adapters are treated under
their retained rank-zero contract. It does not rederive Clifford lowering or
absolute phases, prove the owned-query copy/erase implementation, audit owned
center erasure, validate arbitrary-column physical lifting, or recompute the
moment, paid tails, compiler, BIT, precision, stock, tape or outer admission.
In particular, the 112-port query tariff is the inherited contract, not newly
proved physical implementation. Neither the proposed kappa nor the full
multiplication theorem is independently accepted here. The selected record is
unchanged.

## Open next questions

The next useful check is the **native arbitrary-input/owned-query boundary**
of this exact proposal. Reconstruct the changed physical Clifford routes and
both helper normalizers with a separate interpreter, then check the copied
query's arbitrary dirty inputs and exact erase before composing them with the
main word. This matters because matching tariffs and a formal controller
identity do not discharge physical realization. Start with one changed edge
and one query, with a wrong-phase or omitted-erase control; a complete all-column
audit needs a separate budget and the retained native contracts. Further digits
of the same moment are not the next missing coverage. See [TASK.json](TASK.json).

## Credit and coordination

Construction credit remains with @1337isnot1337 for #4441's helper retiming and
combination; Cinna Davis for #4440's query thinning and owned queries; zxv for
the native/controller and compiler lineage; Jacob Alan Sussman for the mixed
integer flow; and the native, Clifford, BIT, precision and outer contributors
credited in the retained source. This package contributes the independent
contact-path accounting, symbolic controller replay, conservation check and
failure controls only.

Prepared for Mihir Srivastava (@mihir-s-05) with substantial OpenAI Codex
assistance. No subagents were used. Apache-2.0.

Canonical investigation: [Discussion #4443](https://github.com/CrocSwap/integer-mult-bounds/discussions/4443).
The task-picker seed is `500420262fb1df156828aa2604637058`; the
`independent-moment` card is refined to the newer #4441 invoice. Entry overlap
covered 301 open PRs and 3,289 Discussion records with complete remote paging;
the sparse local note corpus and remote closed PR bodies were incomplete.
The focused terms found #4440 and #4441. This deliberately audits their claims
and makes no claim that the mechanism is new.

The closing snapshot (21:12–21:14 UTC) covered 302 open PRs and 3,294 Discussion
records; canonical main and the audited #4441 head were unchanged. The recent
PR check also found concurrent
[#4446](https://github.com/CrocSwap/integer-mult-bounds/pull/4446), head
`7d05d73f96c27a9d360011e04af69b23fa903757`, which certifies the same profile
and a slightly different endpoint. Its `local_supplier.py` freshly calls
#4441's retained `native.py`; this audit adds a separately implemented
per-role contact-path reconstruction and dimension-conservation check without
those imports. #4446's own geometry and interval work retains its credit and
was not independently replayed here. The scope remains this finite accounting
audit; its result is compatible corroboration, not a competing construction.
