# Exact p2 oracle repair minimum

The frozen p2 model of PR5587 needs exactly **240 new returns** at every width
f >= 72. Its previous bounds were 225 and 240. The new second-moment certificate
closes the integer gap. This is an arbitrary-linear-oracle optimum, with fixed
original inputs, history, capacities, ordinary algebra and targets.
Complete kappa is unchanged. No native 240-call supplier is supplied.

Read [PROOF.md](PROOF.md), [RESULT.json](RESULT.json) and [SOURCES.json](SOURCES.json).

```sh
python3 -B scripts/research_package.py --package research/p2-exact-oracle-repair
```

Use Python 3.12 and the standard library. Expected markers:
`PASS_P2_EXACT_ORACLE_REPAIR_240` and `PASS_REGISTERED_RESEARCH_PACKAGE`.
Normal and optimized checks use exact integer and rational arithmetic.

The source deficit, the source 240-return construction and the pointwise
Clifford theorem are credited premises, not independently replayed here.
The proof identifies the checked identities and the remaining caller obligations.
Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.

## Open next questions

Can a changed original paid input evade the fixed-history deficit with a
complete profitable bill? Specify that input, then rebuild the full history
module and invoice. More exact rank computation in this frozen model cannot
lower its now sharp return count.
