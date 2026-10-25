# Source-bound obstruction to single-ADD rank-profile retiming

**Result.** On both literal PR3734 staged544 providers, no transformation in the
single-ADD class below strictly lowers the raw recursive moment for any real
`0 < a < 1`. The exact over-approximation has **1,776,295 insertion-cut/frame-
dimension candidates per provider**, and just **19 signed histogram changes**.
Every change has an exact all-exponent non-improvement certificate. This rules
out PR3863's proposed `2+2 -> 1+3` exchange through this particular class. It does
not rule out coupled edits, neutral intermediate words, or changed interfaces.

This is a user-assigned investigation of converting rank-profile savings into
actual circuit transformations, on canonical main
`20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority revision 6. It is a scoped
negative result and a constructive positive control, not a new supplier or a
new value of kappa. The selected certificate is unchanged.

## Exact transformation class

Move exactly one existing scalar ADD within its A, B, or restore phase, after
the A prelude and without crossing any native B warp cut. All other gates and
their frames stay fixed. Crossed ADDs must satisfy the sufficient commuting
condition `destination(g) != source(h)` and `destination(h) != source(g)`.
Crossed nonzero SCALEs are allowed, with the moved coefficient conjugated
exactly. Choose any binary subspace of F_2^9 as the moved gate's common frame.
Keep entrances, target/centre cuts, helper exits, and the rest of the caller
contract fixed. Reconstruct inverse cleanup from the edited word.

The census includes frame-only changes at the original position. It has no
radius limit. It does not cover crossing a warp, moving a SCALE, cancellation
or deletion, a commutator correction gate, two variable gate frames, moving
across phases, or subsequent edits of a neutral intermediate word.

For a fixed placement, legal frames lie between the join of the two preceding
frames and the intersection of the two successor constraints. Every intermediate
dimension is achievable. The invoice depends on that dimension, not on which
subspace of that dimension was chosen. Therefore the verifier enumerates every
possible price, rather than sampling bases. Fixed checks are relaxed to virtual
climbs when pricing candidates. Such climbs are zero in every genuinely legal
witness. Proving non-improvement in this larger class proves the stated scoped
obstruction. See PROOF.md for the exact boundary argument.

| Phase | Candidate cut/dimension pairs, each provider |
| --- | ---: |
| A | 1,451,231 |
| B | 308,890 |
| restore | 16,174 |
| Total | 1,776,295 |

Counts include distinct placements with the same price. They are not a count of
distinct circuits or all binary frame assignments. CENSUS.json retains every
signed profile and its multiplicity, not only a success flag. The two providers
are checked separately; their literal B frames and native warp maps differ.

## Constructive control and actual paid credit

The verifier rolls back one already-retained **Jeremy Kothe PR2957** swap on the
current word, then recovers the original word by an explicit retiming. In current
zero-based addresses, the rollback changes A[4043:4045] from the additions to
register 81 using sources 40 then 17, into sources 17 then 40, with both at the
first gate's rank-7 frame. Moving source 17 back after source 40 and using the
retained rank-8 frame recovers the literal source word, after basis spelling and
the derived report are normalised.

The per-call profile changes from `{1:2439,2:726,3:225,4:101,5:20,8:8}` to
`{1:2440,2:725,3:224,4:102,5:20,8:8}`. Thus this actual circuit performs the
mass-preserving **`2+3 -> 1+4`** replacement, with no extra scalar gate, helper,
private cleanup buffer, or helper-width change. Both orientations and all 632
live inputs plus 91 arbitrary dirty buffers are replayed through the retained
free-operator interpreter. This rollback is a counterfactual local control,
not a claim to reproduce the complete historical PR2957 parent supplier.

Applying Dugongue's PR3863 rational credit to the two negative caps gives
`1491695107/1513529160000` per call, uniformly for
`17/10000 <= a <= 18/10000`. For 3,240 repetitions, this is
`40275767889/12612743000`, strictly greater than three by
`2437538889/12612743000`. Under unchanged normalisers and the complete common
invoice, this can pay three additional rank-1 children. It is an accounting
reserve attached to a credited circuit, not an implemented new overhead or a
new improvement over current staged544, which already contains this swap.
No new physical allocation or outer admission is asserted for the rollback.

## Reproduce

Python 3.12, standard library only, no network, solver, native build, or Lean.

```sh
python3 -B research/rank-profile-retiming-obstruction/verify.py --summary
python3 -O -B research/rank-profile-retiming-obstruction/verify.py --summary
python3 -B scripts/research_package.py --package research/rank-profile-retiming-obstruction
```

The standalone verifier authenticates every vendored input before executing the
retained interpreter source without a bytecode-cache import. It independently
reconstructs the chronological invoice, regenerates both complete censuses,
checks every exact sign certificate, recovers the literal positive-control word,
and runs eight rejecting/sensitivity controls. A wrong coefficient is tested
after cleanup has been freshly rederived, so an obsolete inverse is not what
causes rejection. Normal and optimised-Python execution are separate checks.

The standalone source-export runs are the scientific evidence. Registration is
provided for the existing repository hook; its metadata/history validation and
any hosted CI result are separate from these finite mathematical checks. The
native Clifford phase, physical allocation, full admission wrapper, precision,
all-size/compiler, analytic, and BIT chains have not been freshly replayed here.
They remain inherited or open as appropriate. No formal-kernel proof,
independent human review, architectural optimum, or unconditional multiplication
theorem is claimed.

## Open next questions

Can a neutral first retiming enable a second, strictly improving edit? The
certificate is tied to the exact baseline and cannot be iterated as a global
barrier. A useful first experiment would pin one neutral source-level witness,
then alter one interacting frame or gate, with the same dirty-state and complete
cost checks. The second move's geometry and complete invoice remain unresolved.

Can a coordinated two-frame or boundary-changing rewrite realise PR3863's
`2+2 -> 1+3` target? The first step is a literal before/after word and helper/caller
boundary, not selecting children solely from the aggregate histogram. Stock,
chronology, native semantics, restoration, and any added physical calls must be
charged. These questions are also structured in TASK.json.

## Provenance and credit

PR3734, dataisfire, commit `fa041037a3374eaa08feeca0b26a5d6893194147`, supplies both
literal words and the retained auditors. Jeremy Kothe's PR2957 supplies the
already-present commuting-swap mechanism; its re-addressed records are on main
under `research/rank7-joint-endframes/data/REWRITES-2957.json`. PR2979 and the
subsequent staged-entry/retiming chain retain their construction credit.
Dugongue's PR3863, commit `635fe84596c19016f3d0316a5cf7abbe48285490`, supplies the
quantitative credit theorem and proposed rank-2 exchange target. The capped-mass
and discrete-curvature identities retain ranked-pair-verification and its
credited predecessor authors' attribution.

Sagar Thakrar's exact interpreter is vendored unchanged, including its attribution
to Arham Tahir's frame-bill contract; roger-sato's semantic adapter is also reused
unchanged. Neither is called a newly independent interpreter here. The new
chronological trace, census, sign reduction, source binding, and controls are by
Chris R / Clear1nsight, with substantial OpenAI assistance. This AI-assisted
verification is not independent human review. See vendor/SOURCE-CREDITS.md and
SOURCES.json. Apache-2.0 terms and retained notices apply.

The overlap refresh read the contribution guides, revision-6 guidance, PR3863,
PR3734/3815, PR2979/2957 records, and live commuting/3734-retiming PR searches.
Discussion HTML coverage was partial. This is not an exhaustive novelty claim.
The source acquisition used a temporary fork-only, read-only Actions export;
that workflow is not part of this proposed package. No frontier, other PR, or
canonical default branch was modified.
