#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Build or check the Git-free, byte-exact continuation replay inventory.

This is a producer packaging tool. verify.py only reads its completed
manifest. Mathematical predecessors and their source pins are unchanged.
Substantial OpenAI assistance under the user's direction.
"""
from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SCHEMA='kappa-next-regime-release-manifest-v1'
EXCLUDED={'MANIFEST.json','VALIDATION.json'}
DEPENDENCY_TREES=('research/selected-bit-physical-caller','research/coupled-carrier-cap740')


def need(ok,reason):
    if not ok:raise ValueError(reason)


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def relative_name(name):
    need(isinstance(name,str),'manifest path is a string')
    path=Path(name)
    need(name and not path.is_absolute() and '..' not in path.parts and path.as_posix()==name,
         'normalized relative source path: '+repr(name))
    return path


def digest(path):
    need(path.is_file() and not path.is_symlink(),'regular source file: '+str(path))
    with path.open('rb') as handle:
        h=sha256()
        for block in iter(lambda:handle.read(1024*1024),b''):h.update(block)
    return {'bytes':path.stat().st_size,'sha256':h.hexdigest()}


def tree_files(directory):
    need(directory.is_dir() and not directory.is_symlink(),'regular source directory: '+str(directory))
    files=[]
    for path in directory.rglob('*'):
        need(not path.is_symlink(),'source symlink is outside the inventory contract: '+str(path))
        if '__pycache__' in path.parts or path.suffix=='.pyc':continue
        if path.is_file():files.append(path)
    return sorted(files)


def dependency_names():
    names={path.relative_to(ROOT).as_posix() for name in DEPENDENCY_TREES
           for path in tree_files(ROOT/name)}
    physical=ROOT/DEPENDENCY_TREES[0]
    names.update(row['path'] for row in read(physical/'inputs/pr2753/SOURCES.json')['files'])
    names.update(read(ROOT/'research/coupled-carrier-cap740/SOURCE-PINS.json'))
    names.update(('research/native-complex-moment552/engines/moment.py',
                  'research/native-complex-moment552/engines/base_two_moment.py',
                  'research/bit-partial-width7-optimum/verify.py'))
    binding=read(HERE/'outer/BINDING.json')
    need(set(binding)=={'check_ledger.py','independent_check.py'},'both frozen outer predecessors')
    names.update(row['original'] for row in binding.values())
    # These completed receipts also name any additional external proof input
    # used by the independent width or actual complex-fill reviews.
    for name in ('width-search/FINAL-INVOICE-OUTER-REVIEW.json',
                 'width-search/PHYSICAL-PROBE-STATIC-REVIEW.json',
                 'complex/FRESH-FILL-REVIEW.json'):
        names.update(read(HERE/name)['source_sha256'])
    out=set()
    for name in names:
        path=ROOT/relative_name(name)
        if not path.is_relative_to(HERE):out.add(name)
    return sorted(out)


def inventory():
    scoped={path.relative_to(HERE).as_posix():digest(path) for path in tree_files(HERE)
            if path.relative_to(HERE).as_posix() not in EXCLUDED}
    dependencies={name:digest(ROOT/name) for name in dependency_names()}
    return {'schema':SCHEMA,'scope':HERE.relative_to(ROOT).as_posix(),
        'files':scoped,'repository_dependencies':dependencies,
        'excluded_scope_paths':sorted(EXCLUDED),
        'ignored_runtime_cache_names':['__pycache__','*.pyc'],
        'managed_dependency_trees':list(DEPENDENCY_TREES),
        'python_requirement':'Python 3.11 or later, standard library; assertions enabled; bytecode writes disabled.',
        'scope_note':'Byte-exact file closure for the published finite replay. It is not an independent all-size multiplication proof.'}


def check(path=HERE/'MANIFEST.json'):
    expected=read(path)
    need(expected.get('schema')==SCHEMA,'recognized complete replay manifest schema')
    observed=inventory()
    # Compare canonical JSON, preserving integer/bool and all metadata types.
    if canonical(expected)!=canonical(observed):
        for field in ('files','repository_dependencies'):
            wanted,got=expected.get(field,{}),observed[field]
            missing=sorted(set(wanted)-set(got));extra=sorted(set(got)-set(wanted))
            changed=sorted(name for name in set(wanted)&set(got) if canonical(wanted[name])!=canonical(got[name]))
            if missing or extra or changed:
                raise ValueError('manifest '+field+' mismatch: '+json.dumps({
                    'missing':missing[:12],'extra':extra[:12],'changed':changed[:12]},sort_keys=True))
        raise ValueError('complete manifest metadata mismatch')
    return {'manifest_sha256':digest(path)['sha256'],'scope_files':len(observed['files']),
            'repository_dependencies':len(observed['repository_dependencies'])}


def main():
    parser=ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=HERE/'MANIFEST.json')
    parser.add_argument('--check',action='store_true',help='read-only validation of --output')
    parser.add_argument('--replace',action='store_true',help='producer-only replacement after release files change')
    args=parser.parse_args();path=args.output.resolve()
    if args.check:result=check(path)
    else:
        need(args.replace or not path.exists(),'manifest output must be fresh unless --replace is explicit')
        value=inventory();path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n',encoding='utf-8')
        result=check(path)
    print(json.dumps({'status':'PASS_COMPLETE_REPLAY_MANIFEST',**result},sort_keys=True))


if __name__=='__main__':main()
