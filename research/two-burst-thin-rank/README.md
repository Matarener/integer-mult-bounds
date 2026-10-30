# Eight thin queries are necessary in the saved two-burst schedule

**Finite certificate over F2; no new kappa.** Fix the six full matrices from
Ali Romman's PR #5673, in order `(1,3,2,4,0,5)`, and permit constant thin
queries only after two and four full calls. Every complete word requires at
least eight rank-one thin queries. The eight square-zero queries in
[theon199's PR #5699](https://github.com/CrocSwap/integer-mult-bounds/pull/5699)
attain this minimum.

The new result is the lower bound for that fixed schedule. PR #5699 proved
that two occupied gaps are optimal and explicitly left the thin-query count
open. This answers its first next question on its saved gap pair, not on every
two-gap schedule. Coefficient changes at these gaps cannot produce seven queries.

## Evidence and scope

Consecutive thin queries aggregate to two arbitrary binary matrices Z1,Z2.
The complete polynomial endpoint gives 1,728 binary equations on their 128
entries. Exact elimination has rank 104 and leaves 24 free coordinates. The
verifier enumerates all **16,777,216** solutions and finds

`min(rank(Z1) + rank(Z2)) = 8`.

Subadditivity of matrix rank makes this a lower bound on the number of
rank-one factors, even without imposing square zero. The cited construction
attains it with legal square-zero factors. [PROOF.md](PROOF.md) explains the
reduction, completeness and finite claim. No predecessor verifier is imported.

The computation includes every coefficient of every matrix entry, not only
constant or first mixed coefficients. It checks the attaining source data,
512 independent kernel/rank cases, and nine boundary, rejection or enumeration
controls. Stdout is a generated receipt with the affine basis, complete rank-pair
histogram, and SHA256 hashes of package files and live inputs. It writes nothing.

This is neither a search failure nor a complete multiplication theorem.
Extension fields, changed full matrices, other full-call orders, other gaps,
additional gaps, stage-dependent thin entries, native lifts and physical
implementation are outside the certificate. No current supplier, complete
invoice, selected frontier or framework assumption changes. The predecessor's
optimistic invoice remains a separate cited limitation; it is not replayed here.

## Reproduce

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/two-burst-thin-rank/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/two-burst-thin-rank/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/two-burst-thin-rank
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/two-burst-thin-rank --check-source-history
```

Use the corresponding CPython 3.12 path on another machine. Both registered
commands enumerate the entire domain. Expected status is
`PASS_TWO_BURST_THIN_RANK`, with 16,777,216 solutions and minimum rank sum eight.
The registered runner also checks metadata and pins. Publication-byte and
source-history checks require a committed package and full Git history.
The standalone verifier also works in a source export without Git or network.

## Open next questions

- Can different gaps, another full-call order or more occupied gaps admit seven
  binary queries? Start from the changed full coefficient system. A positive
  word needs every coefficient, not a sampled endpoint. No broader search is
  included, and a favorable complete invoice must precede supplier expansion.
- Does the rank-sum bound persist over characteristic-two extension fields?
  The same affine equations define a symbolic problem, but the enumeration here
  assigns binary values only. A field-uniform rank argument remains open.

## Credit and provenance

This result was produced by Nick Petalas. New work is Apache-2.0. Independent
human and formal proof-kernel review are unclaimed.

Credit GitHub contributor **theon199** for PR #5699's two-burst construction,
saved witness and explicit question. Credit **Ali Romman** for
[PR #5673](https://github.com/CrocSwap/integer-mult-bounds/pull/5673), its full
matrices, normalized escape-word model and original construction. Retain
**Cinna Davis** and the PR #5617/#5631/#5649 controller lineage, P104/native/helper/
compiler contributors and every unchanged predecessor notice. Classical binary
elimination, rank subadditivity and Gray enumeration are not claimed as new.

[SOURCES.json](SOURCES.json) pins the exact retained main inputs at
`de5ec2e7a6074068452f45b1a191b5c72832df4a`. The catalogue and selected record
are historical provenance. The three explicit predecessor files are live
inputs; the verifier checks their hashes without importing predecessor code.
[TASK.json](TASK.json) records the changed card scope and overlap coverage.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19216167)
and [finite-field clarification](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19216231)
record the bounded assignment and result.
