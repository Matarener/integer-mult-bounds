"""Public grouped source visits and fresh Residual-wrapper accounting.

Groups have sizes K and disjointly cover request IDs 0..R-1; empty groups are
allowed. Each group makes rho=replicas passes over its K*N source keys. Local
common groups are LOW-major, idle noncommon groups ID-major. ID order is the
given tuple, not numeric order. A key is (request_id, common, LOW ordinal).

Proof: each key belongs to exactly one group and occurs once per group pass.
Thus M=R*N distinct keys each have multiplicity rho, and T=rho*R*N visits.
Under the public source-audited factory/Code contract, every visit creates a
fresh Residual wrapper retained by Code: T objects, not M. Each wrapper has
one begin and one end reference, giving exactly 2*T such references. Additional
plan-dependent block references B are NOT counted here; total references are
2*T+B. Specifications DOES cache source records/plans; that caching does not
intern the Residual wrappers. This is not a byte-cost or native-cost model.

Only abstract histories of at most 64 calls may be expanded. Arithmetic needs
no source imports, frozen files, source execution, or actual optimization.
"""
from dataclasses import dataclass


def need(ok, message):
    if not ok:
        raise ValueError(message)


def nat(value, name):
    need(type(value) is int and value >= 1, name + ': expected an exact positive integer')


@dataclass(frozen=True)
class Group:
    kind: str
    order: str
    request_ids: tuple
    common: bool


def validate(groups, replicas):
    nat(replicas, 'replicas')
    try:
        groups = tuple(groups)
    except TypeError as exc:
        raise ValueError('groups must be iterable') from exc
    need(groups, 'at least one group required')
    ids = []
    for g in groups:
        need(type(g) is Group, 'expected Group')
        need(type(g.request_ids) is tuple and type(g.common) is bool, 'canonical IDs/common')
        need((g.kind, g.order, g.common) in (
            ('local_cover_sweep', 'low-major', True), ('idle', 'id-major', False)),
            'unsupported kind/order/common contract')
        need(all(type(i) is int and i >= 0 for i in g.request_ids), 'nonnegative integer IDs')
        ids.extend(g.request_ids)
    need(ids and len(ids) == len(set(ids)) and set(ids) == set(range(len(ids))),
         'groups must disjointly cover a nonempty canonical request interval')
    return groups, len(ids)


def visit_invoice(groups, replicas, N):
    """Count source keys, fresh wrappers and begin/end refs; block refs B stay unknown."""
    groups, R = validate(groups, replicas)
    nat(N, 'LOW classes')
    M, T = R*N, replicas*R*N
    return dict(replicas=replicas, requests=R, low_count=N,
                group_sizes=[len(g.request_ids) for g in groups],
                source_visits=T, distinct_keys=M, key_multiplicity=replicas,
                fresh_residual_objects=T, retained_residual_objects=T,
                begin_references=T, end_references=T, begin_end_references=2*T,
                block_references=None, total_reference_formula='2*T+B')


def projected_keys(groups, replicas, N):
    """Abstract testing only: reject TOTAL histories over 64 calls before expansion."""
    groups, R = validate(groups, replicas)
    nat(N, 'LOW classes')
    need(replicas*R*N <= 64, 'abstract history exceeds 64 calls')
    for g in groups:
        for _ in range(replicas):
            if g.order == 'low-major':
                for ordinal in range(N):
                    for identifier in g.request_ids:
                        yield identifier, g.common, ordinal
            else:
                for identifier in g.request_ids:
                    for ordinal in range(N):
                        yield identifier, g.common, ordinal
