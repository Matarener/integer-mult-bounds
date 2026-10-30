# Complete optimal dyadic representations for P104

The complete public and private construction saves **24,334 scalar
primitives per call**, or **438,012 across18 calls**. The actual allowance
falls224,880 to200,546, including384 entry and399 exit SCALEs. This is the
minimum over all signed power-of-two representations at the stated source
SCALE epochs, with every public boundary conversion charged.

The source is PR5824. Its private optimum is predecessor work. This package
optimizes all1,540 representation nodes and22,763 weighted graph edges.
It emits the full26,351-instruction word, not only a numerical objective.
All paid ranks, productive targets and the12-slot private pool stay fixed.
No new kappa or selected-frontier change is claimed.

## Exact global optimum without an exponent box

Write a stored field as x'=g*x with signed dyadic g. An ADD/COPY coefficient
q becomes q*g_target/g_source. A SCALE becomes q*g_after/g_before. The
public entry uses g and its exit uses1/g. Those operations are explicit in
the emitted word and the invoice. Owned reset boundaries still have zero
value. There is no free conversion of nonzero data.

For each source coefficient q=m*2^e with odd m, the variable tariff is
2*abs(e+x_a-x_b). Aggregate repeated edges with weight w. Public entry and
exit edges connect their actual epochs to anchor0. The full exponent
objective is P=sum w*abs(e+x_a-x_b).

CERTIFICATE.json gives integer potentials x and integer edge values y.
The checker requires abs(y)<=w and zero net y flow at every node. Therefore,
for every real or integer potential vector,

```
P >= sum y*(e+x_a-x_b) = sum y*e.
```

The emitted potentials attain equality. The common optimum is10,471,
compared with22,168 at zero gauge. This proves a global unbounded-exponent
minimum without trusting an optimizer or a guessed finite search range.
The certificate's exponents lie from-3 to4.

Signs have a separate exact optimum. ADD/COPY signs have no extra source
charge. Each private SCALE sign can be absorbed along its epoch chain.
For each public chain, the parity of its negative SCALEs is the only
remaining sign obstruction after entry and exit are included. There are
112 odd public chains. The old word has582 negative SCALEs. Thus the exact
complete saving is2*(22168-10471)+2*(582-112)=24,334.

The optional search uses NetworkX3.5's integer network simplex on a
min-cost circulation. The independent standard-library checker needs only
the retained primal and dual. Network simplex is predecessor software;
this package does not claim a new flow algorithm.

## Larger word, explicit bounds

The optimum has388 more instructions than the source because boundary
conversions have a cost. The old endpoint check's26,000-instruction cap
therefore does not apply. The adapted local.py exposes an explicit positive
operation bound, with the old26,000 default. Every other source check is
byte-identical, and verify.py checks that exact adaptation.

The new strict bound is27,504: source length plus two possible public
boundary SCALEs per field, plus one. The actual length is26,351. No bound
is silently disabled. Exact positive scalar propagation gives maximum
193235952662117675775/512. Under the retained unitary native-chart premise,
this is below the source envelope2^(16*26000). The old scalar-growth budget
therefore still holds by a direct calculation, although its old instruction
cap does not. This is a conservative growth bound, not a sharp error theorem.

The actual scalar bill plus all retained local route/helper/owned terms is
5,521,546, below the source's10^7 per-call allowance. All source query ranks
and public interfaces agree. Full global event/compiler hashes and rounded
child error contracts have not been regenerated or admitted here. The
five framework assumptions, exact reset premise and physical tape/ROW
obligations remain. These limits are separate from the proved scalar optimum.

## Verification and reproduction

```sh
python3.12 -B scripts/research_package.py --package research/p104-complete-dyadic-gauges
```

Normal and optimized registered commands need only Python3.12's standard
library. They authenticate every frozen input, check the conserved dual,
rebuild the complete word, and prove the exact representation invariant at
every scalar event and every native call. The same linear native operator
commutes with each declared scalar gauge; its frame, rank and phase remain
source dependencies. Complete782-axis forward and611,524-coefficient reverse
checks prove the arbitrary public and dirty-owned endpoints. Controls reject
a false optimum, excess dual capacity and an omitted public entry SCALE.

To generate another candidate, use an isolated environment with
`networkx==3.5`, then run `python3.12 -B search.py --output candidate.json`
from this package. Search has no role in acceptance: the default verifier
checks the retained certificate and complete receipts without NetworkX,
Git or network access. See the official
[network_simplex contract](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.flow.network_simplex.html).

## Open next questions

Among equally cheap complete words, can a different exact gauge reduce
maximum field amplification or completed-operation error? Start from the
retained optimal dual. Its complementary-slackness conditions describe all
cost-optimal potentials. A new norm result must use the actual word and
keep boundary SCALEs and the full local allowance. PR5819's error constants
apply to another frozen word and must not be transferred without replay.

## Credit

Ali Romman with substantial OpenAI Codex assistance; no subagents. Retain
PR5824/5822/5812 and all P104 authors in inputs/NOTICE. The private-gauge
result supplies the representation premise. NetworkX developers and their
network-simplex references supply the search software. New work is the
complete anchored source graph, exact unbounded dual, explicit boundary
conversion word and complete tariff/bound verification. Apache-2.0.
Coordination: https://github.com/CrocSwap/integer-mult-bounds/discussions/5804.
