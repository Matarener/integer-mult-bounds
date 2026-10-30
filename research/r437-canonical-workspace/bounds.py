"""Source-parameter bounds, evaluated by the checker and never by the runtime.

Prepared for commdata2338 with substantial OpenAI Codex assistance. Apache-2.0.
The local consumer extent bound is inherited explicitly from PR #5187.
"""


def backing(*, q, prefixes, fibre, old_fields, code_bits, dimension,
            residue_bits, index_bits, program_body, callback_depth):
    values = (q, prefixes, fibre, old_fields, code_bits, dimension,
              residue_bits, index_bits, program_body, callback_depth)
    if any(type(x) is not int for x in values) or q < 2 or min(
            prefixes, fibre, code_bits, dimension, residue_bits, index_bits) < 1 or min(
            old_fields, program_body, callback_depth) < 0:
        raise ValueError("valid exact source extents")
    field = code_bits + 1 + dimension**2 * (residue_bits + 1) + 1
    record = max(2 * index_bits + 4, residue_bits + 3)
    body = max(fibre, (old_fields + 1) * field, program_body,
               (2 * callback_depth + 3) * record, index_bits + 3,
               residue_bits + 3, fibre.bit_length() + 3, prefixes.bit_length() + 3)
    roles = q*q + 141
    return dict(field_body=field, pool_roles=roles, pool_body_bound=body,
                pool_cells=roles * (body + 2),
                three_producer_cells=(2*old_fields + 1)*field + index_bits + 7,
                full_output_cells=prefixes*fibre + 2)


def pooling_surcharge(*, roles, prefixes, acquisitions, callback_closes):
    if any(type(x) is not int for x in (roles, prefixes, acquisitions, callback_closes)) or (
            roles < 5 or prefixes < 1 or min(acquisitions, callback_closes) < 0):
        raise ValueError("valid pooling tariff counts")
    # Four entry role guards; three exit role guards; one final pool.empty.
    return acquisitions + 28*callback_closes + 4*(roles-5)*prefixes + 4*roles + 28


def commit_and_retire(output_bits, previous_destination_bits):
    n, t = output_bits, previous_destination_bits
    if type(n) is not int or type(t) is not int or min(n, t) < 0:
        raise ValueError("nonnegative contiguous body extents")
    return dict(reads=2*t + 7*n + 10, writes=t + 2*n, moves=2*t + 6*n + 14)
