#!/usr/bin/env python3
"""Four deliberate audit defects must fail their mathematical diagnostics.

Only in-memory copies of this package's verifier are modified. Frozen inputs
are not changed or executed. OpenAI Codex assistance; Apache-2.0.
"""
from pathlib import Path

path = Path(__file__).with_name("verify.py")
original = path.read_text(encoding="utf-8")
cases = [
    ("dot(e, e)/d for e in errors", "dot(e, e)/(d*d) for e in errors",
     "module_checks", "relative error lower bound"),
    ("Q(1, 3) if j == k else 0", "Q(0) if j == k else 0",
     "module_checks", "nonorthogonal cross Gram"),
    ("repaired[1] += len(ports)", "repaired[1] += len(ports)-1",
     "pricing_checks", "repair adds exactly the claimed 104 rank-one jobs"),
    ("paid, targets = extract_invoice()", "paid, targets = extract_invoice(); targets[17] -= 1",
     "pricing_checks", "original target credits retained exactly once"),
]
for old, new, entry, diagnostic in cases:
    if original.count(old) != 1:
        raise ValueError("mutation anchor must be unique: " + old)
    namespace = {"__file__": str(path), "__name__": "audit_mutant"}
    exec(compile(original.replace(old, new), str(path), "exec"), namespace)
    try:
        namespace[entry]()
    except ValueError as error:
        if str(error) != diagnostic:
            raise ValueError("wrong mutation diagnostic: " + str(error)) from error
    else:
        raise ValueError("deliberate defect was not rejected: " + old)
print("PASS_PAID_RETURN_BRIDGE_MUTATIONS controls=4")
