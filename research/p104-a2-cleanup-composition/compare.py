"""Compare the concurrent P104 artifacts. Ali Romman with OpenAI Codex. Apache-2.0."""
from copy import deepcopy
from hashlib import sha256
import gzip
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def need(ok, why):
    if not ok:
        raise ValueError(why)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def compare_word(a, b):
    need(a.keys() == b.keys(), 'Same complete word fields')
    need({k for k in a if a[k] != b[k]} == {'schema'}, 'Only the schema label differs')
    return sha256(json.dumps({k:v for k,v in a.items() if k != 'schema'},sort_keys=True,separators=(',',':')).encode()).hexdigest()


def main():
    pins = read(HERE/'CONCURRENT-SOURCE.json')
    for row in pins:
        need(sha256((HERE/row['local']).read_bytes()).hexdigest() == row['sha256'], 'Exact concurrent source pin')
    a,b = read(HERE/'WORD.json.gz'),read(HERE/'inputs/pr5650/WORD.json.gz')
    digest = compare_word(a,b)
    mutant = deepcopy(b)
    mutant['program'].pop()
    try:
        compare_word(a,mutant)
    except ValueError:
        pass
    else:
        raise ValueError('Missing-event control accepted')
    a,b = read(HERE/'RESULT.json'),read(HERE/'inputs/pr5650/FULL-RESULT.json')
    for key in ['local','native','physical']:
        need(a[key] == b[key], 'Same full scientific result: '+key)
    need(a['separate_columns'] == b['transpose'], 'Same complete dense-column result')
    shared = ['paid','targets','productive_fields','paid_calls','rank_mass_surplus','raw_root_interval',
              'raw_ceiling','nonrecursive','ordinary_BIT','full_forward_calls','query_shears','whole_idle_jobs']
    for key in shared:
        need(a['complete_cost'][key] == b['complete_cost'][key], 'Same invoice property: '+key)
    print('PASS_CONCURRENT_P104_SAME_WORD_AND_INVOICE')
    print('shared_word_sha256='+digest)
    print('The two claim/test points differ. They do not define different mechanisms.')


if __name__ == '__main__':
    main()
