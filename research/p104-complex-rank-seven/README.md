# Complex rank-seven P104 approximation below 1/4

**Exact finite construction and field separation; no new kappa.**

Complex coefficients can beat the sharp real rank-seven error floor for the
fixed P104 Gram matrix. This answers the released complex-field question in
[PR6191](https://github.com/CrocSwap/integer-mult-bounds/pull/6191), at
`be3fc854aa380b3d81e134ce9a4282468e4fa999`. It does not contradict that
PR's theorem, whose coefficient field is real.

Let R contain the 104 retained roots, each of squared norm two, and let
`K=RR^T/2`. The explicit vector

```text
z = (5-5i, 3+9i, 5-5i, 7, 5-5i, -1-4i, -7, -7)
```

has `z* z=404`. The filter `D=I-zz*/404` is a Hermitian orthogonal
projector of complex rank seven, hence `0<=D<=I`. Its approximation
`C=RDR^T/2` has complex rank seven and exact maximum complex entry error
**25/101 < 1/4**, a gap of **1/404**. A second retained witness gives the
stronger bound **1205/4912 < 1/4**, with gap **23/4912**. Neither value is
claimed optimal. [PROOF.md](PROOF.md) contains both vectors and the proof.

The distinction matters: C is Hermitian positive semidefinite with
`0<=C<=K`; the contraction claim applies to D, not to C relative to the
104-dimensional identity. Both candidates have trace 91. Their real parts
have real rank eight, so these are not seven-real-mode implementations.
Their coefficients contain odd denominators and are not Gaussian-dyadic.

## Evidence and reproduction

`verify.py` authenticates the three pinned predecessor inputs, reconstructs
all 104 roots, checks an orthogonal eight-root basis, and certifies both
projectors and every entry of both full Gram approximations: **21,632
entries**. It checks real-part rank eight both by exact elimination and
by the real/imaginary Gram determinant. Nine controls cover all sixteen
real omitted-root quarter-error witnesses, a retained-root unit error,
dropping imaginary coordinates, missing conjugation, projector and Gram
normalizations, wrong parity, duplicate lines and a missing line.

`independent.py` was written separately, without reading or importing the
primary checker. It reconstructs the roots in a different order, uses
Gaussian pairs of `Fraction` values instead of a common integer denominator,
checks every residual entry, and independently certifies complex rank seven
and real-part rank eight through the orthogonal-root minor. Four additional
projector controls reject wrong normalization and missing conjugation.

Run from the repository root with Python 3.12 and its standard library:

```sh
python3.12 -B scripts/research_package.py --package research/p104-complex-rank-seven --check-only
python3.12 -B scripts/research_package.py --package research/p104-complex-rank-seven
```

The registered commands run each checker normally and with `-O`, with
isolated imports and warnings treated as errors. Expected markers are
`PASS_P104_COMPLEX_RANK_SEVEN` and `PASS_INDEPENDENT_COMPLEX_RANK_SEVEN`.
For the official Git-free source export, run these direct commands from its
root, once normally and once with `-O` added:

```sh
python3.12 -I -B -W error research/p104-complex-rank-seven/verify.py
python3.12 -I -B -W error research/p104-complex-rank-seven/independent.py
```

The export must include the three external inputs declared in
[VERIFY.json](VERIFY.json). [SOURCES.json](SOURCES.json) pins their base
commit, Git blobs and SHA256 digests. The original card and selected record
are historical provenance; the three PR6183 files are live inputs. The
primary verifier checks all three live hashes before arithmetic. The
independent checker separately pins the root-data hash. Both write no files
and preserve every mathematical check under optimized Python.

## Sources, scope and coordination

Canonical main was refreshed first at
`a5bff3bf133e482541c09eba4e773884bdb2b1b7`, priority revision 8. The selected
record identifies conditional `kappa=781451/250000000` and five remaining
framework assumptions; neither changes here. Binding-only orientation was
reused after confirming all 1227 bound inputs unchanged since checkpoint
`3f0152a32eeebac0df11946dbd50cabe5a7f7839`. No selected scientific cold replay
was run.

The original `coverage-law-change` card is retained in [TASK.json](TASK.json),
with scope explicitly changed to this algebraic field-extension question.
This identifies a limitation of a real approximation obstruction, but does
not meet the original completed-call and full-invoice acceptance gate.
The [canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19275237)
records the two previously unpublished local candidates and stops after
their exact certification. No additional numerical search was run.

The local overlap helper searched 30 of 8623 notes (8593 absent in the
sparse checkout), without a usable remote cache. Live checks covered the
newest 20 PRs, newest 15 handoff comments, and all-state searches for
P104/complex/rank, 6191 and Gram/contractive. Nearest results are PR6191's
real theorem and Nick Petalas's [PR6183](https://github.com/CrocSwap/integer-mult-bounds/pull/6183)
contractive theorem. PR6194 concerns a different paid frame-graph objective.
No competing complex witness appeared in the checked results; this is not
an exhaustive novelty audit.

PR6183 at `eaf77790466f34b86ce72080e3ec690e26dfacab` supplies the retained
root data, contractive question and Gram convention. Matarener's PR6166
at `096938513138868f0ed27639061f1a5054900f96` supplies the cited P104-to-D8
identification and omitted lines. Those physical coordinates are a cited
premise, not independently audited here. Their archival retention does not
constitute scientific acceptance. PR6191 remains a pending comparison
source; its real lower-bound argument is restated with credit in PROOF.md,
and no replay requires its pending Git objects or executable code.

The proof establishes two finite counterexamples to extending the real
quarter-error floor over Q(i). It does not give the optimum complex error,
an asymptotically vanishing residual, native implementation, side correction,
source/consumer installation, ownership/dirty restoration, full paid/target
invoice or multiplication theorem. Independent human and formal proof-kernel
review are unclaimed. No Lean, Docker or physical/native replay was run.

## Open next questions

- **Can a Gaussian-dyadic rank-seven filter also beat 1/4?** The odd
  denominators leave a coefficient-field gap before native implementation.
  A bounded first step is one exact dyadic Hermitian projector on these same
  104 roots, checking its complete coefficient error. No such projector or
  native circuit is supplied here; any wider search needs a justified scope.
- **Can an actual caller use and correct this residual profitably?** A lower
  coefficient error alone earns no independent target credit. Start with
  one source-bound scalar word, track this exact rank-one residual through
  every retained output, and price restoration and correction. The absent
  caller and complete bill are blockers; no additional parameter search is
  justified as a bound improvement before that gate.

Structured questions, relevance, first steps and blockers are in TASK.json.

## Credit

Prepared by **apoursh**, with substantial OpenAI Codex assistance in witness
discovery, separately written exact verification, mathematical audit, proof
and packaging. Nick Petalas retains PR6183's contractive question and real
attaining projection; Matarener retains PR6166's D8 identification and omitted
lines. Rohan Arun, Chafik Boukhalfa, Ali Romman, DreamingOfClouds, Cinna Davis,
Pierre-Loic Doulcet, icekylinx, zxv, Jacob Alan Sussman and the retained
P104/root/frame/native/helper/compiler/BIT lineage retain their source credit.
Hermitian projection and Gram-rank facts are classical; no general literature
priority is claimed. New material is Apache-2.0; predecessor files are unchanged.
