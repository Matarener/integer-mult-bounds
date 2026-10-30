# Replay adaptations

The frozen historical code and data are unchanged. Original imports, absolute
path constants and command-line entrypoints are not imported wholesale.
`verify.py` authenticates each selected file against `FROZEN-SHA256.json`,
selects unique named top-level definitions and compiles those definitions
with `dont_inherit=True, optimize=0`.

The inherited nested recipe loaders still select the original `recipe`
definition. Their supplied AST parser requires that definition to be unique,
and their supplied compiler also forces assertions on under optimized Python.
Only the recipe executes from the original `global_k.py`; its imports and
other top-level code do not execute.

Every retained historical source read uses an explicit `SourcePath` mapping.
Its only I/O authenticates the declared frozen bytes anew. This covers the
recipe, matrix input, R438 word, full E8 root word and route-generator hash.
The original unique literal `RAW_SHA` is parsed from the retained
`bit_cap_copy_local.py` and must agree with the frozen R438 input. No function
from that cap-copy file runs.

The original closed-hybrid `receipt()` is evaluated directly. The original
nilpotent and early-promotion generators run their selected `main()` with
`--write` and a temporary output directory outside the package. Those complete
fresh JSON values are compared against the three frozen receipts with a typed
canonical serialization, preserving every field and list position.
The old Python dictionary-equality acceptance paths are therefore not the
publication acceptance check.

Only `need`, `mul`, `plus`, `scale` and `ident` are selected from the seeded-star
file. Its main program and unused `inverse_event` stub do not execute. That
stub's broad involution comment does not describe the new-F primitive and is
not used as a premise.

The independent checkers receive only explicit input paths and external output
paths. Their complete modules are compiled from authenticated bytes with
assertions enabled. Every full generated receipt is compared, and the frozen
inventory is checked again after each stage.

These are loading and acceptance adaptations. They do not alter the old
mathematical functions, discard receipt fields or turn an imported native
premise into a proof.
