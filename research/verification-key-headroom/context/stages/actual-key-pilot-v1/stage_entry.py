"""Parent-frozen guarded entry; source-preparation copies cannot execute."""
from pathlib import Path
from actual_driver import main
stage=Path(__file__).resolve().parent
if stage.parent.name!='stages' or stage.name!='actual-key-pilot-v1':
    raise RuntimeError('requires immutable stages/actual-key-pilot-v1 copy')
main(stage.parent.parent/'runtime/actual-key-pilot-v1-artifacts')
