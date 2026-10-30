# Binary deficiency-two symplectic spread completion

This contribution was produced by Nick Petalas. Independent human and formal
proof-kernel review are unclaimed.

## Result and scope

Claim type: scoped written mathematical proof, with exact finite corroboration.

Let n >= 1, and let S consist of 2^n - 1 pairwise trivially intersecting
Lagrangian subspaces of a nondegenerate alternating 2n-dimensional F2-space.
A symplectic spread has 2^n + 1 members, so S has deficiency two.

Let Gamma have the uncovered nonzero vectors as vertices. Over F2 these are
also the uncovered projective points. Two distinct vertices are adjacent
exactly when their symplectic pairing is one. Write A for the ordinary integer
adjacency matrix, and put

$$
N=2(2^n-1),\qquad k=2^{n-1},\qquad Q=kI_N+A.
$$

Then S extends to a full symplectic spread if and only if Q is singular over
the rationals. When Q is singular, Gamma is connected and bipartite, Q has
nullity one, and every nonzero rational kernel vector has two nonzero opposite
constant values. Its two sign classes are exactly the nonzero vectors of the
two missing Lagrangians. The unordered completion pair is unique. If Q is
nonsingular, it is positive definite over the reals and S has no completion.

This answers Open next question 1 in Nick Petalas's
[odd-field spectral criterion, PR #5248](https://github.com/CrocSwap/integer-mult-bounds/pull/5248).
That theorem covers q >= 3 and leaves the binary case open because its graph
order argument fails there. Its proof and verifier are cited, not audited or
replayed. The new step here is a geometric component lemma using the span of a
color class. David Ganz's [atlas B098, PR #2849](https://github.com/CrocSwap/integer-mult-bounds/pull/2849)
supplies the original deficiency-two question and its deficiency-one predecessor.
The signless-Laplacian identity and basic symplectic dimension facts are
classical. Global literature priority is unclaimed.

This is an algebraic side result, recorded as a changed scope of the
`formal-interface-lemma` card. It supplies a precise completion interface for
the atlas. It does not change a supplier, COPY bill, kappa or selected result,
and it does not prove a complete multiplication theorem.

## Proof

### Hole count and degree

A Lagrangian has 2^n - 1 nonzero vectors. The old members have disjoint nonzero
sets, so the number of uncovered vectors is

$$
2^{2n}-1-(2^n-1)^2=2(2^n-1)=N.
$$

Fix a hole h. For each old Lagrangian L, the functional omega(h,-) on L is
nonzero. Otherwise h would belong to L-perp = L, contrary to being uncovered.
Thus exactly 2^(n-1) vectors of L pair to one with h. There are 2^(2n-1) vectors
in the whole ambient space pairing to one with h. Subtracting the old members
gives

$$
\deg_\Gamma(h)=2^{2n-1}-(2^n-1)2^{n-1}=2^{n-1}=k.
$$

Alternation excludes loops. Therefore Gamma is a simple k-regular graph with
k > 0.

### The new geometric component lemma

Suppose C is a connected bipartite component, with color classes X and Y.
Every vertex in X has k distinct neighbors in Y, and conversely, so both color
classes contain at least k = 2^(n-1) points.

Points in X pair to zero with each other because there are no edges within a
color class. Their linear span L is isotropic and has dimension at most n.
An F2-subspace of dimension at most n - 1 has at most 2^(n-1) - 1 nonzero
vectors, fewer than |X|. Hence dim L = n and L is Lagrangian.

Every hole outside C is orthogonal to every member of X, since an edge would
put it in C. It therefore lies in L-perp = L. All holes outside C consequently
pair to zero with one another. They have no edges to C either. Such a vertex
would have degree zero, contradicting k > 0. There are no holes outside C.

Thus any bipartite component is the whole hole graph. This argument uses the
symplectic geometry rather than a bound on N/k. In the binary case N = 4k - 2,
which exceeds the earlier N <= 3k gate when n >= 3.

### Spectral decision and recovery

For every real vector z indexed by the holes,

$$
z^TQz=\sum_{\{u,v\}\in E(\Gamma)}(z_u+z_v)^2.
$$

Thus Q is positive semidefinite. Its kernel consists exactly of assignments
satisfying z_u = -z_v on each edge. On a connected component these assignments
are determined by one value. An odd cycle forces that value to zero, whereas
a bipartite component admits the opposite constants on its two color classes.
Consequently Q is singular if and only if at least one component is bipartite.

The geometric lemma makes that component the whole graph. The kernel is
one-dimensional. Because Q has integer entries, its nonzero real kernel has a
nonzero rational vector. Its entries have equal nonzero magnitude and their
signs recover the unique bipartition X,Y, up to swapping the classes.

Counting edges on either side gives k|X| = k|Y|, and hence

$$
|X|=|Y|=N/2=2^n-1.
$$

Each class is pairwise orthogonal and therefore spans an isotropic subspace.
Its cardinality forces that span to have dimension n and forces the class to
be its entire nonzero set. These two Lagrangians meet trivially because their
full nonzero sets are disjoint. They meet every old member trivially because
they contain only holes. Adding them completes S.

Conversely, a completion partitions all holes into the nonzero sets of two
Lagrangians. There are no edges within either set, so Gamma is bipartite and
Q is singular. A connected bipartite graph has only one unordered bipartition,
which proves uniqueness of the completion pair. Nonsingularity of the positive
semidefinite Q gives positive definiteness and excludes a completion.

## Exact finite evidence

The standalone verifier constructs four binary models using F_(2^n)^2 and

$$
\omega((x,y),(x',y'))=\operatorname{Tr}_{F_{2^n}/F_2}(xy'+x'y).
$$

For n = 1,2,3,4, the field polynomials are respectively X+1, X^2+X+1,
X^3+X+1 and X^4+X+1. Multiplication permutations certify the finite field
models. The checker verifies alternation and nondegeneracy directly. It uses
the old Lagrangians y = ax for every nonzero a, omitting y = 0 and x = 0.
Every old member is checked for binary linear closure, isotropy and disjointness.

Rational RREF and separate integer Bareiss elimination compute the kernel and
determinant. A second search enumerates every isotropic subspace whose full
nonzero set lies among the holes, without using the graph or its spectrum.
It enumerates every possible completion pair and compares it with sign recovery.

| Ambient F2 dimension | Old members | Holes | Degree | Rank Q | det Q | Hole Lagrangians | Completion pairs |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2 | 1 | 2 | 1 | 1 | 0 | 2 | 1 |
| 4 | 3 | 6 | 2 | 5 | 0 | 2 | 1 |
| 6 | 7 | 14 | 4 | 13 | 0 | 2 | 1 |
| 8 | 15 | 30 | 8 | 29 | 0 | 2 | 1 |

The controls reject three invalid partial spreads: wrong deficiency, duplicated
members and a nonisotropic member. A separate abstract graph is K4,4 disjoint
from K6 with a perfect matching removed. It has N = 14 and k = 4, exactly the
binary n = 3 parameters, and a singular Q whose unique kernel has six zero
entries. Its bipartite component is not the whole graph. The new geometric
lemma excludes its realization as a valid hole graph. It is an abstract
control, not a symplectic counterexample.

The connected 14-vertex circulant with steps +/-1 and +/-2 supplies a
nonbipartite spectral control. Its rational kernel is trivial and its integer
determinant is 49,760,288. No claim that this graph is a hole graph is made.
These controls distinguish generic regular-graph facts from the geometric
implication proved here.

## Reproduction

From the repository root, use CPython 3.12. No third-party packages, predecessor
verifier, subprocess or network is needed for the mathematical check.

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/symplectic-binary-completion/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/symplectic-binary-completion/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/symplectic-binary-completion
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/symplectic-binary-completion --check-source-history
```

The direct check prints `PASS_SYMPLECTIC_BINARY_COMPLETION` and the exact
fixture/control values above. Optional `--receipt /absolute/path/outside-checkout/receipt.json`
writes a generated receipt containing those results, the interpreter version
and SHA256 hashes of all five package files. Receipt paths inside the checkout
are rejected. No receipt is handwritten or committed.

`SOURCES.json` pins the original card, selected-record context and both written
predecessors as provenance. The mathematical verifier neither imports nor
replays those predecessors. Hosted CI execution is recorded separately in the
PR body. Local CPython 3.12.15 normal and optimized checks pass, as do the
registered replay, syntax check and receipt-path rejection controls. The written
all-dimension proof is not machine checked.

## Limits and implementation bounds

The theorem covers q = 2 and every n >= 1. The executable controls cover only
the four specified punctured field spreads and the listed abstract/invalid
controls. They are not a classification of binary partial spreads. No valid
noncompletable binary deficiency-two fixture is supplied. In particular, this
criterion does not assert that every binary deficiency-two partial spread
completes. Larger deficiencies and nonisotropic partial spreads are outside scope.

The linear algebra is over the rationals and integers, even though the geometry
is binary. Reducing Q modulo two is not the decision procedure. The algorithm
is polynomial in the explicit hole inventory, not in n. No proof-assistant
build, supplier replay or independent human proof review was run. The selected
construction's five framework assumptions are unaffected.

The verifier has no recursion or dynamic code evaluation. Finite models have
at most 256 ambient vectors, 30 holes and 30-by-30 matrices. Span enumeration
is bounded by four rounds and a checked capacity of 4,096 stored subspaces;
each subspace has at most 16 vectors. All functions are under 60 physical lines.
Python and Fraction allocate dynamically, a managed-runtime deviation from
fixed allocation. Explicit finite input sizes bound this work. Runtime checks
remain enabled under optimized Python. The only indirect call is the bounded
invalid-input control callback. No shared source or validation policy is changed.

## Open next questions

1. Can the binary criterion be simplified to unconditional completion, or is
   there a binary deficiency-two noncompletable example? This distinguishes a
   recognition theorem from an existence theorem. Start with a literature-bound
   construction or a bounded search at one specified n. A failed finite search
   would not prove all-dimension completion; no such conclusion is claimed here.
2. At deficiency at least three, what geometric replacement for two-color
   recovery can identify the missing Lagrangians? Begin with the hole degree
   and one literal deficiency-three fixture. The signless kernel argument here
   only recognizes two color classes and does not settle that question.

## Provenance and overlap

Base: `de5ec2e7a6074068452f45b1a191b5c72832df4a`, priority revision 8.
The [advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19213513)
records the binary question and source pins. The selected-baseline command was
run after materializing its omitted sparse inputs. It authenticates metadata,
not the selected mathematics.

Live open PRs, recent account PRs, handoffs, active Discussions, local question
reservations, targeted merged searches and main-tree README searches were
checked before claiming. The `formal-interface-lemma` overlap report includes
remote pagination and explicitly incomplete sparse local-note coverage.
The same-account predecessor #5248 was published October 23, outside the last
24 hours. None of its mathematical checks was rerun. No global novelty or
exhaustive unpublished-work coverage is claimed.

Credit David Ganz for atlas B098 and the deficiency-two proposal, and Nick
Petalas for #5248's odd-field criterion and explicit binary question. The new
geometric component argument and binary extension are the contribution here.
All predecessor files and credit lines remain unchanged. Apache-2.0.
