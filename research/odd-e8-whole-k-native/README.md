# A complete native odd-E8 K component

This package constructs the full block-diagonal `K_odd` component from Ali
Romman's [#5439](https://github.com/CrocSwap/integer-mult-bounds/pull/5439).
It retains every original source and reader field and emits every local
Gaussian path, ordinary wrapper, scalar coefficient and absolute phase.
The construction uses two orthogonal nine-dimensional coframes in each
512-port cube, with direct same-frame ADDs and no helper, owned field,
COPY or CLEAR. It complements the directed `H_ab` component in
[#5464](https://github.com/CrocSwap/integer-mult-bounds/pull/5464).

This is a local native construction. It supplies K, including its normalized
forward and backward interfaces. H acquisition, compatible K/H chronology,
the whole caller, complete precision/storage work and kappa admission remain
open. No leaderboard improvement or new kappa is claimed.

For `Q=C_0`, `D=C_[1,25)` and the explicitly emitted real normalizers `L_i`,
the forward word on arbitrary independent ground-chart inputs is

```
F_K = diag(D,D) L(C_K Q^-1),
C_K = diag(L_i^-1) K_odd diag(L_i).
```

Here `L(A)` denotes the two-bank lower shear. Thus sources exit as `D x_i`,
and readers as `D(y_i + sum_j K_odd[i,j] L_i^-1 L_j Q^-1 x_j)`.
Each `L_i` commutes with the full Gaussian `R=DQ`, and `C_K` is a symmetric
involution commuting with R. The reader endpoint is coupled to the sources.

The source's virtual `Q^-1` occurs inside an emitted ordinary monomial
`Phi_[q_i] L_i Q^-1`; it is not an assumed incoming Gaussian service. The
reader's final `D L_i^-1 Phi_(q_i^perp)^-1` is likewise emitted as an
ordinary monomial, with a generic absolute-phase proof. The word works at
every positive field width. Address operators tensor-lift; owner scalar
coefficients are applied once, and a phase opcode theta lifts to `i^(f theta)`.

The complete paid profile per cube is 512 children of each width 8, 9, 15
and 16. Per owner port (one X and one Y field), ordinary work is 76 ADD,
15 P, 15 D, 6 X and 6 phase opcodes. The intermediate coefficient l1 peaks
are 1 on X and 8 on Y, with scalar denominator exponent 4. Unitary address
maps therefore give field l2 growth at most eight times the largest input
field norm. These local constants do not replace a caller precision bill.

`K-PROGRAM.json.gz` fully emits cube `(0,0,0)`. `K-TEMPLATE.json` describes
the literal constructor over all `14^3=2744` disjoint cubes. The generic
Lagrangian and phase arguments are in [PROOF.md](PROOF.md); the independently
checked all-family geometry is [FAMILY.json](FAMILY.json) and
[FAMILY-PROOF.md](FAMILY-PROOF.md). This structured forall word avoids
storing 106,774,528 ADD events. A second, separately reviewed extreme cube
was checked during development; it is additional finite evidence.

The no-erasure word also gives an emitted backward companion,

```
B_K = diag(D,D) U(-Q C_K).
```

`B-PROGRAM.json.gz` transforms each gate by inverse transpose in the same
chronological order, then includes every ordinary boundary normalization.
It does not require `[C_K,Q]=0`. Its paid profile is unchanged; its ordinary
profile per owner port is 76 ADD, 15 P, 15 D, 13 X and 6 phase. Details are
in [BACKWARD-PROOF.md](BACKWARD-PROOF.md).

The independent [reviewer](independent_review.py) does not call the word
generator or phase compiler. It compares all 262,144 scalar entries,
replays all 1,024 independent logical columns, and checks geometry, charts,
normalizer congruences and literal invoices. Small-dimensional exhaustive
tests corroborate the separately reviewed generic phase and Lagrangian
proofs. The same replay independently compares every backward instruction
with its exact gatewise inverse transpose and checks all boundary masks.
[REVIEW.md](REVIEW.md) states the scope of that audit. It is a
separate AI-worker review, not independent human or formal-kernel acceptance.
The backward verifier also runs four executed controls on actual emitted
operations: changed K coefficient, overwritten source, wrong source chart,
and a phase-i change invisible to signed tableaux.

A scoped [terminal support bound](TERMINAL-BOUND.md) now distinguishes the
constructed K word from a completed caller. For distinct fresh-stage proper
K codes in real signed orthogonal gauges, every path of the negative endpoint
Q^-1 B D has Gaussian row support of rank n-2. A fixed finite ordinary
monomial/owner-scalar decoder on that cohort cannot produce a larger-rank
Gaussian job at all positive widths. The permitted n-2 target has not itself
been decoded. This is not a full-caller lower bound; paid correction, earlier
native readout, changed code support and mixed cohorts remain separate gates.
The proof includes a scoped approximation bound. Its verifier checks all
38,912 edges of the committed root K plus 1,344 small actual paths; a separate
portable reviewer reconstructs 672 paths in the old normalizer gauges.
See [the separate review](TERMINAL-REVIEW.md) for exact scope and credit.

Python 3.12 and its standard library suffice. `VERIFY.json` registers eight grouped
bounded, read-only normal/optimized commands for the family geometry,
forward word, independent review, backward word and both terminal-bound engines. With the repository
runner, use:

```sh
python3.12 -B scripts/research_package.py --package research/odd-e8-whole-k-native
python3.12 -B scripts/check_research_commit.py --package research/odd-e8-whole-k-native
```

The grouped forward and terminal hooks each serialize two explicit engines,
for twelve scientific subcommands in total. Direct `--write` flags are reserved for explicit artifact authoring.
Scientific words compare canonical decompressed JSON, avoiding dependence
on gzip container bytes or local paths. Exact source pins and credits are
in [SOURCES.json](SOURCES.json). Original task provenance, scope change and
remaining decisive obligations are in [TASK.json](TASK.json).

Credit Ali Romman for the odd-E8 direct-sum family and product-cube K;
Dugongue / #4929 and Dillon Amburgey for the coded-native normalizers;
Cao Yifan for the retained P112 native construction; and Cinna Davis, zxv,
Jacob Alan Sussman and the native, Clifford, compiler and analytic lineage
credited by those sources. The exact phase tools are retained from #5464.
Standard Clifford algebra, transposition and tensor identities are not
claimed as new general identities.

Prepared for THU New Media Research Center (@thu-nmrc), with substantial
OpenAI Codex assistance. Apache-2.0.

## Open next questions

Can a complete native H service use these actual K paths? The first test is
one chronological K-plus-H word preserving arbitrary old reader data and
all original source exits, with paid source acquisition and every return.
The missing compatible H service and source/reader flag schedule block a
complete supplier; scalar coefficients and static containment do not close it.

Can that completed supplier improve the full caller? Install the exact
normalized contracts, prove all original-input endpoints, then charge every
boundary, central request, precision, storage and compiler obligation. The
current coupled K endpoints and local savings alone give no new kappa.
