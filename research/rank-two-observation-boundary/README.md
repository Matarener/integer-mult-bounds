# A four-call saving with independent output updates

**Scoped proof with exact finite corroboration. No new κ.**
Four fixed two-XOR children can return two independent output updates with
**two adapters instead of three** when one output at one intermediate cut
need not yet be correct. All arbitrary dirty workspace inputs are restored.
The complete local bills are **10 versus 11 XORs**, including entry work,
all children, correction and restoration.

The endpoint is `(x,y,a,b) -> (x+b,y+a,a,b)`: the update matrix has rank two.
This answers the first **Open next question** in Nick Petalas's
[PR5968](https://github.com/CrocSwap/integer-mult-bounds/pull/5968), whose
example updates both outputs by the same input and has rank one. It uses
commdata2338's unchanged [PR2020](https://github.com/CrocSwap/integer-mult-bounds/pull/2020)
model. The predecessors' shorter-chain census and rank-one result are cited,
not claimed as new replays. No error in either predecessor is alleged.

## Exact result and review path

[PROOF.md](PROOF.md) gives the complete model, attaining words, short lower
bounds, dirty-input traces, gate histogram and composition recurrence.
Both optimizers may carry noncanonical workspace and use any of the six
adapters before or between the mandatory children. Thus 11 is the optimized
full-observation bill, rather than the eager bill of 12.

The children are `(0,1,0), (0,0,0), (0,0,0), (1,0,1)` in PR2020 notation.
Only d0 after child 2 is hidden. The partial word adds `w1` into `w0` after
child 2 and `w0` into `w1` after child 3. The full word has a charged entry
adapter, a workspace adapter after child 1 and an output correction after
child 3. The difference in their complete gate histograms is exactly one
`d0 += w1`. Both original workspace values return without copying or erasure.

[model.py](model.py) evaluates formal coefficient rows. [verify.py](verify.py)
also uses a separately written literal bit interpreter that does not call
those child semantics. It enumerates all **571** schedules of adapter costs
0, 1 and 2. Exactly two cost-two schedules satisfy the partial contract;
none satisfy full observation. The literal interpreter checks every boundary
on all 16 dirty inputs: **9,136 executions / 18,272 contract checks**, plus
48 executions of the three positive words. The written argument establishes
the nonzero characteristic-two vector-space statement; this finite replay is not
formal verification of the multiplication theorem.

[RESULT.json](RESULT.json) is generated, not handwritten. It binds the exact
traces, counts, discovery coverage, predecessor inputs and implementation
hashes. Twelve semantic controls include a newly visible output, omitted
restoration, delayed correction, rank-one substitution, a clean-input false
positive and forbidden feedback. [test_faults.py](test_faults.py) injects
nine real faults per mode into private package/source copies and requires
the expected rejection in normal and optimized Python.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3 -B scripts/research_package.py --package research/rank-two-observation-boundary
```

Expected: `PASS_RANK_TWO_OBSERVATION_BOUNDARY rank=2 partial=2 full=3 xor=10/11 no_new_kappa`
in normal and optimized modes; `PASS_RANK_TWO_BOUNDARY_FAULTS rejected=18 modes=normal,optimized`;
then `PASS_REGISTERED_RESEARCH_PACKAGE`.

Direct Git-free scientific replay is
`python3 -I -W error -B research/rank-two-observation-boundary/verify.py`.
It is read-only. To regenerate, pass `--write-result NEW_PATH` and compare
that new file with RESULT.json. An existing output path is refused.

## Provenance and bounded selection

Base: `721c03822c421b7f7fcbb2598993b947c4d88419`; priority revision 8.
[SOURCES.json](SOURCES.json) pins both predecessor contracts by Git blob and
SHA256 at this base, as well as the historical selected record and catalogue.
PR5968's publication head is `8a3fcbcbc6dd83f3f1af3e34df700847f35c9645`;
PR2020's is `f4f8d2afdd3fec60c7739dcd826497e9738f80c1`. Execution uses the
exact base-pinned contract files, not a moving PR head. No predecessor code
is imported. PR2020 is incorporated in the ledger; PR5968 is partially reviewed.

Fresh OS randomness selected **57**, the recursive-interfaces track. The
catalogue's `joint-query-controller` card is marked **changed** in
[TASK.json](TASK.json): this is a historical abstract boundary side result,
not an active-mode injection or a changed supplier on the selected P104 word.
Three candidates and the local advance claim are recorded there. No pinned
sprint issue was found; the connector has no Discussion-writing operation.
The claim is local, with no separate reservation issue.

Seed 57 shuffles all 4,096 four-child lists in the specified lexicographic
order. Rank-two filtering leaves three fully checked candidates among the
first eleven inspected lists before the first witness is found. Each of the
three completes all 571 shorter schedules; search then stops. The seed changes
ordering; the independent-output requirement is what distinguishes this work.
No complete four-call census or maximum saving claim is made.

Open PR bodies, exact overlap searches, the ledger, relevant negative results
and visible Discussion1166 handoffs were checked before selection. The local
overlap helper reports sparse coverage and unavailable CLI remote refresh;
the GitHub connector supplies the separate live checks. Neither search
coverage nor the absence of a match excludes unpublished work. Freshness and
the final compatibility decision are recorded in TASK.json.

## Limits

If the mandatory children can be replaced, two direct XORs implement the
endpoint. Ten is therefore not an unrestricted circuit minimum. Observations
are read-only correctness constraints in this model, not a physical consumer.
The exact 10q/11q bit bill and returned-block recurrence in PROOF.md assume
coordinatewise XORs without cross-bit mixing or tape transport. They must not
be substituted for a native recursive-child tariff.

No actual recursive caller, physical observation service, native alignment,
stock allocation, tape movement, finite precision or complete outer invoice
is supplied. All five selected framework assumptions remain. The selected
κ=781451/250000000 is unchanged. Source-binding orientation is distinct from
the selected scientific cold replay, which was not run. No hosted CI,
independent human acceptance or proof-kernel verification is claimed.

## Open next questions

Does a named mandatory child chain in an actual caller
permit this exact missing observation? First extract its input/output maps,
all later reads and dirty returns, then compare the complete physical bill.
Without those contracts, further abstract enumeration would not establish
a useful supplier improvement. This package stops at the rank-two witness.

Power of Ten scope: managed Python allocates bounded tuples, lists and integers.
The finite verifier uses four rows, five gaps, 571 shorter schedules streamed
one at a time, 16 inputs and a 4,096-chain ordering. The fault harness alone
uses bounded subprocesses and private temporary copies. No scientific
network access or dynamic predecessor import occurs.

## Credit

Prepared for **@CubeJerry** with substantial **OpenAI Codex** assistance.
Credit Nick Petalas's PR5968 for the explicit rank-two handoff and its
rank-one witness; commdata2338's PR2020 for the model and earlier census;
Aaron Wang / navinor's PR1155, Adam Gall's observer-safe restoration and
Sagar Thakrar's restored-cut planner for the retained lineage. The classical
linear-circuit and permutation-parity arguments are not claimed as new.
This contribution supplies one independent-update witness, its sharp minima,
full local accounting and reproducible checks. New files are Apache-2.0;
predecessor files, licenses and attribution remain unchanged.
