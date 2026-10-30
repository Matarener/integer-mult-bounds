"""Newmixedwidthnomination adapter; upstreamfunctions retaincopyright/credit.
No upstreamsource or publicationbytes modified. This adapter loads complete
independentlyaudited finiteowner descriptors and preserves allsource laws.
"""

def _need(value, why):
    if not value:
        raise ValueError(why)
from pathlib import Path
import hashlib, json, gzip
_UPSTREAM = Path(__file__).resolve().parent / 'upstream-owner.py'
_EXPECTED_UPSTREAM = 'b6232c9f7f5d7b9a4be868e5e1d147b57e8e7ba9ddc0d35e7f7170c65b600c66'
_BYTES = _UPSTREAM.read_bytes()
_need(hashlib.sha256(_BYTES).hexdigest() == _EXPECTED_UPSTREAM, 'authenticated upstream owner source')
exec(compile(_BYTES, str(_UPSTREAM), 'exec', dont_inherit=True), globals())
_EXPECTED_ARTIFACTS = {'ORDER': '8a153e3c5086e67735310bc47b2a83a41b55ba8ce102eb9a90e960d49328bbe4', 'CHARTS': 'a794812b3fac17be06d272ed60b735165a5384d7ba967dccfb329d8f00ab3396', 'SLOTS': '8131efe36eae3a25f53b5acd09ff0560ab8fbf693546dbb92af9f6e0ba509994', 'REMAINDERS': '72667ea46851acfe735fd76091c380764792c05dedf6441506b222818947d709', 'DISPATCH': '8d21435c04c44ff86c93d823d7d04b7eeef5766917a2127ae964e42957a34a20'}

def construct():
    summary = json.loads((HERE / 'OWNERS.json').read_bytes())
    artifacts = {}
    for name, pin in _EXPECTED_ARTIFACTS.items():
        raw = (HERE / 'new-owners' / (name + '.json.gz')).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == pin, 'newownedledgerpin ' + name)
        artifacts[name] = json.loads(gzip.decompress(raw))
    need(summary['ordinaryRAW'] == 660 and summary['helpers'] == 438 and (summary['W'] == 28416), 'unchanged660providerinventory')
    need(len(artifacts['SLOTS']) == 438 * 9 and len(artifacts['DISPATCH']) == 288, 'newfiniteownercoverage')
    return (summary, artifacts)
