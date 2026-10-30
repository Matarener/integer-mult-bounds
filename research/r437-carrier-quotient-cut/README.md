# R437 node509: a source-quotient obstruction to a third carrier deletion

**Scoped negative result; no new κ or physical supplier.** At current R437
source `a24f9ff95c12fd0b6792e3f710569237efd72db2`, a promising next deletion is
helper469, the SOURCE92 carrier. Even granting a free SOURCE77 read, its
replacement by an early SOURCE92 injection into receiver444 cannot meet the
fixed node509 output contract with an invertible linear register network.
The source quotient has rank two at entry and rank one at the required exit.
The obstruction persists with any number of borrowed registers returned modulo
the allowed external source span. It excludes arbitrarily long networks in this
specified alphabet, rather than only the six two-register matrices tried.

This informs the next κ search: another GL rewrite at this unchanged boundary
cannot supply the carrier saving. A candidate must change its accessible source
space, retain an additional output dimension, move the receiver/source boundary,
or supply and pay for a different operation. Such changes remain open.

## Exact scope and evidence

The verifier reads a byte-exact retained current R437 word. It independently
checks its full 659-column arbitrary-DIRTY XOR identity and the rational closure
of all 636 frames. Five helpers have exactly one single-SOURCE write in A/B,
are not captured, and are otherwise only read: 462, 463, 466, 468 and469.
At the first read of each, the destination's current frame is not contained in
the SOURCE's current frame. Thus the immediate replacement by a read at that
unchanged SOURCE frame fails. This census does not exclude earlier retiming or
a coordinated rewrite.

The focused cut concerns helper469, SOURCE92, node509 and writable receivers444
and413. At entry before A1998, their SOURCE rows are respectively zero and
`e87`; SOURCE92 is clean, at frame184. We optimistically replace the deleted
carrier by an injection `444 += SOURCE92` at frame184. Frame184 is contained in
509. The resulting source rows are `(e92,e87)`.

Scanning all659 registers gives ten other roles whose frames can enter509 and
then rejoin the next unchanged observation:

`17, 67, 177, 185, 271, 293, 352, 371, 467, 468`.

Targets177 and185 have zero SOURCE rows here. The inherited H1-H5 alphabet
forbids target readout; allowing them as borrowed banks is an additional
favorable relaxation and adds no quotient dimension. The other eight are
SOURCE/helper roles.

Their SOURCE rows span coordinates `17,22,33,38,50,60,67`. Add `e77` as an
explicitly **free relaxed channel**, to avoid charging or assuming a solution to
the incompatible early184/186 injection order. This larger span is called E.
The two actual node outputs, modulo E, both equal `e87 + e92`. Hence the input
quotient rank is two and the required output quotient rank is one.

A second source census covers all 34 insertion cuts A2001 through A2034,
before413 takes its next frame390 gate. The union of all newly eligible
frame509 read channels adds no dimension to E. This is a finite eligibility
fact. The theorem below still fixes the entry and exit SOURCE rows; it does not
claim to rule out arbitrary delayed observations or a two-window program.

The separately implemented checker propagates SOURCE87/92 one column at a time
and checks all GL(2,2), GL(3,2), GL(4,2) matrices: 6, 168 and20,160 respectively.
The added registers begin and end at zero **in the source quotient**, not with
physically clean payloads. These finite checks support the implementation; the
rank argument proves the arbitrary-register statement.

## Theorem and proof

Fix the retained entry/output rows and external space E described above.
The allowed replacement uses any finite sequence of invertible linear updates
among the writable registers, plus reads whose SOURCE row lies in E. Additional
borrowed writable registers may be used if their entry and exit SOURCE rows lie
in E. The replacement does not introduce an erasure, discard, new source
channel, changed observation contract or separate physical primitive.

Project every register's SOURCE row into `V/E`, where `V=F2^111`. Reads from E
vanish. Every invertible linear register update left-multiplies the row matrix
by an invertible matrix and therefore preserves its rank. Borrowed rows add
zero rows at both boundaries. The initial matrix contains the independent rows
`[e92]` and `[e87]`, so has rank two. The required final rows are both
`[e92+e87]`, with all borrowed rows zero, so have rank one. Contradiction.

Arbitrary dirty inputs cannot repair this source-column contradiction. Fresh
D compensation only modifies target DIRTY responses; literal C restores the
reversible word after its observations. Neither supplies a missing SOURCE
identity at this fixed node boundary. This is a necessary-condition argument,
not a proof that every source-correct candidate satisfies the full caller.

The external-role test uses the exact rational closed-frame inclusions
`current_frame <= 509 <= next_unchanged_observation_frame`. Captures are included
before B when finding that next observation. Final frames cover roles with no
later observation. This permits additional frame advances for free and is
therefore favorable to a candidate. Exact closure reconstruction validates the
set-inclusion representation of these retained frames.

Three escape controls deliberately break the strict-loss certificate: grant
an independent SOURCE87 channel; grant a SOURCE92 channel at the cut; or let a
borrowed register retain the missing SOURCE87 quotient row. They are potential
changes of contract, not free operations admitted by this package.

## Budget gate, overlap and limits

Pairing: reversible bit-circuit synthesis with quotient-space rank and frame
partial orders. The initial objective was a fully paid κ improvement. Rohan
Arun's pending PR3959 already realizes the unchanged width-eight pooled slot
optimum supplied by mightyOil's PR1281 theorem, so another unchanged owner
reshuffle was not pursued. The attempted changed local mechanism is an actual
third-carrier deletion at this source. It fails before pricing. All hypothetical
adapter and auxiliary costs were set to zero in the cut relaxation; no saving
is booked when the necessary source contract fails.

| Component | Status here |
|---|---|
| Current word's complete arbitrary-DIRTY linear identity | Checked, all659 columns |
| Rational frames and this source boundary | Checked, all636 frames; exact ten-role frame cut (two target rows are zero) |
| Immediate persistent-source replacements | Five candidates; all first-read gates fail |
| Fixed node509 deletion with returned borrowed banks | Excluded by rank2-to-rank1 theorem |
| Later eligible frame509 channel growth | 34 cuts checked; no new source dimension |
| Native all-size realization, stock, preparation, tape/precision, full physical cost | Inherited and unresolved; not audited here |
| New κ, a new local word, or a global carrier lower bound | Not established |

Canonical main is `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priorities revision6.
The selected κ remains0.001672660197076918. The team claim is
[PR3967 comment](https://github.com/CrocSwap/integer-mult-bounds/pull/3967#issuecomment-6263066320).
Live overlap included PR3647/3700/3950/3958/3959/3967/3982/3995 and the parent
team's Discussion review; coverage is partial. PR1281 already supplies generic
width-seven packing and conditional price tables; this package claims neither.

## Reproduce

From the repository root (Python3.12 standard library):

```sh
python3 -B scripts/research_package.py --package research/r437-carrier-quotient-cut
```

The two direct commands are `python3 -I -B research/r437-carrier-quotient-cut/verify.py`
and `python3 -I -B research/r437-carrier-quotient-cut/test_package.py`.
The latter performs an actual optimized Git-free subprocess replay and rejects
changed source bytes, changed certificate bytes and a missing retained notice.
`RESULT.json` is immutable during ordinary verification. `--write NEW_FILE`
regenerates a certificate explicitly. The source export includes its original
license and notice; `RETAINED.json` records exact origin Git blobs and SHA256s.
Those foreign-head origins are documentary pins, not runtime Git dependencies.
The verifier hashes the self-contained retained bytes before using them.

## Open next questions

1. Can a paid source87 or source92 channel reach this cut without disturbing
   the inherited SOURCE writes and future frames? Start with the exact
   `current <= cut <= next` failure and price a changed source/consumer pair.
   Its physical preparation, restoration and recursive bill are missing.
2. Can a two-window rewrite retain the missing quotient dimension in an
   existing bank and consume it later? Start with a proposed changed future
   observation map for413/444 and the borrowed bank. The fixed-output theorem
   does not apply, but all subsequent reads, COPY windows and full dirty
   cleanup must be checked and charged.
3. Can a different third-carrier construction change the boundary rather than
   merely resynthesize this GL network? Use the five-source census as an
   entry map, then derive a whole paid profile before an owner search.

Credit ai-nanachi/PR3647 for R437 and the helper464 GL deletion; Ali Romman/PR1043
for the retained helper470/SOURCE77 deletion; Sagar Thakrar/PR3700 and PR2423 for
independent checks and OQ4; mightyOil/PR1281 for the slot optimum; Rohan Arun/
PR3959 for pooled R437; eumemic, DreamingOfClouds, DaysSky, Crow, chafreaky and
the full notices for the original word, geometry, native, hosting and compiler.
New proof, implementation and checks by Chris R / Clear1nsight with substantial
OpenAI Codex assistance. Apache-2.0. No independent human or formal-kernel review
is claimed.
