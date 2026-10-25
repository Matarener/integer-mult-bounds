# Pooled R437 replica-indexed native request interface

This package fills the next source boundary exposed by PR3995: all actual pooled
requests now include the caller replica, actual owner charts and absolute IDLE
families. The new topology has an explicit replica-indexed IDLE API. It does not
execute a physical CALL/RETURN or admit the pooled supplier.

The complete source audit checks:

- 903,456 paid request sites: 836,928 MOVE, 2,592 COPY and 63,936 IDLE; exact
  pooled rank profile and rank mass 1,808,352.
- Every request key and actual caller identifier, plus exactly-once IDLE coverage.
- All 1,235 actual charts, with dyadic entries and determinant ±1, and all 179,802
  same-family owner pairs in all 288 calls, each with a dyadic-unit separation
  witness. This certifies owner separation for every odd prime without assuming
  replica symmetry.
- Actual retained q=3 source compilation for the first relocated MOVE in both
  native/common forms, the unique rank-14 IDLE, and a COPY. The committed result
  reports good/fallback classification; compilation is not fallback execution.
- Exactly five additional source-code bits at every fixed q: q=3 grows from
  6,507 to 6,512. Program histories and raw fields must pay for that expansion.
- Wrong replica, legacy IDLE lookup, stale or cross-prime source-code context,
  mismatched Specifications, untyped source, duplicate chart, replica-scaled
  profile and invalid native COPY are rejected.

The ordered request digest is
`29ad864c2a6a31ad15162b0165b4f047cf580d9f2c147aebcfccfd564ccbbc60`.
The first moved helper's MOVE is request 563291; the same literal position in
replica 0 is request 560376. Both use family 209, with distinct charts. This is
why absolute family alone cannot identify the caller's request.

Run the registered, standard-library replay:

```
python3 -B scripts/research_package.py --package research/r437-pooled-native-interface
```

No Git, network or predecessor worktree is used by verification. `SOURCES.json`
authenticates retained bytes and the canonical source closure. Pending source
files are retained locally; source-provenance metadata identifies their original
commits. The inherited full compiler file is retained unchanged, but only its
source overlay/slot validator is executed here, not its unused emitter helpers.
The new catalogue intentionally requires an IDLE consumer change; it is not a
silent replacement accepted by the old physical compiler.

`PROOF.md` states the complete changed contract and uniform algebra, exact
transport multiplicities, code-width invoice and remaining unknowns. Physical
routing, complete residual/source access, prior dirty-state observation, native
preparation, CALL/RETURN, all consumers, source acceptance, chronological history,
parking and global visited-cell/resource coupling remain obligations. There is
no shortened-volume execution passed off as a production result, no new kappa,
and no frontier change.

Credit Rohan Arun's PR3959/3958/3939 for pooling and its conditional endpoint;
ai-nanachi's PR3647, Ali Romman's PR1043 and Sagar Thakrar's PR3700/2423 for the
R437 word/hosting lineage; PR3995 for absolute-owner emission and the catalogue
counterexample; PR3980 for the dyadic owner checker; PR3983 for complete
chronological parking accounting; Nick Petalas's PR2989 for earlier owner
separation/compiler correspondence. The prior PR3959 local follow-up already
established the first helper's permutation transport and common plan identity.
Canonical physical/source/compiler credit includes zxv, David Arias, Jose Manuel
(jmbarrancoml), ywz65, alephnan, Adam Gall, Ross Richardson and the retained
notices, together with mightyOil, DaysSky, chafreaky, DreamingOfClouds and eumemic.

New interface, audit and writing: Chris R / Clear1nsight with substantial OpenAI
Codex assistance. Same-session AI cross-review is distinct from human or formal
kernel acceptance. Apache-2.0; inherited notices and byte-exact retained sources
are preserved.

## Open next questions

1. Adapt the full physical compiler's IDLE enumeration and bind the first actual
   pooled gather/native source/return with its preceding dirty read and every
   consumer. Source compilation and owner separation are ready premises;
   physical primitive and complete source acceptance are still required.
2. Substitute the widened source-code field into the actual chronological
   history, raw fields, checkpoint codec, scans and returns. Count all occurrences
   and whole-run reserve before claiming a complete numerical physical bill.
3. Join the actual pooled caller to an admitted child supplier and all-size,
   stock, precision and analytic bounds. A successful finite replay alone does
   not discharge these remaining supplier obligations.
