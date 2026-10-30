#!/usr/bin/env python3
"""Bounded exact ambient REL contraction and cumulative-debt checks.

AAAmirinu with substantial OpenAI Codex assistance. Apache-2.0.
Nick Petalas's PR6229 model and debt argument are retained and credited. Its
strict confined checker is not used to validate equal contracted frames.
"""
from fractions import Fraction as F
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PORTS = (73, 239, 336, 502, 81, 247, 328, 494)
WORD = 'research/p104-helper-subspace-splits/WORD.json.gz'
MODEL_SOURCE = 'research/p104-two-clique-relay-floor/model.py'
MODEL_PIN = ('head:50540b2a7e0d219bc4920e6252e75113b5a9d8d8:'
             'research/p104-two-clique-relay-floor/model.py')


def require(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate_bytes(raw, row):
    require(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source SHA256 mismatch')
    blob = b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw
    require(hashlib.sha1(blob).hexdigest() == row['git_blob'], 'source Git blob mismatch')


def authenticate():
    rows = json.loads((HERE / 'SOURCES.json').read_bytes())['files']
    inputs = [row for row in rows if row['usage'] == 'input']
    vendors = [row for row in rows if row['path'] == MODEL_SOURCE]
    require(len(inputs) == 1 and inputs[0]['path'] == WORD and len(vendors) == 1,
            'source inventory')
    require(vendors[0]['usage'] == 'provenance' and vendors[0]['pin'] == MODEL_PIN,
            'predecessor source pin')
    word_path, vendor_path = ROOT / WORD, HERE / 'vendor/model.py'
    require(not word_path.is_symlink() and not vendor_path.is_symlink(), 'source symlink')
    word_bytes, vendor_bytes = word_path.read_bytes(), vendor_path.read_bytes()
    authenticate_bytes(word_bytes, inputs[0])
    # The manifest pins the original source path; the retained local copy is
    # authenticated against those exact source bytes, not a fabricated Git path.
    authenticate_bytes(vendor_bytes, vendors[0])
    model = types.ModuleType('pinned_two_clique_model')
    exec(compile(vendor_bytes, '<pinned PR6229 model>', 'exec', optimize=0),
         model.__dict__)
    require(set(PORTS) <= set(json.loads(gzip.decompress(word_bytes))['ports']),
            'ports belong to pinned source')
    return model, [inputs[0], vendors[0]], vendor_bytes, vendors[0]


def plain(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {key: plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [plain(item) for item in value]
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='write the checked CERTIFICATE.json')
    args = parser.parse_args()
    m, source_rows, vendor_bytes, vendor_row = authenticate()
    tags = m.tags_for(PORTS)
    w = m.span(list(PORTS))
    require(m.dimension(w) == 4 and 1 not in w, 'four-dimensional port span')
    identity = tuple(tuple(F(i == j) for j in range(8)) for i in range(8))
    unit = lambda k: tuple(F(i == k) for i in range(8))
    orthogonal = lambda frame, port: all((x & port).bit_count() % 2 == 0 for x in frame)

    def check_rel(moves, output, allow_equal=False, confined=False):
        """Literal ambient legality and endpoint, without a quotient-lift assumption."""
        require(len(moves) <= 16 and len(output) == 8 and
                all(len(row) == len(moves) for row in output), 'network/output capacity')
        vectors, landings, gaps = [], [], []
        for gather, landing, local, parents in moves:
            m.row_basis_binary(gather)
            m.row_basis_binary(landing)
            require(landing <= gather and (allow_equal or landing != gather),
                    'ambient strict descent' if not allow_equal else 'contracted descent')
            require(not confined or gather <= w, 'contracted frame confinement')
            require(len(local) == 8 and len(parents) == len(vectors), 'local/parent shape')
            require(all(not x or PORTS[i] in gather for i, x in enumerate(local)),
                    'local source availability')
            require(all(not x or landings[i] <= gather for i, x in enumerate(parents)),
                    'ancestor arrival availability')
            vector = tuple(F(local[i]) + sum((F(a) * old[i] for a, old in zip(parents, vectors)), F(0))
                           for i in range(8))
            vectors.append(vector)
            landings.append(landing)
            gaps.append(m.dimension(gather) - m.dimension(landing))
        for j, row in enumerate(output):
            require(all(not coefficient or orthogonal(landing, PORTS[j])
                        for coefficient, landing in zip(row, landings)), 'receiver availability')
        endpoint = tuple(tuple(sum((F(a) * v[i] for a, v in zip(row, vectors)), F(0))
                               for i in range(8)) for row in output)
        shadow = tuple(tuple(endpoint[j][i] * ((PORTS[j] & PORTS[i]).bit_count() % 2)
                             for i in range(8)) for j in range(8))
        return dict(vectors=tuple(vectors), C=endpoint, H=shadow, gaps=gaps, paid=sum(gaps))

    def cumulative_debt(moves, result):
        """Confined L<=g recurrence, including legal zero-dimensional gaps."""
        debt, effective, trace = (), 0, []
        for index, (gather, landing, _, _) in enumerate(moves):
            require(landing <= gather <= w, 'debt frame contract')
            vector = result['vectors'][index]
            before = m.annihilator(m.image(gather, PORTS, tags))
            after = m.annihilator(m.image(landing, PORTS, tags))
            require(all(m.in_rows(m.packet(vector, tags, z), debt) for z in before),
                    'incoming cumulative debt')
            extended, added = m.row_basis(list(before), 2), []
            for functional in after:
                if not m.in_rows(functional, extended):
                    added.append(m.packet(vector, tags, functional))
                    extended = m.row_basis([*extended, functional], 2)
            drop = len(after) - len(before)
            require(len(added) == drop and 0 <= drop <= result['gaps'][index], 'quotient drop bill')
            previous_dimension = len(debt)
            debt = m.row_basis([*debt, *added], 8)
            require(len(debt) <= previous_dimension + drop, 'cumulative debt growth')
            # Check all earlier landing obligations, not only the newest vector.
            for old_index in range(index + 1):
                old_after = m.annihilator(m.image(moves[old_index][1], PORTS, tags))
                require(all(m.in_rows(m.packet(result['vectors'][old_index], tags, z), debt)
                            for z in old_after), 'all-parent cumulative debt')
            effective += drop
            trace.append(dict(gap=result['gaps'][index], quotient_drop=drop, debt_dimension=len(debt)))
        rank = len(m.row_basis(result['H'], 8))
        require(all(m.in_rows(row, debt) for row in result['H']), 'output debt containment')
        require(rank <= len(debt) <= effective <= result['paid'], 'complete contracted rank invoice')
        return dict(shadow_rank=rank, debt_dimension=len(debt), effective_paid=effective, trace=trace)

    def contract_check(moves, output):
        original = check_rel(moves, output)
        contracted = [(g & w, landing & w, local, parents) for g, landing, local, parents in moves]
        projected = check_rel(contracted, output, allow_equal=True, confined=True)
        require(all(projected[key] == original[key] for key in ('vectors', 'C', 'H')),
                'complete endpoint preservation')
        require(all(a <= b for a, b in zip(projected['gaps'], original['gaps'])),
                'contraction gap monotonicity')
        debt = cumulative_debt(contracted, projected)
        require(debt['shadow_rank'] <= projected['paid'] <= original['paid'], 'ambient rank invoice')
        return original, projected, debt, contracted

    def require_identity(result):
        require(result['H'] == identity, 'identity shadow mismatch')

    # Fixed finite geometry: all subspaces of W+span(1), not all ambient networks.
    universe = m.span([*m.row_basis_binary(w), 1])
    frames = {frozenset({0})}
    for _ in range(5):
        fresh = set(frames)
        for frame in frames:
            basis = m.row_basis_binary(frame)
            for x in universe - frame:
                fresh.add(m.span([*basis, x]))
        frames = fresh
    frames = sorted(frames, key=lambda f: (len(f), tuple(sorted(f))))
    require(len(frames) == 374, 'all five-dimensional subspaces')
    equal = reduced = strict = parent_pairs = local_cases = receiver_cases = 0
    for gather in frames:
        gc = gather & w
        m.row_basis_binary(gc)
        before = m.annihilator(m.image(gc, PORTS, tags))
        for i, port in enumerate(PORTS):
            require((port in gather) == (port in gc), 'local contraction equivalence')
            if port in gather:
                local_cases += 1
                require(all(not any(m.packet(unit(i), tags, z)) for z in before), 'local lift annihilation')
            if orthogonal(gather, port):
                receiver_cases += 1
                require(orthogonal(gc, port), 'receiver contraction implication')
                functional = (1, 0) if tags[i] == 1 else (0, 1)
                require(m.in_rows(functional, m.row_basis(list(before), 2)), 'contracted receiver lift')
        for landing in frames:
            if not landing <= gather:
                continue
            lc = landing & w
            require(lc <= gc, 'parent arrival contraction implication')
            parent_pairs += 1
            if landing == gather:
                continue
            strict += 1
            old_gap, new_gap = m.dimension(gather) - m.dimension(landing), m.dimension(gc) - m.dimension(lc)
            require(0 <= new_gap <= old_gap, 'all frame gap bounds')
            after = m.annihilator(m.image(lc, PORTS, tags))
            require(all(m.in_rows(z, m.row_basis(list(after), 2)) for z in before)
                    and len(after) - len(before) <= new_gap, 'all contracted quotient bounds')
            equal += gc == lc
            reduced += new_gap < old_gap
    require((strict, equal, reduced) == (5395, 307, 1503), 'frozen geometry counts')
    require(tags[0] == tags[2] and (PORTS[0] & 1) != (PORTS[2] & 1),
            'ambient same-class pairing can differ')

    direct = [(m.span([port]), m.span([]), unit(i), (0,) * i) for i, port in enumerate(PORTS)]
    direct_output = [list(row) for row in identity]
    outside, outside_output = [], [[0] * 4 for _ in PORTS]
    for i in range(4):
        local = tuple(int(j in (i, i + 4)) for j in range(8))
        extra = [1] if i >= 2 else []
        outside.append((m.span([PORTS[i], PORTS[i + 4], *extra]), m.span(extra), local, (0,) * i))
        outside_output[i][i] = outside_output[i + 4][i] = 1
    chain = [(m.span([73, 1]), m.span([73]), unit(0), ()),
             (m.span([73]), m.span([]), (0,) * 8, (1,))]
    chain += [(m.span([PORTS[i]]), m.span([]), unit(i), (0,) * (i + 1)) for i in range(1, 8)]
    chain_output = [[0] * 9 for _ in PORTS]
    chain_output[0][1] = 1
    for i in range(1, 8):
        chain_output[i][i + 1] = 1
    fixtures = []
    projected_chain = None
    for label, moves, output, old_bill in (
        ('direct-identity', direct, direct_output, 8),
        ('outside-paired-attainer', outside, outside_output, 8),
        ('zero-gap-parent-chain', chain, chain_output, 9),
    ):
        original, projected, debt, contracted = contract_check(moves, output)
        require_identity(projected)
        require(original['paid'] == old_bill and projected['paid'] == 8, 'fixture exact bill')
        if label != 'zero-gap-parent-chain':
            old = m.check_network(PORTS, contracted, output)
            require(old['shadow'] == list(projected['H']) and old['paid'] == projected['paid']
                    and old['debt_dimension'] == debt['debt_dimension'], 'strict predecessor agreement')
        else:
            projected_chain = contracted
            require(projected['gaps'][0] == 0 and any(projected['vectors'][0])
                    and contracted[1][3] == (1,), 'nontrivial zero-gap parent retained')
        fixtures.append(dict(label=label, moves=len(moves), original_paid=original['paid'],
                             contracted_paid=projected['paid'], C=projected['C'], H=projected['H'],
                             vectors=projected['vectors'], completion_rank=len(m.row_basis(projected['C'], 8)),
                             original_frames=[dict(g=list(m.row_basis_binary(g)), L=list(m.row_basis_binary(l)))
                                              for g, l, _, _ in moves],
                             contracted_frames=[dict(g=list(m.row_basis_binary(g)), L=list(m.row_basis_binary(l)))
                                                for g, l, _, _ in contracted], **debt))

    controls = []
    def reject(label, action, expected):
        try:
            action()
        except ValueError as error:
            require(str(error) == expected, 'unexpected control rejection: ' + label)
            controls.append(dict(control=label, rejected=str(error)))
        else:
            raise ValueError('control accepted: ' + label)
    bad = list(direct)
    g, l, local, parents = bad[0]
    bad[0] = (g, g, local, parents)
    reject('ambient-equal-frame', lambda: check_rel(bad, direct_output), 'ambient strict descent')
    malformed = [(frozenset({0, 1, 2}), l, local, parents), *direct[1:]]
    reject('non-subspace-frame', lambda: check_rel(malformed, direct_output), 'binary subspace closure')
    wrong_local = [(g, l, unit(1), parents), *direct[1:]]
    reject('unavailable-local-source', lambda: check_rel(wrong_local, direct_output), 'local source availability')
    extra_local = [(g, l, (*local, 1), parents), *direct[1:]]
    reject('extra-ambient-source', lambda: check_rel(extra_local, direct_output), 'local/parent shape')
    wrong_parent = [(chain[0][0], m.span([1]), chain[0][2], ()), *chain[1:]]
    reject('unavailable-parent', lambda: check_rel(wrong_parent, chain_output), 'ancestor arrival availability')
    wrong_receiver = [row[:] for row in chain_output]
    wrong_receiver[0][0] = 1
    reject('unavailable-receiver', lambda: check_rel(chain, wrong_receiver), 'receiver availability')
    wrong_output = [row[:] for row in direct_output]
    wrong_output[0][0] = 0
    reject('incorrect-identity-shadow', lambda: require_identity(contract_check(direct, wrong_output)[1]),
           'identity shadow mismatch')
    reject('old-strict-checker-equal-frame-contract', lambda: m.check_network(PORTS, projected_chain, chain_output),
           'confined strict descent')
    reject('corrupted-vendor', lambda: authenticate_bytes(vendor_bytes + b'\n', vendor_row), 'source SHA256 mismatch')
    authenticate()
    receipt = dict(status='PASS_P104_AMBIENT_RELAY_FLOOR', source_pins=source_rows,
                   geometry=dict(frames=len(frames), strict_pairs=strict, equal_contractions=equal,
                                 strict_cost_reductions=reduced, parent_inclusion_pairs=parent_pairs,
                                 local_generators=local_cases, receiver_cases=receiver_cases),
                   fixtures=fixtures, controls=controls, maximum_network_moves=9,
                   limitations=['Finite geometry and network fixtures support the written contraction theorem; they do not enumerate all networks.',
                                'No additional ambient local sources are admitted.',
                                'The old strict checker rejects equal frames by its original contract; this is not a predecessor defect.',
                                'No physical P104 word, full invoice, supplier admission or frontier change.'])
    receipt = plain(receipt)
    certificate = HERE / 'CERTIFICATE.json'
    if args.write:
        certificate.write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n',
                               encoding='utf-8', newline='\n')
    else:
        require(json.loads(certificate.read_bytes()) == receipt, 'recorded certificate differs')
    print(json.dumps(receipt, sort_keys=True, separators=(',', ':')))
    print('PASS_P104_AMBIENT_RELAY_FLOOR')


if __name__ == '__main__':
    main()
