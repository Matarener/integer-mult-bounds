# Retain an operand to remove a root stop

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The source construction is PR6144 by DreamingOfClouds. See NOTICE for all
retained source credit.

## Exact source and claim

Use PR6144 at `5ec9b6dafc1ec54e2c0ca0771e8ed032f7888417`. Under the same five
framework assumptions as the selected P104 result, the changed finite word and
complete caller support **κ = 0.003128645**. The proof has two parts: equality
of the changed local operation and a complete cost and compiler check.

Event positions below are zero-based positions in the immutable source word.
The native frames have these dimensions and containments:

```text
dim(3)=0, dim(595)=1, dim(737)=4, dim(520)=6;
3 ⊂ 595 ⊂ 737 ⊂ 520 ⊂ 529.
```

The checker proves these containments and the ranks through the unchanged
source replay and the exact native-map checker. No new frame is introduced.

## Equality at the cut

Let `a` be the decoded value of reader 451 before event 12918. Let `b` be the
decoded value of helper 228 at event 12918. Let `q` be the decoded root value
in register 772 at event 13485. The source performs:

1. Move reader 451 from frame 3 to frame 737 and add `b` at event 12918.
2. Move root 772 from frame 520 to frame 737 at event 13486.
3. Add `-4q` to reader 451 at event 13487.
4. Move root 772 from frame 737 to frame 595 at event 13488.

At this cut, reader 451 has value `a+b-4q` in frame 737. Root 772 has value `q`
in frame 595. No other register reads reader 451 between events 12918 and
13488. Its next external read is event 14524.

The new word performs:

1. Move reader 451 from frame 3 to frame 595 at event 12913.
2. At event 12918, initialize owned register 770 in frame 737 and copy `b` into
   it. This uses the source value before helper 228 leaves that frame.
3. At event 13488, move root 772 directly from frame 520 to frame 595. Add
   `-4q` to reader 451 in that frame.
4. Move reader 451 from frame 595 to frame 737, add the saved `b`, and clear
   register 770.

The value is now `a-4q+b = a+b-4q`. The two schedules give the same values and
frames for all public and live owned registers at the cut. The saved value is
zero on exit. Register 770 has no earlier live lifetime; its source lifetime
starts at event 13658. The new lifetime ends before that event.

Each scalar operation acts in a common native chart. Each new MOVE has the
proper nested direction: public registers move to a containing frame and owned
registers move to a contained frame. The native checker verifies every signed
Pauli image and the exact global phase. Full arbitrary-input and
reverse-chronology transpose replays also check the complete word, including
all later reads and public restoration.

## Complete bill

The old three changed routes have ranks `4, 2, 3`. The new three routes have
ranks `1, 5, 3`. The rank-3 terms cancel. For `H_r=r^t` and `0<t<1`, the saving
is

```text
H_2 + H_4 - H_1 - H_5
  = (H_2 - H_1) - (H_5 - H_4) > 0.
```

Strict concavity gives the last inequality. The number of paid calls and rank
mass stay the same. All productive targets and all 104 main ports stay the
same. The complete caller has 18 local calls, so its paid change is
`18(H_1-H_2-H_4+H_5)`. The 15 thin-query groups, 3,120 whole idle jobs, main
adapters and helper normalizers retain their full charges.

The full word has 22,821 events, 770 public registers, 29 owned register labels,
32 owned lifetimes and peak owned use 13. The new cache adds one INIT, one COPY
and one CLEAR. The local scalar allowance rises from 189,658 to 189,670. The
route bound is 5,325,000 and includes four route allowances for each owned
lifetime. Their sum is below the retained local budget of `10^7`.
The full nonrecursive bound is 184,647,552, below `10^9`.
The scalar-growth bound uses 26,000 events; the word remains below that bound.

The complete invoice has 66,762 paid calls, 13,444 productive fields and rank
surplus 760. A separate census from the two caller path lengths agrees with
the physical-event census. No target is assigned to the new cache.

## Price, completion and transfer

The two exact rational moment engines give a unique raw crossing in

```text
(0.00312865201590, 0.00312865201591).
```

The derivative bound is negative on the retained interval up to the BIT cap
0.0034. This ceiling is for this fixed invoice. The old PR6144 invoice has a
negative upper margin at the new claim.

Use tested saving 0.003128650, cutoff 16, floor 17, tensor power 1024, tail
offset `1/7`, reserve `10^-12`, decay `125/128` and tail block 128. The paid,
offset and completion ratios have upper bounds below, respectively,
`1-10^-12`, `125/128` and `125/128`. Splitting and rounding charges are included.
The compiler gap is `1/1400000000`. The finite threshold is
`N = 2^65807000000000`; its integer threshold test rejects the preceding value.
All 54 strict outer inequalities and four functional inequalities pass.

These checks retain the native-all-columns, owned-erasure, uniform-compiler,
precision/tape and analytic-recovery assumptions. They do not materialize the
uniform word or the rounded integer multiplier. Independent scientific review
remains open. The selected frontier is not changed.
