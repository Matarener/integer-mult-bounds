# Independent review of the partial-Pauli cyclic refinement

Verdict: PASS for the precise logical frame model and the finite construction
stated in the Pauli proof. No outstanding mathematical finding was identified.
This review was completed against the frozen files below on 2026-10-20 UTC.
It is a new companion review; the frozen cyclic core and its inventory were
not modified.

## Reviewed bytes and independent evidence

The reviewed Pauli package is the sibling contribution `c03-pauli`. Its
scientific snapshot is `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.

| File | SHA-256 |
| --- | --- |
| `check.py` | `97b97531bd312ccae4da4ce2e7a767f32c749db2eb7408eb38b517699f970a66` |
| `PROOF.md` | `74e81020d348b57f21bb857ce25f1d68efd822d6c7a4e1e97219d80f1eb8ed9c` |
| `CHECKS.json`, recovered from the transport | `dd2bd852b6b5b3c78f2e0cb6a5e6aff49cf4f3956aa18673bd555bfb6b069220` |
| `CHECKS.json.gz` | `8e87b99cbab046151357691f7b891f25daf4aba5f2ad6c6bedda3342d003bce4` |
| `OUTPUT-INVENTORY.json` | `e298c71472382495463ff06cb423458c2c96fd7644dd87910ace3a687c7d3987` |

Every entry in that inventory was freshly checked for byte length and digest.
The compressed receipt was freshly decompressed and compared with the raw
receipt. The independent cyclic receipt used for reconciliation has raw
SHA-256 `f06ada7495619759967cc1160a1012d8ed12e527970fd389717c4ef9b78cc832`.

`CROSS-REVIEW-PAULI-CHECK.json`, SHA-256
`569ac24b666e6260e5efab3f9a718c28e4e16a702ea1f7dcb22010fedafbfc8c`,
records a fresh independent recount. That recount reads JSON as data, uses a
separate binary Gaussian elimination routine, and imports no checker code.
It compares the complete arrays of 2,400 frame cases, 40 triples, 60 pairs,
and all triple gauge signs. It also reconstructs every selected join, the
separate role histograms, the complete changed histograms, and the eight
individual scalar-support censuses. The shared canonical frame-array digest
is `90b0a4049066b6eb08ab223ba03d8f9af95bbe688a09c4ee5c7f586ad1fdd46b`.

This is source/proof review plus the stated independent finite recount. It
does not repeat the author's complete normal/optimized run or the other
reviewer's ordinary-column/control audit.

## Mathematical interface and restoration

The selected polynomial is `E_i(a,b)=a_i q(b)`, where
`q(b)=sum_j (-1)^j b_j^2`. Inspection of the retained evaluator agrees with
the index translation `120+44i`, weight 1 and denominator 8192. The retained
NumPy evaluator is not claimed to have been executed by the portable audit.
The independently counted support has 5,760 signed physical ports; every
individual feature has 3,072 coefficients of absolute value 8 and 672 of
absolute value 16. This reproduces the component primitive invoices
1,258,008 forward and 1,258,032 dual, including their distinct private bills.

For arbitrary ordinary dirt `d`, the forward word has target change
`-E d/8192 + E(d+E^T x)/8192 = E E^T x/8192`, followed by centre cleanup.
The same-chronology logical inverse transpose yields source change
`-E(d+E^T y/8192)+E d = -E E^T y/8192`, with centre dirt restored. The proof
correctly gives a separate dual private readout interface: it does not take
an inverse transpose of a destructive CLEAR. Forward source immutability is
used only in the forward substitution and schedule. It is not incorrectly
assumed for the changing source rows of the dual word.

These statements concern logical values under fixed representatives `T_A`.
Ordinary centres start at ZERO and finish at FULL. Their final logical value
is their initial dirt, while their final physical value is `T_FULL d`.
The proof expressly retains this physical endpoint transport. The support
space U has dimension 15 and radical W of dimension 2; W is contained in U.
The frame and private dimension-difference tariffs are explicit assumptions,
including for these degenerate spaces. No native phase, raw-return, or
physical inverse-transpose theorem is inferred from the binary inclusions.

## Actual common-frame chronology

Exactly 12 b-pairs are supported by q, so precisely 960 of the 4,800 signed
cyclic modules are affected. The source and target arc indices agree with
the cyclic word, including its cyclic direction and excluded target group.
All 1,440 selected triple/pair/group records have signed multiplicity four.

The independent elimination confirms for every selected record that the
source's final rank-three arc lies in U, and that the target delivery arc A
has `dim(A intersect W)=1`. Thus `W` is not contained in A. One cannot insert
a free monotone target visit `ZERO -> W -> A`. The actual join `J=A+W` has
dimension four and lies in each receiving target cap. The revised delivery
is legal because both target and reader are at the identical representative
`T_J` when the original scalar coefficients are applied.

The following dependencies are satisfied by the written global schedule:

1. All ZERO dirt prefixes and residual edge-helper loads occur before their
   data operands leave the required ZERO/source-line frames.
2. The cyclic gathers finish before the selected sources enter U. Those
   sources remain there for the eight selected centre gathers, then move
   to FULL.
3. All unchanged 808-centre ZERO outputs finish before affected targets
   enter W. Selected output occurs at ZERO or W according to its stated
   private variant, with centres then cleaning up at FULL.
4. Radical targets move W to J, and their module readers move their old arc
   to the same J before cyclic delivery. Unaffected modules retain their
   existing frames. Targets then reach their caps for residual delivery;
   ordinary readers finish their logical cleanup at FULL.

No new ordinary role is required. No selected Pauli coefficient changes the
cyclic sign gauge: the latter remains absorbed in its own gather/delivery
coefficients. The same frame chronology supports the logical dual because
each dualized scalar ADD still has a common representative, and the private
dual interface was separately specified.

## Complete role invoice and the decision it supports

The independently reconstructed affected paths are

| Role | Original increments | Radical refinement |
| --- | --- | --- |
| source | `[1,1,14]` | `[1,1,12,2]` |
| target | `[3,13]` | `[2,2,12]` |
| cyclic reader | `[2,1,14]` | `[2,1,1,13]` |

There are 5,760 instances of each affected role. For ZERO output only the
source path changes. The eight selected centres change `[17]` to `[15,2]`;
their private events change rank 17 to rank 15 or 13. Separately including
the reader change is essential. With `H_r` denoting a rank-r event, direct
subtraction gives

```
ZERO:    5760*(H12+H2-H14) + 8*(2H15+H2-2H17),
radical: 5760*(H1+3H2+2H12-H3-2H14)
         + 8*(H15+H2+H13-2H17).
```

The rank masses are -16 and -32, entirely from the private saving. The
complete paid power comparison uses every displayed term, rather than
substituting that smaller rank mass for its concave moment. The source's
rational power enclosure, sign propagation, and threshold-neighbor tests
were inspected. Their integer inequalities bind the result independently of
the floating initial root guess. The derivative bound used for the
`10^-24` exponent shift is valid for all recorded ranks at most 17.

At the three stated exponents, the fully charged standalone and actual
cyclic refinements worsen the stated moment. The positive factor `m^beta`
does not change this sign. The admitted full invoice is restricted to odd
L at least 3, where the cap admits every rank at most 17 without splitting.
No L=1 capped-invoice result is inferred. The threshold table concerns
another hypothetical word with identical visits already paid; it is not a
certificate that the present cyclic word supplies them.

## Evidence limits

The proof clearly separates the four 46-column diagnostics, the exhaustive
finite support/frame data, and the all-input factor identity. It does not
claim a dense 5,760-port replay, a rerun of the full 816-centre background,
whole-supplier precision, a native compiler, physical stock/owner access,
or a new multiplication bound. The logical prefix bounds and dyadic depth
are appropriately limited to the selected subword. The rank-34 restriction
is confined to the stated 35-dimensional quadratic evaluation family.

No additional mathematical correction is requested for this frozen version.
