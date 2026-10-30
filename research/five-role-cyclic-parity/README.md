# A five-role cyclic parity stencil needs twenty clockwise XORs

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: finite certificate with a written reduction to arbitrary binary
vector inputs. For five arbitrary labeled registers, the complete map

```
y_i = x_i + x_(i+1 mod 5) + x_(i+2 mod 5),   0 <= i < 5,
```

has exact minimum cost twenty when the only allowed operations are
`r_(i+1 mod 5) += r_i`, each at unit cost. No workspace, free wire permutation
or free basis change is allowed. [PROOF.md](PROOF.md) gives a twenty-step word.
The complete radius-nine identity ball and radius-ten target ball contain
10,566 and 22,576 matrices and are disjoint, excluding every shorter word.

The contribution is this restricted-alphabet optimum. Gareth Davidson's
[merged PR #1188](https://github.com/CrocSwap/integer-mult-bounds/pull/1188)
already gives a complete unrestricted five-role metric with twenty generators;
that result is credited and not replayed here. [Ali Romman's PR #5793](https://github.com/CrocSwap/integer-mult-bounds/pull/5793),
head `9ddb022cc1d879a5d3173f8f1f526a2ff504e7b3`, supplies the custom-alphabet
synthesis interface and its four-role limit. Classical finite-group search and
meet-in-the-middle exclusion are inherited methods. Literature priority is
unclaimed.

## Reproduce

From the worktree root, with the CPython 3.12 standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/five-role-cyclic-parity/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/five-role-cyclic-parity/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/five-role-cyclic-parity
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/five-role-cyclic-parity --check-source-history
```

Local validation uses CPython 3.12.15 on macOS 27.0.1 arm64. Another Python
3.12 interpreter may replace the absolute path. Each registered command has
a 120-second timeout. The standalone verifier requires neither Git nor network,
writes no files and emits `PASS_FIVE_ROLE_CYCLIC_PARITY` in a generated JSON
receipt bound to all six package files' SHA256 hashes. No receipt is handwritten.
[SOURCES.json](SOURCES.json) pins historical provenance, including #1188's README.
No predecessor executable or mathematical certificate is imported or replayed.

The checker enumerates the two exclusion balls and a separate known
nineteen-gate positive-control ball. It checks all 32 literal inputs, inverse
recovery, twenty deleted-gate controls and nine malformed-input rejections.
All counts concern labeled complete matrices, without a symmetry quotient.
Every word shorter than twenty in the declared alphabet is excluded.

## Scope and limits

The `complex-rank-shape-decoder` card changes to this scalar linear-synthesis
side result in [TASK.json](TASK.json). Source-binding orientation passed at
canonical main `de5ec2e7a6074068452f45b1a191b5c72832df4a`, priority revision 8.
No native caller or complete signed invoice is supplied. The selected conditional
kappa and its five inherited framework assumptions remain unchanged.

The [original CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19216913)
proposed unrestricted synthesis. The [scope correction](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19217027)
withdraws originality for that covered case and restricts the operation alphabet.
Only the clockwise optimum is claimed as new. Live PRs, main README formulas,
merged work, Discussions and local reservations were checked. Cached/sparse
and unpublished coverage remains limited; no-match searches do not prove novelty.

Extra roles, free bases/permutations, other endpoints, nonlinear instructions,
odd characteristic and unequal gate prices are outside scope. Native phases,
ownership, routing, dirty return, rounding, tape movement and complete recursive
costs remain open. No selected cold replay, Lean, Docker or complete multiplier
is claimed. Independent human and formal proof-kernel review are unclaimed.

Power of Ten inspection is confined to the new verifier. Loops are bounded by
five roles/gates, at most ten search layers, 32 inputs or twenty witness gates.
The conservative generated-word bound per ball is `sum(5^k,k=0..10)=12207031`;
the largest retained ball here contains only 22,576 matrices. Functions fit
within 60 lines, mutable search state is local, and there is no recursion,
subprocess, network call or dynamic code generation. Explicit checks remain
active under -O. Rule 3 has a managed-runtime deviation for Python's bounded
integer, tuple and set allocation. Warning-strict normal/optimized execution
and in-memory syntax compilation supply diagnostics.

## Open next questions

Can a concrete native caller use this clockwise-local stencil as a cheaper
complete adapter? First identify its five-role cyclic layout and exact boundary,
then price conversions, phases, aliases, ownership and every restoration.
No compatible caller or complete invoice is supplied. A scalar XOR optimum
alone does not imply a recursive gain. No follow-up is reserved.
