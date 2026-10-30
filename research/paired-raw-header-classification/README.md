# Exact optimal headers for paired raw broadcasts

This contribution was produced by Nick Petalas. Apache-2.0.

**Scoped proof with finite corroboration.** For any n independent uniform
mate pairs, a mandatory one-bit public header of price two and branch-dependent
raw source broadcasts of price one attain expected charge 2n exactly when

```text
h = one complete pair's parity XOR any Boolean function of the other bits.
```

Every other header costs at least 2n+1 in this contract. The one-unit gap is
sharp. Every optimal branch omits one complete pair and broadcasts all other
sources once. Allowing the omitted pair to depend on the header creates more
optimal protocols but no additional optimal headers.

The new all-n classification has the closed-form count

```text
N_n = sum_(k=1)^n (-1)^(k+1) binom(n,k) 2^(2^(2(n-k))).
```

For three pairs, the verifier enumerates **196,562** distinct optimal headers
and **196,704** ordered choices of the two branch payload sets. It performs
**25,178,112** literal decodes of omitted demands. Exactly 196,518 headers
have one full parity pair, 42 have two, and two have three.

Jerry Chen's merged [#912](https://github.com/CrocSwap/integer-mult-bounds/pull/912)
establishes the two-pair classification with arbitrary allowed payloads.
Here the number of pairs increases while the payload alphabet is restricted
to raw broadcasts. Its original census and predecessor geometry are cited,
not audited or replayed. General nonlinear payload optimality at n>=3 is
unclaimed. The n=5 instance uses the original ten-port Hurwitz tariffs; for
other n the theorem concerns the explicitly stated abstract matching model.

## Proof and evidence

[PROOF.md](PROOF.md) proves that a branch omitting bits from k mate pairs
contains at most a 2^-k fraction of all inputs. A balanced optimal branch
must omit both bits of one pair. Saturation forces the header to flip under
each coordinate of that pair. Inclusion-exclusion then counts the class.
The written argument applies to every n>=1. Finite checks corroborate it.

The new verifier imports and executes no predecessor implementation. It:

- Enumerates all three-pair templates in Gray order, independently computes
  their full-pair Boolean derivatives and checks the exact intersection counts.
- Decodes both omitted demands for every optimal ordered branch-payload choice
  and every six-bit input. The other four demands are directly broadcast.
- Exhausts both branches and all 64 raw subsets on 386 declared headers,
  including all 128 affine headers, 256 reproducible additional tables and
  two explicit nonlinear tables. These 49,408 subset checks find 1,879 feasible
  branch subsets. They independently compute minimum charges and check the
  fibre bound, the attaining class and the one-unit gap.
- Rejects five invalid protocols and four invalid dimension arguments. It
  checks balanced and unbalanced sharp-gap witnesses and demonstrates why
  pricing the same valid header at one would defeat the stated floor.

The finite oracle sample contains 75 optimal and 311 other headers. It is not
an enumeration of all 2^64 Boolean headers on three pairs. Exclusion of that
entire complement is the written theorem. The sorted new header/pair-mask
record has SHA256
`0cd84486e9ad2f78b21d1816832353ae35ced2c0b92bf6d3efda8b2609cdee49`.
Checks compare counts, actual derivatives and literal decodes rather than
this digest alone.

## Reproduce

From the repository root, CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/paired-raw-header-classification
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/paired-raw-header-classification/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/paired-raw-header-classification/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/paired-raw-header-classification --check-source-history
```

Substitute another CPython 3.12 executable on another machine. The direct
marker is `PASS_PAIRED_RAW_HEADER_CLASSIFICATION`. Normal runs write nothing.
An optional `--receipt /absolute/new/path.json` produces a fresh receipt bound
to every package file and the three declared predecessor documentation inputs.
The destination must be outside the checkout and must not already exist.
All mathematical checks remain active under optimized Python.

## Scope and verification design

One-bit sources, independent uniform inputs, mate-only free side information,
zero error, a mandatory public one-bit header of price two, and raw broadcasts
of price one are hypotheses. All receivers get every payload. Payload order,
length and source selection depend only on that header. Header preparation,
physical copying, decoding, source access, storage and cleanup are unpriced.
This is an optimistic abstract interface result, not a physical saving.

The code has no recursion, subprocesses, dynamic imports or external libraries.
Its enumeration fixes three pairs, at most 3*65,536 generated records, 64 inputs
and 386 oracle tables. Supporting dimension arguments are limited to 1..5;
the universal theorem is not inferred from that executable limit. All functions
fit within 60 lines. Source inputs and receipt files have explicit size bounds.
Boundary errors raise exceptions. Warning-strict normal and optimized replay
provide interpreted-code diagnostics; no separate static type checker is
required by this package.

Power-of-Ten rule 3 has a managed-runtime deviation. Python dictionaries and
integers allocate while checking. The record count and integer widths are
bounded, the oracle processes one header at a time, and file reads are limited
to one MiB each. Fixed-capacity allocation would require a different
implementation language. Registered replay checks these limits; any future
larger enumerator must revisit them before expansion.

No selected cold replay, native/all-size compiler, owned-erasure,
precision/tape or analytic-recovery proof is run or discharged. No new kappa,
supplier admission or complete multiplication theorem is claimed. Independent
human and formal proof-kernel review are unclaimed.

## Open next questions

- Can three-pair headers outside this class attain cost six with general
  nonlinear payloads under the original pairing-rank tariff? First try a
  balanced conditional choice between two pair parities and charge each
  nonlinear payload's complete source/reader span. The raw-broadcast theorem
  gives no answer for that enlarged alphabet.
- For a public header with two or more bits, characterize the headers that
  attain the matching copy floor with branch-dependent raw broadcasts. First
  analyze three pairs and four equal-size fibres. The binary-fibre saturation
  argument used here does not directly cover four branches.

## Credit and provenance

Credit Jerry Chen / CubeJerry #912 for the paid adaptive-header model, its
two-pair result and the explicit raw-bit witnesses. Alexander Templeton #785
supplies the nonlinear transcript framework, following Douglas R. Colkitt
#703 and Joel Pulikkan / GamingPuzzled #620 for the Hurwitz geometry, pairing
tariff and copy floor. DreamingOfClouds #446/#595/#717 retain their separate
format-accounting credit. Classical fibre counting and inclusion-exclusion
are used without a literature-priority claim.

[SOURCES.json](SOURCES.json) pins the unchanged #912 README, proof and notice
at canonical main `de5ec2e7a6074068452f45b1a191b5c72832df4a`. The original
notice and every predecessor credit line remain unchanged. The new step is
the all-n raw-broadcast classification, exact three-pair count, sharp gap
and full description of optimal branch payload sets. The selected record,
shared code, upstream sources and frozen evidence remain unchanged.
