#!/usr/bin/env python3
"""Source integration for GL3 free scalar mixing; no CNF/SAT lower-bound claim.

The normalized paid-step implementation is retained source. Scalar interleaving
and conversion are adapter-owned and explicitly distinguished from the source.
Prepared with OpenAI Codex assistance; Apache-2.0.
"""
from __future__ import annotations

import argparse
import ast
import copy
from functools import reduce
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
from operator import xor
import sys

HEAD = "ca0002008b497428f0b651501c4a220a9d2785e7"
PINS = {
    "model.py": "38945ee5997b0b985d3fa461a06451ae91f6a0ac5757e42b74c5e175967a785c",
    "cnf_model.py": "12a02756ee757e5b70507e30fc6b8657f802000945742db5726335e83c56793f",
    "exact_checker.py": "92d7b726d3776012743fbc7713193a8b338ce6ae0d868f3805b9160ebd93efe1",
    "DIRECT_NINE.json": "adc28b1cf52b848875062e9df0abdb2bc4d7b4aa4caa809480c723b571de845a",
    "ENCODING_AUDIT.md": "b149c967439acffd458f22c4e480e475c8732249313bd23bd7b55265d72892f0",
    "README.md": "f5e97f74a34d53607eac9802f9cacdb84a39c187c7ee8c7bb2e8fb96c9698294",
    "NOTICE.md": "4e0e33ce73e962a9acd7a41ea3206e93e8ef3d2513deb45980f6596e04f13329",
    "LICENSE": "c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4",
}
ORACLE_SHA256 = "f6e0fb0916bd79ffa0da7696b9e0f722daf64ce6726834c9732dcb264b309fe0"
ORACLE_CODE_SHA256 = "743db5628457694a2ce3fbb789ec07b608c01a4f5cd21455997816dd98839b4a"
TRIPLE_SHA256 = "52c0cefefa4b1b0cee3cd99c1373ad3d750613cddac4cb0f70eae51f77681c36"


def need(ok, why):
    if not ok:
        raise ValueError(why)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def rows(packed):
    return tuple((packed >> (3*r)) & 7 for r in range(3))


def pack(matrix):
    return sum(x << (3*r) for r, x in enumerate(matrix))


def column(matrix, c):
    return sum(((matrix >> (3*r+c)) & 1) << r for r in range(3))


def outer(u, v):
    return tuple(v if u & (1 << r) else 0 for r in range(3))


def load(source):
    for name, digest in PINS.items():
        need(sha((source/name).read_bytes()) == digest, "source hash "+name)
    sys.path.insert(0, str(source))
    for name in ("model", "cnf_model", "exact_checker"):
        sys.modules.pop(name, None)
    model = importlib.import_module("model")
    cnfm = importlib.import_module("cnf_model")
    exact = importlib.import_module("exact_checker")
    for name, module in (("model",model),("cnf_model",cnfm),("exact_checker",exact)):
        need(Path(module.__file__).resolve() == (source/(name+".py")).resolve(), "source module path "+name)
    return model, cnfm, exact


def selector_truth_table(cnfm, source):
    """Execute only the original vTu selector statement, not build()/transitions."""
    tree = ast.parse((source/"cnf_model.py").read_bytes())
    build = next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name == "build")
    matches = [node for node in ast.walk(build) if isinstance(node,ast.Call)
               and isinstance(node.func,ast.Attribute) and node.func.attr == "add"
               and len(node.args) == 1 and isinstance(node.args[0],ast.Call)
               and isinstance(node.args[0].func,ast.Attribute) and node.args[0].func.attr == "xors"]
    need(len(matches) == 1, "unique original scalar selector expression")
    expression = ast.Expression(copy.deepcopy(matches[0]))
    ast.fix_missing_locations(expression)
    cnf = cnfm.CNF()
    u = [cnf.variable() for _ in range(3)]
    v = [cnf.variable() for _ in range(3)]
    eval(compile(expression,"<original vTu selector only>","eval",optimize=0), {"cnf":cnf,"u":u,"v":v})
    accepted = []
    table = []
    for uu in range(8):
        for vv in range(8):
            assignment = {x:bool(uu & (1 << k)) for k,x in enumerate(u)}
            assignment.update({x:bool(vv & (1 << k)) for k,x in enumerate(v)})
            failures = cnf.failed_clauses(assignment)
            parity = (uu & vv).bit_count() % 2
            need((failures == 0) == bool(parity), "actual scalar selector truth table")
            if not failures:
                accepted.append((uu,vv))
            table.append({"u":uu,"v":vv,"accepted":failures == 0})
    need(len(accepted) == 28, "28 actual source selector pairs")
    return accepted, table, sha(ast.dump(expression).encode())


def run(source, oracle_path, oracle_code):
    model, cnfm, exact = load(source)
    algebra = model.Algebra()
    need(len(algebra.group) == len(set(algebra.group)) == 168, "actual source group order")
    identity = algebra.endpoint((model.ID,)*3)
    inverse = {}
    for p in algebra.group:
        choices = [q for q in algebra.group if model.multiply(p,q) == model.ID
                   and model.multiply(q,p) == model.ID]
        need(len(choices) == 1, "unique source frame inverse")
        inverse[p] = choices[0]
    pairs, selector_table, selector_ast = selector_truth_table(cnfm, source)
    need(set(pairs) == {(u,v)for u,v,_,_ in algebra.generators}, "packed alphabet equals actual CNF selector pairs")
    need(model.PAIRS == cnfm.PAIRS and len(model.PAIRS) == 6, "six address labels agree")
    factors = {(u,v,i,j)for u,v in pairs for i,j in cnfm.PAIRS}
    need(factors == set(algebra.generators) and len(factors) == 168, "all 168 actual normalized factors")
    source_projectors = {outer(u,v) for u,v in pairs}
    need(len(source_projectors) == 28, "28 distinct source projectors")
    conjugacies = []
    fibers = {}
    source_rows = {tuple(x)for x in cnfm.address_data()[0]}
    need(source_rows == {rows(p)for p in algebra.group}, "actual rowtuple/packed source frames agree")
    for prefix in sorted(algebra.group, key=rows):
        pinv = inverse[prefix]
        for r in range(3):
            e = 1 << (3*r+r)
            n = model.multiply(model.multiply(pinv,e),prefix)
            u,v = column(pinv,r), rows(prefix)[r]
            need(rows(n) == outer(u,v) and (u,v) in pairs, "actual packed frame conjugacy admitted")
            nr = exact.product(exact.product(rows(pinv),rows(e)),rows(prefix))
            need(nr == rows(n) and nr in source_projectors, "actual rowtuple conjugacy admitted")
            need(all((u,v,i,j) in factors for i,j in cnfm.PAIRS), "all six labels at this conjugacy admitted")
            fibers[nr] = fibers.get(nr,0)+1
            conjugacies.append({"frame":list(rows(prefix)),"coordinate":r,"inverse":list(rows(pinv)),
                                "u":u,"v":v,"projector":list(nr)})
    need(len(conjugacies) == 504 and set(fibers) == source_projectors
         and set(fibers.values()) == {18}, "504 conjugacies cover 28 projectors with fibers18")
    need(sha(oracle_path.read_bytes()) == ORACLE_SHA256, "frozen independent table bytes")
    independent_table = json.loads(oracle_path.read_bytes())
    fields = ('frame','coordinate','inverse','u','v','projector')
    projected = [{k:row[k]for k in fields}for row in independent_table['conjugacies']]
    need(canonical(projected) == canonical(conjugacies), "all504 actual source rows equal frozen independent rows")
    triples = [{k:row[k]for k in ('frame','coordinate','projector')}for row in conjugacies]
    need(sha(canonical(triples)) == TRIPLE_SHA256 == independent_table['binary_table_sha256'],
         "all504 canonical triple checksum")
    converse_witnesses = 0
    for row in independent_table['conjugacies']:
        witness = row['converse']
        basis, prefix = pack(witness['basis']), pack(witness['frame'])
        need(witness['coordinate'] == 0 and inverse[basis] == prefix, "independent converse basis inverse")
        need([column(basis,c)for c in range(3)] == witness['basis_columns']
             and column(basis,0) == row['u'] and rows(prefix)[0] == row['v'],
             "actual source columns bind independent converse witness")
        e0 = 1
        need(rows(model.multiply(model.multiply(inverse[prefix],e0),prefix)) == tuple(row['projector']),
             "independent converse witness yields same source projector")
        converse_witnesses += 1
    need(sha(oracle_code.read_bytes()) == ORACLE_CODE_SHA256, "frozen independent converter code")
    spec = importlib.util.spec_from_file_location('_independent_normalization_oracle',oracle_code)
    independent = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(independent)

    def scalar_left(frame, state):
        # This scalar interleaver is adapter code, not a source circuit operation.
        return tuple(reduce(xor,
                     (state[3*k+c] for k in range(3) if frame & (1 << (3*r+k))),0)
                     for r in range(3)for c in range(3))

    def augmentation(state):
        return sum((poly.bit_count()%2) << k for k,poly in enumerate(state))

    def normalize(frames, calls):
        need(len(frames) == len(calls)+1, "raw chronology frame count")
        prefix = frames[0]
        normalized = []
        for j,(r,i,k) in enumerate(calls):
            normalized.append((column(inverse[prefix],r),rows(prefix)[r],i,k))
            prefix = model.multiply(frames[j+1],prefix)
        return normalized, prefix

    def execute_raw(frames,calls):
        state = scalar_left(frames[0],identity)
        for frame,(r,i,j) in zip(frames[1:],calls):
            state = algebra.step(state,(1 << r,1 << r,i,j))
            state = scalar_left(frame,state)
        return state

    def named_raw(free,paid):
        return {'r':3,'paid_count':len(paid),'free':[list(rows(f))for f in free],
                'paid':[{'coordinate':r,'address':['g'+str(model.PAIRS.index((i,j)))]}for r,i,j in paid]}

    def named_normal(word):
        return {'r':3,'paid_count':len(word),'residual':list(rows(model.ID)),
                'factors':[{'projector':list(outer(u,v)),'u':u,'v':v,
                            'address':['g'+str(model.PAIRS.index((i,j)))]}for u,v,i,j in word]}

    def concrete(operator):
        # Evaluate frozen free positive words in the actual source GL3 address group.
        answer = []
        for row in operator:
            for polynomial in row:
                coefficient = 0
                for word in polynomial:
                    address = model.ID
                    for token in word:
                        need(token in {'g'+str(j)for j in range(6)}, "declared symbolic address label")
                        address = model.multiply(address,model.LABELS[int(token[1:])])
                    coefficient ^= 1 << algebra.index[address]
                answer.append(coefficient)
        return tuple(answer)

    def check_independent_raw(free,paid):
        raw = named_raw(free,paid)
        result = independent.normalize_raw(raw)
        own_word,net = normalize(free,paid)
        need(result['residual'] == list(rows(net)) and result['paid_count'] == len(paid),
             "independent conversion residual/count equals source adapter")
        need([(f['u'],f['v'],*model.PAIRS[int(f['address'][0][1:])])for f in result['factors']] == own_word,
             "independent conversion preserves exact source gate/address chronology")
        actual = execute_raw(free,paid)
        need(concrete(independent.evaluate_raw(raw)) == actual
             and concrete(independent.evaluate_normalized(result)) == actual,
             "independent full free-word operators evaluate to actual source endpoint")
        return sha(canonical(independent.polynomial_json(independent.evaluate_raw(raw))))

    def basis_prefix(u,v):
        kernel = [x for x in range(1,8) if (v & x).bit_count()%2 == 0]
        bases = []
        for a in kernel:
            for b in kernel:
                s = sum((((u >> r)&1) | (((a >> r)&1) << 1) | (((b >> r)&1) << 2)) << (3*r)
                        for r in range(3))
                if s in inverse:
                    bases.append(s)
        need(bool(bases), "basis extends u by kernel(v)")
        s = min(bases, key=rows)
        prefix = inverse[s]
        need(column(s,0) == u and rows(prefix)[0] == v, "converse basis witnesses actual source pair")
        return prefix

    def realize(word):
        if not word:
            return [model.ID], []
        prefixes = [basis_prefix(u,v) for u,v,_,_ in word]
        frames = [prefixes[0]]
        frames.extend(model.multiply(b,inverse[a]) for a,b in zip(prefixes,prefixes[1:]))
        frames.append(inverse[prefixes[-1]])
        calls = [(0,i,j)for _,_,i,j in word]
        return frames,calls

    converse_rows = []
    for gate in sorted(factors):
        frames,calls = realize([gate])
        converted,terminal = normalize(frames,calls)
        actual = execute_raw(frames,calls)
        need(converted == [gate] and terminal == model.ID and actual == algebra.replay([gate]),
             "one-factor source converse preserves endpoint and paid chronology")
        need(augmentation(algebra.replay([gate])) == model.ID, "all168 actual normalized factors augment to identity")
        converse_rows.append({"gate":list(gate),"frames":[list(rows(f))for f in frames],"paid_calls":1})
    direct = json.loads((source/'DIRECT_NINE.json').read_bytes())['word_uvij']
    direct = [tuple(g)for g in direct]
    direct_endpoint = algebra.replay(direct)
    need(direct_endpoint == algebra.endpoint(), "actual packed direct-nine formal endpoint")
    direct_check = exact.check(direct)
    need(direct_check['accepted'] and direct_check['basis_columns_checked'] == 504,
         "actual direct-nine full168-address regular action")
    frames,calls = realize(direct)
    normalized,terminal = normalize(frames,calls)
    raw_endpoint = execute_raw(frames,calls)
    need(normalized == direct and terminal == model.ID and raw_endpoint == direct_endpoint,
         "direct-nine raw realization and converse chronology")
    need(len(calls) == len(direct) == 9 and augmentation(raw_endpoint) == model.ID,
         "direct-nine paid cost and augmentation")
    direct_symbolic_sha = check_independent_raw(frames,calls)
    independent_converse = independent.compile_normalized(named_normal(direct))
    independent_free = [pack(w)for w in independent_converse['free']]
    independent_paid = [(item['coordinate'],*model.PAIRS[int(item['address'][0][1:])])
                        for item in independent_converse['paid']]
    need(len(independent_paid) == 9 and independent_converse['paid_count'] == 9
         and execute_raw(independent_free,independent_paid) == direct_endpoint,
         "frozen independent converse compiler realizes actual direct-nine source endpoint")
    raw_examples = []
    frame_cycle = pack((2,4,1))
    need(frame_cycle in inverse and inverse[frame_cycle] != frame_cycle, "noninvolutory frame witness")
    tests = [([frame_cycle],[]),
             ([frame_cycle,model.ID,inverse[frame_cycle]],[(0,0,1),(1,1,2)]),
             ([algebra.group[k]for k in (5,30,65,100,135)],[(0,0,1),(2,1,2),(1,2,0),(0,1,0)])]
    for free,paid in tests:
        norm,net = normalize(free,paid)
        endpoint = execute_raw(free,paid)
        need(all(g in factors for g in norm), "raw conversion chooses admitted source factors")
        need(endpoint == scalar_left(net,algebra.replay(norm)), "raw equals net scalar times chronological normalized word")
        need(augmentation(endpoint) == net, "actual raw augmentation equals net scalar frame")
        symbolic_sha = check_independent_raw(free,paid)
        raw_examples.append({'frames':[list(rows(f))for f in free], 'coordinate_calls':[list(g)for g in paid],
                             'normalized':[list(g)for g in norm], 'terminal_frame':list(rows(net)),
                             'paid_calls_before':len(paid),'paid_calls_after':len(norm),
                             'raw_endpoint_sha256':sha(canonical(list(endpoint))),
                             'independent_free_word_sha256':symbolic_sha})
    e0 = 1
    correct_n = model.multiply(model.multiply(inverse[frame_cycle],e0),frame_cycle)
    wrong_inverse_n = model.multiply(model.multiply(frame_cycle,e0),frame_cycle)
    need(wrong_inverse_n != correct_n and model.multiply(wrong_inverse_n,wrong_inverse_n) != wrong_inverse_n,
         "replacing noninvolutory frame inverse by frame rejects projector")
    wrong_inverse_uv = column(frame_cycle,0),rows(frame_cycle)[0]
    need(wrong_inverse_uv not in pairs, "actual source selector rejects the wrong-inverse projector")
    raw_frames = [frame_cycle,inverse[frame_cycle]]
    raw_calls = [(0,0,1)]
    norm,_ = normalize(raw_frames,raw_calls)
    wrong_order_gate = (column(frame_cycle,0),rows(inverse[frame_cycle])[0],0,1)
    need(algebra.replay([wrong_order_gate]) != execute_raw(raw_frames,raw_calls)
         and algebra.replay(norm) == execute_raw(raw_frames,raw_calls), "opposite conjugacy order changes actual endpoint")
    need(execute_raw([frame_cycle],[]) != identity, "omitting terminal free frame changes raw endpoint")
    address_confusion = algebra.endpoint((frame_cycle,)*3)
    need(address_confusion != execute_raw([frame_cycle],[]) and augmentation(address_confusion) == model.ID,
         "scalar frame is not a group-algebra address monomial")
    chronology = [(1,1,0,1),(1,1,1,2)]
    need(algebra.replay(chronology) != algebra.replay(list(reversed(chronology))),
         "reversing noncommuting address chronology changes source endpoint")
    table = {'source_head':HEAD,'conjugacies':conjugacies,'selector_truth_table':selector_table,
             'one_factor_converses':converse_rows}
    result = {'status':'PASS_SOURCE_FREE_MIXING_INTEGRATION','source_head':HEAD,'source_sha256':PINS,
              'group_order':168,'frame_coordinate_conjugacies':504,'projectors':28,'fiber_multiplicity':18,
              'source_normalized_factors':168,'source_selector_assignments':64,'source_selector_ast_sha256':selector_ast,
              'source_table_canonical_sha256':sha(canonical(table)),
              'independent_table_sha256':ORACLE_SHA256,'independent_converter_sha256':ORACLE_CODE_SHA256,
              'independent_conjugacy_rows_compared':504,'independent_converse_witnesses_bound':converse_witnesses,
              'independent_triple_canonical_sha256':TRIPLE_SHA256,
              'one_factor_converses_checked':168,'direct_nine_source_check':direct_check,
              'direct_nine_raw_realization':{'frames':[list(rows(f))for f in frames],
                  'coordinate_calls':[list(g)for g in calls], 'normalized':[list(g)for g in normalized],
                  'paid_calls_before':9,'paid_calls_after':9,'terminal_frame':list(rows(terminal)),
                  'formal_endpoint_canonical_sha256':sha(canonical(list(direct_endpoint))),
                  'independent_free_word_sha256':direct_symbolic_sha,
                  'independent_converse_raw_frames':[list(rows(f))for f in independent_free],
                  'independent_converse_paid_calls':[list(c)for c in independent_paid]},
              'arbitrary_raw_examples':raw_examples,
              'controls':{
                  'inverse_equals_frame':{'detected':True,'frame':list(rows(frame_cycle)),
                      'inverse':list(rows(inverse[frame_cycle])),'correct_projector':list(rows(correct_n)),
                      'wrong_projector':list(rows(wrong_inverse_n)),'wrong_uv':list(wrong_inverse_uv),
                      'source_scalar_selector_accepts':False},
                  'opposite_conjugacy_order':{'detected':True,'wrong_source_gate':list(wrong_order_gate),
                      'reason':'different actual source formal endpoint'},
                  'dropped_terminal_frame':{'detected':True,'residual':list(rows(frame_cycle)),
                      'reason':'different raw zero-paid endpoint'},
                  'scalar_address_confusion':{'detected':True,'scalar_augmentation':list(rows(frame_cycle)),
                      'address_monomial_augmentation':list(rows(model.ID)),
                      'reason':'different augmentation and formal endpoint'},
                  'reversed_address_chronology':{'detected':True,'source_word':[list(g)for g in chronology],
                      'forward_endpoint_sha256':sha(canonical(list(algebra.replay(chronology)))),
                      'reversed_endpoint_sha256':sha(canonical(list(algebra.replay(list(reversed(chronology)))))),
                      'reason':'different actual source endpoint'},
              },
              'scope':'Actual normalized source alphabet and endpoint binding; raw scalar interleaver is adapter-owned.',
              'limits':['no full CNF/Tseitin equivalence','no SAT/RUP replay or minimum-nine certification',
                        'no physical scalar-mixing or delivery tariff','not independent human or proof-kernel acceptance','no new kappa']}
    return table,result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    here = Path(__file__).resolve().parent
    parser.add_argument('--source',type=Path,default=here/'source')
    parser.add_argument('--table-output',type=Path)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--oracle',type=Path,default=here/'ORACLE.json')
    parser.add_argument('--oracle-code',type=Path,default=here/'oracle.py')
    parser.add_argument('--expected',type=Path,default=here/'INTEGRATION-RESULT.json')
    parser.add_argument('--table-expected',type=Path,default=here/'SOURCE-TABLE.json')
    args = parser.parse_args()
    table,result = run(args.source,args.oracle,args.oracle_code)
    if args.table_output:
        args.table_output.write_text(json.dumps(table,sort_keys=True,indent=2)+'\n')
    payload = json.dumps(result,sort_keys=True,indent=2)+'\n'
    if args.output:
        args.output.write_text(payload)
    else:
        need(canonical(json.loads(args.expected.read_bytes())) == canonical(result), "complete typed integration receipt")
        need(sha(canonical(json.loads(args.table_expected.read_bytes()))) == result['source_table_canonical_sha256'],
             "complete retained source table")
    print(payload,end='')


if __name__ == '__main__':
    main()
