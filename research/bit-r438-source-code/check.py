#!/usr/bin/env python3
"""Independent sparse integer / F2 endpoint and rational native-cap replay.

No producer module is imported. Every public input is an independent column.
"""
from collections import Counter
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import types

HERE = Path(__file__).resolve().parent

def load(name):
    path = HERE / (name + ".py")
    module = types.ModuleType(name)
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module

cap, scalar = load("native_caps"), load("signed_rows")
need = cap.need

def projected(program):
    dead = [h for h in range(222,660)
            if all(not(op == 1 and s == h or op in (2,3) and d == h)
                   for op,d,s,c,f,p in program['records'])]
    need(dead == list(range(471,480)),'unread physical helper classification')
    dead_set = set(dead)
    keep = [p for p in range(660) if p not in dead_set]
    mapping = {old:new for new,old in enumerate(keep)}
    mapping[660] = len(keep)
    records = []
    removed = Counter()
    for op,d,s,c,f,p in program['records']:
        if d in dead_set:
            need(op in (0,1),'discarded helper has an owned snapshot role')
            if op == 0:
                removed[f] += 1
            continue
        need(op == 0 or s not in dead_set,'remaining record reads discarded input')
        records.append([op,mapping[d],s if op == 0 else mapping[s],c,f,p])
    return keep,records,dict(sorted(removed.items()))

def execute(word,keep,records,backward=False,initial=None):
    n = len(keep)
    rows = ([{i:1} for i in range(n)]+[{}]) if initial is None else [r.copy() for r in initial]
    frames = [word['final' if backward else 'start'][i] for i in keep]+[None]
    dims = [cap.rank(word['lines'][j] for j in f) for f in word['frames']]
    masks = [sum(1 << j for j in f) for f in word['frames']]
    opened,copies,prefix = None,0,1
    profile,counts = Counter(),Counter()
    for op,d,s,c,f,p in reversed(records) if backward else records:
        counts[op] += 1
        if op == 0:
            old,new = (c,s) if backward else (s,c)
            lo,hi = (new,old) if backward else (old,new)
            need(frames[d] == old and not masks[lo] & ~masks[hi] and dims[hi]-dims[lo] == f > 0,'projected MOVE frame/rank')
            frames[d] = new
            profile[f] += 1
        elif op == 1:
            need(d < n and d != s and frames[d] == frames[s] == f and d != opened,'projected common-frame ADD or snapshot source mutation')
            rows[d] = scalar.add(rows[d],rows[s],-c if backward else c)
            prefix = max(prefix,sum(abs(v) for v in rows[d].values()))
        elif op == (3 if backward else 2):
            need(opened is None and s == n and not rows[n] and frames[n] is None,'projected fresh private field')
            need(d < 111 and frames[d] == c == 1 and not masks[f] & ~masks[c] and dims[c]-dims[f] == 1,'projected actual source cap COPY')
            rows[n],frames[n],opened = rows[d].copy(),f,d
            profile[1] += 1
            copies += 1
        else:
            need(op == (2 if backward else 3) and opened == d and s == n and rows[n] == rows[d] and frames[d] == c and frames[n] == f,'projected immutable snapshot ERASE')
            rows[n],frames[n],opened = {},None,None
    need(opened is None and not rows[n] and frames[n] is None and copies == 3,'projected private endpoint')
    need(frames[:n] == [word['start' if backward else 'final'][i] for i in keep],'retained physical endpoint frames')
    need(profile == Counter({1:1298,2:1342,3:79,4:44,5:93,6:11,7:9}),'projected paid profile')
    need(counts == Counter({0:2873,1:13223,2:3,3:3}),'projected literal record counts')
    return rows,{'prefix_row_l1':prefix,'profile':dict(sorted(profile.items())),
                 'rank_mass':sum(k*v for k,v in profile.items()),'copies':copies,
                 'counts':dict(sorted(counts.items()))}

def binary_rank(rows):
    basis = {}
    for row in rows:
        while row:
            p = row.bit_length() - 1
            if p not in basis:
                basis[p] = row
                break
            row ^= basis[p]
    return len(basis)

def binary_product(a, b):
    output = []
    for row in a:
        value = 0
        for i, other in enumerate(b):
            if row >> i & 1:
                value ^= other
        output.append(value)
    return output

def matrices(raw, meta):
    rows = [1 << i for i in range(660)]
    for phase in ("D", "A"):
        for _, dst, sources in raw[phase]:
            for src in sources:
                rows[dst] ^= rows[src]
    mask = (1 << 111) - 1
    need(all(not(rows[j] & (((1 << 111)-1) << 111)) for j in raw["ret"]), "retained target dependency")
    R = [rows[j] & mask for j in raw["ret"]]
    K = [sum(1 << j for j in subset) for subset in raw["scatter"]]
    M = binary_product(R, K)
    J = [(1 << i) ^ r for i, r in enumerate(binary_product(K, R))]
    need((R, K, M, J) == tuple(meta[k] for k in ("R", "K", "M", "J")), "actual raw R/K/J binding")
    need(M == [507,135,238,349,185,437,205,503,425], "actual quotient matrix")
    need(binary_rank(R) == binary_rank(M) == 9 and binary_rank(J) == 108, "actual ranks")
    eye = [1 << i for i in range(111)]
    A, inv, Q = (meta[k] for k in ("H", "Hinv", "Q"))
    direct_A = [eye[i] if i < 3 else J[i] for i in range(111)]
    need(A == direct_A and A[:3] == [1,2,4], "actual row-deletion source code")
    N = [(1 << i) ^ row for i,row in enumerate(M)]
    S = [sum(((row >> p) & 1) << p for p in range(3)) for row in R]
    D = K[:3]
    Y = [a ^ b for a,b in zip(N,binary_product(S,D))]
    B0 = meta["B0"]
    need(Y == [10,373,282,165,176,405,356,145,166] and binary_rank(Y) == 9, "invertible actual quotient")
    need(binary_product(B0,N) == [0]*3 and binary_product(B0,S) == [1,2,4], "left-null section")
    need(binary_product(B0,Y) == D and meta["Y"] == Y and meta["D"] == D, "quotient repair identity")
    need(binary_product(A, inv) == binary_product(inv, A) == eye, "source-code inverse")
    need(binary_product(J, inv) == [a ^ b for a,b in zip(eye,Q)], "section equation")
    need([i for i,r in enumerate(Q) if r] == [0,1,2] and binary_rank(Q) == 3, "three actual target rows")
    need(binary_rank([a ^ b for a,b in zip(A,eye)]) == 9, "source-code rank")
    return A, inv

def source_code(records):
    code = [r for r in records if r[0] == 1 and r[5] in (21,22,23,24)]
    need(len(code) == 1499, "complete source-code gates")
    forward, reverse = scalar.identity(111), scalar.identity(111)
    for _, x, y, c, frame, phase in code:
        need(x < 111 and y < 111 and frame == 1, "source-only code")
        forward[x] = scalar.add(forward[x], forward[y], c)
    for _, x, y, c, frame, phase in reversed(code):
        reverse[x] = scalar.add(reverse[x], reverse[y], -c)
    return forward[:111], reverse[:111]

def endpoints(forward, reverse, records, A, inv):
    az, azi = source_code(records)
    need(forward[:111] == az and reverse[:111] == azi, "exact integer source and inverse")
    need(scalar.parity(az) == A and scalar.parity(azi) == inv, "source parity binding")
    n = len(forward) - 1
    eye = scalar.identity(n)
    for i in range(222,n):
        need(forward[i] == reverse[i] == eye[i], "arbitrary dirty helper restoration")
    for rows in (forward, reverse):
        for p in range(111):
            need({j:c for j,c in rows[111+p].items() if 111 <= j < 222} == {111+p:1}, "target identity block")
            need(all(c % 2 == 0 for j,c in rows[111+p].items() if j >= 222), "target even helper leakage")
    expected_f = [1 << i for i in range(n)] + [0]
    expected_r = expected_f[:]
    for i in range(111):
        expected_f[i], expected_f[111+i] = A[i], expected_f[111+i] ^ A[i]
        expected_r[i], expected_r[111+i] = inv[i], expected_r[111+i] ^ (1 << i)
    need(scalar.parity(forward) == expected_f and scalar.parity(reverse) == expected_r, "all 651 F2 endpoint columns")

def rejection(label, fn):
    try:
        fn()
    except ValueError:
        return label
    raise ValueError("Defect control escaped: " + label)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    expected = json.loads((HERE / "EXPECTED.json").read_bytes())
    source = args.repo / expected["source_word"]
    need(hashlib.sha256(source.read_bytes()).hexdigest() == expected["source_sha256"], "original native source hash")
    raw = json.loads(gzip.decompress(source.read_bytes()))
    word = json.loads(gzip.decompress((args.out / "BIT-PRUNED-WORD.json.gz").read_bytes()))
    support = json.loads(gzip.decompress((args.out / "support/BIT-SUPPORT-WORD.json.gz").read_bytes()))
    keep, projected_records, removed = projected(support)
    need(len(keep) == 651 and removed == {1:27,5:9}, "complete unread-family projection")
    need(word["records"] == projected_records and word["public_registers"] == word["private_register"] == 651, "complete literal projected word")
    need(word["deleted_public_families"] == list(range(471,480)), "deleted physical identities")
    need(word["start"] == [raw["start"][i] for i in keep] and word["final"] == [raw["final"][i] for i in keep], "projected actual boundary frames")
    meta = json.loads((args.out / "support/BIT-SUPPORT.json").read_bytes())["matrices"]
    need(hashlib.sha256(cap.canonical(meta)).hexdigest() == expected["source_matrix_sha256"], "complete final matrix payload")
    A, inv = matrices(raw, meta)
    records = word["records"]
    forward, fwd = execute(raw, keep, records)
    reverse, rev = execute(raw, keep, records, True)
    endpoints(forward, reverse, records, A, inv)
    roundtrip, _ = execute(raw, keep, records, True, forward)
    need(roundtrip == scalar.identity(651), "full integer roundtrip")
    projectors = cap.address_identities(raw)
    need([r[1] for r in records if r[0] == 2] == [0,1,2], "actual source pivots")
    need(fwd["prefix_row_l1"] == 34285 and rev["prefix_row_l1"] == 5839860, "exact local integer prefix norms")
    sign_records = [r[:3]+[-r[3]]+r[4:] if r[0] == 1 and r[5] == 33 else r[:] for r in records]
    bad_sign, _ = execute(raw, keep, sign_records)
    need(scalar.parity(bad_sign) == scalar.parity(forward) and bad_sign[:111] != forward[:111], "sign defect distinguished beyond parity")
    controls = ["wrong_integer_unprepare_sign"]
    controls.append(rejection("omit_pivot_unprepare", lambda: execute(raw,keep,[r for r in records if not(r[0] == 1 and r[5] == 33)])))
    bad = [r[:] for r in records]
    position = next(i for i,r in enumerate(bad) if r[0] == 2)
    bad[position][4] = 1
    controls.append(rejection("FULL_to_FULL_copy", lambda: execute(raw,keep,bad)))
    bad = [r[:] for r in records]
    position = next(i for i,r in enumerate(bad) if r[0] == 2)
    pivot = bad[position][1]
    bad.insert(position+1,[1,pivot,(pivot+1)%111,1,1,99])
    controls.append(rejection("mutate_live_source", lambda: execute(raw,keep,bad)))
    controls.append(rejection("reuse_noninvolutive_code_as_inverse", lambda: endpoints(forward, reverse, records, A, A)))
    wrong = dict(meta)
    wrong["Q"] = meta["Q"][:]
    wrong["Q"][0] ^= 1
    controls.append(rejection("wrong_section_query", lambda: matrices(raw,wrong)))
    bad_support = dict(support, records=support["records"]+[[1,111,471,1,0,99]])
    controls.append(rejection("read_deleted_family", lambda: projected(bad_support)))
    result = {"status":"PASS_INDEPENDENT_LOCAL_SIGNED_NATIVE", "columns":651, "dirty_helpers":429,
              "source_code_rank":9, "clean_target_rank":108, "minimal_repair_rows_in_fixed_class":3,
              "forward":fwd, "inverse":rev, "projectors":len(projectors), "address_columns":3552,
              "frame_bindings":222, "deleted_original_families":list(range(471,480)), "removed_profile":removed, "projector_hashes":projectors, "controls":controls,
              "integer_target_contract":"y+T_Z x+E_Z h; T_Z mod2=A and E_Z even", "no_new_kappa":True}
    (args.out / "INDEPENDENT.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:result[k] for k in ("status","columns","dirty_helpers","source_code_rank","projectors","controls","no_new_kappa")},sort_keys=True))

if __name__ == "__main__":
    main()
