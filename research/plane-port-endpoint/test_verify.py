#!/usr/bin/env python3
"""The plane repair delivers both coordinates, and dropping it does not."""

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("plane_port_endpoint", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    dirty = verify.square(verify.coordinate(2))
    delivered = verify.multiply((1, 1, 0), dirty)
    if verify.endpoint((0, 1), dirty, True) != delivered:
        raise SystemExit("the plane repair missed the endpoint")
    if verify.endpoint((0, 1), dirty, False) == delivered:
        raise SystemExit("the omitted repair still hit the endpoint")
    if verify.endpoint((0,), dirty, True)[0] != 1:
        raise SystemExit("the line repair left the port coordinate short")
    print("PASS_PLANE_PORT_ENDPOINT_TESTS groups=1")


if __name__ == "__main__":
    main()
