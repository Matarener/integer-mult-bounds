# Restored P104 query and its observable quotient

**Result:** PR #3467's larger stagewise entrance gives no larger range for the
first collector's five readouts. A source-bound closed caller returns all
52 original coefficient banks and five dirty D banks, and changes Q by exactly

\[
Q_{\rm out}=Q_{\rm in}+E_9(a_2+a_9+a_{16}+a_{27}+a_{51}),
\qquad
E_9=\begin{pmatrix}1&0\\1&1+i\end{pmatrix}^{\otimes9}.
\]

Two direct, strict real-register schedules implement the same returned
coefficient/query interface, with explicit ownership, zero cleanup, operation
counts, and signed-width bounds. This closes the named-caller/observable question
released by [PR #3467](https://github.com/CrocSwap/integer-mult-bounds/pull/3467).
It does not establish a physical supplier or a new multiplication bound.

Clear1nsight, with substantial OpenAI assistance. Four concurrent agents split
coordination/source review, source composition, independent literal arithmetic,
and direct/quotient construction, with cross-review between those roles.
No independent human review or formal proof-kernel verification is claimed.

## Exact scope and why it matters

The inputs are 52 distinct Gaussian coefficient arrays of length 512, five
separate dirty D arrays in the Newton lattice \(B_9\), and a separate Q array
in \(B_9\). The coefficient meanings are those of the inherited encoder K.
They are not arbitrary raw Y values already supplied by another caller.

The new caller applies K, the actual **257-event producer dependency cone**,
the actual **15-event first collector**, a **252-event selective inverse**,
and the inverse codec. The selective inverse omits only the five inverse Q
compensation ADDs. It returns all source banks and frames and erases the first
private C at zero. Reversing every producer operation instead leaves precisely
the unwanted sum of initial dirty D values in Q.

This has three connected consequences:

| Question | Answer established here |
|---|---|
| Does the enlarged source module enlarge the five collector readouts? | No. Both it and the strong product entrance map onto the same \(B_9^5\), with one common explicit section. |
| Can the actual collector be closed while restoring its sources? | Yes, with the specified selective inverse; full inversion has an exact dirty-state error. |
| What does the resulting returned caller compute? | One Newton transform of a sum of five terminal coefficient banks; two strict direct schedules implement it. |

The 47 nonterminal coefficient banks and four terminal differences are invisible
to the final increment. They remain present as unchanged outputs. No source
information is erased and no bank storage is released by this observation.

This is a changed caller/observability audit under the original
p104-side-correction card, not another static flag census or a new entrance
classification. The complete card, scope-change reason, overlap coverage,
checkpoints, and family decision are in [TASK.json](TASK.json).

## Precise quotient statement

Write \(L\subset B_9^{52}\) for the inherited exact stagewise module and
\(S=(4B_9)^{52}\). The already established indices are

\[
[B_9^{52}:L]=2^{20424},\qquad [B_9^{52}:S]=2^{106496}.
\]

For the five disjoint chronological Y groups, let
\(\rho_5(y)_j=\frac14\sum_{Y\in G_j}y_Y\).
Place \(4b_j\) in the last Y of each group and zero elsewhere to obtain a
common section \(\sigma:B_9^5\to S\). Then

\[
\rho_5(L)=\rho_5(S)=B_9^5,\qquad
L/S\cong \ker(\rho_5|_L)/(S\cap\ker\rho_5),\quad |L/S|=2^{86072}.
\]

Every relative-domain class has a readout-kernel representative.
\(\rho_5\) itself does **not** descend to L/S, because S has nonzero readouts.
The full derivation, actual terminal-slot table, selective-return proof, and
three discriminating fixtures are in [PROOF.md](PROOF.md).

One fixture sets only \(a_{44}=\delta_{15}\). Its actual Y91/Y90 pair produces
a \(-1\) intermediate D value on 32 addresses and then cancels from all five
readouts and the final query. It lies outside S, while its nonzero coefficient
still must be returned. Another fixture has two nonzero opposite terminal
readouts and zero query increment. These distinguish the two different kernels.

## Direct schedules and costs

One mode gathers into an owned zero Gaussian bank and leaves every coefficient
read-only. The other temporarily uses \(a_2\), restores it, and requires no
extra Gaussian bank. Both need one separate real zero scratch word, restored
after every multiplication or exact division by \(1+i\).

| Strict rank-nine invoice | Owned zero bank | Temporary terminal bank |
|---|---:|---:|
| Real ADD/SUB, excluding doubling | 43,520 | 41,472 |
| Real doublings | 2,304 | 2,304 |
| Exact real halves | 4,608 | 4,608 |
| ADD/SUB if doubling costs one ADD | 45,824 | 43,776 |
| Extra Gaussian banks | 1 | 0 |
| Separate real zero scratch words | 1 | 1 |

With coefficient component bound H and initial Q component bound J,
the direct schedules have conservative bounds \(67260H\) for all non-query
arithmetic registers and \(J+16815H\) for Q. No fractional precision is added.

The literal core has 402 native occurrences, rank mass 722, 184,832 native
pairs, 804 wrappers, 388,480 direct Gaussian payload SWAPs, and 120 weighted
ADDs. Both inherited codec directions are additional. These native/component
inventories are not silently equated with a fully strict physical bill.
The [cost ledger](COSTS.md) specifies donor restoration charges, inherited codec
cost models, zero/ownership contracts, and every remaining physical obligation.

**Family decision: narrow and stop at this caller.** The unchanged-profile
599/584 supplier stop and the selected frontier remain unchanged. Further
construction needs a different required observable, a named physical caller,
or a changed fully priced mechanism.

## Evidence and reproduction

The source-bound integrated replay reports **PASS_P104_RESTORED_QUERY**.
Its [deterministic receipt](RECEIPT.json) records:

- Two separately constructed dense literal executions, each with **524 events**
  and **184,832 completed literal/ideal pair comparisons**.
- Equality of complete prepared Y, returned Y, returned coefficient, returned D,
  six-bank cut, and Q arrays before hashing; all 58 public return frames empty.
- Both strict direct schedules matching the literal query and all returned
  coefficient arrays; exact primitive counts, widths, and zero-scratch exits.
- Three preparation/readout/direct fixtures, signed arithmetic checks at
  ranks 0, 1, 2, and 9, 81 Gaussian \(\pi\)-roundtrips, and ownership controls.
- Exact dirty-sum failure for full reversal; missing Q return frame, wrong
  phase/readout/return signs; malformed, missing, corrupt, changing or linked
  source inputs; Boolean-versus-integer receipt distinction.

The dense final Q SHA256 is
6a42a56f516a1c19847cc05085d8febf6cdc519a2cabcc628ec3677ac1ae75bb.
Its initial 58-bank hash agrees with the frozen predecessor fixture.
Finite checks substantiate the implementations and source binding; the
arbitrary-input theorem relies on the written proof and inherited theorems.

Run from a complete checkout with history and Python 3.12:

~~~sh
python3.12 -B scripts/research_package.py --package research/p104-restored-query --check-only
python3.12 -B scripts/research_package.py --package research/p104-restored-query
python3.12 -B scripts/check_research_commit.py --package research/p104-restored-query --check-source-history
~~~

The registered manifest runs both normal and optimized Python, with 180 seconds
per command. All dependencies are standard library. No Lean, native build,
network access, external solver, or historical replay is required by the
scientific verifier. A direct source-export replay is:

~~~sh
python3.12 -I -B research/p104-restored-query/verify.py
python3.12 -I -O -B research/p104-restored-query/verify.py
~~~

The default verifier checks the committed receipt and never rewrites it.
Its explicit developer option to regenerate this package's receipt is
--write-receipt. Frozen scientific inputs and retained predecessors are never
generated or modified by that command.

For an exact committed export:

~~~sh
python3.12 -B scripts/export_research_package.py export --package research/p104-restored-query --ref HEAD --output /tmp/p104-restored-query.tar
python3.12 -B scripts/export_research_package.py check /tmp/p104-restored-query.tar
~~~

The exporter includes the package and every declared live input. Its transport
integrity check is separate from mathematical verification and source provenance.
The registered metadata checks require Git history; the direct verifier does not.
The publication handoff records actual commit/export/hosted results separately,
rather than treating these reproduction instructions as evidence of unrun gates.

## Source and review boundary

The frozen scientific base is
6f100d4bb5083f8c35d96fd95a539811c62f245c, priority revision 6.
At the 05:11 UTC checkpoint on October 18, 2026, canonical main had advanced to
20ecf2891d80b5acf18d980b2164fb44ea7faa90. Relevant guidance, selected record,
external live inputs, and registered replay tools were byte-identical; the new
package path was absent. The original scientific baseline is intentionally kept.

WORD SHA256:
cec1fb3fbd0067b500ad5119a62ba60685be718e769374d7ec8abdd2beaa7e50.
NATIVE compressed-source SHA256:
ab91c78835c3e10cf3b2cb8a5d4e0b7cfc3df1ae5a811298d27842f2193e1e3d.

Ten exact selected predecessor files were compared with immutable public
PR3467 head 4e4b08c689242f7f3be2e5e08dc1ae8d728ff920 and retained in this
publication's ancestor 9e501ba770d31c9f3decd51c987081c3b0acd256. This preserves
the sources frozen when that predecessor was pending; it also makes the direct
export self-contained. [SOURCES.json](SOURCES.json) declares all live inputs,
origins, Git blobs, hashes, dependencies, and credit. Every declared source
commit must be an ancestor for the strict publication-history preflight.

The primary checker reuses those authenticated implementations. The independent
checker imports no predecessor executable, derives actual Y paths separately,
and credits adapted arithmetic from our prior checker. Both inherit written
Newton/native theorems; neither is a new proof of all 1,245 native recipes.
Modules are compiled from captured bytes and all captured sources/proofs are
rechecked before a successful exit. The environment and checkout must remain
stable; this is not an atomic filesystem snapshot or an adversarial proof of
the Python runtime.

The original full 2,025-event prefix, the 5,398-event whole word, other consumers,
the 675 external ports, physical layout/access/control, zero supply, strict
native/codec lowering, and the complete recursive bill are outside this result.
No selected construction replay or human mathematical approval is implied.

## Open next questions

The two structured questions, first steps, relevance, and blockers are in
[TASK.json](TASK.json):

1. **Name a physical caller for these exact coefficient meanings.** State its
   actual reads, returned outputs, dirty-bank admission, and zero or mutable
   terminal storage before pricing the direct schedule's access and controller.
   This package supplies no such physical caller.
2. **Name an additional required observable that detects the kernel.** Start
   with the Y91/Y90 intermediate fixture and one legal consumer, including
   frames, coefficient, acquisition, restoration, and a complete allowance.
   Stop if no useful consumer is justified. A broader lattice census alone
   cannot change the present readout conclusion.

These are conditional handoffs, not a recommendation to expand the stopped
supplier or duplicate the distinct full-prefix/recipient work.

## Predecessor credit

- **ywz65, PR #2586:** frozen word, native recipes, and original physical
  inverse-transpose lineage; **Arham Tahir, PR #2665:** retained scientific inputs.
- **Nick Petalas:** PR #3426's ideal correlated entrance, PR #3416's
  phase-correct covariance, and the distinct full-prefix/adapter work in
  #3466 and #3469. The sharper two-source calibration in #3449 is complementary.
- **Clear1nsight with substantial OpenAI assistance:** PR #3382's Newton
  exactness application; #3423's actual producer interfaces and already established
  rank-one port map; #3467's exact stagewise module, codec, and cost ledger.
- **Tekalign:** signed-floor and phase-sensitive checks in #3025 and #3218;
  **Ross Richardson:** the exactness-domain question in #3068.
- **Jose Manuel and Vasek:** the inherited unchanged-profile cost stop,
  with its original assumptions; all retained geometry, native, compiler,
  precision, and repository contributors keep their original attribution.

This applies the existing Gaussian Newton/Clifford lattice framework; it does
not claim a new classical lattice family. Root LICENSE and NOTICE,
upstream/LICENSE, the source archive notices, and exact predecessor documents
are retained as declared inputs. New work is Apache-2.0.
