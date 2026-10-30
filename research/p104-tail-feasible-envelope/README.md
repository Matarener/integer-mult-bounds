# Complete P104 R22 tail-parameter envelope

For the fixed PR5756 invoice at saving `622627591/200000000000`, the existing
128-block compiler tail gates admit exactly one integer cutoff and completion
floor: **16 and 17**. The full positive offset interval is between two roots,
with enclosures near **0.0901726680035 and 0.193311515488**. The unique best
offset is in `(0.141270802754661, 0.141270802755571)`. Its best decay infimum
is in `(0.975481788192714, 0.975481788192715)`.

This is a scoped proof for the declared, complete invoice: 66,852 paid calls,
13,390 targets and rank surplus 760. It is not a new κ or supplier admission.
The source's prose count 12,958 is stale; this package uses its JSON and the
complete inventory. [PROOF.md](PROOF.md) proves coverage of all integer cutoffs,
all integer floors and the continuum of positive offsets. It permits every
rational decay with `decay^128 < 1/16`, not only the source's `125/128`.

The source point `(16,17,1/7,125/128)` passes. Offset `1/5` fails for every
permitted decay. Offset `1/10` fails at the source decay but passes at `489/500`.
Thus a failed fixed-decay test is not a proof that an offset is impossible.
The optimized tail margin does not raise the fixed invoice's moment crossing.

## Reproduce

Use standard-library CPython 3.12 from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/p104-tail-feasible-envelope
python3.12 -I -O -B research/p104-tail-feasible-envelope/verify.py
```

The checker authenticates inputs, imports the existing directed-integer power
engine and imports no source constructor or pricing engine. It uses exact
rational logarithm bounds, strict derivative and root brackets, and a convex
lower bound at the minimum. It includes 640 exact rational-power fixtures,
80 separate Decimal power checks, 80 separate Decimal logarithm checks,
missing-count rejections and passing/failing tail points. Decimal checks are
corroboration; all feasibility certificates use rational bounds. `RESULT.json`
uses outward rational rounding. No floating-point search is accepted as proof.

`ORIGINS.json` binds the retained source bytes to the exact PR5756 Git blobs.
`SOURCES.json` binds those bytes to this branch's retention commit and pins the
power engine and its dependency. The direct replay is read-only and Git-free.
The optional full-history provenance check needs history absent from this
shallow checkout. Normal and sealed replay evidence is in `VALIDATION.md`.

## Scope and credit

Canonical [Discussion5773](https://github.com/CrocSwap/integer-mult-bounds/discussions/5773).
Base `de5ec2e7a6074068452f45b1a191b5c72832df4a`, priority8. This changes the
independent-moment card to a compiler parameter-existence question. The active
R22 subspace optimizer has a distinct scope. The earlier adaptive-tail-entropy
and adaptive-gate-existence results concern a different compiler contract.

Credit Joel Pulikkan/GamingPuzzled's PR5756 construction, Ali Romman's PR5751,
flyingviper's PR5718, and all retained P104, native and controller contributors.
Credit Jacob Alan Sussman, zxv and Cao Yifan for the compiler gates; retain the
existing directed-power and invoice-comparator credits. New proof and checker
by Ali Romman with substantial OpenAI Codex assistance, without subagents.
Apache-2.0. This is author-side verification, not independent human acceptance.

The invoice's physical legality, native phases, chronology, precision, other
compiler gates, outer transfer and five framework assumptions remain separate.
No full source scientific replay, Lean or Docker run is claimed. The selected
frontier is unchanged. This does not limit a different invoice or compiler.

## Open next questions

- Can a legal changed helper invoice retain a nonempty tail interval? Supply its
  exact complete bill, then repeat these bounds. A legal construction is needed.
- Can a new fully charged completion or block rule enlarge the envelope? State
  its normalization, exit and rounding costs before optimizing its parameters.
