# Exact local invoice and conditional consumer stop

The in-place entrance completion reduces scalar ADD work and improves the
native-only concave tariff. It still fails the retained five-forward/four-dual
consumer model after substituting its **newly constructed** profile. This is a
local construction with a conditional stopping result; it supplies no improved
supplier or selected bound.

Counts below are the source-derived outputs of [invoice.py](invoice.py), the
actual wrapper census in [native.py](native.py), and the serialized
[PROGRAM.json](PROGRAM.json). Source hashes and predecessor provenance are in
[SOURCES.json](SOURCES.json). The cost units remain separate throughout.

## Scalar work, return, and native children

Each field has 512 Gaussian entries, hence 1,024 real components. A unit
Gaussian bank ADD/SUB therefore costs 1,024 real ADD/SUB operations. Integer
coefficients are expanded into repeated unit operations. Each fractional source
read is implemented by exact componentwise halving, the signed ADD, and source
restoration by doubling before the next original event. A quarter read uses two
half passes and two restoring double passes. These are separately charged.

| Scope | Unit Gaussian bank ADD/SUB | Real ADD/SUB | Exact real halves | Restoring real doubles |
| --- | ---: | ---: | ---: | ---: |
| Removed original events | 1,364 | 1,396,736 | 98,304 | 98,304 |
| New entrance completion | 887 | 908,288 | 105,472 | 105,472 |
| Original full word | 4,353 | 4,457,472 | 2,750,464 | 2,750,464 |
| Changed full word | 3,876 | 3,969,024 | 2,757,632 | 2,757,632 |

Thus the substitution saves 488,448 scalar real ADD/SUB operations and adds
7,168 exact halves and 7,168 restoring doubles. The 787 weighted ADDs in the
factor notation are **887 unit operations**: 247 for dirty preconditioning,
393 for gathering, and 247 for scattering. Exactly 103 Y sources are halved
and immediately restored; Y1 is unused by this completion.

| Scope | Native calls | Native rank mass | Coordinate C pairs |
| --- | ---: | ---: | ---: |
| Removed original events | 473 | 889 | 227,584 |
| New entrance completion | 145 | 889 | 227,584 |
| Original full word | 2,070 | 3,542 | 906,752 |
| Changed full word | 1,742 | 3,542 | 906,752 |

The new profile is $52H_1+93H_9$. The 4,027-event retained projection and
1,238-operation prelude together have 5,265 serialized operations. Removing
the old complement removes 104 whole-bank sign events; 104 such signs remain
in the projection and require their own 106,496 real negations. All eight
original private-C zero/erase lifetimes remain. The prelude adds no private
Gaussian bank: its eight dirty accumulators are required X outputs, and their
original contributions are preserved. Literal native-pair arithmetic is not
included in the scalar ADD table.

## Wrappers and widths remain charges

The actual 145 native occurrences have 290 monomial wrappers. Their 148,480
address entries form 97,840 cycles. Direct cycle permutations require 50,640
Gaussian SWAPs; the recorded phases additionally require 61,440 real SWAPs and
148,480 real negations. A Gaussian SWAP exchanges two Gaussian entries, hence
two pairs of real components. Its two-real-SWAP lowering would total 162,720
real SWAPs including phase rotations.
These are explicit operation inventories, not free relabelings or a completed
machine tariff. The old omitted wrappers are outside this comparison; a
difference of complete physical bills is not claimed.

Let $H_X$ bound real and imaginary components after the singleton-to-empty
entrance maps, and let $H_Y$ bound the **actual unhalved** common-frame Y
fields. The fixed schedule's scalar row envelope is

$$
\max\{8H_X+95H_Y,\ 11H_X+64H_Y,\ 12H_X+49H_Y,\ 14H_X\}.
$$

Consequently $103H$, with $H=\max(H_X,H_Y)$, is a uniform bound. The
equal-bound maximizing row has weights $(8,95)$ at prelude operation 929,
equivalently scalar operation 877; indices are zero-based. Its
$8H_X+95H_Y$ value alone is not a uniform bound for independently varying
inputs. Entrance/exit native growth and signed-floor temporaries require
additional bounds.

The dense physical fixture's observed peak, 11,232, measures stored field
values after complete operations. It does not measure internal native-pair
temporaries or prove a universal width allowance. Python oracle arrays,
dictionaries and temporary vectors are verification storage, not claimed
physical workspace.

## New profile substituted into the named consumer

Jose Manuel's original stopping insight and Vasek's
[PR2744 consumer audit](../p104-consumer-budget-audit/README.md) concern fixed
predecessor profiles. Their theorem does not automatically cover this
resynthesis. `invoice.consumer_stop` performs a new substitution, retaining
the same explicit coverage assumptions:

- Width $m=73$, $W=832$ original families, five fixed forward calls and four
  calls of this newly constructed dual word.
- Favorable persistent credit $P=3014$ per call, leaving
  $I=72\cdot832-9\cdot3014=32778$ paid coverage units.
- Up to 416 integer rank units forgiven per dual, with the new decomposition
  otherwise fixed; other positive children have rank at most 73.
- Every auxiliary bank adds 73 paid coverage units and one family; all other
  charges are nonnegative.

The unchanged forward mass is 3,070. The nine-call profile, after favorable
H1 forgiveness, has H1 count 9,680 and total mass 27,854. The certified bounds

$$
\log 73>4,\qquad \log(73/r)>2\quad(2\le r\le9)
$$

give the new slope

$$
L=4(9680)+2(27854-9680)=75068.
$$

For every finite number $B\ge0$ of fully paid auxiliary banks and primitive
saving $0<a<1$, the favorable moment satisfies

$$
M_B(a)>1+\frac{75068a-104}{73(832+B)}.
$$

At the retained benchmark

$$
\kappa=\frac{836330098538459}{500000000000000000},\qquad
75068\kappa-104=
\frac{2695406959271260053}{125000000000000000}>0.
$$

With no auxiliary banks this gives the exact lower bound

$$
M_0(\kappa)>
\frac{7594695406959271260053}{7592000000000000000000}>1.
$$

The retained transfer requires primitive saving greater than this tested
multiplication saving. The lower bound increases with $a$, so this consumer
fails already under the more favorable test. Additional resynthesis, changed
coverage, or a different consumer requires a new calculation.

The native-only gain is real: concavity gives the old omitted tariff at least

$$
421+52\,9^s,
$$

while the new tariff is $52+93\,9^s$. Their difference is at least

$$
41(9-9^s)>0\quad(0\le s<1),
$$

with equal rank mass at $s=1$. This gain does not discharge the consumer's
remaining coverage or physical charges.

## Obligations and stopping decision

| Boundary | Established here or explicitly inherited | Remaining obligation |
| --- | --- | --- |
| Local operator | Exact scalar matrix, dirty preservation, source return, 53 native certificates and dense literal comparison | Actual supplier invocation with these fields |
| Source domain | Local 93 dirty fields in B9 and Y in 4B9; common full-word sufficient domain: 104 Y in 4B9, 78 N in 2B9, 176 other inputs in B9 | Paid preparation from a named upstream input |
| Storage | No added Gaussian bank; eight inherited private-C lifetimes retained | Owners, allowed source mutation, component scratch and legal erasure implementation |
| Width and addressing | Scalar envelope and explicit wrapper inventory | Finite caller widths, temporary headroom, routing and controller lowering |
| Recursive supplier | Exact conditional model rejection | All-size/rounded-child transfer and a different favorable complete bill |

Stop dependent owner or supplier construction aimed at beating the selected
target with this exact five-forward/four-dual model. The local identity remains
useful evidence; the failed favorable model does not justify further physical
construction along that route.

Credit Jose Manuel (`jmbarrancoml`) first for the consumer-budget observation,
then Vasek (`flyingviper`)/PR2744 for its conditional audit; Ross Richardson's
PR2458 forward binding and PR2445 word; ywz65's P104/native/dual lineage;
Hiroki Kumazaki's PR3446 retained projection; Nick Petalas's PR3462 factor,
PR3469 adapters and PR3416 covariance; Jeremy Kothe's retained compiler lineage;
and Tekalign's PR3218 phase-sensitive criterion and the earlier compiler authors
retained in [SOURCES.json](SOURCES.json). This package contributes the
dirty-basis entrance schedule and its new profile substitution, with substantial
OpenAI assistance. Predecessor credit and notices remain in force.
