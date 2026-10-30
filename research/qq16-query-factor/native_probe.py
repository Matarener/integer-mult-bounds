"""Read-only native-frame discriminants from exact selected chart data.

No package executable is imported. This rejects omitted/incorrect native
query alignment; it does not exclude a correctly paid query implementation.
"""
from pathlib import Path
from itertools import combinations
from functools import lru_cache
import gzip
import hashlib
import json
import tarfile

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT/'research/community-frontier1042-audit/selected-replay.tar.gz'
PACKET = ROOT/'research/joint-query/certificate.json.gz'

def need(value, message):
    if not value:
        raise ValueError(message)

def sha(data):
    return hashlib.sha256(data).hexdigest()

need(sha(ARCHIVE.read_bytes()) == '22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754', 'selected archive SHA')
need(sha(PACKET.read_bytes()) == 'a5ed85fac5ebf3c091482a113ab0d351eb5a7892fe2841a35e16017ec1ff49f7', 'QQ16 packet SHA')
with tarfile.open(ARCHIVE) as archive:
    raw = archive.extractfile('t16/global/base/work/complex-nine-native/DATA-PHASES.json').read()
need(sha(raw) == 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa', 'actual phase member SHA')
phases = json.loads(raw)
packet = json.loads(gzip.decompress(PACKET.read_bytes()))
identity = tuple(1 << j for j in range(73))
registry = {(tuple(v['owner_right_matrix_columns']), v['payload_translation_at_identity_owner']): k for k,v in packet['map_registry'].items()}

def act(columns, vector):
    out = 0
    while vector:
        bit = vector & -vector
        out ^= columns[bit.bit_length()-1]
        vector ^= bit
    return out

@lru_cache(None)
def chart(port, stage, kind):
    rec = phases['recipes'][port]
    basis = rec['idle_children'][0]['orthogonal_axes'][:8]
    external = [1 << (9 + 8*(stage-1) + j) for j in range(8)]
    swaps = [a ^ b for a,b in zip(basis,external)]
    rho = tuple(v ^ act(swaps, sum(((v&s).bit_count()%2) << j for j,s in enumerate(swaps))) for v in identity)
    beta = [((v.bit_count()-1)//2) % 2 for v in basis]
    lifted = sum(bit*v for bit,v in zip(beta,external))
    intrinsic = act(basis, sum(bit << j for j,bit in enumerate(beta)))
    delta = (rec['q'] if kind == 'Y' else intrinsic) ^ lifted
    need((rho,delta) in registry, 'reconstructed alignment absent from actual packet')
    need(tuple(act(rho,v) for v in rho) == identity, 'involutive route')
    return rho, delta, registry[rho,delta]

def exponent(port, completed_stage, alignment_stage, kind, character):
    rho,delta,_ = chart(port,alignment_stage,kind)
    # A=M(rho,delta) changes each native frame axis a to rho*a and
    # contributes translation phase 2 delta.dot(character).
    value = sum((rho[j] & character).bit_count()%2 for j in range(9+8*completed_stage))
    if kind == 'Y':
        value -= (phases['recipes'][port]['q'] & character).bit_count()%2
    value += 2*((delta & character).bit_count()%2)
    return value % 4

ports = [0,25]
row = packet['R_rows'][0]
need([row[str(p)] for p in ports] == ['1','1'], 'actual query supports both sources')
old = [exponent(p,1,1,'Y',1) for p in ports]
need(old == [2,3], 'old-chart Y mismatch')
# Exact phase polynomials have degree at most2 modulo4. These values check
# the legitimate X-after1 and Y-before2 alignments on the active25 axes.
characters = [0]+[1 << j for j in range(25)]+[(1 << i)^(1 << j) for i,j in combinations(range(25),2)]
for port in range(112):
    for u in characters:
        need(exponent(port,1,1,'X',u) == (u & ((1 << 17)-1)).bit_count()%4, 'X-after1 common F17 control')
        need(exponent(port,1,2,'Y',u) == ((u >> 9) & ((1 << 16)-1)).bit_count()%4, 'Y-before2 common F16 control')

word_path = ROOT/'research/qq16-query-factor/CANDIDATE-WORD.json'
word = json.loads(word_path.read_text())
first_index,first_event = next((i,e) for i,e in enumerate(word['events']) if e[0]=='add_view')
need(first_index == 32 and first_event == ['add_view','q0','Y0','1','r1_0'], 'actual first candidate ingress')
g = tuple(word['routes']['r1_0'])
need(g == chart(0,1,'Y')[0], 'first candidate route matches actual source')
raw_source_exponent = (sum((a & 1).bit_count()%2 for a in g[:17]) - (phases['recipes'][0]['q'] & 1).bit_count()%2) % 4
target_exponent = 1
need(raw_source_exponent == 0 and target_exponent == 1, 'literal first ingress phase mismatch')
need((target_exponent-raw_source_exponent)%2 == 1, 'payload translation alone cannot repair odd phase difference')

same_query_gates=[]
for p in ports:
    index,event=next((i,e) for i,e in enumerate(word['events']) if e==['add_view','q0','Y'+str(p),'1','r1_'+str(p)])
    g=tuple(word['routes'][event[4]])
    need(g==chart(p,1,'Y')[0], 'same query source route binding')
    raw_phase=(sum((a&1).bit_count()%2 for a in g[:17])-(phases['recipes'][p]['q']&1).bit_count()%2)%4
    same_query_gates.append({'event_index':index,'event':event,'raw_routed_source_phase_mod4':raw_phase})
need([v['raw_routed_source_phase_mod4'] for v in same_query_gates]==[0,3], 'two ingress phase parity separation')

result = {
    'fixed_carrier_translation_only_obstruction':{'owner':'I73','character':1,'gates':same_query_gates,'claim':'No one fixed query-carrier phase can accept both these independent contributions using their actual owner routes and arbitrary payload translations only, because their required phase parities differ. Carrier changes and compensated native words remain open.'},
    'status':'PASS_EXACT_NATIVE_QUERY_ALIGNMENT_DISCRIMINANTS',
    'actual_candidate_ingress':{'word_sha256':sha(word_path.read_bytes()),'event_index':first_index,'event':first_event,'owner':'I73','character':1,'raw_routed_Y_phase_mod4':raw_source_exponent,'declared_F17_query_phase_mod4':target_exponent,'required_multiplier':'i','payload_translation_only_impossible':True,'scope':'This exact first gate is invalid if interpreted as owner route plus raw scalar ADD, even allowing an extra payload translation; a paid native adapter remains possible.'},
    'source_archive_sha256':sha(ARCHIVE.read_bytes()),
    'packet_sha256':sha(PACKET.read_bytes()),
    'phase_member_sha256':sha(raw),
    'old_chart_query':{
        'query':'a=R_1 Y at completed stage1; attempt uses the Y-before1 maps',
        'owner':'I73','character':1,'R_row':0,'ports':ports,
        'normals':[phases['recipes'][p]['q'] for p in ports],
        'coefficients':['1','1'],
        'map_ids':[chart(p,1,'Y')[2] for p in ports],
        'aligned_phase_exponents':old,
        'aligned_multipliers':['-1','-i'],
        'conclusion':'Two nonzero same-query sources have different native frames, so the unchanged Y-before1 alignment cannot collect this query into one common native accumulator.'
    },
    'legal_controls':{'X_after1':'common F17','Y_before2':'common F_(E1+E2), dimension16','ports':112,'characters_per_port_per_control':len(characters),'active_axes':25},
    'cross_frame_selected_sum':{'port':0,'normal':11,'owner':'I73','character':1,'logical_input_X':'chi_e0','logical_input_Y':'0','physical_X':'i chi_e0','physical_Y':'0','required_physical_Y_after_logical_sum':'chi_e0','raw_physical_ADD_result':'i chi_e0','required_correction':'C_q^-1 on the X contribution, or equivalent native implementation'},
    'scope':'Necessary native-lift controls for a successful logical query factor. No native price lower bound, no general repair impossibility, no contradiction to properly gauged logical selected rotation, and no all-size supplier acceptance.'
}
receipt=Path(__file__).with_name('NATIVE-PROBE.json')
if json.dumps(json.loads(receipt.read_text()),sort_keys=True,separators=(',',':')) != json.dumps(result,sort_keys=True,separators=(',',':')):
    raise ValueError('independent native probe receipt mismatch')
print('PASS_INDEPENDENT_NATIVE_QUERY_ALIGNMENT_AND_FIXED_CARRIER_CONTROLS')
