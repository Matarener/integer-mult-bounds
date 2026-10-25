# Encoded CRT address conversion for the physical tensor

This package implements the CRT coefficient-order entrance and exit left open
by Jose Manuel's [PR3935](https://github.com/CrocSwap/integer-mult-bounds/pull/3935),
pinned at `240597ed313fc2854c0462b23c89dc3bae72aaf5`. It preserves source08's
triangular CRT algebra and substitutes one **paid full-support router** for a
quadratic sequence of adjacent-axis exchanges. Both directions include the
two padding/cropping scans required by the actual compact tensor interface,
all encoded offsets, complete spectator records, copies and cleanup.

Under the pinned router premises and the explicit newer many-axis caller laws,
the complete conditional conversion bill fits `O(V p^Φ log p)`,
Φ=.99827619697. [PROOF.md](PROOF.md) states the full invoice and backing bound.
Integer multiplication requires **three** conversions; its numerical tensor,
prime supply, final normalization and integer recovery remain separate.
There is **no new κ claim**, production-sized native execution or formal proof
of the complete multiplication theorem.

The implementation uses canonical Count tapes and a fixed 192-role wrapper.
`Converter.run_plan` accepts the actual PR3935 `TensorPlan` and verifies its
products and address width. Coprimality is checked rather than inferred from
the type; the predecessor's repeated-(7,7) fixture is not a CRT witness.

## Reproduce

Base: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`; Python 3.12, standard library.
From the repository root:

```sh
python3.12 scripts/research_package.py --package research/crt-address-streams
```

The registered command explicitly downloads about 38.5 MB of **pinned external
predecessor sources** into temporary storage. Every size, SHA256 and Git blob
is checked; no GitHub credentials are needed. Network availability is required
for that command. The exact files and source commit are in
[NETWORK-SOURCES.json](NETWORK-SOURCES.json). This avoids duplicating large
frozen predecessor archives in the PR. Only declared source files enter a private import tree, with a fresh bytecode
namespace; unpinned siblings and cached bytecode in an offline tree are ignored.
The predecessor loader independently
checks the complete embedded exports, receipts and source-specific notices.

For an already downloaded, authenticated tree with paths matching that manifest:

```sh
python3.12 -B research/crt-address-streams/verify.py --source-root /path/to/dependencies
```

Expected: `PASS_CRT_ADDRESS_STREAMS ...`. Direct replay also works from a Git-free
source export. Neither mode writes into the package or modifies predecessors.
Dependency source authentication/setup is outside the numerical macro and is
explicitly disclosed; it is not free runtime arithmetic.

## Evidence and limits

[EXPECTED.json](EXPECTED.json) records deterministic replay coverage: every basis
column for four complete shapes, both descriptor/conversion directions, all
padded lower prefixes, arbitrary nonzero invalid shear cells, 2,176 independent
unit/nonunit inverse cases, the actual compact typed-plan fixture, failure
controls and exact cost-gap arithmetic. The wrapper peak in these fixtures is
39 scratch leases. Finite observations do not replace the all-parameter role,
cost or router assumptions. Python backing retains past high-water lengths;
the proof distinguishes that from current live space.

Wrong offsets, wrong shift direction and wrong field permutation are checked
against the direct `k μ_i mod s_i` oracle. Malformed extents/metadata, nonzero
padding, dirty prior work, internal-port aliases and unconsumed outputs reject.
The tests use the unchanged full router with its q=2 **literal** native fixture;
they do not execute the enormous production native instance or establish its
universal cost premise.

## Open next questions

The two structured questions in [TASK.json](TASK.json) are actual numerical
tensor composition and final integer normalization/rounding. Each names its
first experiment and inherited blockers. Neither is discharged by this layout
contribution. Pairwise coprime near-one lengths under the newer asymptotic laws
also remain an explicit source premise, rather than an assertion about an old
prime-generation cutoff.

## Credit and license

Prepared by Tekalign (tekuuu), with substantial OpenAI Codex assistance in design,
code, proof and verification. New work is Apache-2.0. CRT algebra follows
Agarwal and Cooley and the retained source08 construction; the full router and
physical tensor interface are Jose Manuel (`jmbarrancoml`)'s PR3935, building on
PR3619 and the predecessors pinned within its complete exports, including the original
OpenAI manuscript, RaD/hipotures reports and Douglas Colkitt's retained work. Those sources,
licenses and notices are unchanged. This contribution adds the actual encoded
layout composition and full conditional cost/backing argument; it does not
claim the predecessor's algebra or routing theorem as new work.

Jose Manuel's concurrent [interface clarification](https://github.com/CrocSwap/integer-mult-bounds/discussions/3664#discussioncomment-19036660)
confirms the direction convention, actual scalar-axis notation and the two final
S factors for the eventual numerical sandwich. Its prospective recovery work is
separate; this package pins the published tensor head above.
