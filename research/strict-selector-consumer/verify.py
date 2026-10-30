"""Source-closed replay of the exact encoded-plan ordinary caller."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from binding_source import installed, require


def main():
    require(len(sys.argv) == 1, "no verifier arguments")
    with installed():
        import binding_checks
        import endpoints
        import node_endpoint

        result = dict(
            status="PASS_STRICT_SELECTOR_CONSUMER",
            full_cases=endpoints.full_cases(),
            node=endpoints.one(factory=node_endpoint.completed),
            geometries=binding_checks.geometries(),
            fallback=[
                binding_checks.fallback(e, p, z, t)
                for e in (1, 2, 3, 4)
                for p, z, t in ((1, 1, 1), (2, 2, 2))
            ],
            controls=binding_checks.controls(),
        )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
