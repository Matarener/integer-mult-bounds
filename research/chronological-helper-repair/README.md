# Chronological helper spill has an exact repair rank

This scoped written proof determines how multiple individually normalized
helper replacements interfere. The contribution was produced by Nick Petalas.
It does not change kappa or the selected frontier.

For a scalar identity helper word, transport the row and column at ordered
cut i to the input boundary as c_i,d_i, with c_i d_i=1. Assume the k rows
form an invertible helper basis C, and put the columns in D. Write
CD=I+L+U, with strictly lower L and strictly upper U. For arbitrary old
inputs h, independent replacement inputs z, early outputs t and final
helpers f, the complete map is

```text
(I+L)t = Ch + Lz,
Cf     = (I+U)z - Ut.
```

The early outputs have new-input leakage rank exactly rank(L). Final
helpers have old-input leakage rank exactly rank(U). Both banks are
independent under the prescribed old/new input partition without repair
exactly when CD=I. Separate invertible basis changes within either bank
cannot remove these leakage ranks.

When L=0, exactly rank(U) cross-bank rank units suffice and are necessary
to repair the final helpers. This allows arbitrary finite restored clean
or dirty workspace and grants free invertible operations within either
bank. It is an optimistic linear communication tariff, not a physical
Gaussian rank tariff. For every k>=2 an explicit family has k individually
valid cuts, already independent early outputs, and repair cost k-1.

[PROOF.md](PROOF.md) contains the all-field derivation, workspace-robust
lower bound and attaining decoder. Classical elimination and rank-cut
methods are credited as methods. The new contribution is this precise
chronological helper-replacement application. No general literature
priority is claimed.

## Reproduce

From the repository root, using standard-library CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/chronological-helper-repair/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/chronological-helper-repair/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/chronological-helper-repair
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/chronological-helper-repair --check-source-history --check-modes
```

Another CPython 3.12 executable can replace the absolute interpreter path.
The direct commands print `PASS_CHRONOLOGICAL_HELPER_REPAIR` and a generated
SHA256 receipt covering all six package files. The registered replay also
prints `PASS_REGISTERED_RESEARCH_PACKAGE`.

The verifier replays changing original prefixes and literal cut events
on every input coefficient. It compares this direct endpoint with the
closed form, checks both leakage ranks and full reversibility, and emits
minimal rank-factor repairs when L=0. Its finite domains are:

- All 10,752 pairs of an invertible binary 3-by-3 C and a unit-diagonal
  binary 3-by-3 K, and all 729 ternary unit-diagonal 3-by-3 K with C=I.
- All 25 quinary unit-diagonal 2-by-2 K with C=I, and 72 rational fixtures
  through k=6, including nontrivial dyadic C and nonzero L and U.
- Twenty-five sharp-family cases over Q, F2, F3, F5 and F7 through k=6.
  An independent enumeration rejects all 64 binary outer products as
  one-unit repairs of a rank-two defect.
- Eight invalid-domain fixtures and four semantic controls, including
  reversed chronological pairing and the biorthogonal positive control.

The three finite-field domains contain 1,376 cases with L=0. The
rational domain contains 43. Every such case checks the attaining repair;
the sharp-family checks are additional fixtures and can overlap those
domains. Counts are enumerated by the verifier, not extrapolated.

## Scope and predecessor credit

The target was an original causal-composition question under the current
`coverage-law-change` card, not a follow-up question taken from another
package. It changes the single-cut premise to multiple prescribed cuts.
The task and exact provenance are in [TASK.json](TASK.json) and
[SOURCES.json](SOURCES.json), based on canonical main
`19fdb086ea96af9a9f87936a2b888e10af4ed810`, priority revision 8.

Ali Romman's [#5599](https://github.com/CrocSwap/integer-mult-bounds/pull/5599)
supplies the independent-input replacement contract and the retained
Pierre-Loic Doulcet, Cinna Davis, Jacob Alan Sussman and P104 lineage.
His [#5615](https://github.com/CrocSwap/integer-mult-bounds/pull/5615)
supplies the dyadic single-cut pairing context. They are cited premises,
not audit or scientific-replay deliverables of this package. Historical
multi-cut response-kernel work concerns a different replacement operation.

The result is a written proof with exact finite corroboration. It is not
a finite search failure, native certificate, complete multiplier theorem
or independently accepted formal proof. Physical cut eligibility, common
charts, availability of retained early outputs, scalar bases, coefficient
restrictions, native alignment, ownership, precision, stock, complete
signed moment, compiler and outer funding remain payable. All five
selected framework assumptions remain. No selected supplier cold replay,
Lean or Docker run is performed.

Independent human and formal proof-kernel review are unclaimed.
Apache-2.0.

## Open next questions

1. Does one changed P104 word contain a full or separately justified
   partial family of eligible cuts with zero lower pairing and nonzero
   upper pairing? Extract exact transported rows and columns from a named
   word. The blocker is physical eligibility and chart compatibility,
   not the scalar formula.
2. Can a real consumer deliver the necessary early-output reads within
   a favorable complete signed moment? Start with a rank factorization
   of that actual U and charge every read, basis operation and restore.
   The tariff here grants free operations that a physical caller must pay.

## Verification design

The kept code has no recursion, dynamic code execution or external
scientific dependency. Functions are at most 33 lines. Matrices have at
most 12 rows and columns; input helper dimension is at most six. Scientific
domains and all loop counts are fixed by the enumerations above. Runtime
checks remain enabled under `-O` and enforce dimensions, unit diagonal,
invertibility, coefficient bounds and exact residuals. Warnings are errors
in both registered commands. The only filesystem reads in the scientific
replay generate the six-file receipt, each bounded to one MiB.

Power-of-Ten rule 3 has a managed-runtime deviation in `verify.py`. Python
integers, lists and Fractions allocate during arithmetic. The scope is the
fixed finite replay only. The compensating controls are bounded dimensions,
fixed coefficient grids, streamed cases, no retained case history and the
receipt size limit. Normal and optimized replays check the same domains.
An embedded implementation would need fixed-capacity integer storage and
a separate bit-capacity analysis; this verifier is not such an implementation.
