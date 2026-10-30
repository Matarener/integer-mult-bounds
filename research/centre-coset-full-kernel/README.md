# The 4,080-owner centre block saves exactly one information coordinate

This answers the second open question of [PR3656](https://github.com/CrocSwap/integer-mult-bounds/pull/3656),
head `69e745992b966c647e10696b980cb4c96d7ebeed`. Allowing all 112 ports on
its exact subgroup coset does not reveal a larger common kernel. Its dimension
is exactly **one**, and the minimum additional scalar linear observations are
**424,319**. A collector using 420,240 ordinary coordinate reads and 4,079
differences attains that information minimum in the declared source-field model.

The finite certificate partitions all port output cosets: `(0,6,85)` form one
rank-two class and the other 109 ports are singleton classes. Their columns
force every nontriple input to vanish. The remaining scalar amplitude must be
constant on the connected 4,080-owner subgroup. [PROOF.md](PROOF.md) proves
the all-coefficient implication, the sharp information bound and the explicit
attaining interface. [RESULT.json](RESULT.json) records the exact finite data.

The known witness therefore saves only one of 424,320 information coordinates.
In the explicitly conditional implementation charging one rank-one recursive
child per additional scalar observation, repair exceeds even the entire
removable centre path by **163,199 rank units**, granting all other costs free.
That replacement fails for every saving parameter `0<=a<=1` with unchanged
width, stock and call normalization. Information coordinates do not establish
a universal recursive tariff; compressed children and changed interfaces
remain outside this screen. There is no supplier, new kappa or selected-frontier
claim.

## Exact scope

The model retains PR3071/3291's regular cover owners, independent constant
source payloads, whole later-query reader, and inherited native common-frame
and source-adapter premises. The old reader is `Sx(g)=R x(g)` and the later
reader is `Tx(d)=sum_p R[:,p] x_p(d rho_p)/4`. The source block is any one
left translate of `L=<rho_0 rho_6,rho_6 rho_85>`; all 112 source ports are
allowed. Extra observations are scalar linear; decoding may be globally
nonlinear. Equal arbitrary dirty inputs suffice for the lower bound. Attainment
concerns the displayed pure source-field interface; unknown native dirt offsets
and reversible acquisition/restoration still require their own implementation.

This is a finite exact source certificate plus a written proof over Q and C.
It is not a formal-kernel proof, an all-size physical supplier, a minimum-support
classification, or a native cold replay. No other block or union of blocks is
screened.

## Reproduce

From a repository checkout with the declared pinned inputs:

```sh
python3.12 -I -B research/centre-coset-full-kernel/verify.py
python3.12 -I -O -Werror -B research/centre-coset-full-kernel/independent.py
python3.12 -B scripts/research_package.py --package research/centre-coset-full-kernel
```

The first checker uses exact column-major GF(2) group multiplication and
rational elimination. The second uses independently reconstructed row-major
routes and separate elimination, sharing the authenticated inherited scalar
source extraction. Their different roles and exact coverage are described in
[INDEPENDENT.md](INDEPENDENT.md). The source extraction and conditional native
interpretation are inherited evidence, not newly independent claims.

Controls reject the wrong subgroup, a changed route, a changed scalar column,
and executable-source corruption before execution. The omitted-owner witness
shows why deleting one raw coordinate read fails; an optimal collector must
retain differences instead. Additional independent controls are recorded by
the second checker. These checks make no claim of independent human review or
hosted CI; local validation is recorded separately in [VALIDATION.md](VALIDATION.md).

## Sources and credit

Canonical base `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority revision 6;
[SOURCES.json](SOURCES.json) pins the actual executable source closure and
selected record. The [canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/3062#discussioncomment-19025999)
records the bounded scope and claim lifecycle. Full outgoing review and run
receipts are retained outside the disposable checkout; they are not hosted CI.

Matarener (donor Mark), with Claude assistance, supplied the PR3656 coset,
known witness and this exact open question. Sagar Thakrar/PR3291 supplied the
authenticated loader; Ross Richardson/PR3071 the block-repair model and
independent extraction. Credit also dcharb78/PR3147, Gonzalo Mier/PR3097,
Sudarsh Chaturvedi/PR3168, Aaron Wang/navinor, ywz65 and all retained selected
construction authors. Ross Richardson with substantial OpenAI Codex GPT-6.1
Sol assistance, including separate mathematical specialists, developed this
full-kernel reduction, interface and checks. Apache-2.0; predecessor files stay
unchanged. Separate AI executions are not independent human review.

## Open next questions

- A different explicit block could have a larger common kernel. It needs a
  changed source/consumer budget before another search; this result gives no
  minimum-support or global-compression theorem.
- A repair consumer using compressed higher-rank children could have a different
  per-information-coordinate tariff. First specify its actual input/output
  frames, source access, dirty restoration and full normalized moment. No such
  implementation or favorable complete budget is supplied here.
