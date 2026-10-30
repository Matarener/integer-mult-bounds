"""Optional bounded discovery; proof replay never imports PySAT.

Run with --output /path/outside/package/result.json. Negative solver reports
are not proof-checked. Seed, domain and stop rule are fixed to this experiment.
"""
import argparse
import itertools
import json
from pathlib import Path
import random
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.resolve().is_relative_to(HERE) or args.output.exists():
        parser.error('output must be new and outside the package')
    from pysat.card import CardEnc, EncType
    from pysat.solvers import Solver
    import check
    labels,old,_=check.inputs()
    frames=old['orthonormal_groups'][:13]
    tail=[i for g in old['orthonormal_groups'][13:] for i in g]
    choices=list(itertools.combinations(range(13),2))
    random.Random(40).shuffle(choices)
    attempts=[];answer=None
    for bound in (4,5):
        for removed in choices:
            vertices=sorted(tail+[i for r in removed for i in frames[r]])
            graph={i:{j for j in vertices if j>i and (labels[i]&labels[j]).bit_count()%2==0}
                   for i in vertices}
            groups=[]
            def extend(used,remain):
                if used and len(used)%2==0:groups.append(used)
                for i in sorted(remain):extend(used+[i],remain&graph[i])
            extend([],set(vertices))
            clauses=[];top=len(groups)
            for vertex in vertices:
                cnf=CardEnc.equals([i+1 for i,g in enumerate(groups) if vertex in g],
                                   bound=1,top_id=top,encoding=EncType.seqcounter)
                top=cnf.nv;clauses+=cnf.clauses
            cnf=CardEnc.atmost(list(range(1,len(groups)+1)),bound=bound,
                              top_id=top,encoding=EncType.seqcounter)
            clauses+=cnf.clauses
            with Solver(name='cadical195',bootstrap_with=clauses) as solver:
                ok=solver.solve()
                attempts.append(dict(removed=list(removed),group_bound=bound,
                                     even_cliques=len(groups),solver_sat=ok))
                if ok:
                    chosen=[groups[x-1] for x in solver.get_model() if 1<=x<=len(groups)]
                    output=[g for i,g in enumerate(frames) if i not in removed]+chosen
                    check.need(sorted(i for g in output for i in g)==list(range(112)),
                               'discovery partition')
                    check.need(all(len(g)%2==0 and all(
                        (labels[i]&labels[j]).bit_count()%2==int(i==j) for i in g for j in g)
                        for g in output),'discovery Gram identities')
                    answer=dict(orthonormal_groups=output,removed=list(removed),
                                scalar_rank_upper=2*len(output))
                    break
        if answer is not None:break
    receipt=dict(seed=40,domain='78 predecessor frame pairs; four then five local groups',
                 stopping_rule='first verified construction or complete finite domain',
                 attempts=attempts,answer=answer,negative_proofs_checked=False)
    with args.output.open('x') as stream:json.dump(receipt,stream,indent=2);stream.write('\n')
    print('DISCOVERY_RESULT',json.dumps(dict(attempts=len(attempts),answer_found=answer is not None)))


if __name__=='__main__':main()
