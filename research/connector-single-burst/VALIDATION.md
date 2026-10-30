# Validation receipt

Canonical base: `df0137efd35e11b4445734bf612bdd4c7ebc330c`.
Environment: Linux, Python 3.12.14, standard library only.

Passed:

- `python3 -B research/connector-single-burst/verify.py`: all 5,040 exact
  contradictions, full original and changed polynomial words, eight rank-one
  square-zero queries, complete negative optimistic tariff, six rejecting
  controls, and the pure-stage false-positive control.
- `python3 -I -O -B research/connector-single-burst/verify.py`: identical JSON
  to the normal invocation; no assertion-dependent acceptance.
- `python3 -B research/connector-single-burst/generate.py --output /tmp/burst-regenerated.json`
  and `cmp` against CERTIFICATES.json: byte-identical generation, including
  the seed-26 burst decomposition.
- Copied the complete package without Git or bytecode caches into a temporary
  directory, made files/directories read-only, and ran optimized isolated replay
  from `/tmp`: PASS, 36.036 seconds. No network, repository-relative imports or
  external packages were needed. The scientific JSON matches RESULT.json.
- Appended one byte to the exported SOURCE-WORD.json: rejected at source
  authentication before mathematical checks. Restored original bytes before
  the read-only positive replay.
- The retained source's Git blob recomputes to
  `aae71c6ad294d6bc9ca5e2216a7785b9e6611afd`.

The generator and verifier share algebra.py; no independent implementation,
proof-assistant, human peer review or whole multiplication proof is claimed.
No repository-wide suite or selected frontier replay was run: this changes only
an isolated research package and publication handoff files. The optional
registered-package runner was not used.

Publication refresh: canonical main remained the base above. PR5673 remained
`c10f75f09e41803ae8efe478331a7509b7379b2f`; complementary PR5681 remained
`67f07448eec5ad8d84bdf96b46981ac0b893592f`. A fresh open-PR search for “burst”
returned no matches. This is a targeted overlap check, not proof of novelty.
The lower bound's predecessor corollary is explicitly credited in README.md.
The final branch/commit, patch digest, offline publication guard checks and
actual push/PR outcome are recorded separately in the external handoff, so a
publication failure cannot be confused with a failed mathematical replay.
