# Exact F3 minimum for the one-source additive connector

**Scoped interface bound; no new kappa.** The selected record is unchanged.

## Scope

Chooser seed `04cbf2cbcf13a1a4ea434b5ef3acf93b` drew `connector-alphabet-change`
on priority revision 7, base `12fa8c5c844be21bfefb38a19503fbd867a11244`.
Live alphabet extensions already cover arity-four source events, joint
outputs, high-arity toggles and the direct product call. The starting
[universal-connector-boundary](../universal-connector-boundary/README.md)
README already states that ordinary addition in odd characteristic does not
inherit the F2 construction. This package keeps the same operators

```text
B: z += x
A: y += z
```

and changes only that characteristic-two premise on the minimal one-source
one-output identity with arbitrary dirty `x`, `y` and `z`.

## What is established

Over F2 the word `BABA` meets every dirty input and restores `z`; no shorter
word in this alphabet does. Over F3 that word fails.

Track the affine state

```text
z = zx·x + zz·z0
y = yx·x + yy·y0 + yz·z0
```

with initial `(zx,zz,yx,yy,yz)=(0,1,0,1,0)`. Each `B` adds 1 to `zx`. Each `A`
adds the current `zz` to `yz`; `B` never changes `zz`, so `zz` stays 1 and
each `A` adds 1 to `yz`. A correct final state is `(0,1,1,1,0)`, so the number
of `B` calls and the number of `A` calls are each multiples of 3. Hence every
correct word has length at least 6.

Over F3, with arbitrary dirty x, y and z, every correct word in the additive alphabet {B, A} for the one-source one-output identity has length at least 6, and length 6 is attained by exactly six words.

An exhaustive enumeration finds no correct word of length at most 5 and
exactly these six length-6 witnesses, each with three `B` and three `A`:

```text
BBAABA  BABBAA  BAABAB
ABBAAB  ABABBA  AABABB
```

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/f3-additive-connector-1x1
```

Expected marker: `PASS_F3_ADDITIVE_CONNECTOR_1X1`.

## Limits

This does not price a five-source F3 batch, signed patterns, nonlinear
readouts or a physical supplier. The predecessor package's full 945-pairing
replay was not run in this partial checkout. No selected-frontier change is
claimed.

## Open next questions

For the five-source all-31-mask batch over F3 with the same additive alphabet,
what is the exact optimum? The F2 optimum is 74. A first step is to search
restored words whose per-label counts are multiples of three, starting from a
short positive witness. No such witness is pinned here.

## Credit

The F2 alphabet and 1x1 four-call control come from
`research/universal-connector-boundary` and the later direct-call audit
lineage. The signed F3 connector of #1349 is a different interface and is not
replayed. Riquelme Soares (@hevlyo), with substantial AI assistance in the
search, bound and write-up. Apache-2.0. No independent human review is claimed.
