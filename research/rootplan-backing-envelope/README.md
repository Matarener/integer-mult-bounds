# Complete encoded RootPlan backing bound

This contribution was produced by Nick Petalas. Apache-2.0.

Scoped written proof with finite source-bound corroboration. The complete
unchanged PR5707 `MinimumRootPlan.compute`, including its 256 scratch tapes
and 29 retained field tapes, has a history-aware numerical backing envelope.
This answers the caller-transfer question in JoyboyBrian's
[PR #6098](https://github.com/CrocSwap/integer-mult-bounds/pull/6098).

For successful calls with precision p, selected width s, spacing K,
side widths left and right, coefficient count C, outer rows B, and fixed
construction constants m, F, g, define

```
b=bitlength(p), u=bitlength(C), v=bitlength(B),
c=ceil(log2 F), h=m-1, z=left+s*K+right,
E=8+max(1994*b, c*h*b, z+u+v+b+g).
```

Physical tape i has extent at most `max(initial_i,E_1,...,E_j)` through
call j and cleanup. The total is the sum over all 285 tapes. A cold planner
therefore has the sufficient bound `285*max_j E_j`. The full domain and
complete expression ledger are in [PROOF.md](PROOF.md).

For the production parameter law, `(s*K)^500000 <= p^499497`. With fixed
construction constants the cold bound is
`O(left+right+p^(499497/500000)+bitlength(p)+u+v)`.
The numeric side widths cannot simply be replaced by their bit lengths:
the direct p=2, s=right=0, C=B=1 family stores `gaussians=2^left`, requiring
left+3 cells through RIGHT.

## What is new and what is assumed

JoyboyBrian's PR6098 bounds the standalone minimum-prefix callee on a
32-tape pool and explicitly excludes the enclosing planner. We cite that
mathematical envelope as an input, without auditing or rerunning that
package. The new step accounts for all other live caller expressions,
parameter arithmetic, large saved powers, both caller branches, all 285
physical histories and erased warm tails. Saturated multiplication is
charged for its uncropped intermediate, before applying the cap.

Ali Romman supplied PR5707's complete encoded planner and PR5688's minimum
prefix theorem. Jose Manuel supplied the physical RootPlan and Count cohort
in PR3385. The retained sources preserve their complete predecessor notices,
including commdata2338's reached-depth result and the address/geometry lineage.
The per-tape high-water identity is elementary and is also used by PR6098.
The contribution is the complete caller envelope and its explicit dependence,
with no priority claim for that general identity.

## Reproduce

From the repository root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/rootplan-backing-envelope/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -W error -B research/rootplan-backing-envelope/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/rootplan-backing-envelope
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/rootplan-backing-envelope --check-source-history
```

Set TMPDIR to a scratch directory to choose where the unchanged source
loaders extract their temporary trees. The verifier removes those trees on
exit and writes its hash-bound receipt to stdout. It changes no source file.
The marker is `PASS_ROOTPLAN_BACKING_ENVELOPE`.

The checker runs seven complete planner calls and observes every owned
write, checking the exact high-water identity and the new envelope. One
call uses the production parameter law at p=2. Six use the predecessor's
explicit reduced tuple `(d,K,G,H,delta)=(8,1,1,1,32)` to reach both branches,
in cold and reused warm histories. These fast fixtures exercise the caller
body; they are not production-law fast cases. All seven borrowed inputs,
all 29 canonical fields, pool closure and owned cleanup are checked.

Further controls check 256 parameter substitutions, seven address-power
lower-bound fixtures, rejection of digit-only side-width accounting, and
failure of a fresh-history bound on preexisting erased backing. The finite
checks corroborate the proof. They do not quantify over all inputs.

## Limits

The sufficient constants are conservative. The theorem concerns successful
planner calls with the stated ownership contract. It does not prove pool
sufficiency on every input, exceptional-exit cleanup, Python heap bounds,
RootLayer payload storage, movement/time costs, numerical accuracy, any
selected framework assumption in full, or a new kappa. The standalone callee
theorem is a cited mathematical premise. Independent human and proof-kernel
review are unclaimed. No predecessor scientific suite or full selected
supplier replay is required for this scoped addition.

## Open next questions

The structured questions are also in [TASK.json](TASK.json).

- Bind actual root caller restrictions on left, right, C and B to this
  envelope. Start with one descriptor producer and include retained backing
  outside the planner. The remaining RootLayer storage ledger is a blocker.
- Replace the conservative 1994*b parameter term by a sharper source-bound
  bound, or change the capped multiply implementation to avoid full temporary
  products. First identify its maximum reached product. A replacement needs
  its own physical cost and ownership proof.

## Verification design decisions

The write observer delegates to actual complete source execution. Source
binding, caller execution and publication checks are separate. Functions are
under 60 lines. Fixture sets, the 285-slot state and five source-tree owners
are fixed and bounded.

Power of Ten deviations, rules 3 and 9: Python and the inherited interpreter
allocate dynamically, and observation requires replacing one Tape.write call
with a wrapper. Scope is this bounded checker only. The wrapper has one
original target, delegates each write exactly once, checks the resulting
physical extent, and is restored in finally. Fixed fixture sets bound live
observer state; the finite parameter/word sizes bound the source run. Warning-
strict normal and optimized replays verify this path. The five source loaders
are explicitly cleaned up in finally. The proof does not infer a Python heap
bound from numerical tape extents. A future runtime port must replace these
managed allocations and callback with its own bounded observation mechanism.
