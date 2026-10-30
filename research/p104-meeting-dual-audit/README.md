# Exact vector audit of the paid-meeting helper cuts

All 23 cuts in PR #5751 pass a separate vector audit. The checker reconstructs
the exact published word and witness, checks all 776 scalar input columns and
recounts the complete declared invoice. It imports no archived constructor,
scalar checker or pricing engine. The source is pinned at
`8483f9a679d06c1e270141dbc686a7e76e7a7522`.

This resolves the scalar-cut portion of the released frame-105 review request.
The same method covers all 21 meetings. It checks the prefix and suffix modes,
both bases, helper restoration, actual field frames, paid subdivisions, dirty
owned inputs and COPY zero conditions. The [proof](PROOF.md) gives the exact
predicates and an invertible two-field counterexample to a weaker rule.

Frame 105 has three successive cuts. The last uses an input created by the
previous cut, so each check uses the newly constructed word. All 23 target
credits and all 27 added paid queries per local call survive the full recount.
The complete counts are 66,834 paid calls and 13,390 productive targets. The
rank surplus is 760. These figures confirm the source bill; they are not a new
kappa improvement.

## Reproduce

Python 3.12 and the standard library suffice:

```sh
python3.12 -B scripts/research_package.py --package research/p104-meeting-dual-audit
python3 -B scripts/compare_recursive_invoices.py research/p104-meeting-dual-audit/SOURCE-INVOICE.json research/p104-meeting-dual-audit/INVOICE.json
```

The registered audit authenticates the retained source, checks all cuts and
columns, then compares RESULT.json and both invoice files exactly. Only the
explicit `--record` option writes those files. The signed-invoice preflight is
expected to be inconclusive: the improvement does not dominate every concave
tariff. These bills exclude compiler completion parameters.

The vector implementation is checked against explicit dense matrix products
for 4,369 finite programs, including singular INIT, CLEAR and COPY operations.
Twenty source-specific negative controls reject, including changed cut vectors,
false physical frames, missing basis work, missing paid queries, nonzero COPY
targets, missing caller events and invented productive targets. The separate
algebraic control shows why pivot restoration cannot be omitted.

## Scope and attribution

This is exact scalar, chronology and invoice evidence for one source. It does
not replay native phases, prove physical caller operators or revalidate the
compiler and outer theorem. The five inherited assumptions remain. The two
implementations are separate code paths from the same contributing account;
independent human acceptance is not claimed. See [VALIDATION.md](VALIDATION.md)
for exact execution and publication status.

The official 20-file PR #5751 export is retained byte-exact, with its notices
and complete predecessor closure. Its digest matches the source publication.
Credit the paid-meeting construction, flyingviper PR #5718, the PR #5599/5609
helper identity, Joel Pulikkan/GamingPuzzled PR #5684, and all retained sources.
The [NOTICE](NOTICE) states the new and reused work. New audit: Ali Romman with
substantial OpenAI Codex assistance; no subagents. Apache-2.0.

Base `de5ec2e7a6074068452f45b1a191b5c72832df4a`, priority 8.
[Canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/5764).

## Open next questions

- Bind this exact scalar certificate to an independent native-phase and complete
  physical-caller check on the same head. The present audit does not transfer
  the source author's native acceptance.
- Audit the changed completion parameters with the actual new bill. The old
  cutoff and tail bound are not compatible merely because rank mass is preserved.
- For a successor word, pin its source and rerun every cut on the changed
  intermediate program. A successful cut from this head is not a reusable
  acceptance receipt for another schedule.
