"""Separate adjoint, stream and rational-series checks for the emitted caller.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
This is a second implementation, not independent human review.
"""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import gzip
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import integration as L


def adjoint(modulus):
    base, frames, _ = L.source()
    data = L.read(L.R / "WORD.json.gz")
    owned = set(data["owned"])
    word = data["records"]
    geometry = L.SOURCE.Geometry(frames)
    point = tuple(v % modulus for v in (1, 3, 9, 27, 2, 6, 18, 54, 5, 15, 45, 34, 7, 21, 63, 88))
    fields = [{point: 1 << i} for i in range(len(data["start"]))]
    raw = [1 << i for i in range(len(data["start"]))]
    for e in reversed(word):
        op, d = e[:2]
        if op == "ADD":
            s = e[2]
            raw[s] ^= raw[d]
            for x, value in fields[d].items():
                fields[s][x] = fields[s].get(x, 0) ^ value
                if not fields[s][x]:
                    del fields[s][x]
        elif op in ["ERASE", "ZERO_Q", "INIT"]:
            # A zero-only header map has the total zero extension.
            L.need(d in owned or op=="ZERO_Q", "Only proved whole-zero maps extend to zero")
            raw[d] = 0
            fields[d] = {}
        else:
            L.need(op == "Q", "Adjoint opcode")
            residual = geometry.residual_mod(*e[2:], modulus)
            fields[d] = {geometry.move(residual, x, modulus): value for x, value in fields[d].items()}
    expected = [0 if i in owned else (1 << i) ^ ((1 << (i + 111)) if i < 111 else 0) for i in range(len(data["start"]))]
    L.need(raw == expected, "Every adjoint RAW/DIRTY column")
    for output, row in enumerate(expected):
        want = {}
        for source in L.bitids(row):
            x = geometry.move(geometry.project_mod(data["final"][source], modulus), point, modulus)
            x = geometry.move(geometry.project_mod(data["start"][output], modulus), x, modulus)
            want[x] = want.get(x, 0) ^ (1 << source)
        L.need(fields[output] == {x: v for x, v in want.items() if v}, "All adjoint physical columns")
    return modulus


def stream(corrupt=False):
    invoice = L.read(L.R / "INVOICE.json")
    n, own = invoice["originals"], invoice["owned_allocated"]
    values = [1 << i for i in range(n + own)]
    norms = [1] * (n + own)
    versions, epochs = [0] * (n + own), [0] * (n + own)
    sources = iter(L.read(L.R / "SOURCE-DESCRIPTORS.json.gz"))
    paid, ops, prefix, peak, used = Counter(), Counter(), sha256(), 1, 0
    with gzip.open(L.R / "GLOBAL.jsonl.gz", "rb") as handle:
        for event, line in enumerate(handle):
            e = json.loads(line)
            op, d = e[:2]
            ops[op] += 1
            if op == "ADD":
                values[d] ^= values[e[2]]
                norms[d] += norms[e[2]]
                peak = max(peak, norms[d])
                versions[d] += 1
            elif op == "OWNED_CLEAR":
                L.need(n <= d < n + own, "Only owned global erasure")
                values[d] = norms[d] = 0
                versions[d] += 1
                epochs[d] += 1
            elif op == "QUERY":
                item = next(sources)
                if corrupt and not used:
                    item["epoch"] += 1
                expected = {"event": event, "prefix_sha256": prefix.hexdigest(), "owner": d,
                            "rank": e[2], "version": versions[d], "epoch": epochs[d], "RAW_hex": hex(values[d])}
                L.need(all(item[k] == v for k, v in expected.items()), "Actual chronological query descriptor")
                used += 1
                paid[e[2]] += 1
                versions[d] += 1
            elif op in ["OWNED_ZERO_HEADER", "WHOLE_ZERO_FRAME"]:
                L.need(values[d] == 0 and (op=="WHOLE_ZERO_FRAME" or n<=d<n+own), "Whole zero global frame change")
            else:
                L.need(op == "PAID_PORT_ROUTE", "Known global event")
            prefix.update(line)
    L.need(next(sources, None) is None, "No unused source descriptor")
    L.need(values == [1 << i for i in range(n)] + [0] * own, "All global RAW and DIRTY columns")
    L.need(paid == {int(k): v for k, v in invoice["paid"].items()}, "Recounted global invoice")
    original_targets = L.read(L.S / "provider/data/TARGET-OWNERS.json")
    old_calls = L.read(L.S / "provider/data/CALLS.json")
    retired = {c["helper_owner_begin"] + h - 222 for c in old_calls for h in list(L.RETIRED)}
    targets = Counter(t["rank"] for t in original_targets if t["original_owner"] not in retired)
    targets[8]-=18;targets[4]+=36
    L.need(targets == {int(k): v for k, v in invoice["targets"].items()}, "Every retired target is debited")
    L.need(len(retired) == 396 and sum(targets.values()) == n == 11022 and own == 48, "Global ownership census")
    g = L.read(L.R / "GLOBAL-RESULT.json")
    L.need(prefix.hexdigest() == g["canonical_stream_sha256"] and ops == g["operation_counts"], "Recounted literal stream")
    L.need(peak.bit_length() == g["majorant_bits"] <= 1024, "Fresh precision envelope")
    return {"events": event + 1, "queries": used, "originals": n, "owned": own, "majorant_bits": peak.bit_length()}


def pricing():
    I=L.load("refinement_second_series",L.S/"ordinary-certificate/inputs/separate_series.py")
    invoice=L.read(L.R/"INVOICE.json");result=L.read(L.R/"ORDINARY-RESULT.json");glob=L.read(L.R/"GLOBAL-RESULT.json")
    paid,target=({int(k):v for k,v in invoice[name].items()} for name in ["paid","targets"])
    c,uniform,reserve=F(".00350771905977"),F(".00350771905976"),F(1,2**48)
    denominator=I.moment(target,1-c)
    alpha=I.div(I.moment(paid,1-c),denominator)
    gamma=I.div(I.moment(paid,1-c+F(1,5)),I.mul(I.power(17,F(1,5)),denominator))
    delta=I.div((F(11022*18),)*2,I.mul(I.power(17,c),denominator))
    L.need(alpha[1]<1-reserve and gamma[1]<F(31,32) and delta[1]<F(19,20),"Separate charged compiler tails")
    for name,interval in [("alpha",alpha),("gamma",gamma),("delta",delta)]:
        other=list(map(F,result['tail'][name]));L.need(max(interval[0],other[0])<=min(interval[1],other[1]),"Separate interval overlap")
    gap,h,v=(c-uniform)/2,F(1,64),2048;z0=1-(c+uniform)/2
    expression=(gap*(5+8*h)*v+1+8*v*(1-z0))/(h*gap)
    h0=expression.__floor__()+1;h1=(h0*(1-z0)/gap).__floor__()+1
    L.need([h0,h1]==[result['tail']['H0'],result['tail']['H1']],"Strict integer compiler thresholds")
    L.need(1-1/(1+v*reserve)-F(4,2**(v//32))>0,"Exact tensor contraction margin")
    cover=F(1,10**14);L.need(2**60*cover>256,"Paid regular cover and prime guard")
    c1=uniform-cover;backend=F(L.read(L.R/'prior/ORDINARY-RESULT.json')['admitted'])
    grid=10**15
    for level in result['finite_backend_levels']:
        a=F(99,100)*c1+F(1,100)*backend
        numerator=-((-a.numerator*grid)//a.denominator)-1;b=F(numerator,grid)
        L.need(backend<b<a<c1<F(1,100)<1-a,"Strict acyclic backend gaps")
        L.need([str(backend),str(a),str(b)]==[level[k] for k in ['completed_backend','ordinary_exact','admitted']],"Exact backend level")
        backend=b
    L.need(backend==F(3507719059749,10**15),"Complete ordinary saving")
    L.need(result['fee_bounds']['base_counts']['all_owned_allocated']==invoice['owned_allocated']==48,"Complete owned stock")
    ops=glob['operation_counts'];scans=sum(ops[k] for k in ['ADD','OWNED_CLEAR','OWNED_ZERO_HEADER','WHOLE_ZERO_FRAME'])+96
    parking=4*(11022+48)*56223;matcher=L.read(L.R/'MATCHER.json')
    terms=matcher['global_occurrences']*matcher['paired_address_coefficient_terms_per_call']+matcher['new_target_coefficient_terms']
    L.need(terms==5472+matcher['new_target_coefficient_terms'],"Every new residual matcher coefficient and both address halves")
    fee=scans+parking+7548+7248+72+glob['expanded_event_count']+56223*(32*127**2+8*127**3)+terms
    L.need(fee==result['fee_bounds']['base_counts']['coarse_primitive_count_with_dimension_work']<2**64,"All positive finite costs")
    L.need(not alpha[1]<1-F(1,10**7) and not F('.00350771905979')<c1,"Unfunded contraction and raw-as-ordinary controls")
    # The strict lower grid must also work when its argument is already on grid.
    on_grid=F(7,grid)
    L.need(F(-((-on_grid.numerator*grid)//on_grid.denominator)-1,grid)<on_grid,"Exact-grid strictness control")
    return dict(admitted=str(backend),H0=h0,H1=h1,positive_base_fee=fee,matcher_coefficient_terms=terms)


def main():
    result = {"status": "PASS_G20_CONJUGATION_SEPARATE_ADJOINT_STREAM_ORDINARY",
              "adjoint_moduli": [adjoint(m) for m in [101, 101 ** 2]], "global": stream(), "ordinary": pricing()}
    try:
        stream(corrupt=True)
    except ValueError:
        result["stale_query_epoch_rejected"] = True
    else:
        raise ValueError("Stale query epoch accepted")
    L.put("INDEPENDENT-RESULT.json", result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
