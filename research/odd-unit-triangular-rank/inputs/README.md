# Frozen comparison source

I exported these exact files from Philippe Van Velzen's published commit
`b5ce9d223feeed73d07e2a07321f7a025bd5865e`:

- `LICENSE`
- `research/complex-budget-law/closures-2/small-units-h5/unit.py`
- `research/complex-budget-law/closures-3/small-units-lp/README.md`
- `research/complex-budget-law/closures-3/small-units-lp/core6.py`
- `research/complex-budget-law/closures-3/small-units-lp/idem77.py`

I used `git archive --format=tar` with these paths to retain the original
bytes and notices. Replay checks the committed archive and its regular
members without requiring the fork's Git objects or executing its code.
The verifier reconstructs the small geometry with standard-library code.
The archive is a source snapshot, not a certificate of the predecessor's
unreplayed LPs or a new selected frontier.
