# SPDX-License-Identifier: Apache-2.0
"""Bounded preconditioning checks, with the missing corrector kept explicit."""
from fractions import Fraction as Q
from hashlib import sha256
import gzip
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bindings import authenticate, canonical, module, need
from boundary import (SOURCE, TARGET, bridge, channel_rows, conditional_completion,
                      correction, physical_sources)


def run():
    raw = authenticate()
    pooled = module(raw, "credited_p104_pooled", "research/p104-pooled-cut-independent/verify.py")
    native = module(raw, "credited_p104_native", "research/p104-native-channel/vendor/native_verify.py")
    cert, word, fixture = pooled.load_inputs()
    receipt = pooled.replay(False)
    need(receipt == json.loads(raw["research/p104-pooled-cut-independent/RESULT.json"]), "complete pooled source receipt")
    need(sha256(canonical(receipt)).hexdigest() ==
         "462227d245f3932d56aafc5ba5a81aedc0d26fcef8b3c2a4b1ed673c7c5e329a", "canonical pooled receipt")
    _, gram_half, old = correction(fixture)
    available = [int(row, 16) for row in receipt["output_masks"]]
    missing = [(i, j, value) for i, row in enumerate(old) for j, value in enumerate(row)
               if value and not available[i] >> j & 1]
    need(missing == [(TARGET, SOURCE, Q(-1, 2))], "entire unsupported nonzero correction")
    corrected = tuple(tuple(0 if (i, j) == (TARGET, SOURCE) else value for j, value in enumerate(row))
                      for i, row in enumerate(old))
    need(sum(bool(value) for row in corrected for value in row) == 4991 and
         all(not value or available[i] >> j & 1 for i, row in enumerate(corrected) for j, value in enumerate(row)),
         "changed correction passes only the pooled necessary support test")
    conditional_completion(gram_half, corrected)
    state = channel_rows(word)
    expected_changed = 0
    for name, row in state.items():
        expected = {name: Q(1)}
        if name == "X71":
            expected["X102"] = Q(-1, 2)
        elif name.startswith("Y"):
            index = int(name[1:])
            for source, coefficient in enumerate(gram_half[index]):
                value = coefficient - (gram_half[index][TARGET] / 2 if source == SOURCE else 0)
                if value:
                    expected["X" + str(source)] = value
            expected_changed += int(bool(gram_half[index][TARGET]))
        need(row == expected, "complete preconditioned channel endpoint: " + name)
    need(all(word["final_frames"]["X" + str(i)] == word["final_frames"]["X0"] for i in range(104)),
         "common final source frame for scalar restoration")
    native_data = json.loads(gzip.decompress(raw["research/p104-native-channel/NATIVE-RECIPES.json.gz"]))
    masks, entries = physical_sources(native_data, word, fixture, native)
    tensors = []
    digest = sha256()
    for columns in (1, 2, 3):
        actual, expected = bridge(native, masks, columns)
        need(len(native.state(actual)[0]) == 1 << (2 * columns), "support-spread standalone rank control")
        tensors.append(dict(columns=columns, paid_rank=2 * columns, nonzero_column_entries=1 << (2 * columns)))
        if columns == 1:
            for column in range(512):
                value = native.state(actual, column)
                need(value == native.state(expected, column), "all native source-bridge basis columns")
                digest.update(canonical([sorted(value[0].items()), value[1]]))
            native.equal((("C", masks[1], 1),) + actual, (("C", masks[0], 1),), "source preconditioning transport")
            adapted = native.adjoint(native.recipe(entries[1]["recipe"])) + actual + native.recipe(entries[0]["recipe"])
            native.equal(adapted, native.adjoint(native.frame((masks[1],), 9)) + native.frame((masks[0],), 9),
                         "same boundary after canonical entry adapters")
    controls = []
    for label, arguments in (("old_correction", (gram_half, old)),
                             ("wrong_shear_sign", (gram_half, corrected, Q(1, 2))),
                             ("missing_source_restore", (gram_half, corrected, Q(-1, 2), False))):
        try:
            conditional_completion(*arguments)
        except ValueError:
            controls.append(label)
        else:
            raise ValueError("accepted boundary corruption: " + label)
    try:
        wrong, _ = bridge(native, (22, 415))
        expected = native.adjoint((("C", 296, 1),)) + (("C", 121, 1),)
        native.equal(wrong, expected, "raw compressed labels are not physical masks")
    except ValueError:
        controls.append("compressed_physical_confusion")
    else:
        raise ValueError("accepted raw compressed physical coordinates")
    return dict(status="PASS_P104_SOURCE_PRECONDITIONING_BOUNDARY", missing_old=[[TARGET, SOURCE, "-1/2"]],
                required_after=4991, simultaneous_corrector_constructed=False,
                channel_input_columns=280, changed_channel_target_rows=expected_changed,
                physical_masks=masks, native_columns=512, tensor_controls=tensors,
                bridge_sha256=digest.hexdigest(), controls=controls,
                added_forward_children={2: 1}, source_restoration="one scalar ADD at common FULL after last correction read",
                scope="Exact native boundary and conditional completion algebra; no coefficient/flag/hosting/dual supplier admission.")


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
