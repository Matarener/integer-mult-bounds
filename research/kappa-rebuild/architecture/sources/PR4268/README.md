# The recursion lever on the community's words: b = 1.7887046e-3 on #2979's words with the full cut (checked by computer), DFT bounds up to 1.7806935e-3 proved in Lean (complex side only, no new κ)

Jacob Sussman. Apache-2.0 ([NOTICE](NOTICE)). Built with AI agents (Claude); see *Credit* below.

## 1. What this is

Marius-Paul Dumitrean's #2979 (`research/rank7-joint-endframes`, on main) prices its words at a complex-side root of
b = 1.7290339826e-3. This package changes nothing in those words or their packing, and in its registered
instance 2979 nothing in their allocation; the headline A-fc (section 9) carries a re-solved allocation (table of
hosts) for the same words. It changes the
**recursion** that turns a word into a running time, and with that change the same words give

| | figure | status |
|---|---|---|
| #2979 as it is on main (one job size, 73 axes) | 1.7290339826e-3 | the community's own checks; reproduced here to 24 digits |
| **#2979 with the lever (jobs of 73 and 49 axes)** | **1.7556473153e-3** | the registered check: price, heads and rate inequality checked by computer here; the DFT bound at 1.7556473e-3 is proved in Lean (section 5) |
| the same lever on Dugongue's #3945 | 1.7501109246e-3 | checked by computer with the same programs (section 6); proved in Lean at 1.7501109e-3 |
| **the lever on #3945 with every head kept** (#3945's words and price, a re-solved table of hosts) | **1.7581520168e-3** | checked by computer with the same programs and the table this package carries (section 7); the DFT bound at **1.7581520e-3** is proved in Lean (section 5) |
| **the full cut on #3945 with every head kept** (the same table; heads removed, job 25 on their arrays; the other rank-48 blocks split 24 + 24) | **1.7806935406e-3** | checked by computer with the same programs (section 8); the DFT bound at **1.7806935e-3** is proved in Lean (section 5), the highest of the five |
| the lever on #2979 with every head kept | 1.7564708e-3 | proved in Lean at 1.7564707e-3 (section 7); not replayed in this package |
| **the full cut on #2979's words with a re-solved table (A-fc)** (#2979's words, order and dispatch unchanged; a new table of hosts carried here, with its own paid profile; heads removed, job 25 on their arrays) | **1.7887045643e-3** | **the headline of this package**: checked by computer here, as registered commands (section 9); **not proved in Lean**. Its own figure with no lever is 1.6897030e-3, below #2979's, so the community's admission rejects it at its strict-gain steps (section 9) |

The highest figure here, A-fc's 1.7887046e-3, is checked by computer and not proved in Lean; the highest figure proved
in Lean is the full cut on #3945 with every head kept, 1.7806935e-3. The figure is a saving for the **discrete Fourier transform** in OpenAI's exact-arithmetic machine model, the model
of OpenAI's "Exact Fourier transforms below n log n" (openai/math, family 130): the program computes the DFT of every
length n in O(n (log n)^(1-s)) operations with s = 1.7806935e-3. It is the same kind of number as the community's
complex side b, so the comparison above is b against b. It is not a κ for integer multiplication: whether the outer
step accepts a recursion with two job sizes is open (section 4), and no κ is claimed.

## 2. The idea in one paragraph, and the numbers

The community's recursion gives every array of a unit a full job of 73 axes. In #2979's unit, 16,086 of the 28,190
rank-48 blocks per round are **literal heads**: each is the first non-identity operation on its own array, acting on
that array alone, with no helper hosted there before it. On such an array the unit can take a smaller job instead.
I cut each head by 24 of its 48 axes, so that its array takes a job of 49 axes and the head pays a block of rank 24;
every other array keeps the full job of 73. The recursion must then feed the word with jobs of two sizes in a fixed
ratio (66,304 arrays per round: 50,218 full jobs and 16,086 cut jobs). Theorem 1G ([PROOF.md](PROOF.md)) shows that
such a *mixed-target recursion* runs at the speed its balance predicts, provided every paid block is smaller than every
job (here 48 < 49). Its balance is the root b of

    sum_r n_r (r/73)^(1-b) = 50,218 + 16,086 (49/73)^(1-b),

with the paid blocks n_r = {1: 1,645,680, 2: 470,196, 3: 159,468, 4: 71,928, 5: 13,716, 8: 5,328, 24: 16,086,
48: 12,104} per round. Cutting only half of each head (not all of it) is what keeps every paid block below the
smaller job here. I call this step *the lever*. Cutting the whole head (a job of 25 axes) needs every other paid block
below 25 as well: on #3945 with every head kept, splitting each remaining rank-48 block into two blocks of 24 on the
same role does that, and that *full cut* is the highest figure proved in Lean here (section 8). On #2979's words a
table of hosts re-solved for the full cut (A-fc) has no rank-48 block other than its 16,576 heads, so nothing needs
to be split, and the full cut prices at 1.7887045643e-3 (section 9, checked by computer, not proved in Lean).

## 3. The registered check

    python3 -B research/lever-mixed-targets-2979/verify.py --part main       # about 50 s on a laptop
    python3 -B research/lever-mixed-targets-2979/verify.py --part controls   # about 5 s
    python3 -B research/lever-mixed-targets-2979/verify.py --instance 2979Fc --part main       # A-fc, section 9
    python3 -B research/lever-mixed-targets-2979/verify.py --instance 2979Fc --part controls

The last two run the same checks on the headline A-fc (section 9). Standard library only; it reads #2979's ten files on main (pinned in `SOURCES.json`, declared in `VERIFY.json`) and
writes only to a temporary folder. What it checks, in order:

1. **Pins.** Every input and every data file of this package equals its recorded sha256; the stated local profile,
   widths, zero buffers and complex root are read from #2979's `CLAIM.json` and `allocation/PROVIDERS.json`.
2. **My conversion of both words** (gauge44 and extra). `tools/transport.py` rebuilds the community's native
   canonical form from the borrowed word (the PR does not ship one) and replays it exactly on all 632 columns, in
   both orientations. `tools/lower_w.py` lowers it to my certificate format: frames nested at every climb, warps
   carried by their maps, residual widths equal to #2979's widths helper by helper, the block histogram equal to
   the local profile, the whole program replayed to the community's endpoint (91 zero buffers back at zero), and
   seven wrong versions of each word rejected. For #3945 the same transport reproduces the community's own native
   canonical words exactly (equal content hashes), which is how it was validated.
3. **The head test** (`tools/g0_staged.py`) in my network: the step order of my nine-stage hosted network, read as
   data from its Lean source (`network/`; nothing is compiled), run on #2979's ORDER, DISPATCH, PLAN, TEMPLATE and all
   271,728 FILL rows. Every role lies in a window of my network, no bin exceeds its rank, every role is used once
   per call, and the global paid profile equals `allocation/PROFILE.json` digit for digit. It finds **16,086 literal
   heads** (8,064 in child 8, 8,022 in child 10) and 12,104 other rank-48 blocks (children 12 and 13) that are
   neither heads nor tails. Its controls: moving gate A4 before its climb leaves no heads; deleting gate C2 turns
   the 12,104 other blocks into tails.
4. **The price** (`tools/price_ours.py`, with `pricer.py`, an exact re-implementation of the community's moment
   engine, and `mixed.py`): the uniform root of my profile equals #2979's `complex_lower` to all 24 digits; the half
   cut gives 1.7556473153e-3; the full cut is priced as a what-if only.
5. **The rate certificate** (`tools/rate_cert.py`): on the half-cut profile derived from the measured heads (not
   typed in), exact rational enclosures prove the inequality of section 2 at the figure 17,556,473/10^10 and
   refute it one grid step higher. The derived profile equals the histogram of the Lean rate module.
6. **Controls** (second command): the head test on the earlier T74 circuit (`controls/t74`, from Jeremy Kothe's
   #1839) finds the 11,010 heads (6,150 + 4,860) of the first head test; the figure is refused with a single head,
   with one head fewer (16,085), for a profile that is not separated, and one grid step above.

## 4. What changes from the community's model, and what does not

- **Changed: the recursion.** The community's recursion is one call per job, and every paid block is an independent
  call of the same job size; the ceiling tool assumes this. The mixed-target recursion needs several job sizes at
  once, fractional portions of batches, a tree of classes run in lockstep, a top split and exit calls
  ([PROOF.md](PROOF.md) section 3). As the card `complex-new-helper-inventory` allows when the coverage law changes,
  Theorem 1G is given as the replacement bound, and the incumbent ceiling is not applied.
- **Unchanged: the words, the packing, the endpoint.** No gate moves; no axis moves between children. The cut changes
  the job taken by an array whose first operation is the head; the rest of the word is the same. The allocation is
  #2979's own in the registered instance 2979 and #3945's own in instance 3945; the instances 3945H and 3945F and the
  headline A-fc (2979Fc) each carry a re-solved table of hosts (sections 7 and 9), checked as a table by the
  community's own programs.
- **Not checked here: the community's eight-stream operator model.** The heads and the cut are checked in my
  lowering and my network (and, for the DFT, proved in Lean, section 5), not in the community's exact operator
  replay. The idle-axis moves retracted on 18 and 19 October changed that operator; this package does not exchange
  idle blocks, but the check in that model has not been run (open question 2).
- **κ.** None is claimed. For orientation only: b = 1.7556e-3 is above the selected bit side c = 1.7334270e-3
  (#589), so if the outer step accepted this supplier the bit side would bind, at κ = 1.7334270e-3 in the newer
  convention or 1.7304275e-3 in the older one. The halving guard m^2 > 2R^2 of the outer recipe, read per array, holds
  for the half cut (on a head array the remaining paid block has 24 axes and 49^2 > 2 * 24^2; argued, not checked)
  but fails for the full cut, the headline included (25^2 = 625 < 2 * 23^2 = 1,058; < 1,152 on #3945), so the outer
  recipe as written does not take the full cut; one more reason no κ is claimed.

## 5. The Lean proofs (outside this repository)

The DFT bounds are proved in Lean 4 in my public repository
[jacobalansussman/wht-power-saving-lean](https://github.com/jacobalansussman/wht-power-saving-lean), commit
`563b4e6e913625637f36ba7869bf5fcd0dd4975a`, one package per instance: `package/leverF` (the full cut on #3945 with every head kept, the
highest), `package/leverB` (#3945 with every head kept, 1.7581520e-3), `package/leverA` (#2979 with every head kept,
1.7564707e-3), `package/lever2979` (#2979, 1.7556473e-3) and `package/lever` (#3945, 1.7501109e-3). For the highest,
the statement is OpenAI's `UniformFourier` statement with only the exponent (1 - 17806935/10^10) and the names changed
(statement file sha256 `2e32984d9d6a269b19d2fabafc9085360284d352d4bdccf90e4dff5786061f35`); the theorems are
`OAI.PowerSaving.transform_mainL3945F` and `OAI.PowerSaving.convolution_mainL3945F`, with only the axioms `propext`,
`Classical.choice` and `Quot.sound`. The other four are the same statement at their own exponents. The same statement one
grid step stronger is refused. The official comparator, with the Lean kernel and nanoda, accepts it against OpenAI's statement at this exponent and rejects the statement one step stronger. It is prepared for the Lean leaderboard
bigospeedrun.com/exact-dft, whose robot re-checks it independently: a pull request with it is meant to be opened alongside this package, and I will add its link and the robot's receipt as a comment once it is open.

This repository cannot pin bytes outside its own Git history, so the link is by content: every program in `tools/`
(`*.py`) and every file under `network/` of this package equals, byte for byte, a file of that commit (`SOURCES.json` lists the pairs of
paths), and the Lean rate modules `Rate2979`, `Rate3945H` and `Rate3945F` there state the inequality of section 2 for
the profiles recorded in `instances/2979.json`, `instances/3945H.json` and `instances/3945F.json`. Lean is not run by
this check.

## 6. The second instance: #3945

The same programs on Dugongue's #3945 (`research/staged544-terminal-gap-fill`, head `91f81d13`, archived on main on 20 October 2026 with the same files):
57,312 literal heads (28,672 + 28,640), the global profile equal to #3945's, the uniform root equal to its stated
root to 24 digits, and a half-cut price of **1.7501109246e-3**, certified at 17,501,109/10^10. It is not a registered
check here: when this package was made, #3945's files were on an open pull request. Its folder on main is the
default source of the instance, so it replays from the repository root with

    python3 -B research/lever-mixed-targets-2979/verify.py --instance 3945

(about 3 minutes; every input is checked against `instances/3945.json`; on a checkout of #3945's head, add
`--source <its research/staged544-terminal-gap-fill>`). The DFT bound at 1.7501109e-3 on #3945 is
proved in Lean too, in the same repository (`package/lever`). On #3945's published table the lever gives less than
on #2979's, from a unit five times the size (360 replicas against 74); with every head kept it gives more than on either published table
(section 7), and the full cut on that table gives the most (section 8).

## 7. Every head kept: #3945 with a re-solved table of hosts

The community's programs that decide where helper storage goes (the table of hosts, `owner/FILL.json.gz`) put each
empty rank-48 block either where it is a head or where it never is, at the same price, as their solvers happened to:
on #3945, 57,312 of the 80,640 blocks of children 8 and 10 end up as heads. I re-ran the community's own allocation
programs (Erwan Secousses' / ChaloupeMusic's, from #3815, as #3945 uses them) with one added condition, that every
block that can be a head stays empty. The result, `fills/3945H/FILL.json.gz`, keeps #3945's words, order, dispatch,
plan, template and global profile (`PROFILE.json` is unchanged), so the circuit's own price stays #3945's
1.7306632365e-3; #3945's complete stated verification (`owner/verify.py` and `admission/full_replay.py`) passes on
it from scratch, with all 119 of its controls rejected (checked by computer, the community's own programs). Then
**80,640** blocks are heads (40,320 in child 8, 40,320 in child 10), and the half cut prices at **1.7581520168e-3**:

    python3 -B research/lever-mixed-targets-2979/verify.py --instance 3945H

(about 6 minutes; the same checks as section 3 on #3945's files and this package's table: 80,640 literal heads,
57,312 other rank-48 blocks, the global profile equal to #3945's, the uniform root equal to its stated root to 24
digits, and the rate certificate at 17,581,520/10^10, refused one step higher). The DFT bound at 1.7581520e-3 is
proved in Lean (section 5). The commands that made the table are in the Lean repository, `package/leverB/fill/`.
On #2979 the same condition gives 16,576 heads instead of 16,086 and 1.7564708e-3 (proved in Lean at 1.7564707e-3,
one grid step lower, because the Lean rate enclosure stops just short of the rounded price); its table and the
community's complete replay of #2979 on it are in `package/leverA/fill/` of the Lean repository.

## 8. The full cut on #3945 with every head kept

On the same table, each of the 80,640 heads can be removed entirely instead of halved: its array then takes a job of
73 - 48 = 25 axes. The recursion needs every paid block smaller than every job, so the other 57,312 rank-48 blocks of
the unit (children 12 and 13, whole idle bins that host no role) are each split into two blocks of rank 24 on the same
role. A block of rank 24 + 24 is the product of its first 24 and its last 24 directions, so the split changes no
output; it only makes the recursion pay two blocks of 24 where it paid one of 48. Every paid block then has rank at
most 24 < 25. The balance becomes

    sum_r n_r (r/73)^(1-b) = 241,920 + 80,640 (25/73)^(1-b),

with n_r = {1: 8,041,680, 2: 2,306,880, 3: 729,648, 4: 353,160, 5: 69,120, 8: 25,920, 24: 114,624} per unit, and its
root is **1.7806935406e-3**, 1.28 % above the half cut on the same table and 2.89 % above #3945's own figure. On #3945's
published table the full cut does not pay (1.7307680e-3, break-even 57,262 heads against 57,312); with every head
kept it does.

    python3 -B research/lever-mixed-targets-2979/verify.py --instance 3945F

(about 3 minutes; the same checks as section 7, then the full-cut price, the profile derived from
the measured heads equal to the Lean rate module `Rate3945F`, the rate certificate at 17,806,935/10^10, refused one
step higher, and as controls the figure refused with a single head, with one head fewer, and without the split.) The
DFT bound at 1.7806935e-3 is proved in Lean (section 5, `package/leverF`); in Lean the split is a general identity
(a block of rank a + b is the product of two blocks of ranks a and b), with no hypothesis on the block.

## 9. The headline: the full cut on #2979's words with a re-solved table (A-fc)

**Status: checked by computer, not proved in Lean.** #2979's words, order, dispatch, plan and template are unchanged
and read in place from main; only the table of hosts is new (`fills/2979Fc/FILL.json.gz`, with its paid profile
`fills/2979Fc/PROFILE.json`). I re-solved it for the full cut: a class solution of a mixed-integer program on
#3815's Hall model, then a literal placement with #3815's own reverse-time placement (Erwan Secousses' /
ChaloupeMusic's `construction/build_fill.py`) run in a tolerant mode: a role with no planned slot left at its call
goes to the cheapest spare place, a bin open at that call that is not a head bin, not yet used at that call, and has
room in its final capacity. **Nine roles were placed that way** (8 of width 6 at call 553 and 1 of width 4 at call 0),
and 8 planned width-6 slots stayed idle. These are exactly the window, same-call and capacity rules that the
community's owner engine enforces. However the table was made, it is checked as a table: it passes #2979's unmodified
owner engine (PR2839, `allocation/vendor/independent_owners.py`, 271,728 roles, T = 74), and that engine rejects all
seven of its corruption controls.

    python3 -B research/lever-mixed-targets-2979/verify.py --instance 2979Fc --part main
    python3 -B research/lever-mixed-targets-2979/verify.py --instance 2979Fc --part controls

(the same checks as section 3, on #2979's files and this package's table: **16,576 literal heads** (8,288 in child 8,
8,288 in child 10) and **no other rank-48 block**, the global profile equal to `fills/2979Fc/PROFILE.json`, the
uniform root equal to the community's own root for this table to 24 digits, then the full-cut price, the full-cut
profile derived from the measured heads, and the rate certificate at 17,887,045/10^10, refused one step higher; as
controls, the figure is refused with a single head, with one head fewer, and with the heads kept as blocks of 48
while their arrays take the job of 25.) Every head is removed, its array takes a job of 73 - 48 = 25 axes, and every
paid block has rank at most 23 < 25, so the recursion is separated. The balance is

    sum_r n_r (r/73)^(1-b) = 49,728 + 16,576 (25/73)^(1-b),

with n_r = {1: 1,630,639, 2: 470,196, 3: 154,512, 4: 71,928, 5: 11,988, 6: 5, 7: 3, 8: 5,328, 17: 8, 19: 1, 23: 25,905}
per round, and its root is **b = 1.7887045643e-3** (three routes, exact rational enclosures on a 1e-24 grid, 60-digit
arithmetic and an independent 70-digit interval program, agree to 3e-60).

**Why the community's admission rejects it.** The table's own figure with no lever (the uniform root of its paid
profile, as the community's exact moment auditor computes it) is **1.6897030e-3**, below #2979's 1.7290340e-3: this
table pays off only with the full cut. The community's checks of #2979's line, run unmodified on a fresh clone at the
base, reject it at every step that compares that lower figure with a higher one, by design, and nowhere else:

| check of #2979's line (unmodified) | A-fc |
|---|---|
| `verify.py` (three-stage local replay of the words, 86 controls) | pass |
| `check_allocation.py`: pins, words, PROVIDERS, the PR2839 owner engine, the physical count 66,813, its 5 rejection controls | pass |
| `check_allocation.py`: the exact moment auditor (`tools/audit_allocation_moment.py`): rank mass, root bracket, exact bisection | pass, root 1.6897030e-3 |
| `check_allocation.py`: the auditor's strict-gain step (`audit_allocation_moment.py` line 65) | **rejected**: `strict frontier improvement and lower endpoint` |
| `check_cap.py`: cap certificate, rank mass, local profile paid, root at most the cap | pass |
| `check_cap.py`: `recorded gap` (line 68) | **rejected**: this is a near-optimality bound on #2979's own claim (the root within 1e-6 of the cap 1.7290358e-3), not literally a strict-gain check; A-fc's gap is 3.93e-5, the same lower figure measured against the cap |
| complete replay (`reproduce.py`): exports, fresh retained bootstrap, the native stages, owners, parent lift, rebind, discovery (7 steps), outer ledger (63 positive checks), independent check | pass |
| complete admission (`admit_extension.py` line 388) | **rejected**: `candidate must strictly improve full exact pinned frontier headline before full release` |
| the release stage, run past that step by my own driver: its `verify.py` (139 strict controls rejected) and outer checks | pass; then **rejected** at its strict-gain list over earlier packages, at `ledger kappa does not exceed PR2269` |

The same harness passed #2979's published table and design A completely (positive controls).

**Why the community's moment engine cannot price this figure.** The community's moment engine asserts the halving
constraint m^2 > 2 r_max^2. For the uniform model of this table it holds (73^2 = 5,329 > 2 * 48^2 = 4,608; its largest rank is the
48 of the 16,576 heads), and that is the 1.6897030e-3 above. With the cut arrays' job of 25 it fails
(25^2 = 625 < 2 * 23^2 = 1,058; after the cut the largest paid rank is 23), so the community's engine
cannot price A-fc's model with two job sizes at all. The figure 1.7887046e-3 comes from my own pricing under
Theorem 1G (`tools/price_ours.py`, `tools/mixed.py`, `tools/rate_cert.py`), which has no such condition: the full cut on
#3945 with every head kept, with 25^2 = 625 < 2 * 24^2 = 1,152, is proved in Lean the same way (section 8).

**What is proved in Lean and what is not.** Proved in Lean, in the Lean repository of section 5: Theorem 1G, the
recursion with jobs of two sizes (`Eng.engine_seam_final`), and the general theorem of the full cut
(`cut_heads_full` in `Work/Mixed/Bridge/CoreF`), as used for the full cut on #3945 with every head kept at
1.7806935e-3. **Not in Lean: A-fc's own instance**, that is, its heads-first certificate, the cut fact on
#2979's words, and the rate fact at 17,887,045/10^10. Its heads-first certificate and the rate fact are checked by
computer (this section's commands); the cut fact on #2979's words is argued by hand from the template it shares with
#3945's (where it is proved in Lean), not checked.

**What is claimed.** b, the complex side only, for the DFT in OpenAI's model, checked by computer. No κ: even if the
outer step accepted this supplier, κ would be capped by the selected bit side, about 1.7334e-3 (#589). The figure is
above every complex-side construction claimed on the hub by others; some research notes there print higher ceilings,
targets or hypothetical ledgers, which are not constructions.

## Open next questions

The structured list with first steps is `open_questions` in [TASK.json](TASK.json); in short:

1. **The outer step with two job sizes.** Does the outer theorem accept a complex supplier whose recursion uses jobs
   of 73 and 49 axes (the half cut), or of 73 and 25 axes (the full cut, the headline)? First step: write the mixed recursion as a supplier interface in the outer theorem's terms and
   list the changed hypotheses (PROOF.md section 3).
2. **The cut in the community's operator model.** First step: replay the cut of a sample of heads with #3187's exact
   eight-stream operator replay, with a control that a wrong cut changes the operator.
3. **A-fc in Lean.** The full cut on #2979's words is checked by computer with the re-solved table A-fc (section 9,
   1.7887046e-3), and proved in Lean on #3945 with every head kept (section 8). First step: build A-fc's instance in
   Lean the way the full cut on #3945 was built (its heads-first certificate, the cut fact on #2979's words, the rate
   module at 17,887,045/10^10).
4. **More heads.** Keeping every head that the table of hosts allows is done (section 7). Still open: whether some
   of the remaining 'neither' blocks (children 12 and 13) can become heads by moving the first touch of their array.
   First step: for each, find that touch before its climb and test whether it can be moved after it.
5. **Newer words** (for example #4088). First step: write `instances/<id>.json` and run the head test.
6. **The log factor of Theorem 1G.** First step: search small separated rules for a flow whose exits carry less
   than the sources (PROOF.md, remark after Theorem 1G).

## Credit

- **The words, allocation and checks this package reads** are Marius-Paul Dumitrean's #2979 (with substantial AI
  assistance, Anthropic Claude via Claude Code), on Jeremy Kothe's #2957 / #2948 / #2966 rewrites, Mason Hale's #2917,
  Jeremy Diviney's #2908, Dugongue's #2969, #2863 and #2839, Yiyang Lu's #2857 / #2848, RossRichardson's #2918,
  Jeremy Kothe's #2894 / #2833, Tekalign's owner checker, icekylinx's auditor, themilkman216's integrality
  observation and Gareth Davidson's #1995 / #2013, as #2979's NOTICE and CREDITS.md name them.
- **The borrowed helpers and their warps** that #2979 uses are Cinna Davis's (1337isnot1337, #2226), with Jeremy
  Kothe's width exchange (#2312); the T74 layout underneath grows from the work of Rohan Arun, Marius-Paul Dumitrean,
  Jeremy Kothe, LeverRank, Thomas DiFiore, Jeremy Diviney, Chafik Boukhalfa (chafreaky) and Vlado Vojdanovski.
  The T74 control data come from Jeremy Kothe's #1839.
- **The headline's table** (`fills/2979Fc/`) was placed with the construction of Erwan Secousses (ChaloupeMusic,
  #3815), its Hall model and reverse-time placement, run in a tolerant mode of mine, on #2979's own files.
- **The second instance** is Dugongue's #3945 (with substantial OpenAI Codex assistance, as its NOTICE says) and the
  line of circuits it ends, as its NOTICE names them: dataisfire's #3734, zxv's #3682 and #3638, Ross Richardson's
  #3605, Erwan Secousses' (ChaloupeMusic's) #3815, hexapode's #3802 and #3875, Dugongue's #3857 and #3929, and the
  earlier line under them. I read and re-ran the checks of #3945 by others, among them Chris R's (Clear1nsight's)
  audits #3969, #3988, #3994 and #4016. The table
  with every head kept (`fills/3945H/`) was made with the allocation programs of Erwan Secousses (ChaloupeMusic,
  #3815) that #3945 uses, from #3945's own files.
- **The moment engine** that `tools/pricer.py` re-implements is the community's
  (`research/native-complex-moment552`, `research/gauge44-frames-x`).
- **The Lean route** rests on Ryan Shea's conversion pipeline, generators and Lean tree, Nil Mamano's gauged Lean
  extension and Fourier chain templates, and OpenAI's model and statement. `network/Gates.lean` is a file of Ryan
  Shea's tree; its header credits Dugongue (#401), Lydakis (#275), jacklightChen (#377) and DaysSky (#363).
- **New here** (mine): the lever (the head test, the half cut, the full cut with the split, the mixed-target
  recursion and Theorem 1G), the tables with every head kept (the added condition), the table A-fc (its class solution and the tolerant placement),
  my transport and lowering of these words, the rate
  certificate, and the Lean proofs of section 5. The new files were
  written by AI agents (Claude) under my direction; the Lean proof is checked by Lean's kernel, and no person outside
  this project has reviewed this package.

## Files

| path | what |
|---|---|
| `verify.py` | the registered check (both parts) and the replays of the other instances |
| `instances/2979.json`, `instances/3945.json`, `instances/3945H.json`, `instances/3945F.json` | each instance's input paths and sha256, the stated values, and the recorded results (`3945F`: the full cut on the table of `3945H`) |
| `fills/3945H/FILL.json.gz` | the table of hosts of #3945 with every head kept (section 7) |
| `instances/2979Fc.json`, `fills/2979Fc/FILL.json.gz`, `fills/2979Fc/PROFILE.json` | the headline A-fc: its instance, its table of hosts and that table's paid profile (section 9) |
| `tools/` | `transport.py`, `lower_w.py` (my conversion), `g0_staged.py` (head test), `pricer.py`, `mixed.py`, `lever_price.py`, `price_ours.py` (price), `rate_cert.py` (rate certificate); [tools/README.md](tools/README.md) says where each comes from |
| `network/` | the Lean source of my nine-stage hosted network, read as data by the head test |
| `controls/t74/` | the T74 regression data |
| `PROOF.md` | Theorem 1G and what the mixed recursion needs |
| `RESULT.json` | the result in machine-readable form (no κ field) |
| `TASK.json`, `SOURCES.json`, `VERIFY.json`, `NOTICE`, `.gitattributes` | package metadata |

## Sources

- #2979: `research/rank7-joint-endframes` on main, head be191346391661f4d35fc0d1508d0a6029572576; the ten inputs
  with their Git blobs and sha256 in `SOURCES.json`. #3945: head 91f81d131252db704f945891da1ea54e29d46b8b. The
  table with every head kept: `fills/3945H/FILL.json.gz`, sha256
  9c06677d66b04436b02ec8d88036327bdc8fb12e6fd4f71a1b9c7e915c10c2d3. The headline's table (A-fc):
  `fills/2979Fc/FILL.json.gz`, sha256 7fc766c6c3e1561cee60b258138a918020b96d85ea782a2b01ad0ee035fd082e; the programs
  that made it are in the Lean repository, `research/record-track/programs/a-fc/`, with the class solution and the
  re-create commands in `research/record-track/data/a-fc/`. The community's checks of section 9 were run on a fresh
  clone at the base on 20 October 2026.
- The package's base commit is `SOURCES.json` `base_commit`. Hub figures as their authors state them, read on
  20 October 2026, 03:00 EDT.
- The Lean repository: commit `563b4e6e913625637f36ba7869bf5fcd0dd4975a`; leaderboard submission a pull request to bigospeedrun/verifier adding submissions/dft/jacobalansussman-lever-3945-full-cut.
