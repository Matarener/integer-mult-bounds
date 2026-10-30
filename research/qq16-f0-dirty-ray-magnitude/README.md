# Intermediate magnitudes on one F0 dirty-helper ray

**Scoped scalar ledger. No new exponent.**

On the common-chart scalar projection of the literal reviewed `programs.F_0`
word, the initial state `L359 = T` (every data and private register zero)
reaches intermediate coefficient **128T in data register L103** and **68T in
helper L609**. The same word then restores that input exactly. The published
cut used by the restoration-preserving fault is only **4T**. Selected κ stays
`0.001672660197076918`.

This is the intermediate ledger asked for by one ray. It is not a bound for
every dirty helper, not a Hilbert-norm certificate, and not an F17 consumer bill.

## Statement

Expand `programs.F_0` exactly as the scalar fault audit does: 26,099 events,
of which 21,025 are scalar. Non-scalar events do not change this projection.
Coefficients below are for `T = 1`; the word is linear and homogeneous, so the
`T` ray is the same scan multiplied by `T`.

| Class | Peak absolute coefficient | First attained | Gate, frame annotation |
| --- | ---: | --- | --- |
| Data `L0..L223` | 128 | after event 24280, `L103 = -128` | `L103 += 64 L354`, annotation `1` |
| Helpers `L224..L703` | 68 | after event 24338, `L609 = 68` | `L609 += -34 L354`, annotation `1` |
| Private `C0..C7` | 0 | — | never written on this ray |

Immediately before the data-peak add, `L103 = -64` and `L354 = -1`. A relative
destination defect `u(|d| + |c| |s|)` at that add therefore has allowance
**128 u T**. The coefficient `-128` then sits only in `L103` across the next
154 scalar states. At the published fault index 24438 the pre-state is still
`L39 = -4`, `L359 = 1`, and the final state is exactly the input.

The data ray `L112 = 1` is the control. Its largest absolute coefficient is 1,
every helper and private register stays 0, and it also restores exactly. At
event 24438 that ray contributes nothing to `L39` or `L359`.

A unit injection into `L103` after event 24280 does **not** preserve helper
restoration. Its final image has 78 nonzero data fields, maximum `1/16`, and
71 nonzero helpers, maximum `17/32`. The published fault at event 24438 is a
different site: there the helpers restore and the completed data factor is
`4 u T`. The intermediate peak does not replace that necessary reserve.

## What this does not say

`||F|| <= 58` in the #2965 completed-output contract is a bound on the finished
data map. An intermediate register coefficient 128 does not contradict it.
Frame annotation `1` is the word's label at the two peak adds. This package
does not load native frame vectors, so it does not promote 128T or 68T to
payload Hilbert norms. Exact execution of this ray has completed data error 0;
the peak is not an exhibited rounding failure.

Open [PR #3552](https://github.com/CrocSwap/integer-mult-bounds/pull/3552)
compares four stored final magnitudes with the #2965 tolerance and does not
replay intermediate states. The scalar-projection digest here equals that
package's published `scalar_projection_sha256`.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/qq16-f0-dirty-ray-magnitude/verify.py
python3.12 -B research/qq16-f0-dirty-ray-magnitude/test_verify.py
python3.12 -B scripts/research_package.py --package research/qq16-f0-dirty-ray-magnitude
```

`verify.py` is read-only. Dense lists and sparse dictionaries are separate
forward scans; both must report the same peaks, cut and final state. The tests
use a three-operation synthetic word and change the peak coefficient from 64
to 63. The full literal scan takes well under a minute.

## Open next questions

1. Do the frame annotations `1` at events 24280 and 24338 denote the constant
   payload vector, so the Hilbert norms are exactly 128T and 68T? The native
   dirty-fault package already checks frame 1's canonical vector on its own
   witness; this ledger does not.
2. Is register 359 special, or does another helper force an intermediate data
   coefficient at least this large? A uniform dirty range has to cover the
   worst ray. Only this ray was scanned.

## Credit

The literal F0 word and scalar projection are the reviewed joint-query
program. Arham Tahir's `qq16-producer-dirty-fault` package supplies the
expansion, the cut `(-4, 1)`, and the final-defect formula this ledger does
not replace. Nick Petalas's #2965 contract supplies the completed-output norm
`||F|| <= 58` and the open producer-interior question. Ali Romman and the
joint-query lineage retain the program. Tekalign's native binding is the
frame-vector predecessor named above and is not replayed here.

Prepared by unpaidmoon, with substantial assistance from Grok 4.7 in Cursor.
Apache-2.0. No independent human review is claimed.
