"""Fresh local reconstruction/semantics; authenticate separate native evidence.
Dugongue with substantial OpenAI Codex assistance. Apache-2.0.
"""
import gzip
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
from apply_terminal import apply, exact_semantics, need
HERE = Path(__file__).resolve().parent


def load(root=HERE):
    pins = json.loads((root / 'INPUTS.json').read_text(encoding='utf8'))
    for name, expected in pins.items():
        need(hashlib.sha256((root / name).read_bytes()).hexdigest() == expected, 'input hash: ' + name)
    return [(tag, json.loads(gzip.decompress((root / ('inputs/OLD-' + tag + '.json.gz')).read_bytes())),
             json.loads((root / ('patches/' + tag + '.json')).read_text(encoding='utf8')),
             json.loads(gzip.decompress((root / ('inputs/NEW-' + tag + '.json.gz')).read_bytes())))
            for tag in ('base', 'extra')]


def main():
    from checks.exact_root import FULL_PROFILE, LOWER, UPPER, OUTER_LOWER
    actual_profile = {int(k): v for k, v in json.loads((HERE / "owner/PROFILE.json").read_text(encoding="utf8")).items()}
    need(actual_profile == FULL_PROFILE, "owner / moment profile bridge")
    declared = json.loads((HERE / 'RESULT.json').read_text(encoding='utf8'))
    need(declared['status'] == 'PASS_SOURCE_BOUND_TERMINAL_CONSTRUCTION', 'result status')
    need({int(k): v for k, v in declared['full_profile'].items()} == FULL_PROFILE, 'result profile')
    need(Q(declared['root_lower']) == LOWER and Q(declared['root_upper']) == UPPER, 'result root interval')
    need(Q(declared['conditional_kappa']) == OUTER_LOWER, 'result conditional endpoint')
    for tag, source, patch, target in load():
        word = apply(source, patch)
        need(word == target, 'entire frozen word mismatch')
        exact_semantics(word)
        receipt = json.loads((HERE / ('evidence/NATIVE-' + tag + '.json')).read_text(encoding='utf8'))
        need(receipt['status'] == 'PASS_COMPLETE_T74_NATIVE_REPLAY', 'native status')
        need(receipt['word_sha256'] == hashlib.sha256((HERE / ('inputs/NEW-' + tag + '.json.gz')).read_bytes()).hexdigest(), 'native input')
        closure = {p.relative_to(HERE / 'native/vendor').as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in (HERE / 'native/vendor').rglob('*') if p.is_file()}
        need(receipt['source_sha256'] == closure, 'native source closure')
        need([s['step'] for s in receipt['steps']] == ['native', 'ledgers', 'local-replay', 'wrappers', 'phases']
             and all(s['exit_code'] == 0 for s in receipt['steps']), 'native stages')
    print(json.dumps({'status': 'PASS_TERMINAL_GAP_WORDS', 'providers': 2,
          'local_profile': {'1':2482,'2':712,'3':218,'4':109,'5':20,'8':8},
          'width_inventory': {'5':28,'6':18,'7':53,'8':96,'9':213},
          'scope': 'Fresh full literal reconstruction, exact frame/lifted-action and arbitrary-dirty forward/dual/boundary checks. Native receipts authenticated; phases are a separate fresh-run command.'}, sort_keys=True))


if __name__ == '__main__':
    main()
