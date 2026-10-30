# Exact five-bit coordinate-parity recovery

**Scoped proof with a finite exhaustive certificate; no new kappa.** For
the fixed 112-owner rounded inverse in zxv's
[PR5444](https://github.com/CrocSwap/integer-mult-bounds/pull/5444), after
four uniform relative precision bits, exactly five fixed original-input
coordinate parities suffice to recover every integer input. Every choice
of four coordinates fails. One attaining zero-based set is

    {0, 9, 27, 76, 79}.

The explicit map is

    F(x) = 16 x - M round_away(16 M^T x / 52),   x in Z^112.

Each tag is x_i modulo two, retained before overwriting x. The decoder sees
only F(x), those five bits, and the fixed matrix. This is a new restricted
recovery interface answering part of PR5444's recovery question. Its
unrestricted four-bit recovery tag remains better in bit count. The new
result determines the exact one-bit penalty for using individual source
parities instead of an arbitrary tag function.

[PROOF.md](PROOF.md) reduces every collision to an explicitly attainable
direction v in {-1,0,1}^8 with Mv even. There are 480 such nonzero directions
and 128 distinct parity signatures. The five selected coordinates cover
all signatures. All 6,210,820 four-coordinate sets leave at least four
signatures uncovered. These signatures range over all outputs, rather
than belonging to one fiber. [parity.py](parity.py) supplies a decoder with
at most 256 candidate quotient tuples.

## Reproduce

From the repository root, with standard-library CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/rounded-inverse-parity-tags/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/rounded-inverse-parity-tags/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/rounded-inverse-parity-tags
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/rounded-inverse-parity-tags --check-source-history
```

Another CPython 3.12 executable can replace the local path. Expected markers
are `PASS_ROUNDED_INVERSE_PARITY_TAGS`, `PASS_REGISTERED_RESEARCH_PACKAGE`
and `PASS_RESEARCH_COMMIT_BYTES`.

The verifier generates a JSON receipt on stdout, binding all eight package
files by SHA256. It checks the complete four-set lower bound, every signed
direction's explicit collision with a separate rational interpreter, 131
decoder round trips including every coordinate basis input and two
4,096-bit fixtures, five omission controls and seven invalid-input classes.
It uses no predecessor executable and writes no checkout files. The
receipt is generated, not supplied as handwritten evidence.

For direct codec use from Python, load the package directory on the module
path, then call `matrix()`, `right_inverse(rows)`, `encode(rows, x)` and
`decode(rows, basis, output, tags)`. The matrix and basis are trusted fixed
configuration. Input values and packets pass explicit length, integer,
bit-width, congruence and final-map checks. The operational input limit is
4,096 bits per integer; the written injectivity theorem has no magnitude
limit. This is an exact integer codec, not a reversible physical circuit.

## Limits and verification status

The contribution is the collision reduction, sparse coordinate-tag optimum
and decoder. The source Gram identity, native matrix, uniform precision
frontier and unrestricted tag optimum are cited predecessor premises. No
predecessor scientific suite is replayed or audited. The final lower bound
is finite exhaustive computation, joined to a written all-input reduction.
Independent human and formal proof-kernel review are unclaimed.

There is no new supplier, paid-call reduction, current P104 word, rounding
budget, complete caller, physical tag-acquisition/erasure tariff, tape
compiler, selected cold replay or outer theorem. All five selected
framework assumptions remain. No Lean or Docker run is supplied. No
kappa gain follows.

The verifier uses bounded Python allocations. The collision domain has at
most 6,560 nonzero candidates of eight entries and 112-entry images;
the fixed matrix leaves 480. The lower-bound loop visits exactly
binomial(112,4) sets while retaining only a bounded histogram. Decoder work
has at most 256 candidates, each with 112 bounded integers. These are the
managed-runtime deviations from preallocated steady-state memory in
Power of Ten. All functions are below sixty lines; no recursion, dynamic
code generation, subprocess or callback dispatch is used. Exceptions keep
invariants active under optimization. Warning-strict execution and
in-memory syntax/AST inspection supply the interpreted-code diagnostics.
Follow-up for a physical implementation is a fixed-capacity bit/tape
layout and charged reversible arithmetic, rather than assuming Python's
allocation and arithmetic are free.

## Open next questions

Can these five source parities be retained and erased more cheaply than
the predecessor's four-bit rank tag? Start with the five explicit owners
and one actual inverse call, then price every source read, scratch cell,
decoder operation and eventual erasure. Physical access and the caller's
restoration contract are blockers; no execution advantage follows from
the bit count alone.

Can a permitted fixed change of input coordinates make four individual
parities sufficient? Start by declaring its complete forward/inverse
cost and applying the finite collision-signature criterion in that
coordinate system. An arbitrary recoding cannot be assumed free.

## Credit and provenance

This contribution was produced by Nick Petalas. Credit zxv's PR5444 for
the rounded-map precision/recovery interface and explicit open questions;
Ali Romman's PR5323 for the underlying recovery-state theorem;
JoyboyBrian's PR5035 for the finite kernel; Dillon Amburgey's PR4933 and
David Ganz's PR4929 for the native matrix/geometry; and their retained
native, controller, precision, compiler and recovery lineage. Integer
rounding, congruence and finite set cover are standard background. No
general priority claim is made for those methods.

MATRIX.json is an exact copy of PR5444's FIXTURE.json. Its original source
notices are retained in the unchanged predecessor package. No predecessor
credit line is edited. Apache-2.0.

Scientific base: canonical main `3f0152a32eeebac0df11946dbd50cabe5a7f7839`,
priority revision 8. The source package's last changing commit is
`9004eb1b185803ba2f3101b8955e6e8d0dc12ed4`. [SOURCES.json](SOURCES.json)
pins all source bytes and the original card. The current selected record
is conditional kappa 0.003125804 and is unchanged. The scope change from
the uniform-transfer card to this recovery side result is explicit in
[TASK.json](TASK.json).

The [advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19267749)
names the delivered question. Live main, merged/open PRs, recent account
contributions and coordination claims were checked before research.
The overlap helper reported complete remote pagination and sparse local
notes; targeted searches read canonical-main README matches directly.
These checks do not cover unpublished work or every diff and do not
establish novelty by themselves.
