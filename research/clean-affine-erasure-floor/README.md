# Clean copying and erasure cannot beat the binary-affine tariff

This scoped algebraic proof extends Gareth Davidson's [#1333](https://github.com/CrocSwap/integer-mult-bounds/pull/1333). Its exact binary-affine paid-call floor survives arbitrary clean helpers, free scalar copying and reset, discarded garbage, and a changing number of live registers:

```
minimum paid calls = sum_j rank_F2([A_j-I | b_j]).
```

The paid alphabet is unchanged. Each call is `I+([g]+1)uv^T` over the full formal algebra `F2[AGL_d(F2)]`, with `v^T u=1` and `rank([A_g-I | b_g])=1`. Every free operation is an arbitrary rectangular binary scalar map. The retained outputs must implement the independent target maps `g_j(x)=A_j x+b_j` on arbitrary inputs. Helpers need not return to zero, garbage may be discarded, and any supplied dirty inputs must not affect the retained answer. The schedule is finite and fixed.

The new [proof](PROOF.md) avoids inverse normalization. For a rectangular formal matrix `M`, define

```
delta(M) = rank(H(M) - epsilon(M) tensor I),
delta(UV) <= delta(U) + delta(V).
```

Here `H` is the homogeneous affine representation and `epsilon` is augmentation. Every free rectangular scalar map has defect zero; every paid call has defect one. The selected output rows have defect equal to the displayed target bill. This proves the enlarged-model lower bound. The matching upper construction is cited directly from #1333, PROOF.md Section 4; no predecessor census or verifier is replayed.

This closes a clean/erasing-workspace loophole for this specified alphabet. It is a side result under `bit-new-register-model`, with changed free-operation and output hypotheses. It supplies no physical supplier, recursive moment, new kappa or complete multiplication theorem. The selected frontier is unchanged.

## Reproduction and evidence

From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/clean-affine-erasure-floor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/clean-affine-erasure-floor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/clean-affine-erasure-floor
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/clean-affine-erasure-floor --check-source-history
```

Substitute another CPython 3.12 executable elsewhere. The standard library suffices. Verification writes only a generated JSON receipt to stdout, bound to the six package source hashes. The direct marker is `PASS_CLEAN_AFFINE_ERASURE_FLOOR`; the runner and publication preflight print `PASS_REGISTERED_RESEARCH_PACKAGE` and `PASS_RESEARCH_COMMIT_BYTES`.

The finite corroboration checks 74,384 compatible rectangular products, 682 free scalar maps, 315 paid factors, 48 clean/erasing circuits, 2,304 faithful basis columns, 192 omitted-call controls and eight boundary controls. It exhausts every compatible pair of rectangular matrices with one or two rows/columns over `F2[C2]`. It separately checks all binary scalar maps of shapes one through three and every allowed paid factor through three roles in the dimension-two affine group. New clean copy/compute/reset/discard circuits use two arbitrary data inputs, two zero helpers, four paid calls and two retained outputs. Full formal multiplication and a separate set-based faithful regular-action interpreter check their endpoints, including every group/data basis column. Single-call omissions, dirty-helper leakage, illegal free addresses, rank undercharging, a nonfaithful representation kernel and invalid domains are controls. The proof covers unbounded finite parameters; this finite domain does not enumerate arbitrary circuit words.

The card's first working command, `scripts/research_selected_baseline.py`, passed with `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`. This was orientation only. No selected scientific replay, native/tape execution, Lean or Docker check was run. Hosted CI is separate from local evidence.

## Implementation scope

The checker has no external executable, dynamic imports, recursion or filesystem mutations. Its finite group bound is 24, scalar width is at most four, represented matrices have at most twelve rows/columns, and all enumeration products have fixed limits visible in the code. All mathematical acceptance checks remain enabled under `-O`.

Power of Ten rule 3 deviation: CPython and its standard library allocate managed objects during verification. This six-file standalone checker bounds live mathematical data by the complete 292-entry small-matrix inventory and the fixed four-role/24-element domains; it streams composition checks and faithful basis inputs. Runtime/library allocation is not statically controlled. Follow-up is required if these limits are enlarged. Other checks include a separately enumerated row-span rank oracle, explicit domain rejection, functions below sixty lines and warning-strict normal/optimized execution. No standalone linter is installed in this environment; AST inspection and both interpreter modes are the available diagnostics. No repository-wide diagnostic configuration is changed.

## Sources and overlap

[SOURCES.json](SOURCES.json) pins the unchanged predecessor README and proof at canonical main `de5ec2e7a6074068452f45b1a191b5c72832df4a`. They are cited inputs, not scientific replay targets. [TASK.json](TASK.json) records the changed hypothesis, exact claim and bounded overlap coverage. Live PRs, recent handoffs, local question reservations, merged-PR searches and all-main README terms were checked before claiming and before publication. These searches do not exclude unpublished work or establish literature priority.

Credit Gareth Davidson #1333 for the binary-affine model, homogeneous displacement method, exact original tariff and direct attaining factorization. Its eumemic #288, Ali Romman #468, David Govea #720 and classical rank/reflection lineage retain credit. The new contribution is the rectangular augmentation-defect lower bound and its clean/erasing boundary application. This contribution was produced by Nick Petalas. Independent human and formal proof-kernel review are unclaimed. Apache-2.0.

## Open next questions

Can a physically justified free operation escape this defect bound while its complete cost remains favorable? Start with one actual native address-dependent operation and compute its represented defect and complete input/output invoice. The current theorem excludes only scalar free maps; physical legality, movement, ownership, precision and recursive charges remain blockers. Adding a nonzero-defect address operation at zero price changes the model rather than supplying an improvement.

Can the same rectangular invariant give a sharp tariff for another specified group representation with clean/erasing workspace? Start with a cited direct construction whose representation-rank bill is attained, then state the retained output contract. A matching upper construction is necessary; a generic lower bound alone is not an exact tariff.
