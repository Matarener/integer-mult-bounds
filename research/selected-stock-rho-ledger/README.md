# Selected m=73 row ledger: the non-complex terms do not bind `rho`

**Card `selected-stock-envelope`, scope refined. Partial. No new κ.**
[#3113](https://github.com/CrocSwap/integer-mult-bounds/pull/3113) and
[#3421](https://github.com/CrocSwap/integer-mult-bounds/pull/3421) bound `B`
and `A` for the selected m=73 complex producer:

```text
sigma <= (43/26)*(1-s)*(A+B) + rho,    A = 0,  B = 2642
```

That leaves `rho`, the leaf reserve, as the only unbound term. This package
traces every non-complex term of the selected row ledger to its source. It
shows that those terms cannot serve as `rho`, and that the selected layer's
construction uses none of them. It then reads the merged
selected complex layer to settle how its callees get their stock: the layer's
only row stock is its own divisor, so `S_leaf = 1` and `rho = 0`. This holds
conditionally on that chain. All fourteen recorded stage guards pass either
way.

```sh
python3 -I -B research/selected-stock-rho-ledger/verify.py
```

Expected:

```text
PASS_SELECTED_STOCK_RHO_LEDGER B=2642 ledger=16469 9909=367*27 252=9*28 1024=2*512 bit_row=18355=8194+9909+252 implicit_rho_3113=11185 rho_a=0 sigma_a<=4362.14 rho_b=8194 sigma_b<=12556.14 L_bits=2642 S_leaf=1 guard=16,17<=6562783 stages=14 H_min=6562783 lean_row=6308 qadic_bit_row>=655356>20161 controls=16 checks=62
```

Python 3.12 standard library, under one second. The verifier authenticates
every live input listed in [SOURCES.json](SOURCES.json). It reads three
members of the pinned PR1087 tarball in memory; its `code/assemble.py` hash is
the one `selected-bootstrap-stock-audit` pins. Every constant is parsed from
source text, not typed in. Nothing from the repository is imported or executed.

## Source facts

1. **The selected ledger.** Frozen PR1087 `code/assemble.py` asserts the
   ledger `2*stock.bit_length()+9909+252+1024`, which gives 16469. It also
   asserts the retained cap `20161` and the external degree gap
   `10^6 - (51/25)*20161`. That gap is the selected `ASSEMBLY.json`
   `outer.row_product_gap = 23971789/25`.
2. **9909 and 252 are historical family charges.**
   `notes/partial-gauge-assembly.tex` gives the "coarse bit, ordinary leaf and
   complex families" the (halving degree, wire bits) pairs `(367,27)`,
   `(9,28)` and `(200,28)`. Hence `9909 = 367·27` and `252 = 9·28`. Later
   assembly notes carry them forward unchanged as "conservative previous bit
   and ordinary-leaf reserves" (`58344+9909+252`, `10284+9909+252`). The
   367-level coarse-bit family is not the selected PR589 BIT producer, whose
   halving depth is 2.
3. **1024 is the row surcharge for the 512-bit prefix payload.** The payload
   is the invoice's precision reserve: the bits by which an intermediate value
   of the selected complex program may grow. PR1087's invoice needs the local
   prefix bits plus `37+144+144+4` (`code/assemble.py` L165). These pay for
   the input conversion, one bit per complete invocation sweep, one bit per
   bridge sweep, and a 4-bit margin. Here that totals 397 (tarball README
   L14). `code/invoice_allcold.py` charges `payload = 512` (L263, L285–288)
   and adds `row_prefix_extra = 2*payload` to the complex row (L278, L297).
   "What the 1024 term pays for" traces the factor 2.
4. **The selected BIT ledger stacks the same constants.** PR510's
   `assemble9.py` computes `row = DEPTH*(m*m+1)+9909+252 = 18355`. With
   PR589's `nine.bit` record (m=64, maximum child 42, 28,425 physical roles,
   halving depth 2), the BIT family's own term is `2·(64²+1) = 8194`. That is
   the coefficient
   [PR2084](https://github.com/CrocSwap/integer-mult-bounds/pull/2084)
   (`research/selected-bit-parent-reserve`) proves conditionally. PR2084
   already reads this formula and argues that the other outer allowances do
   not enter the BIT sigma. That BIT-side observation is not new here.
5. **The two stocks have different units.** The assembly notes define a row
   coefficient as the degree of a **fixed external polynomial reserve**:
   `log2 Q <= (51/25)·K·log2 p`, and `p^(10^6)` for the selected assembly.
   They state that the width-dependent q-adic selector stock is "supplied by
   the separate internal borrowing proof, rather than multiplied into this
   external polynomial stock". H3,
   `log_q S(e,w) <= sigma·w·(1+log2 e)` with `k < e/2`, constrains that
   internal borrowed stock.
6. **The selected complex layer's only row stock is its own divisor.** Jose
   Manuel's PR2287 (`selected-complex-layer-closure/PROOF.md`) is the written
   all-size m=73 layer. PR3385 implements it physically; the PR ledger records
   intake checks only for that archive, with no scientific verifier run. A
   local replay is in "PR3385 replay and B1's fit". PR2287 sets
   `W = 14336` and `L = W·|O(73,2)|`. Its only row stock is `L^D0(d)`, taken
   from a prefix of `q0 = ceil(log2 L)·D0(d)` chunks. A child receives `U`
   with `L^D0(e') | U`, and "a completed child restores its own row labels".
   - **Peeled axes and stopped leaves.** The layer processes the
     `e mod 73` leftmost axes individually, and "the leaves require only the
     elementary C kernel". These calls have no callee and need no stock.
   - **Compact fields.** The root also reserves `qF + qB` chunks for three
     H-bit compact fields (`H = dG`, `G = 4⌈log2 p⌉ + 6`). They may start
     dirty, and the adapters restore them. "No compact-field bit enters this
     selector", so they are not row stock and lie outside A, B and `rho`.
   - **Ordinary/BIT calls.** The only ones sit inside PR2250's compact
     adapters, which run them on `(f-1)G`-bit pieces of the compact fields.
     PR2287 says its bound uses "an ordinary binary chunk interchange …
     PR2234 proposes that contract". PR2250 grants that callee "no external
     row stock or ancestor access". PR3385 binds it to B1/C0 (L17–19).
   - **The callee's own stock.** PR2234 §8 (realized physically as B1 in
     PR2899) chooses its own stock `S=K(w)^D(e)` with `log_q K <= 4097w`. It
     borrows `k=ceil(log_q S)` leading digits of its own chunk, so inside the
     compact-field piece it was given. Below the fitted range it falls back to
     elementary interchanges. With halving
     depth 2 that stock is exactly PR2084's `8194` coefficient.
   - **The divisor matches B.** `ceil(log2(14336·Γ)) = 2642`, the same as
     #3113's B. The divisor is w-free, consistent with #3421's `A = 0`.

## What follows for `rho`

- #3113's conditional readings sigma ≈ 16469 or 15555 put the external-ledger
  constants `9909 + 252 + 1024 = 11185` into the borrowed-stock envelope. The
  verifier reproduces `15555 − ⌈43·2642/26⌉ = 11185`. Those constants are
  w-free degrees of an external reserve, and 9909 belongs to a historical
  family. So the ledger does not supply a source-bound `rho`. The control
  `ledger_constant_as_rho` rejects 9909 as a w-free bound on the w-shaped BIT
  term, because `9909 < 8194·w` for every `w >= 2`.
- **Reading (a), completed callees, is what the selected layer does.** Every
  callee inside an m=73 node is either elementary or a completed ordinary call
  that borrows internally and restores (fact 6). So `S_leaf = 1`, as
  `selected-coarse-depth-stock/PROOF.md` already allowed conditionally. Then
  `rho = 0` and, at native stage 1,
  `sigma <= (43/26)(1-s)·2642 ≈ 4362.14`, with `ceil(log2(8·sigma)) = 16`.
- **Reading (b), the parent reserving the BIT factor, is kept only as a
  counterfactual.** An earlier version cited `structured-bulk-assembly.tex`'s
  "Both factors are reserved simultaneously" for it. That sentence concerns
  fixed-wire *external* factors (`W_b,W_c<2^{43}`, bounded in `p^{108000}`),
  the kind the selected ledger pays as 9909. It is not the w-shaped BIT
  stock. If a parent did reserve that stock, `rho` would have to dominate
  PR2084's 8194. That gives `sigma <= 12556.14` with guard 17, which still
  passes.
- **All fourteen recorded stages pass both values.** That is native stages
  1–7 and conservative stages 1–7, each with its branch's own `s` and its own
  headroom. For each stage record, the verifier re-derives
  `H_j = floor(L_j·gap_j/2) − 4` from the recorded `L_j` and gap. It checks
  that the gap is the least of the four recorded gaps, that the stock gap is
  `1 − s`, and PR1965's premises (`L ≥ 2`, `L·gap² ≥ 36`,
  `0 < gap ≤ 1 − s`). The tightest stage is stage 1
  in both branches, at `H = 6,562,783`. The guards are only 16 and 17.
  No selected step bootstraps the complex layer (see "Where the H3 fit
  applies"), so these are consistency checks, not obligations.

## What the 9909 and 252 slots pay for

The selected certificate charges the complex row
`2·2642 + 9909 + 252 + 1024 = 16469`. Separately, it charges the BIT row
`8194 + 9909 + 252 = 18355`. Both are checked against one cap, 20161
(`assemble.py` L159, L173, L204).

- **No selected family has the 9909 or 252 parameters.** The selected BIT
  is halving depth 2 with `64²+1` bits, giving 8194. The selected complex
  layer's peeled axes and leaves are elementary C kernels (fact 6). The pairs
  `(367,27)` and `(9,28)` are historical families.
- **In the selected layer, the two slots pay for nothing.** Its only row
  stock is `L^D0(d)`, and its BIT callee borrows internally. Without the
  slots, the complex row is `2·2642 + 1024 = 6308`, so they are inherited
  slack. Dropping them would not change κ: the physical row only has to stay
  below the retained 20161, and only that retained cap enters the outer
  assembly, through the strict degree-gap constraint.
- **The BIT's 8194 here is a binary model.** The certificate's 8194 is
  PR510's model of the BIT, with `m²+1` bits per level. In that model, 8194
  would fit in the 9909 slot (`6308 + 8194 + 252 = 14754 < 20161`), so the
  cap check alone decides nothing about how the BIT gets its stock.
- **The BIT the adapters call is q-adic, and its stock cannot fit the
  cap.** The adapters call PR2234's BIT, which has `q > 2^80`. Its level
  divisor has at least `4096·80 − 2` bits, because
  `|GL_64(F_q)| ≥ q^4096/2`. In the certificate's own row convention
  (halving depth × bits per level), that gives a row term of at least
  `2·(4096·80 − 2) = 655,356` at `w = 1`. That is over 32 times the 20161
  cap, and it grows with `w`. So the row ledger cannot be holding that
  stock. It is borrowed inside the call, as fact 6 says, and this is the
  same w-shape point as fact 5 and the `ledger_constant_as_rho` control.

## What the 1024 term pays for

The 1024 is a precision reserve billed as row stock, and the selected layer
does not use it.

- **The factor 2 is the halving depth.**
  - The term entered with Dugongue's PR514. That PR replaced the old 192-bit
    local prefix allowance with a 512-bit global one, for asynchronous
    scheduling.
  - Its invoice says "512 bits are charged, and an additional 2*512 enters
    the two-level physical row bound". PR523 vendors it unchanged, with the
    same Git blob as PR514's head, at
    `research/punctured112-global/vendor/pr514/code/audit_async_invoice.py`
    (scope L96, row formula L87).
  - The PR484 invoice it replaced, vendored alongside, has no payload term
    (`vendor/audit_scalar_invoice.py` L78).
  - Two levels halve the width, because `73² > 2·48²` (PR2287 L129–130). So
    the payload is billed once per halving level, like the stock bits.
  - Hao Yan's PR858 T16 proof, whose controller PR1087 uses (tarball README
    L20–21), calls this "the retained row formula"
    (`research/complex-double-replica-owners/PROOF.md` L166–170).
  - The same sentence appears earlier in Dugongue's closed
    [PR505](https://github.com/CrocSwap/integer-mult-bounds/pull/505).
- **No source says why a precision reserve is row stock.**
  - PR505, PR514, PR858, PR1087 and the assembly notes all state or compute
    the term. None names a construction step that needs `2^512` extra rows at
    each halving level.
  - The assembly notes' "physically preceding prefix" is a different object.
    It is the run of `q0 = ⌈log2 Q⌉` chunks that supplies the rows. Its single
    padding grows volume by less than two (`structured-bulk-assembly.tex`
    L84–91). Neither the prefix nor the padding is 512 bits.
- **The selected layer keeps rows and precision apart.**
  - PR2287 reserves exactly `L^D0(d)` rows, from `q0 = ⌈log2 L⌉·D0(d)` chunks
    (L136–147). That is the `2·2642` term.
  - It supplies precision separately, with `Δ = ⌈C0·d⌉` guard bits on each
    component (L374–380).
  - It calls the finite 397-bit bound "useful bindings, but they are not this
    all-depth proof" (L363–364).
  - PR3385 does the same physically. It pads the row range once to a multiple
    of `L^D0(d)` (`PROOF.md` L190–197), and it appends `Δ` low zeros and
    `Δ+1` sign bits to each component (L199–201).
- **So 1024 is inherited slack, like 9909 and 252.** The marker's lean row
  of 6308 still contains it. The selected layer's own row need is the stock
  term `2·2642` alone. Removing the 1024 would not change κ, because only the
  retained 20161 enters the outer assembly.

## Where the H3 fit applies

No selected step bootstraps the m=73 complex layer.

- **The bootstrap chain is the bit chain.** The selected assembler builds
  one seven-step chain per branch, then calls
  `A.assembly(chain[-1],bb,...)` (PR1087 `code/assemble.py` L205–214).
- **The complex saving is a fixed input.** The pinned `engines/outer.py`
  (`research/complex-k492-owner-repair/vendor/multicold/`, the copy PR1087
  pins) takes the chain's end as `bit_saving` and the complex root `bb` as
  `complex_saving` (L16–17).
- **It only caps `s`.** The complex saving reaches the chain only through
  `s=min(c,(1-beta)*bb)-1/10^27` (`assemble.py` L206). That cap is what the
  outer slacks `complex_above_bit=b-a` and `leaf_saving_above_bit=(1-beta)*b-a`
  need (outer.py L27, L29).
- **The layer itself has no stage.** Its fallbacks are elementary kernels,
  not a previous-stage algorithm. PR2287 says "If D<=Q0, apply the selected
  C kernels individually" (L139) and "The base cutoff is max(73,d^beta)"
  (L424). Where its compact-field inequality fails, it uses "individual
  kernels" (L442–443).

So this package's m=73 sigma is a consistency bound, not an obligation of
the selected record. The H3 envelope the record needs belongs to the bit
producer, for example PR2084's conditional 8194.

## PR3385 replay and B1's fit

This is local evidence, outside this package's verifier. It was run with
Python 3.12.10 on Windows 11 at `2b4a97e`. PR3385's 38 package files there
have the same Git blobs as its head `7e5a187`.

- **The registered replay fails on Windows only.** It stops in the second
  check. The cause is a frozen predecessor verifier: member
  `inputs/pr2753/verify.py` of
  `research/physical-ordinary-interchange/inputs/pr2809.tar` (L72–75). It
  compares `str(path.relative_to(...))` with `/`-separated names. On Windows
  that string uses `\`, so it raises "no omitted or extra predecessor files".
  This is a portability issue, not a mathematical failure.
- **With a local path shim, all three suites pass.** The shim only makes
  relative paths print with `/`. It is not part of this package, and the run
  is not the registered replay.
  - The `sources`, `execution` and `planning` suites print their PASS
    markers, over 16 checks.
  - All nine receipt hashes in PR3385's `EVIDENCE.md` (L17–25) match.
  - The fixtures reach only B1's elementary branch (`check_monomial.py`
    L66–67).
  - On this laptop the `execution` suite took 727 s, longer than its
    registered 420 s timeout.
- **B1 borrows only on very wide compact fields.**
  - The adapters call B1 only on compact fields of width `nG`, with
    `n = f-1` (PR2250 `PROOF.md` L20, L73–74).
  - B1 turns `b` bits into `e = ceil(b/log2 q)` radix-q digits (PR2234
    `PROOF.md` L412–413).
  - B1 runs its fitted branch only if `2k < e` and the body has at least 64
    atoms (PR2899 `PROOF.md` L71–78).
  - At `q* = 213·2^80+1` (PR3385 `PROOF.md` L43), `k < e/2` holds for
    every `e >= 311311` and fails at `e = 311310`
    (`bit2234-stock-threshold/README.md` L34–35, L137–140).
  - So B1 is fitted when `(f-1)G >= bitlength(q*^311310) = 27,312,693`
    bits. Below that it runs its elementary branch, as PR2234 (L408–410),
    PR2899 (L80–85) and PR3385 (`PROOF.md` L185–186) say.
  - The widths can only reach that size when the precision p is at least
    19,782,090. This uses `f = floor(e/73)` (PR2287 L159–160), plus
    `d = floor(p^(997/1000))` and `D <= d` (PR3385 `PROOF.md` L9–10).
  - A local exact-integer check, not part of this package, confirms these
    numbers. It also finds no fitted width below 311311 at q*.
- **Neither branch takes row stock from the caller.** The fitted branch
  borrows `k` leading digits of its own earlier chunk (PR2234 L382–388). The
  elementary branch is one atom swap over `Z/q^e` (PR2899 `ordinary.py`
  L106–114). So `rho = 0` is unaffected.

## Controls

Each of these must be rejected:

1. A flipped byte in a pinned input.
2. A ledger constant changed to 9908.
3. The family wire bits changed to 28.
4. `Sp(70,2)` in place of `Sp(72,2)`.
5. A prefix extra of 2048.
6. The eleven-stage BIT record.
7. A tampered `row_product_gap`.
8. 9909 used as a w-free `rho`.
9. The `S_leaf=1` premise removed.
10. A guard set below sigma.
11. PR2250's adapter callee given external row stock.
12. PR2234's per-level stock coefficient changed to 4098.
13. PR2287's leaves given a BIT reserve.
14. PR2287's divisor family count doubled.
15. A tampered headroom on the last conservative stage.
16. PR2234's prime bound lowered to `q > 2^2`.

## Not claimed

- No supplier, κ, cutoff, frontier or selected-record change.
- The stage records are the `selected-bootstrap-stock-audit` receipt. Their
  cutoffs and gaps are taken as recorded, not recomputed from the selected
  savings.
- `rho = 0` rests on PR2287, PR2250, PR2234 and PR2899. The PR ledger
  (`docs/research/pr-ledger.json`) records all four as `incorporated` after
  a scoped review of written constructions with passing replays. None is an
  executed GL64 or O(73,2) machine or a formal proof. PR2234 itself says
  "Independent mathematical review remains necessary" (PROOF.md L432).
- PR3385, the physical controller, is only `partially_reviewed` in the PR
  ledger, after source-only archival intake. The local Windows run in "PR3385
  replay and B1's fit" used a path shim. It is not the registered replay and
  not an independent review of PR3385's refinement. #3113 (B) and #3421
  (`A = 0`) are also only `partially_reviewed`.
- No physical O(73,2)/GL64 payload has been run by those sources or by this
  package.
- The PR2084 coefficient is used as that package's conditional result, not
  re-derived.
- "No source says why" covers only the sources named in "What the 1024 term
  pays for". It does not show that no construction could use such a reserve.
  It shows only that the selected layer's construction does not.
- This is a finite source-bound audit, not a supplier replay or a
  multiplication theorem.
- Overlap covered open and closed PRs and package READMEs. It also covered
  Discussion search for the terms in TASK.json, Discussions #2238 and #2319
  in full, and the latest 100 comments of #1166. For the 1024 term it also
  covered PR and code search for `row_prefix_extra`, `charged_prefix_bits`
  and "two-level row".

## Open next questions

None remain within this card's scope. [TASK.json](TASK.json) records the
reason: every ledger term is now bound, and the H3 envelope that the record
needs belongs to the bit producer (PR2084), outside this package.

The last question was which construction step uses the 1024 prefix term.
"What the 1024 term pays for" answers it: none in the selected layer. The
earlier questions are answered here:

- which reading the selected layer realizes: fact 6;
- all fourteen stages: "What follows for `rho`";
- what the 9909 and 252 slots pay for: "What the 9909 and 252 slots pay for";
- whether an H3 envelope applies to the complex layer: "Where the H3 fit
  applies" (it does not);
- the PR3385 replay and B1's fit at compact widths: "PR3385 replay and B1's
  fit".

## Credit

- Aaron Wang (#3113, `selected-stock-envelope-m73`) bound `B = 2642` and
  stated the missing `A, B, rho` lemma.
- Wentao Li (#3421, `selected-stock-shape-a-zero`) proved `A = 0`.
- Sricharan Vagvala (#2105, `selected-coarse-depth-stock`) supplied the
  `43/26` depth rate, the composition formula and the conditional
  `S_leaf = 1` sentence.
- Adam Gall (PR2084, `selected-bit-parent-reserve`) supplied the conditional
  BIT coefficient 8194, its completed-leaf hypothesis and the BIT-side reading
  of the 18355 formula.
- Josie Elliston (PR1965) and ToikY (`selected-bootstrap-stock-audit`)
  supplied the stage receipt and guard.
- Aakash (`bit2234-stock-threshold`) proved the sharp 311311 borrowing-fit
  cutoff that the B1 threshold uses.
- philippeVV (Discussion #1166, comment 18932239) independently named the
  PR589 BIT, not the m=73 supplier, as the stopped producer, minutes after
  PR2084 opened.
- Jose Manuel supplied the selected complex layer and its physical
  controller (PR2287, PR3385), the compact adapters (PR2250, which retains
  Douglas Colkitt's compact-control method), the selected BIT interchange
  (PR2234) and the physical ordinary wrapper B1 (PR2899, around Nick
  Petalas's PR2808 wrapper). Fact 6 reads them; it adds no construction.
- Jeremy Kothe (PR1087) and Rohan Arun (PR1094) supplied the selected
  assembler and invoice. The partial-gauge, three-stage, paired-cube and
  structured-bulk assembly notes keep their original attribution.
- Dugongue (PR505, PR514) introduced the 512-bit global prefix allowance and
  its two-level row charge. Hao Yan (PR858) retained it in the T16 reserves.

Prepared by Mainzu, with substantial Claude Code (Anthropic) assistance. No
independent human review is claimed. Apache-2.0.
