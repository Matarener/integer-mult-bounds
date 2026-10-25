# A joint native odd-E8 cross-cube primitive

This package constructs a concrete native primitive for one missing `H_ab`
block of Ali Romman's [#5439](https://github.com/CrocSwap/integer-mult-bounds/pull/5439),
pinned at `e6d50e7ebd0bb1fd4f388930df78df696e56b404`. Its 64 exact dyadic
channels share four actual orthogonal eight-space interfaces. The emitted
25-dimensional program retains all 512 source inputs and all 512 arbitrary
old reader inputs, includes every local Gaussian path and absolute phase,
and returns its one zero-owned scratch to zero at its original chart.

**This is a constructive local component, with no new kappa.** It supplies
one directed cross-cube block. The whole odd-E8 side map, compatible K/H
chronology, complete caller and scientific admission remain open. The
selected conditional kappa at the publication base is `0.003027288235`.

## The exact interface

For literal source and reader labels, the entry and exit are

```
source s: Phi_[q_s] x_s  -> R25 x_s
reader r: y_r           -> Phi_(q_r^perp)(y_r + sum_s H_ab[r,s] x_s)
owned C0: zero@ground   -> zero@ground
```

Every `x_s` and `y_r` is independent. The source line services are an entry
requirement to be paid by the eventual caller. Reader endpoints contain
the stated source contribution; they are not credited as independent
Gaussian jobs on the original `y_r`.

The complete local paid profile is

| Width | Jobs | Actual path |
| --- | ---: | --- |
| 7 | 512 | source line to common S8 |
| 17 | 512 | source S8 to canonical full R25 |
| 8 | 512 | reader ground to common S8 |
| 16 | 512 | reader S8 to its explicit q-perp flag |

The program uses 13,056 ordinary ADDs, four CLEAR_ZERO checks, eight
zero-retags and one owned zero cell. Literal monomial wrappers and their
counts are included. It uses no independent COPY and no retained
408-helper bank. All main Gaussian paths above are still charged.

[PROOF.md](PROOF.md) proves the chronological factorization, native full
conjugation phase and all-positive-width tensor identity. The source exit
is compiled without a dense `2^25` state vector. [MODULE.json](MODULE.json)
states the contract; [PROGRAM.json.gz](PROGRAM.json.gz) contains every path,
monomial, group, field role, coefficient and chronological event.

## Geometry and independent evidence

The new polarization reduces 64 source/read rectangles from span nine
and pairing rank two to span eight and cross-pairing zero. There are four
distinct coframe pairs, each serving 128 sources and 128 readers through
16 channels. [POLARIZATION.md](POLARIZATION.md) derives the factorization;
the geometry checker compares all 262,144 scalar entries and all 295,936
literal rectangle pairings.

A separately written reviewer checks the emitted word without calling its
generator. It replays all 1,024 original columns, same-frame ADDs and owned
returns, and independently checks 512 source gauges, 512 reader gauges and
four native full anchors. It also rejects a global-phase mutation, a wrong
physical frame and a missing uncompute. This is a separate AI-worker audit,
not independent human or formal-kernel acceptance.

The exact intermediate coefficient l1 peaks are 1 for sources, 5 for C0
and 53/8 for readers. Since all intervening Clifford maps are unitary, the
same constants bound field l2 growth relative to the largest original
field norm. This does not replace the eventual caller's precision bill.
See [REVIEW.md](REVIEW.md) and its JSON receipt.

The restricted 1,024-label geometry also has an explicit minimal standard-dot
embedding in dimension 20. [EMBEDDING-PROOF.md](EMBEDDING-PROOF.md) proves
minimality and the exact scalar minimum fitting rank 256; all `1,024^2`
ordered Gram pairs are checked. The emitted native program remains in
dimension 25. No free connection from a local full20 chart to global full25
is assumed. The four-clique scalar code in that proof has an existing generic
implementation and is not claimed as a new native construction.

## Reproduce

Python 3.12 and the standard library suffice:

```sh
python3.12 -B scripts/research_package.py --package research/odd-e8-polarized-native
python3.12 -B scripts/check_research_commit.py --package research/odd-e8-polarized-native
```

`VERIFY.json` registers eight bounded commands: normal and optimized geometry,
native-module and independent replay, followed by the embedding and a fresh
275-case small-dimension dense phase audit. Direct verifiers are read-only;
`--write` is reserved for explicit artifact authoring. Proof artifacts are
compared by canonical decompressed content. Retained container SHA256 values
authenticate source bytes or record environment metadata.

## Open next questions

The boundary of this small component is now constructive. Its paid paths,
coefficients, source/reader versions, zero-owned lifetime and phase conventions
are proved. Full-H acquisition, shared K/H flags, decoder COPY schedule,
caller termination, complete precision/storage work and the outer invoice
remain unknown. Unknown costs receive no zero-cost assumption.

The next decisive test is an actual K-plus-cross-block program that shares
these physical paths and fits the complete budget. Static containment is
insufficient: ADD needs the same current physical chart. The #5439 planning
gate leaves about 0.0902501847 per port per local invocation for **all** missing
work under its stated full-source COPY model. This package does not assert
that the global construction fits that allowance. Repeating this primitive
independently over every cube edge is not an admitted schedule.

The other question is whether the explicit I20 realization supports a smaller
complete supplier. Its first test must include actual entry/exit maps and
charge any return to the global 25-dimensional service. `TASK.json` records
these questions, their first steps and present blockers. Further construction
should require a compatible complete invoice, rather than optimize more local
modules while leaving the same boundary unknown.

## Sources and credit

Publication base: canonical main `32890bc5de034ab8fc93ac88ead7279a6a416d04`.
Credit Ali Romman for the odd-E8 direct-sum family and missing-H formulation
in #5439; Dugongue / #4929 and Dillon Amburgey's coded-native normalizers;
Cao Yifan for the retained P112 native construction; and Cinna Davis, zxv,
Jacob Alan Sussman and the native, Clifford, compiler and analytic lineage
credited in those sources. Exact runtime source pins and vendored byte
provenance are in `SOURCES.json`. Standard polarization, rank factorization
and Clifford algebra are not claimed as new general identities.

Prepared for THU New Media Research Center (@thu-nmrc) with substantial
OpenAI Codex assistance. Apache-2.0. No selected record, shared implementation
or predecessor evidence is changed.
