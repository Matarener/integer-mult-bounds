# A fused two-root readout reaches 72 calls at exactly 30 fused reads

**Scoped proof with an exact finite census; no new κ.** This package adds one
operation family to Ross Richardson's five-source dirty connector
([PR943](../universal-connector-boundary/README.md)): a fused readout of the
sum of two borrowed dirty roots. With it, the batch of all 31 nonzero output
masks attains the 72 A/B map-call support bound, which the one-connector
alphabet cannot reach. The price is sharp: **every 72-call schedule uses at
least 30 fused reads, and 30 are attained**, including by Richardson's own
ten-call word `B0 B1 B2 B0 B3 B1 B4 B2 B3 B4`.

The card asks whether one charged alphabet extension gives a favorable
complete budget. The answer for this family is conditional. It beats the
74-call one-connector optimum only if `30φ + ρ + ΔH < 2c`, where φ is the
surcharge of a fused read over a plain read. It beats the credited
eight-transfer endpoint only if `30φ < 8σ + ΔH'`, with σ the transfer price.
No physical price is measured here.

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -B research/two-root-sum-readout-connector/verify.py
```

Expected (about 0.2 s, standard library only):

```text
PASS_TWO_ROOT_SUM_READOUT words=945 single_root_max=31 min_fused_reads=30 attaining=310 attaining_words=135 infeasible=28000 histogram={'30': 310, '42': 40} map_calls=72 fused=30 root1=[1] dense_cases=600 mutations_rejected=5
```

Add `--json` to print the literal 72-call schedule.

## Interface

Keep the exact interface of the
[universal connector boundary](../universal-connector-boundary/README.md):
five read-only sources x_j, 31 arbitrarily dirty outputs y_m (one per nonzero
five-bit mask m), fixed arbitrary F2-linear maps, complete calls, a
data-independent straight-line word, and no observation of targets before the
batch ends. The requested update is `y_m += A_m sum_(j in m) B_j x_j`.

Change one premise. There are two borrowed, arbitrarily dirty roots z1 and z2
of the same shape. Both must be restored. The calls are:

```text
B_j -> r : z_r += B_j x_j          r in {1,2}, chosen per call
A_m <- r : y_m += A_m z_r          plain readout of one root
A_m <- s : y_m += A_m (z1 + z2)    fused readout (the added family)
```

A fused readout applies A_m once, to the sum of the roots, and leaves both
roots unchanged. It is a complete call with its own price. There are no
root-to-root transfers, frames, copies, DUO/TRIO calls or source mutations.
Without the fused family this is the two-root, free-port-choice model of
[PR1438](https://github.com/CrocSwap/integer-mult-bounds/pull/1438) and
[PR1615](https://github.com/CrocSwap/integer-mult-bounds/pull/1615) with zero
transfers.

## Theorem

Every schedule in this alphabet uses at least 72 A/B map calls. Every
schedule with exactly 72 uses at least 30 fused readouts, and a 72-call
schedule with exactly 30 fused readouts exists.

**Specialization.** Take L=1, all maps equal to the identity, and independent
bits for the sources, both roots and all outputs. A schedule correct for
arbitrary maps and inputs is correct here. Root r ends as
`z_r + sum_j (number of B_j -> r calls) x_j`, so each source is sent an even
number of times to each root. Output m receives z1 from its plain root-1 and
fused reads and z2 from its plain root-2 and fused reads. If it has a1, a2 and
a3 reads of the three kinds, cancelling both roots' dirt needs a1+a3 and a2+a3
even.

**Floor.** Every source appears in some mask, so each B_j is called at least
twice. Every output needs at least one read, and one read leaves dirt, so each
A_m is called at least twice. That gives 10 + 62 = 72.

**Structure at 72.** Each B_j is called exactly twice, and evenness per root
puts both calls on one root. This partitions the sources into S1 and S2. Each
A_m is read exactly twice, and the parity conditions force both reads to be of
one kind. Let q_t be the source-parity prefix of the ten-call word. A plain
pair on root r at boundaries s,t yields the projection of `q_s XOR q_t` to
S_r; a fused pair yields `q_s XOR q_t` itself.

**Lower bound.** If S2 is empty, plain root-2 pairs yield 0 and plain root-1
and fused pairs both yield the one-connector difference set D(w). The 945
canonical ten-call words cover at most 31 of 32 masks (Richardson's census,
rerun here as a positive control), so this fails. The case with S1 empty is
symmetric. Otherwise let a=|S1|, with 1 ≤ a ≤ 4. A plain pair yields a mask
inside S1 or inside S2. The `(2^a - 1)(2^(5-a) - 1)` masks that meet both
parts must each be read by a fused pair. That count is 15 for a ∈ {1,4} and 21
for a ∈ {2,3}. So at least 30 fused readouts are needed.

**Attainment.** Take Richardson's word `B0 B1 B2 B0 B3 B1 B4 B2 B3 B4`, send
both B1 calls to root 1, and send the other eight calls to root 2. The root-2
subword `B0 B2 B0 B3 B4 B2 B3 B4` covers all sixteen masks on {0,2,3,4}, and
root 1 covers mask 2 (source 1 alone). The fifteen masks containing source 1
and some other source are full-word prefix differences of the ten-call word,
so they are read by fused pairs. Mask 21, the single mask the predecessor's
one-connector word misses, lies inside root 2 and is read by a plain pair.
The schedule has 10 B calls, 32 plain readouts and 30 fused readouts.

## Census

The verifier evaluates every canonical ten-call word against every ordered
assignment of sources to roots: 945 × 30 cases. For each it computes the
fewest fused readouts, or infeasibility. Results:

| Fused readouts at 72 calls | Ordered (word, root assignment) cases | Split |
|---:|---:|---|
| 30 | 310 | 1 \| 4 |
| 42 | 40 | 2 \| 3 |
| infeasible | 28,000 | any |

Swapping root labels pairs these cases, so there are 155 and 20 unordered
cases. 135 of the 945 words attain 30. Every feasible case meets its crossing
count exactly. The census corroborates the proof; the lower bound itself is
the counting argument above.

## Replay and controls

- **Arbitrary maps.** A symbolic replay tracks each row as a formal XOR sum of
  terms (`z1`, `z2`, `B_j`, `A_m(term)`). Both roots return to their initial
  terms, and every output gains exactly `A_m(B_j)` for j in m. This checks
  the identity for arbitrary linear maps. It uses no commutation or
  invertibility.
- **Dense dirty inputs.** 600 random dense F2 instances with L = 1, 2, 3 and
  dirty sources, roots and outputs.
- **Mutations.** All five are rejected: one source call moved to the other
  root, one fused read replaced by a plain read (mixed ports), one read
  dropped, one fused pair replaced by a plain pair, and one readout moved past
  a source call.

## Complete bill and comparison

Use the predecessor's notation: c_Bj and c_Am are complete call prices, I is
input admission, P_F is coefficient preparation and D is root dispatch.
Write c_Am + φ for a fused readout, ρ for reserving the second dirty root and
σ for a complete one-way root transfer. Let C_72 be
`I + sum P_F + 2 sum c_Bj + 2 sum c_Am`. Then:

| Schedule | Bill |
|---|---|
| One connector, repair (PR943) | C_72 + 2 c_B2 (or 2 c_A20) + D |
| Two roots, eight transfers (PR1615) | C_72 + ρ + 8σ + D' |
| Two roots, 30 fused readouts (here) | C_72 + ρ + 30φ + D'' |

The fused schedule beats the one-connector repair iff
`30φ + ρ + D'' - D < 2 min(c_B2, c_A20)`. It beats the eight-transfer schedule
iff `30φ + D'' < 8σ + D'`. PR2182 reports a six-transfer endpoint with
occurrence-varying ports (PR2065), which would tighten this to
`30φ < 6σ` plus dispatch terms. That endpoint is cited, not checked here.

Pricing a fused readout as a transfer, a plain read and a second transfer
gives φ ≤ 2σ, which is far above σ/5: the transfer schedules already batch
that work. The fused family helps only with a native fused read whose
surcharge is below about a fifth of a transfer. With a cell-access price in
which a dense A_m must read every cell of z2, a fused read adds at least L
cell reads per call. Thirty of them then add at least 30L reads, while eight
transfers read 16L cells. So under that price the fused family loses to the
transfer endpoint. This comparison is a price model, not a theorem about all
implementations.

## Limitations

- Abstract complete-call model only. No supplier, caller, compiler, tape,
  precision or hosting obligation is discharged. No new κ and no
  selected-frontier change.
- The lower bound is a written proof. The one-connector exclusion it uses is
  Richardson's finite census, rerun here only as a positive control. No proof
  assistant or independent human review is claimed.
- Only the 72-call layer is settled. The fused-read minimum at 73 and more
  calls is not computed. With fused reads an output can be read three times
  (one of each kind), so odd totals are not excluded by parity.
- φ, ρ and σ are not measured.

## Open next questions

Structured versions are in [TASK.json](TASK.json).

1. **What is the fused-read minimum at 73 calls?** One output read once from
   each of z1, z2 and the sum receives `q1_s + q2_t + q_u`, a three-term mask,
   so 73 is legal. The crossing argument then gives at least 29. First step:
   extend the census to one triple-read output and add 4-read outputs at 74.
2. **Does any caller supply a native fused read with φ < σ/5?** Only then can
   this family beat the transfer endpoints. First step: name one caller whose
   A_m leaf can consume z1 + z2 in one pass, and price that pass against a
   transfer at the same ports.
3. **Mixed alphabets.** Can a schedule with a few transfers and a few fused
   reads beat both endpoints at intermediate φ/σ? First step: add transfer
   calls to this census's state model and minimize `t σ + f φ` over a grid of
   ratios.

## Credit

This contribution was produced by Nick Petalas. Apache-2.0.

Ross Richardson's PR943 supplies the interface, the prefix-difference
criterion, the 945-pairing census and the ten-call word used here. The
two-root, free-port-choice transfer model and its thresholds are woklerx's
PR1438, Gareth Davidson's PR1498 and Hanson Sun's PR1615 (with Cinna Davis's
eight-transfer word). PR2182 (conorholds) and PR2065 are cited for the
fixed-port and six-transfer endpoints. Their results are premises or
comparators here, not re-verified.
