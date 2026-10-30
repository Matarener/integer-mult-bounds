# Exact star budgets for prescribed targets with one odd cycle

Scoped uniform proof with finite exact corroboration. In the binary signed
two-port observation model of [Sam Sung's PR #669](https://github.com/CrocSwap/integer-mult-bounds/pull/669),
allow every vertex star and the empty star. If the prescribed target graph
has exactly one cycle in total, and that cycle is odd, its exact deletion
budget is

```text
delta_+(T) = 2p(p-1) - r - floor((2p-r+1)^2/4),  r = |T|.
```

Attached trees, other tree components and isolated vertices are allowed.
The theorem holds for every p >= 3. A five-cycle on six vertices needs
exactly six deletions; the source's triangle formula is the r=3 special
case. Within this class, the optimum depends only on p and r.

The source already supplies the general nonzero-constant lower bound and
the triangle optimum. The new step is a balanced root construction that
attains that bound for the whole odd-unicyclic class, despite the removed
perfect matching. [PROOF.md](PROOF.md) supplies the uniform argument and
literal vector-valued decoder coefficients. Predecessor results are cited,
not audited or replayed as the contribution.

This is a scalar observation result. It supplies no paid supplier, physical
frame schedule, helper preparation, dirty restoration, precision/tape bill
or new kappa. The selected result and its five framework assumptions remain
unchanged. Independent human and formal proof-kernel review are unclaimed.

## Evidence

The independent small-instance oracle enumerates all 4,096 retained graphs
at p=3, computes their observation row spaces, and optimizes every target
set by a superset transform. All 864 eligible target sets agree with the
formula and the constructed coefficients. By target count r=3,4,5,6 there
are respectively 8,72,288,496 sets. The matching obstruction triggers the
root replacement on 128 of these sets.

The constructor also checks 2,704 fixed fixtures at p=4,...,16, covering
every odd cycle length from 3 through 31, attachments and separate tree
components. These are fixture cases, with repetition allowed, rather than
a census of all larger target graphs. Every one of their 101,231 retained
input columns has its literal required coefficient.

Controls reject five invalid target inputs, three decoder mutations and
all twelve single-edge restorations of the displayed p=4 triangle witness.
The component-concentration inequality is also checked on 1,600 integer
pairs. These finite checks corroborate the written proof; they do not
replace its all-size quantifiers. The verifier imports no predecessor code.

## Reproduce

From the repository root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/odd-unicyclic-star-budgets/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/odd-unicyclic-star-budgets/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/odd-unicyclic-star-budgets
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/odd-unicyclic-star-budgets --check-source-history
```

Another CPython 3.12 executable can replace that local interpreter path.
The marker is `PASS_ODD_UNICYCLIC_STAR_BUDGETS`, followed by enumerated
coverage and SHA256 hashes. `--receipt /absolute/new/file.json` writes a
new source-bound receipt outside the package and refuses overwrite.
The default verifier writes nothing. Registered normal and optimized
commands each have a 120-second limit.

[SOURCES.json](SOURCES.json) pins the exact main-branch predecessor note;
the shared metadata runner authenticates its working bytes and historical
provenance. The direct mathematical checker needs only this package and
does not consume the predecessor's implementation. The original catalogue
card and selected record are retained as historical provenance. The changed
scope from a native-register construction to an algebraic side result is
explicit in [TASK.json](TASK.json).

## Open next questions

What is the exact C+ budget for a prescribed forest with r>p? The source
gives a C- matching formula and a uniform no-benefit result for C+ when
p>=6 and r<=p. Start with one p>=6 forest above that range and compare
the matching optimum with the nonzero-constant bipartite bound. A forest
does not force a nonzero empty-star coefficient, so both decoder types
must be considered. This question is left unclaimed.

## Engineering limits

All scientific loops have explicit finite domains. Constructor fixtures
validate 2<=p<=20, giving at most forty vertices and 760 edges. The largest
exhaustive arrays have 4,096 entries. The proof has no such p limit.
Functions are below sixty lines; all checks use exceptions and remain
active under optimization. No recursion or subprocess is used.

Power-of-Ten rule 3 has a managed-runtime deviation: CPython and its standard
library allocate during replay. Live collections are bounded by the above
input limits, receipts contain bounded aggregates, and the shared runner
enforces the timeout. Extending the finite domain requires reassessing
those capacities. Rule 9 has a bounded test-only dispatch deviation:
rejection controls call the local analyze and endpoint functions through
fixed lambdas. The target set of those callbacks is explicit and contains
no external code. Warning-strict normal and optimized execution provide
the available interpreter diagnostics; no external linter is required.

## Credit

This contribution was produced by Nick Petalas. Sam Sung /
the-missionary-company retains credit for PR #669's observation model,
graph-target reductions, inherited lower bound and triangle result.
The graph-incidence bridge retains Martinez-Bernal, Valencia-Bucio and
Villarreal's credit. Joel Pulikkan / GamingPuzzled, icekylinx and eumemic
retain the paired-cube lineage. The new attainment proof, constructor and
independent finite oracle are the contribution here. New work is Apache-2.0.
