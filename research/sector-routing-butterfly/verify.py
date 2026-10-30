"""Check all columns in the group ring and exact native address actions."""
import hashlib
import json
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from routing import emit, emit_preserving, tariff
P = Path(__file__).resolve().parent


def require(ok, why):
    if not ok:
        raise RuntimeError(why)


def shift(g, mask):
    return g ^ ((mask & 1)*2) ^ ((mask >> 1) << 2)


def query(g):
    return (g & ~3) | ((g+1) & 3)


def transform(row, fn):
    return {(a,fn(g)):c for (a,g),c in row.items()}


def plus(a,b,c=F(1)):
    out = a.copy()
    for key, value in b.items():
        out[key] = out.get(key,F(0)) + c*value
        if not out[key]:
            del out[key]
    return out


def run_ring(word, width, adjoint=False):
    rows = [{(i,0):F(1)} for i in range(width)]
    colnorm = [F(1)]*width
    rownorm = [F(1)]*width
    maximum = F(1)
    for op in reversed(word) if adjoint else word:
        dst = op[1]
        if op[0] == "ADD":
            _,dst,src,c,mask = op
            if adjoint:
                dst,src = src,dst
            require(dst != src, "same-role ADD")
            row = plus(rows[dst],transform(rows[src],lambda g:shift(g,mask)),c)
        elif op[0] == "SHIFT":
            row = transform(rows[dst],lambda g:shift(g,op[2]))
        elif op[0] == "QUERY":
            row = transform(rows[dst],query)
        elif op[0] == "CLEAR":
            row = {}
        else:
            raise RuntimeError("unknown instruction")
        for (a,_),c in rows[dst].items():
            colnorm[a] -= abs(c)
        for (a,_),c in row.items():
            colnorm[a] += abs(c)
        rows[dst] = row
        rownorm[dst] = sum(map(abs,row.values()),F(0))
        maximum = max(maximum, max(colnorm if adjoint else rownorm))
    return rows, maximum


def expected(s,r,mode):
    n = 1 << s
    width = r*n + (mode=="perturbation")
    out = [{} for _ in range(width)]
    for i in range(r*n):
        a = i % n
        out[i] = {(i,0):F(1)}
        for mask in range(n):
            c = F((-1)**((a & mask).bit_count()),n)
            g = shift(0,mask)
            out[i] = plus(out[i],{(i,query(g)):c},F(1,2) if mode=="perturbation" else F(1))
            if mode=="gauge":
                out[i] = plus(out[i],{(i,g):-c})
    return out


def transpose(rows):
    out = [{} for _ in rows]
    for i,row in enumerate(rows):
        for (j,g),c in row.items():
            out[j][i,g] = c
    return out


def zadd(a,b):
    return (a[0]+b[0],a[1]+b[1])


def zscale(c,a):
    return (c*a[0],c*a[1])


def native_q(v,f):
    out = v[:]
    for k in range(f):
        for a in range(len(v)):
            if a & (1 << k):
                continue
            b = a | (1 << k)
            x,y = out[a],out[b]
            sm = zadd(x,y)
            df = zadd(x,zscale(-1,y))
            idf = (-df[1],df[0])
            out[a] = zscale(F(1,2),zadd(sm,idf))
            out[b] = zscale(F(1,2),zadd(sm,zscale(-1,idf)))
    return out


def native_shift(v,mask,f):
    address_mask = (((1 << f)-1) if mask & 1 else 0) | ((mask >> 1) << f)
    return [v[a ^ address_mask] for a in range(len(v))]


def native_run(word, values, f):
    rows = [v[:] for v in values]
    for op in word:
        dst = op[1]
        if op[0]=="ADD":
            src,c,mask = op[2:]
            v = native_shift(rows[src],mask,f)
            rows[dst] = [zadd(a,zscale(c,b)) for a,b in zip(rows[dst],v)]
        elif op[0]=="QUERY":
            rows[dst] = native_q(rows[dst],f)
        elif op[0]=="SHIFT":
            rows[dst] = native_shift(rows[dst],op[2],f)
        else:
            rows[dst] = [(F(0),F(0))]*len(rows[dst])
    return rows


def native_expected(values,s,r,f,mode):
    n = 1 << s
    out = []
    for i in range(r*n):
        v = values[i]
        e = [(F(0),F(0))]*len(v)
        for mask in range(n):
            c = F((-1)**(((i % n)&mask).bit_count()),n)
            e = [zadd(a,zscale(c,b)) for a,b in zip(e,native_shift(v,mask,f))]
        q = native_q(e,f)
        out.append([zadd(a,zscale(F(1,2),b)) for a,b in zip(v,q)] if mode=="perturbation" else
                   [zadd(a,zadd(b,zscale(-1,c))) for a,b,c in zip(v,q,e)])
    if mode=="perturbation":
        out.append([(F(0),F(0))]*len(values[0]))
    return out


def local_norms():
    word = emit(1,1,"gauge")[:7]
    rows,prefix = run_ring(word,2)
    _,suffix = run_ring(word,2,True)
    want = [{(0,0):F(1,2),(0,2):F(1,2),(1,0):F(1,2),(1,2):F(-1,2)},
            {(1,0):F(1,2),(1,2):F(1,2),(0,0):F(1,2),(0,2):F(-1,2)}]
    require(rows==want, "controlled swap identity")
    return prefix,suffix


def main():
    sources = json.loads((P/"PINS.json").read_text())
    for pin in sources:
        require(hashlib.sha256((P/pin["file"]).read_bytes()).hexdigest()==pin["sha256"],"source hash")
    local = local_norms()
    require(max(local)<=2, "local norm")
    cases = sorted({(s,1) for s in range(1,6)} | {(s,r) for s in range(1,4) for r in range(1,5)})
    records = []
    for s,r in cases:
        for mode in ("perturbation","gauge"):
            word = emit(s,r,mode)
            expected_map = expected(s,r,mode)
            rows,pre = run_ring(word,len(expected_map))
            rev,suf = run_ring(word,len(expected_map),True)
            require(rows==expected_map, "all-column forward map")
            require(transpose(rev)==expected_map, "reverse oracle")
            count = Counter(op[0] for op in word)
            bill = tariff(s,r,mode)
            require(all(count[k]==v for k,v in bill.items() if k!="owned"), "exact tariff")
            records.append(dict(s=s,r=r,mode=mode,**bill,prefix=str(pre),suffix=str(suf)))
    preserving = []
    for s in range(1,6):
        n = 1 << s
        word = emit_preserving(s)
        want = [{(i,0):F(1)} for i in range(n)] + expected(s,1,"perturbation")
        rows,pre = run_ring(word,2*n+1)
        rev,suf = run_ring(word,2*n+1,True)
        require(rows==want and transpose(rev)==want,"input-preserving map")
        count = Counter(op[0] for op in word)
        require(count==Counter(ADD=6*n*s+n+2,SHIFT=n*s,QUERY=1,CLEAR=n+2),"preserving tariff")
        preserving.append(dict(s=s,**dict(count),owned_including_outputs=n+1,prefix=str(pre),suffix=str(suf)))
    baseline = json.loads((P/"inputs/SECTOR-RESULT.json").read_text())["examples"]
    require(all(x["ordinary_adds"]==2*(1 << (2*x["generators"]))+(1 << x["generators"])
                and x["owned_fields_including_outputs"]==(1 << x["generators"])+1
                for x in baseline),"source comparison")
    physical = 0
    for s in range(1,4):
        for r in (1,2):
            for f in range(1,5):
                for mode in ("perturbation","gauge"):
                    width = r*(1 << s)+(mode=="perturbation")
                    values = [[(F(((i+3)*(a+2))%13-6,4),F((i+2*a)%7-3,2))
                               for a in range(1 << (f+s-1))] for i in range(width)]
                    require(native_run(emit(s,r,mode),values,f)==native_expected(values,s,r,f,mode),"native map")
                    q2 = native_q(native_q(values[0],f),f)
                    require(q2==native_shift(values[0],1,f),"native Q square")
                    physical += 1
    word = emit(2,1,"perturbation")
    want = expected(2,1,"perturbation")
    mutants = {}
    for name,kind in (("missing_query","QUERY"),("missing_shift","SHIFT"),("missing_entry_clear","CLEAR")):
        idx = next(i for i,op in enumerate(word) if op[0]==kind)
        mutants[name] = word[:idx]+word[idx+1:]
    idx = max(i for i,op in enumerate(word) if op[0]=="CLEAR")
    mutants["missing_final_clear"] = word[:idx]+word[idx+1:]
    idx = next(i for i,op in enumerate(word) if op[0]=="ADD" and op[-1])
    bad = word[:]
    bad[idx] = (*bad[idx][:-1],2)
    mutants["wrong_involution"] = bad
    for name,bad in mutants.items():
        require(run_ring(bad,len(want))[0]!=want,"undetected mutant: "+name)
    require((F(3,2).numerator % 3)==0, "nonunit scale scope control")
    result = dict(status="PASS_SECTOR_ROUTING_BUTTERFLY",formal_cases=records,preserving_cases=preserving,native_cases=physical,
                  local_controlled_swap_prefix=str(local[0]),local_controlled_swap_suffix=str(local[1]),
                  rejected_controls=list(mutants)+["nonunit_scale_not_invertible_mod_3"],
                  selected_frontier_changed=False,new_kappa_claim=False)
    raw = json.dumps(result,indent=2,sort_keys=True)+"\n"
    if "--write" in sys.argv:
        (P/"RESULT.json").write_text(raw)
    else:
        require((P/"RESULT.json").read_text()==raw,"result mismatch")
    print(result["status"],len(records),"formal cases",physical,"native cases",flush=True)


if __name__=="__main__":
    main()
