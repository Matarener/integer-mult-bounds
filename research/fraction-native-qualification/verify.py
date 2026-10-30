"""Fresh registered finite/native/source-custody verification, not timing admission."""
import json,sys
from pathlib import Path
from frozen import require
import custody
from finite import main

if __name__=='__main__':
    require(len(sys.argv)==1,'No registered verifier arguments')
    custody.main()
    result=main();build=result.pop('build')
    require(result==json.loads(Path(__file__).with_name('RESULT.json').read_text()),'all inherited/native finite outputs and controls')
    require(build['source_sha256']==json.loads(Path(__file__).with_name('NATIVE-SOURCE.json').read_text())['sha256'],'native build source authenticated')
    print('PASS_FRACTION_NATIVE_FINITE_AND_CUSTODY')
