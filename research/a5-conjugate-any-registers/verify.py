#!/usr/bin/env python3
"""Verify the any-register A5 conjugate 5-cycle four-call floor."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
CERT_NAME = "CERTIFICATE.json"
if str(PACKAGE) not in sys.path:
    sys.path.insert(0, str(PACKAGE))

from algebra import (  # noqa: E402
    IDENTITY,
    SELECTED_KAPPA,
    X,
    Y,
    apply_factor,
    build_group,
    compose,
    direct_word,
    elem_mask,
    ga_mul,
    identity_state,
    is_rank_one_idempotent,
    mat_add,
    projector,
    rank_f2,
    subsequence_support,
    target_state,
)


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def git_blob(path: str) -> str:
    return (
        subprocess.check_output(["git", "rev-parse", f"HEAD:{path}"], cwd=ROOT)
        .decode()
        .strip()
    )


def load_json_reject_duplicates(path: Path):
    text = path.read_text(encoding="utf-8")

    def hook(pairs):
        seen = {}
        for key, value in pairs:
            if key in seen:
                raise ValueError(f"duplicate JSON key {key!r} in {path}")
            seen[key] = value
        return seen

    return json.loads(text, object_pairs_hook=hook)


def source_pin_rows() -> list[dict]:
    sources = load_json_reject_duplicates(PACKAGE / "SOURCES.json")
    need(sources["base_commit"] == "bb4bccbf42844d2801487450727c2f63e10d1d0f", "base pin")
    rows = []
    for row in sources["files"]:
        path = row["path"]
        full = ROOT / path
        need(full.is_file(), f"missing source {path}")
        digest = sha256_file(full)
        blob = git_blob(path)
        need(digest == row["sha256"], f"sha256 drift {path}")
        need(blob == row["git_blob"], f"git blob drift {path}")
        rows.append(row)
    return rows


def group_axioms(elements, index, table) -> dict:
    need(len(elements) == 60, "A5 order")
    need(IDENTITY in index and X in index and Y in index, "generators present")
    xy = compose(X, Y)
    yx = compose(Y, X)
    cur = IDENTITY
    for _ in range(5):
        cur = compose(xy, cur)
    need(cur == IDENTITY, "xy order 5")
    cur = IDENTITY
    for _ in range(5):
        cur = compose(yx, cur)
    need(cur == IDENTITY, "yx order 5")
    need(compose(X, X) == IDENTITY, "x order 2")
    cur = IDENTITY
    for _ in range(3):
        cur = compose(Y, cur)
    need(cur == IDENTITY, "y order 3")
    need(xy != yx, "distinct conjugate 5-cycles")
    need(len(elements) == 60, "generated group is A5")
    table_bytes = bytes(value for row in table for value in row)
    return {
        "order": 60,
        "xy_index": index[xy],
        "yx_index": index[yx],
        "x_index": index[X],
        "y_index": index[Y],
        "identity_index": index[IDENTITY],
        "group_table_sha256": sha256_bytes(table_bytes),
    }


def support_exclusion(xy, yx) -> dict:
    """Only xyx and yxy among length <=3 label words can host both 5-cycles."""
    patterns = {
        "x": (X,),
        "y": (Y,),
        "xx": (X, X),
        "xy": (X, Y),
        "yx": (Y, X),
        "yy": (Y, Y),
        "xxx": (X, X, X),
        "xxy": (X, X, Y),
        "xyx": (X, Y, X),
        "yxx": (Y, X, X),
        "xyy": (X, Y, Y),
        "yxy": (Y, X, Y),
        "yyx": (Y, Y, X),
        "yyy": (Y, Y, Y),
    }
    both = []
    excluded = []
    for name, labels in patterns.items():
        support = subsequence_support(labels)
        has_both = xy in support and yx in support
        if has_both:
            both.append(name)
        else:
            excluded.append(name)
    need(both == ["xyx", "yxy"], f"unexpected both-support patterns {both}")
    need(len(excluded) == 12, "twelve patterns excluded by support")
    return {"both_support_patterns": both, "support_excluded_patterns": excluded}


def ring_masks(index, table):
    alpha = elem_mask(index, X) ^ elem_mask(index, IDENTITY)
    beta = elem_mask(index, Y) ^ elem_mask(index, IDENTITY)
    ab = ga_mul(alpha, beta, table)
    ba = ga_mul(beta, alpha, table)
    aba = ga_mul(ab, alpha, table)
    bb = ga_mul(beta, beta, table)
    bab = ga_mul(ba, beta, table)
    need(ga_mul(alpha, alpha, table) == 0, "alpha^2 = 0")
    xy = compose(X, Y)
    yx = compose(Y, X)
    need(bool(ab >> index[xy] & 1) and not (ab >> index[yx] & 1), "αβ has xy only")
    need(bool(ba >> index[yx] & 1) and not (ba >> index[xy] & 1), "βα has yx only")
    need(bool(aba >> index[xy] & 1) and bool(aba >> index[yx] & 1), "αβα has both")
    return {
        "alpha": alpha,
        "beta": beta,
        "ab": ab,
        "ba": ba,
        "aba": aba,
        "bb": bb,
        "bab": bab,
    }


def _zero_matrix(roles: int) -> tuple[int, ...]:
    return tuple(0 for _ in range(roles * roles))


def _target_delta(roles: int) -> dict[str, tuple[int, ...]]:
    """Required P-I coefficients for named group elements (others must vanish)."""
    e00 = projector(roles, 0)
    e11 = projector(roles, 1)
    both = mat_add(e00, e11)
    return {
        "e": both,
        "xy": e00,
        "yx": e11,
    }


def prove_xyx_impossible(roles: int, index, table, masks) -> dict:
    """Coefficient analysis of D_A(x) D_B(y) D_C(x) forces a rank-2 'rank-one'."""
    need(roles >= 2, "roles")
    elements = {value: key for key, value in index.items()}
    xy = compose(X, Y)
    yx = compose(Y, X)
    xyx_g = compose(xy, X)
    # Ring terms in P-I = α(A+C) + β B + αβ (AB) + βα (BC) + αβα (ABC).
    term_masks = {
        "U": masks["alpha"],  # U = A+C
        "B": masks["beta"],
        "AB": masks["ab"],
        "BC": masks["ba"],
        "ABC": masks["aba"],
    }
    # Collect which matrix symbols contribute to each group element.
    contrib: dict[tuple[int, ...], list[str]] = {}
    for name, mask in term_masks.items():
        for i in range(60):
            if (mask >> i) & 1:
                contrib.setdefault(elements[i], []).append(name)

    need(contrib[xyx_g] == ["ABC"], "xyx only from ABC")
    need(set(contrib[xy]) == {"AB", "ABC"}, "xy from AB,ABC")
    need(set(contrib[yx]) == {"BC", "ABC"}, "yx from BC,ABC")
    need(set(contrib[IDENTITY]) == {"U", "B", "AB", "BC"}, "[e] contributors")
    need(set(contrib[X]) == {"U", "AB", "BC"}, "[x] contributors")

    required = _target_delta(roles)
    # ABC coefficient of xyx must vanish ⇒ ABC = 0.
    abc = _zero_matrix(roles)
    # Then AB = E00 and BC = E11.
    ab = required["xy"]
    bc = required["yx"]
    # [e]: U + B + AB + BC = E00+E11 ⇒ U+B = 0 ⇒ U = B.
    # [x]: U + AB + BC = 0 ⇒ U = AB+BC = E00+E11.
    u = mat_add(ab, bc)
    b = u
    need(b == required["e"], "forced B equals E00+E11")
    need(rank_f2(b, roles) == 2, "forced B rank 2")
    need(not is_rank_one_idempotent(b, roles), "forced B not rank-one idempotent")
    # Remaining named equations are consistent with these forced matrices.
    need(mat_add(mat_add(ab, abc), required["xy"]) == _zero_matrix(roles), "xy eq")
    need(mat_add(mat_add(bc, abc), required["yx"]) == _zero_matrix(roles), "yx eq")
    need(
        mat_add(mat_add(mat_add(u, b), ab), bc) == required["e"],
        "[e] eq",
    )
    need(mat_add(mat_add(u, ab), bc) == _zero_matrix(roles), "[x] eq")
    return {
        "pattern": "xyx",
        "forced_B": "E00+E11",
        "forced_B_rank": 2,
        "contradiction": "rank_one_idempotent",
        "roles_checked": roles,
        "unique_xyx_carrier": "ABC",
    }


def prove_yxy_impossible(roles: int, index, table, masks) -> dict:
    """Coefficient analysis of D_A(y) D_B(x) D_C(y) forces the same rank clash."""
    need(roles >= 2, "roles")
    elements = {value: key for key, value in index.items()}
    xy = compose(X, Y)
    yx = compose(Y, X)
    yxy_g = compose(yx, Y)
    y2 = compose(Y, Y)
    # P-I terms: β(A+C) + α B + αβ (BC) + β² (AC) + βα (AB) + βαβ (ABC).
    term_masks = {
        "U": masks["beta"],  # U = A+C
        "B": masks["alpha"],
        "BC": masks["ab"],
        "AC": masks["bb"],
        "AB": masks["ba"],
        "ABC": masks["bab"],
    }
    contrib: dict[tuple[int, ...], list[str]] = {}
    for name, mask in term_masks.items():
        for i in range(60):
            if (mask >> i) & 1:
                contrib.setdefault(elements[i], []).append(name)

    need(contrib[yxy_g] == ["ABC"], "yxy only from ABC")
    need(set(contrib[xy]) == {"BC", "ABC"}, "xy carriers")
    need(set(contrib[yx]) == {"AB", "ABC"}, "yx carriers")
    need(set(contrib[y2]) == {"AC", "ABC"}, "y2 carriers")
    need(set(contrib[X]) == {"B", "BC", "AB", "ABC"}, "[x] carriers")

    required = _target_delta(roles)
    abc = _zero_matrix(roles)
    ac = _zero_matrix(roles)  # from y² with ABC=0
    bc = required["xy"]
    ab = required["yx"]
    # [e]: U + B + BC + AC + AB + ABC = E00+E11 ⇒ U+B = 0 ⇒ U=B.
    # [x]: B + BC + AB + ABC = 0 ⇒ B = BC+AB = E00+E11.
    b = mat_add(bc, ab)
    u = b
    need(b == required["e"], "forced B equals E00+E11")
    need(rank_f2(b, roles) == 2, "forced B rank 2")
    need(not is_rank_one_idempotent(b, roles), "forced B not rank-one")
    need(mat_add(mat_add(bc, abc), required["xy"]) == _zero_matrix(roles), "xy eq")
    need(mat_add(mat_add(ab, abc), required["yx"]) == _zero_matrix(roles), "yx eq")
    need(mat_add(ac, abc) == _zero_matrix(roles), "y2 eq")
    need(
        mat_add(
            mat_add(mat_add(mat_add(mat_add(u, b), bc), ac), ab),
            abc,
        )
        == required["e"],
        "[e] eq",
    )
    need(
        mat_add(mat_add(mat_add(b, bc), ab), abc) == _zero_matrix(roles),
        "[x] eq",
    )
    return {
        "pattern": "yxy",
        "forced_B": "E00+E11",
        "forced_B_rank": 2,
        "contradiction": "rank_one_idempotent",
        "roles_checked": roles,
        "unique_yxy_carrier": "ABC",
    }


def finite_controls(elements, index, table) -> dict:
    xy = compose(X, Y)
    yx = compose(Y, X)
    meta = {
        "xy_index": index[xy],
        "yx_index": index[yx],
        "x_index": index[X],
        "y_index": index[Y],
        "identity_index": index[IDENTITY],
    }
    direct_ok = []
    omission_rejects = 0
    for roles in (2, 3, 4, 5):
        got = direct_word(
            roles,
            meta["x_index"],
            meta["y_index"],
            meta["identity_index"],
            table,
        )
        want = target_state(
            roles,
            meta["xy_index"],
            meta["yx_index"],
            meta["identity_index"],
        )
        need(got == want, f"direct word fails at r={roles}")
        direct_ok.append(roles)
        e00 = projector(roles, 0)
        e11 = projector(roles, 1)
        schedule = (
            (meta["x_index"], e00),
            (meta["y_index"], e00),
            (meta["y_index"], e11),
            (meta["x_index"], e11),
        )
        for drop in range(4):
            state = identity_state(roles, meta["identity_index"])
            for i, (label, proj) in enumerate(schedule):
                if i == drop:
                    continue
                state = apply_factor(state, label, proj, roles, table)
            need(state != want, f"omission {drop} unexpectedly hits at r={roles}")
            omission_rejects += 1
    # Rank-one census at small widths (supports the projector language).
    idempotent_counts = {}
    for roles, expected in ((2, 6), (3, 28), (4, 120)):
        count = 0
        for code in range(1 << (roles * roles)):
            matrix = tuple((code >> bit) & 1 for bit in range(roles * roles))
            if is_rank_one_idempotent(matrix, roles):
                count += 1
        need(count == expected, f"idempotent count r={roles}")
        idempotent_counts[str(roles)] = count
    return {
        "direct_word_roles": direct_ok,
        "omission_rejects": omission_rejects,
        "rank_one_idempotent_counts": idempotent_counts,
    }


def build_certificate() -> dict:
    elements, index, table = build_group()
    axioms = group_axioms(elements, index, table)
    xy = compose(X, Y)
    yx = compose(Y, X)
    support = support_exclusion(xy, yx)
    masks = ring_masks(index, table)
    xyx_proof = [prove_xyx_impossible(r, index, table, masks) for r in (2, 3, 4, 5, 8)]
    yxy_proof = [prove_yxy_impossible(r, index, table, masks) for r in (2, 3, 4, 5, 8)]
    controls = finite_controls(elements, index, table)
    pins = source_pin_rows()
    cert = {
        "schema_version": 1,
        "package": "research/a5-conjugate-any-registers",
        "theorem": {
            "statement": (
                "For every finite register width r>=2, in M_r(F2[A5]) with paid "
                "labels {x,y} and every binary rank-one idempotent, the target "
                "diag([xy],[yx],e,...,e) has exact paid-call minimum 4."
            ),
            "exact_minimum_calls": 4,
            "roles": "all finite r>=2",
            "selected_kappa": SELECTED_KAPPA,
            "new_kappa": False,
        },
        "algebra": axioms,
        "support_filter": support,
        "xyx_obstruction": xyx_proof,
        "yxy_obstruction": yxy_proof,
        "finite_controls": controls,
        "source_pins": len(pins),
        "pin_base_commit": "bb4bccbf42844d2801487450727c2f63e10d1d0f",
    }
    return cert


def compare_certificate(fresh: dict, committed: dict) -> None:
    need(fresh == committed, "CERTIFICATE.json drift versus fresh rebuild")


def reject_temp_corruption(cert: dict) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / CERT_NAME
        path.write_text(json.dumps(cert, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        corrupted = json.loads(path.read_text(encoding="utf-8"))
        corrupted["theorem"]["exact_minimum_calls"] = 3
        path.write_text(json.dumps(corrupted, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        try:
            compare_certificate(cert, load_json_reject_duplicates(path))
        except ValueError as exc:
            need("drift" in str(exc), "corruption must be rejected for drift")
        else:
            need(False, "corrupted certificate was accepted")


def verify(write: bool = False) -> dict:
    cert = build_certificate()
    path = PACKAGE / CERT_NAME
    if write:
        path.write_text(json.dumps(cert, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        need(path.is_file(), "missing CERTIFICATE.json")
        committed = load_json_reject_duplicates(path)
        compare_certificate(cert, committed)
        reject_temp_corruption(cert)
        # Read-only: package directory mtime/contents for CERT unchanged path.
        need(path.is_file(), "certificate still present")
    print(
        "PASS_A5_CONJUGATE_ANY_REGISTERS "
        "minimum=4 roles=all_finite_r>=2 "
        "support_patterns=['xyx','yxy'] "
        "forced_B_rank=2 "
        f"direct_roles={cert['finite_controls']['direct_word_roles']} "
        "no_new_kappa"
    )
    return cert


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    verify(write=args.write)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
