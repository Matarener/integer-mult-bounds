# Logical and physical meaning of the six-contact retiming

Let Phi_F denote the exact canonical physical chart for frame F. At field width f, a typed field contains Phi_F tensor-power f applied to its logical value. A MOVE from F to G changes that chart by the exact operator Phi_G Phi_F^{-1}; the logical value is unchanged. A scalar ADD or COPY at a common chart acts on logical values by the specified scalar once, outside the tensor power. SCALE has the same convention.

The independent interpreter checks all consecutive MOVE boundaries, strict subspace nesting in the proper direction, exact common-chart identities for every scalar/COPY, and all INIT/CLEAR lifecycles. It propagates each logical row using exact integer numerators and a common binary denominator for each row. It compares every final row with the full required operator, including all 527 independent helper inputs and all eight owned columns. It also verifies that the candidate's scalar/owned operation sequence is the predecessor's sequence, after removing chart labels and MOVE records. Therefore, when the native chart-change interfaces are lowered with their exact phases, the typed word has the same physical endpoint for every positive integer f. This is a direct compositional identity; no width-one matrix independence argument or tensor-powered owner coefficient is used.

Native lowering is a distinct check. This peer package does not import a native lowering implementation or silently infer its absolute phase from a signed tableau.

## First connected change: source events 10461, 10462, 13970

The shared old frame 335 has dimension 2; new frame 17 is the one-dimensional span of 145. The exact scalar coefficients are unchanged:

```
297 += 303
303 -= 297/2
152 -= 297/2
```

The role histories in the receipt bind the different actual field versions and all intervening contacts. The paid profiles change as follows:

- Role 297 replaces its consecutive frame-chain ranks 1+1 by rank 2, retaining its initial rank-1 arrival at frame 17.
- Role 303 splits one old rank-2 rise into two rank-1 rises, placing its second rise after the two butterfly ADDs but before its next required frame-335 use.
- Role 152 replaces two rank-2 rises by rank 1 followed by rank 3.

The net profile change is H1 - 2 H2 + H3. The interpreter verifies the complete chronological word, so none of these statements grants a free conversion between unequal physical charts.

## Second connected change: source events 15479, 15639, 15640

The shared old frame 915 has dimension 7. New frame 207 has dimension 8 with basis

```
[2, 5, 8, 17, 33, 65, 129, 257].
```

The exact scalar sequence is

```
198 += 319
205 += 198
198 -= 205/2
198 *= -2
```

The three ADDs and final SCALE move to frame 207. Role 198 replaces ranks 4+1 by rank 5. Role 319 replaces ranks 1+2 by ranks 2+1; this changes chronology, with no paid-profile change. Role 205 replaces rank 2 by two rank-1 rises. The resulting net change is H1 - H2 - H4 + H5.

The remaining fourteen SCALE chart retimings commute through their own chart changes, retain exactly their source coefficients and scalar order, and are explicitly checked in their actual surrounding field versions. They do not change any paid rank.

Combining the two changes gives +2 H1 -3 H2 +H3 -H4 +H5, with zero change to rank mass. No helper target is promoted or discarded; no borrowed source is erased; owned peak and lifetimes remain the predecessor's values.
