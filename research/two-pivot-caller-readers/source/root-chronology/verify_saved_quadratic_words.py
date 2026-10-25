#!/usr/bin/env python3
"""Replay saved retiming choices without running a search or trusting its bound.

Apache-2.0; substantial OpenAI Codex assistance. This verifies exact words and
rank screens, not native lowering, numerical precision, or a kappa claim.
"""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
import quadratic_charts as q
from audit_encoded_complete import inverse_events

HERE = Path(__file__).resolve().parent
BASE = HERE.parents[3]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run():
    cases = []
    for name in ('INDEPENDENT-ENCODED-COMPLETE', 'BALANCED-PHYSICAL-REPLAY-Q3'):
        witness = HERE / ('CLUSTER-' + name + '-ALLPAIRS.json')
        saved = json.loads(witness.read_bytes())
        source = Path(saved['source_path'])
        if not source.is_absolute():
            source = BASE / source
        original = json.loads(source.read_bytes())
        n, banks = saved['ambient_arity'], saved['width']
        choices = [tuple(a) for a in saved['choices']]
        events = q.compile_word(original['events'], banks, n, choices)
        q.need(json.loads(json.dumps(events)) == saved['events'], 'saved complete word matches current compiler')
        hist = Counter(e.get('rank_per_f', 0) for e in events)
        hist.pop(0, None)
        mass = sum(r * c for r, c in hist.items())
        q.need(mass == saved['native_rank_mass'] == 130, 'complete current integer rank invoice')
        I = q.identity(n)
        E = q.Mono(I.rows, (1 << n) - 1, (3, 1) * (n // 2), (0,) * n, 0, (n // 2) % 4)
        target = q.replay([dict(kind='NATIVE', bank=i, x_monomial=E.data()) for i in range(banks)], banks, n)
        q.need(q.replay(original['events'], banks, n) == target, 'current original source supplies every independent full-native output')
        q.need(q.replay(events, banks, n) == target, 'retimed complete original-column target for all f')
        inv = inverse_events(events, n)
        ident = q.replay([], banks, n)
        q.need(q.replay(events + inv, banks, n) == ident == q.replay(inv + events, banks, n), 'both literal inverse orders')
        index = next(i for i, e in enumerate(events) if e.get('rank_per_f', 0))
        q.need(q.replay(events[:index] + events[index+1:], banks, n) != target, 'omitted paid query mutant rejected')
        cases.append(dict(witness=str(witness), witness_sha256=sha(witness), source=str(source), source_sha256=sha(source), width=banks, ambient_arity=n, histogram=dict(sorted(hist.items())), native_rank_mass=mass, stock=n*banks, both_literal_inverse_orders=True, omitted_query_rejected=True))
    return dict(status='PASS_SAVED_QUADRATIC_WORDS_ALL_F', no_new_kappa=True,
                sources={str(p):sha(p) for p in (Path(__file__), HERE/'quadratic_charts.py', HERE/'audit_encoded_complete.py')},
                domain='Every integer f>=1; exact Gaussian coefficient tuples for all four residue classes; every original independent bank column.',
                cases=cases,
                limits=['No optimizer is run and no numerical optimizer bound is used.',
                        'Rank130 exceeds stock128 before precision, ownership, COPY and tape costs.',
                        'Every rank invoice still needs native lowering and contracting splits for recursive admission.',
                        'Older search receipts are historical; this receipt binds only these saved choices to the current exact compiler.'])

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--write', action='store_true'); args=parser.parse_args()
    result=json.loads(json.dumps(run())); path=HERE/'SAVED-QUADRATIC-WORDS-VALIDATION.json'
    if args.write: path.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else: q.need(json.loads(path.read_bytes())==result, 'saved validation differs')
    print(result['status'], 'triangular130/128 balanced130/128; both inverses; omitted-query controls')

if __name__=='__main__': main()
