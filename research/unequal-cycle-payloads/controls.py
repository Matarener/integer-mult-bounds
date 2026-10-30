"""Counterexamples to incomplete formulas and actual source/semantic failures."""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory

import cycle
from check import principal
import source


def reject(fn, message):
    try:fn()
    except ValueError as error:
        cycle.need(message in str(error),'expected rejection: '+str(error));return
    raise ValueError('negative control accepted: '+message)


def run():
    cycle.need(cycle.minimum((100,1,1,1,1))==101>52,'half-total alone misses independent-pair bottleneck')
    cycle.need(cycle.minimum((1,1,1,1,1))==3>2,'pair bound alone misses odd-cycle bottleneck')
    cycle.need(cycle.minimum((2,2,2,2,2))==5<6,'scaling scalar optimum is not valid')
    for bad in ((1,2,3,4), (1,2,3,4,-1), (1,2,3,4,True), (1,2,3,4,1.0)):
        reject(lambda:cycle.construct(bad),'payload dimensions')
    recipe=cycle.construct((2,2,2,2,2))
    bad=deepcopy(recipe);bad['edge'][0]-=1
    reject(lambda:cycle.validate(bad),'coordinate coverage')
    bad=deepcopy(recipe);bad['rank']-=1
    reject(lambda:cycle.validate(bad),'query dimension')
    a=cycle.matrix(recipe)
    # A one-direction forbidden 2x2 block has zero trace and kills constants.
    a[0][4],a[0][5],a[1][4],a[1][5]=1,-1,1,-1
    cycle.need(a[0][4]+a[1][5]==0 and a[0][4]+a[0][5]==0 and a[1][4]+a[1][5]==0,
               'invisible to trace and all-ones probes')
    reject(lambda:cycle.fits(a,(2,2,2,2,2)),'complete block mask')
    model=source.model()
    wrong=model['core'][:];wrong[0],wrong[1]=wrong[1],wrong[0]
    reject(lambda:source.validate_core(wrong,model['clique'],model['allowed']),'cycle mask')
    bad=deepcopy(model['allowed']);bad[model['clique'][0]][model['core'][0]]=True
    reject(lambda:source.validate_core(model['core'],model['clique'],bad),'separation mask')
    dims=[1]*112
    correct=principal(dims,model)
    widths=[dims[model['pairs'][i][0]] for i in model['core']]
    cycle.need(correct['principal_minimum']==49 and correct['separated_dimension']+cycle.minimum(widths)==47,
               'omitting second plane-port payload undercharges')
    with TemporaryDirectory() as path:
        root=Path(path);first=source.ARCHIVE
        target=root/first;target.parent.mkdir(parents=True)
        target.write_bytes((source.ROOT/first).read_bytes()+b'\n')
        reject(lambda:source.model(root),'source SHA256')
    return dict(formula_controls=3,invalid_dimension_cases=4,semantic_controls=6,
                source_corruption=1,no_new_kappa=True)
