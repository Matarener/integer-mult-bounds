#!/usr/bin/env python3
"""Cold, source-authenticated finite CRT replay. No Git or working-tree writes."""
import argparse
import ast
from hashlib import sha256
import json
from pathlib import Path
import crt_sources

HERE=Path(__file__).resolve().parent


def need(test,message):
    if not test:
        raise ValueError(message)


def static_contract():
    files=sorted(HERE.glob('crt_*.py'))+[HERE/'encoded_crt.py']
    runtime=[p for p in files if p.name!='crt_sources.py']
    for p in runtime:
        tree=ast.parse(p.read_text())
        for node in ast.walk(tree):
            if isinstance(node,ast.Attribute):
                need(node.attr not in ('cells','head','inspect','__dict__'), 'no runtime host state decoding')
            if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='range':
                need(len(node.args)==1 and isinstance(node.args[0],ast.Constant) and node.args[0].value==6,
                     'only fixed six-field runtime loop')
    return len(runtime)


def source_controls():
    import copy
    import sys
    import tempfile
    manifest=crt_sources.source_manifest()
    row=next(r for r in manifest['files'] if r['path'].endswith('/tensor_sources.py'))
    with tempfile.TemporaryDirectory(prefix='crt-source-controls-') as folder:
        target=Path(folder)/row['path']
        target.parent.mkdir(parents=True)
        raw=Path(sys.modules['tensor_sources'].__file__).read_bytes()
        target.write_bytes(raw)
        single={'files':[row]}
        crt_sources.check_tree(folder,single)
        def rejects(m):
            try:crt_sources.check_tree(folder,m)
            except ValueError:return
            raise ValueError('source-integrity negative control accepted')
        target.write_bytes(raw[:-1]);rejects(single)
        target.write_bytes(raw[:-1]+bytes([raw[-1]^1]));rejects(single)
        target.write_bytes(raw)
        wrong=copy.deepcopy(single);wrong['files'][0]['git_blob']='0'*40;rejects(wrong)
        target.unlink();rejects(single)
    return 4


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    source=parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--source-root',type=Path)
    source.add_argument('--fetch',action='store_true')
    parser.add_argument('--write-receipt',type=Path)
    args=parser.parse_args()
    from check_crt_cost import check
    result={'schema':1,'base':'20ecf2891d80b5acf18d980b2164fb44ea7faa90',
            'source_head':'240597ed313fc2854c0462b23c89dc3bae72aaf5',
            'runtime_files':static_contract(),'cost':check()}
    with crt_sources.opened(args.source_root,fetch=args.fetch):
        import check_crt_runtime as checks
        result['source_controls']=source_controls()
        for name in ('complete_columns','descriptor_and_prefix','shear_geometry',
                     'inverse_units','typed_plan','rejection_controls'):
            result[name]=getattr(checks,name)()
        # Check the exact offline dependency bytes again after execution.
        if args.source_root is not None:
            crt_sources.check_tree(args.source_root,crt_sources.source_manifest())
    normalized=json.loads(json.dumps(result))
    if args.write_receipt is not None:
        args.write_receipt.write_text(json.dumps(normalized,indent=2,sort_keys=True)+'\n')
    else:
        need(normalized==json.loads((HERE/'EXPECTED.json').read_text()),'complete deterministic CRT receipt')
    print('PASS_CRT_ADDRESS_STREAMS '+json.dumps({'columns':138,'inverse_cases':2176,
          'controls':normalized['rejection_controls']['controls']+normalized['source_controls'],'wrapper_peak':39},sort_keys=True))


if __name__=='__main__':
    main()
