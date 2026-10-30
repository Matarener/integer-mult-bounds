# Remove duplicate ancestors from fixed PAIR coefficient evaluation

This package pairs local-ring coefficient algebra with compiler
common-subexpression elimination. It changes the actual serialized
`children.coefficient` path through a guarded, package-local `Callback.weight`
adapter. When the actual prepared fallback permutation fixes a head field,
two identical ancestor requests become one. The ancestor still runs, and the
inverse/unit check and both multiplications remain: malformed high fields and
nonunit ancestors are not hidden by premature algebraic cancellation.

For d consecutive fixed-head PAIR descriptors, preparation calls decrease from
`2^d-1` to `d`. Actual admitted nonzero-high-lift fixtures at d=1,2,3 verify
`1,3,7 -> 1,2,3`. At d=3 the entire coefficient call uses 2,228,010 record actions
instead of 2,840,912, a 21.57% reduction; both admissions, extension, stacks,
erasure and restoration are included. Numerical word actions decrease from 90,711,429 to 39,007,018 (57.00%)
on the same fixture; they are separately recorded in RESULT.json. The existing eleven record tapes and numerical backing suffice.
This is a measured fixture saving, not a full multiplication runtime claim.

The proof covers arbitrary accepted stable inputs and prime-power high lifts;
the shortcut is selected from the actual permutation, not inferred from a low
class. Nonfixed PAIR, reverse tail, GOOD, UNIT and half-unit branches retain their
contracts. General nonfixed trees may still branch exponentially. No runtime
coordinate is decoded into Python control, and no dynamic native cache is added.

The complete component invoice remains
`K_CSE = A_parent + E + A_leaf + W_CSE + N + D`.
Three physical leaf ADDs still require **six independent coefficient calls**,
with four positive and two negative-inverse calls. Admission scanning, matrix
preparation, source production, payload traversal and original-width stock are
not free. PR4011's separate admission cursor is not assumed in these measurements.
The selected conditional kappa remains 0.001672660197076918.

The finite fixtures are admitted rank-seven definitions in the exact physical
runtime, not an independently reconstructed full R437 source catalogue. An
actual-R437 occurrence census, complete physical payload replay and all caller
costs remain open. See PROOF.md for the sufficient-capacity error boundary;
source bytes and inputs must remain stable during execution.

## Replay

```
python3 -B scripts/research_package.py --package research/r437-fixed-pair-cse
python3 -B research/r437-fixed-pair-cse/verify.py
python3 -O -B research/r437-fixed-pair-cse/verify.py --quick
python3 -B research/r437-fixed-pair-cse/verify.py --export
```

The verifier never regenerates RESULT.json. Normal checks compare original and
adapted complete calls against an independent local-ring matrix oracle, with
Word.inspect forbidden in runtime. Controls cover malformed ancestor high digits,
nonunit root, false fixed-permutation guard, changed source/AST, false receipt,
missing input and symlink input. The export uses exactly declared inputs and the
package, without Git. All executable pins are canonical-main inputs; pending
predecessor PRs are attribution/motivation only.

## Open next questions

* Compose this adapter with PR4011's admission cursors on a source-bound pooled
  R437 request, preserving six independent calls, actual raw-source precision,
  and physical call/return. Start with the rank14 pooled request from PR4010;
  source/stock and full payload tariffs remain blockers.
* A stronger cancellation could use PR4008’s actual-source unit recurrence and
  credited `Page.child_weight` algebra, but only with a source-bound certificate
  that every skipped validation and unit failure has already been discharged.
  First price that certificate and its admission/cleanup; distinguish a generic
  admitted context from an actual selected context. No such cancellation occurs
  in this adapter.
* For nonfixed PAIR trees, measure repeated `(level, coordinate)` states and price
  a genuine encoded DAG/cache. A free host-language dictionary is not an answer.
* Measure how frequently the actual R437 prepared permutations fix requested head
  fields, and then incorporate this weighted saving into the complete invoice.
  This package does not supply that frequency or a new kappa.

## Credit

Chris R / Clear1nsight, with substantial OpenAI Codex assistance and same-session
AI cross-review; no independent human or formal-kernel acceptance is claimed.
The physical coefficient runtime and normal forms retain source527,
PR2160/2159/2234/2310/2332/2405, Jose Manuel's PR2697 and David Arias's PR2753
credit. The current stream and remaining bill build on zxv's PR3690, Chris R's
PR3967, PR3950 and PR4008 (`70c5ed674c7dc1c339254bae3818dd52a0015ac1`).
PR4008 identified duplicate fixed-PAIR ancestors and the six-call physical bill;
this package implements and proves the guarded shortcut. PR4011
(`fc1426353de3389409a27e5b9bc146a95edf811c`) independently optimizes admission,
which remains unchanged here. Nick Petalas's PR2989/3041 and commdata2338's
PR2399/3223 retain their conditional correspondence/substitution/stock credit.
Apache-2.0; frozen predecessors and the selected frontier are unchanged.
