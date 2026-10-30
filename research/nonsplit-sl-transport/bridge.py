"""Connect recovered residue tables to fixed models and special-linear transport.

Field-table identifications use primitive components of C tensor D, without
enumerating either extension field. Reference residue presentations are supplied;
they are not discovered canonically. The retained character witness routines do
enumerate explicit residue fields, so the complete API has no polynomial-time
claim. New work by apoursh with substantial OpenAI Codex assistance, Apache-2.0.
Predecessor sources and notices remain byte-for-byte unchanged.
"""

import builtins
import hashlib
import json
from itertools import product
from pathlib import Path
from types import ModuleType


ROOT = Path(__file__).resolve().parent
ORIGINS_SHA256 = "6fff7388379b3a02558caf3c7225bf590717fe69b69c871f94a5bd217c795563"
_origins_bytes = (ROOT / "vendor/ORIGINS.json").read_bytes()
if hashlib.sha256(_origins_bytes).hexdigest() != ORIGINS_SHA256:
    raise ValueError("retained-source origin manifest hash mismatch")
_source_bytes = {}
for _entry in json.loads(_origins_bytes):
    _path = ROOT / _entry["path"]
    _data = _path.read_bytes()
    if hashlib.sha256(_data).hexdigest() != _entry["sha256"]:
        raise ValueError("retained-source hash mismatch: " + _entry["path"])
    _source_bytes[_entry["path"]] = _data


def _load(name, relative_path, importer=None):
    module = ModuleType(name)
    module.__file__ = str(ROOT / relative_path)
    if importer is not None:
        module.__dict__["__builtins__"] = dict(vars(builtins), __import__=importer)
    exec(compile(_source_bytes[relative_path], module.__file__, "exec"), module.__dict__)
    return module


# Retained imports name `vendor`; resolve only these imports in the executing
# module's builtins rather than installing or replacing a global vendor package.
characters = _load("nonsplit_transport_characters", "character_model.py")
local = characters.local
Field, Extension = characters.Field, characters.Extension
_vendor = ModuleType("nonsplit_transport_vendor")
_vendor.local = local


def _retained_import(name, globals=None, locals=None, fromlist=(), level=0):
    if level == 0 and name == "vendor":
        return _vendor
    if level == 0 and name == "vendor.split":
        return _vendor.split if fromlist else _vendor
    return builtins.__import__(name, globals, locals, fromlist, level)


split = _load("nonsplit_transport_split", "vendor/split.py", _retained_import)
_vendor.split = split
recognition = _load("nonsplit_transport_recognition", "vendor/recognize.py", _retained_import)


def field_isomorphism(source_table, target_table, base, component_choice=0):
    """Return an explicit matrix C -> D for two equal-degree K-field tables.

Both tables must have first basis vector one. Different primitive-component
choices return the different field isomorphisms; no choice is called canonical.
"""
    if not isinstance(base, Field):
        raise ValueError("base must be the retained explicit Field")
    if not recognition.field_table_valid(source_table, base):
        raise ValueError("source is not a coefficient-field table with first basis vector one")
    if not recognition.field_table_valid(target_table, base):
        raise ValueError("target is not a coefficient-field table with first basis vector one")
    d = len(source_table)
    if len(target_table) != d:
        raise ValueError("coefficient-field degrees differ")
    if type(component_choice) is not int or not 0 <= component_choice < d:
        raise ValueError("primitive-component choice must be in range(degree)")
    n = d * d
    tensor_product = [[[0] * n for _ in range(n)] for _ in range(n)]
    for i, j, k, ell in product(range(d), repeat=4):
        tensor_product[d*i+j][d*k+ell] = [
            base.mul[x][y] for x in source_table[i][k] for y in target_table[j][ell]
        ]
    unit = [1] + [0] * (n - 1)
    parts = recognition.primitive_parts(tensor_product, unit, base)
    if len(parts) != d:
        raise ArithmeticError("tensor product has the wrong number of primitive components")
    e = parts[component_choice]
    basis = local.identity(n)
    source_images = [local.tensor_value(tensor_product, e, basis[d*i], base) for i in range(d)]
    target_images = [local.tensor_value(tensor_product, e, basis[j], base) for j in range(d)]
    if local.rank(source_images, base) != d or local.rank(target_images, base) != d:
        raise ArithmeticError("coefficient embedding has the wrong rank")
    coordinates = split.coordinate_map(target_images, n, base)
    change = local.columns([coordinates(v) for v in source_images], d)
    if not local.determinant(change, base) or local.column(change, 0) != local.identity(d)[0]:
        raise ArithmeticError("coefficient-field identification is not unital and invertible")
    for i, j in product(range(d), repeat=2):
        if local.tensor_value(target_table, local.column(change, i), local.column(change, j), base) != local.mv(change, source_table[i][j], base):
            raise ArithmeticError("coefficient-field identification fails a basis product")
    return change


def normalize_certificate(t, certificate, base, residues, field_choices=None):
    """Check and normalize a PR5664 certificate to supplied reference fields.

`residues` maps each nontrivial degree to an Extension over `base`; degree one
may be omitted. All repeated degrees use the same reference presentation.
Component order and every discovered coefficient basis are transported explicitly.
    Optional `field_choices` are indexed in the sorted reference-component order.
"""
    if not isinstance(base, Field):
        raise ValueError("base must be the retained explicit Field")
    if not recognition.check_certificate(t, certificate, base):
        raise ValueError("invalid recovered-product certificate")
    components = certificate["components"]
    order = sorted(range(len(components)), key=lambda j: (components[j]["degree"], components[j]["heights"]))
    types = [[components[j]["degree"], components[j]["heights"]] for j in order]
    model = characters.make_model(base, types, residues)
    if field_choices is None:
        field_choices = [0] * len(order)
    if not isinstance(field_choices, (list, tuple)) or len(field_choices) != len(order):
        raise ValueError("one primitive-component choice is required for each model component")
    source_offsets, offset = [], 0
    for component in components:
        source_offsets.append(offset)
        offset += component["degree"] * base.p ** sum(component["heights"])
    n = model["n"]
    change = [[0] * n for _ in range(n)]
    field_maps = []
    for target_index, source_index in enumerate(order):
        component = components[source_index]
        d = component["degree"]
        reference = characters.make_model(base, [[d, []]], {d: model["residues"][d]})["table"]
        field_map = field_isomorphism(reference, component["field"], base, field_choices[target_index])
        field_maps.append(field_map)
        for monomial in range(model["local_dimensions"][target_index]):
            row_start = source_offsets[source_index] + d * monomial
            col_start = model["offsets"][target_index] + d * monomial
            for i, j in product(range(d), repeat=2):
                change[row_start+i][col_start+j] = field_map[i][j]
    maps = {name: local.mm(certificate[name], change, base) for name in ("U", "V", "W")}
    checked = characters.validate_certificate(model, t, **maps)
    return dict(checked, model=model, bridge=change, field_maps=field_maps, **maps)


def recognize(t, base, residues):
    """Return (normalized certificate, None), or (None, nonmembership reason).

    Invalid tensor shapes, base fields or reference parameters raise ValueError.
    """
    certificate, reason = recognition.recognize(t, base)
    if certificate is None:
        return None, reason
    return normalize_certificate(t, certificate, base, residues), None


def sl_transport(t1, t2, base, residues):
    """Return determinant-one P,Q,R with t2(Px,Qy)=R t1(x,y), or a reason.

The returned A=P^{-T}, B=Q^{-T}, C=R are the corresponding covariant
tensor-action maps. Both inputs are recognized and checked independently.
"""
    first_raw, reason = recognition.recognize(t1, base)
    if first_raw is None:
        return None, "first tensor: " + reason
    second_raw, reason = recognition.recognize(t2, base)
    if second_raw is None:
        return None, "second tensor: " + reason
    first_types = sorted((c["degree"], c["heights"]) for c in first_raw["components"])
    second_types = sorted((c["degree"], c["heights"]) for c in second_raw["components"])
    if first_types != second_types:
        return None, "component degree-and-height types differ"
    first = normalize_certificate(t1, first_raw, base, residues)
    second = normalize_certificate(t2, second_raw, base, residues)
    if first["label"] != second["label"]:
        return None, "special-linear orbit labels differ"
    ratios = [base.mul[x][base.inv[y]] for x, y in zip(first["determinants"], second["determinants"])]
    correction = characters.autotopism(first["model"], *ratios)
    maps = [local.mm(local.mm(second[k], correction[k], base), local.inverse(first[k], base), base)
            for k in ("U", "V", "W")]
    if [local.determinant(m, base) for m in maps] != [1, 1, 1]:
        raise ArithmeticError("transporter does not have determinant one on every factor")
    p, q, r = maps
    for i, j in product(range(len(t1)), repeat=2):
        if local.tensor_value(t2, local.column(p, i), local.column(q, j), base) != local.mv(r, t1[i][j], base):
            raise ArithmeticError("transporter fails a basis-product identity")
    return dict(P=p, Q=q, R=r,
                A=list(map(list, zip(*local.inverse(p, base)))),
                B=list(map(list, zip(*local.inverse(q, base)))), C=r,
                first=first, second=second, correction=correction), None
