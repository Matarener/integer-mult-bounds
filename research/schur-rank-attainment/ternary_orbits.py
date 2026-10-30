"""Complete simultaneous-conjugacy partition of 2x2 ternary triples.
SHIN09-git, substantial OpenAI Codex assistance. Apache-2.0.
Independent of the Schur constructor; arithmetic is the subspace oracle.
"""
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
from types import ModuleType

path=Path(__file__).with_name("oracle.py")
o=ModuleType("orbit_oracle")
o.__file__=str(path)
exec(compile(path.read_bytes(),str(path),"exec"),o.__dict__)

def partition():
    matrices=[tuple(tuple(v[i*2:(i+1)*2]) for i in range(2))
              for v in product(range(3),repeat=4)]
    index={a:i for i,a in enumerate(matrices)}
    gl=[i for i,a in enumerate(matrices) if o.rank_vectors(a,3)==2]
    if len(gl)!=48:
        raise ValueError("GL2 F3 census")
    actions=[]
    for g in gl:
        inverse=o.inverse(matrices[g],3)
        row=[index[o.mm(o.mm(matrices[g],a,3),inverse,3)] for a in matrices]
        if sorted(row)!=list(range(81)) or {row[x] for x in gl}!=set(gl):
            raise ValueError("conjugation not a permutation")
        actions.append(row)
    # Independently verify composition of the full finite action table.
    position={g:i for i,g in enumerate(gl)}
    for gi,g in enumerate(gl):
        for hi,h in enumerate(gl):
            gh=index[o.mm(matrices[g],matrices[h],3)]
            if actions[position[gh]]!=[actions[gi][actions[hi][m]] for m in range(81)]:
                raise ValueError("conjugation action composition")
    def encode(a,b,h):
        return (a*81+b)*81+h
    seen=set()
    representatives=[]
    digest=sha256()
    sizes={}
    for a in gl:
        for b in gl:
            for h in range(81):
                key=encode(a,b,h)
                if key in seen:
                    continue
                orbit=sorted({encode(row[a],row[b],row[h]) for row in actions})
                if key!=min(orbit) or seen.intersection(orbit):
                    raise ValueError("orbit partition overlap or ordering")
                seen.update(orbit)
                representatives.append((a,b,h))
                sizes[str(len(orbit))]=sizes.get(str(len(orbit)),0)+1
                digest.update(json.dumps(orbit,separators=(",",":")).encode()+b"\n")
    expected={encode(a,b,h) for a in gl for b in gl for h in range(81)}
    fixed_sum=sum(sum(row[a]==a for a in gl)**2 * sum(row[m]==m for m in range(81))
                  for row in actions)
    if fixed_sum%48 or seen!=expected or len(representatives)!=fixed_sum//48:
        raise ValueError("complete ternary triple coverage")
    metadata={"raw_triples":len(expected),"orbit_representatives":len(representatives),
              "invertible_pivots":len(gl),"group_elements":len(actions),
              "distinct_actions":len({tuple(a) for a in actions}),
              "burnside_orbit_count":fixed_sum//48,
              "orbit_size_histogram":sizes,"orbit_partition_sha256":digest.hexdigest(),
              "coverage":"All A,B in GL_2(F3), all H in M_2(F3), by exact simultaneous conjugacy"}
    return [(matrices[a],matrices[b],matrices[h]) for a,b,h in representatives],metadata

if __name__=="__main__":
    _,metadata=partition()
    print(json.dumps(metadata,indent=2,sort_keys=True))
