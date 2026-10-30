# Fixed controller: all-depth obstruction for the five-terminal BIT word

This strengthens `PROOF.md`: **with the pinned controller's public touch
chronology, the frozen five-terminal local histogram cannot reach b=.002
at any halving depth or any permitted odd arity**, even after granting
fractional owners, arbitrary dedicated full-progress helper stock, zero
fallback/adapters, and full-rank idle work on that dedicated stock.
Consequently `.002/.003/.005` joint targets through an outer map K<b fail
within this model. No physical implementation or universal lower bound is
claimed.

The hypothetical depth11/rank60 passing screen in `PROOF.md` is therefore
unavailable in the pinned chronology. It is not a practical opening provided
by deeper recursion: obtaining such a public remainder would require changing
the controller's public touch/idle structure or another premise.

## Exact source boundary

At Git pin `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, the source is

```
research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/vendor/
e8-r715-eleven-stage-whole/code/global_k.py
SHA256 6368196a393ac25bb2918880e4c4bd31ed733b762c27b6873ab391cbc0c5c3c8
```

The source credits DreamingOfClouds's arbitrary-odd-stage generalization,
the PR436/PR386 work of Zhihao Chen and eumemic, and chafreaky's integration
and routes, with the AI disclosures retained in that file. PR589's hosting
proof supplies the actual pending-axis interpretation of each idle child.

Sagar Thakrar's [PR3948](https://github.com/CrocSwap/integer-mult-bounds/pull/3948)
at `5505853988cfc05bc8ad9bfcf07879727932b0d5` already records the generic
K-parametrized idle-window formula, its nine-stage rank-42 specialization,
and the bridge-delimited no-fusion observation. We reproduce that source
calculation here to make the premises explicit. The added result is its
application to the five-terminal histogram for every odd arity and depth,
with the dedicated-stock minimization below; the window formula itself is
not claimed as new.

The source's `recipe(K)` has L=2K+1 local sweeps. Its idle insertion block
gives, directly and for every K:

1. After odd s=1,3,...,2K-3, an initially untouched pair moves from level-1
   to s, with rank `7(s+1)=14j`, j=1,...,K-1.
2. After even s=2,4,...,2K-2, a pair advances one level, with rank7.
3. At s=2K, pair j has old level2j+2 and advances to2K, with rank
   `7(2K-2j-2)=14(K-j-1)`, j=0,...,K-1. The last rank is zero.

Thus the positive idle rank multiset is two copies of14j for j=1,...,K-1,
and K-1 copies of7. Its maximum is

```
R(L)=14(K-1)=7(L-3)=m-22.
```

At L=9 the full emitted idle sequence is exactly
`14,7,28,7,42,7,42,28,14,0`. There is no rank60 interval to host or leave
unoccupied. A remainder contained in an original idle interval has rank no
larger than that interval, independently of the recursive child's depth.

The rule also gives bare public idle rank stock per local invocation

```
(222/L) * [2*sum_(j=1)^(K-1) 14j + 7(K-1)] = 777(L-3).
```

This independently matches `T-(1554+63)`, with the notation of `PROOF.md`.
The local helper progress is3484. Therefore public leftover rank mass after
hosting all helpers would be `777(L-3)-3484=T-C`.

`check_windows.py` extracts and executes only the pinned `recipe` and idle
insertion AST, with every extracted assertion converted to an explicit check
that remains active under `python -O`. Surrounding stage/bridge/exchange level
conditions are checked explicitly. It compares the extracted source output
to the closed-form multiset for odd L=3,...,101. This finite comparison is a
transcription control; the displayed three source cases are the all-K proof.
The source CLI guard requires odd L≥5, but its `NAMES` table limits named
emitted layouts to5,7,9,11,13. The all-odd mathematical scope comes from the
written recipe argument, not an all-odd executable compiler claim. The formal
recipe and auxiliary algebra also make sense at L=3, which is included only
as an additional favorable case.
No native scalar or machine execution is inferred from this small AST check.

## Dedicated stock cannot evade the public window cap

One must not impose R(L) on idle work in a new dedicated helper bank without
proof. We instead grant that bank an ideal rank-m child, although rank m is
not a valid recursive child, so its idle work costs only its rank mass.

Let q≥0 be the total helper progress removed from public hosts and placed
in additional full-progress stock X. Public leftover rank mass is
`T-C+q≥0`, while dedicated idle mass is `mX-q≥0`. Thus

```
q ≥ qmin=max(0,C-T),     mX ≥ q.
```

For L≥5 and b>0 put `u=(m/R(L))^b>1`. Ignoring fallback and all adapters, the actual
raw excess is bounded below by

```
A_m(b) + (T-C+q)u + (mX-q) - m(w+X)
  = A_m(b) + (T-C)u - mw + q(u-1).
```

The extra stock X cancels only because its idle work has been granted the
unrealistically favorable unit cost. The coefficient of q remains positive.
Hence the minimum is attained at qmin. For L=5,7 this minimum becomes
`A_m(b)-C-(w-63)`, as in the earlier proof. At the formal L=3 case there are
no public idle slots (R=0): all3484 helper-progress ranks must use dedicated
stock, giving the same expression directly, without dividing by R.
At L≥9, qmin=0; moving any
helpers to extra banks only increases this lower bound. This covers added
full-progress stock without incorrectly assuming its idle ranks obey the
public source-window cap.

It does not cover auxiliary streams having a new useful partial-progress
endpoint instead of complete progress m; that is a changed recursive contract.

## All arities, independently of depth

At L≥9 define `I=T-C=777L-5815=111m-5926` and

```
E(L,b)=A_m(b)-C-(w-63) + J(m,b),
J(m,b)=I*((m/(m-22))^b-1).
```

Fix b=.002. For every 0<b<1, J increases with m. To see this, set
`x=22/(m-22)>0` and `f(x)=(1+x)^b-1`. Then

```
J=2442*f(x)/x - 3484*f(x).
```

The function f is increasing and concave with f(0)=0, so f(x)/x is
nonincreasing in x. As m increases, x decreases: both displayed terms are
therefore nondecreasing, and the second is strictly increasing. In particular
`dJ/dL≥0`. Since `A_m(b)≥C`,

```
dE/dL ≥ 7bC/(7L+1)-111/L².
```

At b=1/500, multiply by the positive `L²(7L+1)` and write L=13+y. The
numerator becomes

```
(928483 + 539882*y + 35707*y²)/500,
```

whose coefficients are all positive. Hence E increases on every real L≥13.
Exact rational interval checks for the remaining odd starting cases give:

| L | favorable excess per local invocation at b=.002 |
|---|---:|
|3| >13.5540428589069553897 |
|5| >3.8049595866973275552 |
|7| >.8340592145604612887 |
|9| >.8384204496318681522 |
|11| >1.4470054318573842990 |
|13| >2.1235527765277093862 |

These signs and monotonicity prove failure for every odd L≥3 in the stated
source coverage/chronology model. Each fixed-L complete bill is increasing in
b, so every b≥.002 also fails. No halving guard was used.

At fixed L=9, the ideal rank42 remainder root, with the inherited fallback,
lies strictly between `.001954220766879` and `.001954220766880`. This is a
lower-bound invoice's root, not an attained BIT exponent. Actual integral
owners, windows, extra children, precision and native execution can reduce
feasibility further.

## Remaining boundary and reproduction

This result leaves changed public chronology, legal fusion across old idle
intervals with a new paid operator, new useful partial-progress auxiliary
contracts, changed coverage/unpaid directions, changed local H, reduced COPY
work and complete caller redesign outside its scope. An adapter that changes
one of those premises must be constructed and fully charged. It cannot be
silently assigned the old source's stock or chronology.

Dynamic precision128/256, or a different valid precision charge, does not by
itself invalidate this obstruction. Precision-cap failure is not used here.
The scalar word remains independently useful as a finite arbitrary-input
restored operator regardless of this failed joint-target screen.

```
python3 -B check_windows.py
python3 -O -B check_windows.py
```

`WINDOW-RESULT.json` binds source hashes, the complete nine-stage source
schedule, exact interval signs and the polynomial coefficients. Its arithmetic
engine is `check_moment.py`; the independent reviewer separately uses rational
nth-root bisection. These are written proofs and finite exact checks, not
formal-kernel certification or a full multiplication theorem.

Apache-2.0; substantial OpenAI Codex assistance. No new κ.
