# Successor hand-off of productive conduit helpers: a verified proof of concept (no κ claim)

This package introduces a native operation pattern, the **successor hand-off**. It demonstrates the pattern exactly
on a scaled-down instance and prices what it is worth on the selected #5413 profile. It also shows exactly why
the current #4610 word admits no hand-off. **No κ is claimed.** The mechanism only gains inside a new native word,
and this package does not build one.

> **Addendum (follow-up, `addendum-r19-neutrality/`): a local hand-off is gain-neutral once re-flagging is priced.**
> Between two anchors a register's paid rank mass is fixed. Routing any register through a mid frame F therefore costs
> g(p,q) = f(p) + f(q) − f(p+q), the same concave function as the hand-off gain.
> - **Screen (exact rows):** all 408 helpers of the #4610 word, every event and every mid frame, both orientations,
>   about 1.88M points per orientation, with holder and cancellation lifts priced. **0 net-positive.** Wherever all
>   holders can be lifted, the carried data contains port inputs held only by registers on dim 5–8 frames not
>   contained in F, which climbs can never bring back.
> - **Designed F2^9 conduit blocks (exact replay):** a hand-off is **exactly neutral** (dM = 0) when the helper starts
>   at its load frame. With a bottom holder, a later entrance with no hand-off dominates by at least 0.004192.
> - **Consequence:** the 0.0035309 ceiling below counts the hand-off gain without the re-flagging cost, so it is
>   **not** an achievable estimate. A gain needs a new *main* transform, whose port flags pass through the helpers'
>   mid frames with the carried data unchanged; a local helper block is not enough.
>
> `addendum-r20-p19-repricing/` separately prices the p19 line of #5270/#5440 with the reviewed costs charged. The
> corrected complex saving is 0: the 4,256 missing letter-Q rank-1 jobs per unit are about 3.5× the 1,202 tolerance,
> and merging cannot rescue it (≥ 4,179). This agrees with zxv's and Matarener's numbers and adds the merge-robust
> bound, the idle-Q count and the literal middle-idle pricing.

Labels used below:
- **checked**: an exact computation in this package, reproduced by `verify.sh`.
- **screen**: an exact computation whose interpretation covers only the stated rewrite family.
- **argued**: a written argument that is not machine-checked.

## The mechanism

In the productive-helper paradigm (#4359), a helper's arbitrary input that climbs from dim d0 to dim d1 earns one
rank-(d1−d0) target. By concavity of x^(1−C), splitting that one target into a + b at the **same** paid climbs is
a strict gain: f(a) + f(b) − f(a+b) > 0. R16 (#5469) looked only for free *pure* split points and found none.

The successor hand-off produces the split constructively, with a second helper:

1. A successor helper `s` (a fresh arbitrary input) **starts at the mid frame F** and stays idle there.
2. **Co-framed cancellation.** At time t, conduit helper `h` and the port data D it carries meet at F, with D
   unchanged. Free ADDs at F make `h` pure (`h −= x`) and load `s` (`s += x`). `h` retires at F.
3. **Renaming.** Every later operation on `h` acts on `s` instead.
4. **Successor pre-subtraction.** Each consumer above F used to pre-subtract `h_in` and later receive
   `h_in + D` through the conduit. It now pre-subtracts `s_in` during its own early pass through F, while `s` is
   still idle and pure.

Paid climbs are unchanged and the target mass is unchanged. The single target d1−d0 becomes (dim F − d0) + (d1 − dim F).

**Hand-off condition (argued in general, checked on the gadget).** Let τ swap the inputs `h_in` and `s_in`.
Suppose free scalar edits up to time t bring every register to τ(its original row), with two exceptions: `h` holds
exactly `h_in`, and `s` holds τ(original row of h). Then every later operation is linear and frame-identical. So
the final state is τ(original final state): `s` ends holding `s_in` at h's old final frame, `h` ends holding `h_in`
at F, and every other register is unchanged.

Prior art, stated honestly:
- R16 split screen (#5469): pure point and no other holder. Here the condition is generalised to co-framed
  cancellation, deferred cancellation and pre-subtraction.
- #4441 (helper retiming) and #4470 (entrance/exit lattice). A hand-off at a pure point with no outside holder is
  only a later helper entrance.
- #3039 (block-climb obstruction, older cost alphabet).
- #5462 (relations; a hand-off that is not free leaves coupled outputs).
- "Relay" in the P104 packages means value delivery paths. That is unrelated.

We found no PR that hands a conduit to a successor helper that starts mid-flag.

## 1. Constructive proof of concept: `gadget.py` (checked)

The instance lives on F₂⁵ and uses the conduit motif of #4610 helper threads (compare h300, which reads x19 at
dim 1, carries it on another flag, delivers it, and uncomputes at dim 9). Its registers:
- port x: frames A → Xb → F → U;
- consumers m1 (at B) and c (at G);
- helper h;
- for the hand-off, successor s, which starts at F.

`nreplay.py` is the interpreter. It enforces exactly the rules of `native_extensions.literal_replay`, generalised
to any register count. `control_4610.py` checks it against the original: it reproduces `literal_replay` on the
#4610 word, with identical rows on all 632 registers plus C0, both orientations, and profile
{1:2201, 2:412, 3:510, 4:127, 5:40, 8:8}.

| word | exact on all arbitrary columns | paid profile | helper climbs | productive targets |
|---|---|---|---|---|
| baseline (conduit uncomputed at the top) | yes (4 columns) | {1:12, 2:2, 3:1} | h: 5 | [5] |
| successor hand-off at F | yes (5 columns) | {1:12, 2:2, 3:1} | h: 3, s: 2 | [3, 2] |

Three mutation controls are each rejected:
- no successor pre-subtraction (wrong endpoint row);
- no co-framed cancellation (wrong endpoint row);
- cancellation attempted before x reaches F (frame violation).

**Gain per unit.** One hand-off adds dM = f(a) + f(b) − f(a+b) at the root. On the selected #5413 profile
(`price_handoff.py`, Decimal at 50 digits; raw roots, not the strict compiler):

| hand-off | dM each | raw root, one per local in all 18 locals |
|---|---:|---:|
| 9 → 4+5 | 0.018612 | 0.0030286465 (+1.36e-6) |
| 9 → 3+6 | 0.017248 | 0.0030285469 |
| 9 → 1+8 | 0.009464 | 0.0030279787 |
| a single hand-off anywhere | ≥ 0.0084 | ≥ 0.0030273222 (> U = 0.00302728825) |

The ceiling, with every rank-9 helper handed off once at 4+5, is 0.0035309 (gain-only; see the addendum: re-flagging costs cancel it locally).

The table shows that a **single** legal hand-off would raise the raw root by about 3.3×10⁻⁸. That is far more
than U's 6×10⁻¹⁴ gap and than the roughly 10⁻¹¹ that the strict compiler reserves below the raw root. This is
argued, not funded.

**Scope of the gadget.** The conduit above F is needed in the gadget only because consumer c must leave F before x
arrives there. That ordering stands in for the dependency structure of a real word. If c could wait at F, reading
x directly would dominate.

## 2. The #4610 word admits no hand-off (`screens/`, exact screens)

Base word: `research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz`. Rows are replayed exactly over ℚ in the free
group ring of warp words. The pool covers helpers at an intermediate frame (start dim < dim F) with climbs ahead.

| screen | forward | backward |
|---|---|---|
| necessary span condition h_in ∈ span(rows at F) (`spanb.py`) | 172 helpers (168 at pure points just after the first climb) | 65 helpers (all pure points) |
| co-framed cancellation with all h_in holders at F (`relay.py`) | 0 | 0 |
| pure point + deferred cancellation by the rest of the program (`relay2.py`, 257 / 455 tests) | 0 | 0 |
| pure candidates whose outside h_in holders never visit F, so pre-subtraction is impossible (`presub.py`) | 165 of 168 (3 partial) | 65 of 65 |
| fewest foreign input variables left in h after co-framed cancellation, where (a) holds (`relay_def.py`) | 6 | 2 (67 helpers at dim 3) |

**Reading.** The only points where a hand-off is linear-algebraically possible come right after a helper's first
climb, before its first read. At every such point, the helper's input has already been spread at the entrance into
consumers, and those consumers recollect it only at the top frame. Away from those points, the carried port data
never shares a frame with a copy of itself. The helper flags and the port flags cross only at dim 1 and dim 9.
So the existing word gives no hand-off. This is consistent with the conclusion of #5465 and #5469 that fixed
operation sets are exhausted.

## 3. The other candidate mechanisms (argued)

- **A. Field packing / mixed recursion sizes.** #4359's balance Σ p_r r^(1−C) counts paid arrays. A rank-r job on
  a pack of k fields is k standard rank-r jobs, so packing changes nothing. Transforming the pack axis would turn
  free scalar mixing into paid rank. In a volume-weighted invoice, the rank of a job grows only by merging
  consecutive climbs of the *same* data, which is lever B. A multi-size recursion is admissible only in that
  volume-weighted form, and it brings no gain.
- **B. Pre-gathered helper reads.** In the native grammar, data changes frame only through paid climbs or
  registered warps. Staging in owned C0 costs paid centre transports with zero credit; #3039 is the analogue in
  the older alphabet. Defragmentation at a fixed operation set is closed (#5426, #5465). B therefore needs new
  flags in which helpers and port lines cross at mid frames. That is the same requirement as the hand-off, which
  converts such a crossing into a split target.
- **C. Product-output helpers.** The successor hand-off **is** a concrete form of C, with the 9 → a+b split
  realised by two independent helpers and no relation decoding.

## What remains to scale it to a full supplier

1. Build a new native local word in which conduit helpers meet the port lines they carry at a mid frame, with the
   data unchanged (flag crossings). Consumers above that frame must pass it before the hand-off.
2. Re-run the full admission chain:
   - all-632-column replay in both interpreters;
   - Clifford admission of any new G maps;
   - helper boundaries and the controller;
   - the owned relations of #5383, which are pinned to helper rows and must be re-derived;
   - the #5402/#5413 caller;
   - the strict compiler and the 54 outer predicates.
3. Hand-offs must not add paid work. Any extra rank-1 job costs about 1, which outweighs the ≤ 0.0186 a hand-off
   earns.

## Reproduce

```sh
sh research/helper-handoff-r18/verify.sh      # PASS_HELPER_HANDOFF_R18 (~60 s, python3.12, stdlib only)
```

Expected outputs (`*.txt`) are stored next to each script.

**Credits.**
- Cao Yifan (#4610 word and native semantics).
- zxv (#4359 productive-helper paradigm; native interpreter `literal_replay`).
- Clear1nsight (#5413 caller and profile).
- #5409 (ceiling U).
- Matarener (#5422/#5426/#5433).
- aliromman (#5383 relations).
- #4441/#4470 (helper retiming and lattice).
- Aaron Wang (#3039).

AI disclosure: Claude Opus 5.5 (Anthropic) via Claude Code, directed by Joel Pulikkan (GamingPuzzled). Apache-2.0.
