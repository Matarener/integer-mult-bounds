# Smaller sufficient ranks for the conditional κ = 0.0023 compiler

The finite source/exit compiler of [PR4359](https://github.com/CrocSwap/integer-mult-bounds/pull/4359)
admits the same proposed uniform savings at much smaller specified ambient
ranks. Replace the intermediate power majorant by

\[
L(n)\le n^t(1+\log_2 n)^{1/q},\qquad L(n)=P_n/B_n.
\]

Together with a compatible outer parameter retuning, this gives sufficient
ranks **`2^465000` (complex)** and **`2^7100` (BIT before cover)** while retaining
the proposed **κ = 0.0023**. The exact outer ledger passes all nine cost rows,
all 63 inherited arithmetic predicates, and 22 additional interface inequalities.
The retuning spends supplier saving that the κ target does not need.

There are two useful configurations. First, preserve the original supplier
savings, invoices, tested mixed exponents and native hypotheses:

| Family | Original sufficient rank | New sufficient rank | Reduction in exponent of 2 | Uniform saving |
| --- | ---: | ---: | ---: | ---: |
| Complex | `2^276540184361` | **`2^2352000`** | about 117,577× | 0.002304 |
| BIT, before delayed cover | `2^6552928412` | **`2^529000`** | about 12,387× | 0.002760 |

Second, retain κ = 0.0023 with weaker supplier savings and retuned outer parameters:

| Family | Sufficient rank | Uniform saving | Consumer condition |
| --- | ---: | ---: | --- |
| Complex | **`2^465000`** | 0.0023005 | Above outer `b=0.0023004` |
| BIT, before delayed cover | **`2^7100`** | 0.002318 | Cover/atom conversion gives ordinary saving 0.0023011913797 |

The original rank exponents decrease by about 594,710× and 922,948× in this
second configuration. The two rows of each configuration belong together;
the weaker savings are not substituted into the predecessor's original
outer parameter point.

These ranks remain astronomical. This is a written conditional proof with
author-checked exact arithmetic. It does not emit the winning words, bound
their complete constants, independently admit the compiler/native/outer
transfer, or claim a new κ. In particular, it does not assert that the
productive width `B_N`, scalar word or precision constants improve by the
same factors. No selected-result record or predecessor package is changed.

## What changes in the argument

PR4359 chooses `t < z0 < z`, pays an induction constant
`A = n0^(1-z0)`, and then makes `A*N^z0 < N^z`. Its sufficient `log2 N`
therefore loses two inverse powers of the small exponent gap. The logarithmic
majorant below has constant **one** and uses `t` directly. With fixed `q`, its
final condition is just

\[
1+H < 2^{q(z-t)H},\qquad N=2^H.
\]

As `z-t` decreases, this condition needs
`H = O((z-t)^(-1) log(1/(z-t)))`. This comparison concerns the two sufficient
estimates; it is not an asymptotic formula for the compiler's smallest success.
The mixed rule, source complements, whole-array routing, integral batch
replication and owned-bank allocation are unchanged. Only the choice of the
fixed ambient rank changes.

## Conditional logarithmic-majorant theorem

Assume the native finite compiler in the pinned
[`FINITE-PRECOMPILATION.md`](vendor/FINITE-PRECOMPILATION.md), including its
whole-job adapters, arbitrary-input restoration and finite-program closure.
Set `m=max(k)`, `k_min=min(k)`, `r_max=max(r)`, with
`1 <= r_max < k_min <= m`.

Use the ordinary base `L(n)=n` for `0 <= n < m`. For every integer `n >= m`,
the compiler gives finite nonnegative weights and the exact recurrence

\[
\begin{aligned}
L(n)&=\sum_s w_sL(n-s)+\sum_e x_eL(e), &\sum_s w_s&=1,\\
n/m&<s\le n, &1\le e&\le E(n)<n.
\end{aligned}
\]

For a tested rational `0<t<1` with a strict unit superpotential,

\[
\sum_r n_r r^t<\sum_k W_k k^t,
\]

cancellation of the matched internal jobs gives

\[
\sum_e x_e e^t\le\sum_s w_s s^t.
\tag{1}
\]

The normalized weights come from whole integer batches. No fractional-array
routing or extra productive credit is introduced by (1).

Let `theta=log(r_max)/log(k_min)`. The largest target degree in the lockstep
flow is `G=floor(log_(k_min)(n/m))`: every degree-G product is at least
`k_min^G`, and repetitions of the minimum target attain it. Deepest exit
classes have degree zero, so each exit rank is at most `r_max^(G+1)`.
Consequently

\[
E(n)=r_{\max}(n/m)^\theta
\]

is an upper bound. This bound also gives `E(n)<n` for `n>=m` because
`r_max<m` and `theta<1`.

Choose a rational `theta_bar=a/b` with `theta<theta_bar<1`, and a positive
integer `q`, such that

\[
\begin{aligned}
2^{b-a}r_{\max}^b&\le m^a, &(2)\\
\bar\theta&<\eta^q,\qquad \eta=t\,m^{t-1}, &(3)\\
m^{q(1-t)}&<2. &(4)
\end{aligned}
\]

Then for every integer `n>=1`,

\[
L(n)\le F(n):=n^t(1+\log_2 n)^{1/q};\qquad F(0):=0.
\tag{5}
\]

### Base ranks

For `n=1`, (5) is equality. For `2<=n<m`, condition (4) implies
`n^{q(1-t)}<2<=1+log2(n)`. Taking the q-th root proves `L(n)=n<=F(n)`.
Rank zero is defined separately and contributes zero.

### Exit contraction

Write `C(n)=(1+log2(n))^{1/q}` for `n>=1`. Because `n/m>=1`,

\[
\begin{aligned}
1+\log_2 E(n)
&\le \bar\theta\log_2 n+1+\log_2 r_{\max}-\bar\theta\log_2 m\\
&\le \bar\theta(1+\log_2 n),
\end{aligned}
\]

where the last inequality is exactly (2). Thus
`C(e)<=theta_bar^(1/q)*C(n)` for every exit. By (1),

\[
\sum_e x_eF(e)\le
\bar\theta^{1/q}C(n)\sum_s w_s s^t.
\tag{6}
\]

### Source complements and strong induction

For `y=s/n` in `(1/m,1]`, concavity of `x^t` gives

\[
1-(1-y)^t\ge ty\ge t m^{t-1}y^t=\eta y^t.
\]

Since `C(n-s)<=C(n)` whenever `n-s>=1`, and `F(0)=0`,

\[
F(n)-\sum_s w_sF(n-s)
\ge \eta C(n)\sum_s w_s s^t.
\tag{7}
\]

Condition (3) makes the upper bound in (6) strictly smaller than the lower
bound in (7). All complement and exit ranks are below `n`. Substituting the
strong induction hypotheses into the exact recurrence proves (5). This
avoids both an intermediate exponent and an unknown multiplicative constant.

## Two explicit choices of N

The source histograms are copied byte-for-byte in `vendor/`, and their exact
origin is recorded in [VENDOR.json](VENDOR.json). Leaf arithmetic uses separate
code; the consumer cross-check executes the pinned outer ledger function as
described below.

| Family | `t` | `z` | `theta_bar` | `q` | Certified `eta^q - theta_bar` lower bound |
| --- | ---: | ---: | ---: | ---: | ---: |
| Complex | 0.997695 | 0.997696 | 9/10 | 9 | 0.000646856868158037041419759048 |
| BIT | 0.997231 | 0.997240 | 15/16 | 4 | 0.009533387925024688687300943262 |

The κ-preserving configuration uses the same `t`, `theta_bar` and `q`, with
`z=0.9976995` for complex and `z=0.997682` for BIT.

For `N=2^H`, (5) yields `L(N)<N^z` precisely when the stated sufficient
majorant obeys `1+H<2^{q(z-t)H}`. The chosen H values reduce this to small
exact integer comparisons:

```
Complex: 2352001^125 < 2^2646.
BIT:      529001^250 < 2^4761.

With the retuned κ-preserving savings:
Complex:  465001^400 < 2^7533.
BIT:       7101^2500 < 2^32021.
```

Hence the original integer compiler, run at these specified ranks, supplies
`P_N/B_N<N^z` with the same uniform savings as the predecessor estimate.
The complete words remain defined by that algorithm, with every batch
denominator cleared and all owned instances charged as before. The native
and outer arguments must still use the constants of the resulting word.

The H values are the first successful multiples of 1000 **for this majorant**,
except the retuned BIT value, which uses a grid step of 100.
The preceding grid points fail their final integer comparison. Increasing
q to 10 for complex or 5 for BIT fails (3), checked with a strict opposite
interval. These controls exclude accidental weakening of this certificate;
they do not exclude smaller real programs or other logarithmic majorants.

## Retuning the complete consumer while keeping κ = 0.0023

The additional reduction changes the admitted supplier savings. It therefore
requires repricing their consumer. The old parameter point requires complex
saving above `b=0.002303` and admits BIT saving 0.0027. The following point
uses the smaller suppliers without changing the target:

| Parameter | Value |
| --- | ---: |
| Complex uniform saving | 0.0023005 |
| Selected complex saving `b` | 0.0023004 |
| Outer `q` (distinct from the logarithmic-majorant q) | 0.0023002 |
| Effective router saving `a` | 0.0023003 |
| Admitted ordinary BIT saving | 0.002301 |
| `epsilon`, `group_beta` | 0.99999, 0.99997 |
| `r0`, layout slack, stop fraction | `10^-6`, `10^-6`, `10^-8` |
| `lambda`, `lambda_prime` | 0.99769975, 0.9976998 |
| Boundary cap `xi` | `epsilon*(1+outer_q) - 3/32 + 10^-6` |
| Strassen exponent, halo power, core power | `45/16`, 48, 128 |

The gap between the BIT saving before and after cover remains `10^-5`:

```
C0 = 0.002318, C1 = 0.002308.
ordinary = (1-0.003)*C1 + 0.003*0.0000384599
         = 0.0023011913797 > 0.002301 > a = 0.0023003.
```

The unchanged gap preserves the entire delayed-cover inequality: the prime
rule remains `prime > 25,600,000*N^5`, avoiding the finite denominator/rank
exclusions, and the fully charged fallback moment remains at most
`400001/400002`. Since `N>=2`, the same proof uses
`N^gap > 1+gap/2` and fallback multiplier `<1+gap/4`. The atom power remains
0.003, which exceeds the new ordinary saving; its borrowed-stock and linear
adapter inequalities remain strict. The row-stock exponent and support-local
reserve argument therefore have the same form, with constants recomputed for
the new finite words.

For the outer recursion, `b>a>outer_q`, the stopped internal and leaf
exponents are below `lambda` and `lambda_prime`, and the complex saving is
strictly above `b`. The nine cost savings, recomputed from the pinned outer
equations, are:

| Cost row | Saving |
| --- | ---: |
| Main transform | 0.002300176998 |
| Global coordinate router | 0.0023003 |
| Fused Gaussian | 0.002310130994 |
| Group BIT router | 0.002310230991 |
| Group scans | 0.99998 |
| Boundary algebraic matrix | 0.002301176998 |
| Sparse union movement | 0.408551176998 |
| Polynomial products | 0.99999 |
| Microbox face corrections | 77.00004 |

Every row exceeds 0.0023. The smallest strict margin is exactly
`88499/500000000000 = 0.000000176998`. The grid/backoff calculation with
`FLOOR=10^7`, `BACKOFF=10^-7` returns exactly 0.0023. This is an ordinary
strict lower target, not a claim of maximizing the predecessor's old grid.

The checker separately executes only the pinned `check_ledger.py` **ledger
function** and its historical comparison constants, following PR4359's AST
oracle approach. All nine rows agree exactly, and all 63 inherited predicates
remain positive. It does not run or bypass the old m=73 native admission
script. An additional 22 inequalities cover the changed supplier endpoints,
stopped recursion, cover/atom terms, semantic guards, support reserve, fine-prime
guard, explicit metadata halo and record budgets. Four outer mutations reject:
`epsilon=1`, zero layout slack, group width equal to global dimension and an
unfunded old per-axis scan. The full rational ledger and failure rows are in
`RESULT.json`.

The native, delayed-cover, precision and support proofs are reused as stated
in the pinned [outer transfer argument](vendor/OUTER-TRANSFER-AUDIT.md).
This package checks their changed quantitative premises, not their independent
scientific acceptance. All compiled-word constants must still be replaced;
the reduced ranks do not grant the predecessor's small-template constants.

## Reproduction and evidence

From the repository root, with Python 3.12 or newer and no third-party packages:

```sh
python3 -B research/log-potential-template-ranks/verify.py
python3 -B scripts/research_package.py --package research/log-potential-template-ranks --check-only
```

To recompute a receipt without editing the package:

```sh
python3 -B research/log-potential-template-ranks/verify.py --out /absolute/path/to/new-result.json
```

The verifier authenticates all ten predecessor inputs, encloses each mixed
moment and `eta^q` with rational arithmetic, checks the integer theta/shift
tests, proves the entire base range by (4), and checks the final integer
powers. Twelve mutations must reject at the specified obligation: losing the
unit superpotential, losing strict separation, and increasing q, for each
configuration and family. Previous grid points provide four additional failing
final comparisons. The retuned consumer checks and its four controls are
described above.
`RESULT.json` contains the complete receipts.

Logarithm bounds use the first 80 terms of `2*atanh(u)`, with binary range
reduction and the tail bound `2*u^161/(161*(1-u^2))`. Exponential bounds use
48 positive Taylor terms and the geometric upper tail beginning at term 49.
Every exponential argument is checked in `[0,1)`. Displayed decimal intervals
are rounded outwards; all decisions use exact fractions or integers.

Local validation used Python 3.12.8 on macOS 26.5.1 arm64, with the same receipt
also generated under Python 3.14.5. The registered replay and metadata/pin check
passed. An inode-independent, Git-free copy passed `python3.12 -I -O -B verify.py`
in 8.77 seconds while another light check ran; changed-input and changed-receipt
controls both rejected. Timings are host-dependent.

The algebraic proof above is not machine-formalized. No native circuit replay,
delayed-cover implementation replay, full multiplication theorem, Lean build,
Docker run or historical replay suite is part of this bounded quantitative change.

## Provenance, overlap and scope

Scientific predecessor: zxv's PR4359 head
`da637c87c89482bc4c86be36bd0071b3d400dbed`, including its finite compiler,
explicit-rank estimate, productive complex controller and delayed BIT cover.
The integer lockstep construction and Theorem 1G are Jacob Alan Sussman's
work, retained by that PR from `wht-power-saving-lean` commit
`563b4e6e913625637f36ba7869bf5fcd0dd4975a`. The original repository supplier,
PR589 BIT word and the contributor lineage recorded by PR4359 retain credit.
This package contributes the logarithmic majorant, its sufficient ranks and
the compatible outer retuning.

The publication base is canonical main
`12fa8c5c844be21bfefb38a19503fbd867a11244`, priority revision 7. Ten immutable
inputs from the pending predecessor are included so this focused follow-up
can replay independently of whether PR4359 has merged. `SOURCES.json` pins
main's orientation metadata; `VENDOR.json` separately binds the copied inputs
to their original commit, paths, Git blobs and SHA256 hashes. This is an
offline byte binding, not an independent replay of their producers.

The overlap refresh covered 513 open PR bodies and 3,250 discussions/comments,
with complete reported pagination at 2026-10-21 17:02 UTC, plus local package
notes and the ledger. It did not search remote closed PR bodies or every code
diff. [pinterbanget's initial claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19102222)
targeted the predecessor's recurrence and H0/H1 chain. Before submission, they
published [PR4404](https://github.com/CrocSwap/integer-mult-bounds/pull/4404), head
`77f20afb7c24286937c75cb65a7f19e24e7a567f`, reporting that the original arithmetic,
exit bound and induction hold, with separate flow simulation through rank 10,000.
That is external evidence about the predecessor, not independent review of this
new majorant or its retuned consumer. No part of PR4404's code is imported.

The same refresh located parallel [PR4405](https://github.com/CrocSwap/integer-mult-bounds/pull/4405),
head `873d1b3c96a83b701a5c0bba8e37a861e6672fef`. It sharpens the original
power-majorant coefficient and proposes a higher conditional κ = 0.00230509.
At the original supplier savings it reports rank exponents 1,546,084,442 and
42,843,607. Our unchanged-saving exponents 2,352,000 and 529,000 improve those
sufficient estimates by a different argument. Its higher-κ parameter point is
not instantiated here, and no part of its code or proof is imported.

## Open next questions

1. **Sharpen the logarithmic exponent using actual source/exit distributions.**
   A useful first test is a uniform bound on their complete weighted ratios,
   rather than just the worst-case `eta` and `theta_bar`. This could lower H
   further; another q grid by itself would add little evidence.
2. **Bound productive width and total program size.** Start with compressed
   recurrences for `B_N`, `P_N`, batch denominators and owned-unit counts.
   Ambient rank alone does not bound the complete constants. Integer batch
   growth and the absence of a materialized winning word remain the blockers.
3. **Review the inherited compiler and native/outer transfer independently.**
   Follow the existing source/exit audit, then separate the native closure,
   delayed BIT cover and outer support obligations. Their acceptance remains
   necessary before interpreting either set of sufficient ranks as an
   admitted multiplication result.

4. **Combine with PR4405's higher proposed κ endpoint.** Pin its exact
   parameter point, choose a strict rational tested `t`, then apply (5) and
   reprice the full consumer. The logarithmic majorant is general, but that
   extra point and PR4405's scientific acceptance are not checked here.

Prepared by zxv with substantial OpenAI Codex assistance. Apache-2.0. No
subagents or independent human mathematical review were used for this package.
