# Coalesce an owned P104 copy and save twelve scalar units

This contribution was produced by Nick Petalas. Apache-2.0.

A new exact word coalesces owned register 770 with its source register 791 in
DreamingOfClouds' [PR6144](https://github.com/CrocSwap/integer-mult-bounds/pull/6144)
word. After its last frame-549 read, 791 performs 770's continuation itself.
The duplicate INIT, COPY and CLEAR disappear. The public boundary and every
paid and productive rank remain unchanged.

```text
Local scalar units   189658 -> 189646
Events                22818 -> 22815
Owned fields             29 -> 28
Owned lifetimes          31 -> 30
Peak live owned fields   13 -> 13
```

This is a **finite exact circuit certificate and scoped substitution proof**.
There is no new kappa, strict peak-space reduction, supplier admission or
complete multiplication theorem. [PROOF.md](PROOF.md) gives the all-input
substitution argument, exact event anchors, prices and remaining obligations.

The initial target was an interior descent-stage deletion, taking the
read-rerouting question of JosieElliston's
[PR6136](https://github.com/CrocSwap/integer-mult-bounds/pull/6136).
No paid-profile stage deletion was obtained. The first smaller improvement
was shipped instead. Frames 553 and 1047 remain in the substituted trajectory.
This changes owned lifetime identity, rather than repeating PR6136's chart-only
search or the earlier fixed-word scalar resynthesis. The complete cost profile
and boundary are retained, so no dependent construction expansion is proposed.

## Reproduction

From the repository root, with CPython 3.12 and no third-party packages:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -I -B research/owned770-descent-pruning/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -I -O -B research/owned770-descent-pruning/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/owned770-descent-pruning
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/owned770-descent-pruning --check-source-history
```

A clean `python3.12` may replace that local interpreter path. Direct output is
`PASS_OWNED_LIFETIME_COALESCENCE columns=798 coefficients=636804 controls=9 scalar_saved=12`.
The registered replay runs both ordinary and optimized checks.

`construct.py` emits the complete word from the unchanged retained input.
The verifier checks all arbitrary-input endpoint and ownership conditions with
Ali Romman's unchanged main-branch checker, including a separate dense reverse
check. It enumerates every literal scalar price and paid rank, compares native
frame-boundary multisets, and rejects nine faults. `RESULT.json` is generated
by this verifier and binds all package files by SHA256. To regenerate a receipt
outside the checkout, pass `--receipt-out /absolute/scratch/RESULT.json`.

The retained input is byte-identical to the PR6144 word at
`4f3b67e7c37ae270da9584033132866d0cf63e42`.
[PREDECESSOR.json](PREDECESSOR.json) records its original path, blob, size and
hash. It is retained in publication ancestry, so replay does not fetch an
unmerged commit or depend on a shared local object cache. The predecessor's
supplier result is cited; its verifier stack is not rerun as this contribution.

## Limitations

The edited word has 798 logical input columns because one owned coordinate is
removed; all 770 public inputs and their exact endpoints are retained. The
existing physical caller's conservative owned reserve is not reduced. Peak
occupancy remains thirteen. There are no new frame pairs, and the formal
native operators are unchanged after renaming, but their actual implementation
is not rerun. Caller/compiler/outer, rounded numerical analysis, the selected
cold replay, Lean and Docker are unrun. The five framework assumptions remain.
Independent human and formal proof-kernel review are unclaimed.

This verifier uses bounded finite programs and managed Python allocation.
The input has 22818 events and 799 original role coordinates. Its largest dense
matrix has 798 by 798 entries. The one authenticated checker import is the only
dynamic import. These are explicit Python allocation and import deviations
from the Power of Ten rules. The existing frozen checker is unchanged.

## Open next questions

- Can a read-rerouting construction actually omit frame 553 or 1047 from this
  trajectory? Start with the exact readers 169 and 206, preserve their other
  meetings and price the complete changed route. Their current routes do not
  permit a direct move to the neighboring owned frame.
- Can the actual caller use the reduced declared inventory? First bind its
  alias allocation and lifetime schedule to the 28-field word. The unchanged
  global peak and caller reserve prevent claiming physical memory savings here.
- Does a specified rounded implementation admit the same lifetime substitution
  with a no-larger error budget? Bind actual COPY/SCALE and erasure semantics;
  exact rational equality alone does not settle that numerical question.

## Credit

DreamingOfClouds supplies PR6144 and its owned-relay descent, extending that
author's PR6143, PR6030 and PR5907 words. Ali Romman supplies PR5827 and the
unchanged exact checker, building on Mason Hale's PR5811 and the P104 lineage
back through Pierre-Loic Doulcet's PR5565. JosieElliston supplies PR6136's
read-rerouting question. The native, helper, controller and framework
predecessors retain their original credit and notices. Last-read register
coalescence is a standard compiler technique. The contribution here is this
literal legal P104 substitution and its exact complete-word certificate.
