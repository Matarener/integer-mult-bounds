# Paid source update closes the CRT row-reentry boundary

The returned physical row stream can now update the actual owned axis-record
tape, retire its old query, and supply the next row without host serialization.
For any admitted fixed node and finite compiled row sequence, the resulting
source equals the corresponding sequence of source Caller row permutations.
The source keeps the same backing and extent. All non-target fields and all
protected dirty words remain unchanged. Each row's new work is retired.
This gives complete forward and reverse execution of one mixed-width level.
It does not change complete kappa or the selected result.

## 1. Sources and exact domain

The unchanged joined query is JoyboyBrian's
[PR #5496](https://github.com/CrocSwap/integer-mult-bounds/pull/5496), exact head
`a99afd7e0024af8367d5a2f6f4d2da57a1d13dd5`.
It uses Ali Romman's [PR #5353](https://github.com/CrocSwap/integer-mult-bounds/pull/5353)
RowEntry, JoyboyBrian's numerical Entry/producer and encoded ROM producer.
The multi-target audit and exact bank count are from commdata2338's
[PR #5519](https://github.com/CrocSwap/integer-mult-bounds/pull/5519), exact head
`53a034436f17ef5b8fdf7a02f5066528cdfe5446`.
SOURCES.json pins every consumed file at canonical main
`6cf7a683f447b9f1e2333791907fd92be5009a63`.

Retain the admitted domain: a power-of-two axis count d, ell>=2,
widths h_i in {ell-1,ell}, pairwise coprime moduli 2<=s_i<2^h_i,
arbitrary padded coordinates 0<=x_i<2^h_i, and a compiled node [a,a+n)
with n=2^level. Write b=a+n/2. The runtime source is the literal sequence
of width, modulus and coordinate records. Eight protected numerical words
of width P=1+sum_(a<=i<a+n) h_i are supplied with legal entry heads.

The caller owns the coordinate fields of this source. The existing query
borrows the whole source unchanged until its close. Source records, moduli,
widths and dirty-word setup remain supplied inputs. Every fresh query has
its own supplied blank work roles. One distinct blank staging tape is
supplied and reused between rows. No alias with a source or query role is
allowed. Malformed execution and failure rollback are outside the theorem.

The RowQuery, numerical and ROM producer theorems remain named hypotheses.
This proof establishes their new consumer and sequential composition; it
does not independently re-prove their all-size arithmetic or ROM claims.

## 2. The ownership boundary

For an active row, retain_stream copies the complete owned result through
local reads, writes and unit moves. It translates no coordinate into a host
integer. The original result and staging heads return to L. The new copy
is needed because RowQuery.close erases the original result.

Next, call the unchanged query.close exactly once. At this point the source
borrow has ended. All old numerical, header, ROM, layer, countdown and result
roles are blank with their specified heads, by the source contract. Staging
contains the result on a distinct owned tape.

The consumer scans the original axis source from its first record. It checks
and crosses each tag, unary width, width delimiter, modulus field and modulus
delimiter. It writes only the h_i coordinate cells with b<=i<a+n. Those cells
receive exactly h_i bits from the staged result, in the original axis order.
It checks the coordinate and record delimiters; it neither inserts nor removes
a source cell. All other coordinates and all source metadata are read only.
After the last record, the source is at its original RIGHT marker and staging
is at R. Local rewinds restore source head one and staging head zero. Erasing
staging clears all its cells, including its markers.

For an all-idle row, the source query creates no result. The consumer only
closes that empty query. It does not read, move or write either tape. This
preserves the source's exact identity-row convention.

The staging length is fixed by the compiled node:

    S = 2 + sum_(b<=i<a+n) h_i + n/2.

Its full retained extent is S after any active row. Every later active row has
the same extent. Its erasure therefore leaves no hidden tail, and its capacity
is counted once even though it is blank between rows.

## 3. Correct current-state row composition

Assume the source contains state x on entry to a row. By the credited query
theorem, its result is exactly the right-node slice of Caller.apply(x,row(x)).
Idle target axes are included unchanged when some other axis is active.
The consumer installs that exact slice and keeps every other field. Thus the
new source contains exactly the next Caller state, including padded targets.
No x_i<s_i test suppresses a query or an update.

The source retains its fixed widths, moduli, record shape and entry head.
The coordinate bits still lie in the admitted padded domain. The protected
words have returned unchanged, and staging is blank. These are precisely the
entry conditions for the next row. Induction proves the claim for every finite
compiled row sequence at this node. It is not a fixed-width sample argument.

For a full forward level, use global rows 0 through 2ell-2. Its left child
never changes. Consequently the current-left offsets recomputed by each query
agree with the source caller's offsets held during that level. Reverse row
order gives its inverse on the entire padded domain, by the retained Beneš
row theorem. Forward followed by reverse restores every source byte and head.
The intermediate owned coordinate changes are intended output, not a claim
that a forward query preserves the caller's original coordinates.

This statement concerns one fixed node. It does not silently reuse numerical
words at a different precision or install the three changing-left-state epochs
of an exceptional key. Such compositions need their own input and cost binding.

## 4. Complete local cost and retained backing

Let L=2+sum_i(3h_i+4). Retain the full original row-query allowance, including
numerical entry and retirement, every complete ROM production, full-layer
output disposal and all query scans. For an active set A, define

    F = L+(n+1)(P+2)
        + sum_(i in A) [(2^h_i+1)(h_i+1)
                       +2^h_i(2h_i-1)+2h_i+4],
    T_entry = 2^20(P+2)^4+2^16(P+2)^2+128(L+P+n+1),
    T_rom(i) = 2*10^6 P^2(2^h_i+1)^3(h_i+1)^4,
    T_query = T_entry + sum_(i in A) T_rom(i) + 4096F.

For the added consumer, the stream copy and both rewinds use at most 8S
primitive tape actions plus a constant. The source scan and rewind use at
most 4L+S such actions. The staged read and erasure use at most 10S plus a
constant. The conservative bound 128(L+S) covers their sum, guards and even
an additional count of the original result erasure. Each loop has fewer than
32 finite-control transitions per charged action or compiled iteration, so
4096(L+S) is a source-operation allowance for the whole added boundary.
No input-sized host operation occurs in reentry.py. The complete active-row
bound is therefore

    T_new = T_query + 4096(L+S).

An all-idle row has zero tape work. For a sequence, sum T_new over active rows.
This is a finite-symbol source-operation bound with the same numerical model
as its predecessors. It is not a new binary transition-table compilation.

For a nonempty active set put H=max_(i in A) h_i. Use the credited exact
52-role bank count and exact three-extra-port count from the audit:

    B_bank(P,H) = 5P 2^H(H^2+3H+1)+2^H(4H-1)+48P+2H+104,
    B_extra = 2(H+2)+S.

The source numerical Entry bound is

    B_entry = 57(P+2)+3(P-2)(2P+4)+6+3P+4n+4.

The entire sequence uses distinct query workspaces. Erasure does not release
their capacity. Thus the complete retained owned-work bound is

    S + sum_(active rows) [B_entry+B_bank(P,H)+B_extra].              (1)

The actual source of length L and the eight protected words of total length
8(P+2) are additional supplied backing. Any exterior blank reserve is also
separate. Interpreter metadata and a future binary compiler are excluded from
this finite-symbol tape-cell count. The shared bank formula is predecessor
work; applying it once per distinct row does not grant reuse across rows.

The verifier retains all query objects, deduplicates physical backing identities,
checks the bank and extra counts separately, and sums every retired row bank.
It never replaces this sum by a largest-row bound. The staging backing is counted
once. A cross-row shared-bank implementation is not claimed.

## 5. Executed evidence

There are four actual forward/reverse fixtures, with one initial serialization
per fixture and no source replacement between any of their ten rows:

* (7,3), widths (3,2), state (1,1): the forward result is (1,2), with actual
  intermediate padded coordinate three. Reverse rows restore (1,1).
* (5,7,3,2), widths (3,3,2,2), root state (3,2,1,1): two target streams give
  forward state (3,2,1,0), then return to the complete original source.
* The same four-axis source, nonroot node [2,4): only its right coordinate
  changes. Both exterior records remain byte-exact.
* (7,3), widths (3,2), invalid left state (7,1): offset disabling and all
  row, retirement and reentry obligations still hold.

Together these execute 40 row invocations and 30 unchanged physical ROM calls.
Every row is checked against the retained logical caller. That oracle only
observes; it supplies no runtime table, offset, coordinate or branch. The
verifier checks all dirty bytes/heads, source identity/extent, numerical roles,
all ROM tails, staging erasure, exact non-numerical bank counts and total bills.

Five separately executed adapter mutants omit query retirement, overwrite the
coordinate with zero, change the target interval, retain staging or omit the
source rewind. They fail an endpoint or ownership check on the actual row-one
return shape. These small adapter controls do not claim a new independent audit
of the inherited numerical or ROM producer. Normal and optimized registered
runs compare their complete receipts. Committed and Git-free checks are separate
transport evidence.

## Limits and attribution

Initial axis-record production, arbitrary dirty backing acquisition, a common
workspace across rows, whole-tree changing-precision entry, complete three-epoch
keys, global address/key transport, binary numerical lowering, full E(p,ell),
native/ordinary/outer admission and complete multiplication remain open.
No selected cold replay, human acceptance or proof-kernel acceptance is claimed.
No predecessor implementation or source pin is changed.

Credit commdata2338 for the source-update handoff and exact ROM-bank audit;
JoyboyBrian for the joined query, encoded ROM and numerical lifecycle;
Ali Romman for the actual RowEntry; ToikY for the explicit-width mixed caller
and arena refinement; Hiroki KUMAZAKI for the current-state CRT contract;
Cinna Davis for the original CRT construction. Retain Tekalign, Jose Manuel,
Ryanson Jonathan, unpaidmoon, Douglas Colkitt, John-Michael Smith and the source
license notices. New consumer, composition proof and checks: Ali Romman with
substantial OpenAI Codex assistance. Apache-2.0.
