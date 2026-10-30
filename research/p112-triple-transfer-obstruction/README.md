# A three-target boundary for support transfer

An exact four-term factorization can fail termwise support transfer to every
characteristic-two field. PROOF.md constructs one using three disjoint
indicators, four non-Fano query rays and one reader that varies inside an
indicator. Arbitrary new coefficients and support deletion cannot repair it.
The proof is algebraic and covers every field; finite field tests corroborate it.

This advances a method boundary, not the multiplication frontier. The complete
literal one-port reader-switch census has 52,080 cases, and every bill exceeds
the original. The best is 20 versus 16, with actual term charges [4,4,4,8].
Appending the untouched indicators gives 228 versus the retained whole bill
224. No supplier or new kappa is claimed.

## Evidence and scope

The four-port witness has query/reader ranks (3,4). Its reader rows force three
pair-span requests and one additional edge-triple request. In characteristic
two, the pair requests force a weighted triangle annihilated by a functional
that is nonzero on the requested target. Thus no same-target four-term
factorization can shrink both actual supports. Transfers that split terms
are outside the claim.

The primary checks the exact four-port identity and all 12,544 entries of the
selected literal witness. It enumerates 1,243,16,807 normalized source cases
over GF2,GF4,GF8, respectively, and finds no completion. The separate checker
also exhausts all 4,096 raw GF2 source arrays, allowing support shrinkage.

Both implementations independently recompute all 52,080 literal bills, their
full excess histogram and the ordered stream digest in RESULT.json. The
primary uses binary label-basis Gram elimination; the separate checker uses
full label spans and annihilator intersections. These are deterministic finite
counts, not runtime measurements or independent human review. The universal
characteristic statement relies on PROOF.md, not the finite field samples.

Four actual optimized CLI corruptions reject a lowered recorded bill, drift
in either pinned input, and replacement of the actual reader by the query in
the tariff. Restoring the bytes passes. Private-copy controls reject overwrite
and a symlink source. Original input/source bytes remain unchanged.

The census fixes w=1 on the target union except for one port of the first
indicator. It does not optimize arbitrary readers, multiple switched ports,
new query rays, more terms or other geometries. This is a scoped negative
result. Failure of characteristic-two transfer alone does not predict a saving.
Physical acquisition, scalar execution, frames, dirty restoration, hosting,
stock, precision, all-size/compiler and complete consumer costs remain open.
Independent human and formal proof-kernel review are unclaimed.

## Reproduction

Use CPython 3.12 and the standard library. Set TMPDIR to an existing private
output directory so test fixtures stay outside the checkout. All three direct
commands work without Git when the package and declared input are present:

```sh
python3.12 -I -O -Werror -B research/p112-triple-transfer-obstruction/verify.py
python3.12 -I -O -Werror -B research/p112-triple-transfer-obstruction/independent.py
python3.12 -I -O -Werror -B research/p112-triple-transfer-obstruction/test_controls.py
python3.12 -I -Werror -B scripts/research_package.py --package research/p112-triple-transfer-obstruction
python3.12 -Werror -B scripts/check_research_commit.py --package research/p112-triple-transfer-obstruction --check-source-history
```

The registered wrapper needs Git provenance. Publication helpers use ordinary
import mode. Official Git-free export:

```sh
python3.12 -Werror -B scripts/export_research_package.py export --package research/p112-triple-transfer-obstruction --ref HEAD --output /chosen/owned/output/package.tar
python3.12 -Werror -B scripts/export_research_package.py check /chosen/owned/output/package.tar
```

Extract the checked archive into a fresh owned directory, and run the three
direct commands from that directory. An externally chosen TMPDIR remains
necessary for disposable controls. No selected cold replay, Lean or Docker
run is needed to check this isolated method-boundary result.

## Sources and credit

Canonical base `6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority revision 6,
task `coverage-law-change`, scope changed to this decoder side result.
SOURCES.json binds the exact canonical label input and includes an authenticated
copy of Tekalign's PR3370 partition fixture. Runtime and proof premises are
source-closed; no pending Git object or network fetch is needed for the science.

[PR3505](https://github.com/CrocSwap/integer-mult-bounds/pull/3505) supplies the
full-matroid sufficient condition;
[PR3506](https://github.com/CrocSwap/integer-mult-bounds/pull/3506) supplies
two-target non-Fano selective transfer;
[PR3475](https://github.com/CrocSwap/integer-mult-bounds/pull/3475) covers
target-span readers. The present nonconstant reader leaves that span, and its
three-target support obstruction is disjoint from the concurrent five-term
pair classification. COMPARISONS.json records exact inspected heads and proof
hashes separately from dependency pins. The proof here is self-contained.

Retain Tekalign's geometry, Philippe Van Velzen's integral/expanded-rank floor,
Arham Tahir's PR3345 application, DreamingOfClouds' decoder model and the
P112/E8/native/compiler/supplier lineage credited by those packages. The
non-Fano characteristic obstruction is standard; no literature priority is
claimed. Nick Petalas. Apache-2.0.

## Engineering constraints

Build the Lever produced two rerunnable census implementations. Prove It Works
requires the actual committed-byte and Git-free export replays, with source
hashes before and after, rather than a metadata-only receipt.

Power of Ten inspection: no recursion; loops are bounded by 112 ports, 32
targets, 16 groups, 9 ambient bits, 52,080 declared cases, 16,807 normalized
field cases, or the fixed 4,096 GF2 arrays. Files are limited to 1 MiB.
Rank dimensions and field domains are checked. Caches enforce a 250,000-entry
limit. No meaningful checks depend on Python assertions, so optimized runs
retain them. Subprocesses have 60-second timeouts and the registered commands
have 120-second limits. All functions are under 60 physical lines.

Rule 3 deviation: CPython allocates managed objects during arithmetic and set
operations. Scope: these three offline scripts. The finite capacities above
bound live work; field sets have at most 512 elements and the census stream
has exactly 468,720 bytes. Context managers close files and remove exclusively
created private fixtures. Verification: both complete implementations and
success/failure controls. Follow-up: replace the bounded caches with fixed
buffers if this checker is moved into a fixed-memory runtime.

Rule 9 deviation: argparse and subprocess use standard-library dispatch.
Scope: fixed CLI options and five fixed local control runs; no user-selected
code is loaded. Controls mutate only owned regular private copies, check owner
and distinct device/inode, use exclusive creation and copy no metadata.
Verification: overwrite/symlink rejection, restored positive CLI and unchanged
source hashes. Follow-up: revisit if a new plugin or dynamic command interface
is introduced. There is no macro generation or dynamic evaluation.

Rule 10: warnings-as-errors, optimized isolated direct runs, strict Ruff checks
and formatting are the affected validation configuration. Ruff 0.17.1 checks
E,F,I,B,UP,SIM,RUF,C4,PIE,PERF,PTH,RET at target py312, with no suppression.
This package changes no repository-wide diagnostic configuration.

## Open next questions

The structured question in TASK.json asks for an exact cheaper literal
factorization with a changed support mechanism. The first step is to provide
its coefficients and complete actual-reader tariff. The present one-port
family loses by at least four, so it does not justify a dependent native
construction round. Arbitrary-reader savings and all physical consumer costs
remain blockers. This family is narrowed; another seed within the same
52,080-case domain has no remaining search obligation.
