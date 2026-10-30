# Gate-operand parity contract: the exact agreement condition and which export guards separate divergent from agreeing gates

**Boundary audit; no new κ.** The selected κ stays `0.001672660197076918`.
This is the gate-operand completion of the checker/exporter schema cascade:
[#2977](https://github.com/CrocSwap/integer-mult-bounds/pull/2977) named the
scatter multiplicity gap, `research/scatter-parity-contract-audit` (with the
#2992/#3273/#3346 successors) derived the exact scatter contract, and
[#3696](https://github.com/CrocSwap/integer-mult-bounds/pull/3696) showed that
destination-free gates always agree and left open question 1: does a
simple-support guard on gate operands reject all divergent dest-in-sources
cases without rejecting agreeing dest-free lists? This package answers it
exactly, with a measured guard census and the selected word's blast radius.

## The two operators, exactly

One gate `(d, srcs)` over registers `0..n-1`, with the pinned frozen sources:

- **Sym** (checker `xcheck_p.py`, `run`): `acc = XOR(val[s] for s in srcs)`
  reading pre-gate values, then `val[d] ^= acc` once.
- **Exp** (exporter `export_records.py`, `run`): one `ADD(d, s)` per listed
  source, replayed sequentially over current values, so a source equal to `d`
  re-reads the destination and annihilates whatever it accumulated.

Both are linear maps over F2^n, so agreement on the register basis is
functional agreement for every valuation. The checker additionally requires
`srcs` nonempty with all of `[d] + srcs` distinct (`bad operands`), so every
checker-accepted gate is destination-free.

## The agreement contract

Let `m` be the multiplicity of `d` in `srcs` and `k` the index of its last
occurrence. Coefficient-wise over F2:

> **Sym and Exp agree iff `d ∉ srcs`, or (`m` odd and every register `r ≠ d`
> occurring before position `k` occurs an even number of times before `k`).**

- Destination-free: both maps write `x_d ⊕ Σ_{r≠d} occ(r)·x_r`. They agree for
  every source list, repeated or not.
- Destination-in, `m` even: Sym keeps a `x_d` term (coefficient `1 ⊕ m = 1`);
  Exp's last self-ADD annihilates it. Always divergent.
- Destination-in, `m` odd: the `x_d` terms cancel in Sym; Exp keeps only
  sources after position `k`. They agree iff the pre-`k` part cancels
  per-register (`[d]`, `[d,a]`, `[a,a,d]`, `[d,d,d]` agree; `[a,d]`, `[a,b,a,d]`
  diverge — an even pre-count cancels, an odd one does not).

## Measured census (standard library, independent implementation)

All `(d, srcs)` pairs with 6 registers and source lists of length 0..4 — the
same bounded domain as the published gate-operand census — plus a length ≤ 5
extension. Simulation and the coefficient-level prediction agree on **100%**
of pairs in both domains (asserted per pair):

| class | pairs |
|---|---:|
| domain (n=6, len ≤ 4) | 9,330 |
| destination-free, all agreeing | 4,686 (matches the published census exactly) |
| destination-in | 4,644 |
| divergent | 3,492 |
| agreeing destination-in | 1,152 |
| extended domain (len ≤ 5) | 55,986 |
| extended divergent | 26,172 |

## Guard census at the export boundary

| guard (accept iff) | accepted | divergent admitted | agreeing rejected | sound |
|---|---:|---:|---:|---|
| `checker_contract` (srcs nonempty, `[d]+srcs` distinct) | 1,230 | 0 | 4,608 | yes |
| `distinct_only` (drop the nonempty clause) | 1,236 | 0 | 4,602 | yes |
| `dest_free` (`d ∉ srcs`) | 4,686 | 0 | 1,152 | yes |
| `srcs_simple` (scatter guard transplanted) | 3,102 | **1,350** | 4,086 | **no** |
| `exact` (the contract above) | 5,838 | 0 | **0** | yes |

Accepted sets form the strict chain `checker_contract ⊂ distinct_only ⊂
dest_free ⊂ exact` (1,230 / 1,236 / 4,686 / 5,838). The accepted counts match
closed forms independently: `checker_contract` accepts 6·Σ P(5,L) = 1,230
ordered distinct nonempty lists per destination, and the transplanted guard's
1,350 divergent admissions are exactly the simple destination-in lists with
`d` not first.

## The answer to the open question

**Not as literally stated, for the simple-support guard.** Distinct-operand
guards do reject every divergent destination-in gate (all 3,492), but they
also reject agreeing destination-free lists — 4,608 of them on this domain,
the smallest being the empty source list and the smallest nonempty one being
`[a,a]`. Every one of those rejected agreeing lists is already rejected by the
checker (`bad operands`), so **no checker-accepted word is affected**; the
boundaries align exactly when the exporter adopts the checker's own operand
contract. The only guard that is simultaneously sound and free of agreeing
rejections is the exact minimal guard above. A scatter-style simple-support
guard on `srcs` alone is **unsound**: it admits 1,350 divergent gates
(destination among the sources but not first, e.g. `[a,d]`), so the scatter
schema does not transfer to gates unchanged.

**Blast radius on the selected word.** The pinned tuned word
(`SHA-256 e3e301e6…`, `v=111`, `R=439`) has **5,472** D/A/B/C gates, every one
with distinct nonempty operands, and 111 simple scatter rows over nine
retained totals with 527 terms. Under any of the three sound guards every
selected gate is accepted and its Sym/Exp agreement is the destination-free
lemma, so the selected word's exported records are unchanged. This is a
census of the pinned word's gate lists, not a record-stream replay; the
27,234-record baseline and the 27,235-record `self_even` mutant emission are
the published package's measurements and are cited, not re-derived here.

## Reproduce

The registered hook requires Python 3.12; the verifier itself is standard
library and runs on 3.10+. From the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/gate-operand-parity-contract
python3.12 -I -O -Werror -B research/gate-operand-parity-contract/verify.py
```

Expected:

```text
PASS_GATE_OPERAND_PARITY_CONTRACT domain=9330 dest_free_agree=4686 dest_in=4644 divergent=3492 agreeing_dest_in=1152 checker_sound=true checker_over_rejects=4608 transplant_admits=1350 exact_over_rejects=0 selected_gates=5472 selected_distinct=5472 no_new_kappa
```

Admission uses an explicit `need()` that stays enforced under `-O`. The
verifier is read-only: it writes nothing. Runtime is a few seconds. The three
live inputs (tuned word, checker, exporter) are hash-bound in
[SOURCES.json](SOURCES.json) and their decisive source lines are asserted as
exact substrings; both operators' semantics are re-implemented here, not
imported. The published cross-check constant 4,686 comes from the
gate-operand-export-parity package's census on the same domain and is checked,
not imported.

## Open next questions

1. **Which sound guard should a successor gate schema adopt?** The checker's
   own contract is the minimal change (exact boundary alignment, no
   checker-accepted word affected); `dest_free` additionally admits agreeing
   duplicate-source gates the checker still rejects; `exact` additionally
   admits agreeing destination-in gates. Weakening the export guard without
   loosening the checker contract re-opens the two boundaries. First step:
   compose the chosen guard with `simple-scatter-v1` / `integer-xor-scatter-v1`
   in a successor checker/exporter pair. Blocked by the schema-adoption review
   of the #2977 cascade, not by arithmetic.
2. **Does the native formal-column checker independently reject a divergent
   self-operand export?** First step: feed the `[d,d]` mutant's export to the
   native column checker. Blocked by a C++17 toolchain; the synthetic word is
   outside the selected producer either way.
3. **Does the contract survive reordered emission?** The divergence class
   depends on source order through the last self-occurrence. If a successor
   exporter reorders or buffers sources, re-derive the condition; the census
   harness here re-runs with any per-source emission order.

## Scope, credit and verification limits

Base main `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority revision 6.
Card `supplier-boundary-audit` with `scope_status: changed` — the scatter-side
obligation is settled on main by `scatter-parity-contract-audit` and the
#2992/#3273/#3346 successors, and this package takes PR3696's stated open
question 1; the scope change and its justification are recorded in
[TASK.json](TASK.json). Overlap was checked with `scripts/find_overlap.py`
against open PRs and discussions and by reading the cascade's packages.

Credit **Nick Petalas** for naming the scatter multiplicity gap (#2977);
Kumagi for the exact scatter agreement contract (#3004); Wentao Li
(VictorLiwentao) for the gate-operand census, witnesses and open question this
package completes; Dylan Crow for the exporter; eumemic for the symbolic
checker; and the retained tuned-word lineage. Predecessor notices and source
licenses are unchanged.

This contribution was produced by Nick Petalas with AI assistance. Separate
internal source inspection and review do not constitute independent human or
proof-assistant review. No new kappa, no supplier admission, no production
schema adoption, no selected-frontier change, and no claim about any bound for
multiplication is made here. Full selected cold replay, all-size transfer and
hosted CI are not claimed.
