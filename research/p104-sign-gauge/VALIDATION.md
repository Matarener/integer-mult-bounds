# Local verification record

Linux x86_64, CPython 3.12.14, standard library only. Base:
`df0137efd35e11b4445734bf612bdd4c7ebc330c`; OS assignment seed 34.
Work resumed after an environment interruption with the same seed and inputs.
Canonical main and selected kappa were rechecked unchanged.

## Scientific checks

- Registered normal and optimized replays pass against the same exact receipt;
  no proof check depends on a Python `assert`.
- Sparse rational replay covers all 25475 source cuts, 905501 nonzero row
  coefficients and final corrections. All per-role scalar prefix-l1 maxima
  agree, with largest value 131072.
- Dense integer/dyadic reverse replay checks all 571536 endpoint coefficients.
  Its transpose method follows the predecessor and is credited accordingly.
- Every ordered MOVE, INIT/COPY/CLEAR, boundary and independent input is
  unchanged. Complete chart, owned-state and scalar tariff checks pass.
- Six semantic rejection controls pass: missing final sign, wrong ADD sign,
  reversed MOVE, changed native itinerary, lost owned COPY sign and moving a
  whole-role sign inside a tensor factor. Owned reuse is a positive fixture.
- The source's unchanged `local.py` checker was separately run on both words.
  It agrees on allowances 220232 and 219258, 3447 paid calls, rank mass 6014,
  748 public inputs and 540 helpers. This is reused source verification,
  distinct from the new prefix evidence; it is not imported by `verify.py`.

Reproduce scientific and integrity checks with:

```sh
python3 -B scripts/research_package.py --package research/p104-sign-gauge
```

Expected: `PASS_P104_SIGN_GAUGE`, `PASS_P104_SIGN_INTEGRITY`, then
`PASS_REGISTERED_RESEARCH_PACKAGE`.

## Integrity and portability

`test_integrity.py` runs the actual verifier in temporary copies. A Git-free,
read-only optimized replay succeeds with empty PATH and unchanged file hashes.
Consumed-source, receipt and full candidate-word corruptions fail at their
intended gates. Lossless gzip repacking succeeds: mathematical equality uses
the complete decompressed payload. Direct scientific replay uses no network
or Git. The registered launcher separately checks source provenance.

Publication checks use `check_research_commit.py` and the official package
exporter on the final commit; exact commit and patch are in the publication
handoff. Full-history preflight is not claimed because this checkout is
shallow. Every declared source resolves at the direct parent base; no unmerged
object is needed by the shipped-byte scientific replay.

## Limits and overlap

This is an exact scalar circuit/allowance result. Native recipe, complete
caller, compiler and outer admission replays are not claimed. Exact native
transport follows unchanged requests and whole-role linear sign commutation.
Rounded arithmetic and tape implementation remain separate. No wall-clock
speedup, optimum, stronger kappa, human review or proof-kernel acceptance is
claimed. Hosted CI is separate from local verification.

The final targeted refresh inspected PR5713 at
`a5348f7143f95fe0046b92b96172e30763c7d731` and PR5718 at
`a1534ac45401c9a9c80c07aa65c89e00e33594f8`. They change recursive profiles
on newer words. This contribution counts only scalar sign propagation on the
accepted word; PR919/1153 retain method credit. Search coverage was bounded:
50 of 69 P104/sign/scalar hits and all five exact sign-propagation hits.
This is not an exhaustive novelty claim.

PR5718 reports two existing CI documentation failures at this base and points
to PR5703. Those unrelated files are unchanged here. A local package pass
does not assert hosted-CI success.
