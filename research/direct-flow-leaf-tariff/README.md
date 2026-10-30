# Exact power-tariff asymptotics for direct-flow leaves

Scoped proof produced by Nick Petalas. No new κ.

For the fixed historical raw-p7 leaf measure of Ryanson Jonathan's
[PR #4467](https://github.com/CrocSwap/integer-mult-bounds/pull/4467), this
package derives the full power-tariff asymptotic from the tilted local-limit
framework in DLamdata's
[PR #6118](https://github.com/CrocSwap/integer-mult-bounds/pull/6118)
(`6310550e932de70243fc2aaab6f4885688b6fe21`). This extends that saturation
result; its certificate is not rerun or audited here.

Write `Z(s)=sum_r P[r]r^s`, `a=log5`, `mu(alpha)=a`, `lambda=t-alpha>0`,
`sigma^2=(log Z)''(alpha)`, and `N=121 exp(Ga+delta)`. Define

```
M_G(u,delta) = sum_leaves ell^(t+u) / (N^u sum_leaves ell^t),
A(u) = 121^(-u) Z(t+u)/Z(t),       v=lambda+u.
```

Multiplicities are included in both sums. The new theorem is

```
v > 0:  M_G -> A(u) lambda/v
v = 0:  M_G ~ A(u) lambda sigma sqrt(pi G/2)
v < 0:  M_G ~ A(u) lambda sigma sqrt(2 pi G) exp(-v delta) R(u)^G,
        R(u)=Z(t+u)/Z(alpha) exp(-v a) > 1.
```

Each statement is for a fixed real u, uniformly over `delta in [0,log5]` in
the fixed-depth family: keep G at the upper endpoint. Actual integer ranks use
`G=floor(log_5(N/121))`, hence `delta in [0,log5)`.
See [PROOF.md](PROOF.md) for the exact finite quotient, the nonlattice
local-limit dependency, critical CLT argument and second change of measure.
In particular, convergence of the mean log-depth does not imply that all
power tariffs converge. The exact threshold is `t+u=alpha`.

## Evidence and reproduction

The infinite-parameter result is a written scoped proof. The standard-library
verifier checks its new finite factorization and tilted quotient using exact
rational arithmetic. It imports no predecessor verifier and computes no
predecessor root, saturation value or full-flow result. It authenticates two
main-branch input files and reads their literal P/M inventory without executing
them.

From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/direct-flow-leaf-tariff/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/direct-flow-leaf-tariff/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/direct-flow-leaf-tariff
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/direct-flow-leaf-tariff --check-source-history
```

Other hosts can use their CPython 3.12 executable. Direct replay prints
`PASS_DIRECT_FLOW_LEAF_TARIFF_FINITE_IDENTITIES`: 15 finite fixtures,
225 moment identities, 450 tilted-quotient identities, 210 second-measure-change
identities, 10,191 accepted ordered
prefixes counted across fixtures, and eight rejecting controls. The five
semantic controls omit the terminal factor, truncate the terminal rank, reverse
the power sign, drop the lockstep offset or reverse the tilt shift. Three
boundary/source controls reject excessive depth, an empty barrier domain and
corrupted source bytes. Finite exponent choices are integral so these checks
are exact; they do not certify the asymptotic theorem by enumeration.

All loops are bounded by depth four, nine paid ranks and fixed fixture lists.
The largest ordered-word enumeration has 9^4 tuples. Python's managed allocation
is a Power-of-Ten deviation, with live collections bounded by these fixed
inputs. If a later version accepts variable depth or inventories, it must
replace these fixed bounds with enforced resource limits before reuse.
Functions are below 60 lines, no recursion, callback dispatch or dynamic code
execution is used, and normal/optimized warning-as-error runs exercise the same
explicit checks. Ruff, mypy, Pyright and Pylint are unavailable in the local PATH
and environment; stronger static-analysis coverage is unclaimed. A future
language/toolchain change should add its available diagnostics to VERIFY.json.
No generated receipt is committed or hand-written.

## Limitations

The local-limit theorem is a cited classical mathematical dependency, following
#6118's specialization; independent human and formal proof-kernel review are
unclaimed. The theorem uses any fixed t>alpha and inherits #6118's identification
of the raw-p7 crossing exponent for that application. It does not reverify that
identification. No finite-depth rate or practical rank threshold is supplied.
Relative source/boundary/leaf masses, a complete direct-flow invoice, native
operators, compiler realization, physical costs and selected supplier admission
are unproved here. The historical raw-p7 law is not the selected #6030 invoice;
all five selected framework assumptions remain.

## Open next questions

- Determine the full source/boundary/leaf-normalized exit coefficient, using
  compatible tilted measures and retaining the offset. The missing non-leaf
  asymptotics and relative masses block a complete refined-induction ceiling.
- Give explicit finite-depth errors for these three regimes. Start with a
  quantitative interval local-limit bound for the fixed log{2,3,5} support;
  recurrent finite-support phases prevent assuming strong nonlattice decay.

The relevance, first steps and blockers are also in [TASK.json](TASK.json).

## Credit

New theorem and verifier produced by Nick Petalas. DLamdata (#6118) supplies the
saturation framework; Ryanson Jonathan / pinterbanget (#4467/#4465/#4459)
supplies the leaf law and diagnostics; zxv (#4436) supplies the direct flow;
Cinna Davis / 1337isnot1337 (#4405) supplies refined induction; Jacob Alan
Sussman supplies the lockstep compiler; Stone supplies the classical local
limit theorem. All predecessor files and credit remain unchanged. Apache-2.0.
