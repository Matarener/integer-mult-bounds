#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Replay PR3934's and PR3955's literal idle-axis moves with PR3187's exact eight-stream operator.

PR3934 (hosted receivers) and PR3955 (hosted frame selection) supply the complex root used by
PR3939, PR3958 and PR3959. This verifier checks:

1. inclusion: every move of the retracted PR3251 is in PR3934, and PR3934 and PR3955 both contain
   PR3296's port-0 witness moves;
2. hosted receivers: each of PR3934's 2,374 moves outside PR3251, applied alone at its own
   (owner replica, port), changes the exact operator at its moved-axis character;
3. frame selection: at owner replica 0, every PR3955 port whose donated axes all lie in the literal
   remainders (identity selection) changes the exact operator; other ports are counted, not replayed.

The operator model, fill authentication and data events are PR3187's (Nick Petalas) and the per-port
projection, remainders and declared rule are PR3296's (Matarener), imported unchanged. The only new
code path is the owner-replica index, which PR3296 fixes at 0.

--write regenerates RESULT.json instead of comparing with it.
"""
import argparse
import gzip
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "pr3190-remainder-stream-obstruction"))
sys.path.insert(0, str(HERE.parent / "rank7-idle-star-stream-obstruction"))
import obstruction as O  # noqa: E402

S, A = O.S, O.A
COLUMNS = ["replica", "port", "donor_child", "receiver_child", "axis"]
PINS = {
    "PR3251": ("ec9c11b924e4ab9de4f66cb42cc914fb7eb8c80c0f16f7a34d1dcf51f73ad52e", 435604),
    "PR3934": ("173c83d34d4922584da0a8acdb429c29e0ad3e4a7960fb4de05bfec4848c9249", 437978),
    "PR3955": ("01e8417b90783f707cd18871be7c615eb9162f356460f07963b5198522aa692b", 521798),
}
WITNESS = [(0, 0, 14, 8, O.AXIS72), (0, 0, 15, 10, O.AXIS72)]


def load(name):
    raw = S.read_bytes(HERE / "vendor" / (name + "-MOVES.json.gz"))
    sha, count = PINS[name]
    S.require(hashlib.sha256(raw).hexdigest() == sha, name + " MOVES pin")
    data = json.loads(gzip.decompress(raw))
    S.require(data["columns"] == COLUMNS and len(data["moves"]) == count, name + " MOVES shape")
    return [(r, p, d, c, int(a)) for r, p, d, c, a in data["moves"]]


def owner_rows(owners):
    """PR3296's fill projection, for a set of owner replicas instead of owner 0 only."""
    vendor = S.PACKAGE / "vendor"
    base = S.decode(S.read_bytes(vendor / "BASE-FILL.json.gz"))["rows"]
    edits = S.journal_edits(base, S.decode(S.read_bytes(vendor / "EXCHANGE.json")))
    rows = defaultdict(list)
    for index in range(S.TOTAL_ROWS):
        row = edits[index] if index in edits else S.lifted_row(base, index)
        if row[2] in owners:
            rows[row[2], row[4]].append(row)
    return rows


def replay(ctx, blocks, hosts, residual, character, owner):
    """O.replay with the owner's own data events instead of replica 0's."""
    matrix = A.identity()
    for time, (stage, replica) in enumerate(ctx["order"]):
        for stream, axes in hosts.get(time, ()):
            A.phase(matrix, stream, sum(A.dot(character, v) for v in axes))
        if replica == owner:
            for event in blocks[stage]:
                A.data_event(matrix, event, ctx, residual, character)
    return matrix


def changed_entries(ctx, blocks, moves, owner):
    residual, hosts = O.residual_and_hosts(ctx)
    final = O.apply_moves(ctx["recipe"], residual, moves)
    out = {}
    for character in sorted({axis for _, _, axis in moves}):
        before = replay(ctx, blocks, hosts, residual, character, owner)
        S.require(before == O.scalar(character), "baseline equals the scalar operator")
        out[character.bit_length() - 1] = len(O.diff(before, replay(ctx, blocks, hosts, final, character, owner)))
    return out, residual, hosts


def rejected(f):
    try:
        f()
    except ValueError as error:
        return "rejected: " + str(error)
    raise AssertionError("control accepted")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    pr3251, pr3934, pr3955 = load("PR3251"), load("PR3934"), load("PR3955")
    set3251, set3934, set3955 = set(pr3251), set(pr3934), set(pr3955)
    new3934 = [m for m in pr3934 if m not in set3251]
    S.require(set3251 <= set3934, "PR3934 contains every PR3251 move")
    S.require(all(m in set3934 and m in set3955 for m in WITNESS), "PR3934 and PR3955 contain PR3296's witness")
    inclusion = dict(pr3251_moves=len(pr3251), pr3251_in_pr3934=len(set3251 & set3934), pr3934_new_moves=len(new3934),
                     pr3251_in_pr3955=len(set3251 & set3955), witness_in_pr3934=True, witness_in_pr3955=True)

    ctx0, rows0, recipes = O.contexts()
    blocks = A.stage_blocks(ctx0["template"])
    groups = defaultdict(list)
    for owner, port, donor, receiver, axis in new3934:
        groups[owner, port].append((donor, receiver, axis))
    rows = owner_rows({owner for owner, _ in groups})

    def context(owner, port):
        return dict(ctx0, rows=rows0[port] if owner == 0 else rows[owner, port], recipe=recipes[port])

    # Positive control of the owner generalization: PR3296's port-0 witness.
    witness, _, _ = changed_entries(context(0, 0), blocks, [m[2:] for m in WITNESS], 0)
    S.require(witness == {72: 10}, "owner-0 port-0 witness equals PR3296 RESULT.json (10 entries at 2^72)")

    hosted_receivers, entries, per_owner, preserved = 0, Counter(), Counter(), []
    first = None
    for (owner, port), moves in sorted(groups.items()):
        ctx = context(owner, port)
        result, residual, hosts = changed_entries(ctx, blocks, moves, owner)
        full = [len(e["orthogonal_axes"]) for e in ctx["recipe"]["idle_children"]]
        hosted_receivers += sum(len(residual[r]) < full[r] for _, r, _ in moves)
        entries.update(result.values())
        per_owner[owner] += len(moves)
        if not all(result.values()):
            preserved.append([owner, port])
        if first is None:
            first = (owner, port, ctx, moves, residual, hosts)
    S.require(sum(per_owner.values()) == len(new3934), "every new PR3934 move replayed")
    S.require(not preserved, "every new PR3934 move changes the exact operator")

    # Controls on the first non-zero-owner configuration. The scalar baseline does not depend on the owner
    # index (replaying another replica's data events also gives it), so it is not used as an owner control.
    owner, port, ctx, moves, residual, hosts = first
    character = moves[0][2]
    before = replay(ctx, blocks, hosts, residual, character, owner)
    controls = dict(
        empty_overlay_preserves_operator="PASS" if replay(
            ctx, blocks, hosts, O.apply_moves(ctx["recipe"], residual, []), character, owner) == before else "FAIL",
        axis_not_in_donor_remainder=rejected(lambda: O.apply_moves(
            ctx["recipe"], residual, [(moves[0][0], moves[0][1], 1 << 200)])),
        self_move=rejected(lambda: O.apply_moves(ctx["recipe"], residual, [(moves[0][0], moves[0][0], character)])),
    )
    S.require(owner != 0 and all(v != "FAIL" for v in controls.values()), "controls")

    # PR3955 at owner replica 0.
    by_port = defaultdict(list)
    for owner0, port0, donor, receiver, axis in pr3955:
        if owner0 == 0:
            by_port[port0].append((donor, receiver, axis))
    identity, reselected, unchanged = [], [], []
    for port0, moves0 in sorted(by_port.items()):
        ctx = context(0, port0)
        residual, _ = O.residual_and_hosts(ctx)
        if not all(axis in residual[donor] for donor, _, axis in moves0):
            reselected.append(port0)
            continue
        identity.append(port0)
        result, _, _ = changed_entries(ctx, blocks, moves0, 0)
        if not all(result.values()):
            unchanged.append(port0)
    S.require(not unchanged, "every identity-selection PR3955 port changes the exact operator")

    got = dict(
        status="PASS_PR3934_PR3955_OPERATOR_REPLAY", admitted=False, selected_frontier_changed=False, new_kappa=False,
        inclusion=inclusion, owner0_port0_witness_entries={"72": 10},
        pr3934_hosted_receivers=dict(moves=len(new3934), configurations=len(groups), owners=len(per_owner),
                                     moves_into_hosted_receivers=hosted_receivers, preserved_configurations=preserved,
                                     changed_entries_histogram={str(k): v for k, v in sorted(entries.items())}),
        controls=controls, controls_owner_port=[owner, port],
        pr3955_owner0=dict(ports_with_moves=len(by_port), identity_selection_ports=len(identity),
                           identity_ports_changed=len(identity) - len(unchanged), reselected_ports_not_replayed=len(reselected)),
    )
    path = HERE / "RESULT.json"
    if args.write:
        path.write_text(json.dumps(got, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    S.require(json.loads(json.dumps(got)) == json.loads(path.read_text(encoding="utf-8")), "recomputed result differs from RESULT.json")
    print("PASS_PR3934_PR3955_OPERATOR_REPLAY hosted_receiver_moves=%d changed=%d pr3955_owner0_identity_ports=%d changed=%d no_new_kappa"
          % (len(new3934), len(new3934), len(identity), len(identity) - len(unchanged)))


if __name__ == "__main__":
    main()
