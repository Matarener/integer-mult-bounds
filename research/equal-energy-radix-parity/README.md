# A smaller even radix for equal-energy packed rows

Scoped written proof with exact finite corroboration, produced by Nick Petalas.
Apache-2.0. No new kappa or complete multiplication theorem is claimed.

Equal-energy Gaussian-integer rows admit a smaller sufficient even packing
radix than the whole-ball threshold in
[Arham Tahir's PR #1906](https://github.com/CrocSwap/integer-mult-bounds/pull/1906).
At row energy `512^2`, **B=726 suffices instead of B=1024**. For 512 columns,
the largest packed input `B^511` has **4,857 bits instead of 5,111**, a
reduction of 254 bits. These are exact integer lengths, not runtime measurements.
The row-energy hypothesis is essential.

## Theorem and proof

For a finite vector z over Z[i], define

```
E(z) = sum_j |z_j|^2,       P_B(z) = sum_j z_j B^j.
```

**Sharp even-energy kernel bound.** For every even integer B>=2, a nonzero
finite Gaussian-integer vector d with P_B(d)=0 and even E(d) satisfies

```
E(d) >= 2(B^2-B+1).                                      (1)
```

Equality is attained by d=(B,B-1,-1), and by appending zero coordinates.
Thus (1) is sharp uniformly in dimensions at least three. No assertion of
sharpness for differences of unitary rows follows from this witness.

To prove (1), regard d as the coefficients of D(x). Since D(B)=0,
monic division gives D(x)=(x-B)Q(x) with Gaussian-integer coefficients q.
The finite nonzero q has at most one fewer coefficient than d. Extend q
by zeros at both ends and put

```
S = sum_j |q_j|^2,
V = |q_0|^2 + sum_j |q_(j+1)-q_j|^2 + |q_last|^2.
```

The sum in V runs over consecutive coefficients inside q. Expansion gives

```
E(d) = (B^2+1) S - 2B Re sum_j q_j conjugate(q_(j+1))
     = (B-1)^2 S + B V.                                  (2)
```

The first jump from zero to a nonzero Gaussian integer and the last jump
back to zero each contribute at least one to V, even if the supplied
coefficient list contains leading or trailing zeros. Therefore V>=2.
Since B is even, (2) gives E(d)=S modulo 2. The assumed even energy forces
S to be a positive even integer, hence S>=2. Equation (2) now yields

```
E(d) >= 2(B-1)^2 + 2B = 2(B^2-B+1).
```

The displayed d evaluates to zero and has exactly that energy, proving
sharpness. The parity step is the new restriction absent from the
whole-ball B^2+1 argument.

**Equal-energy comparator.** Let u,v be Gaussian-integer rows of the same
finite length, with E(u)=E(v)<=M. If B>=2 is even and

```
B^2-B+1 > 2M,                                           (3)
```

then P_B(u)=P_B(v) if and only if u=v. Indeed d=u-v has even energy because

```
E(d) = 2E(u) - 2 Re sum_j u_j conjugate(v_j).
```

The parallelogram identity also gives E(d)<=4M. A nonzero packing-kernel
difference would contradict (1) and (3). This proves the statement in every
finite dimension, jointly for real and imaginary components, including
absolute phase. The sufficient condition (3) is not claimed optimal.

## Application and exact improvement

PR #1906 supplies the retained gate-valid unitary premise and the scaling
contract. If U1,U2 are square unitary matrices, R U1 and R U2 are
Gaussian-integer matrices, and R is a positive integer, every scaled row
has the same energy R^2. Apply (3) row by row with M=R^2. Evaluation on the
single vector (1,B,...,B^(N-1)) then determines the complete matrices.

For two retained circuits with C-gate counts k1,k2, that predecessor sets
K=max(k1,k2), rescales both integer executions to R=2^K, and obtains the
required equal row energies. Those premises are cited, not re-audited here.
The new lemma applies to every such matrix pair; no particular predecessor
circuit or recorded receipt is replayed.

At the N=512, K=9 parameters reported in #1906:

```
M = 262144,    2M = 524288,
726^2-726+1 = 526351 > 524288,
724^2-724+1 = 523453 < 524288.
bit_length(726^511) = 4857,
bit_length(1024^511) = 5111.
```

Thus 726 is the least even radix satisfying **this criterion**, rather than
an asserted minimum radix for the actual rows. It is smaller than the
whole-ball threshold 2R by 298. A power-of-two radix remains 1024 under this
criterion; exploiting 726 requires general integer multiplication in the
packing recurrence. A speedup, lower total execution cost, production adoption
and a new Lean theorem are all outside this contribution.

## Reproduction and evidence

From the repository root, with the standard library only:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/equal-energy-radix-parity
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/equal-energy-radix-parity/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/equal-energy-radix-parity/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/equal-energy-radix-parity --check-source-history
```

Expected marker: `PASS_EQUAL_ENERGY_RADIX_PARITY`. The proof supplies the
unbounded conclusion. The standalone verifier corroborates it with:

- 6,200 constructed quotient/kernel identities, including 3,112 nonzero
  even-energy kernel vectors, and 256 sharp witnesses at even B=2..128.
- Independent direct polynomial sums on all 3,051 real three-digit words
  with digits in [-B,B] at B=2,4,6, and 1,875 complex two-digit words with
  real/imaginary digits in [-2,2]. Respectively six and four are nonzero
  even-energy kernel vectors.
- 19,800 complete equal-energy shell vectors at energies 2,6,10 and complex
  lengths 1..4, obtained by filtering 6,299,180 bounded digit words. The
  (energy,packed-value) keys have no collision at the proved radices.
- Thirty new small scaled-unitary fixtures at dimensions 2,4,8 and C counts
  0..9, 840 exact Gram entries, 300 normalized matrix comparisons across
  unequal C counts, and thirty rejected absolute-phase mutations.
- Four explicit hypothesis countercontrols and thirteen input rejections.
  Odd radix B=3 admits the even-energy kernel (3,-1) below (1). At even
  B=2 the odd-energy vector (2,-1) also violates (1). Two rows of energies
  36 and 37 collide at B=12 while satisfying the other M=64 hypotheses.
  Distinct rows of equal energy three collide at the unsafe radix two.
- Exact least-even-criterion arithmetic at all M=1..4096, plus the stated
  R=512 application. This is not a search for optimal comparator radices.

`--receipt /absolute/path/outside/checkout.json` optionally writes the actual
executed counts, interpreter version and SHA256 of all five package files.
Default replay writes nothing. The receipt is generated, not hand-written.
The source README and orientation records are pinned as provenance only;
no predecessor executable or numeric receipt is imported. Direct replay is
Git-free and supports read-only exported package files.

Power-of-ten scope: no recursion, no external solver, no dynamic code generation,
functions under 60 lines and explicit contracts that remain active under -O.
All loops use fixed domains. The largest enumeration has 7^8 digit words;
its set is bounded by that domain. Integer and collection allocation in Python
is a managed-runtime deviation from fixed allocation, constrained here by the
fixed dimensions, digit bounds and gate counts. The comparator boundary caps
rows at sixteen coordinates, components at 2^32 and M at 2^64. Warning-strict
normal and optimized replays supply the applicable interpreter diagnostics.

## Scope, overlap and credit

The formal-interface-lemma card is changed to a written algebraic side result.
Its first baseline command passed with `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`.
The selected result and all five framework assumptions are untouched.

Credit Arham Tahir / Arham-Tahir64 #1906 for the energy-ball method and its
explicitly excluded equal-energy sharpness scope; woklerx #1859 for the
unitary premise; Jeremy Kothe / jeremykothe2 #593 for the retained Clifford
semantics and packed equality argument; commdata2338 for semantic binding;
Ross Richardson #1934 for separate full-matrix corroboration; ywz65 #2499
for the separate formal energy law; and the retained Lemma A/G, icekylinx,
Chafik Boukhalfa and jacklightChen lineage. Polynomial division, the
parallelogram identity and the discrete quadratic-energy expansion are classical.
The new step is their parity-sensitive packing-kernel application and its
smaller sufficient equal-energy radix. No literature-wide priority is claimed.
Predecessor credit lines and files are unchanged.

Overlap checks read live open PRs, this account's recent PRs, active Discussions,
local reservations, relevant merged PR bodies and all-main README searches for
packed radix, equal-energy packing, the new formula and the value 726.
The cached card scan covered 310 open PRs and 5,456 Discussion records, with
7,902 sparse local notes omitted. Separate Git searches covered relevant
omitted README text. Closed PR diffs, nested code and unpublished work remain
coverage limits. The prospective
[CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19219147)
records the target. These checks are not proof of novelty.

## Open next questions

What is the smallest common energy of a genuine pair of colliding rows at an
even radix, and which such rows extend to scaled Clifford matrices? Start with
a fixed B and minimize both row energies subject to equal packing. The sharp
kernel witness alone need not be realizable at the radius used by the bound.
This blocks any claim that (3) or 726 is optimal for actual unitary rows.

Can the quotient energy identity and finite-path variation bound be proved in
Lean and connected to an actual comparator? The first step is that exact
integer lemma, followed by the gate-valid equal-row-energy interface.
No kernel proof, implementation-cost study, supplier replay or complete
multiplication proof was run. Structured questions are in TASK.json.
