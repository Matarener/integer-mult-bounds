# Gate operand symbolic/export parity

**Card `supplier-boundary-audit`, priority revision 6**, refined to PR
[#3004](https://github.com/CrocSwap/integer-mult-bounds/pull/3004) open question 2
under the [#2977](https://github.com/CrocSwap/integer-mult-bounds/pull/2977)
checker/exporter cascade. No new kappa
(`0.001672660197076918`).

#3004 characterised scatter rows and left gate operand lists as a schema-consistency
question, stating that accepted words cannot diverge and that “no known divergent
word exists.” This package supplies the missing gate-side contract:

- **Sym** (checker): accumulate source XOR from the pre-gate valuation, then XOR
  into the destination.
- **Exp** (exporter): sequential `ADD` of each listed source into the destination,
  re-reading the current valuation.

If the destination is absent from the source list, Sym and Exp always agree — even
with repeated sources. If the destination appears among the sources, they can
disagree. Concrete witnesses include `srcs = [d, d]` and `srcs = [a, d]`.

The selected checker rejects every non-distinct operand list (`bad operands`)
before export. The exporter does not enforce distinctness and will emit the
extra `ADD`s. A scatter-only uniqueness guard therefore misses this gap.

```sh
python3.12 -I -B research/gate-operand-export-parity/verify.py
```

Expected:

```text
PASS_GATE_OPERAND_EXPORT_PARITY dest_free_agree=4686 dest_in_disagree_witnesses=2 selected_distinct_gates=5472 checker_rejects=4 no_new_kappa
```

## Evidence

- Exhaustive census on 6 registers and source lists of length 0..4: **4686/4686**
  destination-free patterns agree; destination-in patterns include disagreements.
- Named witnesses `self_even` and `dest_with_src` diverge on integer valuations;
  destination-free duplicate sources still agree.
- Pinned selected tuned word: all **5472** D/A/B/C gates have distinct operands;
  baseline export has **27234** records.
- Mutating `B[0]` from `[127, 111, [3]]` to self-operand forms: checker rejects
  all four mutants with `bad operands`; exporter still runs and the `self_even`
  mutant emits **27235** records.
- Scatter rows of the self-operand mutant remain unique, so a scatter-only guard
  accepts them.

Default verify is read-only against `CERTIFICATE.json`. Admission uses `need()`
and stays enforced under `python -O`. Explicit `--write` regenerates the
certificate only.

## Reproduce

```sh
python3.12 -I -B research/gate-operand-export-parity/verify.py
python3.12 -I -O -Werror -B research/gate-operand-export-parity/verify.py
python3.12 -I -B research/gate-operand-export-parity/independent.py
python3.12 -I -B research/gate-operand-export-parity/test_package.py
python3.12 -B scripts/research_package.py --package research/gate-operand-export-parity
```

## Open next questions

1. **Should a successor schema reject destination-in-sources gates at export time?**
   First step: compose the distinct-operand check with an existing opt-in boundary
   (`simple-scatter-v1` / `integer-xor-scatter-v1`) before export. Blocked by
   maintainer schema adoption, not by arithmetic.
2. **Does native legality independently reject self-operand gates?** First step:
   feed the `self_even` export into the native column checker. Blocked by a C++
   toolchain in this session; not required for the Sym/Exp lemma.

## Credit

Nick Petalas / #2977 named the scatter multiplicity gap. Kumagi / #3004 gave the
exact scatter agreement contract and left the gate-operand question open. Dylan
Crow authored the exporter; eumemic the symbolic checker; the tuned PR589 word
is the retained selected bit supplier. Predecessor notices are unchanged.

Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
No independent human or proof-assistant review is claimed.
