# Independent verification of PR #3633 (T488): literal owners, fixed-inventory ceiling, staged words (no κ)

**Object.** Open [PR #3633](https://github.com/CrocSwap/integer-mult-bounds/pull/3633) (hexapode, Pierre-Loic
Doulcet; head `72c268f113368ea0387d188225e3f81ba6d6ef73`, package `research/staged-width-t488`). It combines three
chronologies (T37 from Ross Richardson's PR #3605; T8 from hexapode's PR #3485/#3494; T16 from Nick Petalas's
PR #3413, via hexapode's PR #3457/#3465) as 8 copies of 61 base replicas (T = 488). It uses the unchanged staged
644/660 supplier words of [PR #3605](https://github.com/CrocSwap/integer-mult-bounds/pull/3605) (Ross Richardson),
and claims:
- 1,791,936 literal owner roles;
- the complete profile `{1:10826280, 2:3188592, 3:1015650, 4:447984, 5:94794, 8:35136, 48:186782}`;
- physical stock 437,757;
- an aggregate that attains the fractional packing optimum of its fixed inventory;
- κ = 0.001730096363528623534230 − 10⁻⁴⁶ − 10⁻⁷⁰.

Ross Richardson's [PR #3630](https://github.com/CrocSwap/integer-mult-bounds/pull/3630) independently bounds that
fixed inventory below .001730096363528623534231.

```text
Status / UTC update / priority revision: DONE (audit) · 2026-10-18 16:20 UTC · priority revision 6 · base main 20ecf289
Concrete question: are PR #3633's allocation, complete invoice, ceiling attainment and endpoint correct when checked
    by code that does not run PR3633, PR3630 or PR3605?
Result (independently checked, AI-assisted; no human review): no correctness defect in PR3633's finite claims in
    the checked scope.  All 1,791,936 roles pass a separate audit and the recount equals the claim.  An own dual
    certificate shows that no allocation, for any T, in the fixed-inventory model has a larger 24-digit endpoint,
    and PR3633's profile is exactly 488 x the unique LP minimum, so it attains that ceiling.  κ reproduces in two
    rational enclosures.  Two process defects are reported: tautological inherited controls, and platform-dependent
    native pins.
Artifact: PR #3694 (https://github.com/CrocSwap/integer-mult-bounds/pull/3694).  Replay: python3 -I -B research/t488-independent-audit/verify.py --fetch (212/212 controls)
Claim: released (advisory claim at discussions/1166#discussioncomment-19017329)
```

## What was checked

`verify.py` and the `audit_*.py` modules import and execute nothing of PR3633, PR3630 or PR3605: their files are
read as pinned git data. The scope-C2 analyser parses copies of PR3605's auditor with `ast` as the object it
studies. The local-only `tools/` scripts run PR3633 code as the object under study, and their outputs are labelled
as local-only.

| Scope | Check | Result | Negative controls |
| --- | --- | --- | --- |
| B `audit_owners.py` | the complete literal journal | all 1,791,936 roles pass; invoice = claim | 24 |
| A `audit_ceiling.py` | fixed-inventory LP, own simplex and dual certificate | profile = 488 × unique LP minimum | 52 |
| C1 `audit_staged_words.py` | both staged supplier words | exact forward and dual; widths = PR3633 providers | 50 |
| D `audit_endpoint.py` | endpoint, gains, PR3653 downstream | C = 0.001730096363528623534230 | 13 |
| C2 `audit_inherited_controls.py` | the five `reject()` controls of PR3605's auditor | tautological in all 15 copies | 65 |
| vendor | byte pins of this contributor's earlier modules | 8 files | 8 |
| | | **total** | **212/212** |

- **B, the literal journal.** The journal ships as `data/FILL-columns.xz` (0.77 MB: owner, child, port and offset
  columns; time and helper are implicit). The decoded rows re-serialise byte-identically to PR3633's pinned payload
  (`owners/EXPECTED.json`, sha256 `20662cc6…`), so the encoding cannot change the audited object. ORDER, DISPATCH and
  PROFILE are rebuilt from PR3633's base-chronology files, with each base call followed by its 8 copies (copy index
  innermost), and must equal PR3633's literal-file pins. The audit covers:
  - **Windows.** Each (replica, child) window is derived twice from the frozen template on main
    (`rank7-joint-endframes/allocation/vendor/TEMPLATE.json.gz`), once from its level annotations and once by
    replaying its event schedule. The two derivations must agree, and children of one family class have disjoint
    windows.
  - **Roles.** Every role must satisfy:
    - `lo < t ≤ hi`;
    - the active-local-pair exclusion of PR3630's checker, checked per role and also as a template lemma over 18,544
      triples, which shows the windows imply it;
    - same-call physical families;
    - capacity, with the widths recounted in C1;
    - chronological compact offsets.
  - **Invoice.** All 983,808 bins are charged, empty ones included: idle `{1:114192, 3:31842, 5:6954, 48:186782}`.
    With 4,392 local bills this gives exactly the claimed profile.
  - **Aggregate and stock.** The journal realises the aggregate's 11 capacity-patterns. The stock is
    896T + 408 + 8 + 91 + 2 = 437,757, with each component read from the word or the template.
  - **Controls.** Controls include PR3133's widths (helpers 389/397 at 8), which do not host the journal.
- **A, the ceiling.** The model is fixed: per-call widths {4:26, 5:2, 6:18, 7:52, 8:97, 9:213}, the local bill
  2439H1+726H2+224H3+102H4+20H5+8H8, nine calls per replica, bins (672, 448, 448, 448) of capacities (8, 16, 32, 48),
  live 896 per replica, and H_r(a) = r^(1−a).
  - **Certificate.** Over this model, 2,551 patterns (7 + 38 + 399 + 2,107) go into an own exact simplex. Its dual
    is certified rigorously: 12 reduced costs are identically zero and 2,539 are positive on [a_lo, a_hi].
  - **LP minimum.** The unique LP-minimum profile is 22185H1 + 6534H2 + (8325/4)H3 + 918H4 + (777/4)H5 + 72H8 +
    (1531/4)H48 per replica, and PR3633's aggregate attains it.
  - **What the ceiling covers.** It holds for every T within this model, and it relaxes windows, families,
    chronology and integrality.
  - **Cross-checks.** It cross-checks PR3633's `CEILING.json` (model, field hash, basis, dual, value and root
    polynomial) and PR3630's model constants, basis, dual and published dual digest `11c3cade…`.
  - **Independence.** A first draft mirrored PR3633's enumeration and column code. It was rewritten after review (see
    the module docstring).
- **C1, the words.** These are this contributor's PR3053 word pipeline, run on the two words that are byte-identical
  in PR3633 and PR3605: forward and dual replay of 632 inputs through cleanup and the target endpoint, the tracker,
  the cleanup re-derivation and the 91 buffers. The helper widths equal PR3633's `PROVIDERS.json`, and they differ
  from main's PR3133 providers only at helpers 389/397 (registers 644/660, 8 → 7). The change from the parent words
  on main is localised:
  - 8 helper→target writes are deleted, and 4 donor releases are inserted, with their 4 inverses in cleanup;
  - restore 210 changes its frame only;
  - the 72 warps move position only;
  - `start_extra` changes.

  This contributor's parallel session audits the same two words independently, with a different code lineage, in
  [PR #3687](https://github.com/CrocSwap/integer-mult-bounds/pull/3687) (14:46 UTC, same account). That audit and C1
  agree on the width inventory (8:97, 7:52) and the local bill. C1 is here to supply scope B's per-helper widths and
  to bind them to PR3633's providers.
- **D, the endpoint.** Two independent enclosures accept C and reject C + 10⁻²⁴: atanh/Taylor series (PR3053) and
  640-bit fixed point (PR2804). κ = C − 10⁻⁴⁶ − 10⁻⁷⁰. The exact gains are 2.449882e-8 over PR3626, 4.881144e-8 over
  PR3624, 8.967322e-8 over PR3630 and 8.981399e-8 over PR3605, and each predecessor's profile is rejected at C.
  C is below PR3605's recorded BIT endpoint, which is compared, not re-derived.
- **D, downstream.** rohanarun's [PR #3653](https://github.com/CrocSwap/integer-mult-bounds/pull/3653) (head
  `607a09ff`) puts roger-sato's [PR #3642](https://github.com/CrocSwap/integer-mult-bounds/pull/3642) retimed words
  on this journal. Both words recount to PR3633's helper widths, with local bill {1:2437, 2:724, 3:226, …} (jwr404's
  PR #3677 checks the same bill change). The profile is derived here, not read from PR3653: PR3633's audited profile
  plus 4,392 × the bill change. That profile has endpoint 0.001730418899766071163804 = PR3653's κ + 10⁻⁴⁶ + 10⁻⁷⁰.

  The LP's reduced costs do not involve the local bill, and b·y = c·x holds symbolically, so only dual feasibility at
  the new endpoint needed re-certifying. The scope-A dual, re-certified on that endpoint's 24-digit step (12 tight,
  2,539 positive), puts PR3633's allocation at the fixed-inventory ceiling for the retimed bill.

  This assumes PR3653 uses PR3633's journal unchanged; PR3653 pins the same `EXPECTED.json` (blob `415eac1a`), which
  is not compared beyond that pin. The retimed words' exactness is not checked here; roger-sato's PR #3693 audits it.
- **C2, the inherited controls.** See finding 1.

## Findings (non-blocking)

1. **The literal-owner audit's five `reject()` controls cannot fail.** PR3633's `owners/independent_literal.py`
   adapts PR3605's auditor: it adds input-authentication gates for artifact, source and native pins, the FILL payload
   and exact ORDER/DISPATCH, and keeps its predicates and its five controls unchanged. `reject(name, test)` runs
   `need(not test())`, but no `test` feeds changed data to a gate:
   - three predicates are unsatisfiable: a shifted column compared with the tile, `lo < lo`, and `len({f, f}) == 2`;
   - two test a +1 perturbation of an equality that the preceding gate has just asserted.

   **Where the same controls appear.** A scan of every `.py` blob in main and eight PR heads finds the same five
   controls in 15 files. Static analysis (syntactic name tracking, with the remaining aliasing exclusions checked by
   inspection) shows they are tautological in each:
   - PR3633's own file;
   - PR3605's file and its `provenance/` copies;
   - PR3624's and PR3626's `independent_literal.py`, and PR3630's `independent_owners.py`;
   - zxv's PR3638 (adapted);
   - roger-sato's PR3642 (one adapted, two byte copies);
   - rohanarun's PR3653 (one adapted, two byte copies).

   **Demonstration.** `evidence/GATE-DISABLE-DEMO.json` is local-only (Linux, CPython 3.14.4, numpy 2.5.4). In it,
   PR3633's auditor ran unmodified, then with each of the five gates the controls are named after replaced by
   `need(True, …)`, then with all five replaced. Every variant printed PASS and listed the same five controls.

   **What this is and is not.** It is a control-coverage defect, not a correctness defect: the gates are real checks
   and pass on the real data, and scope B re-checks each one with controls that do feed violations. PR3633's other
   guard tests (aggregate, stored-receipt and ceiling corruptions) do feed changed data to their checkers. Its
   admission `owners` stage, which passed here, also re-checks windows, families and prefixes.

   **Lineage.** PR3605's file describes itself as an adapted copy of a parent audit (SHA256 `1001cb1c…`). No `.py`
   blob in main or these heads has that hash (10,239 blobs scanned; archives not searched), so where the controls
   were first written is not determined. The earlier checker of this lineage on main,
   `research/rank7-joint-endframes/allocation/vendor/independent_owners.py`, credits its chronology/mask method to
   Tekalign's PR2751. It reruns its `check()` on mutated inputs (a role outside its window, a same-call family
   collision, a prefix hole, a changed profile, and T, role-count and dispatch corruptions) and requires the exact
   rejection reason.

   **Suggested fix.** Factor the gates into a `check()` function and rerun it on each mutated journal, requiring the
   expected message.
2. **Rebuilt native files fail only on the gzip header byte.** Here, PR3633's replay rebuilt both changed native
   providers with PASS (Linux, CPython 3.14.4). The rebuilt `CANONICAL-WORD`, `FULL-WORD` and `LOCAL-PROGRAMS`
   `.json.gz` files differ from the pinned files only in byte 9, the gzip OS field:
   - FULL-WORD was compared byte by byte, because its pinned bytes ship as `supplier3605/STAGED644-660-*.json.gz`;
   - the other four were compared by sha256 after setting byte 9.

   The payloads are identical. The pinned files carry 0x13; on this machine CPython 3.14.4 writes 0xff and CPython
   3.12.15 writes 0x03.

   **What the lineage already handles.** PR3605's `staged_pair.py` already restores this byte for the supplier words,
   and PR3633 pins FILL by payload. `replay.py`'s native stage compares FULL-WORD by payload, which is why it passed
   unpatched.

   **The remaining gap.** The case not covered is the `native_canonical` pin in `independent_literal.py` (PR3653's
   adapted auditor has the same pin). It compares the rebuilt CANONICAL-WORD file hash, so a correct rebuild on
   another platform fails it. The gate-disable demo fed it rebuilt files with byte 9 set to 0x13. Pinning payload
   hashes would remove the gap (`evidence/NATIVE-REPRODUCTION.json`).

## Overlap and timing

- **Before the claim.** Overlap checks ran at 12:04 UTC (`find_overlap.py`, open PRs and discussions), and the
  advisory claim was posted at 12:07 UTC (comment 19017329).
  zxv's [PR #3638](https://github.com/CrocSwap/integer-mult-bounds/pull/3638)
  (11:58 UTC) predates the claim and was missed by that check. It reaches the same endpoint with a different T360
  allocation and its own dual replay. It is not a check of PR3633's journal, and this package did not audit it.
- **After the claim.** Later PRs on this line:
  - PR3653 (13:08 UTC, ready for review since 13:46 UTC);
  - jwr404's PR3677 (the retimed bill keeps rank mass 5,135 and lowers the moment) and PR3680 (T360 role count);
  - this account's PR3687 (an independent audit of PR3605's words; see C1);
  - roger-sato's PR3693 (an audit of the retimed and delayed words, reusing PR3687's interpreter);
  - roger-sato's PR3681 (a full replay of PR3605's wrapper, Ross Richardson's handoff);
  - zxv's PR3682 (retimed releases at T360).

  None is an independent check of PR3633's journal or ceiling. The final recheck was at 2026-10-18 16:19 UTC. It
  found roger-sato's PR3693 (15:33 UTC), which audits the retimed and delayed supplier words by reusing PR3687's
  interpreter, and nothing on PR3633's journal or ceiling.

## Scope limits

- **Native lowering.** It is not checked. C1 replays the words in the lineage's free-operator model.
- **Release stages.** The precision, the prefix receipt and the physical invoice beyond the stock count are not
  checked, nor the modern joint outer transfer, the bootstrap or the BIT side, which is only compared.
- **All-size hypotheses.** The inherited all-size dispatcher/compiler, uniform-cost, hosting, mutable-source,
  rounding, tape, recovery and analytic hypotheses are not checked.
- **Written arguments.** PR3633's written call-copy and owner-copy (Hall) arguments are not checked; only their
  output, the journal, is.
- **Model premises.** These are taken as given: the physical-family model (owner, 2·pair + side, port), as used by
  the main-lineage checker, and the base-chronology files. Their equality to main's retained chronologies is not
  checked, and legality does not depend on it.
- **Full replay.** PR3633's full fresh `replay.py`, which its author disclosed as not run, was attempted four times
  here on 7.9 GB RAM with no swap. Fresh native passed every time. Owners passed in runs 2–4; parent-lift was
  OOM-killed in run 2 and passed in runs 3–4; rebind and discovery `bind` passed in runs 3–4. Discovery `emit` was
  OOM-killed in runs 1, 3 and 4, at 5.14 GB in run 4, which had no other job. So the release stage was never reached
  (`evidence/NATIVE-REPRODUCTION.json`, local-only).
- **Frontier.** No selected-frontier change is proposed. κ is unchanged by this audit.

## Reproduce

```sh
python3 -I -B research/t488-independent-audit/verify.py --fetch          # compares RESULT.json
python3 -I -B research/t488-independent-audit/verify.py --fetch --mutations --jobs 2
python3.12 scripts/research_package.py --package research/t488-independent-audit   # registered replay
```

`--fetch` needs git ≥ 2.29 and network access, and writes only the eight PR heads to `refs/audit/prN`. The replay
needs those heads to remain fetchable and a clone containing main `20ecf289`. The registered replay passed here with
CPython 3.12.15 (`PASS_REGISTERED_RESEARCH_PACKAGE`). RESULT.json was written with CPython 3.14.4; the
default run under CPython 3.12.15 (the CI interpreter) reproduces it exactly. Runtime is about 3 minutes on 4 cores,
with peak memory about 1.5 GB (local measurement).

The mutation sweep runs an unmutated baseline first. It then applies each of the 45 checker mutations in a
subprocess, and each must load the mutated module and end in an audit rejection. Result: 45/45 killed, 0 survived
(`PASS_MUTATIONS`), after a passing unmutated baseline, with CPython 3.14.4 and 2 jobs, 2026-10-18 15:34–16:19 UTC, on
the final code bytes (log local-only).

Local-only tools (not run by `verify.py` or CI):
- `tools/encode_journal.py` re-encodes the journal from PR3633's `owners/portable_expand.py` output. That output
  reproduced PR3633's pinned FILL byte for byte here.
- `tools/gate_disable_demo.py` regenerates `evidence/GATE-DISABLE-DEMO.json`; it was run twice, with identical
  results.

## Open next questions

1. **Does a width change, or a local-bill change beyond PR3642's retiming, raise the ceiling above
   0.001730418899766071163804?** That is the retimed ceiling certified here for PR3633's allocation.
   - *Why it matters:* within scope A's model, packing is closed for every T. PR3633 attains the ceiling (checked
     here) and PR3638 reports the same endpoint. PR3653 shows that a local-bill change with unchanged widths moves
     the endpoint, with PR3633's allocation at the re-certified ceiling.
   - *First step:* use `audit_ceiling.py`'s LP to price single-helper width changes and local-bill changes before
     building any word.
   - *Blocked by:* a width change needs a new exact word, as PR3605 built.
2. **Make the owner-audit controls test the gates.**
   - *Why it matters:* finding 1 affects 15 copies of the same five controls.
   - *First step:* rerun a `check()` function on mutated journals (as the main-lineage checker does), or reuse
     `audit_owners.controls`.
   - *Blocked by:* nothing.
3. **Make the native pins platform-independent.**
   - *Why it matters:* finding 2.
   - *First step:* pin the decompressed payloads of `CANONICAL-WORD` (and `FULL-WORD` and `LOCAL-PROGRAMS`) in
     `independent_literal.py`'s `native_canonical` and in the receipts.
   - *Blocked by:* nothing.
4. **Complete PR3633's fresh end-to-end replay.**
   - *Why it matters:* its author did not run it, and here it stopped in discovery `emit` for lack of memory.
   - *First step:* rerun `replay.py` with ≥ 12 GB RAM or swap. roger-sato's PR3681 reports a full PR3605-wrapper
     replay, which may show a working configuration.
   - *Blocked by:* memory on this machine.

## Credits

- **The object and its sources.** hexapode (Pierre-Loic Doulcet): the T488 composition and aggregate (PR3633), T450
  (PR3624), T530 (PR3626), the T8 chronology (PR3485/PR3494) and the T16 provider composition (PR3457/PR3465). Nick
  Petalas: the T16 chronology (PR3413). Ross Richardson: the staged 644/660 supplier, the T37 lineage and the
  allocation machinery (PR3605), and the all-T ceiling and dual (PR3630).
- **Downstream and concurrent work.** roger-sato: the retimed words (PR3642). rohanarun: their composition with T488
  (PR3653). zxv: the concurrent T360 allocation (PR3638).
- **Earlier work.**
  - Marius-Paul Dumitrean (PR2979): the frozen template and plan of the rank7-joint-endframes package (windows,
    family convention).
  - dcharb78 (PR3133): the parent words and providers.
  - Jeremy Diviney (PR3148, coupled-carrier-cap740): the capacity model and the finite-pattern primal/dual approach.
  - The owner-checker lineage those packages name, including Tekalign's PR2751 independent owner checker.
  - Clear1nsight's handoff suggested this audit.
- **Vendored code.** This contributor's own merged checkers (PR #3053 and predecessors). Their predecessors are
  credited in `vendor/NOTICE.md`: Jeremy Kothe, Cinna Davis, Dugongue, Rohan Arun, mdumitrean, Vlado Vojdanovski,
  Hao Yan, Josie Elliston, and icekylinx and Zhihao Chen (jacklightChen) as two contributors.
- **Author.** Sagar Thakrar (thakrarsagar), with substantial AI assistance (Claude Code, Anthropic: subagents built
  two scopes and ran adversarial reviews). No independent human review is claimed.
