# Theorem 1G: a recursion with jobs of several sizes

Status of each part, in words:
- the theorem below is **argued by hand** in a simple model of jobs (this file), and its numerical checks were run by
  computer on small rules;
- the recursion that the DFT proof actually uses, with the two job sizes of this package, is **proved in Lean** inside
  OpenAI's machine model, in the repository named in README section 5;
- whether the community's outer step for integer multiplication accepts such a recursion is **open**.

## 1. The model of jobs

A job of size s is a transform on s address bits of a register; its cost is counted in passes per entry. A *rule*
(a word, read as a recursion) has targets W_k for k in K: in one round a unit at column c consumes W_k jobs of size
k c for each k (W = sum W_k arrays, m = max K the full job, k_min = min K the smallest job). It pays P rounds j, in
word order, of ranks r_j >= 1 (n_r rounds of rank r, r_max = max r_j), each round being one job of size r_j c, plus F
free passes. A job a + b may be split into a and b, and a plain job of size s costs s.

The balance τ in (0, 1) is the root of

    sum_j r_j^τ = sum_k W_k k^τ.

With the single target {73: W} this is the community's moment equation, and b = 1 - τ is its complex root. For the
lever on #2979: K = {73, 49}, W_73 = 50,218, W_49 = 16,086, and the paid ranks are those of README section 2.

**Separation hypothesis (S):** r_max < k_min, that is, every paid block is smaller than every job. On #2979 with the
half cut, r_max = 48 < 49 = k_min. With the full cut (job 25) the other rank-48 blocks would break (S) unless they are
split, which is why the half cut is the one used.

## 2. The theorem

**Theorem 1G.** Under (S), T(n) <= C n^τ (ln n)^κ for all n >= 3, with κ = ceil(ln(2/η) / ln(1/θ)),
θ = ln r_max / ln k_min < 1, η a constant of the rule, and C depending only on the rule. So T(n) = O(n^(τ+δ)) for every
δ > 0: every saving below 1 - τ is reached with a fixed constant.

The proof builds a **dilated lockstep tree** of classes of units:

- **Lemma B (exact balance).** Index classes by sequences of rounds. Round j of a class feeds exactly one child
  class, and at every point the child's demand equals the parent's supply, both jobs of the same integer size (a
  product of ranks; no rounding of sizes). This uses (S).
- **Lemma C (sources only at the top).** Every job that is not produced inside the tree is a source of size in
  (L/m, L], cut from the top job.
- **Lemma D (exits).** Jobs leave the tree only at the last generation, with sizes at most r_max (L/m)^θ, so ln e <=
  θ ln L; they are done by fresh top calls, which costs the (ln n)^κ factor.
- **Lemma E (number of units).** The number of units is at most a constant times the sources' weight, with no log
  factor.
- **Lemma F (order).** Processing class by class, round by round, is a straight-line program with no deadlock: a
  round j + 1 is issued only after every unit that consumed a round-j job has finished.

The induction then closes with the top split (Lemma A: the exact condition for closing the induction with leftovers).
The numerical checks on three small separated rules and a rank-1 control found every class exactly fed, all sources
in (L/m, L], the exits' weight equal to the sources', and the largest exit within the bound of Lemma D, at L up to
10^7 (up to 1.6e10 classes counted with multiplicity).

Exact O(n^τ) with no log factor is **not** proved for grouped paid blocks; rules that break (S) are **open**.

## 3. What the mixed recursion needs that the community's uniform recursion does not have

The community's recursion is one call per job: a call of size s slices its own batch into W arrays of rank m at
column s/m, and each paid block is an independent recursive call; no call ever needs a job of another size. Theorem
1G needs:

1. **Several sizes at once.** A unit at column c takes rank-73 arrays of size 73c and rank-49 arrays of size 49c in a
   fixed ratio (50,218 : 16,086 for #2979). They come from different producers' outputs, never from one call's batch.
2. **Fractional portions.** Classes are fractional portions of batches: a portion step in the cost model, and dyadic
   rounding with enough batch bits (the number of classes is polynomial in n).
3. **A class tree in lockstep.** Round j of every unit in a class is issued together, and the child class consumes
   exactly those outputs plus top sources; a careless order deadlocks.
4. **A top split.** The top job is cut into portions of sizes in (n/m, n] plus rests, done recursively.
5. **Exit calls.** Jobs of size at most r_max (n/m)^θ are completed by fresh top calls. So the Lean statement uses a
   rational exponent strictly inside the root, with an existential constant: the figure N/10^10 sits below the root
   (README section 2), and the Lean rate fact is stated two hundredths of a grid step further inside.
6. **Words for the smaller job.** The word with each head cut must be correct for the job of 49 axes on the head's
   array and the full job everywhere else. In Lean this is the head lemma: removing half of a head leaves a program
   that does exactly the smaller job on that array.
7. **Hypothesis (S).** #2979 with the half cut meets it: 48 < 49.
8. **The heads.** Each cut block must be a literal head: the first non-identity operation on its own array, acting on
   that array alone, with nothing hosted there before. `verify.py` counts them in my lowering and my network; the Lean
   proof checks the same property for the blocks it cuts.
