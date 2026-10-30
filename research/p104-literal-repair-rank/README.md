# P104 literal correction needs 192 arrays of repair information

The full error from applying the old correction to PR3954's literal encoded
P104 banks has rank **192d**, where one array has complex dimension d. Its
data kernel has dimension **16d**. Extending both maps by identity on all
72 arbitrary dirty helpers leaves rank 192d and gives kernel dimension 88d.

This strengthens the previously stated **first-bank** rank 96d to the full
two-bank boundary. It also answers a changed consumer question: any additive
repair whose entire increment factors through k array-sized linear summaries
needs **k >= 192**, even when those summaries are granted for free. An
explicit algebraic factorization attains 192. This is a scoped proof and
source-bound finite audit, not a native-call count, scratch-space lower bound,
complete physical correction, supplier or new kappa.

## Boundary and result

Retain the predecessor notation

```
P=[I 0; T^-1 I],  L=[D HT; 0 I],  Pi=[I-H H; H I-H],  A=Pi L.
```

The wrong order gives `PAx`; the required order is `APx`. With `H^2=H`,
`HT=TH`, and invertible T, the complete defect E has the exact formula

```
rank(PA-AP) = 2 rank(H) + rank((I-H)(D-I)(I-H)).
```

The last rank is restricted to the complementary subspace, equivalently
computed in the whole space with zeros elsewhere. For the actual P104
pivot block `D_JJ=I_8`, it vanishes. The two N-bank input/output submatrix
is invertible:

```
[ -T_N^-1      0      ]
[   -I       T_N^-1   ].
```

Every pivot input column is zero in E. The 16-dimensional data kernel is
therefore exact, not just a dimension count from the first output bank.
In pre-encoding coordinates it consists of inputs supported on the pivot
ports in both banks. In already encoded coordinates the equivalent condition
is `first_N=0, second_N=B^t first_J`; these are different coordinates.

The unique repair after the wrong operation is `R=APA^-1P^-1`. Thus
`rank(R-I)=192d`. If `R(s)=s+VUs`, the summary Us must have dimension at
least 192d. [PROOF.md](PROOF.md) supplies the kernel proof, a sharp explicit
summary factorization, dirty-state implications and the complete obligation
ledger. No commutation of D with T is assumed.

## Exact evidence

The new checker imports no predecessor executable. It reconstructs the 120
doubled E8 representatives, removes the two pinned frames, orders the 104
ports, reconstructs B and D, and binds the retained physical labels to every
Gram pairing. It checks all **512 phase patterns**, executing both operation
orders on **280 basis inputs each: 143,360 columns**. It checks the full
defect, its explicit invertible minor, the complete kernel, the postprocessor
and every dirty return. This covers all distinct character blocks of a fixed
nonzero physical row fiber; the proof explains the tensor contraction.

[RESULT.json](RESULT.json) stores every pattern's exact-column digest and
the complete typed receipt. Digests summarize already compared coefficients;
they do not replace operator comparisons. Default replay is read-only.

A separate dense rational checker, [algebra.py](algebra.py), tests all 2,048
combinations of a binary 3-by-3 D and a coordinate projection H. Its larger
address-block fixture uses noncommuting chart blocks and checks the full
repair directly. Changing one pivot entry raises its rank from eight to nine.
Dropping the H/T commutation or projection hypothesis fails the appropriate
identity.

Seven further semantic controls reject a missing second-bank defect, a
first-bank-only repair, a rank-preserving sign error, the same-rank ordered
encoding in place of the literal slots, leaked or erased helper dirt, and
an uncancelled dirty summary. A dense Gaussian fixture includes nonzero
independent helper contents; every one of the 192 summary-dirt basis
directions has a nonzero output response. These are separate implementations in one
AI-assisted session; no independent human or proof-kernel review is claimed.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3 -B scripts/research_package.py --package research/p104-literal-repair-rank --check-only
python3 -B scripts/research_package.py --package research/p104-literal-repair-rank
```

The registered replay runs the main check normally and under `-O`, followed
by the separate algebra check. Direct commands also work in a source-complete
Git-free export:

```sh
python3 -I -W error -B research/p104-literal-repair-rank/verify.py
python3 -I -O -W error -B research/p104-literal-repair-rank/algebra.py
```

The main marker is
`PASS_P104_LITERAL_REPAIR_RANK rank=192 data_kernel=16 dirty_helpers=72 characters=512 columns=143360 summary_arrays=192 controls=7 no_new_kappa`.
`verify.py --emit` prints a newly derived receipt without modifying files.
Source SHA256 and Git blob IDs are checked before and after the main replay.

## Decision and limits

Task `p104-side-correction`, scope **refined**, priority revision 7; base
`32890bc5de034ab8fc93ac88ead7279a6a416d04`. The question follows the literal
slot finding in [discussion #1166](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19057044)
and its original [adjacent-pair handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19034066).
The claim is in [discussion #1166](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19173713).
The changed consumer admits arbitrary linear summaries instead of only a
uniform scalar repair. Predecessor block identities and the old first-bank
defect retain their credit; the complete rank, kernel and sharp summary
contract are the addition.

**Narrow and stop.** The existing 44,096-excess scaffold remains rejected.
We neither convert information rank into a recursive tariff nor propose a
changed paid profile. Summary production, new scratch restoration, actual
chart availability, native phase lowering, owners, physical scalar/movement
costs, precision, the complete moment and all-size admission remain open.
The 72-helper identity extension does not execute their earlier native
completion. No full original-word or selected cold replay, Lean or Docker
run is part of this audit. The selected record remains unchanged.

## Open next questions

Can a concrete caller use the two summaries in PROOF.md's equation (6)
without paying for a full decode? First name the physical chart, owner,
available value and dirty state for `r_N` and `w_N-B^t r_J`, then derive the
complete acquisition, output and restoration bill. This determines whether
the algebraic factorization is physically useful. An actual prepared caller
and a newly favorable full budget are blockers; the unchanged failed
scaffold does not justify a further implementation search. Repeating the
rank calculation or adding phase patterns cannot resolve those obligations.

## Credit

Chris R / Clear1nsight's PR3954, head
`f1e2839819959cd0534d008be91ed5b79ec55a6a`, supplies the physical encoding,
slot swap, correction, pivot block and failed scaffold, following
PR3882/3940/3943. Unpaidmoon's PR4133, head
`88666f1dee93fbd85b31fd5d6f91a219e111b5f4`, supplies the general literal
commutator and uniform-scalar obstruction. PR4370 concerns the different
helper-completion gate; PR4339 corrects the different fiber-tag orientation.
Neither is claimed as new coverage here.

Retain Rohan Arun / PR1972, Chafik Boukhalfa / PR1991, Adam Gall / PR1940,
Josie Elliston / PR1071, and the E8, native, Clifford and caller contributors
credited by the pinned sources. The previous commdata2338 P104 acquisition,
matching, native transport and precision contributions have different scopes.
Rank-nullity and linear factorization are standard tools; only their stated
complete-boundary application and checking are new here.

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
New work is Apache-2.0. No independent human review is claimed.
