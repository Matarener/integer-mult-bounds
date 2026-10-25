# Selective low-correction P112 co-delivery

**LOCAL_PROGRESS / INCONCLUSIVE for a changed supplier. No supported κ increase.**
Four cheap tetrads compose exactly as an abstract centre readout, with nominal
sensitivity cost 104 versus 112. Their live-port update is a different target.
The tested direct port repair loses, and the correctly oriented literal
four-block forward repair adds 276 scalar operations with no recursive delta.
These are stopping results for the stated candidates, not a general exclusion
of changed consumers or native co-delivery.

This research package is on branch `codex/selective-p112-codelivery`, based
on canonical main `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority revision 6.
The selected conditional κ remains 0.001672660197076918. Live comparison at
entry found PR3653 `607a09ff441c79b215a8127a81f4cc70021d0d9b` and PR3682
`431e6c6023ef352c41696469de7fb614cd4ded8c` reporting the same stronger conditional
endpoint, .001730418899766071163804 − 10^-46 − 10^-70. This package does not
improve either endpoint. Those complete releases were not independently replayed.
The human subsequently requested submission of this scoped finding, including
its negative repair results. Submission does not claim a new supplier or κ.

## Exact selective composition

Pins: PR3566 `ebd6b92c43239d76b1a59e29f574563494388f6a`, PR3604
`7156bb98f78b7492002010e8729d59fe38b92e60`, and direction correction PR3632
`7e7a889cbf6da2c4461af806fe52a888c621a7e7`.
[SOURCES.json](SOURCES.json) binds retained source bytes, original Git blobs,
and the two extracted selected-archive members. Frozen predecessors are unchanged.
The `retained_sources` inventory records the original foreign PR commit/blob/hash
pins; the direct verifier authenticates and compiles their package-local copies.
The generic `files` provenance inventory uses only the canonical base, so a clean
CI checkout does not need unrelated PR histories to replay this package.

The original completion has centre-support vector
`[2,8,9,2,8,9,8,9,8,8,2,8,9,2]`. Select only zero-based blocks `0,3,10,13`,
whose tetrads are `[0,1,2,3]`, `[0,2,4,6]`, `[1,3,5,7]`, `[4,5,6,7]`.
All 112 source/port labels and all 12,544 pairings are checked against the
selected port map. The eight native centre-frame orthogonal complements derive
the slot map `[7,5,4,6,3,1,0,2]`.

In block b, use PR3604's matrices `E_b`, `K_b=E_b E_b^T`, `U_b`,
`M_b=U_b E_b`, `C_b=S_b-H_b`, and `J_b=(C_b^T M_b)E_b^T`.
Let `D` be block diagonal with `U_b K_b` on the four chosen blocks and
`K_b` elsewhere. Let `K` contain all original `K_b`. Assemble the correction
`J` by **adding** all four contributions to the shared eight centre rows,
at their disjoint source columns. Exact rational arithmetic checks

```
S^T (D-K) = J,
S^T(d + D x) - J x = S^T(d + K x).
```

This identity holds for independent arbitrary `d,x` and an arbitrary additive
centre baseline `c`; it does not depend on zero dirty values. The port supports
partition all 112 ports. The four selected blocks provide sixteen augmented
rank-one terms; the other ten retain forty rank-two terms. Charging one rank-one
unit per nonzero centre coefficient, as the **published sensitivity assumption**,
gives `16+80+8=104` versus 112. Neither this tariff nor support-pair rank one
is a native COPY constructor.

## The missing full endpoint and the tested repair

The centre identity does not identify `d+D x` with `d+K x`.
The difference `D-K` has rational rank **16**, four in each chosen block.
For example its entry at selected port row/column `(0,0)` is `-2`.
These are defects of the abstract changed decoder against its original
untransformed decoder target, not a claim that `K` is the literal selected
forward scatter. They give no proof that a caller can accept the new ports.

Applying `U_b^-1` only after the update fixes the product part but leaves
`U_b^-1 d + K_b x`, which fails on independent dirty baseline columns.
Conjugating the complete target state also requires the dirty entrance and a
compatible consumer. A post-basis change alone cannot fill that gap.

One generous abstract repair is to perform the readout first, then add
`(I-U_b)K_b x` to the ports. This preserves the already-correct centre readout.
Its natural four-term factorization `(E_b-M_b)E_b^T` costs five additional
support-pair rank units per chosen block: three rank-one and one rank-two.
The four-block sensitivity becomes **124 versus 112** before source acquisition,
native conversion, hosting or cleanup. This is one losing factorization, not
a minimum or an exclusion of joint implementations. Merging coefficients back
to the original `E_b E_b^T` target merely returns the original rank-two terms.

The supplied scalar control realizes the *abstract* first block on independent
common-frame inputs `x[8]`, dirty ports `y[8]`, dirty centres `c[8]` and a dirty
scratch `h`. For each of the four terms, with `a=(M[:,q],-C^T M[:,q])` and
`b=E[:,q]`, it executes

```
(y,c) -= a h; h += b^T x; (y,c) += a h; h -= b^T x.
```

All 25 independent columns are checked, including arbitrary scratch dirt.
This costs **100 scalar ADDs**, reuses one restored dirty scratch, and is verified
in a model with eight independent output centre roles, of which only two are
actively updated. Eight is not a demonstrated minimum. It constructs a scalar linear map under
that explicit abstract contract. It is not a physical rank-one recursive COPY.

The exact first-block source registers would be
`L[110,21,37,47,46,36,20,111]`; at the actual selected pre-B cut their frame
ranks are `[8,2,8,2,3,2,8,2]`. The eight output ports are in frame zero. The
selected private centres are temporary copies of distinct rank-eight carriers,
descend separately, and are later cleared. They are not the eight independent
dirty output banks of the scalar control. In particular, the common-frame
zero window does **not** provide those eight immutable source forms or the
new centre-output contract for free. Source acquisition, chart conversion and
eventual consumption/restoration remain unsupplied. This diagnostic does not
exclude acquiring them elsewhere in a changed producer.

## Actual selected forward-cut control

The selected physical cut is `d <- d + S p`, not `p <- p + S^T d`.
All 176 canonical/native destination-first bindings are checked afresh.
For the four chosen blocks the forward target transform must use `U_b S_b`.
Each cheap block's old scatter has eight coefficients and the transformed
scatter has seventeen, including eleven in its first four rows. The zero
rows of `U_b K_b` therefore are not zero rows of the real scatter.

The concrete control inserts `U` before the existing private centre phase,
scatters `U S`, and inserts `U^-1` after the final private clear, before B.
It retains every existing child, carrier copy/descent, adapter and cleanup.
The full normalized scalar/frame replay checks all 704 ordinary dirty columns,
common-frame requirements, every final frame and private restoration.
The identity `U^-1(Ud+USp)=d+Sp` extends the changed common-frame boundary to
arbitrary 512-address vectors. Unchanged native kernels are inherited, not
recertified by this normalized replay.

| Item | Four-block result |
|---|---:|
| Old/new complete cut ADDs | 176 / 212 |
| Additional scalar ADDs, including both basis directions | 252 |
| Additional sign scales | 24 |
| Additional scalar operations | 276 |
| Recursive histogram delta | zero at every rank |

Installing the hybrid inverse-transpose reader as the scatter fails the full
endpoint. Omitting the entrance transform fails on initial dirty output columns.
Both controls preserve valid labels and expose actual semantic failures.
The unchanged native/recursive bill means no new unpaid coordinate or κ gain
is supplied by this repaired candidate.

## Coverage and complete-cost decision

The parent planning template `m=73, families=896, stages=9, centre=112, R=51`
is retained only as a hypothesis, with no new coverage-law claim.

| Hypothetical two-unpaid profile | Mass | Optimistic complex κ ceiling |
|---|---:|---:|
| Baseline `{1:192,2:56,32:166}` | 5616 | .013787668108147456 |
| Selective `{1:216,2:40,32:166}` | 5608 | .013807267286268059 |
| With the tested post-reader port repair `{1:228,2:44,32:166}` | 5628 | .013645894493467795 |

These numbers are exact-interval screen outputs rounded for display. They are
not realized κ values and cannot be combined with T360. Under the same
one-unpaid law the zero-saving moment is already
`1+(112-896/9)/(73*896/9)>1`, independently of the local histogram. Thus this
fixed planning model supplies no positive saving with one unpaid coordinate.
Even reinterpreting 104 as its centre charge would leave `104>896/9`; that
reinterpretation is not a derived coverage law either. No second unpaid
coordinate is exhibited in either actual supplier.

| Obligation | Evidence / cost status |
|---|---|
| Mixed coefficient identity and native-label support ranks | proved by exact finite algebra |
| One-unit centre coefficient tariff | sensitivity assumption only |
| One dirty scalar augmented block | constructively upper-bounded: 100 ADDs, one scratch, two active independent centre outputs in an eight-centre model |
| Actual acquisition of eight source forms and charts | unknown |
| Physical rank-one recursive implementation | unknown |
| Full changed live-port consumer and centre lifetime | unknown |
| Tested abstract post-reader repair | proved 20 added rank mass under its stated term pricing; loses |
| Tested literal forward sandwich | constructive +276 scalar operations; zero recursive delta |
| New hosting, rounded precision, magnitude, storage and cleanup | unknown |
| Replacement complex/bit coverage laws and complete joint invoice | unknown |
| All-size/compiler, outer transfer and multiplication theorem | not established |

**Expansion decision: stop these two repair candidates and hand off the changed
consumer premise.** Unknown costs are not zero. Another basis/shear census or
large synthesis is unjustified until a complete source/consumer contract avoids
the displayed port repayment. No heavy native/global replay, Docker or Lean was
run. The first unresolved obligation is a source-bound augmented native
COPY/consumer that supplies the correct full live-port endpoint with acquisition,
frames, arbitrary dirty state and restoration. The rest of the joint invoice
comes after that gate.

PR3684 at `fad2e401ff63c634fb04e47146b0323449af70dd` treats replacements of
up to five terms on a fixed rank-57 whole-triad target. PR3685 at
`7b55935a33b50d05858095dee93c669eadd122e8` rejects a specified generalized
non-Fano six-query/five-target split-reader invoice on that geometry. Neither
proves an obstruction for this changed tetrad output contract; neither is
used as a lower bound here. Their fixed targets and physical bills remain
relevant if a later candidate returns to those premises.

## Reproduce and review

```
python3.12 -I -O -Werror -B research/selective-p112-codelivery/verify.py
python3.12 scripts/research_package.py --package research/selective-p112-codelivery
```

The direct verifier needs no Git, network or unretained repository data. It
authenticates source bytes before compiling them directly, avoiding stale
bytecode. [RESULT.json](RESULT.json) retains matrices, supports, witnesses and
exact arithmetic brackets. [VALIDATION.json](VALIDATION.json) records executed
checks and environment; [REVIEW.md](REVIEW.md) records the fresh independent
AI review. That review is not human approval or a formal proof-kernel check.

## Open next questions

Can a changed native consumer use the four augmented tetrads while avoiding
the rank-16 live-port defect and preserving arbitrary dirty state? This is the
first gate that could reopen the route. Specify actual source forms, port and
centre ownership, entry/exit frames and a cost allowance of only two nominal
sensitivity units per cheap block. Demonstrate one complete block, with every
changed recursive child and scalar operation, before expanding.

If that gate succeeds, can both complex and bit suppliers justify a replacement
coverage law and its complete finite/outer invoice? The first step is an actual
full-call endpoint with the new centre lifetime and a specifically exhibited
extra unpaid coordinate. Neither scalar savings nor zero rows in `UK` answer it.

## Credit

Gonzalo Mier / PR3566 and PR3604 supplied the selected-port binding, tetrad
completion and co-delivery factorization. Ross Richardson / PR3632 supplied
the direction correction and normalized forward replay/sandwich helpers.
The P112 local geometry, gauge44, selected centre native-lift and their named
predecessors retain their original attribution in the unmodified vendor
READMEs. The ceiling engine retains Douglas Colkitt's attribution and its
disclosed Claude assistance. The source lineage includes selected E8/compiler,
owner, scalar/bit and multiplication reduction work; no new attribution for
those inherited constructions is claimed.

This selective composition, explicit scalar control, endpoint/repair screens
and handoff were prepared by OpenAI Codex at human direction, with substantial
AI assistance throughout and a separate GPT-6 Astra medium review. New work is
Apache-2.0. No independent human or complete formal theorem review is claimed.
