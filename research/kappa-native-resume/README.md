# Kappa native continuation

This cumulative research continuation adds an exact cheaper clean-J core
rebase, a padded shared-helper cover with full-macro connector fusion,
causal scalar simplification, changed QQ16 geometry probes, and exact
native-cost/minrank target gates. **No new multiplication κ is admitted.**

Read [REPORT.md](REPORT.md) for the findings, quantitative limits and next
implementation targets. [RECOVERY.md](RECOVERY.md) states exactly which
prior archive bytes were available and the known later-archive recovery gap.

## Replay

```sh
python3 research/kappa-native-resume/validate.py \
  --output /absolute/path/to/fresh-native-validation.json
```

The scoped replay needs Python 3.12, NumPy and Node.js. It authenticates
the delivered files and runs from an isolated copy. It does not invoke
network access or the historical full release engine. The stage-level
claims are enumerated in `REPLAY-PLAN.json`.

`INTEGRITY.json` authenticates source and reference results. The generated
`VALIDATION.json` binds the actual fresh run to that manifest. The enclosing
cumulative overlay has its own full archive/path/blob manifest and safe
apply procedure.

The literature links and their scoped use are in `LITERATURE.json`.
Retained sources are unmodified and pinned in their adjacent provenance
records. New work includes OpenAI assistance and follows the repository's
Apache-2.0 context.
