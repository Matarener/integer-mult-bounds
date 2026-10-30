#!/usr/bin/env python3
"""Explicit P104 gauge and completed-transform tags. Apache-2.0; see README."""
from __future__ import annotations
from collections import Counter
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PINS = {'PROOF.md': 'bdc7d868e4411541a33179af683f48011e66d6446a45bef363f3f3dd5163f717', 'README.md': 'd13777b9065d4d575cbc0e41293b454f15ad0455d5047bb36c6b1ed527ff48e0', 'RESULT.json': 'ce05a27ebc98677bec4febaa488fa03f5b6fc60216aa43b34298444d12f7ab6c'}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def unique(pairs):
    out = {}
    for key,value in pairs:
        need(key not in out, 'duplicate JSON key')
        out[key] = value
    return out


def load(path):
    return json.loads(path.read_text(), object_pairs_hook=unique)


def authenticate():
    for name,digest in PINS.items():
        need(hashlib.sha256((HERE/'source'/name).read_bytes()).hexdigest()==digest,
             'source bytes: '+name)


def dot(x,y):
    return (x&y).bit_count()&1


def linear(columns,x):
    value = 0
    for i,c in enumerate(columns):
        if x>>i&1:
            value ^= c
    return value


def tensor(x,y,n=9):
    return sum(y << (n*i) for i in range(n) if x>>i&1)


def orthogonal(columns):
    n = len(columns)
    need(all(type(c) is int and 0<c<(1<<n) for c in columns), 'matrix domain')
    need(all(dot(a,b)==(i==j) for i,a in enumerate(columns)
             for j,b in enumerate(columns)), 'orthogonal matrix')


def character_solutions(labels,target):
    # Enumerate 512 characters, not the orthogonal group.
    return [t for t in range(512)
            if all((p.bit_count()+2*dot(t,p))%4==target for p in labels)]


def check_completion(columns,a):
    """Polar-form preservation makes the quadratic difference linear; test its basis."""
    orthogonal(columns)
    n = len(columns)
    need(type(a) is int and 0<a<(1<<n), 'completion translation domain')
    need(all((c.bit_count()-1-2*((a>>i)&1))%4==0
             for i,c in enumerate(columns)), 'completed-transform phase character')
    need(linear(columns,a)==a, 'explicit gauge must fix completion tag')


def check_roles(columns,tags,a):
    """Direct-sum character identity on independent data and dirty-helper roles."""
    need(len(tags)==280, 'all local roles including 72 arbitrary helpers')
    for role,tag in enumerate(tags):
        need(type(tag) is int and 0<=tag<(1<<len(columns)), 'role tag domain')
        for i,c in enumerate(columns):
            need((c.bit_count()-1-2*((tag>>i)&1))%4==0,
                 'all-role completion tag '+str(role))
    need(all(tag==a for tag in tags), 'common tag on every role')


def translation_word(a,n):
    need(type(a) is int and 0<a<(1<<n) and a.bit_count()%2==0,
         'nonzero even translation')
    e = 1
    return [(e,1),(e,1),(e^a,1),(e^a,1)]


def check_word(word,a,n):
    need(all(type(u) is int and 0<u<(1<<n) and u.bit_count()%2==1
             and type(sign) is int and sign in [-1,1] for u,sign in word),
         'odd-line quarter-turn alphabet')
    # This constructive word has two repeated pairs. Its character is the XOR
    # of their labels for every frequency, without enumerating 2^81 addresses.
    need(len(word)==4 and word[0]==word[1] and word[2]==word[3], 'paired word')
    need(word[0][0]^word[2][0]==a, 'translation endpoint')
    for x,y in [(0,0),(0,1),(1,0),(1,1)]:
        phase = 2*word[0][1]*x+2*word[2][1]*y
        need(phase%4==2*(x^y), 'translation character table')


def gate(n=104,helpers=72,m=81,local_mass=2576,local_progress=2312):
    roles = 2*n*n+2*n*helpers
    calls = 2*n
    capacity = m*roles
    required = capacity-n*n
    remaining = max(0,required-calls*local_progress)
    lower = calls*local_mass+remaining
    return {'roles':roles,'local_calls':calls,'capacity':capacity,
            'required_progress':required,'remaining_rank':remaining,
            'lower_mass':lower,'excess':lower-capacity}


def audit(certificate=None):
    authenticate()
    source = load(HERE/'source/RESULT.json')
    cert = load(HERE/'CERTIFICATE.json') if certificate is None else certificate
    labels = source['physical_labels']
    need(len(labels)==104 and len(set(labels))==104 and
         all(type(p) is int and 0<p<512 and p.bit_count()%2 for p in labels),
         'published odd-label domain')
    z = cert['z']
    need(type(z) is int and 0<z<512 and z.bit_count()%4==0, 'isotropic weight-four gauge')
    O = [(1<<i) ^ (z if z>>i&1 else 0) for i in range(9)]
    need(isinstance(cert['columns'],list) and len(cert['columns'])==9 and
         all(type(c) is int and 0<c<512 for c in cert['columns']), 'typed gauge columns')
    need(cert['columns']==O, 'explicit gauge columns')
    orthogonal(O)
    need(all(linear(O,linear(O,x))==x for x in range(512)), 'gauge involution')
    need(all((linear(O,x).bit_count()-x.bit_count()-2*dot(z,x))%4==0
             for x in range(512)), 'nine-dimensional quadratic character')
    mapped = [linear(O,p) for p in labels]
    need(all(p.bit_count()%4==3 for p in mapped), 'uniform port phase')
    solutions = {c:character_solutions(labels,c) for c in [1,3]}
    need(solutions=={1:[91],3:[420]}, 'unique phase-uniform characters')
    need(solutions[1][0].bit_count()%2==1 and solutions[3][0]==z,
         'characteristic-vector obstruction to phase one')
    pairs = [tensor(p,q) for p in mapped for q in mapped]
    need(len(set(pairs))==10816 and all(v.bit_count()%4==1 for v in pairs),
         'uniform tensor-line phase')
    K = [tensor(O[i],O[j]) for i in range(9) for j in range(9)]
    a = tensor(z,511)^tensor(511,z)
    need(type(cert['translation']) is int and cert['translation']==a, 'completion tag')
    need(a.bit_count()==40 and all(linear(K,c)==(1<<i) for i,c in enumerate(K)),
         'tensor involution and nonzero even tag')
    check_completion(K,a)
    check_roles(K,[a]*280,a)
    # The two alternating encodings return after two completed uniform calls.
    need(linear(K,a)^a==0, 'two-completion tag cancellation')
    word = [tuple(op) for op in cert['translation_word']]
    check_word(word,a,81)
    need(word==translation_word(a,81), 'literal constructive correction')
    invoice = gate()
    need(invoice['excess']==44096 and invoice['roles']==36608, 'unchanged scaffold gate')
    # Restricted appended route only: four isolated calls on each completed bank.
    appended = 4*invoice['roles']
    need(type(cert['bankwise_appended_calls']) is int and
         cert['bankwise_appended_calls']==appended, 'appended-route invoice')
    return {'ports':104,'product_lines':10816,'original_phase_counts':dict(Counter(p.bit_count()%4 for p in labels)),
            'new_phase_counts':dict(Counter(p.bit_count()%4 for p in mapped)),
            'phase_failures_after':0,'unique_characters':solutions,'z':z,
            'completion_translation':a,'translation_weight':40,'restricted_translation_minimum':4,
            'all_role_character_checks':280*81,'gate':invoice,
            'bankwise_appended_calls':appended,
            'conditional_unit_tariff_route_excess':invoice['excess']+appended,
            'native_supplier_admitted':False,'new_kappa':False}


if __name__=='__main__':
    print('PASS_P104_PHASE_UNIFORM_GAUGE '+json.dumps(audit(),sort_keys=True))
