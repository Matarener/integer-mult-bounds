# Sharp actual-body borrowing cutoff

For the prescribed one-factor GL64 reserve at the actual body depth, every
original width **e>=245767** has a legal covering plan for every prime q>2^80.
The same cutoff is sharp for strict-volume padding. At e=245766 the certified
prime **q=213*2^80+1** admits neither plan. [PROOF.md](PROOF.md) gives the
all-width argument, exact depth intervals and prime witness.

The parameters are the existing w=ceil(e^(17/10000)), n=floor((e-k)/w),
2k<e, n>=64, D(n)=1+D(42 floor(n/64)) above 63, and
S_d=9475*(28416*|GL64(F_q)|*q^(4096(w-1)))^d at positive depth.
Covering means S<=q^k. Strict-volume means S<2q^k.

PR3486 and PR3523 already supply the respective selectors. This package adds
their universal sharp existence threshold. The original-width 311311 theorem
uses a different, repeated-Q stock at depth D(e) and remains unchanged.
The numerical difference is 65544 digits. It is not a runtime speed factor,
an actual selected bootstrap-stage coefficient, supplier admission or a kappa
improvement. Physical composition retains its inherited premises.

## Reproduction

Use standard-library CPython 3.12 from the repository root:

```sh
python3.12 -W error -B scripts/research_package.py --package research/actual-body-fit-cutoff
python3.12 -W error -B scripts/check_research_commit.py --package research/actual-body-fit-cutoff --check-source-history
```

The registered commands also work in a Git-free export with the nine explicit
source files declared in VERIFY.json:

```sh
python3.12 -I -W error -B research/actual-body-fit-cutoff/verify.py
python3.12 -I -O -W error -B research/actual-body-fit-cutoff/verify.py
python3.12 -I -O -W error -B research/actual-body-fit-cutoff/independent.py
python3.12 -I -O -W error -B research/actual-body-fit-cutoff/controls.py
```

Set TMPDIR to an existing owned external directory for the controls' temporary
byte copies. No command writes into the published package. The primary checks
all proof-input hashes and the complete typed RESULT.json. Acceptance checks
remain active with assertions disabled. The separate forward-depth census
imports neither cutoff.py nor RESULT.json. It checks every e from 1 through
1048575 at the certified prime, with separately enclosed covering and strict
thresholds. Each predicate has 802809 fitted widths and last failure 245766.
The complete decision SHA256 is
`af7b7197d5977772fdd5a6a8339bf365cf3dbab317d63e8dc75b8791b6cc15f3`.
Its finite coverage corroborates the proof; the infinite tail
rests on the written dyadic induction. Controls execute valid and corrupted
public CLIs in optimized Python, including changed sources, duplicate and
floating-point receipts, a bad prime witness and a changed child rank.

## Scope, sources and credit

Base is canonical 20ecf2891d80b5acf18d980b2164fb44ea7faa90, priority revision 6.
This explicitly changes the selected-stock-envelope card to the concrete
replacement caller's actual-body reserve. Every actual selected bootstrap
coefficient remains unresolved. The baseline orientation command encountered
an omitted selected complex package in sparse checkout; no full selected replay
is claimed. [TASK.json](TASK.json) preserves the original card and changed scope.

All runtime sources used by these checks are package-local Python standard
library code. The nine pinned external files are mathematical/source-boundary
inputs, authenticated at their canonical-main versions. No foreign Git object,
pending archive or network resource is needed for scientific replay. No frozen
predecessor changes. Exact input bytes, blobs and SHA256s are in SOURCES.json.

Credit Nick Petalas's PR3486 body-depth selection and PR3246 one-factor guard,
Hiroki Kumazaki's encoded-selector lineage, PR3503/3523 strict-volume work,
Tekalign's PR3264 consumer binding, Jose Manuel's PR2234/2809/2899 caller and
width definitions, David Arias's PR2753 recursive caller, and Aakash's sharp
original-width threshold, dyadic-tail proof and prime certificate. Ross
Richardson's stronger dual-format contract remains separate. Retain the
DreamingOfClouds/eumemic, source527, alephnan and selected BIT/geometry/assembly
lineage credited in the unchanged source files. This contribution is the new
cutoff and proof, not their reserve, selectors, padding or consumer results.

## Open next questions

The useful next step is the selected-root physical contract and full paid
invoice already identified by PR3564. Start with the actual selected coefficient
parser, one complete nonterminal return and its source/index/stock ownership.
This matters because arithmetic fit alone cannot admit the supplier. The full
GL64 payload, universal caller/refinement and full-cover premises remain blockers.
No larger constant search is justified by this cutoff alone. Independent human
and formal proof-kernel review are unclaimed; no selected frontier changes.
