"""Source binding and observer audit of the literal dense guard-mask program.

Geometry-to-stencil construction/admission and source-oracle computations below
are host adapters, explicitly OUTSIDE the transducer's machine tariff.
"""

import argparse
import hashlib
import json
from pathlib import Path
import sys
import types


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def load_bytes(name, data, path):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(data, str(path), "exec"), module.__dict__)
    return module


def admit_stencil(cells, machine):
    """Host admission only, not a claimed tape implementation or charged step."""
    need(len(cells) >= 1, "nonempty stencil")
    active = None
    for atom in cells:
        need(type(atom) is tuple and len(atom) == 5, "fixed product alphabet")
        kind, begin, end, lo, hi = atom
        need(kind in ("S", "D", "G") and type(begin) is bool and type(end) is bool
             and lo in ("0", "1") and hi in ("0", "1"), "finite alphabet atom")
        if kind == "S":
            need(atom == machine.SKIP and active is None, "skip outside intervals")
            continue
        if begin:
            need(active is None, "nonoverlapping ordered interval start")
            active = kind
        else:
            need(active == kind, "interval continuation")
        if kind == "D":
            need(lo == hi == "0", "digit has no threshold data")
        if end:
            active = None
    need(active is None, "complete intervals")
    return cells


def geometry_stencil(g, h, ybits, targets, k, back_bits, machine, include_parity=False):
    """Unpriced source-binding adapter; preserves all unspecified bits as SKIP."""
    targets = tuple(targets)
    need(all(type(v) is int for v in (g, h, ybits, k, back_bits)), "integer geometry")
    need(g >= 1 and targets and h >= len(targets) * g and k >= g + 4 and back_bits >= 0,
         "admissible compact/guard widths")
    need(all(type(j) is int and 0 <= j and j + k <= ybits for j in targets), "complete target intervals")
    intervals = sorted((j, j + k) for j in targets)
    need(all(a[1] <= b[0] for a, b in zip(intervals, intervals[1:])), "disjoint target intervals")
    length = 2 * h + ybits + back_bits
    cells = [machine.SKIP] * length

    def place(lo, hi, kind, low=0, high=0):
        width = hi - lo
        low_bits = format(low, "0%db" % width)
        high_bits = format(high, "0%db" % width)
        need(width >= 1 and len(low_bits) == len(high_bits) == width, "fixed threshold widths")
        for offset, position in enumerate(range(lo, hi)):
            need(cells[position] == machine.SKIP, "no overlapping stencil cells")
            cells[position] = (kind, offset == 0, offset == width - 1,
                               low_bits[offset], high_bits[offset])

    for field_start in (0, h):
        for digit in range(len(targets)):
            place(field_start + h - (digit + 1) * g, field_start + h - digit * g, "D")
    for j in targets:
        # The source compares K-1 HIGHER guard bits, excluding parity bit j.
        start = 2 * h + ybits - j - k
        stop = 2 * h + ybits - j - (0 if include_parity else 1)
        place(start, stop, "G", 1 << (g + 1), (1 << (k - 1)) - (1 << (g + 1)))
    return admit_stencil(cells, machine)


def audit(cells, machine, **mutant):
    """Observer integers are not read by the literal transducer."""
    admit_stencil(cells, machine)
    stencil = machine.Tape([machine.LEFT] + cells + [machine.END])
    original = list(stencil.cells)
    counter, mask = machine.transduce(stencil, **mutant)
    length, records = len(cells), 1 << len(cells)
    need(stencil.cells == original, "protected stencil unchanged")
    need(counter.head == stencil.head == 0, "private/input heads returned")
    need(counter.cells[0] == machine.LEFT and all(c == machine.BLANK for c in counter.cells[1:]),
         "private counter restored to blank data, including right marker")
    need(mask.cells[0] == machine.LEFT and mask.cells[-1] == machine.END,
         "owned output markers")
    bits = "".join(mask.cells[1:-1])
    need(len(bits) == records and all(bit in "01" for bit in bits), "one BAD bit per complete address")
    actions = sum(t.actions for t in (stencil, counter, mask))
    if not mutant:
        need(mask.head == 0, "owned output head returned")
        need(actions == 8 * records * length + 15 * records + 13 * length + 18,
             "derived exact marker/counter/cleanup action census")
        need(sum(len(t.cells) for t in (stencil, counter, mask)) == records + 2 * length + 6,
             "derived exact three-role visited space")
    return bits, {"address_bits": length, "addresses": records,
                  "good_addresses": bits.count("0"), "bad_addresses": bits.count("1"),
                  "read_actions": sum(t.reads for t in (stencil, counter, mask)),
                  "write_actions": sum(t.writes for t in (stencil, counter, mask)),
                  "move_actions": sum(t.moves for t in (stencil, counter, mask)),
                  "total_cell_head_actions": actions,
                  "visited_cells_including_owned_mask": sum(len(t.cells) for t in (stencil, counter, mask)),
                  "heads_returned": mask.head == counter.head == stencil.head == 0,
                  "private_data_blank": True,
                  "mask_semantics": "1=bad, 0=good; increasing MSB-first binary address",
                  "mask_ascii_sha256": hashlib.sha256(bits.encode()).hexdigest()}


def fixture(name, g, h, ybits, targets, k, back_bits, source, machine):
    cells = geometry_stencil(g, h, ybits, targets, k, back_bits, machine)
    mask, receipt = audit(cells, machine)
    for address, bit in enumerate(mask):
        y = (address >> back_bits) & ((1 << ybits) - 1)
        t = (address >> (ybits + back_bits)) & ((1 << h) - 1)
        u = address >> (h + ybits + back_bits)
        expected = source.good(u, t, y, bits=g, positions=targets, guard=k)
        linear = source.linear_guard(u, t, y, bits=g, positions=targets, guard=k,
                                     control_bits=h, ybits=ybits)
        need(expected == linear == (bit == "0"), "literal mask equals exact source predicates on every address")
    receipt.update({"name": name, "G": g, "H": h, "Y_bits": ybits,
                    "targets": list(targets), "K": k, "back_skip_bits": back_bits,
                    "domain": "predicate projection/stencil fixture, not a full production reservoir invocation"})
    return receipt, cells, mask


def must_reject(call, label):
    try:
        call()
    except ValueError:
        return label
    raise ValueError("admission control accepted: " + label)


def controls(machine):
    cells = geometry_stencil(1, 1, 5, (0,), 5, 0, machine)
    right, _ = audit(cells, machine)
    mutants = []
    for name, kwargs in (("lower threshold incorrectly strict", {"lower_strict": True}),
                         ("upper threshold incorrectly inclusive", {"upper_inclusive": True}),
                         ("last differing bit overrides MSB significance", {"last_difference_wins": True})):
        wrong, _ = audit(cells, machine, **kwargs)
        different = next((i for i, (a, b) in enumerate(zip(right, wrong)) if a != b), None)
        need(different is not None, "semantic mutant differs: " + name)
        mutants.append({"name": name, "address": different,
                        "correct_bad_bit": right[different], "wrong_bad_bit": wrong[different]})
    wrong_cells = geometry_stencil(1, 1, 5, (0,), 5, 0, machine, include_parity=True)
    wrong, _ = audit(wrong_cells, machine)
    different = next(i for i, (a, b) in enumerate(zip(right, wrong)) if a != b)
    mutants.append({"name": "whole K-bit segment compared to unadjusted K-1-bit thresholds",
                    "address": different, "correct_bad_bit": right[different], "wrong_bad_bit": wrong[different]})
    _, missing_return = audit(cells, machine, omit_output_return=True)
    need(not missing_return["heads_returned"], "missing owned-mask return detected")
    return {"semantic_mutants": mutants, "ownership_mutants": ["owned mask head return omitted"],
            "counter_mutants": [must_reject(lambda: audit(cells, machine, skip_low_counter_bit=True),
                                            "least significant counter bit omitted")],
            "unpriced_adapter_rejections": [
                must_reject(lambda: admit_stencil([], machine), "empty stencil"),
                must_reject(lambda: admit_stencil([("D", False, True, "0", "0")], machine), "missing interval start"),
                must_reject(lambda: admit_stencil([("G", True, False, "0", "1")], machine), "missing interval end"),
                must_reject(lambda: geometry_stencil(1, 2, 10, (0, 4), 5, 0, machine), "overlapping source guards"),
                must_reject(lambda: geometry_stencil(1, 1, 4, (0,), 5, 0, machine), "incomplete source guard"),
            ]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args()
    pins = json.loads((PACKAGE / "SOURCE-PINS.json").read_text())
    authenticated = {}
    for row in pins:
        data = (ROOT / row["path"]).read_bytes()
        need(hashlib.sha256(data).hexdigest() == row["sha256"], "source SHA256: " + row["path"])
        need(hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest() == row["git_blob"],
             "source Git blob: " + row["path"])
        authenticated[row["path"]] = data
    path = "research/unconditional-batched-crt/check_batched_crt.py"
    source = load_bytes("_guard_source", authenticated[path], ROOT / path)
    machine = load_bytes("_literal_guard_machine", (PACKAGE / "machine.py").read_bytes(), PACKAGE / "machine.py")
    rows = []
    for name, g, h, y, targets, k, w in (
            ("two_target_complete", 1, 2, 10, (0, 5), 5, 0),
            ("inactive_digits_and_Y_spectators", 2, 3, 9, (1,), 7, 0),
            ("one_target_with_back_spectator", 1, 1, 5, (0,), 5, 1)):
        receipt, _, _ = fixture(name, g, h, y, targets, k, w, source, machine)
        rows.append(receipt)
    all_skip = []
    for length in (1, 2, 3):
        mask, receipt = audit([machine.SKIP] * length, machine)
        need(set(mask) == {"0"}, "all-skip stencil accepts every address")
        all_skip.append(receipt)
    result = {"schema_version": 1, "result": "PASS_LITERAL_DENSE_GUARD_MASK",
              "base_commit": "12fa8c5c844be21bfefb38a19503fbd867a11244", "source_inputs_checked": len(authenticated),
              "fixtures": rows, "all_skip_boundaries": all_skip, "negative_controls": controls(machine),
              "limitations": ["Literal transducer starts from admitted ordered finite-alphabet stencil.",
                              "Geometry/stencil generation and admission are unpriced host adapters, not discharged tape obligations.",
                              "Observer integers, hashes and source comparisons are outside runtime finite control.",
                              "No source/E callback exists in the detector interface; keyed work is outside it.",
                              "No extraction/sort/repair/payload movement, full CRT evaluator or new kappa."]}
    output = PACKAGE / "RESULT.json"
    if args.write_result:
        output.write_text(json.dumps(result, indent=2) + "\n")
    else:
        need(json.loads(output.read_text()) == result, "stored receipt differs from replay")
    print(json.dumps({"result": result["result"], "source_addresses": sum(r["addresses"] for r in rows),
                      "tape_actions": sum(r["total_cell_head_actions"] for r in rows)}, sort_keys=True))


if __name__ == "__main__":
    main()
