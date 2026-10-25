#!/usr/bin/env python3
"""Portable signed-literal provider and exact native-format admission.

This is a NEW provider interface, not an unchanged old A/scatter/B/C exporter.
It verifies signed local columns, literal COPY cleanup, native frame legality,
five/nine/eleven-stage Boolean columns, and the declared precision bill.
With --output it also emits the old raw6 binary/state/frame schema.
No original acceptance predicate is disabled or edited.
Python 3.12 standard library; no network, Git, or unpinned imports.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from math import gcd
from pathlib import Path
import argparse
import gzip
import json
import struct

BASE = "12fa8c5c844be21bfefb38a19503fbd867a11244"
ROOT = Path(__file__).resolve().parent
INPUTS = {
    "WORD.json.gz": "c46ccd7d3eedabc6a7efbb1a91ec13f2928bad8ee0bac57c6e593a092d13d96c",
    "GEOMETRY.json.gz": "a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022",
}
NATIVE_INPUTS = {
    "legality_h.cpp": "6c1ef2b24e57781d6951c172a1024fc4300e6fd392c9d6672079a7806ab663b3",
    "columns_k.cpp": "1c344d18fcd494eeca93e259f10cafae7705780e6592f6dcb35b34752dab9bc2",
    "json.hpp": "aaf127c04cb31c406e5b04a63f1ae89369fccde6d8fa7cdda1ed4f32dfc5de63",
    "stage_cohort.py": "6c288f6f234b528c1a7c0a4adfb724e91e0fe6b18c8dffad96af3f973de1829a",
    "bits/stdc++.h": "420094be2af295eed03a983dd66debbbe9cfb78d8252859f4498a615a0074b99",
}
WORD_HASHES = {
    "baseline": "fab5e51011239a13a79307f1d079551eef38387a45c9ab315ab6bc83aced8de2",
    "candidate": "5f301f0d668ded1028b7603c5ea9c88271e390fb9060ce8e118aad7d9927a7fd",
}
N, V, R, H = 660, 111, 438, 8


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return sha256(canonical(value)).hexdigest()


def write(path, value):
    path.write_bytes(canonical(value) + b"\n")


def rref(rows):
    a = [list(map(Q, row)) for row in rows]
    pivots, rank = [], 0
    for col in range(H):
        k = next((k for k in range(rank, len(a)) if a[k][col]), None)
        if k is None:
            continue
        a[rank], a[k] = a[k], a[rank]
        factor = a[rank][col]
        a[rank] = [v/factor for v in a[rank]]
        for k in range(len(a)):
            if k != rank:
                factor = a[k][col]
                a[k] = [v-factor*w for v,w in zip(a[k], a[rank])]
        pivots.append(col)
        rank += 1
        if rank == len(a):
            break
    return a[:rank], pivots


def integer_row(row):
    den = 1
    for x in row:
        den = den*x.denominator//gcd(den,x.denominator)
    result = [int(den*x) for x in row]
    common = 0
    for x in result:
        common = gcd(common, abs(x))
    return [x//common for x in result] if common else result


def determinant(matrix):
    """Exact elimination, independent of the frame-basis row reduction."""
    rows = [list(map(Q, row)) for row in matrix]
    result = Q(1)
    for j in range(len(rows)):
        pivot = next((k for k in range(j, len(rows)) if rows[k][j]), None)
        if pivot is None:
            return Q(0)
        if pivot != j:
            rows[j], rows[pivot] = rows[pivot], rows[j]
            result = -result
        factor = rows[j][j]
        result *= factor
        for k in range(j+1, len(rows)):
            ratio = rows[k][j]/factor
            for l in range(j+1, len(rows)):
                rows[k][l] -= ratio*rows[j][l]
    return result


def gram_audit(frames):
    """The integer frame bases stay nondegenerate in every odd characteristic."""
    histogram = Counter()
    for frame in frames.values():
        for key in ("A", "B"):
            basis = frame[key]
            gram = [[sum(x*y for x,y in zip(u,v)) for v in basis] for u in basis]
            det = determinant(gram)
            need(det.denominator == 1 and det > 0, "positive integer Gram determinant")
            integer = int(det)
            need(integer & (integer-1) == 0, "Gram determinant has an odd prime divisor")
            histogram[integer] += 1
    need(histogram == {1:56, 4:652, 16:500, 64:64}, "complete frame Gram inventory")
    return {"frames":len(frames), "basis_and_annihilator_Grams":2*len(frames),
            "determinant_histogram":dict(sorted(histogram.items())),
            "nondegenerate_over_every_odd_characteristic":True}


def frame_bank(geometry):
    frames = {}
    for i, labels in enumerate(geometry["frames"]):
        roots = [geometry["lines"][j] for j in labels]
        basis, pivots = rref(roots)
        # A primitive RREF basis alone does not prove reduction preserves the
        # span of the original root rows. Check an actual independent root
        # subset as well; its Gram determinant has no odd prime divisor.
        root_basis=[]
        for row in roots:
            trial=root_basis+[row]
            if len(rref(trial)[0]) > len(root_basis):
                root_basis=trial
        root_gram=[[sum(x*y for x,y in zip(u,v)) for v in root_basis]
                   for u in root_basis]
        root_det=determinant(root_gram)
        need(root_det.denominator == 1 and root_det > 0
             and int(root_det)&(int(root_det)-1) == 0,
             "original root span has an odd-characteristic exception")
        need(len(root_basis) == len(basis), "original root basis rank")
        annihilator = []
        for free in range(H):
            if free in pivots:
                continue
            row = [Q(k == free) for k in range(H)]
            for j,p in enumerate(pivots):
                row[p] = -basis[j][free]
            annihilator.append(integer_row(row))
        b = [integer_row(row) for row in basis]
        need(len(b)+len(annihilator)==H, "frame dimensions")
        need(all(sum(x*y for x,y in zip(u,v)) == 0 for u in b for v in annihilator),
             "integer annihilator")
        frames[str(i)] = {"dim": len(b), "B": b, "A": annihilator}
    return frames


def signed_replay(events, initial=None):
    """Every ordinary input gets its own integer column; private starts zero.

    MOVE changes the physical frame only. In the common-frame decoded chart,
    the exact signed ADD/COPY/ERASE recurrence is the integer recurrence below.
    No reduction modulo two occurs in this function.
    """
    identity = [{i:1} for i in range(N)]+[{}]
    rows = [dict(row) for row in (identity if initial is None else initial)]
    need(len(rows) == N+1 and rows[N] == {}, "signed private starts literally zero")
    peak_l1, peak_coefficient, copies, opened = 1, 1, 0, None
    for e in events:
        op,d = e[:2]
        if op == 0:
            need(opened is None, "signed no recursive MOVE in a live COPY")
        elif op == 1:
            _,d,s,c,_,_ = e
            need(d != opened and d != s and c in (-1,1), "signed immutable COPY source")
            need(s != N or opened is not None, "signed private read outside COPY")
            row = rows[d]
            for col,value in rows[s].items():
                total = row.get(col,0)+c*value
                if total:
                    row[col] = total
                else:
                    row.pop(col,None)
            peak_l1 = max(peak_l1,sum(map(abs,row.values())))
            peak_coefficient = max(peak_coefficient,max(map(abs,row.values()),default=0))
        elif op == 2:
            need(opened is None and rows[N] == {}, "signed literal COPY zero")
            rows[N],opened = dict(rows[d]),d
            copies += 1
        else:
            need(op == 3 and opened == d, "signed ERASE source guard")
            need(rows[N] == rows[d], "signed integer ERASE equality")
            rows[N],opened = {},None
    need(opened is None and rows[N] == {}, "signed private ends literally zero")
    return rows, {"independent_integer_columns":N, "COPY_episodes":copies,
                  "literal_integer_ERASE_equalities":copies, "private_zero":True,
                  "signed_row_l1_peak":peak_l1, "coefficient_peak":peak_coefficient}


def signed_checks(programs):
    identity = [{i:1} for i in range(N)]+[{}]
    outputs, report = {}, {}
    for orientation in ("forward","reverse"):
        rows, stats = signed_replay(programs[orientation])
        for i in list(range(V))+list(range(2*V,N)):
            need(rows[i] == identity[i], "signed exact source/helper restoration")
        for i in range(V,2*V):
            reduced = {j:1 for j,c in rows[i].items() if c%2}
            need(reduced == {i:1,i-V:1}, "signed public Boolean shear")
        stats["exact_source_rows"] = V
        stats["exact_helper_rows"] = R
        stats["public_boundary_domain"] = "integer lift; specified shear modulo two"
        stats["integer_output_sha256"] = digest(rows)
        outputs[orientation],report[orientation] = rows,stats
    for first,last in (("forward","reverse"),("reverse","forward")):
        restored,_ = signed_replay(programs[last], outputs[first])
        need(restored == identity, "signed complete inverse composition")
    report["both_integer_inverse_orders"] = True
    return outputs,report


def candidate(records):
    retired = {53,20255,20256,23408,23409,33620}
    moved = {23405,23406,23407,23515,24189,24190,24515}
    need(records[23889] == [3,476,660,515,0,3], "closed COPY insertion anchor")
    need(records[33619] == [0,469,517,1,1,32], "retained terminal return")
    out = []
    for i,r in enumerate(records):
        if i == 33619:
            out.append([0,469,0,517,7,32])
        if i not in retired|moved and not (r[0]==1 and r[5]==10 and r[2]==469):
            out.append(r)
        if i == 23889:
            out.extend(records[j] for j in (24189,24190,24515))
            out.append([1,413,50,1,509,2])
            out.extend(records[j] for j in (23405,23406,23407,23515))
    return out


def lower(records):
    out = []
    for op,d,s,c,f,section in records:
        native_last = 7 if op == 2 else 0 if op in (0,3) else section
        out.append([op,d,s,c,f,native_last])
    return out


def local_program(raw, reverse):
    events = []
    for op,d,s,c,f,z in reversed(raw) if reverse else raw:
        if op == 0:
            before,after = (c,s) if reverse else (s,c)
            events.append([0,d,before,after,f,int(reverse)])
        elif op == 1:
            events.append([1,d,s,-c if reverse else c,f,int(reverse)])
        elif op == (3 if reverse else 2):
            events.append([2,d,s,c,f,7,int(reverse)])
        else:
            need(op == (2 if reverse else 3), "native opcode")
            events.append([3,d,s,c,f,z,int(reverse)])
    return events


def local_check(events, word, frames, reverse):
    state = list(word["final"] if reverse else word["start"]) + [None]
    values = [1<<i for i in range(N)] + [0]
    norm = [1]*N + [0]
    opened, peak, hist, adds, copies = None, 1, Counter(), 0, 0
    for e in events:
        op,d,s = e[:3]
        need(0 <= d < N and 0 <= s <= max(N,len(frames)), "native destination")
        if op == 0:
            _,d,old,new,rank,flag = e
            need(opened is None and state[d]==old, "native MOVE access")
            a,b = frames[str(old)],frames[str(new)]
            low,high = (b,a) if reverse else (a,b)
            need(high["dim"]-low["dim"]==rank>0 and rank<H, "native recursive rank")
            need(all(sum(x*y for x,y in zip(u,v))==0 for u in low["B"] for v in high["A"]),
                 "native nested MOVE")
            state[d] = new
            hist[rank] += 1
        elif op == 1:
            _,d,s,c,f,flag = e
            need(0<=s<=N and d!=s and c in (-1,1), "native signed ADD")
            need(state[d]==state[s]==f, "native ADD frame")
            need(d!=opened and (s!=N or opened is not None), "native copy immutable")
            values[d] ^= values[s]
            norm[d] += norm[s]
            peak = max(peak,norm[d])
            adds += 1
        elif op == 2:
            _,d,s,c,f,rank,flag = e
            need(s==N and opened is None and values[N]==0 and state[N] is None,
                 "native COPY zero")
            need(state[d]==c and f==0 and frames[str(c)]["dim"]==rank==7,
                 "native COPY tariff")
            values[N],norm[N],state[N],opened = values[d],norm[d],f,d
            hist[rank] += 1
            copies += 1
        else:
            _,d,s,c,f,z,flag = e
            need(op==3 and s==N and opened==d and state[d]==c and state[N]==f,
                 "native ERASE guard")
            need(values[N]==values[d], "native ERASE equality")
            need(z==(7 if reverse else 0), "native ERASE record convention")
            values[N],norm[N],state[N],opened = 0,0,None,None
        need(flag==int(reverse), "native orientation flag")
    expected = [(1<<i)^((1<<(i-V)) if V<=i<2*V else 0) for i in range(N)]+[0]
    need(values==expected and opened is None, "native full Boolean boundary")
    need(state==list(word["start"] if reverse else word["final"])+[None], "native final frames")
    need(copies==9, "native COPY count")
    return {"orientation":"reverse" if reverse else "forward", "columns":N,
            "ADDs":adds, "COPYs":copies, "histogram":dict(sorted(hist.items())),
            "positive_prefix_bound":peak, "events_sha256":digest(events)}


def bridge_recipe(k):
    stages = 2*k+1
    active, reverse = [], []
    after = [[] for _ in range(stages)]
    for stage in range(stages):
        p = 0 if stage<3 else (stage-1)//2
        rev = stage==1 or (stage>=3 and stage%2==1)
        active.append((2*p+1,2*p) if rev else (2*p,2*p+1))
        reverse.append(rev)
    for p in range(1,k):
        after[2*p-1].extend([(2*p-2,2*p,1),(2*p+1,2*p-1,-1)])
        after[2*p].extend([(2*p+1,2*p-1,1),(2*p-2,2*p,-1)])
    for p in range(k-1,0,-1):
        after[-1].extend([(2*p-1,2*p+1,-1),(2*p,2*p-2,1)])
    return active,reverse,after


def bridged_check(programs,k,skip=None):
    active,reverse,after = bridge_recipe(k)
    total = 2*k*V+R
    values = [1<<i for i in range(total)]+[0]
    temp = total
    bridge_index = 0
    for stage,(source_bank,target_bank) in enumerate(active):
        def owner(i):
            if i==N:
                return temp
            if i<V:
                return source_bank*V+i
            if i<2*V:
                return target_bank*V+i-V
            return 2*k*V+i-2*V
        opened = None
        events = programs["reverse" if reverse[stage] else "forward"]
        for e in events:
            op = e[0]
            if op==0:
                continue
            d,s = owner(e[1]),owner(e[2])
            if op==1:
                values[d] ^= values[s]
            elif op==2:
                need(opened is None and values[temp]==0, "bridged private zero")
                values[temp],opened = values[d],d
            else:
                need(opened==d and values[temp]==values[d], "bridged ERASE equality")
                values[temp],opened = 0,None
        need(opened is None, "bridged COPY closure")
        for d,s,c in after[stage]:
            if bridge_index != skip:
                for i in range(V):
                    values[d*V+i] ^= values[s*V+i]
            bridge_index += 1
    for pair in range(k):
        for i in range(V):
            a,b=2*pair*V+i,(2*pair+1)*V+i
            values[a],values[b] = values[b],values[a]
    expected=[1<<i for i in range(total)]+[0]
    if skip is not None:
        need(values != expected, "omitted bridge control accepted")
        return
    need(values==expected, "bridged all-column endpoint")
    need(bridge_index==6*(k-1), "bridged count")
    return {"stages":2*k+1,"formal_columns":total,"helper_columns":R,
            "private_zero":True,"bridge_ADDs":6*(k-1)*V,
            "COPY_episodes":9*(2*k+1),"omitted_bridge_controls":bridge_index}


def precision(forward,reverse):
    p5 = 64*forward**3*reverse**2
    p9 = 2**18*forward**5*reverse**4
    return {"forward_majorant":forward,"reverse_majorant":reverse,
            "local_bound":str(p5),"local_bits":p5.bit_length(),
            "local_precision_charge":64*((p5.bit_length()+63)//64),
            "nine_bound":str(p9),"nine_bits":p9.bit_length(),
            "nine_precision_charge":64*((p9.bit_length()+63)//64),
            "old_104_local_cap_passes":p5<2**104,"old_192_nine_cap_passes":p9<2**192,
            "new_local_128_cap_passes":p5<2**128,"new_nine_256_cap_passes":p9<2**256}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,
                        help="emit native files into a new directory (default: no writes)")
    args=parser.parse_args()
    if args.output is not None:
        args.output.mkdir(parents=True,exist_ok=False)
    data={}
    for name,pin in INPUTS.items():
        raw=(ROOT/"inputs"/name).read_bytes()
        need(sha256(raw).hexdigest()==pin,"input pin "+name)
        data[name]=json.loads(gzip.decompress(raw))
    for name,pin in NATIVE_INPUTS.items():
        raw=(ROOT/"inputs"/"native"/name).read_bytes()
        need(sha256(raw).hexdigest()==pin,"native source pin "+name)
    word,geometry=data["WORD.json.gz"],data["GEOMETRY.json.gz"]
    frames=frame_bank(geometry)
    need(Counter(frames[str(f)]["dim"] for f in word["final"][222:])=={8:433,4:5},
         "heterogeneous terminal contract")
    report={"provider":"signed-framed-literal-v1","source_base":BASE,"input_pins":INPUTS,
            "native_source_pins":NATIVE_INPUTS, "frame_Gram_audit":gram_audit(frames),
            "physical_compiler_run":False,"old_interface_H1_H5_claimed":False,
            "old_104_bit_scalar_checker_pass_claimed":False,"words":{}}
    signed_outputs={}
    for name,records in (("baseline",word["records"]),("candidate",candidate(word["records"]))):
        need(digest(records)==WORD_HASHES[name],"final PR4183 literal word pin")
        raw=lower(records)
        need(all(a[:5] == b[:5] for a,b in zip(records,raw)), "literal lowering preserves operations")
        blob=b"".join(struct.pack("<6i",*r) for r in raw)
        state={"n":N,"v":V,"R":R,"h":H,"ZERO":0,
               "initial":{str(i):f for i,f in enumerate(word["start"])},
               "final":{str(i):f for i,f in enumerate(word["final"])},
               "retained_totals":geometry["ret"],"source_owned_roles":[],"regs":[],
               "provider_contract":"signed-framed-literal-v1"}
        programs={key:local_program(raw,rev) for key,rev in (("forward",False),("reverse",True))}
        checks={key:local_check(programs[key],word,frames,rev) for key,rev in (("forward",False),("reverse",True))}
        signed_outputs[name],integer_checks=signed_checks(programs)
        if args.output is not None:
            dest=args.output/name
            dest.mkdir()
            (dest/"249-records.bin").write_bytes(blob)
            write(dest/"249-states.json",state)
            write(dest/"frames.json",{"frames":frames})
            write(dest/"LOCAL-PROGRAMS.json",programs)
        bridge={}
        for k in (2,4,5):
            bridge[str(2*k+1)]=bridged_check(programs,k)
            for skip in range(6*(k-1)):
                bridged_check(programs,k,skip)
        hist=checks["forward"]["histogram"]
        report["words"][name]={"literal_word_sha256":digest(records),"native_raw6_sha256":sha256(blob).hexdigest(),
            "emitted_file_sha256":{
                "249-records.bin":sha256(blob).hexdigest(),
                "249-states.json":sha256(canonical(state)+b"\n").hexdigest(),
                "frames.json":sha256(canonical({"frames":frames})+b"\n").hexdigest(),
                "LOCAL-PROGRAMS.json":sha256(canonical(programs)+b"\n").hexdigest()},
            "records":len(raw),"ADDs":checks["forward"]["ADDs"],"paid_queries":sum(hist.values()),
            "rank_mass":sum(r*n for r,n in hist.items()),"local_checks":checks,
            "signed_integer_checks":integer_checks,
            "precision":precision(checks["forward"]["positive_prefix_bound"],checks["reverse"]["positive_prefix_bound"]),
            "bridged_scalar_checks":bridge}
    changes=[]
    for i,(a,b) in enumerate(zip(signed_outputs["baseline"]["forward"],
                                  signed_outputs["candidate"]["forward"])):
        delta={j:b.get(j,0)-a.get(j,0) for j in a.keys()|b.keys()
               if b.get(j,0) != a.get(j,0)}
        if delta:
            need(V <= i < 2*V and delta == {469:-2}, "exact changed integer public lift")
            changes.append(i)
    need(len(changes) == 51, "exact integer public difference count")
    report["candidate_integer_lift_difference"]={
        "column":469, "coefficient":-2, "targets":changes,
        "other_integer_outputs_unchanged":True}
    report["status"]="PASS_SIGNED_LITERAL_PROVIDER_AND_BRIDGED_BOOLEAN_COLUMNS"
    report["native_CXX_executed"]=False
    report["no_new_kappa"]=True
    if args.output is not None:
        write(args.output/"NATIVE-PROVIDER.json",report)
    print(json.dumps(report,sort_keys=True,indent=2))


if __name__=="__main__":
    main()
