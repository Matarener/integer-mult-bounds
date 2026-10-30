# One-axis transported coframe optimization is NP-hard

This contribution was produced by Nick Petalas. Apache-2.0.

## Result and scope

**Claim type: scoped mathematical proof, with exact finite corroboration.**
The rank-moment optimization problem for transported binary coframe choices
can encode Simple Max Cut. The reduction uses one Gaussian axis per field,
the identical two-choice menu everywhere, rank-zero/rank-one transitions,
fixed external main charts, and both entrance and exit adapter charges.
Its constructed-family decision problem is NP-complete. All power tariffs
`r^t`, `0<t<=1`, give the same integer objective.

For a graph with `n` vertices and `m` edges, put `M=2n+1`. The explicit word
has bill

```text
B(x) = M (m-cut(x)) + 2|x|,
maxcut(G) = m - floor(min_x B(x)/M).
```

The phase-exact Gaussian-dyadic Fourier axis is
`F=[[1,1],[1,-1]]/(1+i)`, with `F^2=-i I` and `F^-1=i F`.
A transported edge has rank table `[[1,0],[0,1]]`. A triangle gives an
explicit unswitchable interaction graph, with minimum bill nine including
all adapter ranks. See [PROOF.md](PROOF.md) for the universal argument,
literal matrices, chronology, exact threshold reduction and limitations.

This adds an explicit worst-case complexity obstruction beyond the
submodular solver in Ali Romman's [#5783](https://github.com/CrocSwap/integer-mult-bounds/pull/5783).
It builds on David Ganz's [#5693](https://github.com/CrocSwap/integer-mult-bounds/pull/5693)
coframe conjugation and fixed transports. Classical Simple Max Cut hardness
is due to Garey, Johnson and Stockmeyer. Fourier Clifford identities,
graph-cut reductions and signed switching retain their established credit.
The predecessor instances are cited, not audited or replayed.

## Reproduce

From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/transported-coframe-hardness/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B -O research/transported-coframe-hardness/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/transported-coframe-hardness
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/transported-coframe-hardness --check-source-history --check-modes
```

Any CPython 3.12 interpreter with the standard library can replace the absolute
path. The standalone verifier also runs from a Git-free export. It writes
only standard output, including a generated receipt with SHA256 hashes of
all six package files. No committed receipt is hand-authored or trusted.

Expected direct status is `PASS_TRANSPORTED_COFRAME_HARDNESS`. Both registered
commands also require `PASS_REGISTERED_RESEARCH_PACKAGE`. Exact checks cover:

- 1,099 simple labeled graphs on one through five vertices and all 33,866
  coframe assignments, with 7,523 separate decision-threshold comparisons.
- Complete phase-exact logical/physical endpoints for all graphs through
  three vertices, all choices and all 420 basis columns, giving 2,440 scalar
  output equalities over Gaussian rationals.
- Seven invalid-graph rejections, six hypothesis mutants and all eight
  triangle complements. The mutants remove one or both adapter charges,
  remove the logical transport, reduce replication, use the wrong inverse,
  or discard the scalar phase.

The complete-graph minimum bills for one through five vertices are
`0,2,9,22,48`. Finite enumeration corroborates the written reduction; it
does not prove the general complexity theorem by testing.

## Limitations

This is a theorem about the declared rank moment. Ordinary work, precision,
tape movement and storage have no prices in that objective. No complete
physical invoice, source-specific supplier gain, new kappa, selected-frontier
change, all-size multiplication theorem or proof-kernel certificate is
claimed. Independent human and formal proof-kernel review are unclaimed.

The word is constructed for the reduction. Its hardness does not transfer
to the actual 423-choice source, to common-anchor identity transports, or
to unrestricted synthesis of the final linear map. Repeated shears may be
resynthesized in another family; optimizing that changed family is outside
this claim. Structured exceptional sets can still make exact search useful.

## Verifier bounds and diagnostics

The verifier has no recursion, subprocesses, imports of predecessor code or
external inputs. The graph census is bounded by five vertices and ten edges;
the endpoint census is bounded by three vertices, three edges and seven
repetitions. Every failure raises an exception also under `-O`. Every function
is under 60 physical lines. Normal and optimized replay enable warnings as
errors. No separate static analyzer is installed in the local environment.

Power-of-ten managed-runtime deviation, rules 3 and 9: Python fractions,
tuples, iteration and standard-library dispatch allocate during verification.
The fixed finite domains bound live data and call targets; the largest
assignment collection has 32 entries and the largest endpoint state has six
Gaussian-rational scalars. Package hashing reads exactly six named files.
There are no callbacks supplied by inputs. A fixed-capacity implementation
would be a separate port if these limits were expanded.

## Open next questions

Which actual transported coframe incidence graphs have small signed-cycle
deletion sets? This matters because the worst-case obstruction leaves
structured exact cut algorithms useful. Begin by extracting and aggregating
all signed pair tables of one named source word, retaining every fixed
transport and target debit. A specific source-bound instance and its full
physical legality contract are prerequisites. The structured question is
also recorded in [TASK.json](TASK.json).
