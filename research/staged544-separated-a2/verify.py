#!/usr/bin/env python3
"""Seven fixed separated A2 contractions, with complete unchanged paid invoices.

Apache-2.0. ToikY with substantial OpenAI Codex assistance. The exact whole-word
arithmetic and frame engine is credited retained audit_core.py; this is not a
new independent interpreter or native/supplier audit. The replay adapter follows
the ordinary/dual/reverse contract of roger-sato's retained audit_verify.py.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import types

HERE = Path(__file__).resolve().parent
# Exact frozen exports: PR3734 fa041037..., PR3998 389268a6..., PR3945 91f81d13...
PINS = {
 'source/audit_core.py': (19364,'888679ca8502cdcb100420fe5382a052529a494bf76cb332928b86e62612b951','8b5e1d5f2a106402f036b63028ecef31a4e4c462'),
 'source/SOURCE-CREDITS.md': (2882,'d4a13d8b8ed9cdb594f00efb3d1a336e09d934423330f02a1514308a720c278b','c054fad87eeaa510865e682ee0c976c4cd728da2'),
 'source/PR3998-README.md': (6498,'d935e7d10e2935ca82a3ba952308d73b78e76a9039cb335682f1fc5ea3b580d7','dcd14ef45bcfb102d030e3f87a0bb2bf80d57ade'),
 'source/PR3998-PROOF.md': (11251,'0bbec6ba5b03e40e571f7f4a89e5776441a33b6ede41beeb80153ffad39d124f','afa6241fdaee6da1e567eb5ba74b780f9121ba8d'),
 'source/PR3945-NATIVE-LINEAGE-NOTICE': (2456,'ee0c73ca35877aad0e0b6adc560a3881cb82276dba4cf2d4fc58cd19e57cc420','380e979f0e84e00a22bd890615d87cc4684ad740'),
 'inputs/BORROW-WORD-base.json.gz': (72769,'5ca4be99851f8878cbfe0fd6c454df926b11218f17feefa1664721cf03156699','674ea18ade4af85ca865fb08dc973637a09e30e6'),
 'inputs/BORROW-WORD-extra.json.gz': (72766,'965268a9be73d3f62e7ef680d18f108cf064bfe1f44b82157baa61443232904e','b17e2be67e327f04802fd034c344fe4253c13a4a'),
}
SITES = (
 {'section':'A','indices':[1858,1859,1860],'removed_position':2,'known':True},
 {'section':'B','indices':[4,53,54],'removed_position':0,'known':False},
 {'section':'B','indices':[7,49,50],'removed_position':0,'known':False},
 {'section':'restore','indices':[20,21,36],'removed_position':2,'known':False},
 {'section':'restore','indices':[22,23,38],'removed_position':2,'known':False},
 {'section':'restore','indices':[26,27,51],'removed_position':2,'known':False},
 {'section':'restore','indices':[30,31,62],'removed_position':2,'known':False},
 {'section':'restore','indices':[32,33,73],'removed_position':2,'known':False},
)
# These are PR3998's published canonical known-contraction words, including its
# ordered basis [42,82] rather than the older source's [82,42].
KNOWN_WORD = {'base':'32415e93a50f0fdab5fa144da05977fe34bc8340bf967b91c7f7f0bc312df994',
              'extra':'439ce3544b68e3dffdb0cb4496fbc92330e825592515bc28c95580807c9d232d'}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def unique(pairs):
    result = {}
    for key,value in pairs:
        need(key not in result,'duplicate JSON key')
        result[key] = value
    return result


def load_json(path):
    return json.loads(path.read_bytes(),object_pairs_hook=unique)


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'))


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def authenticate():
    for relative,(length,sha,blob) in PINS.items():
        path = HERE / relative
        need(not path.is_symlink(),'source symlink: '+relative)
        raw = path.read_bytes()
        need(len(raw)==length and hashlib.sha256(raw).hexdigest()==sha,'source bytes: '+relative)
        need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==blob,
             'source Git blob: '+relative)
    path = HERE / 'source/audit_core.py'
    core = types.ModuleType('credited_staged544_audit_core')
    core.__file__ = str(path)
    exec(compile(path.read_bytes(),str(path),'exec'),core.__dict__)
    return core


def load_word(provider):
    need(provider in ('base','extra'),'provider domain')
    authenticate()
    return json.loads(gzip.decompress((HERE/'inputs'/('BORROW-WORD-'+provider+'.json.gz')).read_bytes()),
                      object_pairs_hook=unique)


def touched(gate):
    need(isinstance(gate,(tuple,list)) and gate,'scalar operation tuple')
    kind = gate[0]
    need(kind in ('add','scale'),'unknown scalar primitive barrier')
    need(len(gate)==(6 if kind=='add' else 5),'scalar operation arity')
    registers = gate[1:3] if kind=='add' else gate[1:2]
    need(all(type(r) is int and 0<=r<704 for r in registers),'scalar register domain')
    if kind=='add':
        need(registers[0]!=registers[1],'self ADD')
    return set(registers)


def matrix(gates, registers):
    rows = {r:{s:Q(r==s) for s in registers} for r in registers}
    for gate in gates:
        need(gate[0]=='add','A2 ADD alphabet')
        need(type(gate[3]) is int and type(gate[4]) is int and gate[4]>0 and gate[3]!=0,
             'typed nonzero rational coefficient')
        destination,source = gate[1:3]
        coefficient = Q(gate[3],gate[4])
        donor = rows[source].copy()
        rows[destination] = {r:rows[destination][r]+coefficient*donor[r] for r in registers}
    return rows


def segments(word,section):
    if section=='A':
        cuts = [word['prelude_events'],len(word['A'])]
    elif section=='B':
        cuts = sorted({0,len(word['B'])}|{record[0] for record in word['warps']})
    else:
        cuts = [0,len(word['restore'])]
    return list(zip(cuts,cuts[1:]))


def certify_site(word,site):
    need(isinstance(site,dict) and set(site)=={'section','indices','removed_position','known'},'site schema')
    section,indices,position = site['section'],site['indices'],site['removed_position']
    need(section in ('A','B','restore'),'site section')
    need(isinstance(indices,(tuple,list)) and len(indices)==3 and
         all(type(i) is int for i in indices),'typed site indices')
    need(0<=indices[0]<indices[1]<indices[2]<len(word[section]),'ordered site index domain')
    need(type(position) is int and position in (0,1,2),'removed position')
    need(type(site['known']) is bool,'known-site flag')
    need(any(low<=indices[0] and indices[2]<high for low,high in segments(word,section)),
         'prelude/native warp boundary crossed')
    gates = [word[section][i] for i in indices]
    need(all(g[0]=='add' for g in gates),'A2 ADD alphabet')
    support = set().union(*(touched(g) for g in gates))
    need(len(support)==3 and len({tuple(g[1:3]) for g in gates})==3,'three directed A2 edges')
    need(all(g[-1]==gates[0][-1] for g in gates),'common original frame')
    for index in range(indices[0],indices[2]+1):
        if index not in indices:
            need(touched(word[section][index]).isdisjoint(support),'intervening register dependency')
    remaining = [deepcopy(g) for p,g in enumerate(gates) if p!=position]
    replacement = remaining[::-1]
    need(matrix(gates,sorted(support))==matrix(replacement,sorted(support)),'exact inverse A2 identity')
    if site['known']:
        need(site==SITES[0],'only credited known site')
        for gate in replacement:
            gate[-1] = [42,82]
    return {**deepcopy(site),'support':sorted(support),'gates':deepcopy(gates),
            'replacement':replacement,'crossed_disjoint_events':indices[2]-indices[0]-2}


def _contract_sites(word,chosen):
    core = authenticate()
    records = [certify_site(word,site) for site in chosen]
    need(sum(len(r['support']) for r in records)==len(set().union(*(set(r['support']) for r in records))),
         'fixed contraction supports must be pairwise disjoint')
    changed = deepcopy(word)
    body_positions = None
    for section in ('A','B','restore'):
        local = [r for r in records if r['section']==section]
        starts = {r['indices'][0]:r for r in local}
        skipped = {i for r in local for i in r['indices'][1:]}
        result,positions = [],{}
        for index,gate in enumerate(word[section]):
            positions[index] = len(result)
            if index in starts:
                result.extend(deepcopy(starts[index]['replacement']))
            elif index not in skipped:
                result.append(deepcopy(gate))
        positions[len(word[section])] = len(result)
        changed[section] = result
        if section=='B':
            body_positions = positions
    for record in changed['warps']:
        record[0] = body_positions[record[0]]
    changed['cleanup'] = core.derive_cleanup(changed)
    return changed


def contract(word,include_known=True):
    need(type(include_known) is bool,'known contraction flag')
    return _contract_sites(word,SITES if include_known else SITES[1:])


def inspect_word(core,word):
    core.hygiene(word)
    need(word['cleanup']==core.derive_cleanup(word),'literal inverse cleanup differs')
    bill,widths,*_ = core.frame_bill(word)
    need(canonical(word['report']['local_profile'])==canonical({str(k):v for k,v in bill.items()}),
         'declared paid profile differs')
    counts = {section:{kind:sum(g[0]==kind for g in word[section]) for kind in ('add','scale','warp')}
              for section in ('A','B','restore','cleanup')}
    return {'profile':dict(bill),'helper_widths':dict(widths),'lengths':{k:len(word[k]) for k in counts},
            'primitive_counts':counts,'canonical_word_sha256':digest(word),'cleanup_sha256':digest(word['cleanup']),
            'native_operations':len(word['warps'])}


def matrix_digest(rows):
    record = [[r,[[s,list(word),q.numerator,q.denominator] for (s,word),q in sorted(row.items())]]
              for r,row in sorted(rows.items()) if row]
    return digest(record)


def semantics(core,word):
    def endpoint(result,name):
        bad,dirty,leaks,identity = result
        need(not bad and not dirty and not leaks and identity,name+' arbitrary-dirty endpoint')
    boundary = {}
    rows = core.forward_rows(word,symbolic_buffers=True,
                             snapshot=lambda values:boundary.setdefault('defects',core.boundary_defects(word,values)))
    endpoint(core.endpoint_defects(word,rows),'ordinary')
    need(not boundary['defects'],'ordinary cleanup boundary')
    dual = core.forward_rows(word,dual=True,symbolic_buffers=True)
    endpoint(core.endpoint_defects(word,dual,dual=True),'dual')
    reverse = core.transpose(core.reverse_columns(word))
    need(reverse=={r:row for r,row in rows.items() if row},'reverse pullback equals ordinary')
    before = core.transpose(core.reverse_columns(word,upto_cleanup=True))
    before = {r:before.get(r,{}) for r in set(before)|set(range(core.N))}
    need(not core.boundary_defects(word,before),'reverse cleanup boundary')
    live,buffers = core.N-len(word['removed']),len(word['helper_final'])
    need((live,buffers,len(rows))==(632,91,723),'all arbitrary live/buffer inputs')
    return {'live_inputs':live,'arbitrary_dirty_buffers':buffers,'matrix_dimension':len(rows),
            'ordinary_matrix_sha256':matrix_digest(rows),'dual_matrix_sha256':matrix_digest(dual),
            'ordinary':True,'dual':True,'reverse_equals_ordinary':True,'cleanup_boundary_both_directions':True,
            'buffer_to_live_leaks':0,'buffer_self_map':'identity'}


def compute(provider,full=True):
    need(type(full) is bool,'full replay flag')
    core = authenticate()
    source = load_word(provider)
    known = _contract_sites(source,SITES[:1])
    need(digest(known)==KNOWN_WORD[provider],'exact published PR3998 known-contraction word')
    changed = contract(source,True)
    words = {'source':source,'credited_3998':known,'separated':changed}
    info = {name:inspect_word(core,word) for name,word in words.items()}
    profiles = [record['profile'] for record in info.values()]
    need(profiles[0]==profiles[1]==profiles[2],'unchanged complete paid profile')
    need(all(r['helper_widths']==info['source']['helper_widths'] for r in info.values()),'helper widths unchanged')
    allowed = {'A','B','restore','cleanup','warps'}
    need(all(changed[k]==source[k] for k in source if k not in allowed),'nonword fields unchanged')
    need(len(changed['warps'])==len(source['warps']) and
         all(new[1:]==old[1:] for old,new in zip(source['warps'],changed['warps'])),
         'native registers/maps/ordered interface frames unchanged')
    additions = sum(info['credited_3998']['primitive_counts'][k]['add']-info['separated']['primitive_counts'][k]['add']
                    for k in ('A','B','restore'))
    cleanup = info['credited_3998']['primitive_counts']['cleanup']['add']-info['separated']['primitive_counts']['cleanup']['add']
    need((additions,cleanup)==(7,5),'seven additional forward and five cleanup ADDs')
    if full:
        for name,word in words.items():
            info[name]['semantics'] = semantics(core,word)
            print('CHECKED_SEPARATED_A2 '+provider+' '+name+' full723',flush=True)
        need(len({r['semantics']['ordinary_matrix_sha256'] for r in info.values()})==1 and
             len({r['semantics']['dual_matrix_sha256'] for r in info.values()})==1,'complete operators unchanged')
    return {'schema_version':1,'provider':provider,'known_sites':1,'new_sites':7,
            'sites':[certify_site(source,s) for s in SITES],'words':info,
            'additional_forward_add_saving':additions,'additional_cleanup_add_saving':cleanup,
            'recursive_moment_changed':False,'native_operators_changed':False,'new_supplier':False,'new_kappa':False}


def load_certificate():
    certificate = load_json(HERE/'data.json')
    need(isinstance(certificate,dict) and set(certificate)=={'schema_version','providers'},'certificate bundle schema')
    need(type(certificate['schema_version']) is int and certificate['schema_version']==1,'typed certificate schema version')
    need(isinstance(certificate['providers'],dict) and set(certificate['providers'])=={'base','extra'},'exact certificate providers')
    return certificate


def audit(provider,full=True,certificate=None):
    result = compute(provider,full)
    expected = load_certificate()['providers'][provider] if certificate is None else certificate
    expected = deepcopy(expected)
    if not full:
        for word in expected['words'].values():
            word.pop('semantics',None)
    need(canonical(result)==canonical(expected),'complete typed fixed-witness certificate')
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--provider',choices=('base','extra'),default='base')
    parser.add_argument('--quick',action='store_true',help='fixed local identities and invoices only; whole-word replay omitted')
    parser.add_argument('--write-data',action='store_true',help='explicitly regenerate both provider receipts with full replay')
    args = parser.parse_args()
    if args.write_data:
        result = {'schema_version':1,'providers':{p:compute(p,True) for p in ('base','extra')}}
        (HERE/'data.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
        print('WROTE_SEPARATED_A2_DATA bothproviders full723')
    else:
        result = audit(args.provider,not args.quick)
        print('PASS_STAGED544_SEPARATED_A2 provider='+args.provider+' full_replay='+str(not args.quick)
              +' new_sites=7 forward_add_saving=7 cleanup_add_saving=5 unchanged_paid_profile no_new_kappa')


if __name__=='__main__':
    try:
        main()
    except Exception as error:
        import sys
        print('FAIL_STAGED544_SEPARATED_A2 '+str(error),file=sys.stderr)
        raise SystemExit(1)
