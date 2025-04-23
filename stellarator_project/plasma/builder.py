# SPDX-FileCopyrightText: 2024-present United Kingdom Atomic Energy Authority
#
# SPDX-License-Identifier: MIT
"""Plasma Builder."""

from __future__ import annotations

from bluemira.base.builder import Builder
from bluemira.base.components import Component, PhysicalComponent
from bluemira.codes._freecadapi import fix_shape  # noqa: PLC2701
from bluemira.display.palettes import BLUE_PALETTE
from bluemira.geometry.face import BluemiraFace
from bluemira.geometry.shell import BluemiraShell
from bluemira.geometry.solid import BluemiraSolid
from bluemira.geometry.tools import make_bsplinesurface


class PlasmaBuilder(Builder):
    """Build the 3D geometry of a plasma from a given LCFS."""

    param_cls = None

    def __init__(self, surface_data: dict, build_config: dict):
        super().__init__(None, build_config)
        self.s_data = surface_data

    def build(self) -> Component:
        """Run the full build of the Plasma."""
        return self.component_tree(
            xz=None,
            xy=None,
            xyz=[self.build_xyz()],
        )

    def build_xyz(self) -> PhysicalComponent:
        """Build the plasma."""
        # Create a plasma surface from NURBS surface data
        face_tube = make_bsplinesurface(
            poles=self.s_data.poles2d,
            mults_u=self.s_data.mults_u,
            mults_v=self.s_data.mults_v,
            knot_vector_u=self.s_data.internal_knot_vector_u,
            knot_vector_v=self.s_data.internal_knot_vector_v,
            degree_u=self.s_data.degree_u,
            degree_v=self.s_data.degree_v,
            weights=self.s_data.weights_reshaped,
            periodic=False,
            check_rational=False,
        )
        faces = [
            BluemiraFace(wire)
            for wire in sorted(face_tube.edges, key=lambda edge: edge.length)[:2]
        ]
        faces.insert(1, face_tube)

        plasma_surface = BluemiraSolid(BluemiraShell(faces))

        if not plasma_surface.is_valid():
            fix_shape(plasma_surface._shape)  # noqa: SLF001

        component = PhysicalComponent("LCFS", plasma_surface)
        component.display_cad_options.color = BLUE_PALETTE["PL"]
        component.display_cad_options.transparency = 0.5
        return component
