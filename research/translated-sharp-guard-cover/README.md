# Exact sharp-guard translation menus for compact switches

For `r` simultaneous compact-switch targets, the conservative sharp guard
product needs exactly **`3r+1` coordinate translations** to cover every dirty
address, provided `B>=3r+1` and `2^m>=(3r+1)(B-2)`. Each target has two
radix-`B` control digits guarded by `u_i,t_i<=B-2` and a target-free window
guarded by `W_i<=2^m-B+1`. The menu shifts each control digit by `k` and each
window by `k(B-2)`, in its own cyclic coordinate.

The lower bound allows arbitrary constants in every menu entry and coordinate.
It shows why a constant-size menu cannot guarantee these guards for an
unbounded number of targets. This lower bound concerns the stated guard
product, not the full actual agreement set of a compact word.

**Claim type: scoped proof with finite corroboration.** The attaining menu
also gives a source-correct logical switch interface. Select a good translation,
run the raw macro with `f_k=f composed with D_k inverse`, then undo the
translation. The selector depends only on fields restored by the ideal switch,
so an explicitly owned clean selector can be uncomputed. No physical selector,
translation tariff, supplier admission, new kappa or selected-frontier change
is claimed. The selected conditional kappa remains `0.003125804` on this base.

[PROOF.md](PROOF.md) gives the coordinate adversary, attaining menu,
source substitution and complete boundary of the claim. This is an original
alternative guard-interface question on `uniform-transfer-audit`, with
`scope_status=changed`. It does not discharge a selected framework assumption.
The sparse-repair construction and its previous results are cited context,
not an audit deliverable. The elementary coordinate-adversary and pigeonhole
arguments are standard methods. The contribution is their exact sharp-guard
specialization and the source-correct compact-switch interface.

## Evidence and reproduction

From the repository root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/translated-sharp-guard-cover/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B scripts/research_package.py --package research/translated-sharp-guard-cover
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/translated-sharp-guard-cover --check-source-history
```

The registered manifest runs normal and optimized warning-strict replay.
Each returns `PASS_TRANSLATED_SHARP_GUARD_COVER` and reproduces the generated,
file-hash-bound [RESULT.json](RESULT.json). Verification writes nothing.

The new checker covers five geometries with `r=1,1,2,3,4`, attaining menu sizes
`4,4,7,10,13`. It enumerates every individual coordinate value and exactly
counts the product by forbidden-phase masks. Every histogram has zero
uncovered guard tuples. This is compressed enumeration, not individual
execution of every large product address. Two one-target histograms are also
checked by direct guard-tuple enumeration.

The new logical composition is checked on all 2,048 addresses of a dirty
one-target rectangle, including unused high control digits and a data
spectator, for four source families. These are 8,192 endpoint cases.
Four further geometries have 256 deterministic sampled addresses each and
four source families, giving 4,096 further endpoint cases. Every case checks
the full endpoint, translation inverses and selector invariance. Guard-reading
and cross-window sources are included. Larger endpoint domains are sampled,
not exhaustively executed. No predecessor verifier is imported or replayed.

The lower-bound constructor defeats 1,056 explicit arbitrary-phase menus.
Its universal claim rests on the written adversary, not these samples.
Seven rejecting controls detect a shortened menu, overlapping bad-window
phases, missing source transport, and four invalid geometries. The receipt
records concrete counterexamples and every histogram.

No Lean, Docker, selected cold replay, physical tape implementation or complete
ordinary-callee invoice is supplied. Independent human and formal proof-kernel
review are unclaimed.

## Open next questions

1. Can the one-target four-phase menu be implemented and selected within a
   favorable full physical bill? First specify legal modular translations of
   the two dirty digits and the guard window, and charge owned selector
   preparation, controlled source delivery, shuttles and cleanup. Their costs
   are unknown here. A favorable algebraic cover alone is insufficient.
2. Does a larger source-dependent agreement set need fewer translations?
   First characterize an actual raw word's agreement set at one fixed radix,
   then distinguish guaranteed predicate coverage from accidental correctness.
   The present lower bound applies only to the conservative product predicate.

Structured relevance, first steps and blockers are in [TASK.json](TASK.json).
Stop after this first result. Further implementation needs the complete-cost
family decision in the research guidance.

## Provenance and credit

Canonical base is `a5bff3bf133e482541c09eba4e773884bdb2b1b7`, priority revision 8.
[SOURCES.json](SOURCES.json) pins the original card, selected record and cited
predecessor text as historical provenance. The verifier is self-contained;
none of those documents is an executable live input. The advance
[CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19279698)
records the target before implementation. Live overlap and main-tree searches
are bounded evidence, not a novelty certificate.

Cinna Davis / PR4100 supplies the CRT compact-switch caller. Unpaidmoon /
PR4321 supplies the live-digit sharp guard contract. John-Michael Smith /
PR763 supplies the compact carry/repair lineage. Hiroki KUMAZAKI / PR4169
supplies the arbitrary-source caller interface, and Ryanson Jonathan / PR4329
supplies the target-free `K-1` window convention. Douglas Colkitt and the
retained ordinary/CRT contributors keep their predecessor credit.
The new guard cover, proof and logical interface were produced by Nick Petalas.
New material is Apache-2.0.

## Checker design limits

The checker bounds `r<=4`, `G<=4`, `m<=8`, at most 13 phases and at most
8,192 mask entries per product layer. All loops have these fixed finite
bounds or bounds derived from them. Functions stay below 60 lines and explicit
exceptions keep checks active under `-O`. Sources and file writes are confined
to this package and the optional explicit receipt output.

Power of Ten rule 3 has a managed-runtime deviation: Python allocates integers,
tuples and lists during checking. At most two 8,192-entry product-count layers,
fixed coordinate masks and 256 sampled states are live; integer sizes are
bounded by these finite products. The replay exercises the maximum fixture.
Exact heap instrumentation and a fixed-allocation native implementation are
not claimed. If the checker grows beyond these capacities, replace the
storage bound before extending it. Rule 9 retains Python's standard dataclass
properties and bounded iterator dispatch; all targets are visible in this
single module. Rule 10 uses warning-strict normal and optimized execution;
no separate linter or static type checker is installed in the environment.
