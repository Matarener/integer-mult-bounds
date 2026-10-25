"""Recount finite invoice inequalities; do not infer a uniform stage coefficient."""

from intervals import require


def positive(value, name):
    require(type(value) is int and 0 < value < 2**100000, name)
    return value


def local_costs(invoice):
    providers = invoice["providers"]
    require(set(providers) == {"gauge44", "extra"}, "two providers")
    for provider in providers.values():
        require(provider["helpers"] == 408 and provider["zero_buffers"] == 91,
                "literal helper/private inventory")
        require(set(provider["local"]) == {"forward", "backward"}, "orientations")
        for local in provider["local"].values():
            require(type(local["private_zero_buffer_peak"]) is int and
                    local["private_zero_buffer_peak"] == 91, "private peak")
            require(type(local["private_zero_buffer_clears"]) is int and
                    local["private_zero_buffer_clears"] == 182, "all clears paid")
            require(local["macros"] == local["literal_scalar_macros"] + 182,
                    "allocation/free macro charge")
            require(local["real_component_primitives"] ==
                    local["literal_real_component_primitives"] + 364, "component clears")
        records = tuple(provider["local"].values())
        adapters = 16 * (max(x["macros"] for x in records) +
                         max(x["warp_events"] for x in records) + provider["children"] +
                         632 + 8 + 91 + 2) + 64 * 73
        require(provider["local_adapters"] == adapters, "complete routing reserve")
        bound = max(x["real_component_primitives"] for x in records) + adapters * 64 * 74**3
        require(positive(provider["local_primitive_bound"], "local bound") == bound,
                "scalar, warp, wrapper and routing bound")
    return max(x["local_primitive_bound"] for x in providers.values())


def check_invoice(invoice, mass):
    require(invoice["status"] ==
            "PASS_INDEPENDENT_MIXED_ASYNC_SCALAR_PREFIX_AND_FINITE_INVOICE", "finite status")
    live, physical = 896 * 74, 896 * 74 + 408 + 8 + 91 + 2
    require(invoice["live"] == live and invoice["physical"] == physical, "physical stock")
    require(invoice["charged_prefix_bits"] == 2048, "source prefix payload")
    require(type(invoice["global_prefix_bits"]) is int and
            0 < invoice["global_prefix_bits"] <= 2048, "prefix fit")
    require(invoice["compiler"] == 64 * 74**3, "retained compiler reserve")
    local = local_costs(invoice)
    require(invoice["local_primitive_bound"] == local, "maximum local bill")
    used = positive(invoice["conservative_pervertex_used"], "pervertex bound")
    group = 2**(36 * 36)
    for index in range(1, 37):
        group *= 2**(2 * index) - 1
    stock = group * physical
    streamed_mass = group * mass
    logical = group * used + 64
    router = 64 * 74**3 * (logical + 1) * (stock + 1)**2
    literal = 2 * 2**30000 * stock**2 + 8 * streamed_mass + 4 * stock + 4 + 32 * 73
    total_mass = streamed_mass + 2**100000
    row = 2 * stock.bit_length() + 9909 + 252 + 2 * 2048
    checks = {"local_primitive_bound": local < 2**48, "logical": logical < 2**6050,
              "router": router < 2**30000, "literal": literal < 2**100000,
              "mass": total_mass < 2**100001,
              "precision": 32 * 73 * total_mass**2 < 2**210000,
              "tape": 2 * total_mass + 18 < 2**210000, "row": row < 20161,
              "halving": 73**2 > 2 * 48**2}
    stored = invoice["strict_checks"]
    require(set(stored) == set(checks) and all(type(x) is bool for x in stored.values()),
            "strict finite Boolean schema")
    require(stored == checks and all(checks.values()), "all finite inequalities")
    require(invoice["finite"]["physical_row_coefficient"] == row, "row recount")
    return {"strict_checks": checks, "live": live, "physical": physical,
            "global_prefix_bits": invoice["global_prefix_bits"], "charged_prefix_bits": 2048,
            "local_primitive_bound": local, "physical_row_coefficient": row,
            "required_C0_bits": (32 * 73 * total_mass**2).bit_length(),
            "scope": "Finite invoice arithmetic and named reserves only; no uniform time coefficient or stock-envelope implication."}
