# Sharp P104 prefix norms and completed-operation error bounds

The full PR5802 word has exact maximum field amplification **2^17**, attained
at cut24502 in field93. Under unitary native charts, the bound applies to
physical Hilbert norms at every admitted column multiplicity. The source uses
a coarse product bound; this certificate supplies the actual word's norm.

For errors in completed MOVE, ADD and SCALE operations, the exact signed
transfer gives `E <= 56663088*u*B/(1-2428962*u)`. A uniform26-bit guard controls
all prefixes; a23-bit guard suffices for final public outputs. If only native
MOVE operations have error, the corresponding guards are25 and19. The exact
absolute-defect gains are also sharp, with attaining executions.

This gives a concrete precision requirement for a rounded implementation.
It does not implement the child or supply a new kappa. Exact COPY, INIT and
CLEAR remain premises. **29 of30 CLEARs erase nonzero ideal data**; the old
known-zero recovery result cannot be reused for them.

See [PROOF.md](PROOF.md), [RESULT.json](RESULT.json), [ORIGINS.json](ORIGINS.json)
and [VALIDATION.md](VALIDATION.md). The checker uses Python3.12 and its standard
library. It imports no predecessor executable. Default verification writes
nothing and requires neither Git nor network.

```sh
python3.12 -I -B research/p104-sharp-norm-error/verify.py
python3.12 -B scripts/research_package.py --package research/p104-sharp-norm-error
```

Source: PR5802 at9bab1ca917ec4d1a4e60f4eb8c81d7ef92908a62. Base: canonical main
de5ec2e7a6074068452f45b1a191b5c72832df4a, priority8. This source-bound informal
precision lemma replaces the formal-interface card; no Lean theorem is claimed.
The five framework assumptions remain. The selected frontier is unchanged.

Prepared by Ali Romman with substantial OpenAI Codex assistance; no subagents.
Apache-2.0. Credit PR5802 and its complete retained native/compiler/construction
lineage, Adam Gall, ywz65, PR2878, Nick Petalas, Ross Richardson, flyingviper
and Arham Tahir. Retained notices specify predecessor authorship.

## Open next questions

1. Implement a rounded native child whose complete output error satisfies this
   relative Hilbert contract. Include internal wrappers and cancellation inputs.
2. Give a charged physical representation and tape/rounding invoice. Convert
   Hilbert error to component recovery only with an exact output-grid premise.
3. Replace or implement the29 nonzero owned resets. The old zero-recovery proof
   does not establish this obligation.
4. Apply the checker to a changed word only after a fresh exact source pin and
   endpoint replay. These constants do not automatically transfer to PR5806.
