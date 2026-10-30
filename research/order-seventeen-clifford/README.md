# An explicit order-seventeen Gaussian-dyadic Clifford

**Scoped construction and exact finite certificate; no new multiplication bound.**

This answers the order-17 existence question in Nick Petalas's pending
[PR6192](https://github.com/CrocSwap/integer-mult-bounds/pull/6192), pinned at
`91df334ccd2a4bc9959e311f118ac8aaf967ffc2`. We give a four-qubit Clifford
whose actual matrix satisfies `Phi17(U)=0`, then apply that predecessor's
Bell-spectator method to attain its native `B`-rank cap of eight on eight
qubits. The construction works over `Z[i,1/2]`, including its global phase.

With little-endian qubits `0,1,2,3`, rightmost factors acting first, set

```text
Hg = (1+i)/2 [[1,1],[1,-1]],   S = diag(1,i),
U17 = i S_3 CZ_03 CZ_12 CZ_23 Hg^(tensor 4).
```

The complete `16 x 16` certificate gives `U17^17=I`, `Phi17(U17)=0`,
trace `-1`, all eight signed Pauli-generator images, symplectic defect
rank eight and native `B` rank four. On four added identity spectators,
let `V` prepare four Bell pairs and put `W=V^-1(U17 tensor I16)V`.
Then `Phi17(W)=0`, and its native block is

```text
B_W = [[I, A+I], [I, I]],     A = [[0,0,0,1],
                                  [0,0,1,0],
                                  [0,1,0,1],
                                  [1,0,1,1]].
```

Since `A` is invertible over `F2`, `B_W` has rank eight. Adding identity
qubits preserves that rank, so the cap is attained for every ambient
width `M>=8`. See [PROOF.md](PROOF.md) for conventions, the finite
certificate, algebraic extension and credited upper-bound argument.

## Evidence and limits

`verify.py` uses exact Gaussian integer numerators with reduced denominators.
It checks all matrix entries, all sixteen nonidentity powers, all signed
Pauli-generator images, and the complete binary Bell conjugation. Seven
controls distinguish wrong phase, an omitted CZ, a truncated polynomial,
finite order without a primitive response, unused spectators, a nonsymplectic
prediction and a nonunitary cyclotomic companion.

`independent.py` was written separately, without importing the primary
checker. It uses unreduced Gaussian integers `G=4U17` and clears denominators
in the polynomial identity; it independently checks the eight Pauli images
and constructs the binary Bell circuit. Both checkers use explicit failures
that remain active under optimized Python. The eight-qubit polynomial
identity follows by tensoring and conjugation in the written proof; neither
checker expands all powers of a dense `256 x 256` matrix.

This is an explicit finite algebraic response, not an admitted supplier.
No source-bound caller, native legal schedule, ownership/dirty restoration,
complete paid/target invoice or multiplication theorem is supplied. Native
`B` rank is a binary algebraic invariant, not a physical gate-price receipt.
The selected conditional `kappa=781451/250000000`, its five framework
assumptions and selected evidence remain unchanged. No selected cold replay
was run. Earlier binding-only orientation was reused after confirming its
1227 bound inputs were unchanged from checkpoint `3f0152a32eeebac0df11946dbd50cabe5a7f7839` to this base;
that reuse is not a fresh scientific replay.

## Reproduce

From a full Git checkout, with Python 3.12 and no third-party dependencies:

```sh
python3.12 -B scripts/research_package.py --package research/order-seventeen-clifford --check-only
python3.12 -B scripts/research_package.py --package research/order-seventeen-clifford
```

The registered commands run both checkers normally and with `-O`, isolated
and with warnings treated as errors. Expected markers are
`PASS_ORDER_SEVENTEEN_CLIFFORD` and `PASS_INDEPENDENT_ORDER17`.
For a Git-free source export, run these direct commands from its root,
once normally and once with `-O` added:

```sh
python3.12 -I -B -W error research/order-seventeen-clifford/verify.py
python3.12 -I -B -W error research/order-seventeen-clifford/independent.py
```

[VERIFY.json](VERIFY.json) has no external live inputs: all mathematical
inputs are defined in the package. [SOURCES.json](SOURCES.json) pins the
base, original catalogue card and selected record as historical provenance.
The pending predecessor is not an ancestor dependency: its two cited source
documents are retained verbatim under `sources/` to make the precise theorem
and method available in an offline export. [SOURCE-PINS.json](SOURCE-PINS.json)
records their public source URLs, exact head and SHA256 digests, checked by
the primary verifier. Their bytes were also compared with the fetched head
before publication. No predecessor executable is imported or replayed.
The Git source-history preflight covers declared base provenance; it does
not authenticate the external predecessor-head label or validate its theorem.
Package-local changes already select this registered replay.

## Coordination and scope

Canonical main was pulled first at
`a5bff3bf133e482541c09eba4e773884bdb2b1b7`, priority revision 8.
The original `joint-query-controller` card is retained in [TASK.json](TASK.json).
Its scope is explicitly changed to this bounded algebraic subproblem: the
card's complete source/consumer acceptance gate remains unmet.
The canonical investigation is [Discussion 1166, comment 19273131](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19273131),
responding to the predecessor's released
[handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19272674).

Overlap coverage was bounded: the local helper searched 30 of 8623 package
notes (8593 absent in this sparse checkout), without a fresh remote cache.
Live checks read the newest 15 handoff comments and all-state PR searches
for `Clifford seventeen`, `Phi17` and `order-17`; no competing explicit
instance was found in those results. This is not an exhaustive novelty audit.
The stopping rule was the first complete exact order-17 construction and
its rank certificate, without searching larger orders or proposing a
supplier-budget change.

## Open next questions

- **Can this response satisfy an actual source/consumer contract?** Its
  algebraic feasibility removes one uncertainty, but does not remove paid
  work. Start by identifying one current caller whose required whole-bank
  action matches this exact matrix, then check native chronology, all
  retained outputs and restoration. Blocker: no such caller is supplied here.
- **Can the rank-eight witness be implemented more cheaply than this Bell
  conjugation in that caller's allowed alphabet?** A cheaper implementation
  might affect a complete invoice. First establish the matched contract and
  price the stated circuit, then compare one exactly equivalent circuit.
  Blocker: without that contract and cost model, an algebraic gate count
  cannot establish a saving. Do not expand the search before that gate.

The structured questions and blockers are also in [TASK.json](TASK.json).

## Credit

Prepared by **apoursh**, with substantial OpenAI Codex assistance for
construction, independently written exact checks, proof and packaging.
Nick Petalas retains credit for PR6192's odd-cyclotomic rank theorem and
Bell-spectator sharpness method; Ross Richardson retains the earlier
whole-bank cubic/Pauli-character argument (PR4081). Copied predecessor
documents retain their attribution and the repository's Apache-2.0 license.

Cyclic Clifford constructions are classical; for example, Oliver Kern,
Kedar S. Ranade and Ulrich Seyfarth give cyclic MUB constructions in
power-of-two dimensions in
[arXiv:0912.4661](https://arxiv.org/abs/0912.4661).
This package claims a reproducible explicit Gaussian-dyadic instance and
rank-eight certificate for the repository's handoff, not historical priority
for cyclic Clifford existence or Bell conjugation. The cited literature is
context, not a replay dependency. New material is Apache-2.0.
