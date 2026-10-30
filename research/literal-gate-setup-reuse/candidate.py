"""Install literal-only setup in the frozen complete PR5818 qualification."""
from pathlib import Path
import runpy
import sys

from setup_cache import bind, require


def run(base):
    sys.path.insert(0, str(base))
    from source import prepared
    with prepared() as root:
        entry = root / 'research/selected-quadratic-replay'
        sys.path.insert(0, str(entry))
        import checks
        original_load = checks.load
        installations = []

        def load(name, path):
            module = original_load(name, path)
            if name == 'selected_cross_literal_compiler':
                setup, method, binding = bind(module)
                installations.append((module, method, setup, binding))
            return module

        checks.load = load
        try:
            joint = runpy.run_path(str(base / 'joint.py'))
            joint['run'](root)
            require(len(installations) == 1, 'Exactly one literal setup installation')
            _, _, setup, binding = installations[0]
            require(setup.cached.cache_info().hits > 0 and setup.cached.cache_info().currsize <= 512,
                    'Actual bounded setup reuse')
            return {'binding': binding, 'cache': setup.cached.cache_info()._asdict(),
                    'source_head': 'a0171b8d2f942cdfc5295307548fe484c570b1ba',
                    'second_literal': 'Original unchanged independent native_verify.state'}
        finally:
            checks.load = original_load
            for module, method, _, _ in installations:
                module.Op.zero_state = method
