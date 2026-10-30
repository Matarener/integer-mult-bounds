# A legal new P104 contact does not finish the bounded helper680 split

**Local-only checked experiment; no new κ and no universal obstruction.**
Canonical main was freshly fetched as `df0137efd35e11b4445734bf612bdd4c7ebc330c`,
with priority revision7 and selected conditional κ `.00310045` unchanged.
The source is pending [PR5718](https://github.com/CrocSwap/integer-mult-bounds/pull/5718)
at `a1534ac45401c9a9c80c07aa65c89e00e33594f8`, claiming `.00311024570`.
Its inherited native, ownership, compiler, precision/tape and analytic assumptions
remain. This package does not independently admit that claim.

The experiment changes an actual route schedule: source event16655,
`MOVE 153,659,164`, is advanced to just after event16649. No intervening
instruction touches153. This creates a contact between153,685 and the fresh
continuation of680 before680 leaves frame164. Exact replay on every one of753
arbitrary source input columns verifies the retimed word, all frames, owned
lifetimes, target inventory and unchanged complete local paid/scalar bill.
This is a source-preserving change in transport timing, not a new frame itinerary.

## Checked result

1. **The candidate generator discovers the known positive.** It examines both
   departure and arrival groups after every role's MOVE. On PR5713 it finds
   the PR5718 cut at14330, pivot708, `708 +=154/2`, without being given that cut.
   There are1,880 compatible cut encodings on PR5713 and1,871 on PR5718;
   1,554 and1,546, respectively, are triggered by another role's MOVE.
   Counts include distinct encodings and repeated equivalent cut states.
2. **An exact emitted positive control passes.** The generic constructor
   implements the discovered708 split using literal dyadic ADD/SCALE operations,
   every arbitrary input, legal frames and owned INIT/COPY/CLEAR rules. It has
   the published paid/target profile. Its deliberately unsimplified terminal
   normalizer costs225,210 local scalar units, versus221,474 in the published
   PR5718 word. This is a recovered predecessor construction, not a new gain.
3. **Endpoint tests precede expansion.** All1,867 tested successor encodings
   fail cleanup using terminal frame groups alone; four440 encodings were
   excluded rather than revisited. A favorable temporal-span relaxation on
   all123 non-440 cuts with at most three endpoint-response fields rejects
   one:695 at13644. It grants unlimited frame-local memory and allows every
   MOVE to carry the entire available source-frame span. The required output159
   remains outside the span, with exact remainder `2 e700 + 2 e701` in the
   receipt's elimination basis. This is a scoped rational span failure, not a
   claimed universal separating functional. The other122 survive this relaxation.
4. **The three-ADD domain has no survivor.** Three concrete680 cut encodings,
   at13920 and13922, were tested on the original and retimed schedules. Each
   permits zero, one or two ADDs at the cut and zero or one at the later meeting.
   All4,887,150 literal program pairs fail. Two cuts at13922 are triggered by
   another helper's MOVE. The first steps are unrestricted: temporary errors,
   reads from the retired field and movement of corrections between roles are
   allowed. There is no greedy requirement to remove an error immediately.
5. **The four-ADD extension also fails.** For the13920 cut on the retimed word,
   zero, one or two ADDs at each of the two meetings give43,430,473 literal
   program pairs. All fail an exact necessary condition on main output153.
   The second meeting has949 distinct full three-field response matrices and276
   distinct effects on153; these are exact deduplications of all1,333 second
   sequences. The driver evaluates30,919,369 distinct-matrix pairs. Six exact
   rational input-coordinate probes already reject every pair, so no modular
   discovery or unpriced rational inverse is counted as an implementation.

An initial unsorted larger temporal-span run was interrupted without a result.
Only the completed123-cut run is evidence. Three exploratory shorter runs
(4,477,17,329 and49,321 cases) are retained separately; they are not added to
an allegedly disjoint coverage total. The four-ADD domain overlaps the
three-ADD cases. A failed candidate does not receive target credit.

## Exact bounded model

The prefix/suffix generator uses exact `Fraction` arithmetic, all public and
arbitrary dirty-owned entry columns, source frame containment and the actual
scalar word. It tests cuts `a=e_p+q e_s`. If purity determines q, that exact
value must be dyadic; when both rows are pure, the finite menu is
`q in {-2,-1,-1/2,1/2,1,2}`, together with the unmodified pivot.
It requires `c_p=beta_p=c beta=1`, with every nonzero coordinate of c and beta
at the pivot's initial frame. `beta=E^-1 S e_p` includes the actual main shear.
These sufficient conditions do not exhaust all helper boundary bases.

The three selected cut encodings are:

| Index | Source cut | Trigger | Cut operation | Input functional c |
| --- | ---: | ---: | --- | --- |
|1196|13920|680|identity|`e680`|
|1199|13922|681|`680 -=679`|`e680-e679`|
|1200|13922|681|`680 +=682`|`e680`|

Each has suffix response `e126+e153+e680` and split ranks5+4.
The first meeting uses exactly roles`[680,753,679,682,685,686]` at frame1049.
Roles outside that list retain their literal original operations. Here753
is the exploration label for the new independent input; emitted words shift
owned labels and use public index744 instead. On the original schedule the
second meeting is after16651 at frame164, with roles`[685,753]`.
On the retimed schedule it is after16652, with roles`[153,685,753]`.
Every ADD has distinct source/destination and coefficient from the six-value
menu above. Zero-length sequences and cancelling/inverse sequences are included.
The four-ADD domain uses the1196 cut and the retimed second meeting.

The suffix response to a first ADD is propagated through the literal word.
Every second source uses the state changed by all first ADDs. An exact
low-rank endpoint update is checked against a separate literal suffix walk
on every coefficient. Terminal normalization is granted favorably whenever
rational row spaces match. A proposed survivor would still require an emitted
dyadic-unit factorization, full endpoint and ownership replay, ordinary cost,
native/caller compatibility and complete pricing. No new candidate reaches
that stage here.

Resource bounds are explicit: at most six first-meeting roles, three second-
meeting roles, two ADDs per meeting and six possible coefficients. The three-
ADD driver caps each run at1,250,000 program pairs; all six completed. The
four-ADD driver caps at50,000,000 matrix pairs and completes below that cap.
It is a finite alphabet result. Longer programs, a third meeting, SCALEs in
intermediate programs, multi-source cut bases and genuinely different native
routes remain outside it.

## Complete signed invoice and ordinary work

`results/invoice.json` reconstructs the whole18-call source invoice from the
checked local bill and pinned literal controller. It has66,348 paid jobs,
12,976 productive fields and rank surplus760. The source local paid bill is

```
2184 H1 + 459 H2 + 495 H3 + 92 H4 + 159 H5 + 22 H6 + 15 H7.
```

The source local helper target bill is

```
2 H1 + 5 H2 + 91 H4 + 6 H5 + 6 H7 + 15 H8 + 411 H9.
```

The unrealized680 proposal has `Delta paid=0`,
`Delta targets=18(H4+H5-H9)` and therefore
`Delta(paid-targets)=18(H9-H4-H5)<0` for every`0<t<1`, `Hr=r^t`.
Both the retired old input and the new arbitrary input are credited only
if their complete targets are preserved. The route retiming adds zero paid
jobs and zero scalar operations; source scalar work remains221,474.
Input basis plus retirement costs16,32 and24 scalar units for the three cuts;
four menu ADDs cost at most40 additional units. Terminal normalization,
new-helper allocation/routes/cleanup and compiler/outer obligations are
**unknown and unrun**, because every candidate fails before those modules exist.
They are not priced at zero. The favorable signed invoice is an allowance,
not an emitted construction or a κ claim.

## Reproduction and evidence

Python3.14.5 standard library on macOS; source bytes and Git blobs are in
`SOURCES.json`. No Lean, Docker, full native, compiler, outer or selected cold
replay was run. The source and retimed scalar/frame checks cover all753
arbitrary input columns, owned peak2 and11 owned lifetimes. The emitted known
positive covers753 columns after adding one fresh public input to PR5713.
The complete serial `--full` replay passed. Normal and optimized controls and
the complete four-ADD receipts agree. Controls reject an illegal retiming across a write, a wrong source frame,
a non-dyadic ADD, unearned old H9 credit, a missing retirement and wrong-order
multi-meeting operations. A separate two-meeting fixture and real-P104
changed-state formula check pass.

From the repository root:

```sh
python3 -B research/p104-joint-neutral-search/verify.py
python3 -O -B research/p104-joint-neutral-search/controls.py
python3 -B research/p104-joint-neutral-search/verify.py --full
```

The quick verifier checks frozen receipt integrity, regenerates both contact
sets, and runs the constructive/negative controls and complete invoice.
`--full` additionally reruns the1867-cut terminal screen,123-cut temporal
relaxation, six declared three-ADD searches and the four-ADD search, serially.
Expect roughly8 minutes for full replay on the recorded host. Search timings
are diagnostic and excluded from semantic receipt comparisons.

## Open next questions

- A different transport contact is still needed for695 before more scalar
  search: the favorable fixed-itinerary span already fails. This package does
  not revisit helper440 or the known PR5440 native-letter mismatch.
- For680, first test a favorable controllability model with a **third** actual
  meeting, after15468 at frame1075 with479/527/continuation680. That introduces
  source rows absent from the two tested meetings. Preserve the same complete
  invoice and reject by exact availability before enumerating longer words.
  This is a distinct finite question; no success is forecast.
- The optional cross-call paid-answer span discriminator was not run. It still
  needs versioned physical query maps at caller events0 and3, actual stage
  routes and native operators, and retention/read/transport/cleanup charges.
  Input-row continuity and distinct query identities do not answer it. A new
  session should bind one such output rather than enlarge a duplicate census.

## Significance for researchers

The predecessor generator really did omit useful contact classes: the new
one discovers the published positive at another role's MOVE. A legal retiming
also creates a new contact at no recursive charge. Neither fact implies a
new independent split. This experiment explicitly explores temporary correction
redistribution and still fails in its two-meeting domain, while preserving
longer and physically different routes as open questions.

Credit [flyingviper](https://github.com/flyingviper)'s PR5718,
[Ali Romman](https://github.com/aliromman)'s PR5713/5708 and the complete
predecessor P104/native/controller/compiler lineage retained in`NOTICE`.
The frozen earlier information-reuse and multi-meeting investigations are
listed in`SOURCES.json` and remain unchanged. Prepared for
[zxv](https://github.com/zxv) with substantial OpenAI Codex assistance; no
subagents. The linear algebra and temporal identities are standard.
Apache-2.0. No public post, PR, merge or selected-frontier change was made.
