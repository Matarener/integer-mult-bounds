# Sharp integer stock coefficient for the selected BIT caller

For both existing selected BIT stocks, **6741 is the least integer C** such
that `log_q S(e,w) <= C w log2(e)` for all independent integer widths
`e,w>=1` and every prime `q>2^80`. The same least integer works for the
conventional `C w (1+log2(e))` envelope. The earlier source-bound allowance
is 6748. This is a numerical reserve theorem, with no new kappa.

The [proof](PROOF.md) keeps the actual stocks and their different contracts:

```
N = |GL_64(F_q)|, H=q^(4096(w-1)), b=28416 N H, Q=9475,
K=269241600 N H=Q b,
D(e)=0 below 64; otherwise 1+D(42 floor(e/64)),
S_old=K^D,
S_guard=1 at D=0; otherwise Q b^D.
```

The exact certificate `2^2631>21^599` proves the 599/364 depth bound.
The full packet costs less than `4096w+29/80` q-ary digits per level, and
`599*327709/(364*80)=6741-229/29120`. No logarithm approximation enters
acceptance.

For the reverse direction, the exact inverse-depth threshold at depth
262144 has 159307 bits. At w=1, for every admissible prime, both stock
logarithms exceed `1073741824`, while `6740 log2(e)<1073729180`.
Coefficient 6740 fails by a strict margin greater than 12644. It also fails
with `1+log2(e)`. The width is specified by its exact recurrence and hash
in [RESULT.json](RESULT.json), without materializing the immense stock.

The result does not characterize an optimal real coefficient. The explicit
w=1 sharpness witness does not satisfy a bootstrap coupling `w=ceil(e^s)`
for positive s. The upper theorem includes those widths, but restricted-domain
sharpness is unclaimed. `ceil(log2(8*6741))` remains 16, so no changed cutoff
or fit guard follows. No selector, caller, physical consumer, supplier or
selected-frontier record changes.

## Reproduce

Use standard-library Python 3.12 from the repository root:

```sh
python3.12 -W error -B scripts/research_package.py \
  --package research/selected-stock-sharp-integer
```

Standalone commands also work from the committed Git-free package export,
which includes its five declared source inputs:

```sh
python3.12 -I -O -W error -B research/selected-stock-sharp-integer/verify.py
python3.12 -I -O -W error -B research/selected-stock-sharp-integer/independent.py
python3.12 -I -O -W error -B research/selected-stock-sharp-integer/test_controls.py
```

The primary authenticates every live source and compares the complete typed
receipt. It checks all 42 child ranks at 131073 finite widths, 32 threshold
boundaries and the exact large witness. The separate implementation imports
no primary code or receipt. It uses an alternate threshold recurrence and a
forward contraction to reconstruct the same width. The written argument
supplies the all-width theorem; finite checks support it.

Actual optimized CLI controls accept a Git-free source export and reject
changed/missing inputs, Boolean/duplicate-key receipts, a 6740 producer and
an incorrectly rounded threshold producer. Replays write no package files.
Temporary control copies use TMPDIR. Set TMPDIR to an owned external directory
when desired. The [engineering record](ENGINEERING.md) states replay capacities
and remaining platform limits.

## Sources, delta and limits

Canonical base is `6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority revision 6.
[SOURCES.json](SOURCES.json) binds the exact selected assembly, David Arias's
PR2753 proof and NODE implementation, jwr's PR2888 lcm-stock envelope and
Nick Petalas's PR3246 current-guard divisor theorem. Those predecessor proofs
and notices are unchanged and retain their original credit. No predecessor
executable is imported. The contribution is a sharper bound and an explicit
integer-optimality witness for those fixed source contracts.

Adam Gall's PR2084 supplied the ordinary BIT parent-stock implication;
PR2120 supplied its earlier 28/17 depth certificate. Josie Elliston's
PR1956/1965 and ToikY's PR1990 distinguished reserve coefficients from
cutoff headroom. Jose Manuel supplied the preceding selected caller and
physical contract, Ross Richardson the full-format distinction, and
DreamingOfClouds/eumemic the selected BIT lineage. Rohan Arun's PR1094
assembly and Jeremy Kothe's PR1087 assembler retain their original credit.

This package inherits constant atom width, full-cover realization, fresh
fields, completed leaves, pointwise restoration and the actual all-size
caller premises. It does not establish physical time, placement, precision,
the complex m=73 stock, complete supplier admission or outer transfer. No
full selected cold replay, formal proof-kernel or independent human review
is claimed. The introductory baseline probe stopped on omitted sparse
selected-package paths; it is not a passing selected replay.

## Open next questions

The structured questions in [TASK.json](TASK.json) retain two boundaries.
First bind the smaller current-guard stock to an actual odd-prime selector
and complete consumer return, including physical-format constraints. A
sharper logarithm alone changes neither interface nor its costs. A possible
coupled-width optimization would need a concrete stage and a decision it
could change; this result does not justify another constant search.

Nick Petalas. Apache-2.0. Independent human and formal proof-kernel review
are unclaimed.
