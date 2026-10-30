"""Run the complete H4 verifier with exact projective-normal reuse.

This contribution was produced by Nick Petalas. Apache-2.0.
"""

from pathlib import Path
import runpy


if __name__ == "__main__":
    api = runpy.run_path(str(Path(__file__).resolve().with_name("accelerator.py")))
    api["accelerated_source"]().main()
