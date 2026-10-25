# Sharp Q8 inverse-label tariffs with arbitrary dirty workspace

Every finite list of Q8 diagonal targets retains its separate direct bill
when inverse labels have the same price as their positive counterparts.
This is a written all-role theorem over the full formal group algebra F2[Q8].
It extends Aaron Wang's PR2318 two-role census and ywz65's PR2587 restricted
{1,i,j,z} theorem to every target, including signed and k targets.
No native supplier or new kappa is claimed.

Let s_i,s_j,s_k count targets in {i,-i}, {j,-j}, {k,-k}, and let t count
central -1 targets. A paid i or -i call costs alpha; a j or -j call costs
beta, with arbitrary nonnegative real prices. The exact minimum is

    alpha*(s_i+s_k) + beta*(s_j+s_k) + 2*t*min(alpha,beta).

At unit prices this is s_i+s_j+2*s_k+2*t. For example targets
`(-1,k,-k,-i,-j)` need exactly eight calls even with any finite number of
restored dirty spectators. At prices alpha=2,beta=5 their exact bill is 25.
Coordinate-projector words attain every tariff without extra workspace.

## Boundary and new proof step

A paid factor is `I+([g]+1)u v^T`, with g in {i,-i,j,-j}, binary nonzero
u,v and v^T u=1. All inputs are arbitrary independent dirt. Scalar GL mixing
is free; no address operation or other primitive is free. Every endpoint
coefficient must equal the complete requested diagonal target. Restored
spectators finish identically. The same sharp result holds in the larger
alphabet that also admits rank-one nilpotent couplings, v^T u=0, at the
same price.

[PROOF.md](PROOF.md) gives the universal argument. Full formal coefficient
support forces rank X and rank Y at least the active role count W. The new
combined parity quotient sends all four paid labels to 1+epsilon and sends
both k classes and central -1 to 1. It gives `XY=P_i+P_j`, so Sylvester yields
`n>=2W-s_i-s_j`. Unlike separately summing two first-order ranks, this keeps
the complete joint charge for overlapping k and central targets. Separate
label characters supply the two weighted class floors.

This closes the inverse-label all-role gap. Positive-only signed tariffs,
four independently priced signed labels, clean-only endpoints and
projector-dependent prices have different boundaries. PR3137's finite-array
compiler and actual-caller handoff remain separate. A formal call is not a
physical recursive tariff, and this theorem neither admits nor rejects a
complete multiplication supplier.

## Reproduce

Python 3.12+, standard library only, from the repository root. Set TMPDIR to
an existing private external directory for behavioral test exports.

```sh
python3 -I -Werror -B scripts/research_package.py --package research/q8-inverse-uniform-tariff
python3 -I -O -Werror -B research/q8-inverse-uniform-tariff/verify.py
python3 -I -O -Werror -B research/q8-inverse-uniform-tariff/independent.py
python3 -I -O -Werror -B research/q8-inverse-uniform-tariff/test_package.py
```

Expected markers are PASS_Q8_INVERSE_UNIFORM_TARIFF,
PASS_Q8_INVERSE_REGULAR_ACTION, three passing behavioral groups and
PASS_REGISTERED_RESEARCH_PACKAGE. Verification writes no package files.
Explicit `verify.py --write NEW_PATH` refuses an occupied output. Normal
verification recomputes and compares every deterministic receipt field.

[RESULT.json](RESULT.json) records 14,500 attaining cases across 580 target
lists and 25 integer price pairs, all 64 credited predecessor pair minima,
46,656 three-call words with arbitrary rank-one couplings, 4,980 complete
factors through five roles, all three parity quotients, full coefficient
support, Sylvester and 20 single-omission rejections. The finite domain is
corroboration; the nonnegative-real-price and unbounded-role claims follow
from the written proof.

The separate no-import Hamilton quaternion engine checks 26,904 faithful
regular-action columns and 112 omissions from seven noncommuting words that
touch active and spectator dirt. The behavioral tests compare all dirty
columns of 168 further generic words at two through eight roles, exercise
actual faulty endpoint/tariff producers, source/receipt corruption,
non-overwrite and Git-free relocation. These are separate implementations,
not independent human review. Exact commands and limits are in
[VALIDATION.md](VALIDATION.md).

## Sources, scope and credit

Base canonical main is `6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority
revision 6. [SOURCES.json](SOURCES.json) pins the exact predecessor proof,
pair certificate and physical-compiler README. No predecessor code is
imported, no frozen bytes change, and no foreign Git object is required.
The source-complete committed-byte export passes the prescribed selected
baseline orientation. The full selected cold replay is unrun because its
construction and inputs are unchanged.

Initial live overlap fully paginated 358 open/2,761 closed PR bodies and 2,279
Discussion records at 02:02-03 UTC on 2026-10-18. Peer reservations are disjoint.
This covers bodies and prose plus retained source notes, not every diff or
unpublished work. [TASK.json](TASK.json) records the card's changed scope,
explicit side-result status, freshness and stop rule. The canonical
[investigation claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2034#discussioncomment-19009656)
joins the existing Q8 thread.
Submission refresh at 02:10-11 UTC kept the same canonical main, guidance
and inputs. Complete pagination covered 361 open/2,761 closed PR bodies and
2,284 Discussion records, without warnings. No competing all-target tariff
was found; PR3317 has a separate regular-action bit-cell contract.

Credit Aaron Wang/PR2318 for the inverse-label pair theorem and model;
ywz65/PR2587 for the full-coefficient support/Sylvester method and open
k/signed-target question; Cinna Davis/PR1925/2047/2248 for related mixed
Q8 results; Arham Tahir/PR3137 for the separate physical compiler and caller
boundary; steph4n-gh/PR1573 and Tuafo for the rank-nullity/support lineage;
and eumemic/PR288, Ali Romman/PR468, Gareth Davidson/PR1333 and the retained
register-model predecessors. Sylvester and the support method are credited,
not claimed as new linear algebra. No literature-priority claim is made.
New work is Apache-2.0. Nick Petalas.
Independent human and formal proof-kernel review are unclaimed.

## Open next questions

- Four independently priced signed labels or positive-only signed targets
  need a sign-sensitive invariant or sharing construction. Start with one
  mixed signed/central boundary and its complete direct tariff. The present
  binary parity quotients erase signs; they cannot answer that question.
- A useful physical result needs one actual caller with PR3137's contiguous
  eight-block layout, ownership, chronology, width and full routing/scalar
  invoice. Start by binding that caller and its direct alternative. Unknown
  physical costs remain unknown. This theorem reserves no further family
  expansion or word census.
