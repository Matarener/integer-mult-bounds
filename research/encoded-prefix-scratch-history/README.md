# Historical backing of the encoded minimum-prefix planner

This source-bound written proof sharpens the **standalone** PR5707 planner's
scratch extent to a linear digit envelope, including erased retained tails.
It does not sharpen the whole RootPlan's scratch claim or discharge the selected
construction's `precision_tape` assumption. The finite checker exercises the
actual retained implementation, not a replacement search.

Source: Ali Romman's [PR5707](https://github.com/CrocSwap/integer-mult-bounds/pull/5707),
exact merged head `8a3ed4641ed4efd5c0eef70c94dbfc48f95d8cd1`,
`research/encoded-minimum-root-prefix`. Its `MinimumRootPlan.compute` calls
`minimum_prefix`; this result covers that callee on a separately installed
32-tape pool. The enclosing caller has other live results and a 256-tape pool,
so transferring this result to its complete historical schedule remains open.
The source's independent arithmetic verifier already uses this 32-tape binding.
The [claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/4744#discussioncomment-19234413)
fixes the scope. The source archive and all predecessor files remain unchanged.

## Result and domain

For canonical borrowed Counts M>=1, K>=1, T>=m and compiled integers
1<=r<m<=73, F>1, put

```
b = bitlength(M), k = bitlength(K), c = ceil(log2 F), h = m-1,
A = c h b, L = max(7, b+k+1, A+2), E = L+2.
```

In any successful call, including closing its returned q/depth/stock, every
write to an owned pool tape has index at most L+1. Count index zero is LEFT,
indices 1..ell are digits, and index ell+1 is RIGHT. Thus E includes both
markers. A tape's **backing extent** means `len(Tape.cells)`, including erased
BLANK tails; this is neither its live word length nor Python heap allocation.

For any finite sequence of admitted calls on the same pool, with all three
outputs consumed and closed before the next call, let a_i be tape i's initial
extent. Initial bodies may have arbitrary finite erased tails, with LEFT at
zero and head at one. For every prefix of the history, and at every instant
of its calls,

```
len(cells_i) <= max(a_i, E_1, ..., E_j),
sum_i len(cells_i) <= sum_(i=0)^31 max(a_i, E_1, ..., E_j).
```

A sharper exact identity replaces E_j by the largest write index plus one
actually reached on that physical tape. In particular, for a cold pool and
fixed construction constants, the owned backing is O_F(b_max+k_max), not
quadratic in those bit lengths. For the source's bounded-by-p M and K, this
standalone result is O_F(log(p+2)). An arbitrarily large K cannot be omitted:
`divide` and `Count.product` copy it even when the answer q is tiny. T is
borrowed and compared, never copied into this pool.

## Source-bound proof

The source activation authenticates `source-snapshot.tar` and every member
against `SOURCE-INDEX.json`, then invokes the unchanged historical cohort.
The relevant transitive implementations are `cardinality.Natural`,
`counts.Count`, `cardinal_counts.Count`, `encoded`, `root_plan.ceil_divide`,
`scratch_pool`, `session.OuterScope`, and `records.Tape`. Their numeric
allocation sites are specialized to `ScratchPool.acquire`; the installed
scope seals new Tape and Arena constructors. Host observer meters and lease
bookkeeping are not numerical tapes and are outside this extent claim.

**Depth.** Since r/m <= (m-1)/m and
`(1+1/(m-1))^(m-1) >= 2` by the binomial expansion,
`(r/m)^h <= 1/2`. Each profile step sends w to r floor(w/m),
so after hb steps its width is at most M/2^b<1. As T>=m>=2, it
must stop by then. Every profile depth is <=hb and every stock is
`F^d <= 2^(chb)=2^A`. These arguments apply to the initial M and each
subsequent core M-q. All current widths decrease and remain <=M.

**Complete primitive ledger.** The following are all arithmetic paths reached
by `minimum_prefix`, `reached_profile` and `floor_log2`:

| Actual code | Numeric and write-extent reason |
| --- | --- |
| `Natural.__init__`, `Count.literal` | Copy canonical digits through RIGHT. A literal uses an extra temporary tape, then copies and clears it. Literals are 0,1,m; m<=73 has at most 7 digits. |
| `Natural.increment` | Only extends by one digit when all prior digits are one; the new digit length is that of the incremented value. Depth<=hb; scanned stock digit counter<=A+1; trial midpoint after increment<=M-1; division quotient after rounding<=A+1. |
| `Natural.multiply_small` | Overwrites existing digits, emits carry digits and RIGHT. Extent is no greater than the maximum of its old and resulting canonical lengths. Profile stock<=2^A; width after multiply<=M; initial bound cD<=A. The multiplier c, r, F or 2 is fixed control. |
| `Natural.divide_small`, `normalize` | Division overwrites the old digit interval. Normalization moves RIGHT left and erases the former next position; it never writes beyond the old RIGHT (zero has one digit). Thus a numerically shrinking value may retain its old physical extent, already bounded. |
| `encoded.compare`, `positive`, `zero`, rewinds/scans | Allocate no tape and write no cells. Borrowed inputs return at their first digit. |
| `encoded.subtract` | Copies the left operand, overwrites those digits, then normalizes. Left operands are M or the stock digit count<=A+1. No write exceeds the copied extent. |
| `Count.add` | Copies its right operand, writes through at most the sum's length or the longer old input length, then normalizes. Midpoint precursor lower+upper<=2(M-1). Product's additions remain <=Kq. |
| `encoded.divide` within `ceil_divide(cD,K)` | Copies K; scans the numerator<=A. Each pre-subtraction remainder is <2K, each quotient prefix and its final ceiling are <=A+1. `subtract` copies only that bounded remainder. Quotient/remainder doubling is in-place; the old widths stay bounded. |
| `Count.product(K,mid)` | Copies K and mid, initializes result zero, scans mid from its most significant digit. Result is K times a processed prefix; doubling before the optional addition and the addition result are both <=K mid<=KM. A zero multiplier keeps the one-digit zero. The add-source copy is K. |
| `floor_log2` | Scans stock of at most A+1 digits, counts them, subtracts one, and closes both local Counts. It does not materialize a number of size 2^stock. |
| `Natural.close`, `Lease.clear`, `Tape.clear` | Clear writes only through the dense live body ending in RIGHT, stops at its following BLANK, and rewinds. It never traverses or extends the erased tail. |

The initial un-clamped upper bound is <=A+1. After clamping, all search
endpoints are <=M-1. Therefore every digit extent in the ledger is bounded
by L: M, 2M, K, 2K and KM use at most b+k+1 digits;
stock uses at most A+1; A+1 and 2(A+1) use at most A+2 digits
for integer A>=1. This also covers temporary noncanonical high zeros because
the only shrinking operations preserve an already bounded old interval.
This is a primitive-intermediate argument, not a bound inferred from outputs.

**Fixed inventory.** The source's 14-lease maximum includes literal setup.
At a trial start six leases hold one, m, last, lower, upper, mid. The core
and returned profile pair give nine. During profile construction there is
also current, and literal construction temporarily takes two tapes, still
below fourteen. The logarithm's two locals plus subtraction result peak at
twelve and leave ten after returning bits. Product factor and scan give
twelve; its literal's temporary and result give fourteen. Later the add copy
also peaks at fourteen. Initial bound division (including its copied K,
quotient/remainder and subtraction) and final profile/output copying stay
below fourteen. Thus a 32-tape empty pool suffices under the admitted
successful execution contract. Only the returned three leases survive the
call; they are not erased until their owner closes them.

**History.** In the actual `Tape.write`, extension is exactly to `head+1`
when that exceeds the current length. No reached method truncates `cells`.
Consequently each physical tape's length is its initial extent or its largest
write index plus one, whichever is greater. The primitive ledger bounds every
new write by E, including cleanup. Induction on writes, then calls, gives the
claimed envelope and its sum. Taking a maximum of aggregate live leases, or
using only the last call's E, does not give this history bound. Arbitrary
preexisting erased storage must remain in the bill even on never-used slots.

## Reproduction and evidence

```
python3 scripts/research_package.py --package research/encoded-prefix-scratch-history
```

The registered normal and optimized commands authenticate live source pins,
activate the retained source, and run two histories of seven calls each. They
include the first q=2/depth=1/stock=6 fixture, growth then shrinkage, a 61-bit
K, a threshold above M, and a different dimension/rank/divisor. A read-only
observer delegates to the original `Tape.write` and inspects its result; the
planner and arithmetic bodies are unchanged. Every write is checked against
the per-call bound, and exact backing length is independently checked after
each call. All borrowed bytes/heads, output values, lease ownership and fully
erased retained tails are checked. The integer oracle uses strict padded-row
arithmetic, with a proved rows>stock shortcut to avoid allocating 2^(Kq).

Negative controls require rejection of a pool-empty claim before the three
outputs are closed, exhibit a cold large-to-small history exceeding its
last-call bound, and exhibit erased warm tails exceeding the fresh-history
bound. The finite tests corroborate the written proof; they do not quantify
over all inputs. Input construction, borrowed-input destruction, warm-tail
preparation, source extraction, Python heap bytes and full RootLayer payloads
are outside the measured pool-write interval and the claimed extent bound.

## Open next questions

- Transfer the callee envelope to `MinimumRootPlan.compute`'s actual 256-tape
  history with all other live expressions and parameter construction. Start
  with a complete source primitive ledger for `parameters` and its consumers;
  this result alone does not bound their retained backing.
- Independently review the universal primitive ledger and history induction;
  the bounded checker is not a proof-kernel or independent human review.
- Bound complete tape actions and integrate physical supplier/precision and
  payload costs. Erased extent does not pay head movement or native work.

The structured questions and blockers are in `TASK.json`.

JoyboyBrian, with substantial OpenAI Codex assistance, produced this audit.
Ali Romman supplied PR5707's search and integration and PR5688's minimum-prefix
construction. Jose Manuel supplied the retained physical-complex-controller;
all historical Count/tape/cohort contributors retain the source package's
attribution. This package adds a source-bound scratch history proof and checks;
it claims no new kappa, whole multiplier theorem, or selected-frontier change.
Apache-2.0.
