# SPDX-License-Identifier: Apache-2.0
"""Exercise actual complete local groups for both providers and orientations."""
from hashlib import sha256
import json
from pathlib import Path

from binding import T74Binding
from bundles import authenticate_prepared
from compile_word import canonical, need
from cover import multiply


def run(prepared):
    prepared = Path(prepared)
    # Same shape and rank; a changed exact global phase must fail before use.
    path = prepared / "bound/base/providers/gauge44/CLIFFORD-RECIPES.json"
    original = path.read_bytes()
    damaged = json.loads(original)
    warp = damaged["warps"][0]["left"]
    warp["phase"] = (warp["phase"] + 1) % 4
    try:
        path.write_bytes(canonical(damaged))
        try:
            authenticate_prepared(prepared)
        except ValueError as error:
            need(str(error).startswith("frozen T74 input:"), "specific source-drift rejection")
        else:
            raise ValueError("accepted changed native warp phase")
    finally:
        path.write_bytes(original)
    binding = T74Binding(prepared)
    identity = tuple(1 << i for i in range(73))
    label = binding.cover.rank(identity)
    seen, receipts = set(), []
    permitted = {"child", "copy", "identity", "marker", "monomial", "release_zero", "scalar", "zero"}
    for index, event in enumerate(binding.events):
        if event["kind"] != "local_cover_sweep":
            continue
        call = binding.calls[event["time"]]
        key = call["provider_id"], call["orientation"]
        if key in seen:
            continue
        group = binding.group(index, 0, label)
        owners = binding.owner_specs[call["time"]]
        need(len(group.keys) == len(owners) == 632, "complete source-local owner group")
        for physical, owner in zip(group.keys, owners):
            need(physical[0] == owner.family and binding.cover.unrank(physical[1]) ==
                 multiply(identity, owner.sigma_columns), "actual physical owner selector")
        need(set(op[0] for op in group.code) <= permitted, "implemented T74 group alphabet")
        for op in group.code:
            if op[0] != "marker":
                need(type(op[2]) is int and 0 <= op[2] < 731, "actual physical packet operand")
            if op[0] == "monomial":
                need(op[3] in group.recipes, "closed monomial reference")
            if op[0] == "release_zero":
                need(640 <= op[2] < 731, "release addresses only a private Z")
        receipts.append(dict(provider=key[0], orientation=key[1], event=index, owners=len(owners),
                             instructions=len(group.code), sha256=sha256(canonical(group.code)).hexdigest()))
        seen.add(key)
        if len(seen) == 4:
            break
    need(seen == {(pid, direction) for pid in ("gauge44", "extra") for direction in ("forward", "backward")},
         "all dispatch variants exercised")
    # A final correction is expressed in output coordinates, not multiplied by g again.
    factors = [tuple((1 << i) ^ (v if v >> i & 1 else 0) for i in range(73)) for v in (15, 30)]
    g = multiply(*factors)
    final = binding.group(len(binding.events)-1, 0, binding.cover.rank(g))
    mask = sum((((row.bit_count()-1)//2) & 1) << i for i, row in enumerate(g))
    need(len(final.code) == 1 and final.recipes[final.code[0][3]]["offset"] == mask,
         "complete changed controller final correction")
    return dict(status="PASS_T74_COMPLETE_DISPATCH_VARIANTS", groups=receipts,
                final_output_mask=mask, changed_warp_phase_rejected=True,
                scope="Complete local group selectors and instructions at one cover, source-drift rejection and a nontrivial final correction; no full O73 numerical payload.")
