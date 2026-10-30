# Current-budget obstruction for the fixed unpooled R437 moment contract

The published unpooled host of [PR #4067](https://github.com/CrocSwap/integer-mult-bounds/pull/4067), head a95f11c52e3ca1e4c5171b3c20d8f4b0815aee2e, cannot satisfy its retained moment-certification budget at the current admitted BIT target, even after every nonnegative surcharge is omitted optimistically. This is a statement about a fixed invoice and certification method. It is **not a runtime lower bound, a universal R437 exclusion, or a result about a changed pooled caller**. [Canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/4682#discussioncomment-19205685).

The exact host uses dimension64, productive width28416 and paid profile:

```
{1:380448,2:400288,3:22464,4:26592,5:29376,
 6:17376,7:26496,26:32,42:384}
```

The source supplies903456paid children and rank mass1808352. Its288calls and125856hosted owner occurrences are predecessor results, not newly rebuilt here. The source carrier changes each local (2,2) query pair to (1,3), retains rank mass, and adds3scalar ADDs per call,864overall. Its reverse coefficient1123650 is already reported in #4067/#4147; this package does not rederive it or certify its stock/precision envelope.

## Exact result

The live selected certificate distinguishes ordinary BIT saving8590884599/2500000000000, admitted BIT saving s=17/5000 and whole multiplication kappa62009/20000000. The admitted value is the weaker necessary supplier target; whole kappa is not the moment target.

For the frozen profile let M0(c)=sum n_r*r/(64*28416)*exp(c*log(64/r)), with all extra charges omitted favorably. The elementary inequalities log(x)>=2(x-1)/(x+1) for x>=1 and exp(y)>=1+y give:

```
M0(c) >= L(c) = A+B*c,
A = 18837/18944,
B = 227656981418642299/126181391898481920 > 0,
L(17/5000)-1 = 18039021780054799/37112174087788800000 > 0.
```

Thus **every c>=17/5000 fails M0(c)+D(c)<=1 for every nonnegative added normalized charge D(c)**. No numerical log, exponential or root search is used. The quantified implication is proved in PROOF.md; finite exact arithmetic authenticates its constants.

The budget-contract premise is the retained contraction/moment gate requiring M<=1. A failed upper-bound recurrence test does not lower-bound actual runtime or exclude a different analysis. Under the separately declared ordinary bridge0<=a<=c, reaching a>=s would require one of these rejected c values. The historical #3690 text uses a=c(1-c) at c=1/576, with c<1/512 and physical refinement assumptions. Dropping that range is only a favorable mathematical relaxation. This package does not extend its physical theorem or establish physical refinement of the changed #4067 host.

## Evidence and controls

RESULT.json records each rational term, source/AST-site bindings, current budget stages and six controls. The separate ORACLE.json independently accumulates an integer common denominator and proves a positive cross-product gap78505822786798485248. Neither checker imports the other or executes predecessor code.

The controls expose model dependence. At c=0, M0=L=18837/18944<1. Moving rank42jobs to rank1 preserves total paid calls and makes this lower-bound screen inconclusive, but the frozen-profile guard rejects the substitution; it is not a physically realized improvement or admission. Using whole kappa also loses this particular lower-bound rejection and is rejected as the wrong target role. Wrong productive normalization, source-byte drift and typed receipt aliases reject. The oracle additionally rejects negative saving. Default complete canonical receipt comparisons preserve bool/int/float distinctions.

Source bytes are copied directly from current main and checked by raw SHA256/Git blob identity. The primary statically checks selected price AST sites; the complete source formula is also read and stated explicitly in the proof. This does not execute or independently replay the original host. All runtime inputs are package-local and no dependency installation is needed.

## Reproduction

Python3.12, standard library:

```sh
python3.12 -B scripts/research_package.py --package research/r437-unpooled-budget-obstruction
```

Registered normal/optimized primary and separate optimized oracle use explicit guards. --emit is an explicit candidate mode on stdout and never rewrites a receipt. SOURCES.json pins main ancestry separately from the mathematical contract. Metadata, committed-byte/mode, export and cold checks are integrity evidence, not supplier admission. No native, source-word, pooled compiler, full selected replay or Lean build ran.

## Open next questions

A different invoice, productive normalization, target allocation, transfer law or moment analysis needs its own bound. The [released pooled allocation](https://github.com/CrocSwap/integer-mult-bounds/pull/3967#issuecomment-6267387753) already exists and changes the profile; its complete pooled price and regenerated physical catalogue remain open. This result does not call that work unperformed or exclude it. The #4682 stock/payload/caller handoffs remain separate.

Freeze a complete changed pooled invoice and receiver contract before applying this screen. Native/compiler/stock/precision/tape/analytic obligations and the five framework assumptions remain open. No selected-frontier or kappa change follows; independent acceptance remains.

## Credit

Chris R/Clear1nsight supplied #4067's carrier, fixed host and price; unpaidmoon supplied #4147's reverse-envelope distinction. Retain ai-nanachi/#3647, Ali Romman/#1043, Sagar Thakrar/#3700/#2423, zxv/#3690, mightyOil/#1281, Rohan Arun/#3959 and all source/native/hosting/physical/compiler/analytic authors in NOTICE. #3668/#3700 already cover historical profiles/root comparisons; no such result is claimed as new here. The new contribution is this compact revision8 budget implication and independent exact certificate. ToikY with substantial OpenAI Codex assistance in separate primary/oracle/proof-review contexts. Classical inequalities are not new general discoveries. Apache-2.0.
