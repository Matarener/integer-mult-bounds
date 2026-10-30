#!/usr/bin/env python3
"""Rebuild the complete source-bound p17 native/direct physical invoice."""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import importlib.util
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
DEFAULT_SOURCE = HERE.parent/'pr4359-p7-padding/source'
GEOMETRY_PAYLOAD_SHA256 = 'a58789b3cc4449fd7f9520119b2aaf6f5d9f7351cc34ed96f32e41e4169eb034'


def need(ok, why):
    if not ok:
        raise AssertionError(why)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name,path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def run(source_root=DEFAULT_SOURCE, output_dir=None, retimed_source_root=None):
    root = Path(source_root).resolve()
    parameters = load(HERE/'parameters.py','hybrid_inventory_parameters')
    supplier_module = load(HERE/'local_supplier.py','hybrid_inventory_supplier')
    local = supplier_module.run(root,retimed_source_root)
    factory = load(HERE/'controller/make_direct_case.py','hybrid_inventory_factory')
    factor = factory.run(root)
    need(factor['status'] == 'PASS_EXACT_P17_LAURENT_SPECIALIZATION', 'Fresh exact controller factorization')
    geometry_module = load(HERE/'native_geometry.py','hybrid_inventory_geometry')
    geometry,artifact = geometry_module.run(HERE/'controller/P17-FULL-LAURENT-CASE.json',
                                             parameters.NATIVE_MASK,root)
    need((geometry['p'],geometry['keep'],geometry['native_mask'],geometry['dimension']) ==
         (parameters.PAIRS,parameters.KEEP,parameters.NATIVE_MASK,parameters.AMBIENT),
         'Exact source-bound controller and full original carrier')
    need(tuple(geometry['direct_stage_indices']) == parameters.DIRECT_STAGES and
         geometry['native_stages'] == parameters.INVOCATIONS, 'Exact native/direct chronology')
    need(geometry_module.LOCAL_HELPERS == local['local_helper_profile'] == parameters.LOCAL_HELPERS and
         geometry_module.LOCAL_PAID == local['local_paid_profile'] == parameters.LOCAL_PAID,
         'Geometry uses the fresh arbitrary-input local supplier profiles')
    need(geometry['targets'] == parameters.TARGETS and geometry['paid'] == parameters.PAID,
         'Exact complete native/direct/idle/helper tariff')
    need(sum(k*v for k,v in geometry['targets'].items()) == parameters.TARGET_MASS and
         sum(k*v for k,v in geometry['paid'].items()) == parameters.PAID_MASS and
         geometry['productive_fields'] == parameters.PRODUCTIVE_FIELDS,
         'Exact productive census and both rank-one masses')
    direct_case = json.loads((HERE/'controller/P17-DIRECT-CASE.json').read_text())
    need(artifact['formal']['exact_diagonal_monomials'] == direct_case['exact_diagonal_monomials'],
         'Independent literal replay and rational factor factory agree on every endpoint')
    need(Counter({int(k):v for k,v in direct_case['complete_paid_profile'].items()}) == Counter(parameters.PAID) and
         Counter({int(k):v for k,v in direct_case['complete_productive_profile'].items()}) == Counter(parameters.TARGETS),
         'Independent factor invoice agrees with physical geometry')
    payload = geometry_module.canonical(artifact)
    frozen_path = HERE/'certificates/HYBRID-GEOMETRY.json.gz'
    frozen_payload = gzip.decompress(frozen_path.read_bytes())
    need(sha256(payload).hexdigest() == GEOMETRY_PAYLOAD_SHA256 and payload == frozen_payload,
         'Every generated contact/route/endpoint/direct kernel equals the audited canonical payload')
    native_orientation = Counter('backward' if row[3] else 'forward'
                                 for row in artifact['formal']['physical_events'] if row[0] == 'LOCAL')
    need(native_orientation == Counter(forward=2,backward=17), 'Exact local scalar orientation counts')
    native_scalar = sum(local['local_replays'][direction]['conservative_real_scalar_primitive_allowance']*count
                        for direction,count in native_orientation.items())
    need(geometry_module.scalar_invoice(artifact['formal'],native_scalar) ==
         geometry['native_and_boundary_scalar_allowance'], 'Complete fresh native and boundary scalar invoice')
    need(geometry['direct_paid_queries'] == 1792 and geometry['direct_scalar_allowance'] == 64*1792,
         'Every owned-copy direct query and its pointwise operations are charged')
    result = dict(geometry)
    result.update(schema='complete-source-bound-hybrid-p17-native-inventory/1',
                  status='PASS_RETIMED_SUPPLIER_AND_ALL_HYBRID_CONTROLLER_PHASES',
                  local_supplier=local,factor_factory=factor,
                  direct_owned_copy_episodes=1792,direct_owned_release_episodes=1792,
                  direct_productive_scratch_endpoints=0,
                  direct_nonrecursive_movement_records_allowance=8*1792,
                  raw_owned_bank_episodes=parameters.INVOCATIONS+1792,
                  owned_bank_scope='Each direct copy persists across its own recursive request and is released after the ADD. Each native invocation retains its original owned center. All nested suspended banks are separately charged.',
                  all_column_direct_recipe='At f columns the address map is P tensor I_f (or I_f tensor P in column order), with its induced per-column array permutation. Use one Gaussian child of rank f, inverse route and repeated q translation for C_q inverse. The request has the complete ancestor weight.',
                  geometry_payload_sha256=GEOMETRY_PAYLOAD_SHA256,
                  geometry_source_sha256=digest(HERE/'native_geometry.py'),
                  local_supplier_source_sha256=digest(HERE/'local_supplier.py'),
                  factor_factory_source_sha256=digest(HERE/'controller/make_direct_case.py'),
                  parameters_sha256=digest(HERE/'parameters.py'),
                  limits='Complete finite native/direct controller admission. The common-column tensor rule, expanded fixed route/scalar/owned-stock bounds and inherited precision, analytic, fixed-tape and exact-recovery premises are written separately in PROOF.md.')
    if output_dir is not None:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True,exist_ok=True)
        (output_dir/'NATIVE.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root',type=Path,default=DEFAULT_SOURCE)
    parser.add_argument('--output-dir',type=Path)
    parser.add_argument('--retimed-source-root',type=Path)
    args = parser.parse_args()
    result = run(args.source_root,args.output_dir,args.retimed_source_root)
    print(json.dumps({key:result[key] for key in ('status','p','targets','paid','rank_margin','scalar_allowance')},sort_keys=True))
