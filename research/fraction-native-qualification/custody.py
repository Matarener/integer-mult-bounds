"""Retain all four unchanged predecessor custody checks, with scoped imports."""
import importlib.util,sys
from frozen import baseline

def main():
    prior={name:sys.modules.pop(name,None) for name in ('source','observe')}
    paths=list(sys.path)
    try:
        with baseline() as package:
            sys.path.insert(0,str(package))
            spec=importlib.util.spec_from_file_location('native_predecessor_custody',package/'custody.py')
            module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.main()
    finally:
        sys.path[:]=paths
        for name,value in prior.items():
            sys.modules.pop(name,None)
            if value is not None:sys.modules[name]=value

if __name__=='__main__':main()
