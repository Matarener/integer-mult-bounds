# Sharp cost of active-mode delivery

For the fixed F9 source in PR5720, the exact minimum paid cost of canonical
mode delivery is **8H8**. This holds for clean one-frame channels with arbitrary
temporal reuse, and for at most eight channels even if their nuisance outputs
may cancel jointly. It equals the eight center jobs that were removed. This
resolves the direct transport strategy's paid allowance; it is not a new kappa.

The result checks every actual frame state and then the union of response
spaces over all times in each frame. No clean mode response exists below rank
eight. All eight modes have rank-eight witnesses. The full contract, rank
argument and limitations are in [PROOF.md](PROOF.md).

## Construction and evidence

A legal eight-mode completion transports the retained owned payloads, uses
coframed ADDs and restores all helpers and owned zeros. It passes the complete
632-input replay with native warp words retained. All eight new native maps
have grade eight; exact tableau, absolute phase and literal zero-column checks
pass. This extends PR5720's one granted cross-frame injection to a complete
legal word, while charging every added transport.

That word is dominated by the original: the paid profile is unchanged and it
adds 448 ADDs, sixteen CLEARs and eight live owned fields. It therefore does
not justify compiler expansion. The original center implementation remains
the better of these two complete words.

[RESULT.json](RESULT.json) records 5,331 distinct frame states, 3,963 projected
columns, 5,715 temporal frame/column observations, 49 single-cut response
witnesses and sixteen temporal witnesses. [CUTS.json](CUTS.json),
[TEMPORAL.json](TEMPORAL.json) and [WORD.json](WORD.json) retain the exact data.
All counts come from rational elimination, not a modular no-hit search.
Controls cover cross-time nuisance cancellation, independent nuisance,
missing transport, double helper debit, wrong payload sign and eight wrong
native phases. The entire committed receipt and word are checked under -O.

## Reproduce

Use CPython 3.12 and its standard library:

```sh
python3.12 -B scripts/research_package.py --package research/active-mode-delivery-frontier
python3.12 -B scripts/check_research_commit.py --package research/active-mode-delivery-frontier
```

The declared source archive is the unchanged
`research/filtered-native-kappa004/inputs/original-packet.tar.gz`. The official
export includes it. The verifier authenticates the archive before reading
selected data and code members directly in memory. Frozen PR5720 and PR5704
inputs are also checked before import. [SOURCES.json](SOURCES.json) and
[INPUTS.json](INPUTS.json) retain exact pins. No historical source is modified.
A direct exported replay uses `python3.12 -I -O -W error -B research/active-mode-delivery-frontier/verify.py`.

## Scope and coordination

Base: canonical main df0137efd35e11b4445734bf612bdd4c7ebc330c, priority revision 7.
Selected conditional kappa .00310045 stays unchanged. This takes the released
PR5720 handoff at ec327e35a1fb065ae53b6ec61bb3159e1a474371, recorded in the
[canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5125#discussioncomment-19197557).
It is separate from the newer P104 word and active two-field work in Discussion5645.
Fresh canonical priorities and fully paginated public overlap were checked.
Unpublished work remains outside that coverage.

The scalar quotient proves a necessary cost bound for the stated delivery
contract. The attaining word inherits existing native source contracts and
checks its eight added maps. It does not supply general feedback exclusion,
a complete physical caller, compiler/outer admission or a better ordinary bill.
The shallow checkout does not establish full source ancestry. Hosted CI and
independent mathematical acceptance are separate from local verification.

## Open next questions

* Can at least nine jointly noisy payloads beat 8H8? First give their complete
  output response space and payload matrix. A failed clean-channel search does
  not decide that question. All native delivery and restoration costs remain.
* Can a changed native frame or address word reduce the actual delivery grade?
  Start with one literal phase-aware payload map and a complete response. A
  relabeled frame is not a zero-cost transport.
* Independently check the temporal-span reduction and all-cut coverage. The
  exact source, witnesses and replay are available; no human acceptance is claimed.

## Credit

Ali Romman with substantial OpenAI Codex assistance; no subagents; Apache-2.0.
Credit flyingviper's PR5720 restoration certificate and its open physical
transport obligation. The original filtered-native packet retains Cao Yifan,
Cinna Davis, Dugongue and its mode/native/controller/caller authors. The archive's
license and notices remain unchanged. PR5704 supplies the exact compact
phase engine and its retained classical stabilizer-simulation credit.

The new contribution is the complete instantaneous and temporal delivery-space
calculation, its sharp paid-cost consequence, the legal full-mode completion,
and the explicit ordinary-cost dominance comparison. The original center
construction and source helper compensation remain predecessor work.
