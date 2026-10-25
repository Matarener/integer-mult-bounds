# Compact-switch contract

**Scoped contract audit. No new κ.** The selected conditional result stays
0.001672660197076918. This does not accept PR #4100 and it does not formalize
the lemma in a proof assistant.

## Scope and evidence

Card `formal-interface-lemma`, scope **refined**. The catalogue's first
experiment for #4100 is to audit the compact-switch statement and its
hypotheses before a formalization campaign. That audit is the result here.
Gate-operand parity (#3807) and certified endpoint arithmetic (#3857) are
left untouched.

The object is the one-target cancellation and the two-call macro in
`research/unconditional-batched-crt/CRT.md`, section 4, at base
`12fa8c5c844be21bfefb38a19503fbd867a11244`. The displayed gadget is

```text
y += sum_i 2 z_i t_i 2^j_i;
t += sum_i y[j_i] B^i;
y += sum_i z_i (1-2t_i) 2^j_i;
t -= sum_i (y[j_i] XOR z_i) B^i.
```

The same section then says that the two `y` additions have total `z(1-2b)`.
Those two readings disagree. `t_i` is introduced as the digit before `F`.
Reusing that same integer in the third line is a frozen coefficient. The
total `z(1-2b)` is the live digit after `t <- t+b`. The published
`primitive_f` in `check_batched_crt.py` implements the live digit.

## Lemma

Let `B >= 2`, let `τ` be an integer in `0, ..., B-2`, and let `b, z` be bits.
Place the target at bit 0 and let the `m` bits above it hold an integer
window `W` with

```text
0 <= W <= 2^m - B + 1.
```

Set `L = b + 2W`. The post-increment step

```text
L1 = L + 2 z τ
τ' = τ + b
L2 = L1 + z (1 - 2 τ')
```

returns `L2 = L + z(1-2b)`. The target bit flips exactly when `z = 1`, the
window returns to `W`, and neither `L1` nor `L2` uses a bit at position
`m+1` or higher. The updated digit `τ'` is at most `B-1`, so a packed
base-`B` increment does not carry into the next digit. Subtracting the final
bit `b XOR z`, XOR `z`, removes exactly `b` from the digit `τ+b` and restores
`τ` without borrowing from the next digit.

The published margin `2B <= W < 2^m - 2B` implies the bound above for every
`B >= 2`. It is sufficient for this isolated step. It is stricter than the
step requires: `W = 0` satisfies the identity, and the first overflowing
window is `W = 2^m - (B-2)` when `B > 2`, at `τ = B-2` and `z = 1`.

Execute that step, add a Boolean `f` into the control digit, and execute the
step again. If `f` does not read the target bit, the two live parities are
`z` and `z XOR f`, the target ends as `b XOR f`, and both the control digit
and the window return to their starting values. The same holds for several
targets whose `K`-bit guards are pairwise disjoint, with `K = m+1`, when
every source omits every active target and every control digit is at most
`B-2`.

## Witnesses

All of the following use `B = 4` and the published good predicate
(`guard = 6`, so `m = 5` and `8 <= W < 24`).

| Reading | Start `(u, t, y)` | Endpoint |
| --- | --- | --- |
| One post-increment step | `(1, 0, 17)` | `y = 16` |
| One frozen step | `(1, 0, 17)` | `y = 18` |
| Macro, live digit, `f = 0` | `(1, 0, 17)` | `(1, 0, 17)` |
| Macro, frozen digit, `f = 0` | `(1, 0, 17)` | `(1, 0, 19)` |
| Published `primitive_f` | `(1, 0, 17)` | `(1, 0, 16)` |
| Published `compact`, `f = 0` | `(1, 0, 17)` | `(1, 0, 17)` |

`y = 17` is bit 0 set and window `W = 8`. The frozen step adds `+1` at a set
bit and changes the window. The published checker follows the live digit.

Targets at bits 0 and 1 both meet the per-target margin on
`(u, t, y) = (0, 1, 80)`, with sources `(bit 4, bit 5) = (1, 0)`. The ideal
restoration is `(0, 1, 81)`. The live macro returns `(0, 5, 81)`: the data
bit flips and the control word does not return. Disjoint guards are a
hypothesis of the simultaneous claim. The published finite sweep uses
positions `(0,)` and `(0, 6)`, which are disjoint at `guard = 6`; it does
not see this pair.

A source that reads bit 0 on the same start `(1, 0, 17)` ends at `(0, 0, 17)`.
The load and the unload disagree, so omitting every active target is required.

Finite corroboration, all checked by this package:

- 25,592 isolated windows across `B in {2,4,8,16}` and `m = 8`, including
  windows below the published lower margin, with 3 sharp overflows.
- 656 published-margin windows, every one inside the sharp range, and 90
  sharp windows outside the published margin.
- 36,864 single-target macros on every published-good address in
  `u, t < 16`, `y < 256`, for both constant sources.
- 331,776 disjoint two-target macros, positions `(0, 8)`, on every
  published-good address in `u, t < 16`, `y < 2^14`.

## What this does not establish

The twelve paid `H`-bit exchanges, the reservoir shuttle, the bad-key sort,
the `O(V)` guard scan, and the all-size CRT/multiplication assembly are not
replayed. A passing isolated identity does not discharge those obligations.
No Lean proof is supplied. The published `2B` margin remains a valid
sufficient condition for the density estimate in CRT.md; this package does
not replace that estimate.

## Reproduce

From the repository root, Python 3.12, standard library only:

```sh
python3.12 -B research/compact-switch-contract/verify.py
python3.12 -B scripts/research_package.py --package research/compact-switch-contract
```

The direct command prints `PASS_COMPACT_SWITCH_CONTRACT` and the counts
above. Local runtime is a few seconds.

## Open next questions

1. Formalize the live-digit lemma, with disjoint `K`-bit guards and
   target-omitting Boolean sources as hypotheses. The statement above is the
   one to formalize; freezing `t_i` at its pre-step value is a different
   operation. A proof-assistant build is a separate budget. Nothing in the
   arithmetic is still unresolved for that lemma.
2. Recompute the section-4 bad-density estimate from the sharp window
   `0 <= W <= 2^m - B + 1` and check whether the existing `O(V)` room still
   holds. The first step is to replace only the `8B/2^K` term and compare it
   with the printed `2^-G E(p, ell)` bound. The blocker is the rest of that
   amortization, which this package does not audit.

## Credit

The compact-switch writeup and `check_batched_crt.py` are Cinna Davis's
PR #4100 (`research/unconditional-batched-crt`, head retained on this base
as `337d04939571a637aeab54a0f58f54fde811663a` in the family record). This
package does not rerun that construction. Prepared by unpaidmoon with
substantial Cursor Grok assistance. Apache-2.0.
