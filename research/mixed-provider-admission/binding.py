"""Strict per-call binding added to the inherited PR4085 rebind.

SPDX-License-Identifier: Apache-2.0
Prepared for yssite with substantial OpenAI Codex assistance.
The inherited owner, native, phase, invoice and release checks remain required.
"""
from collections import Counter
import gzip
import hashlib
import json


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def account(plan, roles, dispatch):
    """Recompute complements from actual rows, never an orientation average."""
    order = [tuple(c) for c in plan["order"]]
    need(len(order) == len(set(order)), "duplicate call")
    need(len(dispatch) == len(order), "dispatch row coverage")
    selected = {(s, r): p for s, r, p in dispatch}
    need(len(selected) == len(dispatch) and set(selected) == set(order),
         "dispatch bijection")
    registry = plan["provider_registry"]
    need(set(selected.values()) == set(registry), "complete provider usage")
    counts = {len(d["widths"]) for d in registry.values()}
    need(len(counts) == 1, "common helper count")
    helpers = counts.pop()
    need(helpers > 0 and len(roles) == helpers * len(order), "role coverage")
    calls, widths = plan["provider_calls"], plan["per_call_widths"]
    need(len(calls) == len(widths) == len(order), "call descriptor coverage")
    for t, (stage, replica) in enumerate(order):
        c, w, pid = calls[t], widths[t], selected[stage, replica]
        need((c["stage"], c["replica"], c["time"], c["provider"])
             == (stage, replica, t, pid), "per-call provider binding")
        need(c["orientation"] == ("forward" if stage % 2 == 0 else "backward"),
             "per-call orientation")
        need(c["local_program_sha256"] ==
             registry[pid]["orientation_program_sha256"][c["orientation"]],
             "per-call program binding")
        need((w["stage"], w["replica"], w["time"]) == (stage, replica, t)
             and w["widths"] == registry[pid]["widths"], "per-call width binding")
    windows = {tuple(map(int, k.split(","))): (cap, set(times))
               for k, (cap, times) in plan["windows"].items()}
    used = Counter()
    families = set()
    for j, z in enumerate(roles):
        t, h = divmod(j, helpers)
        stage, replica = order[t]
        pid = selected[stage, replica]
        need((z["time"], z["helper"], z["stage"], z["replica"])
             == (t, h, stage, replica), "ordered role identity")
        owner, child, port = z["owner_replica"], z["child"], z["port"]
        need(all(type(v) is int for v in (owner, child, port, z["offset"], z["width"])),
             "integer owner record")
        need((owner, child) in windows and 0 <= port < 112, "owner bin")
        cap, times = windows[owner, child]
        need(t in times, "strict inherited window")
        width = registry[pid]["widths"][h]
        need(type(width) is int and width > 0 and z["width"] == width,
             "actual selected helper width")
        stream = 2 * plan["pairs"][str(child)] + plan["sides"][str(child)]
        family = 896 * owner + 112 * stream + port
        need(z["family"] == family and z["copy"] == 112 * owner + port,
             "physical family binding")
        if h == 0:
            families = set()
        need(family not in families, "same-call family alias")
        families.add(family)
        key = owner, child, port
        need(z["offset"] == used[key] and used[key] + width <= cap,
             "compact per-call residual prefix")
        used[key] += width
    idle = Counter()
    for (owner, child), (cap, _) in windows.items():
        for port in range(112):
            left = cap - used[owner, child, port]
            need(left >= 0, "negative idle remainder")
            if left:
                idle[left] += 1
    total = Counter(idle)
    for call in order:
        total.update({int(r): n for r, n in
                      registry[selected[call]]["actual_paid_profile"].items()})
    return dict(sorted(idle.items())), dict(sorted(total.items()))


def validate_rebind(pkg, plan, locs):
    contract = read(pkg / "new/MIXED-CONTRACT.json")
    need(set(locs) == set(plan["provider_registry"]) == set(contract["providers"]),
         "complete four-provider binding")
    for pid, source in contract["providers"].items():
        word = pkg / source["word"]
        need(sha(word) == source["word_sha256"], "provider source changed")
        full = read(locs[pid] / "FULL-WORD.json.gz")
        need(full == read(word), "native source word")
        canonical = read(locs[pid] / "CANONICAL-WORD.json.gz")
        widths = [len(canonical["frames"][canonical["final"][r]])
                  - len(canonical["frames"][canonical["start"][r]])
                  for r in range(224, 224 + canonical["R"])]
        desc = plan["provider_registry"][pid]
        need(widths == source["widths"] == desc["widths"], "native selected widths")
        checks = read(locs[pid] / "LOCAL-CHECKS.json")
        need(all(checks[o]["paid_profile"] == source["profile"]
                 == desc["actual_paid_profile"] for o in ("forward", "backward")),
             "both orientation paid profiles")
    dispatch = read(pkg / "DISPATCH.json")
    # The inherited reconstructor serializes in chronological order; the input
    # table's row order is immaterial. account() separately requires a bijection
    # and binds every chronological call, width and orientation program.
    need(sorted(dispatch) == sorted(contract["dispatch"]), "literal mixed selector")
    idle, total = account(plan, read(pkg / "OWNERS.json.gz"), dispatch)
    need(idle == {int(k): v for k, v in read(pkg / "CONSTRUCTION.json")["idle"].items()},
         "stale construction idle")
    need(total == {int(k): v for k, v in plan["profile"].items()},
         "complete mixed paid profile")
    return idle
