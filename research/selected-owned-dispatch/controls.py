"""Mutations target the actual codec and continuation execution, not receipts."""
import json
from pathlib import Path
import prototype as p

def rejects(name, patch, restore):
    patch()
    try:
        p.interior_blank_roundtrip()
        p.fixture(9, 2, 2, 17)
    except (ValueError, AssertionError) as exc:
        result = {'mutation': name, 'rejected': True, 'reason': str(exc)}
    else:
        raise RuntimeError('mutation unexpectedly accepted: ' + name)
    finally:
        restore()
    return result

original_write = p.CodedQueryTape.write
def physical_blank(self, value):
    if value == p.q.BLANK:
        for _ in range(3):
            p.s.emit(self.tape, p.s.BLANK)
        p.moves(self.tape, -1)
    else:
        original_write(self, value)

original_return = p.r.return_output
def omit_output(payloads, control, descriptor, relay, child_slot, parent_slot):
    for tape in payloads:
        p.r.retire(tape)
    return p.s.Stack(payloads, control, descriptor).pop()

def alias_parent_z(payloads, control, descriptor, relay, child_slot, parent_slot):
    return original_return(payloads, control, descriptor, relay, child_slot, p.q.Z)

original_ascend = p.Dispatcher.ascend
def wrong_resume(self):
    original_ascend(self)
    # A real source-bit error in the resumed child-output field, before ADD.
    self.ports[p.q.Z].write(1)

def missing_return_clear(self):
    old = p.clear
    def skip_return_role(tape, marker=p.s.LEFT):
        if tape is not self.payloads[8]:
            old(tape, marker)
    p.clear = skip_return_role
    try:
        original_ascend(self)
    finally:
        p.clear = old

def wrong_phase(payloads, control, descriptor, relay, child_slot, parent_slot):
    state = original_return(payloads, control, descriptor, relay, child_slot, parent_slot)
    descriptor.write(0)
    return state

def run_checks():
    results = []
    results.append(rejects('logical_blank_as_physical_delimiter',
        lambda: setattr(p.CodedQueryTape, 'write', physical_blank),
        lambda: setattr(p.CodedQueryTape, 'write', original_write)))
    results.append(rejects('destroy_child_before_output_copy',
        lambda: setattr(p.r, 'return_output', omit_output),
        lambda: setattr(p.r, 'return_output', original_return)))
    results.append(rejects('alias_empty_return_role_with_occupied_parent_z',
        lambda: setattr(p.r, 'return_output', alias_parent_z),
        lambda: setattr(p.r, 'return_output', original_return)))
    results.append(rejects('corrupt_resumed_child_output',
        lambda: setattr(p.Dispatcher, 'ascend', wrong_resume),
        lambda: setattr(p.Dispatcher, 'ascend', original_ascend)))
    results.append(rejects('omit_return_role_retirement',
        lambda: setattr(p.Dispatcher, 'ascend', missing_return_clear),
        lambda: setattr(p.Dispatcher, 'ascend', original_ascend)))
    results.append(rejects('wrong_physical_resume_phase',
        lambda: setattr(p.r, 'return_output', wrong_phase),
        lambda: setattr(p.r, 'return_output', original_return)))
    return results

if __name__ == "__main__":
    print(json.dumps(run_checks(), indent=2))
