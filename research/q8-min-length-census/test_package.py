"""Behavioural controls for the mixed-negative Q8 minimum-length census.

Every check is a real rejection path in `verify.py` or in the model. The
controls run under `-O`, so they must not rely on `assert`.
"""

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("census_verify", ROOT / "verify.py")
census = importlib.util.module_from_spec(spec)
spec.loader.exec_module(census)

FAILED = []


def rejects(label, thunk):
    try:
        thunk()
    except (ValueError, KeyError, TypeError, IndexError):
        return
    FAILED.append(label)


def accepts(label, thunk):
    try:
        thunk()
    except Exception as error:  # noqa: BLE001 - the control wants the message
        FAILED.append(f"{label}: unexpected {error!r}")
        return
    return


# --- positive controls -----------------------------------------------------

accepts("unmodified census passes", census.verify)
accepts("i^3 is zi", lambda: census.require(census.mul(2, census.mul(2, 2)) == census.ZI, "x"))
accepts("three-call spine reaches zi",
        lambda: census.require(
            census.endpoint(tuple(census.spine(1, 0)), 1) == census.wanted(1, (census.ZI,)), "x"))
accepts("legal call enumeration is non-empty", lambda: census.require(census.legal_calls(1), "x"))

# --- algebra controls ------------------------------------------------------

def corrupt_group_product():
    saved = census.group_product
    census.group_product = lambda a, b: saved(a, b) ^ (1 << 4)
    try:
        census.verify()
    finally:
        census.group_product = saved


rejects("Q8 product law corruption", corrupt_group_product)

# --- model boundary controls ----------------------------------------------

rejects("bad paid label", lambda: census.endpoint(((3, 1, 1),), 1))
rejects("zero projector", lambda: census.endpoint(((1, 0, 1),), 1))
rejects("projector outside the role set", lambda: census.endpoint(((1, 4, 1),), 2))
rejects("even projector overlap v^T u = 0",
        lambda: census.endpoint(((1, 1, 2),), 2))
rejects("role capacity", lambda: census.legal_calls(0))
rejects("role capacity high", lambda: census.legal_calls(census.MAX_ROLES + 1))
rejects("empty endpoint target", lambda: census.parity_lower_bound((census.ONE,)))
rejects("unknown endpoint target", lambda: census.parity_lower_bound((7,)))

# --- witness and receipt controls -----------------------------------------

def break_witness():
    saved = census.WITNESSES["t2-zi-zi"]
    census.WITNESSES["t2-zi-zi"] = (2, (census.ZI, census.ZI), saved[2][:5])
    try:
        census.verify()
    finally:
        census.WITNESSES["t2-zi-zi"] = saved


rejects("truncated witness no longer reaches its endpoint", break_witness)


def shrink_census_limit():
    saved = census.CENSUS_CASES[:]
    census.CENSUS_CASES[:] = [("t1-zi", 1, (census.ZI,), 3)]
    try:
        census.verify()
    finally:
        census.CENSUS_CASES[:] = saved


rejects("a one-call word at t=1 contradicts exhaustion", shrink_census_limit)


def corrupt_algebra():
    saved = census.Z
    census.Z = 1 << 7
    try:
        census.verify()
    finally:
        census.Z = saved


rejects("z involution corruption", corrupt_algebra)


def corrupt_parity():
    saved = census.parity_lower_bound
    census.parity_lower_bound = lambda targets: (0, 1, 1, 0)
    try:
        census.verify()
    finally:
        census.parity_lower_bound = saved


rejects("parity bound corruption", corrupt_parity)

# --- receipt shape ---------------------------------------------------------


def receipt_shape():
    receipt = census.verify()
    reloaded = json.loads(json.dumps(receipt, sort_keys=True))
    for name in ("t1-zi", "t2-zi-zj", "t4-balanced"):
        row = reloaded["witnesses"][name]
        census.require(row["calls"] >= row["parity_bound"], "witness below bound")
    for name, row in reloaded["census"].items():
        census.require(row["exhausted"] is True, "census not exhausted: " + name)
        census.require(row["cap_reached"] is False, "census hit the cap: " + name)


accepts("receipt is JSON round-trippable and monotone", receipt_shape)

if FAILED:
    raise SystemExit("CONTROL FAILURES: " + "; ".join(FAILED))
print("PASS q8-min-length-census controls")