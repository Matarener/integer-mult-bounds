# Literal completion/splitting pass and nested owned-bank lifetimes in the lockstep compiler

**Scoped positive result; no new κ.** Target 10 of zxv's #5428 asks for a uniform
fixed-tape compiler theorem and suggests starting with "one chronological
completion/splitting pass" and "owner allocation/erasure". This package supplies two
narrow pieces of that foundation, both executed event by event rather than only
counted:

1. **The pass is a rule.** Completion of every small target to the floor `L` on its
   own owner, followed by splitting of every paid job at the cutoff `J`
   (`p7-TENSOR.md` §§2–3, `higher-moment-strictification` §1), is a transformation
   `U -> U'` of finite native units. `U'` satisfies the lockstep hierarchy, every
   compiled program of `U'` passes the ownership invariants I1–I6 of our #4691
   executor, every added job is a whole job on a field its unit owns, the rank-one
   surplus is preserved exactly, the net-tax identity (1) holds, and the added
   records (pieces, completions, normalizer pairs, relocations) have a closed
   per-unit count that the executor reproduces. [PROOF.md](PROOF.md), Lemma A.
2. **Owned-bank lifetimes are nested.** `FINITE-PRECOMPILATION.md` §6 allocates one
   owned bank per compiled unit instance and says a smaller reuse allocation
   "requires its own lifetime proof". In the lockstep schedule the live units are
   exactly the classes on the current path plus the nested programs, so a LIFO stack
   of bank slots suffices; its peak is an explicit recursion. The executor runs the
   stack allocator with invariant I7 (a finishing class's banks are the top of the
   stack) and its measured peak equals the recursion on every case. Lemma B.

## Evidence (`verify.py`, standard library, CPython 3.12)

- **Counting parity.** The histogram-level counter (`counts.py`, no unit
  enumeration) equals #4691's unit-level counting compiler on the toy rule at
  N = 4..64 and the BIT-shaped rule at N = 50, 400, 3200, and reproduces the
  FINITE-DAG-AUDIT receipt at toy rank 40.
- **Complete profiles, histogram level.** For the p7 invoice (`c=10, b=15`,
  C = 0.00268648) and the selected #5413 invoice (`c=20, b=21`, C = κ) at tensor
  powers v = 1, 2, 3: identity (1) holds to 40 digits, the rank-one surplus is
  unchanged (608 for p7, 752 for the selected profile, raised to the power v), the
  added target and paid masses agree, and `max paid <= J < L <= min target`
  afterwards. At v = 1 the selected unit has 77,204 rounds after the pass:
  64,260 original, 5,152 pieces and 7,792 completions on the 7,792 fields of rank
  4, 7, 8, 9 and 17; 15,584 normalizer records and 12,944 relocations.
- **Event-level execution with the stack allocator.** Toy rule (N = 7..28, full
  width), an overlapping toy rule after the pass (`J=4, L=5`, N = 40 and 64, full
  width: 12,048 and 112,738 bank allocations with peaks 732 and 8,751), two
  p7-shaped rules (`J=10, L=15`, N = 1815) and three selected-shaped rules with the
  caller's chronology shape and random, all-on-centre and one-owner chronologies
  (`J=20, L=21`, N = 3045), and a two-generation rule with path-dependent class
  sizes and exit ranks (N = 45 and 69, full width, peaks 2048 and 16,386). Peak, total, unit instances, pieces, completions,
  normalizer and relocation records all equal the formulas.
- **Complete profiles, compiled counts.** p7 at N = 1815 and the selected profile
  at N = 3045 (one generation each): width, leaves, units per copy, peak units per
  copy and the total/peak bank ratio (346 for the selected profile), with a hash of
  the exact integers.
- **Controls** (`test_verify.py`): the overlapping rule is not a lockstep rule
  before the pass; a cutoff not below the floor, a dropped split remainder and a
  short completion are rejected or break the mass law; a foreign completion owner
  is refused; the release-early allocator, the per-depth allocation, an eager
  parent and a repeated exit field are rejected; the peak recursion without its
  nested term undercounts, and the one that adds the largest path to the largest
  exit peak from a different path overcounts (2050 against the executed 2048); a wrong tax breaks identity (1); a tampered
  RESULT.json is rejected.

```sh
python3.12 -B scripts/research_package.py --package research/lockstep-completion-pass
```

## Scope and limits

- The pass and the compiler are executed on reduced-multiplicity rules with the
  real rank sets and on the complete profiles at histogram level. The literal
  chronology of the 64,260 paid calls of #5413 (which call acts on which field)
  is not bound here; the shaped rules use the caller's event structure (LOCAL
  blocks of small-rank jobs on helper fields and the owned centre, IDLE jobs of
  rank 16..72 on main fields, rank-one queries on the owned bank) with random and
  adversarial owners.
- Record counts are exact; their tape prices are the retained primitive prices
  (a child call on a contiguous axis block, a block address permutation, a whole-job
  normalizer record), not re-derived. No numerical movement bill is claimed.
- The native content of completion jobs and normalizers, the all-column lift, the
  strict moment inequality, precision, analytic recovery and the selected κ are
  inherited and unchanged. The v = 1024 selected template is not materialized;
  the recursions of Lemma B are stated for it but evaluated only at v = 1.

## Relation to the physical half of `native_all_columns`

PR #5442 (`research/allwidth-caller-certificate`) closes the algebraic half of
`native_all_columns`: the caller's identities hold at every column width `f`. Its
physical half stays open: executing `g^(tensor f)` and the port adapters on a fixed
number of tapes, for all `f` columns at once with one fixed primitive list, without
disturbing spectator fields, at the retained tariff. Lemmas A and B do **not** supply
that. They are statements at the level of the rule and the compiled flow: they fix
*which* records the pass and the compiler add (child calls on contiguous axis
blocks, block relocations, normalizer pairs, bank initialisation and erasure), how
many of them one unit instance and one compiled program contain, and on which
owned fields they act. The `f`-dependent tape price of each such record type is
exactly the open physical obligation named in #5442; this package gives it an
exact record count to multiply, not the price. The element inventory of the selected
caller that such a price would have to cover is listed by PR #5442 (port wrappers,
`D`, `C0`, `X0`, the helper alias monomials and the 145-axis `J` routes); the tariff
domain `f <= p` is recorded in `research/final4610-independent-admission/SPECIALIZATION.md` §3.

## Open next questions

1. Bind the actual owners of the selected caller's paid calls (`invoice.json`
   chronology plus the #5402 provider schedule) and execute the literal 77,204-round
   rule at two lockstep copies. First step: extract per-event owner fields from
   `NEUTRAL-BACKWARD-v16c.json`.
2. Price the added records with the retained native tariff to obtain a numeric
   movement bill per unit instance. First step: the 171-record monomial bound of
   the #4610 review for the normalizer pairs.
3. Evaluate `peak(N)` and `total(N)` for larger N (two generations) with
   memoisation over dilations; the present recursion over all sub-ranks is slow
   beyond one generation for the selected profile.

## Credit

Jacob Alan Sussman (Theorem 1G lockstep flow), Cinna Davis (PR4412/4414/4416
product and completion), zxv (`higher-moment-strictification`, `net-tax-rank-compiler`,
#5428), Nick Petalas (#4832 sharp split charge), Chris R / Clear1nsight (#5413),
Dillon (#5402), Ali Romman (#5383/#5398), Cao Yifan (#4610), and our own #4691
executor. Prepared by Mark (Matarener) with substantial Claude Code assistance.
Apache-2.0. No independent human review or formal-kernel verification is claimed.
