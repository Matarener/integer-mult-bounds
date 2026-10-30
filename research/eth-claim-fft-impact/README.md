# If the reported ETH disproof holds: what changes for fast transforms and multiplication

No new κ. If the claim holds, no hub record changes.

Jacob Sussman. Apache-2.0. Written with AI agents (Anthropic Claude); see *AI assistance and credit*.

## 1. The point

OpenAI has released a preprint claiming that the Exponential Time Hypothesis is false. If the claim holds, no κ
record on the hub changes and nothing proved falls. One conditional barrier next to our transforms, Josh Alman and
Baitian Li's bound for depth-2 Walsh–Hadamard circuits, gets weaker but survives. The new algorithm is no use for
the hub's SAT searches. What may matter most here is the technique: the preprint's core matrix construction is a
relative of the polynomial trick behind "the Walsh–Hadamard matrix is not rigid".

The claim is unreviewed. OpenAI's repository says that an independent working group led by Russell Impagliazzo,
Ramamohan Paturi and Ryan Williams will examine and explain the proof. Everything below is conditional on the claim
holding. With a small team of AI agents I mapped, item by item, what would change for the hub's world:
multiplication, the discrete Fourier transform (DFT) and the Walsh–Hadamard transform (WHT).

**Three hypotheses, one sentence each.**
- The *Exponential Time Hypothesis* (ETH) says that 3-SAT (deciding whether a formula with at most three variables
  per clause can be satisfied) needs time at least 2^(c·n) on n variables, for some fixed c > 0.
- The *Strong Exponential Time Hypothesis* (SETH) says more: as the number k of variables per clause grows, k-SAT
  needs time ever closer to 2^n, so no single speed-up to 2^((1−ε)·n) works for every k.
- The *Orthogonal Vectors Conjecture* (OVC) says that, given N vectors of 0s and 1s of length c·log N, deciding
  whether two of them never have a 1 in the same place needs time close to N²: for every ε > 0 there is a c for
  which N^(2−ε) is not enough.

SETH implies both ETH and OVC. I know of no implication between ETH and OVC in either direction.

**Status words.** *Claimed*: stated in OpenAI's preprint, not yet reviewed. *Follows if the claim holds*: a short
implication from the claim. *Argued by hand*: a written argument, checked by no person and no proof checker.
*Theorem*: proved with no unproved hypothesis, in print or in Lean. *Conditional on X*: rests on the named
conjecture X. *Speculation*: a question; nobody claims it. *Recalled*: a standard result not re-read for this map.
One AI reviewer, whose only job was to break the map, attacked every step; its corrections are folded in.

## 2. What the preprint claims

For every fixed clause width k, a deterministic algorithm counts the satisfying assignments of a k-CNF formula with
n variables and m clauses, in polynomial space and time poly(n + m) · 2^(O_k(n · ln ln n / √(ln n))). When m is at
most a constant times n, the exponent improves to O(n / √(ln n)). *Claimed.*

- For k = 3 this is one algorithm with running time 2^(o(n)), so it is ETH itself that is claimed false, not a
  variant. *Follows if the claim holds.*
- It is only just below exponential, not 2^(n^(o(1))). The preprint itself says such bounds do not carry over to
  other NP problems through general polynomial-time reductions.
- The Lean statement has a weaker exponent, n · (ln ln n)² / √(ln n), still o(n). The sharper bound, the
  sparse-case bound and the circuit corollaries are outside the Lean scope. This map does not rely on the Lean
  proof, and it was not built for it.

## 3. What falls, if the claim holds

| What | Why | Status |
|---|---|---|
| ETH, SETH, Gap-ETH, NSETH, #ETH and their randomized versions | the algorithm decides and counts, deterministically, for every fixed k | follows if the claim holds (the preprint lists them) |
| Some lower bounds outside the FFT world: "no 2^(o(v)) algorithm" for q-colouring, independent set, vertex cover and clique on v vertices, and Radu Curticapean's #ETH-based bound for counting perfect matchings | each problem can be written as a fixed-width formula with O(v) variables, so the algorithm beats the bound. Curticapean's implication "#ETH ⇒ bound" stays true; it is the bound that falls | follows if the claim holds (the preprint gives the counting corollaries for colourings, independent sets and perfect matchings; the other encodings are argued by hand) |
| **Nothing on the hub, nothing of mine, and no result on multiplication, the DFT or the WHT that I know of** | each is a theorem, or rests on a conjecture that neither implies ETH nor contradicts what the algorithm does | argued by hand. I found no κ record, target, certificate or framework assumption on the hub that uses ETH, SETH or OVC |

## 4. What survives

### 4a. Unaffected

| What | Why | Status |
|---|---|---|
| Every selected and historical κ record on the hub | upper bounds on the hub's own framework and model assumptions, not on any complexity conjecture | unaffected |
| My Lean-checked savings, 1.7887045e-3 for the DFT and 1.5699306e-3 for the WHT, and my 5/6 and 3/4 operation counts for the WHT | proved in Lean with only the three standard axioms; a correct theorem cannot contradict a proved one | theorem |
| My two earlier hub notes | they use no complexity hypothesis | unaffected; each result keeps the status given in its note |
| Unconditional lower bounds: Jacques Morgenstern's Ω(n log n) for the DFT with bounded coefficients; Ω(N log N) for depth-2 WHT circuits (Noga Alon, Mauricio Karchmer and Avi Wigderson); Paterson, Fischer and Meyer's bound for on-line multiplication; Leslie Valiant's theorem that a sufficiently rigid matrix has no linear-size, logarithmic-depth linear circuit (the claim produces no rigid matrix) | no hypothesis | theorem (Morgenstern, Paterson–Fischer–Meyer and Valiant recalled) |
| Non-rigidity and fast-transform results: Josh Alman and Ryan Williams (the WHT is not rigid); Zeev Dvir and Allen Liu (Fourier and circulant matrices are not rigid); Josh Alman, Yunfeng Guan and Ashwin Padaki (Kronecker powers); Josh Alman and Kevin Rao ((23/24)·N log₂ N + O(N) operations for the WHT, (15/4)·N log₂ N + O(N) for the DFT); David Harvey and Joris van der Hoeven (O(n log n) multiplication); OpenAI's DFT preprint (o(N log N) operations) | no hypothesis | theorems; OpenAI's DFT result is a preprint, and it states no hypothesis |
| Peyman Afshani, Casper Benjamin Freksen, Lior Kamma and Kasper Green Larsen's Ω(n log n) for multiplication circuits, the lower bound usually quoted against the hub, and the hub's coding-gap work on it (by ShikeChen01 and philippeVV) | conditional on the network-coding conjecture of Zongpeng Li and Baochun Li, which has no known link to ETH | conditional on that conjecture; unaffected by this claim. Separately, two preprints of 7 October 2026 (Xindan Zhang, Baochun Li and Zongpeng Li; Mark Braverman and Zhongtian He) claim counterexamples to the conjecture. Neither is refereed, and I make no claim about it |
| Dugongue's notes carrying the preprint's method to the hub's Gaussian axis (#5813 and its follow-up #5815) | they re-prove the local lemmas they borrow; #5813 says it is independent of the preprint's main theorem | #5813: as stated there; #5815: argued from its pull-request description |

### 4b. Survives, on less support

- **The Orthogonal Vectors Conjecture.** No known reduction lets the claim refute it. The standard link runs from
  SAT to Orthogonal Vectors (Ryan Williams, 2005), which is why SETH implies OVC. Going back would need a reduction
  from Orthogonal Vectors to fixed-width SAT with only about log N variables (√(ln ln N) times more is tolerable with
  the sparse-case bound). None is known, and a formula that stores an arbitrary instance needs far more variables
  than that. What the claim removes is OVC's usual derivation, from SETH. I know of no other standard hypothesis that implies OVC in the low-dimensional form Alman and Li use; the
  hypothesis about SAT with unbounded clause width, which the claim does not refute, gives only a weaker,
  higher-dimensional form. *Argued by hand.*
- **Alman and Li's depth-2 barrier.** Josh Alman and Baitian Li showed that OVC implies that the N × N WHT matrix has
  no depth-2 linear circuit of size N^(1+o(1)), with a companion bound for the disjointness matrix; their
  introduction states it under "OVC or SETH". If the claim holds, the SETH half is empty and the barrier stands on
  OVC alone. Their proof needs even less: only that counting orthogonal pairs in dimension O(log N) cannot be done
  in N^(1+o(1)) time. *Conditional on OVC, or on that counting statement.*
- **Other conjectures.** 3SUM, all-pairs shortest paths (APSP), SAT with unbounded clause width, the Li–Li
  conjecture, Paturi and Pudlák's outer-dimension conjecture, Valiant's shift conjectures and Ailon's conjectures
  on well-conditioned circuits: none is known to imply ETH, and the claim contradicts none of them that I know of.
  Each is "not refuted by any known implication", which is weaker than "unaffected". *Argued by hand; 3SUM and APSP
  recalled.*

### 4c. Loses its basis, may still be true

- Abboud, Bringmann, Hermelin and Shabtay's SETH-based limit on speeding up pseudo-polynomial Subset Sum, whose
  best algorithms use the FFT: a faster Subset Sum would still need a reduction to fixed-width SAT that keeps the
  variable count small. *Follows if the claim holds; exact statement recalled.*
- Pătraşcu and Williams's "ETH implies that k-SUM needs n^(Ω(k)) time": no faster k-SUM follows, and the 3SUM
  conjecture is separate. *Recalled.*
- The NSETH barrier of Carmosino, Gao, Impagliazzo, Mihajlin, Paturi and Schneider against deterministic
  fine-grained reductions from SAT to 3SUM and APSP becomes void; neither problem gets easier or harder.
  *Follows if the claim holds.*
- ETH- and SETH-based bounds elsewhere (edit distance, longest common subsequence, treewidth dynamic programs,
  clique by solution size) lose that basis; many survive on OVC or on SAT with unbounded clause width. *Follows if
  the claim holds; the preprint lists many of them.*

## 5. What follows, if the claim holds

- **A circuit lower bound, for one hard language.** Ryan Williams proved in 2013 that if ETH is false, then E^NP
  (problems solvable in exponential time with an NP oracle) does not have linear-size circuits; that theorem would
  fire. The preprint adds, using local reductions of Hamid Jahanjou, Eric Miles and Emanuele Viola, that some
  language in E^NP needs more than c·n·√(log n) gates for infinitely many n. That corollary needs the sharper
  sparse-case bound, which only the preprint's appendix proves and the Lean statement does not cover; with the main
  text's bound the same argument gives c·n·√(log n)/(log log n)², still more than linear. *Follows if the claim
  holds.* As far as I recall, no superlinear general-circuit lower bound was known for E^NP. *Recalled.*
- **For transforms it means little.** The hard language comes from a diagonal (hierarchy) argument, and there is no
  known way to aim it at multiplication, the DFT or the WHT, which have O(n log n) circuits anyway. It counts
  two-input Boolean gates, while the transforms' operation counts are for linear circuits, a different model. It
  gives no rigid matrix and no linear-circuit lower bound. Williams's superpolynomial theorem does not fire, because
  writing a circuit as a formula costs one variable per gate. *Argued by hand.*
- **No practical speed-up.** With every hidden constant set to 1, which is optimistic, the factor
  ln ln n / √(ln n) in the exponent is 0.73 at n = 10^4, 0.71 at n = 10^6 and 0.51 at n = 10^30. The sharper
  exponent beats the best known 3-SAT bound, 1.307^n, only beyond about n = 10^79, and the Lean exponent beats
  brute force, 2^n, only beyond about n = 10^2390. It is no engine for the hub's SAT searches. *Computed; re-checked
  by `verify.py`.*

## 6. What might open up (speculation; nobody claims any of this)

1. **The interpolation trick.** The preprint's core matrix construction interpolates (−1)^j on a short interval to
   get a polynomial in commuting permutation matrices. Alman and Williams used the same kind of interpolation to
   show that the WHT is not rigid; the preprint names their work, Alman–Guan–Padaki and Dvir–Liu as related methods
   and proves its own bounds directly. Its split is of the identity matrix (a low-rank part plus a part with
   restricted support), so it is not itself a rigidity bound for any transform. Alman and Rao's faster WHT count
   uses non-rigidity through a different device, an explicit low-rank-plus-sparse split of the 8-point sign table;
   my 5/6 count follows their method, and my 3/4 count starts from Coppersmith, Feig and Linzer's 4-point circuit.
   The question is whether the preprint's interpolation parameters improve the polynomial behind the known rigidity
   upper bounds for WHT or DFT Kronecker powers. Dugongue's #5813 already carries the method to the hub's Gaussian
   axis, with phases i^j, and gets a precision saving but no κ.
2. **Counting orthogonal vectors.** The preprint's sharper bound comes from a theorem that contracts certain Boolean
   tensor networks with s wires in time 2^(O(s/√(log s))), provided every vertex has degree at most about s^(9/10)
   and there are polynomially many vertices. Could it count orthogonal pairs quickly in dimension c·log N? The direct
   encoding has two vertices of degree c·log N, above the cap, and padding s up to meet the cap makes the time
   superpolynomial in N; splitting the vector tables across low-degree vertices would need a new idea. A fast count
   would refute OVC, but it would remove Alman and Li's barrier only if it ran in near-linear time in every
   dimension c·log N; their own counting algorithm runs in N^(1+0.33c) and leaves the barrier standing. Alman and Li
   note that two earlier Orthogonal Vectors algorithms (by Nederlof and Węgrzycki, and by Williams) can, with work,
   be read as depth-2 circuits for the disjointness matrix, so such an algorithm might come with circuits. Even then
   the gain would be a new route, not a new order: o(N log N) for these transforms is already known without any
   hypothesis, from OpenAI's units and my Lean savings.
3. **Rigid matrices from algorithms.** Josh Alman and Lijie Chen already turn a fast algorithm for counting
   orthogonal vectors over F₂, in dimension much larger than log N, into rigid matrices built with an NP oracle and
   into depth-2 linear-circuit lower bounds. So the route from faster algorithms to linear-circuit lower bounds
   exists; fixed-width SAT does not reach that dimension.

## 7. Limits of this map

- It has had no human review; one AI reviewer attacked every step, and its corrections are folded in.
- It checks no proof in the preprint.
- Several cited results are recalled rather than re-read; each is marked.
- The hub search covered an older local copy of the repository and GitHub's search, which can miss files.
- It covers the claim as released on 26 October 2026. A revision, or the working group's report, could change any
  line.

## Open next questions

The same questions, with their fields, are in `TASK.json`.

1. **Do the preprint's interpolation parameters improve the polynomial used by Alman–Williams or by
   Alman–Guan–Padaki (their Theorem 6.1), and with it their rigidity upper bounds for WHT or DFT Kronecker powers?**
   Why it matters: non-rigidity has given faster transform constants before (Alman and Rao), and rigidity upper
   bounds feed the best depth-2 circuits. First step: put the preprint's polynomial (degree R − 1, matching (−1)^j
   on R consecutive weights near the mean of a binomial weight) next to Alman–Williams's at the same degree, and
   compare the share of entries each gets wrong. Blocked by: nothing; the construction's bounds are proved directly
   in the preprint, though, like the rest of it, they are unreviewed.
2. **Can the preprint's tensor-contraction theorem count orthogonal vectors in dimension c·log N once the vector
   tables are split across low-degree vertices?** Why it matters: a fast count would refute OVC, and a near-linear
   one in every dimension c·log N would remove Alman and Li's depth-2 barrier. First step: write the direct network
   for counting orthogonal pairs, then test one splitting gadget, checking that the number of wires stays close to
   log N while every degree drops below the cap. Blocked by: the theorem's degree cap of about s^(9/10) and its
   bound on the number of vertices.
3. **Does the claim hold?** Why it matters: every line of this map is conditional on it. First step: re-read the map
   against the working group's report when it appears, and against any revision of the preprint. Blocked by: the
   examination led by Impagliazzo, Paturi and Williams.

## How to re-check

```sh
python3 -B research/eth-claim-fft-impact/verify.py
```

Standard library, well under a second. It recomputes the figures of section 5 from their formulas, checks that this
README prints them as computed, and rejects four false figures as controls. Everything else here is argued, read or
recalled, with the status words above; the sources are listed below.

## AI assistance and credit

- **The claim:** OpenAI. The preprint names no individual authors; its README says it was produced by an internal
  OpenAI model. **The examination:** the working group led by Russell Impagliazzo, Ramamohan Paturi and Ryan
  Williams.
- **The hypotheses:** ETH and SETH are due to Russell Impagliazzo and Ramamohan Paturi (with Francis Zane for the
  sparsification lemma); the link from SAT to Orthogonal Vectors is Ryan Williams's (both recalled).
- **Every other result** is credited by its authors where it is used above.
- **On the hub:** Dugongue, for the first transfer of the preprint's method; ShikeChen01 and philippeVV, for the
  coding-gap work that already covers the network-coding side.
- **AI assistance:** the map, the check and this text were written by AI agents (Anthropic Claude) under my
  direction, in five lanes: the news, the hub and the literature, my own files, an impact map, and a reviewer whose
  job was to break it. No independent human review is claimed. Apache-2.0.

## Files

| File | What it is |
|---|---|
| `README.md` | this map |
| `TASK.json` | task card, scope, outcome and the open questions in structured form |
| `SOURCES.json` | base commit, pinned hub files and the outside sources |
| `VERIFY.json` | the registered check |
| `verify.py` | re-computes the figures of section 5, with failure controls |

## Sources

Dates are 2026 unless stated.

- **The preprint and its status.** openai/math at commit 7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a (26 October),
  folder `preprints/The-Exponential-Time-Hypothesis-is-False-October-25-2026/`: `paper.pdf`;
  `build/main_full_version.tex` (dated 17 October, revised 25 October): Theorem 1.1 and the two exponents, lines
  75-94; the hypotheses it refutes and the NSETH barrier, 279-297; the corollaries, 315-324; what survives, 326-378;
  the related interpolation methods, 429-457; the construction, 1101-1205. `build/quantitative-reduction.tex`, the
  degree cap, lines 26-49; `build/quantitative-circuits.tex`, the E^NP corollary. The Lean statement
  `lean/ComparatorChallenges/SubexponentialSAT.lean` and its scope page `lean/docs/378.md`. The working group:
  `history.md`, 26 October entry. Paper:
  https://github.com/openai/math/blob/7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a/preprints/The-Exponential-Time-Hypothesis-is-False-October-25-2026/paper.pdf.
  OpenAI's announcement page and press coverage were used only to find these files; nothing here rests on them.
- **The hub.** CrocSwap/integer-mult-bounds at main de5ec2e7a6074068452f45b1a191b5c72832df4a (26 October). Selected
  record: `certificates/selected-result.json`, κ = 62009/20000000 = 3.10045e-3. The search for ETH, SETH and OVC:
  ripgrep over a local copy at ee4fd87 (22 October), where every hit for "SETH" or "orthogonal vectors" was the name
  Seth or orthogonal vectors in the linear-algebra sense, and GitHub search of issues, pull requests, code and
  discussions on 26 October, which found the preprint only in #5813 and #5815 and no mention of the Orthogonal
  Vectors Conjecture. Cited: #5813 and #5815 (Dugongue, open); #634 (ShikeChen01, closed); discussion #2838
  (philippeVV); my notes #4268 and #4628.
- **Read for this map.** Alman and Li, arXiv:2509.14489 (FOCS 2025): Theorem 1.5; Appendix D, Theorems D.1 and D.2;
  their statement of OVC; their #OV algorithm in Õ(n·1.26^d); their remark on earlier OV algorithms. Afshani,
  Freksen, Kamma and Larsen, arXiv:1902.10935. Williams, "Improving exhaustive search implies superpolynomial lower
  bounds", full version, Theorems 1.2 and 6.1. Alman and Chen, FOCS 2019 (abstract and introduction). Braverman and
  He, arXiv:2610.10108 (abstract, introduction, statements). Abstracts only: Zhang, B. Li and Z. Li,
  arXiv:2610.09367; Alman and Rao, arXiv:2211.06459 (STOC 2023); Alman, Guan and Padaki, arXiv:2211.05217 (SODA
  2023); Jahanjou, Miles and Viola, ECCC TR13-099; OpenAI's DFT preprint in the same openai/math repository. Cited
  through Alman and Li or the preprint: Alman and Williams (STOC 2017); Dvir and Liu (Theory of Computing 16(20),
  2020); Alon, Karchmer and Wigderson (SIAM J. Comput. 19(6), 1990); Williams (Theoretical Computer Science 348,
  2005); Nederlof and Węgrzycki.
- **Recalled, not re-read.** Abboud, Bringmann, Hermelin and Shabtay (SODA 2019); Pătraşcu and Williams (SODA 2010);
  Carmosino, Gao, Impagliazzo, Mihajlin, Paturi and Schneider (ITCS 2016); Curticapean's #ETH bound for perfect
  matchings; Morgenstern (1973); Paterson, Fischer and Meyer (1974); Valiant (1977); Impagliazzo and Paturi, and
  Impagliazzo, Paturi and Zane (2001); the derivation of low-dimensional OVC from SETH by sparsification; the best
  earlier explicit circuit lower bounds (about 3.1n, for functions in P); Harvey and van der Hoeven (2021).
- **My own work.** jacobalansussman/wht-power-saving-lean at f08d308ff93f4867165a1e80765fe985c06b4edf (the DFT
  saving 1.7887045e-3; the WHT saving 1.5699306e-3, `community/wht-c588mhh` in its table of results).
  jacobalansussman/wht-fewer-operations at bbb7f830d8c5612465a9922ace566750ce6d09d2 (the 5/6 and 3/4 counts; the
  credits to Alman and Rao and to Coppersmith, Feig and Linzer in its README).
