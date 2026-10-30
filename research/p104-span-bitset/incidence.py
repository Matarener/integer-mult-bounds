"""Exact binary incidence sections; Apache-2.0, produced by Nick Petalas."""


def require(condition, message):
    if not condition:
        raise ValueError(message)


def zero_masks(ports, width):
    """Bit i is set precisely when port i pairs evenly with the section."""
    require(type(width) is int and 2 <= width <= 9, "width must be 2..9")
    require(type(ports) is tuple and len(ports) <= 1 << width, "bounded port tuple")
    require(all(type(q) is int and 0 <= q < 1 << width for q in ports),
            "port labels must fit the declared width")
    require(len(set(ports)) == len(ports), "distinct port labels")
    return tuple(sum(1 << i for i, q in enumerate(ports)
                     if (q & z).bit_count() % 2 == 0)
                 for z in range(1, 1 << width))


def capacities(ports, width):
    """Retain every unordered pair of distinct nonzero section labels."""
    masks = zero_masks(ports, width)
    one = max(mask.bit_count() for mask in masks)
    two = max((first & second).bit_count()
              for i, first in enumerate(masks) for second in masks[i + 1:])
    return {width - 2: two, width - 1: one}
