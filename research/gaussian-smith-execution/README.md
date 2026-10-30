# Executable Gaussian Smith precision interface

This package implements the full arbitrary-input Gaussian response proposed
in PR5815. It uses exact minimal-size Gaussian residues, preserves the source,
emits all outputs and records both passes, copies, scales and owned cleanup.
An exact forward/swap/inverse adapter includes both kernel costs.

Two scoped results make the precision contract sharp. The diagonal bank uses
exactly the information required to distinguish all raw outputs. At every T
cut, one fewer digit in any live coordinate loses an output for an explicit
integral input. These claims do not bound the time of a different algorithm.

[PROOF.md](PROOF.md) states the all-size argument. [RESULT.json](RESULT.json)
contains the executed cases and operation invoices. [engine.py](engine.py)
exports `execute(x,n,P)`, `formula(n,P)` and `install(x,n,header=0)`. A Gaussian
integer is a pair of Python integers. P is the raw modulus exponent; normalized
output precision p uses P=p+n and denominator tag n.

```python
import engine
output, invoice = engine.execute([(1,0),(0,0),(0,0),(0,0)], 2, 3)
```

Run from the package directory for the example import. The direct verifier
uses Python3.12 and the standard library, writes nothing and needs no Git.

```sh
python3.12 -I -B research/gaussian-smith-execution/verify.py
python3.12 -B scripts/research_package.py --package research/gaussian-smith-execution
```

Normal and optimized checks cover723 modular endpoint cases through1024
coordinates,63 basis axes,19773 residue cases,2746 underprecision witnesses,
768 exact invoices and seven exhaustive finite-ring image censuses. Ten exact
installation fixtures return owned old values to zero. Separate controls retain
odd-precision parity, zero normalized precision and rounded-cleanup failure.
See [VALIDATION.md](VALIDATION.md) for publication evidence.

Base canonical main de5ec2e7a6074068452f45b1a191b5c72832df4a, priority8. The
connector-alphabet card is changed to this explicit ordinary-response audit;
its945-pairing control passed. Source PR5815 is pinned in [ORIGINS.json](ORIGINS.json).
The source theorem and native matching retain Dugongue's credit. New code,
proof and checks: Ali Romman with substantial OpenAI Codex assistance, no
subagents. Apache-2.0; retain all [source notices](source/NOTICES.md).

## Open next questions

1. Bind the indexed circuit to one actual native recipe and physical routing
   contract, then charge all matcher, spectator, representation and tape work.
2. Compare complete routes, not only ADD mass. At p proportional to n, this
   literal circuit retains Theta(2^n*n^2) addition mass and gives no positive
   kappa by itself.
3. Test a changed representation against the proved information and cut
   bounds. An improvement must change the algorithm or mix coordinates.
4. Supply permitted truncation and cleanup on a reversible host. Exact owned
   reset here is an explicit array-model premise.

All five framework assumptions remain; the selected frontier is unchanged.
