# Verification record

Scientific base: `12fa8c5c844be21bfefb38a19503fbd867a11244`, canonical main,
priority revision 7. Fetched at session start and again before publication;
the later checkpoint still returned the same commit. Assignment seed 27 was
drawn with operating-system randomness at 2026-10-21 14:48:38 UTC. The local
claim was recorded at 14:55:40 UTC, within the 24-minute orientation limit.

Environment actually used: CPython **3.12.14**, Linux, standard library only.
No solver, native compiler, third-party numerical library or proof assistant
is a runtime dependency. Both implementations were produced in the same
OpenAI Codex session; there was no independent human or sub-agent review.

## Scientific checks executed

The registered command passed:

```sh
python3.12 -I -B scripts/research_package.py --package research/two-plane-copy-floor
```

It ran the primary exact checker normally and with `-O`, then the independent
checker. Expected final status:
`PASS_REGISTERED_RESEARCH_PACKAGE research/two-plane-copy-floor outcome=negative-result`.
The separate independent command also passed with `-I -O -W error -B`.

The primary replay checked:

- Exact SHA256 of the selected archive, the extracted data-phase member and
  the matching certificate; all 112 labels, all 56 self Gram matrices and the
  port partition.
- Every one of the 1,540 unordered plane pairs and all nine atom tariffs per
  pair, for **13,860** inequalities. The complete tariff table has a bound
  digest in RESULT.json; all five `(cross rank, joint rank)` classes are kept.
- Every binary cross matrix with block dimensions 1 through 3, **682** cases.
  This checks finite premises and examples, not the general proof by census.
- All entries of four explicit scalar factorization fixtures in each geometry
  class: the identity basis, a cofactor-cancelling integer basis outside the
  signed-ternary alphabet, an overcomplete six-term identity, and a complex
  phase fixture using ordinary transpose.
- The exact integer budget `65,632/65,408 = 293/292`, and the equal-mass
  concave-cost boundary fixture. The latter's squared half-power bills are
  16 versus 32, so the COPY-mass theorem cannot be misread as a power theorem.

Seven primary rejection controls passed: duplicate matching port, invalid
label, understated joint-copy rank, free cross-copy mischarge, omitted
off-diagonal compensation, substitution of the rank-two masked broadcast for
the identity, and substitution of Hermitian for ordinary transpose.

The independent implementation imports no primary or predecessor code. It
uses explicit binary vectors and image-set cardinality for geometry, then
nonnegative shortest paths on four-by-four binary matrices. The full state
space is 65,536 matrices, with 225 rank-one moves. It stops when the identity
is settled, proving the minimum in this finite coefficient field for all
finite word lengths. The exact stopping counts were:

| Cross rank, joint rank | Minimum | Settled states |
| --- | ---: | ---: |
| 0,4 | 8 | 59,401 |
| 1,3 | 8 | 62,569 |
| 1,4 | 8 | 59,401 |
| 2,2 | 8 | 55,081 |
| 2,4 | 8 | 49,897 |

Reducing one actual self-copy price from two to one changes the independently
computed optimum to **6**. Exact Gaussian elimination separately reconstructs
the cofactor-cancellation inverse, and literal matrix multiplication checks
the six-term identity and rank-two masked endpoint. None of these finite
checks replaces the all-field proof in PROOF.md.

## Portability and deliberate corruption

A Git-free relocation containing both programs, the receipt and the two
declared inputs passed both programs from an unrelated working directory
under `-I -O -W error -B`. Files were marked read-only and SHA256 inventories
before and after agreed. This checks unchanged scientific working bytes;
the committed package is additionally checked by the publication commands
below. File permissions alone are not treated as an immutability proof.

Disposable copies rejected each of five external corruptions in both normal
and optimized modes (**10 rejecting runs**): lowering the receipt floor to
seven, dropping a geometry case, halving the claimed payload count, changing
a source matching port, and flipping a byte of the frozen source archive.
The first three fail the recomputed receipt comparison; the latter two fail
source authentication before mathematical work. Original inputs were not
modified. These external harness results are local test evidence; they are
not an additional all-input theorem.

The task card's historical positive control,
`python3 -B research/complex-local-word-ceiling/verify.py`, passed after its
omitted sparse-checkout dependencies were materialized unchanged. It reports
the selected-word ceiling `a < 0.001690054109089`. Initial missing-file errors
were checkout preparation failures, not mathematical rejections. The result
here uses the explicitly changed plane-port model, not that ceiling outside
its hypotheses.

## Publication checks and limits

The package uses the repository's metadata/source-pin checker, staged diff
check, committed-byte/source-history gate and committed export/check tools.
Their commands, for reproduction, are:

```sh
python3.12 -B scripts/research_package.py --package research/two-plane-copy-floor --check-only
git diff --check
python3.12 -B scripts/check_research_commit.py --package research/two-plane-copy-floor --check-source-history
python3.12 -B scripts/export_research_package.py export --package research/two-plane-copy-floor --ref HEAD --output /tmp/two-plane-copy-floor.tar
python3.12 -B scripts/export_research_package.py check /tmp/two-plane-copy-floor.tar
```

The handoff records the published commit and checks the complete remote Git
tree against the tested contribution. Publication/integrity checks do not
constitute maintainer mathematical acceptance. No selected cold replay,
physical supplier execution, full multiplication theorem, Lean proof, Docker
run or hosted-CI success is claimed. Frozen predecessors and `upstream/`
remain unchanged. **No new κ.**
