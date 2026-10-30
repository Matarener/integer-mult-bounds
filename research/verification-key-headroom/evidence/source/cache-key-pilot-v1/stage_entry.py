"""Parent-frozen guarded entry. Never run this from the preparation directory."""
from pathlib import Path
from run_pilot import main

stage = Path(__file__).resolve().parent
if stage.parent.name != "stages" or stage.name != "cache-key-pilot-v1":
    raise RuntimeError("requires parent's immutable stages/cache-key-pilot-v1 copy")
main(stage.parent.parent / "runtime" / "cache-key-pilot-v1-artifacts")
