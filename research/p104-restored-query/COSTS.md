# Arithmetic, ownership, and width of the restored query

This ledger separates the explicit strict direct schedules from the source
program's native and weighted-ADD inventory. All counts are constructive
logical counts for the stated model, not minima, physical tape tariffs, or
a recursive multiplication invoice. The [proof](PROOF.md) gives the exact
common coefficient/query interface and source restoration.

## 1. The two direct invoices

Let \(n=2^r\), \(p=rn/2\), and
\(T=(2,9,16,27,51)\). Both schedules implement
\(q\mathrel{+}=E_r\sum_{t\in T}a_t\) and return all 52 coefficients.
The finite implementation accepts ranks 0 through 9; the source caller has
r=9. The five separate dirty D banks are unchanged and may be carried through.

The owned-zero-bank mode performs five full-bank gathers, one Q ADD,
and five ungathers. The temporary-terminal mode performs four gathers,
one Q ADD, and four ungathers, temporarily using \(a_2\).
Both use E and its inverse once. The strict lowering below gives

\[
A_{\rm zero}=14p+22n,\qquad A_{\rm terminal}=14p+18n,\qquad
D=p,\qquad H_{\rm exact}=2p,
\]

where A excludes doubling, D counts explicit real doubling, and H counts
checked exact real halving.

| Rank-nine quantity | Owned zero bank | Temporary terminal bank |
|---|---:|---:|
| Gaussian entries per bank | 512 | 512 |
| Newton pairs per direction | 2,304 | 2,304 |
| Full Gaussian-bank ADD/SUBs | 11 | 9 |
| Strict real ADD/SUB, excluding doubling | 43,520 | 41,472 |
| Real doublings | 2,304 | 2,304 |
| Exact real halves | 4,608 | 4,608 |
| ADD/SUB when a doubling costs one ADD | 45,824 | 43,776 |
| Additional Gaussian banks | 1 | 0 |
| Separate real zero scratch words | 1 | 1 |
| Gaussian zero-bank initialization/erasure | 1 each | 0 |
| Real scratch initialization/final disposal | 1 each | 1 each |

The real scratch has 4,608 verified zero exits, one after every multiplication
or division by \(\pi\), and is zero at the final boundary. The temporary-terminal
mode returns its initially dirty work bank; it does not assume that bank is zero.
All 52 coefficient banks remain named outputs. Their storage cannot be discarded
because the query ignores 47 of them.

For chosen real-doubling and exact-halving tariffs \(\delta,\eta\), the arithmetic
subtotal is \(A+\delta D+\eta H_{\rm exact}\), plus the specified ownership,
zero, control, access, and storage costs. Unknown tariffs are not assigned zero.

## 2. Strict real-register lowering

The allowed updates are \(x\mathrel{+}=y\), \(x\mathrel{-}=y\) on distinct
registers, an explicitly counted doubling, and an exact half checked before
division. There is no unpriced assignment \(x\leftarrow y-x\).

With \(\tau=0\), multiplication of the Gaussian word \((a,b)\) by \(\pi=1+i\)
uses the following updates in order:

| Step | Update |
|---:|---|
| 1 | \(\tau\mathrel{+}=a\) |
| 2 | \(a\mathrel{-}=b\) |
| 3 | \(b\mathrel{+}=\tau\) |
| 4 | \(\tau\leftarrow2\tau\) |
| 5 | \(\tau\mathrel{-}=a\) |
| 6 | \(\tau\mathrel{-}=b\) |

Writing the original components as \(a_0,b_0\), the result is
\((a_0-b_0,a_0+b_0)\). The last three scratch states are
\(2a_0,a_0+b_0,0\). This costs five ADD/SUBs and one doubling.

Division on the true image of \(\pi\) uses:

| Step | Update |
|---:|---|
| 1 | \(\tau\mathrel{+}=a\) |
| 2 | \(\tau\mathrel{+}=b\) |
| 3 | \(\tau\leftarrow\tau/2\), exact |
| 4 | \(b\mathrel{-}=a\) |
| 5 | \(b\leftarrow b/2\), exact |
| 6 | \(a\mathrel{+}=b\) |
| 7 | \(\tau\mathrel{-}=a\) |

The two numerators \(a_0+b_0\) and \(b_0-a_0\) are even on this image,
including for negative inputs. The outputs are
\(((a_0+b_0)/2,(b_0-a_0)/2)\), and scratch is zero.
This costs five ADD/SUBs and two exact halves.

One forward Newton pair \((u,v)\mapsto(u,u+\pi v)\) first multiplies the high
Gaussian word by \(\pi\), then adds the low word: seven real ADD/SUBs and one
doubling. The inverse first subtracts the low word, then divides by \(\pi\):
seven ADD/SUBs and two exact halves. Encoding visits address bits ascending;
decoding visits them descending. The Q update leaves the work bank unchanged,
so all inverse divisions are on the preceding actual image.

The strict machine records every arithmetic update and checks its count and
width. Its Python implementation copies arrays for comparison; Python object
allocation is not the storage invoice of the logical in-place schedule.
Equal-valued distinct banks are admitted. Aliased banks, query aliasing,
duplicate terminal slots, Boolean integer fields, dirty real scratch, and
unavailable signed exact halves have explicit rejection controls.

## 3. Finite signed widths for the direct schedules

Let H bound all real and imaginary input coefficient components and J bound
those of Q. The sum of five terminals has component bound \(5H\).
The exact maximum real absolute row sum of E is

\[
g_r=\sum_{k=0}^r\binom rk
\bigl(|\operatorname{Re}\pi^k|+|\operatorname{Im}\pi^k|\bigr).
\]

This follows from \((E_ra)_x=\sum_{s\subseteq x}\pi^{|s|}a_s\). In particular,
\(g_9=3363\). Disjoint coefficient supports in a Newton pair show that both
its complete boundary and its pre-low-ADD value are bounded by \(5g_rH\).
Decoding follows those same image values in reverse.

Scratch sums and differences in the strict \(\pi\) programs are covered by
the conservative factor four over that payload bound. Therefore

| Quantity | Sufficient rank-nine component bound |
|---|---|
| Stored encoded terminal sum | \(16{,}815H\) |
| Every non-query real arithmetic register | \(67{,}260H\) |
| Query register | \(J+16{,}815H\) |

Gather and ungather partial sums are bounded by \(5H\), and unvisited
coefficients keep their H bound. A sign bit plus enough magnitude bits for
\(\max(67{,}260H,J+16{,}815H)\) suffices. No extra fractional precision is
required. These conservative bounds are checked against observed peaks after
every strict primitive; the Python model uses unbounded integers and does not
simulate fixed-width overflow. Physical signed representation is still a
caller implementation obligation.

## 4. Exact inventory of the literal core

The 257-event producer, 15-event first collector, and 252-event selective
return have the following source-bound inventory. Codec preparation and
decoding are additional, as in the next section.

| Quantity | Count |
|---|---:|
| Core events | 524 |
| Native occurrences | 402 |
| Native rank mass | 722 |
| Completed native pairs | 184,832 |
| Forward / inverse native pairs | 94,208 / 90,624 |
| Monomial wrapper occurrences | 804 |
| Wrapper permutation cycles | 23,168 |
| Direct Gaussian payload SWAPs | 388,480 |
| Weighted ADDs | 120 |
| Quarter / unit ADDs | 104 / 16 |
| Private C zero / zero erase | 1 / 1 |

Each rank unit acts on 256 pairs. A wrapper cycle of length l uses \(l-1\)
Gaussian payload SWAPs, giving \(804(512)-23168=388480\). Inversion preserves
cycle lengths. The 411,648 wrapper entries have phase histogram

| Phase multiplier | Entries |
|---|---:|
| 1 | 142,512 |
| i | 78,336 |
| -1 | 112,464 |
| -i | 78,336 |

The histogram does not identify the operator: the actual permutation, phase
placement, and event order are bound and executed separately. Each literal
pair also has a Gaussian quarter turn.

Using the inherited pair's component formula, before wrapper/phase lowering,
the component arithmetic inventory is:

| Component operation | Count |
|---|---:|
| ADD/SUB evaluations: \(8(184832)+1024(120)\) | 1,601,536 |
| Native signed-floor half evaluations: \(4(184832)\) | 739,328 |
| Exact real halves for the quarter donors | 212,992 |
| Doublings restoring those quarter donors | 212,992 |
| Native Gaussian quarter turns | 184,832 |

The quarter count includes a closed donor-preserving implementation:
temporarily divide each donor real component twice, perform the signed ADD,
and double that donor component twice to restore it. Each quarter bank operation
therefore has 2,048 exact halves, 1,024 ADD/SUBs, and 2,048 doublings.
Its donor is Gaussian-divisible by four at the actual read, and this owned-source
caller permits the temporary mutation. A strictly read-only donor would instead
need a separately priced divided-copy and cleanup implementation.

The native signed-floor formula, wrapper SWAPs, and phase applications remain
named native/component operations in this table. Their full strict physical
lowering, arithmetic scratch, address/control work, and tariffs are not included
in the 1,601,536 subtotal. In particular, it is not advertised as a complete
strict-register bill comparable term-for-term with section 1. The direct
schedules have no native transports, wrapper permutations, or quarter ADDs;
this is an explicit structural simplification for the declared coefficient
interface, not a proof of platform-independent speedup or global optimality.

The primary receipt's measured core peak is explicitly the maximum at
whole-event bank boundaries. It does not measure internal native scratch,
codec intermediates, physical control, or finite-width overflow.

## 5. Both codec directions remain in the reference caller

The retained [PR3467 cost ledger](inputs/PR3467_COSTS.md) prices its explicit
52-bank codec. It is included byte-for-byte and credited, rather than rerun as
a new historical cost theorem. Per direction it uses 158 native occurrences,
rank mass 281, 71,936 native pairs, 331 monomial wrappers, and 159,020 Gaussian
payload SWAPs. Across both directions, the closed reference therefore contains:

| Structural operation, codecs plus core | Count |
|---|---:|
| Native occurrences | \(158+402+158=718\) |
| Native rank mass | \(281+722+281=1284\) |
| Native pairs | \(71936+184832+71936=328704\) |
| Monomial wrappers | \(331+804+331=1466\) |
| Gaussian payload SWAPs | \(159020+388480+159020=706520\) |

The encoder also has 119,808 Gaussian Newton ADDs, 129,992 Gaussian
multiplications by \(\pi\) including profiles, 5,120 Gaussian doublings for
positive terminal 4, and 47 full-bank differences. The decoder reverses those
operations with checked exact divisions and full-bank partial sums.

The inherited ledger distinguishes its component-arithmetic counts from the
repository's strict ADD tariff: its optional three-step component SWAP permits
a source-minus-target overwrite. Those optional totals are not combined with
the strict direct schedule here. Any full strict lowering of that reference
codec must also price its arithmetic scratch, phases, and ownership contract.

Inherited sufficient coefficient-to-prepared-Y width is \(244992H\) per real
component, with a \(612480H\) bound for the named encoder's pair work. Its inverse
ledger gives bounds for an admitted prepared-Y input. These are scoped to that
codec and are not silently used as a full physical-controller width certificate.

## 6. Obligation and decision ledger

| Obligation | Status | Evidence or remaining work |
|---|---|---|
| Exact closed coefficient/query identity | Proved, locally replayed | Selective return in PROOF; two literal implementations and full-array agreement |
| Terminal slots, source frames, dirty compensation | Source-bound and checked | Frozen WORD/NATIVE, explicit event list and adverse controls |
| Larger-domain observable quotient | Proved, formula/fixture checked | Shared five-active section and kernel quotient; no new readout range |
| All coefficient and dirty-D outputs returned | Proved and checked | Both caller implementations; both strict direct schedules |
| Direct logical arithmetic and zero cleanup | Constructive upper bounds | Strict primitive traces, exact half checks, zero exits and invoices |
| Direct finite signed widths | Proved conservative bounds | Row-sum argument and per-primitive observed peaks |
| Native/core/codec structural inventory | Source-bound or credited | Core counted here; exact inherited codec ledger retained |
| Physical caller with these coefficient meanings | Unknown | Name an actual supplied input and required output contract |
| Physical zero generation, addressing, routing, control, primitive tariffs | Unknown | Specify and price the actual implementation |
| Omitted full-prefix histories and external ports | Outside scope | Use or audit the distinct predecessor scopes; no closure inferred here |
| Fast recursive realization and complete supplier budget | Unknown | A changed fully paid route is required |

**Family decision: narrow and stop at this caller/observability audit.**
The result resolves a named acceptance gap: a large entrance index alone does
not create an enlarged collector range or a new query. It also supplies an
exact returned alternative in two ownership contracts. The unchanged-profile
599/584 stop, all original hypotheses, and the selected frontier remain intact.
A further round needs a different actual observable/caller or a changed,
fully priced mechanism that can affect the supplier decision.
