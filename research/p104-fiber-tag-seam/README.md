# P104 fiber-tag seam on one row/column pair

**Finite obstruction; no new supplier and no κ.** On the 104 published P104
labels, the phase-uniform row tag `z ⊗ q_j` and column tag `r_i ⊗ z` are never
the same 81-bit translation. A mixed weight-class pair also disagrees on the
one-dimensional shared line. The published witness `(386, 405)` is such a pair.
Selected conditional κ stays `0.001672660197076918`.

## Scope and evidence

Original card: `p104-side-correction`, scope **refined**. The card allows one
chronological cut or one hosting obstruction. Discussion #1166 comment 19034676
asks for one actual row/column pair and a reconciliation of the fiber-dependent
tags `z ⊗ q_j` and `r_i ⊗ z` on shared owners. This package does that comparison
for every ordered pair of the retained labels, and pins the witness already
named by PR #3954. It does not build a caller, clear the inherited excess
44,096, or admit a physical owner.

The labels are `physical_labels` from the `RESULT.json` exported by PR #3966
at `3e2d70630fde46847c8938564576d78da48d101d`, origin PR #3954 head
`f1e2839819959cd0534d008be91ed5b79ec55a6a`. That file's SHA-256 is
`ce05a27ebc98677bec4febaa488fa03f5b6fc60216aa43b34298444d12f7ab6c`. It is not a
Git object on this base. `labels.json` is the vendored array; `verify.py`
checks its SHA-256
`7227a7d6bdb49f36b6e401478034cc542eb887979890c8deda924b8ac0844209`.

### Conventions

`z = 420`, support `{2, 5, 7, 8}`. `O x = x + (x · z) z`. Bit `9α+β` of
`u ⊗ v` is `u_α v_β`. The row image is `q_j = O p_j` and the column image is
`r_i = O p_i`. The row tag is `z ⊗ q_j`. The column tag is `r_i ⊗ z`. The
shared line is `span(r_i ⊗ q_j)`, read by the dot product with that vector.
The uniform completion tag is `a = z ⊗ 511 + 511 ⊗ z`.

### Proof

`z · z = 0` and `wt(z) = 4`, so `O` is an orthogonal involution and `Oz = z`.
Hence `z · (O p) = z · p`. The checker tests the involution, the orthogonality
identity, and `q(Ox) = q(x) + 2(x · z) (mod 4)` on all of `F_2^9`.

Every retained label is odd, 56 of weight class 1 and 48 of class 3. Every
image has weight class 3, so every image is odd, and none equals `z`. The
weight law then forces `z · p = 1` exactly on class 1.

**Full address.** Summing a matrix over its second index in `F_2`:

- the row tag contributes `z_α (q · 1) = z_α`, because `q` is odd;
- the column tag contributes `r_α (z · 1) = 0`, because `z` is even.

`z ≠ 0`, so the tags differ for every odd `q` and every `r`. All 10,816
ordered pairs therefore have distinct full-address translations. The oddness
hypothesis is necessary: both tags are zero when `q = r = 0`.

**Shared line.** Both images are odd, so `b = r ⊗ q` satisfies `b · b = 1`.
The two tags flip that line by `z · r = z · p_i` and `z · q = z · p_j`. The
flips agree if and only if the labels have the same weight class. That is
5,440 ordered pairs. The other 5,376 disagree.

**Uniform helper.** Write `a = z ⊗ 511 + 511 ⊗ z`. Its column sum, summing
the first factor, is `z`. The column sum of a row tag `z ⊗ q` is `0` because
`z` is even, so `a` is never a row tag. Its row sum, summing the second
factor, is also `z`. The row sum of a column tag `r ⊗ z` is `0`, so `a` is
never a column tag either. On the shared line, `a` matches the row tag exactly
when the column label is class 3.

**Distance.** The minimum Hamming distance between a row tag and a column tag
is 6, attained only by the ordered pairs of labels `32` and `4` (list indices
19 and 75, both class 1, images 388 and 416). Even the two diagonal pairs
differ. No shared-line agreement is a full-address agreement.

### Pinned witness

PR #3954's witness names `p_row = 386` and `p_donor = 405`. In
`physical_labels` those are indices 0 and 8. The field `donor_port = 2` is not
an index into that list.

| | row 386 | column 405 |
|---|---:|---:|
| weight class mod 4 | 3 | 1 |
| image under `O` | 386 | 49 |
| shared-line flip | 0 | 1 |
| Hamming distance of the tags | 20 | |
| separating coordinate | bit 11, which is `(α, β) = (1, 2)` | |

`χ` at that bit takes values `+1` and `-1` on the two translations, so they
differ as operators on arbitrary functions. The uniform tag flips the same
shared line and the row tag does not, so a helper carrying `a` does not match
this row owner.

## What this does not establish

Nothing here clears the scaffold excess 44,096 from PR #3966, which already
grants every gauge and tag for free. Same-class pairs still need a correction
on at least six address bits before the full translations agree. Native
routing, owners, dirty return, precision, and a changed favorable bill are
open. This is not a multiplication theorem.

## Reproduce

From the repository root, CPython 3.12, standard library only:

```sh
python3.12 -B scripts/research_package.py --package research/p104-fiber-tag-seam --check-only
python3.12 -B scripts/research_package.py --package research/p104-fiber-tag-seam
python3.12 -B research/p104-fiber-tag-seam/verify.py
```

Expected marker:

```text
PASS_P104_FIBER_TAG_SEAM pairs=10816 full_equal=0 mixed_shared_disagree=5376 same_shared_agree=5440 min_hamming=6 witness=386/405 shared_flips=0/1 ham=20 helper_disagrees_on_witness=true no_new_kappa
```

The same command under `-O` is registered. A forced claim that the witness tags
are equal is rejected. The zero-vector pair shows that an even image can agree.

`python3 -B scripts/research_baseline.py` returned
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY`. That check binds the selected record.
It is not this certificate.

Not run: the PR #3954 and PR #3966 executables, Lean, Docker, and the selected
cold replay.

## Open next questions

1. For one same-class pair, such as label 32 against itself, can a paid
   correction of the six disagreeing bits be hosted without repaying the
   inherited excess 44,096? The shared line already agrees, so only the
   complementary address bits are in play. Blocked by a physical owner and a
   changed bill; the free-tag scaffold is still over capacity.
2. Does any non-orthogonal address change make the witness pair `(386, 405)`
   share one translation on both the full address and the helper tag `a`?
   This orthogonal gauge cannot. A different gauge needs its own defect
   calculation before it is treated as a caller.

## Credit

Chris R / Clear1nsight for PR #3954 and PR #3966, including the labels, the
witness, the gauge `z = 420`, and the open fiber-tag question. The orthogonal
gauge and the uniform tag `a` are theirs. The comparison of `z ⊗ q_j` with
`r_i ⊗ z` on these labels is new.

Prepared by unpaidmoon with substantial Cursor Grok assistance. No independent
human or formal-kernel review is claimed. New work is Apache-2.0.
