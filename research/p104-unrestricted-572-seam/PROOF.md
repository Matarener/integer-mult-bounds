# Arbitrary linear recoding cannot repair the frozen helper-572 seam

This scoped proof was produced by Nick Petalas. All scalars are rational.
The finite certificate establishes the boundary facts below from the pinned
selected PR6030 word. It does not replay a predecessor's exclusion theorem.

## 1. Contract

Keep the original word, its public inputs, frames, owned lifetimes and event
order. Event indices are zero based; a window is immediately after its event.
After event 13637, `COPY 778 <- 572` in chart 595, overwrite field 572 with a
new independent scalar input z. Every original public input remains arbitrary.

Allow any finite number of homogeneous linear operations, with arbitrary
rational coefficients, within these banks:

- Chart 595 after events 13637 through 13651, on fields
  `(127,572,581,582,731,778)`.
- Chart 603 after event 13652 or 13654, on `(572,740)`, and after event 13655,
  on `(572,709,740)`.

Operations may change original-input rows temporarily. They need not preserve
an original-zero carrier. No extra field, new MOVE or changed prefix/suffix is
permitted. We grant arbitrary linear bank maps, including singular ones, so the
exclusion also covers ADD/SCALE programs of unbounded finite length in these
regions. COPY or erasure within the granted banks cannot evade it.

Put V equal to field 572's original final chart, 127. The necessary condition is
that every public output whose original final chart differs from V equal its
original unsplit value, on all original inputs and z. There are 186 such outputs.
The desired additional target would require nonzero public dependence on z.

**Theorem.** Under this contract, satisfying the protected-output condition
forces every final public output to have zero z coefficient. Thus no nonzero
independent target can be supplied by these corrections, regardless of their
number or coefficients.

## 2. Collapse the chronology to two matrices

The first bank remains exactly the six listed fields through event 13651.
All intervening operations in other charts are unaffected. Absorb the retained
`582 += 2*731` and every allowed first-bank operation into one arbitrary 6 by 6
map A at the first bank's exit.

At event 13652, only field 572 moves from chart 595 to 603. Field 740 is already
there. The retained `740 -= 572` at event 13654 and every allowed operation on
these two fields are linear. Field 709 enters from chart 597 at event 13655;
its value has not been changed by any allowed operation. Extend the earlier
2 by 2 maps by the identity on that entering field and absorb them with the
last operations into one arbitrary 3 by 3 map B.

Consequently only one scalar form r from the first bank reaches the second.
The second bank's three values are linear combinations of `(r,h,k)`, where h
and k are the original cut values of fields 740 and 709. Five first-bank fields
remain in chart 595. CLEAR 778 immediately follows, at event 13656.

This is a relaxation: arbitrary A and B need not be realizable by reversible
scalar gates. Proving failure in this larger class suffices.

## 3. The exact source and suffix certificates

Let u be the eight-component vector of cut forms in this order:

```text
u = (old127, z, old581, old582, old731, ell, h, k),
ell = old572 = old778 after the retained COPY.
```

These eight forms are linearly independent in the original 770 inputs and z.
The exact minor on input columns
`(0,2,34,572,581,582,740,770)` has determinant `1/32`; column 770 denotes z.
The verifier derives the forms from the prefix and checks this determinant
by the Leibniz formula, separately from its pivot selection.

Use the following order for state differences immediately after event 13655:

```text
(127,581,582,731,778,572,740,709).
```

Propagating their eight unit perturbations through the unchanged suffix shows:

1. The perturbation on 778 reaches no final public output.
2. The perturbation on 740 reaches only final public output 740, with coefficient 1.
3. Output 740 is V-final. The six outputs below are protected.

After deleting columns 778 and 740, the suffix rows on protected outputs
`(116,120,127,134,138,176)` are exactly

```text
          127 581 582 731 572 709
116        0   1   0   2   0   0
120        0   0   0   0  -1   2
127        1   0   0   0   0   0
134        0   0   0  -2   0   0
138        0   0   0   0  -1  -2
176        0   0  -1   0   0   0
```

Its determinant is 8. Therefore preserving these six outputs alone forces the
six corresponding state forms `(127,581,582,731,572,709)` to equal their original
unsplit forms. This deduction is an identity in all original input columns and
z, not just a statement about the new input's leakage.

For completeness, the original eight post-seam state forms are, in the same
order as the eight state differences,

```text
(old127, old581, old582+2*old731, old731, ell, ell, h-ell, k).
```

The verifier checks every coefficient of these identities against the prefix.
It also checks the two exceptional suffix columns at every public output.
Together the two nonzero minors and these identities are a finite certificate
of all source-specific premises used in the argument.

## 4. The single-channel obstruction

Write the transmitted form as `r = a*u_first`, where `u_first` consists of the
first six entries of u. Since second-bank values are B applied to `(r,h,k)`,
there are rational coefficients d,e,f with

```text
post572 = d*r + e*h + f*k.
```

Section 3 forces `post572 = ell`. Independence of u therefore gives

```text
d*a = (0,0,0,0,0,1),  e=f=0.
```

The right side is nonzero, so d is nonzero. Thus a is a scalar multiple of the
ell coordinate vector. In particular r has zero z coefficient. Neither h nor
k contains z, so no second-bank field can contain z, including field 740.

The other four non-erased first-bank forms are forced to their original values
by the same minor and hence contain no z. The remaining first-bank field, 778,
has identically zero public suffix response. Every other state field is
unchanged by the allowed corrections. Therefore every final public z
coefficient vanishes, proving the theorem.

Equivalently, the second stage's first-six-input coefficient block has rank at most one.
It must contain the ell row; a nonzero z coordinate in its 740 row would raise
its rank to at least two. A second independent transported scalar could change
that conclusion. No price or physical realization for such a transport is
asserted here.

## 5. What is new and what remains

JoyboyBrian's PR6088 excludes two added ADDs in these regions by inconsistent
endpoint equations. The present result removes the scalar-operation-count
bound and permits arbitrary linear bank recoding. It uses a protected-output
minor and a one-channel factorization rather than the predecessor's pair
census or bilinear relaxation. The predecessor's counts are not rerun.

The carrier-only theorems of apoursh PR6067 and Jonathan Capalbo PR6069 require
original-zero correction sources. This proof permits original-input changes.
JosieElliston PR6108 distinguishes the remaining cross-time problem and supplies
a different scalar witness on PR5907. Nick Petalas PR6040 is the earlier
unit-injection census, not an arbitrary-input recoding theorem.

The exclusion fixes the overwrite, these two chart regions and all later
original events. Later correction windows, a pre-cut save, a second transported
form, changed routes or storage, nonlinear encodings, and another word are
outside scope. There is no physical/native supplier, productive normalization,
complete signed invoice, compiler/precision/caller/outer proof, new kappa or
complete multiplication theorem. The five selected framework assumptions
remain. Independent human and formal proof-kernel review are unclaimed.

Credit JoyboyBrian, apoursh, Jonathan Capalbo, JosieElliston, Matarener,
flyingviper, Ali Romman, DreamingOfClouds and the retained P104 lineage.
Apache-2.0.
