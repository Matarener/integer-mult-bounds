# The char-2 jet obstruction on jf0, jf1, jf2 holds at every order

**Scoped proof with an exact integer certificate. No new κ.** This package
answers Open item 3 of DreamingOfClouds' `research/char2-jets` (PR #2162):
*does the Lemma F flow obstruct at every order on jf0..2?* Yes. Each of the
four immovable harmonic lines (jf0 line 0, jf1 line 7, jf2 lines 0 and 2)
carries an integer multiplicative relation over eight incidences. In any
characteristic-2 deformation with unit coordinates, that relation forces the
diagonal of the line to vanish to at least the smallest order of those eight
incidences. No jet of any order, finite or formal, and around any collapse φ,
can separate them.

The T = 3 target (A) is not touched. Its known values for these instances
already satisfy it: cost(jf0) = 19 (Ross Richardson, PR #2176), cost(jf1) = 12
and cost(jf2) = 14 (PR #2162).

## Setting

Notation follows `research/char2-jets/README.md` §1–2. A configuration has
lines t with p(t), q(t) ∈ Q³, supports π(t), σ(t), and incidences (t, s) of the
full pattern, t ≠ s, p(t)·q(s) = 0 and π(t) ∩ σ(s) ≠ ∅. All three
configurations are no-wild. Every incidence is therefore binomial, over a pair
{i < j} = π(t) ∩ σ(s). A harmonic line h has D(h) = {i < j} with
p_i(h)q_i(h) = p_j(h)q_j(h).

Let K be a field of characteristic 2. A deformation assigns P~(t), Q~(s) ∈ K³
with **exact** supports π(t) and σ(s). For an incidence or harmonic diagonal
e = (t, s) over {i < j}, write

```text
a_e = P~_i(t) Q~_i(s),   b_e = P~_j(t) Q~_j(s),   N_e = P~(t)·Q~(s) = a_e + b_e,
u_e = N_e / b_e,         so a_e / b_e = 1 + u_e   (characteristic 2).
```

## Certificate

For each immovable line h, [CERTIFICATE.json](CERTIFICATE.json) lists eight
incidences e with coefficients c_e ∈ {+1, −1} such that the exponent vectors
satisfy

```text
v_h + Σ_e c_e v_e = 0,    v_e = [P~_i(t)] − [P~_j(t)] + [Q~_i(s)] − [Q~_j(s)].
```

So `a_h/b_h · Π_e (a_e/b_e)^{c_e} = 1` holds as an identity of Laurent
monomials, hence in every field at every nonzero assignment. This is an
integer lift of the F2 flow of Lemma F: reducing it mod 2 gives a flow
certificate in Lemma F's sense. The lift is not automatic. A mod-2 relation
only makes the monomial a square, and in characteristic 2 the square
(1 + δ)² = 1 + δ² would allow the diagonal to reappear at a higher order.

## Theorem

Fix one certificate (h, Z, c). For every exact-support characteristic-2
deformation:

1. **Identity.** `1 + u_h = Π_{e∈Z} (1 + u_e)^{−c_e}`.
2. **Exact realisations.** If N_e = 0 for all eight e ∈ Z, then N_h = 0.
3. **Valuations.** For a valuation ν on K, if m = min_{e∈Z} ν(u_e) > 0, then
   ν(u_h) ≥ m.
4. **Unit jets, every order.** If every support coordinate is a unit
   (ν = 0), then ν(N_h) ≥ min_{e∈Z} ν(N_e) whenever the right side is
   positive. Hence no deformation has every incidence of Z vanishing to order
   greater than k while the diagonal of h has order exactly k. This holds for
   every k ≥ 1.

*Proof.* (1) Substitute a_e/b_e = 1 + u_e into the monomial identity and solve
for the h factor. (2) Put u_e = 0. (3) Each factor (1 + u_e)^{±1} equals
1 + y_e with ν(y_e) ≥ ν(u_e) ≥ m. For the inverse, use
(1 + u)^{−1} = 1 + u/(1 + u) and ν(1 + u) = 0. A product of elements 1 + O(m)
is 1 + O(m). (4) Unit coordinates give ν(b_e) = 0, so ν(u_e) = ν(N_e). ∎

**Corollary (answer to Open item 3).** Corollary J's ansatz, and its order-k
continuations, take P~ = φP + εX₁ + ε²X₂ + … and Q~ likewise over K((ε)),
with any homomorphism φ: Q* → K* such that φ(−1) = 1. Every support coordinate
is then a unit, because φP and φQ vanish nowhere on the supports. An order-k
certificate needs every incidence at order ≥ k + 1 and the immovable diagonal
at order k. Part 4 forbids this for every k, and for every finite or formal
series. The package's order-1 and order-2 failures are the cases k = 1 and
k = 2, now with a common cause.

The same argument applies to the B-dependent jet test on E = supp B whenever
supp B contains the eight edges of one certificate.

**Relation to prior work.** Sagar Thakrar's `research/pool121-jet-rigidity`
(PR #2351, Proposition R) proves the same uniform all-order conclusion for
*rigid* unit-world configurations, such as the 121-line pool, by gauge and
torus renormalisation. jf0..2 are not in that class, and Proposition R is not
used here. The mechanism here is different: a local integer relation on eight
incidences, with no rigidity hypothesis. The bound is per line, so the
diagonal of h is controlled by its own certificate edges and not only by the
minimum over all incidences. PR #2351 also checked the order-2 failure on
jf0..2. It left orders ≥ 3 open on its 25 non-rigid atoms.

## Evidence

[verify.py](verify.py), standard library only, about 0.2 s:

- recomputes incidences, harmonic lines and first-order immovability (F2
  membership, Lemma F) from the pinned configurations. It requires the
  immovable lines to be exactly jf0 {0}, jf1 {7}, jf2 {0, 2}, matching
  `research/char2-jets` §5. The movable harmonic lines are jf0 {1, 6},
  jf1 {0, 5, 6} and jf2 {4, 8};
- finds each lift by column elimination over Z₍₂₎. It requires a ±1
  solution and compares it with `CERTIFICATE.json`;
- checks the exponent identity exactly, edge by edge, against the recomputed
  incidence list and pairs;
- controls: the monomial identity at 200 random nonzero rational points per
  line. It also checks that each certificate edge has ratio −1 on the actual Q
  configuration, while h has ratio +1, so the incidence count is even (Lemma F's
  parity). For 200 random unit jets over F2[[ε]]/(ε²⁴), it checks
  ν(N_h) ≥ min ν(N_e), with equality in 96–112 trials per line, so the bound
  is attained. Flipping one sign or deleting one edge breaks the identity in
  all 16 mutations per line.

It prints `PASS_CHAR2_JET_EVERY_ORDER_OBSTRUCTION lines=4`.

## Reproduce

From the repository root, with CPython 3.12:

```sh
python3 -B scripts/research_package.py --package research/char2-jet-every-order-obstruction --check-only
python3 -B scripts/research_package.py --package research/char2-jet-every-order-obstruction
python3 -B research/char2-jet-every-order-obstruction/verify.py
```

`verify.py --write` regenerates `CERTIFICATE.json` from the pinned inputs.

## Limitations

- The theorem is proved here by hand. The script checks the certificate
  identity exactly. The rest of the argument is two lines of valuation
  algebra, with no proof-kernel check.
- Exact supports are assumed. A deformation that sets a support coordinate to
  zero leaves the scope of the identity. CR2 in `research/char2-jets` allows
  such shrinking, so part 2 strengthens its GF(2), GF(4), GF(8) non-CR2 checks
  only for exact-support realisations, over every field of characteristic 2.
- General VCR2 certificates are not excluded. A realisation whose incidence
  valuations on Z are not all above the diagonal's, or whose coordinates are
  not units, can still meet the directed-cycle condition. The "2-adic shadow"
  conjecture (§6.2 of the predecessor) remains open.
- No statement is made about (A), about other configurations, or about κ.

## Open next questions

1. Does a non-uniform VCR2 certificate exist for jf0..2? Part 3 forces
   ν(u_h) ≥ min over Z, so the low-valuation incidence must lie on Z. That
   matters because it is the remaining B-independent route to cost ≥ v through
   valuations. First step: an LP over valuation vectors w for directed cycles
   of the full pattern, with w_h bounded by part 3. Blocker: the cycle
   condition ranges over all directed cycles. The unit-coordinate restriction
   would have to be dropped as well.
2. Which minimisers of jf1 (192) and jf2 (12 928) contain a full certificate
   Z in supp B? For those B the B-dependent jet test fails at every order, so
   the count may account for the six jf1 minimisers that pass neither test of
   the predecessor. First step: intersect the stored minimiser supports of
   `research/char2-jets` with the four edge sets here. Blocker: the minimiser
   list is regenerated by a C enumerator, not stored.
3. Is every first-order immovable line of a no-wild configuration liftable
   with an odd harmonic coefficient? Here all four lifts are ±1. A
   configuration whose F2 flow has no Z₍₂₎ lift would be a candidate for a
   higher-order jet. First step: run `local_solve` on the 25 non-rigid
   immovable atoms of PR #2351, where orders ≥ 3 remain untested. Blocker:
   none known.

Structured versions are in [TASK.json](TASK.json).

## Credit

Produced by Nick Petalas. The configurations jf0, jf1, jf2, Lemma F,
Corollary J, the order-2 failure and Open item 3 are from DreamingOfClouds'
`research/char2-jets` (PR #2162). The model is #2111's T = 3 pairing-cost
problem, with the lineage recorded there. The exact cost of jf0 is Ross
Richardson's PR #2176. Proposition R for rigid configurations is Sagar
Thakrar's PR #2351. Those results are cited and not re-audited.
Apache-2.0.
