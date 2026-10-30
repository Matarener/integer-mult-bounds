# Owned-772 descent and public-731 relay elimination

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
The predecessor construction and checker are credited to DreamingOfClouds
(PR6143, PR6030 and PR5907), Ali Romman (PR5827), and the cumulative P104
lineage named in their retained notices. This note proves only the local edit;
the complete conditional claim also needs the inherited native/caller/pricing
checks and five framework assumptions.

## Frozen objects

Base: PR6143 at `4cef86d87e47dfcc5a511c99c9f0067c861271b0`,
`research/p104-root-relay-descent/WORD.json.gz`. The canonical JSON SHA256 is
`b66406fa1027ba08ac2a85154ba73289f258f90d79454a193e685221bc61430d`.
The new canonical JSON SHA256 is
`0572c956c77b0ee2ef47169c9df52269bc719e37c7003f3f0245179aea0aad71`.
`EDIT.json.gz` consists of literal new events and exact slices of the base
program. Regeneration requires no solver. No initial/final frame, frame basis,
public register, or productive helper target changes.

Indices below are zero-based indices in the frozen PR6143 base. They are
explanatory; the executable certificate is the complete new word.

## Exact scalar identity

Let `u` denote the independent initial value in public helper 731. It is
unchanged throughout its frame-3 prefix: before the relay it is read at three
frame-3 ADDs but is never a scalar destination. Let `rho` be register 146's
value just after base event 13474 (`146 += 440` in frame 529), and let
`v = -rho/2`. Register 146 does not change again until event 16903, after all
uses discussed here.

The original 772 lifetime copies `rho`, contributes `-rho/2` to register 162,
scales itself to `v`, descends from 529 to 595, and contributes `v` to 708
and 731. Hence 731 holds `u+v` during its ascending relay. The edit leaves
731 at `u` and has 772 deliver `v` directly.

For each of the eight relay readers, the old update `r += q*(u+v)` is
replaced by `r += q*u` in frame 3 and `r += q*v` in its old meeting frame:

| Reader | q | Meeting frame | Frame dimension |
| --- | ---: | ---: | ---: |
| 572 | 2 | 595 | 1 |
| 582 | 2 | 595 | 1 |
| 581 | 2 | 595 | 1 |
| 134 | -2 | 595 | 1 |
| 450 | 4 | 595 | 1 |
| 496 | 4 | 595 | 1 |
| 451 | -4 | 737 | 4 |
| 497 | -4 | 520 | 6 |

The frame-3 update is inserted immediately before the reader's first MOVE,
using 731 itself, which still holds `u` in frame 3. For each reader there is
no intervening source use or SCALE before its old relay read. Intervening
ADDs into that reader commute with adding `q*u`. For readers 451 and 497,
the `v` update moves earlier, to the corresponding point of 772's descent;
they are already at frames 737 and 520, and have no intervening source use
or SCALE before their old read. The remaining six `v` reads stay at their
original chronological locations.

The top-frame read `162 += 2*731` formerly contributed `2*u+2*v`. It now
contributes `2*u` and an adjacent `162 += -146` in frame 529 supplies
`2*v = -rho`. This uses register 146 while it still contains `rho`.
The former cleanup `731 += rho/2` is deleted: the base cleanup sends
`u+v` to `u`; the new register already holds `u`. The subsequent read of
731 by 146 consequently sees the same value.

The original 772 contribution `162 += -rho/2` is retimed without changing
its value: it becomes `162 += 772` just after 772 is scaled to `v`.
Register 162 has no intervening source use, SCALE or other event between
these two positions. The loading of 708 and the first read of 708 by 127
are also retimed. Register 708's MOVE from 595 to 602 follows those reads,
and precedes every old read of 708 at 602. No public output or later value
changes. The complete rational replay checks the result on all 799 formal
input columns, including every arbitrary independent helper input.

## Frames, lifetime and chronology

The base paths are

- owned 772: `529 -> 595` (dimensions `7 -> 1`);
- public 731: `3 -> 595 -> 737 -> 520 -> 529`
  (dimensions `0 -> 1 -> 4 -> 6 -> 7`).

The new paths are

- owned 772: `529 -> 520 -> 737 -> 595`
  (dimensions `7 -> 6 -> 4 -> 1`);
- public 731: `3 -> 529` (dimensions `0 -> 7`).

All containments are the strict reverse of already used base containments.
Reader 497 is at 520 and reader 451 is at 737 before the new descent starts.
All other scalar gates retain common frames, including each compensation.

The new 772 lifetime starts immediately after base event 13641, the last
read of owned register 791 (`COPY 770 <- 791`). The CLEAR of 791 is moved
from base event 15597 to that point, before the INIT of 772. There is no
later read, write, MOVE or COPY involving 791. The slot released by its
legal CLEAR covers the extended 772 lifetime. This is actual chronological
liveness, not an argument from matching INIT/CLEAR multisets. The new CLEAR
of 772 follows the last 595 read (reader 496, base event 14468).

Public count 770, owned labels 29, owned lifetimes 31 and peak live owned
count 13 are all unchanged. Every owned register is cleared at return.
The complete new program has 22,834 events (six more than PR6143), safely
below the inherited 26,000-event bound. It adds seven ADDs net and removes
one MOVE net; INIT, CLEAR, COPY and SCALE multisets are unchanged. The exact
ordinary scalar allowance increases from 189,730 to 189,806, by 76.

## Complete signed local budget

Writing `H_r = r^t`, the old paths cost `H_6 + H_1 + H_3 + H_2 + H_1`;
the new paths cost `H_1 + H_2 + H_3 + H_7`. Thus the complete local paid
profile changes by `-H_1 - H_6 + H_7`. Productive targets, rank mass,
public endpoints, caller query/idles, and helper normalization obligations
are unchanged. No credit is assigned to owned scratch.

For every `0 < t < 1`, strict subadditivity gives `1 + 6^t > 7^t`.
Thus the local complete signed gain is positive throughout that exponent
range. The caller invokes the local word 18 times, so the full paid profile
changes by `-18 H_1 -18 H_6 +18 H_7`, and its paid-call count drops from
66,798 to 66,780. Every newly used signed native map and its absolute phase
still needs the complete native replay; this algebra does not replace it.
The productive count 13,444 and rank-mass surplus 760 remain unchanged.

## What is new and what is not

PR6143 rerouted roots 770/771 through helpers 705/706. This edit uses the
separate root 772 and relay 731; its frame-3 compensation is particularly
simple because 731 has no preceding scalar writes. Retiming the now-dead
791 lifetime is needed to compose all three root changes without increasing
peak occupancy. PR6136's chart-only A-E searches keep the scalar program;
this edit changes the read sources and compensating ADDs, so it is outside
those reported finite domains. This does not show those domains or the
broader supplier globally optimal.

The new word is a finite conditional construction. It does not discharge
native-all-column, owned-erasure, compiler, precision/tape or analytic
recovery assumptions, materialize the uniform word or rounded multiplier,
or authorize changing the selected frontier.
