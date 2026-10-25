# Uniform lazy signed-affine routing for lender333

The actual finite boundary in `staged544-paid-native-fusion` has a uniform
all-width realization with O(N) bounded-word address work and no N-entry routing
table, where N=512^f. It preserves all four arbitrary caller arrays and saves
exactly2N real writes against the strong materialized comparator. Its principal
routing counts also fall from36 to29 odometer lanes and34N to27N leader
comparisons. No recursive child, owner-width or κ improvement is claimed.

[PROOF.md](PROOF.md) gives the quantified algorithm, exact traffic/route categories,
owned metadata, setup and clearing obligations, and remaining tariff boundary.
Setup is fixed but nonzero; no total-time crossover is asserted without fixing
its actual primitive tariffs. The common native child and L suffix remain paid.

```
python3 -I -W error -B research/native-lazy-tensor-boundary/verify.py
python3 -I -W error -O -B research/native-lazy-tensor-boundary/verify.py
python3 -B scripts/research_package.py --package research/native-lazy-tensor-boundary
```

The verifier authenticates the retained exact source boundary/proof, reconstructs
all512 base mappings, checks the actual dirty four-array boundary, uses a separate
out-of-place oracle, exercises tensor cycles and phases on small exhaustive
fixtures, and rejects altered phases/translation/composition. RESULT is regenerated
and compared. Finite probes support the uniform proof; they do not prove it by
extrapolation. Runtime code uses standard-library Python as executable evidence,
not cycle-accurate RAM timing. The source f=1 native certificate is a retained
premise rather than freshly repeated here.

Source base32890bc5de034ab8fc93ac88ead7279a6a416d04, priority7; selected5413 remains
unchanged. [Discussion5474](https://github.com/CrocSwap/integer-mult-bounds/discussions/5474)
is the canonical investigation. Full open-PR and Discussion overlap was coordinated
by root before assignment; this is the explicit all-f handoff of the predecessor,
not a new phase-tag normalization or native recipe census.

## Open next questions

- Fix the ordinary RAM primitive tariff and execute the complete setup/runtime
  instruction trace to determine its crossover against a stronger downstream
  fused comparator. The categories here do not determine actual machine time.
- Bind the lazy ownership representation into one current complete native caller,
  with its precision, fixed-tape and clearing obligations. The historical PR3945
  cut alone does not imply admission into selected5413.

Prepared by JoyboyBrian with substantial OpenAI Codex assistance; Apache-2.0.
Credit Chris R/Clear1nsight for the actual paid-native-fusion boundary and fair
comparator, ToikY PR4002 for phase tags, Chris R PR3987 for signed recipes,
Dugongue PR3945 for native words, and all source-native/compiler lineage retained
in source/PROOF.md. New uniform routing proof and controls are this contribution.
