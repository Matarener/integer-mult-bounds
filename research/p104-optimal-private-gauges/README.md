# Optimal private dyadic gauges for the P104 word

The complete twelve-slot P104 word has a smaller exact scalar implementation.
Its allowance falls **224,976 to 224,880** per call: 96 saved per call and
1,728 across 18 calls. The constructor changes 70 source instructions and
removes 12 private SCALEs. The emitted word has 25,963 instructions.

The gain is maximal over the stated representation grammar: each private
lifetime can choose a signed power of two; each private SCALE can choose a
new such representation. All other event boundaries, native maps and public
representations stay fixed. This is an unbounded integer-exponent optimum,
not only a search in a chosen small box. It is not a global circuit optimum
or a new kappa. The paid query and productive-target profiles are unchanged.

## Representation and exact cost

For a logical field x, store x'=g*x, where g is a signed power of two. At
ADD or COPY from s to r, replace q by q*g_r/g_s. At a private SCALE, replace
q by q*g_after/g_before. A coefficient of one removes that SCALE. A change
on nonzero data is therefore paid by the transformed source instruction;
there is no free hidden conversion. INIT and CLEAR reset the owned field.

The source scalar tariff for q=m*2^e, with odd m, has an exponent term
2*abs(e). Its remaining ADD/COPY term depends only on m. For each edge a,b
of the representation graph, the variable term is therefore
2*w*abs(e+x_a-x_b). The public anchor has x_0=0. The source produces 45
private representation nodes in 15 independent anchored components.
Negative private SCALE signs can all be absorbed along their representation
chains. ADD/COPY signs have no extra charge in the retained tariff.

The absolute-value objective falls61 to24. Sign absorption saves another
22 primitives, so the complete saving is2*(61-24)+22=96. The verifier
checks that identity against a fresh replay of the entire emitted word.

## Why the finite certificate proves the unbounded optimum

Each component is connected to the fixed public anchor. Its positive
absolute-value objective has bounded sublevel sets. A minimum occurs at a
vertex of the arrangement x_a-x_b=-e. A spanning tree of tight edges
connects each vertex to the anchor, so every coordinate is an integer sum
of at most n edge offsets. Thus an optimum exists in [-nM,nM], where n is
the component's variable count and M is its largest absolute offset.

Encode x with monotone threshold bits [x>=k] over this proven interval.
The identity abs(u-v)=sum_k abs([u>=k]-[v>=k]) gives a submodular binary
cost table. A monotonicity penalty exceeds the feasible zero-gauge cost.
PR5783 returns a matching flow and cut. Its separate verifier checks
capacity, conservation, cut equality and the original cost without search.
The largest source component has five variables and bound10. Zero-offset
components have the direct optimum zero. No guessed numerical tolerance
or floating-point optimizer is used.

## Whole-word and native checks

The checker proves the exact representation invariant at every scalar
event and every native call on complete rational RAW rows. A native call
uses the same frame pair and rank. Its input changes only by the declared
g, which commutes with the inherited linear native operator. The source
native phases and all-address contracts remain dependencies; this package
does not rerun those proofs or claim a new native mechanism.

Full forward replay checks all782 arbitrary input axes, including dirty
private slots. A separate dense reverse engine checks all611,524 endpoint
coefficients. Every public endpoint, owned cleanup, target, paid rank and
live-slot bound agrees with PR5822. A false cut optimum and a missing read
compensation are rejected. The full word and all certificates are retained
in WORD.json.gz and RESULT.json.

## Reproduction and limits

```sh
python3.12 -B scripts/research_package.py --package research/p104-optimal-private-gauges
```

Python3.12 standard library suffices. Registered normal and optimized
replays authenticate all source and tool bytes. The direct verifier is
Git-free. The exact new word still satisfies the source's coefficient
bound. No sharp precision/error bound is inferred from the cheaper tariff;
PR5819 concerns a different frozen word. Physical resets, tape costs,
compiler, outer obligations and all five framework assumptions remain.
The old conservative complete caller allowance and conditional kappa stay
unchanged. No selected-frontier change or independent admission is claimed.

## Open next questions

Extend the same certified objective to public representation changes, with
explicit entry and exit SCALE costs. This may lower the much larger public
scalar bill. The first step is an anchored graph for those actual source
versions and a matching dual certificate. Its size exceeds the private
components checked here. Any result must emit the full word and prove
its public/native boundary and complete cost, not only a relaxed optimum.

## Credit

Ali Romman with substantial OpenAI Codex assistance; no subagents. Retain
the P104 source credits in inputs/NOTICE and PR5822. PR5783 supplies the
exact binary optimizer and flow/cut checker; its classical graph-cut
lineage remains in vendor files. New work is the source-derived integer
gauge construction, unbounded-domain reduction and complete word proof.
Apache-2.0. Coordination: Discussion5804.
