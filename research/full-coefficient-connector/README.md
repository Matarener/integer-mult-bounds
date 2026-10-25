# Full coefficient demand has optimal overhead exponent 1/c

For every fixed finite characteristic c >= 3, let OPT_c(n) be the minimum
complete-call count for the unsigned, one-dirty-connector interface below,
with all c^n - 1 nonzero coefficient rows. Then

```text
OPT_c(n) = c(c^n - 1) + Theta(c^(n/c))       as n tends to infinity.
```

This is a **scoped proof with a deterministic construction and finite
corroboration**. It settles the growth rate of the overhead, not its leading
constant or any new exact optimum. The construction has exactly c readouts
per output. The lower bound covers every legal word, including words that
buy extra readouts. No new kappa or selected-frontier change is claimed.

This continues the full ternary demand introduced in
[#4238](https://github.com/CrocSwap/integer-mult-bounds/pull/4238), head
`191a905d7adba6695b079f744140a73e832787a8`, and extended to six sources in
[#4244](https://github.com/CrocSwap/integer-mult-bounds/pull/4244), head
`f436d2911351e5be2842208fe96b0b66442323a4`. Their exact small optima are
cited and not rechecked. The new result is the all-n construction and matching
overhead exponent, extended to every finite characteristic. The written proof
is self-contained and does not depend on either pending census.

## Interface

Work over any nonzero unital ring R of characteristic exactly c, with free
modules of compatible dimensions. Sources x_0..x_(n-1) are immutable; z is one
borrowed arbitrarily dirty connector. Every nonzero row v in (Z/cZ)^n has a
distinct dirty output y_v. The required action is

```text
y_v += sum_j v_j A_v B_j x_j;     every source and z is restored.
```

The maps are arbitrary R-linear maps, possibly singular and noncommuting.
The only calls are unsigned `B_j: z += B_j x_j` and `A_v: y_v += A_v z`.
There are no inverse calls, free copies, source mutation, other connectors,
frame changes, output borrowing or direct A_v B_j calls. Outputs are observed
after the complete batch. Calls include their own private restoration; this
package prices only the number of those complete calls.

The word is fixed independently of data and map entries and must work for
every admissible choice. Characteristic c means c times the identity is zero
and no smaller positive integer times the identity is zero. No field division
or primality assumption is used. The proof also covers c = 2, where block
constructions and the corresponding exponent have predecessors.

## Prefix criterion and counts

Project a word onto its L source calls. At boundary t let q_t count each
source modulo c. Then

```text
z = z_initial + sum_j (q_t)_j B_j x_j.
```

For each output, the sum of its readout prefixes must equal v, and its
readout count must vanish modulo c. Each source count must also vanish
modulo c. These conditions are sufficient by linearity. Necessity follows
by specializing to scalar identity and zero maps on independent source and
dirty inputs. Every source is requested and every row is nonzero, so every
source and output occurs at least c times. In particular L >= cn and c divides
L. This is the established prefix/count argument of #4231/#4238.

## Directed torus cycles

For b >= 1 there is a length-c^b directed Hamilton cycle on (Z/cZ)^b using
only positive coordinate increments. Here is an explicit induction.

- For b = 1 use the one coordinate c times.
- Given a cycle W on b coordinates, delete its last edge to get a path P
  visiting every vertex. Its endpoint is -e_j, where e_j was the deleted edge.
  On one new coordinate k, use `(P B_k)^c`.

Each copy visits every old-coordinate vector in one new-coordinate layer,
translated by the old endpoint accumulated from earlier copies. The new
coordinate separates the c layers. After c copies both the old displacement
-c e_j and the new displacement c e_k vanish. The length is
`c((c^b - 1) + 1) = c^(b+1)`. Thus every vertex occurs exactly once among the
boundaries before closure. The code builds this induction iteratively.

## Construction

Partition the n sources into c blocks, allowing empty blocks. In each
nonempty block run its torus cycle while all other source coefficients are
zero, returning to zero before the next block. An empty block supplies the
zero prefix without calls. For any v, its c block projections occur among
the available boundaries. Read A_v once at each projection, repeating the
zero boundary when needed. Their sum is v and c copies of incoming dirt
cancel. Readouts do not change the connector, so all outputs can use these
boundaries in the same chronological word.

Write n = ac + r, 0 <= r < c. Balanced blocks give the source count

```text
S_c(n) = cn                                  if n < c,
S_c(n) = (c + (c - 1)r)c^a                    if n >= c.
```

There are exactly `c(c^n - 1) + S_c(n)` complete calls. The balance is optimal
within this particular geometry of at most c separately restored blocks,
each exposing every block vector as one prefix. A nonempty b-coordinate block
requires at least c^b boundaries. Splitting a block into two nonempty pieces
does not increase that cost, since c^(a+b) >= c^a + c^b for a,b >= 1, c >= 2.
For a fixed number of nonempty blocks, moving a coordinate from a block of
size b to one of size a with b >= a+2 strictly reduces the sum. This proves
the claimed restricted minimum. It is not a global constant optimum.

## All-word lower bound, including extra readouts

Put M = c^n - 1 and

```text
P_c(L) = binomial(L + c - 1, c) - L,
L_0 = least multiple of c, at least cn, for which P_c(L_0) >= M.
```

A restored source path has at most L boundary vectors: the final boundary
equals the initial boundary. A row served by exactly c reads is the sum of a
c-element multiset of these indexed boundaries. There are
`binomial(L+c-1,c)` such multisets. The L pure repeated multisets each sum
to zero, so at most P_c(L) nonzero rows can use exactly c reads. Duplicate
boundaries or duplicate sums only decrease this upper bound.

Every remaining row needs at least 2c reads, since its count is a positive
multiple of c. Therefore every word has at least

```text
cM + L + c max(0, M - P_c(L))
```

calls. This implies the simpler lower bound **cM + L_0**. If L >= L_0 it is
immediate. Otherwise let h = (L_0-L)/c. The integer function P_c increases
by at least one at each c-step. Indeed
`P_c(L+1)-P_c(L) = binomial(L+c-1,c-1)-1 >= 1` for L >= 1, c >= 2.
Since P_c(L_0-c) < M, we have M-P_c(L) >= h. The extra reads cost at least
ch = L_0-L. This also proves that L_0 is the exact minimum of this relaxed
counting invoice; it need not be attained by a legal word.

Finally,

```text
M <= P_c(L_0) <= (L_0 + c - 1)^c / c!,
L_0 >= (c! M)^(1/c) - (c - 1).
```

Together with the construction this proves, for fixed c,

```text
(c!(c^n-1))^(1/c) - (c-1)
    <= OPT_c(n) - c(c^n-1)
    <= S_c(n) = O(c^(n/c)).
```

Both sides have order c^(n/c). In particular, permitting extra output calls
does not improve the overhead exponent. The constants are not matched.

## Finite examples and evidence

These are emitted literal words, not exact-optimum claims.

| Characteristic | Sources | Source calls | Readouts | Total | Counting lower |
|---:|---:|---:|---:|---:|---:|
| 3 | 5 | 21 | 726 | 747 | 741 |
| 3 | 6 | 27 | 2184 | 2211 | 2202 |
| 3 | 7 | 45 | 6558 | 6603 | 6582 |
| 3 | 8 | 63 | 19680 | 19743 | 19716 |

#4238's exact five-source value 744 and #4244's exact six-source value 2208
are smaller than this uniform construction. #4244 also gives a stronger
seven-source lower bound of 6588 using deletion. Those are cited predecessor
results, not contradicted by this simpler all-characteristic bound.

The verifier checks 41 complete words for c = 2..8, with n ranges
1..9, 1..8, 1..6, 1..5, 1..5, 1..4 and 1..4 respectively. It checks 36,996
output rows and 186,532 literal calls with a formal coefficient ledger.
It also checks 28 Hamilton cycles, all 780 weak block compositions for
c = 2..5 and n = 1..6, and all 2,220 readout multisets in four small cases.
Twelve separate dense executions use dimensions 2 and 3, c = 3,4,6 and
n = 3,4, with dirty registers and singular noncommuting matrices.

Six controls are rejected: a dropped source call, a dropped readout, a cyclic
source relabeling, a misrouted output, an appended source call, and the same
ternary word executed in characteristic six. The generated stdout receipt
binds these counts and the example table to SHA-256 hashes of all package
files. There is no hand-written receipt or stored generated replay output.

## Reproduction

From the repository root, using CPython 3.12 and the standard library:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/full-coefficient-connector/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/full-coefficient-connector/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/full-coefficient-connector
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/full-coefficient-connector --check-source-history
```

The selected record, catalogue and two predecessor READMEs in
[SOURCES.json](SOURCES.json) are historical provenance, resolved from the
pinned base commit. The verifier imports no predecessor code and has no live
external inputs.

Expected marker: `PASS_FULL_COEFFICIENT_CONNECTOR`. The verifier writes no
files. The all-n result is the written induction and counting proof; the
finite replay corroborates it. No full selected replay or formal proof-kernel
build is needed or claimed for this isolated package.

The code has no recursion. Replay parameters cap c at 8, n at 12 and rows
at 100,000; the registered cases are smaller. Python-managed allocation is
an explicit Power of Ten deviation: live storage is O((n+c)c^n + c S_c(n)) for
these bounded cases, rather than allocation-free execution. This is a
verification resource bound, not a physical implementation cost theorem.

## Limits and family decision

The result concerns full coefficient demand and unit complete-call prices.
It gives no exact optimum for n >= 7 and no optimal leading constant.
It changes the demand and characteristic, not the operation alphabet, so it
is a changed scope from the catalogue card. The c = 2 case is a control and
credited predecessor territory. Characteristic zero has no finite c-read
cancellation and is outside the theorem.

The call count is proved and the abstract word is constructively supplied.
A caller needing all coefficient rows is unknown. Coefficient preparation,
dispatch, parent stock, hosting, precision, tape and complete supplier
admission remain unknown. Unknown costs are not zero. The decision is to
finish this local theorem and stop construction expansion until a concrete
consumer or a sharper combinatorial question is supplied. This is not a
complete multiplication theorem or a new selected bound.

## Open next questions

Structured versions are in [TASK.json](TASK.json).

1. Close the constant gap between the all-word counting lower bound and the
   c-block construction, beginning at c = 3 and n divisible by three. Test
   paths whose boundary sets are better c-fold additive bases; include the
   cost of realizing those sets by positive source steps and restoration.
2. Improve the explicit seven-source ternary upper bound 6603 toward #4244's
   lower bound 6588. A path covering all 2186 rows by three-prefix sums would
   preserve the readout floor; count all additional source calls.
3. Identify a real consumer requiring full coefficient demand. Bind its maps
   and complete physical invoice before making a supplier claim.

## Credit

This contribution was produced by Nick Petalas. Credit Nick Petalas's
#4238/#4244 for the full ternary demand and open larger-source question,
#4231 for the arbitrary-characteristic unsigned interface, Riquelme Soares's
#4189 for the unsigned F3 one-source predecessor, Ross Richardson's #943/#934
for the prefix-connector and Gray-block lineage, `conorholds`'s #2208 for
block palettes and all-word counting in different alphabets, and ywz65 for
the five-source contract map. The CLAIM mistakenly attributed #2208 to
Richardson; #2208 is by `conorholds`, with Richardson credited for its
#943/#934 lineage. No priority is claimed for Gray codes, direct-sum additive
bases or elementary dirty cancellation. No predecessor credit is changed.
Independent human and formal proof-kernel review are unclaimed. Apache-2.0.
