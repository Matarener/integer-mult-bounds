# SPDX-License-Identifier: Apache-2.0
"""Reduced complete C-tensor binding for exercising the actual controller.

This deliberately has no claimed favorable moment. It checks the physical
joins on manageable complete domains; selected source binding is separate.
"""
from cover import OrthogonalCover
from scalar_program import ScalarProgram
from selected_binding import Group, literal


class FixtureBinding:
    dimension = 2
    maximum_rank = 1
    families = 2
    slots = 2
    private = 1
    events = ("complete_tensor",)

    def __init__(self):
        self.cover = OrthogonalCover(2)
        self.catalogue = {key: ScalarProgram(*key) for key in
                          (("add", 1, 1), ("add", -1, 1), ("scale", -1, 1))}

    def group_count(self, event):
        if event != 0:
            raise ValueError("fixture event")
        return 1

    def group(self, event, subgroup, cover):
        if event != 0 or subgroup != 0:
            raise ValueError("fixture group")
        recipes = {"view": literal(self.cover.unrank(cover)), "swap": literal((2, 1))}
        code = [("monomial", -1, role, "view", True) for role in range(2)]
        code += [("zero", -1, 2), ("copy", -1, 2, 0), ("child", -1, 2, 1),
                 ("scalar", -1, 1, 2, ("add", 1, 1)),
                 ("scalar", -1, 1, 2, ("add", -1, 1)), ("zero", -1, 2),
                 ("scalar", -1, 1, 0, ("add", 1, 1))]
        for role in range(2):
            code += [("child", -1, role, 1), ("monomial", -1, role, "swap", False),
                     ("child", -1, role, 1), ("monomial", -1, role, "swap", True)]
        code += [("scalar", -1, 1, 0, ("add", -1, 1))]
        code += [("exchange", -1, 0, 1)] * 4
        code += [("monomial", -1, role, "view", False) for role in range(2)]
        return Group(((0, cover), (1, cover)), tuple(code), recipes)
