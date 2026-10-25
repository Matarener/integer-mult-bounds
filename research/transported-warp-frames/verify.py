"""Git-free exact recipe replay. Native phases have a separate fresh-run command."""
import gzip
import hashlib
import json
from pathlib import Path
import sys
from frames import audit, compile_frames, need

HERE = Path(__file__).resolve().parent


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load_inputs(root=HERE):
    pins = json.loads((root / 'INPUTS.json').read_text())
    for name, expected in pins.items():
        need(digest((root / name).read_bytes()) == expected, 'input hash: ' + name)
    source = json.loads(gzip.decompress((root / 'inputs/BASE-WORD.json.gz').read_bytes()))
    recipe = json.loads((root / 'inputs/RECIPE.json').read_text())
    target = json.loads((root / 'inputs/REFRAMED-WORD.json').read_text())
    return source, recipe, target


def check(w, full=True):
    audit.hygiene(w)
    profile, inventory, _, _, _ = audit.frame_bill(w, lagrangian=True)
    need({str(k): v for k, v in profile.items()} == w['report']['local_profile'], 'profile mismatch')
    need({str(k): v for k, v in inventory.items()} == w['report']['width_inventory'], 'inventory mismatch')
    if full:
        need(audit.endpoint_defects(w, audit.forward_rows(w, symbolic_buffers=True)) == ([], [], [], True), 'forward endpoint')
        need(audit.endpoint_defects(w, audit.forward_rows(w, dual=True, symbolic_buffers=True), dual=True) == ([], [], [], True), 'dual endpoint')
        need(not audit.boundary_defects(w, audit.transpose(audit.reverse_columns(w, upto_cleanup=True))), 'cleanup boundary')
    return profile, inventory


def main():
    source, recipe, target = load_inputs()
    got = compile_frames(source, recipe)
    need(got == target, 'compiler does not reproduce the frozen native-audited word')
    old, inv = check(source, full=False)
    profile, new_inv = check(got)
    need(inv == new_inv, 'helper inventory changed')
    delta = {r: profile.get(r, 0) - old.get(r, 0) for r in sorted(set(old) | set(profile))}
    need(sum(r * n for r, n in delta.items()) == 0, 'rank mass changed')
    receipt = json.loads((HERE / 'evidence/NATIVE.json').read_text())
    need(receipt['word_sha256'] == digest((HERE / 'inputs/REFRAMED-WORD.json').read_bytes()), 'native receipt input')
    need(receipt['status'] == 'PASS_COMPLETE_T74_NATIVE_REPLAY', 'native receipt status')
    actual_native = {p.relative_to(HERE / 'native/vendor').as_posix(): digest(p.read_bytes())
                     for p in (HERE / 'native/vendor').rglob('*') if p.is_file()}
    need(receipt['source_sha256'] == actual_native, 'native receipt source closure')
    need([s['step'] for s in receipt['steps']] == ['native', 'ledgers', 'local-replay', 'wrappers', 'phases'] and all(s['exit_code'] == 0 for s in receipt['steps']), 'native receipt stages')
    # A receipt is provenance; this command does not rerun its phase calculations.
    result = {'status': 'PASS_TRANSPORTED_FRAME_RECIPE', 'profile': profile,
              'profile_delta': delta, 'inventory': inv, 'new_kappa': None,
              'scope': 'Fresh exact frame, lifted-action, forward, dual and cleanup-boundary checks. Native receipt authenticated; rerun native/run_native.py for fresh phases.'}
    expected = json.loads((HERE / 'RESULT.json').read_text())
    need(json.loads(json.dumps(result)) == expected, 'frozen result mismatch')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
