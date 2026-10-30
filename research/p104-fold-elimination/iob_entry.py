"""Subprocess entry for the unmodified fold driver's solver invocation."""

import os
from pathlib import Path

from runtime import install


def main():
    root = Path(os.environ["FOLD_TOOLKIT_ROOT"]).resolve()
    install(root, os.environ["FOLD_SOLVER_MODE"])
    import iob2

    iob2.main()


if __name__ == "__main__":
    main()
