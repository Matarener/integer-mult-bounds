# Singular reachability and a Veronese obstruction

This contribution was produced by Nick Petalas. Apache-2.0.

Scoped algebraic proof with exact finite corroboration. For every field K
and every commutative integral domain R containing K, a determinant-zero
matrix on exactly two roles is reachable in the constant-right-vector
alphabet if and only if it has an outer-product factorization over R.
Every reachable singular target therefore needs at most three paid factors.

```text
paid factors: I+u v^T, u in R^2, v in K^2
free factors: arbitrary GL_2(K) maps anywhere
singular M:   reachable <=> M=a b over R <=> cost <= 3
```

The explicit target `[[s²,st],[st,t²]]` over `K[s²,st,t²]` has determinant
zero and fraction-field rank one, but is unreachable at every finite paid
length, over every field K. This answers Open next question 1 of #4808.
The new result is the necessary factorization invariant and its application
to that target. The sufficient three-factor constructor is cited from
Nick Petalas's #4808, not claimed as new. [PROOF.md](PROOF.md) gives the
complete argument. No new kappa or supplier admission is claimed.

## Evidence

The standard-library verifier checks the new singular-factor extraction
and its preservation through complete wrapped matrix words. Over F2 it
examines all 768 paid-factor parameter choices with nonzero constant right
vector and coefficients in the span of `1,s²,st,t²`, finding 48 singular
choices. Over F3 it examines all 52,488 such choices, finding 648 singular
choices. Different parameter choices may give the same matrix. All 696
extracted factorizations and all 696 wrapped endpoints
pass literal polynomial matrix multiplication. Each wrapped word includes
paid factors on both sides and nontrivial free maps.

Complete factor searches for the Veronese target consider 256 first-entry
pairs over F2, 6,561 over F3 and 390,625 over F5. Respectively 2, 4 and 8
pairs multiply to s², and none extends to the complete target. These are
397,442 first-entry candidate pairs across three separate domains. No
outer-product factors of higher degree are omitted: each nonzero factor
entry has total degree at most two, since total degrees add in a polynomial
domain and every target entry has degree two. The full degree-at-most-two
part of R is exactly the span of `1,s²,st,t²`.

Controls cover ten constructor words over Z,F2,F3,F5,F7, all fifteen
single-factor omissions in five nonconstant words, five determinant
mutations and five larger-ring controls. The larger ring `K[s,t]` admits
the target as `(s,t)^T(s,t)`, so allowing the missing coefficients removes
the obstruction. Another 3,123 scalar input comparisons over F2,F3,F5,F7
show that scalar specializations are outer products; these do not prove
the polynomial obstruction. Three invalid-domain/degree controls, one
accepted capacity boundary and two capacity/singular-premise rejection
controls pass. All counts are enumerated by the verifier.

The universal claim is the written proof. Exact finite checks corroborate
only the stated domains. The generated stdout receipt binds all six
package files by SHA256; no receipt is handwritten. No predecessor
scientific verifier is imported or replayed.

## Reproduce

From the repository root, with the CPython 3.12 standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/veronese-singular-obstruction/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/veronese-singular-obstruction/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/veronese-singular-obstruction
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/veronese-singular-obstruction --check-source-history
```

Another CPython 3.12 installation may replace the displayed interpreter.
Expected markers are `PASS_VERONESE_SINGULAR_OBSTRUCTION no_new_kappa`,
`PASS_REGISTERED_RESEARCH_PACKAGE` and `PASS_RESEARCH_COMMIT_BYTES`.
Each registered command has a 120-second limit. Explicit checks remain
enabled under optimized Python. The last command needs committed package
bytes and full Git history. The direct verifier also runs in a Git-free
export without predecessor files.

## Scope and provenance

Base is canonical main `de5ec2e7a6074068452f45b1a191b5c72832df4a`, priority
revision 8. The selected source-binding orientation passed and separates
complex, ordinary BIT, admitted BIT and outer budgets. It is metadata
orientation, not a selected scientific replay. Selected conditional kappa
remains `62009/20000000`.

The original `formal-interface-lemma` card is explicitly changed to this
algebraic side result in [TASK.json](TASK.json). Its relevance is target
feasibility in a declared alphabet, not a reduction of the selected five
framework assumptions. [SOURCES.json](SOURCES.json) pins the original card,
selected record and predecessor proof text as historical provenance. The
verifier reads no predecessor source as a live input.

[Advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19214451).
Live PRs, recent account PRs, handoffs, active Discussions, local reservations,
all-main README terms and distinctive merged-PR searches were checked.
The overlap cache covers 416 open PRs and 5,312 Discussion records with
complete remote pagination. Local notes are sparse and incomplete; arbitrary
historical diffs, unpublished work and global literature priority are not
covered. Merged #4808 is the explicit open-target predecessor. Merged
Ali Romman #5454 concerns factorable targets over cube-zero algebras and
does not establish this domain obstruction.

## Credit

Nick Petalas #4808 supplies the explicit question and the sufficient
three-factor constructor; #4276/#4243 supplies the two-role right-vector
and free-map context, following Wentao Li #4099 and #2513. ToikY #4334
supplies the commutative field-product result and its singular-endpoint
gap. Classical polynomial UFD, gcd and rank-one factorization facts retain
their classical status. The new direction is singular reachability implies
factorization over the coefficient domain, together with the resulting
all-field unreachable target. All predecessor files and credit are retained.

## Limits and code constraints

Exactly two roles, a commutative integral domain, base-field right vectors
and base-field free maps are essential hypotheses. No new classification of
exact cost one versus two versus three, zero-divisor rings or extra roles
is supplied. Native coefficient preparation, frames, routing, precision,
reversible restoration, stock and a complete supplier invoice remain
unknown. No complete multiplication theorem or selected-frontier change
follows. Independent human and formal proof-kernel review are unclaimed.
Lean, Docker and the selected scientific replay are outside scope and unrun.

The verifier has no recursion, subprocess, network, dynamic code or write
path. Its nineteen functions are at most 42 physical lines. Fixed fields
and degree limits bound every loop: each polynomial has at most 45 terms,
each product considers at most 2,025 term pairs, the largest factor search
considers 625² first-entry pairs, and scalar input loops have at most 7^4
iterations. Matrix dimensions are two and wrapped words have five factors.
Receipt reads are capped at 128 KiB plus one guard byte for each of six
fixed files. Warning-strict normal/optimized execution and in-memory
compilation supply the available diagnostics; no external analyzer was
installed or run.

Power of Ten rule 3 deviation: CPython and the standard library allocate
dynamically. Scope is this fixed finite verifier only. Immutable polynomial
values, explicit degree/term limits, at most 625 live search polynomials
and six bounded receipt reads limit live collections; temporary product
dictionaries have at most 2,025 keys before capacity rejection. This is not
a real-time or allocator-internals claim. The verifier checks malformed
fields/degrees and capacity at polynomial construction. Any larger domain
must revise and verify these limits before expansion.

## Open next questions

1. Can one extra restored role realize `diag(M,1)` for the obstructed target?
   Start with the same constant-right-vector alphabet and preserve the third
   input and output exactly. The two-role rank-one argument does not supply
   a three-role obstruction or construction.
2. Which reachable singular targets over a specified non-PID domain need
   one, two or three paid factors? Start with a factorable target and the
   cited constant-chart two-factor divisibility criterion. The reachability
   theorem does not determine its exact finite minimum.

TASK.json records the relevance, first step and blocker for each question.
