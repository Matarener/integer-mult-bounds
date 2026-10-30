# Direct preparation cost and quotient audit

This note prices the explicit preparation from **52 owned Gaussian coefficient
banks to the admitted Y module**. It uses the actual inverse donor paths,
the extra right wrappers, and the groupwise bank differences. It does not
price an arbitrary pre-existing Y caller, the other events of the original
prefix, or the 675 external-recipient histories.

The inventory was independently reconstructed from the frozen WORD and
NATIVE data, without importing the package source layer, classifier, or a
predecessor executable. It is a constructive direct arithmetic schedule,
not a minimum, a physical tape tariff, or a supplier improvement. The
[proof](PROOF.md) states the admission theorem and codec contract;
[SOURCES.json](SOURCES.json) retains the exact origins and mathematical
dependencies.

## 1. What the quotient counts mean

Put $R=\mathbb Z[i]$, $\pi=1+i$, and $B=B_9$. The 32 intervals without
a D transport contribute diagonal exponents
$\max(4-|S|,0)$. The 15 rank-one intervals contribute
$\max(4-|S\setminus\{0\}|,0)$. Each of the five terminal coordinates
contributes exponent four on all 512 coefficients.

| Exponent | No-transport multiplicity | Rank-one multiplicity | Terminal multiplicity | Aggregate |
|---|---:|---:|---:|---:|
| 0 | 32 × 382 | 15 × 326 | 0 | 17,114 |
| 1 | 32 × 84 | 15 × 112 | 0 | 4,368 |
| 2 | 32 × 36 | 15 × 56 | 0 | 1,992 |
| 3 | 32 × 9 | 15 × 16 | 0 | 528 |
| 4 | 32 × 1 | 15 × 2 | 5 × 512 | 2,622 |

The quotient of $B^{52}$ by the exact stagewise entrance $\mathcal M$ is

$$
(R/(\pi))^{4368}\oplus(R/(\pi^2))^{1992}
\oplus(R/(\pi^3))^{528}\oplus(R/(\pi^4))^{2622}.
$$

The exponent-zero coordinates have trivial quotient factors. All 52 input
banks remain present; each admitted module has the same full Gaussian rank.
The index is

$$
[B^{52}:\mathcal M]
=2^{4368+2(1992)+3(528)+4(2622)}
=2^{20424}.
$$

For the ideal terminal-only module $\mathcal I$ from PR #3426 and the
stronger product entrance $\mathcal P=(4B)^{52}$, the inclusions are strict:

$$
\mathcal P\subsetneq\mathcal M\subsetneq\mathcal I,\qquad
[B^{52}:\mathcal I]=2^{10240},\quad
[B^{52}:\mathcal P]=2^{106496}.
$$

Consequently $[\mathcal I:\mathcal M]=2^{10184}$ and
$[\mathcal M:\mathcal P]=2^{86072}$. These quantify the additional
stagewise constraints and the larger allowed correlated set. They are not
saved physical bits, compressed storage, or eliminated operations.

The elementary checks behind the first two rows are

$$
\sum_{j=0}^{3}(4-j)\binom9j=187,\qquad
2\sum_{j=0}^{3}(4-j)\binom8j=280,
$$
$$
32(187)+15(280)+5(2048)=20424.
$$

## 2. Actual path reconstruction

The independent counter finds the first C allocation at zero-based event
2025, derives the five D source roles from the following five collector ADDs,
and finds their earlier quarter reads in the original order. It obtains group
sizes 3, 7, 7, 11 and 24.

For each nonterminal read, it follows that D bank's native history from its
initial empty frame to the read frame. It separately checks the interval to
the next read. Every selected native occurrence is bound to the archive's
old frame, new frame and rank. The 32 empty intervals and 15 single rank-one
intervals yield 47 preparation paths.

A rank-one coordinate first needs the inverse of its actual right wrapper.
It then uses the inverse D path, with native occurrences reversed and each
native inverted in its actual factor order. This is a constructive schedule
on independently supplied coefficient arrays. Repeated uses of one source
recipe are counted once per prepared array, not once per distinct archive
record.

| Preparation part | Native occurrences | Rank sum | Wrapper occurrences | Wrapper cycles | Gaussian payload SWAPs |
|---|---:|---:|---:|---:|---:|
| Inverse donor paths | 158 | 281 | 316 | 9,748 | 152,044 |
| Extra inverse right wrappers | 0 | 0 | 15 | 704 | 6,976 |
| Total | 158 | 281 | 331 | 10,452 | 159,020 |

Each rank unit acts on 256 address pairs, giving **71,936 pair applications**.
Each wrapper permutation is reconstructed on all 512 addresses and checked
to be a bijection. A cycle of length $l$ uses $l-1$ direct payload SWAPs,
so the total is

$$
331(512)-10452=159020.
$$

These are reversible gates on two owned Gaussian payload words. They need no
separate clean swap ancilla. This is different from the credited predecessor
schedule using $N+c$ swaps through one owned zero Gaussian scratch word;
those two invoices must not be mixed. Permutation cycles are unchanged by
taking the inverse.

## 3. Phases and the complete arithmetic subtotal

The wrapper phase is evaluated at its source address, using its recorded
constant phase, linear terms and only strict-upper quadratic terms $j<k$.
The inverse has the negative phase at the corresponding permuted address.
Its histogram is therefore the negated original histogram, since the
permutation is bijective.

| Gaussian multiplier | Encoder inverse wrappers | Decoder forward wrappers |
|---|---:|---:|
| $1$ | 61,696 | 61,696 |
| $i$ | 45,952 | 29,312 |
| $-1$ | 32,512 | 32,512 |
| $-i$ | 29,312 | 45,952 |
| Total | 169,472 | 169,472 |

The histogram does not substitute for correct phase placement. Source
authentication and the actual ordered wrapper implementation bind that
operator. The identity entries need no arithmetic; their address/plan visits
are still part of execution.

All 52 Newton encoders have $52\cdot9\cdot256=119808$ tensor pairs.
Nonterminal profile scaling adds 10,184 multiplications by $\pi$.
Terminals use positive $4$, implemented by two Gaussian doublings per
entry; using $\pi^4=-4$ without its sign would change the parameter map.

| Primitive in preparation | Count |
|---|---:|
| Gaussian ADDs in Newton encoders | 119,808 |
| Gaussian multiplications by $\pi$, including profile diagonals | 129,992 |
| Gaussian terminal doublings | 5,120 |
| Full-bank differences | 47 |
| Gaussian subtractions in those differences | 24,064 |
| Literal native pair applications | 71,936 |
| Native Gaussian quarter turns | 71,936 |
| Gaussian payload SWAPs | 159,020 |
| Wrapper phase applications, including identity entries | 169,472 |

A Gaussian ADD/subtraction and a multiplication by $\pi$ each use two
real ADD/subtract operations. The inherited literal pair uses eight such
operations and four signed floor halves, with its quarter turn listed
separately. This gives **1,123,216 real ADD/subtract operations plus 10,240
real doublings**, or **1,133,456** when a doubling is charged as one addition.
There are also **287,744 native real floor halves**, together with the
explicit swap and phase primitives above.

For a version lowered entirely to the stated real arithmetic primitives,
use three ADD/subtract operations per real-component SWAP, hence six per
Gaussian SWAP. A quarter turn uses one real-component SWAP and one
negation. A Gaussian minus sign uses two negations. The three-operation
real SWAP is explicitly

```text
x <- x+y
y <- x-y
x <- x-y
```

This component-arithmetic model permits a source-minus-target overwrite.
A primitive set restricted to `target += +/-source` needs an additional
target negation, so these optional lowered totals are not the repository's
strict ADD tariff. Counting each displayed negation as `0-value` gives
2,741,400 component additions/subtractions for preparation and 2,731,160
for the inverse, with halves still separately charged.

| Additional lowering | Count |
|---|---:|
| Real ADD/subtract operations for Gaussian payload SWAPs | 954,120 |
| Wrapper and native quarter-turn component SWAPs | 147,200 |
| Real ADD/subtract operations for those component SWAPs | 441,600 |
| Explicit real negations | 212,224 |

The fully lowered encoder therefore uses **2,529,176 real ADD/subtract
operations**, **212,224 real negations**, and **287,744 native real floor
halves**, under this direct model. Doublings are included in that ADD count.
Addressing, iteration, compilation and the eventual bit/tape tariff remain
separate costs.

The inverse codec has the same path/swap/phase-count totals. Its base real
ADD/subtract count is **1,123,216**: terminal doublings become exact
divisions. It has **259,984 real exact halves** from all Gaussian
$\pi$-divisions and **10,240 terminal exact halves**, in addition to the
same **287,744 native floor halves**. With the same swap/phase lowering,
its ADD/subtract count is **2,518,936**, with **212,224 real negations**.
It rejects unavailable divisions; it does not round inputs into the module.

## 4. Conservative finite width

Let $H$ bound every real and imaginary component of each of the 52 raw
coefficient arrays. The exact real row-sum gains from coefficients to the
three local profile arrays are

$$
G_0=3456,\qquad G_1=3828,\qquad G_T=13452.
$$

For example,
$$
G_0=\sum_{d=0}^{9}\binom9d
2^{\lceil\max(4,d)/2\rceil},
$$
$$
G_1=\sum_{d=0}^{8}\binom8d
\left(2^{\lceil\max(4,d)/2\rceil}
+2^{\lceil(\max(4,d)+1)/2\rceil}\right).
$$

The coefficient supports entering each Newton pair are disjoint, so these
nonnegative absolute row sums also bound the intermediate encoding states.
Terminal doubling prefixes are bounded by $G_T H$.

A 512-entry Gaussian array whose real and imaginary components are bounded
by $M$ has complex Euclidean norm at most $32M$. Each actual monomial and
complete coordinate stage is unitary. The native-path portion of the literal
preparation agrees with those ideal stages because its native-path inputs
and stages remain in $B_9$. Therefore:

| Stored or work quantity | Sufficient component bound |
|---|---:|
| Nonterminal inverse-path payload | $122496H$ |
| Terminal partial sum | $13452H$ |
| Any final Y difference | $244992H$ |
| Literal pair arithmetic work | $612480H$ |

The terminal/nonterminal difference separately has bound $135948H$, already
covered by the common Y bound. The factor-five pair bound covers differences,
signed halves, middle values and reconstruction temporaries. Lowering a
payload SWAP to additions introduces at most a doubled intermediate; a
quarter turn of a pair difference introduces at most four times the payload
bound. Both fit within the same $612480H$ allowance.

For the inverse codec, let $J$ bound the components of an admitted prepared
Y input. A group has at most 24 members, so its partial sums are bounded by
$24J$. Forward paths are bounded by $768J$, and the Newton decoder's
component row-sum gain is at most 32. Subsequent exact profile divisions do
not increase the component bound. Thus $24576J$ bounds stored decoding
values and $98304J$ conservatively bounds decoding work.

These are sufficient bounds for this codec. Signed storage with an integer
bound $M$ may use $1+\lceil\log_2(M+1)\rceil$ bits. Actual widths must
also cover the six separately supplied dirty banks and any surrounding
caller; no current external recipient width is established here.

## 5. Ownership, logical target and stopping decision

The in-place encoder uses the 52 owned coefficient banks themselves:
26,624 Gaussian payload words. The six independently admitted dirty D/Q
banks add 3,072 Gaussian words and are not modified by preparation.
The bank-difference step runs backward within each group, so the previous
partial sum remains available until its last use. The inverse runs forward.
Constant arithmetic work space suffices for the stated arithmetic gates;
the Python reference's allocated lists are not this physical layout.

An encoder followed immediately by its inverse restores its coefficient
input. This does not prove that an intervening producer or consumer returns
the prepared banks in the required values, frames, layout and ownership.
Nor does the encoder admit arbitrary pre-existing numerical Y values while
preserving their original interpretation. It supplies a different, explicitly
parameterized entrance contract.

If raw coefficient arrays must remain borrowed and unchanged, an optional
copying boundary additionally needs 52 owned banks and 52 copy ADDs.
Cleanup needs the actual prepared banks returned before inverse decoding,
then 52 subtractions against the borrowed originals and exact zero disposal.
That return is a separate caller obligation. The copies, lifetimes and
cleanup do not acquire zero cost from the module isomorphism.

| Obligation | Status here |
|---|---|
| Direct finite preparation and inverse arithmetic | Constructively counted |
| Actual frame-path, wrapper-cycle and phase inventory | Independently reconstructed from pinned source |
| Codec magnitude bounds | Proved conservative bounds |
| Preparation of the six arbitrary dirty B-domain entrances | Separate input/codec obligation |
| Preservation of borrowed coefficient inputs | Additional copies, owners and cleanup |
| Physical routes, controls, bounded-width gate costs and liveness | No complete physical tariff supplied |
| Omitted original-prefix and external-recipient histories | Outside this cone result |
| Compatible complete consumer and recursive supplier bill | Open |

The unchanged five-forward/four-dual consumer profile and coverage law still
have the credited $599/584>1$ obstruction. A larger exact input domain does
not change that law or remove native children. This result narrows the missing
admission question; it does not reopen the stopped supplier construction or
claim a new $\kappa$.

The actual word and native recipes remain ywz65's PR #2586 contribution,
retained through Arham Tahir's source package. Nick Petalas's PR #3426 supplies
the ideal correlated classification and this literal-admission handoff; his
PR #3416 supplies the inherited covariance theorem. Clear1nsight's PR #3382
and PR #3423 supply the Newton application and prior actual-interface work.
Tekalign's signed-floor and native-comparison lineage, Ross Richardson's
exactness-domain work, and Jose Manuel/Vasek's conditional cost stop retain
their credit. This audit used separate automated source/count reconstruction,
not external human or formal proof-kernel verification.

Prepared by Clear1nsight with substantial OpenAI assistance. Apache-2.0.
