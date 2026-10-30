# A finite-depth tail bound for the direct-flow leaf walk

This scoped proof gives the historical raw-p7 leaf law an explicit
finite-depth exponential envelope. For all G>=11000,
0<=delta<=log(5), and x>=0,

    Pr(Y_G>=x | S_G<=G log(5)+delta) <= min(1, 5 exp(-lambda x)).

Here Y_G=G log(5)+delta-S_G and lambda=t-alpha is the tilt gap defined in
[PROOF.md](PROOF.md). The bound on clipping the deficit at L>=0 is

    E[(Y_G-L)_+ | survival] <= (5/lambda) exp(-lambda L).

The same bound controls the resulting error in mean actual leaf depth,
including the independent unconditioned terminal rank. The proof also gives
E[Y_G 1_{Y_G>=L} | survival] <= 5(L+1/lambda) exp(-lambda L).

This partially answers open question 2 of Ryanson Jonathan / pinterbanget's
[PR #4467](https://github.com/CrocSwap/integer-mult-bounds/pull/4467).
DLamdata's [PR #6118](https://github.com/CrocSwap/integer-mult-bounds/pull/6118),
head `6310550e932de70243fc2aaab6f4885688b6fe21`, supplies the qualitative
saturation theorem and exact leaf-measure identification. Those predecessor
results are cited, rather than audited or claimed here. The new step uses
Berry–Esseen and bounded-variation integration to replace an unspecified tail
constant and onset by explicit finite values.

This does not establish a Bahadur–Rao asymptotic or its error term, a rate of
convergence to the exponential law, stable full-flow shares, a numerical
induction ceiling, supplier admission or a new kappa. The selected PR6030
record and its five assumptions are unchanged. This is historical compiler
side work, not a selected-frontier improvement.

## Reproduce

Python 3.12, standard library only. From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B research/direct-flow-finite-tail/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/direct-flow-finite-tail
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/direct-flow-finite-tail --check-source-history
```

Other reviewers can replace the interpreter path with their CPython 3.12.
The principal marker is `PASS_DIRECT_FLOW_FINITE_TAIL`. Each direct run prints
a generated JSON receipt binding all six package files by SHA256. It writes
nothing to the checkout. The registered normal and optimized commands repeat
the exact numerical gates and rejecting controls with no dependence on Python
assertions. Source laws are parsed as literals from the authenticated pinned
file; no predecessor code executes.

The certificate encloses only the coarse hypotheses needed by the new bound,
not the predecessor's high-precision result. Logarithms use 48 terms of the
atanh series after power-of-two reduction. Exponentials use 32 terms after
scaling by 16, with geometric remainder bounds and four outward-rounded
squarings. All acceptance decisions use integers or rational intervals.
Finite Bernoulli fixtures separately check the tilt ratio and clipping
identity at atoms. The written proof and the external Berry–Esseen theorem
carry the universal probability claim; finite fixtures do not replace them.

## Verification boundaries

The exact source closure is in [SOURCES.json](SOURCES.json). The base is
`721c03822c421b7f7fcbb2598993b947c4d88419`, priority revision 8.
The source question and advisory claim are recorded in [TASK.json](TASK.json).
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19241861)
precedes substantial work. PR6118's separate power-tariff follow-up concerns
asymptotic moments, while this result gives a finite-depth tail envelope.

No selected cold replay, full historical flow replay, native or physical
program, Lean proof or complete multiplication theorem is run. The classical
Berry–Esseen inequality and elementary pi bounds are external mathematical
inputs. Independent human and formal proof-kernel review are unclaimed.

The verifier uses bounded nonrecursive loops. It reads four fixed source
records, parses an authenticated source with at most 100 top-level statements,
and processes two supports of nine ranks no larger than 121. The finite-word
fixtures stop at depth eight, with at most 256 words in a fixture. Functions
stay below 60 lines. Every gate fails through an explicit exception, including
under optimized Python. The JSON serializer has one fixed callback target.

Power-of-Ten rule 3 has a managed-runtime deviation in `verify.py`: Python
allocates Fraction integers and collections during execution. Fixed input
inventories, fixed series lengths, 128-bit outward rounding and the depth-eight
fixture cap bound the live workload. Source files are capped at one million
bytes. The registered normal and optimized checks exercise this bounded path.
A fixed-memory implementation would require a different arithmetic runtime;
no such implementation or physical resource claim is made. Diagnostics use
Python development mode and warnings as errors in local verification.

## Open next questions

Can an effective nonlattice interval local-limit bound give an explicit
*decreasing* error for the distribution or mean relative to its exponential
limit? This would quantify the onset of saturation. A first step is to pair
such a remainder with the finite tail envelope proved here. The missing input
is a quantitative local-limit estimate, not another tail-constant search.

## Credit

The finite-depth envelope and explicit truncation constants are produced by
Nick Petalas. Ryanson Jonathan / pinterbanget supplied the fixed law and the
explicit-constant question in PR4467. DLamdata supplied the saturation theorem
and exact leaf observable in PR6118. zxv supplied the direct flow, Cinna Davis
the refined induction, and Jacob Alan Sussman the lockstep compiler. The
Berry–Esseen inequality, change of measure and bounded-variation estimate are
classical. Predecessor files and credit lines remain unchanged. Apache-2.0.
