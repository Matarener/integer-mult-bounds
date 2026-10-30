"""Negative controls: every mutation must be rejected by audit_local.py / audit_global.py."""
import gzip, json, shutil, subprocess, sys, tempfile, copy
from pathlib import Path
H = Path(__file__).resolve().parent
PKG = Path(sys.argv[1]); FR = sys.argv[2]
w = json.loads(gzip.decompress((PKG / 'WORD.json.gz').read_bytes()))
recs = w['records']
iq = next(i for i, e in enumerate(recs) if e[0] == 'Q')
ia = next(i for i, e in enumerate(recs) if e[0] == 'ADD' and e[1] not in w['owned'] and e[2] not in w['owned'])
iz = next(i for i, e in enumerate(recs) if e[0] == 'ZERO_Q')
local_mut = {
  'wrong_query_rank': lambda x: x['records'][iq].__setitem__(4, x['records'][iq][4] + 1),
  'drop_one_ADD': lambda x: x['records'].pop(ia),
  'duplicate_one_ADD': lambda x: x['records'].insert(ia, list(x['records'][ia])),
  'ADD_wrong_frame': lambda x: x['records'][ia].__setitem__(3, x['records'][ia][3] + 1),
  'free_move_made_paid->ZERO_Q_on_payload': lambda x: x['records'][iq].__setitem__(0, 'ZERO_Q'),
  'paid_query_made_free': lambda x: x['records'][iz].__setitem__(0, 'Q'),
  'erase_an_original': lambda x: x['records'].insert(0, ['ERASE', 5, 1]),
  'changed_final_frame': lambda x: x['final'].__setitem__(300, x['final'][300] + 1),
}
ok = True
with tempfile.TemporaryDirectory() as td:
    for name, f in local_mut.items():
        x = copy.deepcopy(w); f(x)
        p = Path(td) / 'W.json.gz'; p.write_bytes(gzip.compress(json.dumps(x).encode()))
        r = subprocess.run([sys.executable, '-I', str(H / 'audit_local.py'), FR, str(p), name], capture_output=True, text=True)
        rej = r.returncode != 0
        if name == 'paid_query_made_free':  # legal over-payment: must be accepted but must show in the paid bill
            rej = r.returncode == 0 and '"1": 1282' in r.stdout
        ok &= rej
        print('local', name, 'REJECTED' if rej else 'ACCEPTED(!)', (r.stdout + r.stderr).strip().splitlines()[-1][:160], flush=True)
    # global mutations
    ev = gzip.decompress((PKG / 'GLOBAL.jsonl.gz').read_bytes()).splitlines()
    def gmut(name, fn_ev=None, fn_inv=None):
        global ok
        d = Path(td) / name; shutil.copytree(PKG, d, ignore=shutil.ignore_patterns('prior', '*.py'))
        e2 = [json.loads(l) for l in ev]
        if fn_ev: fn_ev(e2)
        (d / 'GLOBAL.jsonl.gz').write_bytes(gzip.compress('\n'.join(json.dumps(e) for e in e2).encode()))
        if fn_inv:
            inv = json.load(open(d / 'INVOICE.json')); fn_inv(inv); json.dump(inv, open(d / 'INVOICE.json', 'w'))
        r = subprocess.run([sys.executable, '-I', str(H / 'audit_global.py'), str(d), FR, name], capture_output=True, text=True)
        rej = r.returncode != 0; ok &= rej
        print('global', name, 'REJECTED' if rej else 'ACCEPTED(!)', (r.stdout + r.stderr).strip().splitlines()[-1][:160], flush=True)
        shutil.rmtree(d)
    qi = next(i for i, l in enumerate(ev) if l.startswith(b'["QUERY"'))
    ai = next(i for i, l in enumerate(ev) if l.startswith(b'["ADD"'))
    gmut('global_query_rank_lowered', lambda e: e[qi].__setitem__(2, e[qi][2] + 1))
    gmut('global_drop_ADD', lambda e: e.pop(ai))
    gmut('invoice_lost_target_debit', None, lambda inv: inv['targets'].__setitem__('8', inv['targets']['8'] + 18))
    gmut('invoice_paid_understated', None, lambda inv: inv['paid'].__setitem__('2', inv['paid']['2'] - 1))
print('ALL_CONTROLS_REJECTED' if ok else 'SOME_CONTROL_ACCEPTED')
