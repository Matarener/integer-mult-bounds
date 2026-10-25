# Program-tape invoice for one R437 child constructor

This note prices `children.extend`, the constructor called by
`SelectedBinding.child_program`. It is one term of `Pi_v` in equation (6) of
PR #3983. It is not the whole of `Pi_v`, not a stock coefficient, and not a
new κ.

## Boundary

The pinned source is `research/selected-bit-physical-caller/inputs/pr2753/predecessor/vendor/children.py`
at base `bb4bccbf42844d2801487450727c2f63e10d1d0f`. `extend` receives a parent
`Program` whose tape head is already on the first symbol. That is the
postcondition of `Program.root`, `Program.step`, `Program.fixture`, and
`Callback._validate_program`. Index words occupy `I` bits and residue words
occupy `L` bits, each ending at `RIGHT`, because `Arena.zero` fills the fixed
width. Finite tags use the pinned `FINITE_BITS = 16`. The code width is `Q`.
The parent holds `h ≥ 0` chronological `STEP` records. The arithmetic that
builds the next child extent is assumed to succeed; its arena traffic is not
part of the tape formulas below.

## Lengths

A full-width word contributes `W + 1` symbols (`W` bits and `WORD_END`).

The root record is `ROOT`, two index words, one residue word, and `RECORD_END`:

```text
R0 = 1 + 2(I + 1) + (L + 1) + 1 = 2I + L + 5.
```

One step record is `STEP`, one `Q`-bit code, five 16-bit tags, two index
words, and `RECORD_END`:

```text
c = 1 + (Q + 1) + 5(16 + 1) + 2(I + 1) + 1 = Q + 2I + 90.
```

The parent therefore has `N = R0 + h c` symbols after `LEFT`. The constructor
writes the same root, copies those `h` steps, and appends one new step, so
the child has

```text
S = R0 + (h + 1) c
```

symbols after `LEFT`. Counting `LEFT`, this is the `P_{h+1}` length already
stated in PR #3983. The new fact is the operation count that produces it.

## Operation count

`Tape.append` is one read, one write, and one move. `Tape.rewind` from a head
sitting on the blank after `n` symbols costs `n + 1` reads and `n + 2` moves.
From head 1, on a tape whose first cell is `LEFT`, it costs 1 read and 2 moves.

On the parent, `extend` then:

1. reads every root symbol once while seeking the first `RECORD_END` (`R0`
   reads and `R0 - 1` moves) and steps past it (one move);
2. copies the following `M = h c` symbols, reading each twice (the loop test
   and the read inside `append`) and moving once per symbol, then reads the
   terminal blank once;
3. rewinds from the blank after all `N` symbols (`N + 1` reads and `N + 2`
   moves).

The parent writes nothing. Its meter is

```text
reads  = 2 R0 + 3 M + 3,
writes = 0,
moves  = 2 R0 + 2 M + 4.
```

The child tape starts empty. Every one of its `S` symbols is one `append`,
and the final rewind runs from the blank after those symbols. Its meter is

```text
reads = 2S + 1,   writes = S,   moves = 2S + 2.
```

These identities do not depend on the child kind, rank, or half-width flag.
Those values change the index-arena arithmetic and the bits stored in the new
step, not the number of full-width symbols.

`S ≥ c ≥ 90`. The `S` child writes are strictly positive. PR #3983's equation
(5) copies an already produced capsule and explicitly excludes producing the
copied data, so these writes belong to `Pi_v`, not to (5).

## What this does not discharge

`SelectedBinding.check_stock` is a single `pass`. Calling the selected
constructor does not compare an original-width stock word. `extend` does not
name a prefix tape; `prepare_child` reads the prefix earlier, outside this
function. Index and residue arena traffic during the extent arithmetic is
present and is not priced here. `Callback._validate_program`, directory
production, `layout.child_extents`, temporary cleanup, and closing geometry
remain other terms of `Pi_v`.

The entry-head hypothesis is necessary. A parent head moved one cell off the
rewind postcondition changes the opening rewind and leaves the formulas.

No selected-frontier statement follows. Selected κ stays
`0.001672660197076918`.
