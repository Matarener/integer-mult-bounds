# Conditional κ = 0.003127804: one more owned-root relay removal

This package adds one finite construction to DreamingOfClouds' pending
[PR6143](https://github.com/CrocSwap/integer-mult-bounds/pull/6143): owned register
772 delivers its value directly while public helper 731 takes a single hop.
Eight compensating reads preserve 731's arbitrary independent input. Moving
791's CLEAR immediately after its last read makes the longer 772 lifetime fit
within the unchanged peak of 13 owned fields.

The complete conditional claim is **κ = 781951/250000000 = 0.003127804**, an
increase of **0.000000667 over PR6143's 0.003127137** and **0.000002000 over the
selected PR6030 claim 0.003125804**. This changes the complete paid profile;
it is not additional digits of the predecessor's crossing. The selected record
is unchanged. The five framework assumptions remain.

| Complete construction | PR6143 input | This word |
| --- | ---: | ---: |
| Paid recursive calls | 66,798 | 66,780 |
| Productive fields | 13,444 | 13,444 |
| Paid / target rank mass | 240,152 / 240,912 | 240,152 / 240,912 |
| Public / owned labels / lifetimes / peak | 770 / 29 / 31 / 13 | 770 / 29 / 31 / 13 |
| Local events | 22,828 | 22,834 |
| Local ordinary scalar allowance | 189,730 | 189,806 |

The exact raw crossing lies in **(0.00312781137239, 0.00312781137240)**.
The compiler is tested at **0.003127809**, with exact gap
`d = (tested − κ)/7 = 1/1400000000`. The unchanged admitted BIT budget `.0034`
still exceeds this complex supplier's saving. This is a small improvement to
the complete conditional multiplication bound, subject to the same assumptions
and independent admission; it is not a measured runtime improvement.

## Construction and complete cost

[PROOF.md](PROOF.md) gives the scalar identity, eight reader coefficients,
chronology and budget. The old paths are

- owned 772: `529 → 595`;
- public 731: `3 → 595 → 737 → 520 → 529`.

The new paths are

- owned 772: `529 → 520 → 737 → 595`;
- public 731: `3 → 529`.

Let `u` be helper 731's arbitrary input and `v = −146/2` at the stated causal
cut. Each old reader receives `q(u+v)`. It now receives `qu` at frame 3 and
`qv` from 772 at its legal meeting frame. A final correction to 162 and the
removed cleanup of 731 preserve every endpoint. No owned register earns
productive credit, and no helper input is assumed zero. The INIT, CLEAR, COPY
and SCALE multisets stay unchanged; their actual chronological legality is
checked separately.

Per local invocation, paid cost changes by `−H1−H6+H7`, where `Hr = r^t`;
productive targets do not change. Across all 18 invocations the signed saving
is `18(1+6^t−7^t)>0` for `0<t<1`. All query calls, whole idles, normalizers,
adapters, source access, erasures, scalar operations and caller obligations
remain charged. The additional 76 local scalar units are included in the
retained ordinary-work budget. Restoring 791's old later CLEAR would raise
peak occupancy to 14, so the lifetime retiming is essential.

`construct.py` applies the 59 copy/literal segments in `EDIT.json.gz` to the
pinned PR6143 word. It compares the entire regenerated JSON payload with
`WORD.json.gz`; no solver or network is needed. Source archives retain exact
byte hashes, while generated gzip container differences are irrelevant.

## Exact sources and what is new

- Checkout base: `721c03822c421b7f7fcbb2598993b947c4d88419`, canonical CrocSwap/main,
  priority revision 8. The selected record is PR6030, not the historical PR5599
  number still present in parts of the guidance.
- Immediate word dependency: PR6143 at
  `4cef86d87e47dfcc5a511c99c9f0067c861271b0`, from
  `DreamingOfClouds/integer-mult-bounds`. Its exact compressed word is vendored
  in `inputs/`; size, SHA256, Git blob and original path are in `SOURCES.json`.
  This pending head is **not** in this branch's ancestry. The standalone checker
  authenticates its bytes; publication-ancestry checks concern the declared
  canonical-main inputs, not this separately retained word.
- Verifier chain: Ali Romman's PR5827 at
  `05cd36e5af06d7a3790e30ce3f449fa89b853768`, using the exact source archive already
  retained by selected PR6030. All 23 archive members and its seven-deep chain
  are authenticated. Only the four pricing replacements in `PRICING-EDITS.json`
  are made; the chain's operators, caller, interval and compiler code are unchanged.
- Independent native inputs: three exact main-branch files listed in
  `NATIVE-SOURCES.json`, also declared as live replay inputs.

PR6143 introduced the separate 770/771 descents through relays 705/706. This
package contributes the 772/731 descent and necessary 791 lifetime change,
plus a new independent integer-dyadic/GF2 replay and dense checks of the changed
native maps. It does not claim the predecessor mechanism as new. PR6030 and
PR5907 supply the earlier helper-470/468 rung removals. PR6136's five reported
chart-only search classes retain the scalar reads; our read substitutions and
compensations lie outside those finite domains. PR6116/6133's scalar savings
alone do not change the paid histogram.

OS assignment seed **33** selected the complex track. The three candidates,
local claim, live overlap limitations and bounded stopping rule are retained in
`TASK.json`. We stopped after this single successful root edit; this is not an
exhaustive search or a global optimality result.

## Reproduce and verification scope

From the repository root, with Python 3.12 and its standard library:

```sh
python3.12 -B scripts/research_package.py --package research/p104-owned772-relay-descent
```

Expected final result: `PASS_REGISTERED_RESEARCH_PACKAGE`, including
`PASS_P104_OWNED772_KAPPA_312780400` and exact equality with the committed
`RESULT.json`, `INDEPENDENT.json` and `NATIVE-AUDIT.json` receipts.

The full registered command passed on 2026-10-28 with Python 3.12.14.
The primary generation pass and final receipt-checking pass both completed;
normal and optimized independent receipts agree. Hosted CI was not run.

The registered checks cover:

- All 799 formal input/output rows, strict frame nesting, arbitrary helper
  inputs, actual lifetimes and exact full profiles. The independent checker
  uses binary Gaussian elimination and normalized integer-dyadic rows, importing
  no predecessor replay or pricing routines. It runs normally and with `-O`.
- Three new distinct signed native maps, plus the already-used helper map
  `3→529` as a positive control: 512 exact columns each, absolute phases,
  norms and support ranks. The four maps are new *paid MOVE pairs*; one was
  already present among helper normalizers. Normal and optimized receipts agree.
- The complete primary chain: every signed native map and phase, all main
  adapters and helper normalizers, separate dense transpose, the actual
  physical caller, both exact rational interval engines, completion and finite
  compiler funding, and all 54 strict plus four functional outer predicates.
- Twelve independent scalar/frame/storage faults, including missing arbitrary
  input compensation, dirty COPY, wrong ownership, non-dyadic scaling,
  premature 791 erasure and the peak-14 schedule. Dense native controls reject
  an absolute-phase fault that preserves the signed tableau and a wrong child
  sign. Primary controls also reject missing new events, sign errors, unpaid
  work, extra target credit and altered immutable inputs. The predecessor's
  full invoice fails at the new claimed κ.
- Seven inherited portability tests in optimized mode, including changed
  payloads, bool/int substitutions, corrupt gzip streams and immutable-source
  changes.

`RESULT.json` is finite conditional construction evidence. Neither normal nor
optimized replay is a proof-assistant formalization or independent human review.
The primary reuses PR5827's implementation; the additional checker is independently
written within this AI-assisted contribution. It does not independently rebuild
the entire uniform caller theorem. Existing unchanged native evidence is reused
explicitly alongside the full primary replay.

## Scope, ceiling and remaining assumptions

The exact crossing is this fixed complete invoice's ceiling on `[0, .0034]` under the
retained power-moment test, not a universal architecture ceiling. Its headroom above the
claim is about `7.37239e-9`; the tested exponent leaves about `2.37239e-9` below
the crossing. A further hill-climbing step needs another changed complete
profile, not repacking this invoice. BIT becomes binding only if the compatible
complex construction reaches the admitted `.0034` budget.

The retained assumptions are `native_all_columns`, `owned_erasure`, `compiler`,
`precision_tape` and `analytic_recovery`. In particular, CLEAR uses the inherited
owned-erasure contract, not a claim that all approximate residuals vanish.
The enormous uniform word and complete rounded multiplier remain unmaterialized.
No selected frontier update, merge or full unconditional multiplication theorem
is asserted.

## Open next questions

1. Can a different owned/public relay pair remove another paid split while
   preserving arbitrary inputs and peak storage? Start with one named pair's
   chronological rows and complete signed bill. Missing compensation or native
   delivery is a blocker, not a zero cost; no global search is claimed here.
2. Can independent maintainers admit this exact finite application under the
   retained five assumptions? Replay the package from its frozen inputs and
   review the local proof against the selected PR6030 application review.
   Full uniform, precision/tape and analytic obligations remain inherited.

## Attribution and license

New work is attributed to **@CubeJerry**, with substantial **OpenAI Codex**
assistance, including complementary construction, cost and independent-check
agents. New code and prose are Apache-2.0. DreamingOfClouds' PR6143/6030/5907
construction and edit/replay wrappers retain their Claude Opus 5.5 assistance
disclosure. Ali Romman and the PR5827 chain retain their OpenAI Codex disclosure.
Mason Hale (PR5811), Pierre-Loic Doulcet (PR5565), Cinna Davis, David Arias,
Gareth Davidson, Jacob Alan Sussman, zxv, Cao Yifan and the full retained
native/controller/compiler/BIT/analytic lineage retain credit through the
unchanged source notices. The dense native method follows Matarener's PR5960
and Clear1nsight's exact Gaussian-dyadic interpreter. Douglas Colkitt's
portability repair and tests are retained with attribution. JosieElliston's
PR6136 helped identify the changed-read search class.
