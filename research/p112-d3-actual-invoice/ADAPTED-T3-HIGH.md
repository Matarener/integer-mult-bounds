# Adapted t=3: every high-containing actual profile

Prepared by conorholds with substantial OpenAI Codex assistance. Apache-2.0.

## Exact scope and sources

Use the actual-basis contract of PROOF.md and the declared inputs in
DEPENDENCIES.md. Additional actual-profile arguments come from PR3689 D2.md, head
`3193d1ea9a4fc5d178570a61e6019454b53c1db9`, as declared in SOURCES.json. The transfer below uses the written arguments, not the D2
theorem with a different global threshold space substituted.

Let dim S=11, C have dimension eight, and let F be an actual basis with
all restricted duals nonzero. Let T span ALL S-words of binary support
rank at most seven. Assume adaptation r=0, dim(C intersect T)=3,
raw sum at most 73, and invoice I<=64. RAW-SHAPE gives dim T=6.
There are six actual inside members forming a basis of T and five
outside members of weight eight/nine. Write Sigma for the inside sum,
and c9 for the outside-nine count. Then

    raw=Sigma+40+c9,  Sigma<=33.

This note excludes the entire branch in which at least one actual
inside member has weight eight or nine. It does not claim a result for
all-low inside profiles without a separate argument.

## 1. Exhaust the relevant minimum profiles

Choose a greedy minimum-weight basis of T, with cost c and weights at
most seven. Actual sorted basis weights dominate its sorted weights.
If an actual inside member has weight at least eight, this gives
c<=Sigma-1<=32. The inherited lower bound is c>=30.

Such a six-member minimum basis must contain a seven. Suppose instead
all weights were at most six. If a smallest weight is at most four,
delete a different coordinate on the three-dimensional code intersection.
The remaining five-piece family has code intersection at least two,
and consists of four pieces of rank at most six plus an exceptional
piece on at most eight sites. The retained four-six-plus-nine lemma
excludes this. If all six weights are at least five, cost at most 32
allows at most two sixes. Killing the two largest coordinates leaves
a nonzero codeword in four rank-five pieces, whose support capacity
is 4*12=48<53. This is again impossible.

Delete one seven from the minimum basis. The remaining five pieces
have code intersection at least two and cost at most 25. The intrinsic
five-piece exhaustion in D2, under “Complete minimum-profile boundary,”
leaves exactly the following necessary six-piece profiles after restoring
that seven:

| c | Necessary minimum T profiles |
|---|---|
|30|777711|
|31|777721, 777541, 777631|
|32|777731, 777722, 777551, 777542, 777641, 777632|

These are necessary candidates, not existence assertions. In particular,
the intrinsic five-piece list includes 77542 and 77632; excluding them
only by the D2 INVOICE theorem would be circular at this stage.

## 2. Exhaust the high-containing ACTUAL six-piece profiles

At c=32 there is at most one unit of actual weight surplus. A high
member forces this entire surplus to raise a seven to eight.

At c=31 there are at most two surplus units. A high member arises
by raising one seven to eight/nine, or two sevens to eight. With one
eight, the remaining surplus can raise one other weight by one.
For minimum 777541 the threshold through weight three is the unit
line, so the unit cannot rise to two. For minimum 777631 the threshold
through weight two is the unit line, giving the same restriction.
The remaining possibilities are precisely covered by the table below.

At c=30 the threshold through weight six is a two-unit plane, supported
on exactly two sites. The six actual members must include exactly two
small members of weights one/two: one small member would already give
cost at least 1+5*7=36, while three independent small members exceed
the threshold dimension. The other four weights are at least seven.
Distributing at most three surplus units among these six weights gives
the remaining rows of the same table.

For each actual profile, remove a heaviest high member Q. The complete
necessary list, grouped by the resulting five-member profile, is:

| Actual six-member inside profile(s) | Remove | Actual remaining profile | Remaining sum |
|---|---:|---|---:|
|877711, 977711|8, 9 respectively|77711|23|
|887711, 987711|8, 9 respectively|87711|24|
|877721, 977721|8, 9 respectively|77721|24|
|877541, 977541|8, 9 respectively|77541|24|
|877631, 977631|8, 9 respectively|77631|24|
|877722|8|77722|25|
|887721|8|87721|25|
|888711|8|88711|25|
|887541|8|87541|25|
|887631|8|87631|25|
|877551|8|77551|25|
|877641|8|77641|25|
|877731|8|77731|25|
|877542|8|77542|25|
|877632|8|77632|25|

Thus there are at most twenty actual high-containing candidates and
fifteen residual actual profiles. The table may retain profiles ruled
out by stronger threshold geometry; completeness only requires that
every actual possibility is included.

## 3. The actual five-member transfer contract

Let L be the span of the five actual members remaining after deleting Q,
and put D'=C intersect L. Its dimension is at least two by dimension.
It is exactly two. Otherwise kill the two largest remaining coordinates
in a code intersection of dimension at least three. A nonzero word
remains in the three smallest actual pieces, with capacity at most 41.
Indeed, write their weights a>=b>=c. Ordering of all five and their sum
at most 25 give 3a+b+c<=25. If a>=8 the left side is at least 26.
If a=7 the capacity is at most 36+4+1=41; if a=6 it is at most
20+20+1=41; if a<=5 it is at most 3*12=36. All are below distance 53.

Consequently C+L=S. The six actual coordinates outside L, including Q,
form an independent family in Ann(L). Restriction to C is injective on
Ann(L), so their restricted duals are independent. All six have weight
eight or nine; their corrected frame axes are distinct and inactive on
D'. The actual basis, restricted duals, corrections, raw sum and invoice
are unchanged: only the proof's division into inside and outside moved Q.

Write s for the displayed remaining sum, and c9' for the number of
weight-nine members among these six outside members. Then

    raw=s+48+c9'<=73,  n_c>=s-16+c9'.

In particular s=23 requires n_c>=7+c9'; s=24 requires n_c>=8+c9';
s=25 forces c9'=0 and n_c>=9. These include all corrected nines.
No assertion L=T, minimum actual basis of L, or threshold filtration
of L is needed for the following actual-profile arguments.

## 4. Audit of all fifteen residual actual-profile exclusions

Ten profiles are literally covered by the [T3.md](T3.md) proofs, which
explicitly use this actual five-member contract:

* Remaining sum 24: 87711 and 77721, under “Sigma24.”
* Remaining sum 25: 87721, 88711, 87541, 87631, 77722, 77551,
  77641, and 77731, under the corresponding “Sigma25” paragraphs.

The proofs use only actual coordinate kernels, support capacities,
independent six outside restricted duals, and the correction thresholds
just displayed. Their common reduction needs dim D'=2 and C+L=S,
already proved here. The 87631 proof in particular uses the ACTUAL
eight-coordinate kernel, and the 77731 proof explicitly handles
repeated corrected indices and its equality-support case. No minimum-L
normalization or global-threshold substitution is imported.

For completeness, here are direct restatements of the five additional
profile arguments from D2.

In each of the two-seven profiles below, the joint kernel of the two
seven coordinates is zero: omitting both sevens leaves capacity 21,
25, 22, or 26 for 77541, 77631, 77542, or 77632, respectively.
Since D' has dimension two, the two seven restrictions are independent
and nonzero. Their corrected indices, when present, are therefore
active and distinct, and their individual kernels are distinct lines.

### 77711

Only the three sevens can be corrected. At least 7+c9' corrections
force at least 4+c9' corrected outside axes, so D' has at most four
active axes. Each seven-coordinate kernel line is nonzero and the three
lines are distinct: killing two seven coordinates leaves one seven and
two units, at most 38 sites. Each kernel word uses two sevens and two
units, at most 74 sites. Restricted four-axis rigidity makes all three
kernel lines root/frame.

Three distinct root lines in a normal plane form A2. Under at most four
active axes the plane is the retained four-axis A2 configuration, whose
distinct-root-coordinate-kernel lemma permits at most one corrected
seven. It has exactly four active axes, so there are at most four
corrected outside axes. Thus n_c<=1+4=5<7. This uses only the displayed
two unit pieces and the actual kernels, not a low-threshold claim for L.

### 77541

At most four inside pieces are corrected, so n_c>=8+c9' gives at
least 4+c9' corrected outside axes and at most four active D' axes.
Killing either seven gives a word in 7541 of capacity
36+12+8+1=57<70. It is root/frame. It cannot be frame, whose target
capacity would be 32+12+8+1=53<56. It is therefore a nonframe root,
using all four active axes. The killed seven cannot be corrected:
its nonzero frame coordinate would vanish on a root using every active
axis. Applying this to both kernels makes both sevens uncorrected.
At most the rank-five and rank-four pieces can then be corrected,
forcing at least six outside axes and at most two active axes, a
contradiction to the nonframe kernel root.

### 77631

Again n_c>=8+c9' and at most four inside corrections give at most
four active D' axes. Each seven-kernel word lies in 7631, capacity
36+20+4+1=61<70, so is root/frame. If one were nonframe it would use
all four active axes; its killed seven would be uncorrected. That
reduces inside corrections to at most three, forcing at least five
outside axes and at most three active axes, impossible for that root.
Thus both kernels are frame lines. They are distinct, because a joint
kernel of both seven coordinates would lie in 631, below distance 53.
Hence D' is their full two-frame plane.

The six-piece coefficient is nonzero in both frame words, because
omitting it leaves 7+3+unit of capacity 41<53. The rank-three
coefficient is also nonzero in both: omitting it gives frame-target
capacity 32+20+1=53<56. Neither intermediate piece can therefore be
corrected, since a frame row vanishes on at least one of two distinct
frame axes. At most the two sevens remain corrected inside. Reaching
n_c>=8+c9' forces c9'=0, all six outside corrections, and both seven
corrections. In a seven-kernel frame word the remaining corrected seven
is matched to that frame; its target capacity is then
20+20+4+1=45<56, contradiction.

### 77542 and 77632

Their sum 25 forces six outside eights and n_c>=9. At most four
inside pieces can be corrected, so D' has at most three active axes.
Killing either seven leaves a word of support at most 58 for 77542,
or 62 for 77632, strictly below 70. The kernel is root/frame and
the axis bound makes it frame. The two kernel lines are distinct,
since omitting both sevens leaves capacities 22 or 26, below 53.
Thus D' is their two-frame plane.

For 77542 each such frame word has target capacity
32+12+8+2=54<56, immediately impossible. For 77632, the six-piece
coefficient cannot vanish in either frame word (7+3+rank2 has
capacity 42<53), nor can the three-piece coefficient (7+6+rank2
has frame-target capacity 32+20+2=54<56). These two intermediate
pieces cannot be corrected, while the rank-two piece is uncorrected.
There are at most two inside corrections, giving n_c<=2+6=8<9.

All fifteen exclusions therefore apply to the actual transferred L
without identifying L with the global threshold space. This closes
every high-containing adapted t=3,d=3 actual inside profile under the
stated raw budget and retained written inputs.
