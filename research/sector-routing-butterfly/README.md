# Boolean-sector routing with one query per block

This package replaces the quadratic ordinary work in the published T7 family with an in-place routing network. It gives an exact construction for every sector count `n = 2^s`, `s >= 1`, and every number `r >= 1` of disjoint blocks. It does not install a complete multiplication caller.

Let `J_0,...,J_(s-1)` be commuting involutions. Let `Q` commute with them and satisfy `Q^2 = J_0`. Put `E_a = product_j (I + (-1)^a_j J_j)/2`. The perturbation map is `x_(b,a) -> x_(b,a) + Q E_a x_(b,a)/2`. The gauge map replaces this expression with `(I + (Q-I)E_a)x_(b,a)`.

| Contract | QUERY | ADD | Pure SHIFT | CLEAR | Extra fields |
|---|---:|---:|---:|---:|---:|
| Perturbation, in place | r | 6rns+2r | rns | r+1 | 1 |
| Gauge, in place | r | 6rns | rns | 0 | 0 |
| Perturbation, inputs retained | r | 6rns+rn+2r | rns | rn+r+1 | rn+1, with outputs |

Each ADD has different source and destination fields. Every coefficient is `1`, `1/2`, or `-1/2`. There is no sector-dependent overwrite primitive. The pure shifts and the shifted ADDs are explicit instructions.

For 32 sectors and one block, the input-preserving version uses **994 ADDs and 160 pure shifts**, instead of the **2,080 ADDs** in PR5626. Both use one query, 34 CLEARs, and 33 extra fields including outputs. If each ADD and pure shift has unit cost, the total falls from 2,080 to 1,154. A physical caller can price these operations differently. The in-place version uses 962 ADDs, 160 shifts, two CLEARs, and one extra field. Its storage comparison has a different input-retention contract.

The query count is minimal in the faithful-sector model of PR5626. The perturbation workspace and CLEAR counts are also minimal in the narrower alphabet specified in [PROOF.md](PROOF.md). The proof does not allow a nonunit scalar overwrite. It counts an owned field as arbitrary on entry and zero on exit. The gauge version needs no owned field.

The proof gives a bound `2 n^2 (1+M)` for every prefix and suffix of an in-place block, if `M >= 1` bounds the query and its internal prefixes and suffixes. The same bound holds for sequential disjoint blocks. Instruction-boundary checks do not certify the arithmetic inside a native query.

## Evidence

Run with Python 3.12 and the standard library:

```sh
python3.12 -I -W error -B research/sector-routing-butterfly/verify.py
python3.12 -I -O -W error -B research/sector-routing-butterfly/verify.py
```

The verifier checks 28 full-column maps in `Q[C4 x C2^(s-1)]`, with `s <= 5` and up to four blocks. A separate reverse-adjoint replay checks each suffix and final transpose. Five further full-column cases retain the inputs. It also checks 48 exact native Gaussian address cases with `1 <= f <= 4`, `1 <= s <= 3`, and one or two blocks. Arbitrary initial workspace columns are included. Five changed words must fail. A nonunit-scale control marks the limit of the storage proof. [RESULT.json](RESULT.json) stores the exact counts and coefficient norms.

The general statement follows from the proof. The finite checks support that proof; they are not an exhaustive native caller certificate. The source files in `inputs/` are evidence, not executable dependencies. Their bytes and commits are pinned in [PINS.json](PINS.json). Source history is not available in the shallow export; byte checks and the committed-file check are separate.

## Attribution and limits

Ali Romman with substantial OpenAI Codex assistance wrote this package. The model derived and implemented the route, proofs and checks. No independent human review is claimed. Retain credit to Dugongue for PR5578 T6/T7 and PR5586 C8; PR5626 supplies the sector-rank lower bound and the comparison compiler. PR5615 supplies its dyadic rank-factor lineage. Retain Nick Petalas, Cao, DaysSky, Cinna, Ryanson, zxv and Jacob in that source lineage. The frozen files retain their original text.

The selected result at base `df0137efd35e11b4445734bf612bdd4c7ebc330c` is unchanged. This result has no new kappa. A complete supplier, a profitable native B/C demand, physical routing, precision, and a complete outer bill remain open. The existing whole-caller and role-gauge obstructions retain their scope.

## Open next questions

- Find an actual caller whose required map has these disjoint sector supports. Price the full input and return protocol before claiming a gain.
- Price the ordinary shifts and shifted ADDs at that caller's actual address layout. A count of field instructions is not a tape cost.
- Test whether a broader scalar-overwrite alphabet can use less workspace without a larger arithmetic or precision bill. The present storage proof does not cover that alphabet.
