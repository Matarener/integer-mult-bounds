# Binary C5 fitting matrices at total payload seven

This contribution is produced by Nick Petalas. Claim type: **finite
classification certificate**, with a written completeness argument. Apache-2.0.

There are exactly **1, 51 and 6 local-similarity classes** of rank-optimal
binary fitting matrices for the three positive total-seven C5 width profiles.
Only 1, 5 and 2 classes, respectively, have integral edge/private-channel
form. Thus 50 of the 58 classes across these three representative profiles
lie outside that form. Every class has an explicit canonical representative
in [RESULT.json](RESULT.json).

| Width profile | All legal matrices | Rank-four matrices | Local classes | Edge/private classes | Other classes |
|---|---:|---:|---:|---:|---:|
| (3,1,1,1,1) | 262,144 | 168 | 1 | 1 | 0 |
| (2,2,1,1,1) | 1,048,576 | 1,332 | 51 | 5 | 46 |
| (2,1,2,1,1) | 262,144 | 216 | 6 | 2 | 4 |

This answers the binary part of the total-seven classification question
explicitly left by JoyboyBrian's [#5215](https://github.com/CrocSwap/integer-mult-bounds/pull/5215).
That predecessor proves half-total rigidity over every field and supplies a
rational noncanonical total-seven example. It does not classify this binary
domain. Its results and JoyboyBrian's rank formula in
[#5023](https://github.com/CrocSwap/integer-mult-bounds/pull/5023) are cited,
without running their verifiers or recounting their domains.

## Exact domain and equivalence

Vertices 0 through 4 are labeled in cyclic order. Vertex i has positive
width d_i, with total seven. A fitting matrix M over F2 has diagonal blocks
I_(d_i), and both ordered off-diagonal blocks vanish at every nonedge.
Neighbor blocks are arbitrary, possibly rectangular and nonsymmetric.

Two fits are equivalent exactly when M'=L M L^-1 for block-diagonal L with
one independent GL_(d_i)(F2) block at each vertex. This is similarity, not
independent changes of row and column bases. Vertex permutations and
transposition are not included. Rotation/reflection sends every positive
total-seven width vector to one of the three displayed profiles, so these
cover all width patterns. The table does not also identify classes under
the automorphisms of each profile.

An integral edge/private form has x_i shared channels on edge (i,i+1) and
p_i private channels at vertex i, with x_(i-1)+x_i+p_i=d_i. Each shared
channel contributes an all-ones 2-by-2 matrix on its endpoint coordinates;
each private channel contributes [1]. Its rank is 7-sum(x_i), including over
F2. Rank-four forms therefore have sum(x_i)=3. Every nonnegative integral
choice and every local conjugate of each choice are included.

## Why the certificate is complete

The primary enumerator visits every assignment to the 18, 20 or 18 free
binary entries exactly once in reflected Gray order. Highest-pivot row
elimination gives these complete rank histograms, in order of ranks 0 to 7:

```text
(3,1,1,1,1): 0 0 0 0 168 18264 146784 96928
(2,2,1,1,1): 0 0 0 0 1332 85716 593688 367840
(2,1,2,1,1): 0 0 0 0 216 19368 147232 95328
```

The local group orders are 168, 36 and 36. Elementary additions I+E_ab
within a vertex generate its full binary general linear group. Gaussian
elimination proves this: no nontrivial scalar rescaling is needed over F2,
and a row interchange is three elementary additions. Starting with an
unclassified rank-four fit, the primary enumerator takes its full generator
orbit and removes it from the remaining set. Each generated matrix must
belong to that remaining set. Thus the resulting orbits are exhaustive and
disjoint, rather than sampled.

A representative is the least 49-bit row-major word in its orbit, with
word=sum_i(row_i*2^(7i)) and bit j in row_i equal to M_ij. RESULT.json records
its seven row integers, orbit size, stabilizer size and channel label.
The orbit-size histograms are {168:1}, {6:6,18:18,36:27}, and {36:6}.
Their weighted sums recover 168, 1,332 and 216 matrices.

All channel multiplicities with sum(x_i)=3 and nonnegative p_i are
enumerated. Local coordinate permutations send every placement of those
channels to the chosen standard placement. Conversely local similarity
preserves ordered block ranks, so distinct edge multiplicities cannot
become equivalent. Orbit membership therefore decides channel equivalence
exactly, including for nonsymmetric fits.

The independent verifier uses different enumeration, rank and orbit methods.
It takes a Cartesian product of complete row choices, intersects precomputed
annihilator sets of all 128 binary vectors, and derives rank from the kernel
cardinality. It enumerates every local invertible matrix by the determinant
formula and applies the entire product group. Every representative must be
canonical, the orbits must be disjoint, and their union must equal the
independently enumerated optimum set. A separately placed channel constructor
checks every edge/private label. No predecessor executable is imported.

For example, rows [73,6,6,9,48,48,64] give the first nonchannel representative
for (2,2,1,1,1). Its orbit has 18 matrices and stabilizer order two. It and
all 57 other representatives are part of the complete replay.

Eight corrupted certificates must reject. They change a rank histogram
while preserving its total, omit or duplicate an orbit, corrupt a
representative, change an orbit size or group order, erase a channel label,
or omit a profile. Another 7,200 checks compare bit operations with literal
entry-array conjugation and confirm elementary additions are involutions.
Complete-group orbits are also compared directly with generator orbits.

## Reproduction

From the repository root, with CPython 3.12 and the standard library only:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B scripts/research_package.py --package research/binary-c5-total-seven-orbits
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/binary-c5-total-seven-orbits/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/binary-c5-total-seven-orbits/independent.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/binary-c5-total-seven-orbits/controls.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/binary-c5-total-seven-orbits --check-source-history
```

Any CPython 3.12 installation can replace the local interpreter path.
Expected markers are PASS_BINARY_C5_TOTAL_SEVEN_ORBITS,
PASS_BINARY_C5_INDEPENDENT_KERNEL_AND_FULL_GROUP and PASS_BINARY_C5_CONTROLS.
The primary verifier prints the SHA256 of the canonical classification.
Its optional --receipt PATH writes a generated receipt containing package
file hashes, the actual interpreter, platform and elapsed time. Choose a
path outside the checkout. Registered commands produce no checkout artifacts.

## Limits and engineering checks

This is a complete **finite binary** classification for the exact domain
above. It is not an all-field classification or proof-kernel verification.
No native decoder, paid basis changes, reads/copies, dirty restoration,
ownership/hosting, preparation, stock/precision, tape, compiler or complete
consumer is supplied. No multiplication theorem, new kappa or selected
frontier change follows. No Lean, Docker or selected cold replay ran.

All loops have finite domain bounds: at most 2^20 matrices per profile,
seven rows per matrix operation, 168 members per orbit, 512 candidate local
GL matrices, and 4^5 channel choices. The primary stores at most 2^20 optimum
words; the largest actual set has 1,332. Independent vector tables have
128 entries per group element. There is no recursion, background process,
network use or predecessor import. Functions stay below 60 physical lines.
Explicit exceptions enforce invariants under normal and optimized Python.

Power of Ten rule 3 has a managed-runtime deviation in the four Python
files. Integer, set and list operations allocate dynamically; the fixed
seven-coordinate domain bounds all live collections. No fixed-allocation
or interpreter-allocation claim is made. A native port would need
fixed-capacity buffers before making that stronger claim. Rule 10 uses
warning-strict normal/optimized replay and the available static checks;
this does not establish a repository-wide static-analysis policy. Other
inspections found direct finite call paths, local state, checked results,
no metaprogramming and no intended additional deviations.

## Open next questions

- Classify the same profiles over larger finite fields or symbolically.
  This would separate field-specific orbit splitting from general odd-total
  geometry. Start with F3 and the one width-three profile. This binary
  enumeration supplies no universal normal form or bound on parameters.
- Determine whether a nonchannel class supports a useful source-compatible
  decoder. Start with a literal producer/consumer mask and one explicit
  representative. Paid basis changes, queries, restoration and a complete
  physical caller are missing; rank four alone is no price certificate.

Structured questions and blockers are in [TASK.json](TASK.json).

## Sources and credit

The base is canonical main de5ec2e7a6074068452f45b1a191b5c72832df4a,
priority revision 8. [SOURCES.json](SOURCES.json) pins predecessor documents
as provenance. The computation imports none of them. The
[advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19214456)
states this finite scope. Live PRs and handoffs, recent account PRs, local
reservations, all-main README searches and merged-PR searches were checked.
The cached scan covered 416 open PRs and 5,307 Discussion records, with
incomplete sparse local-note coverage. These searches do not cover
unpublished work or establish global literature priority.

Credit JoyboyBrian #5215 for the explicit question and #5023 for the rank
capacity theorem; Nick Petalas #5180 and #3248 for earlier rigidity and
equality arguments; Tekalign #3362, Sagar Thakrar #2484/#3232, ywz65 #2471,
Cinna Davis, Adam Gall, ctoth, Philippe Van Velzen and the retained
P112/query-mask lineage for the preceding interfaces. Gaussian elimination,
orbit-stabilizer counting and finite general linear groups are classical.
The new finite classification and standalone verifiers are produced by
Nick Petalas. Independent human and formal proof-kernel review are unclaimed.
