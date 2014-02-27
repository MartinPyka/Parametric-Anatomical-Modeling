"""PAM Measurements Module"""

import logging
import math

import bpy

from . import utils

logger = logging.getLogger(__package__)


class PAMMeasureLayer(bpy.types.Operator):
    """Calculates neuron quantity across the active object

    Important:
        * depends on scene scaling
        * implemented only for metric system
    """

    bl_idname = "pam.measure_layer"
    bl_label = "Measure layer"
    bl_description = "Calculates neuron quantity on mesh"

    @classmethod
    def poll(cls, context):
        active_obj = context.active_object
        return active_obj.type == "MESH"

    def execute(self, context):
        active_obj = context.active_object

        quantity = context.scene.pam_quantity
        area = context.scene.pam_area
        surface = surface_area(active_obj)

        neurons = math.ceil(surface * (float(quantity) / area))

        logger.debug(
            "%s surface (%f) quantity (%d) area (%f) neurons (%d)",
            active_obj,
            surface,
            quantity,
            area,
            neurons
        )

        context.scene.pam_neurons = neurons

        return {'FINISHED'}

    def invoke(self, context, event):
        quantity = context.scene.pam_quantity
        area = context.scene.pam_area

        if not quantity > 0 or not area > 0.0:
            logger.warn("quantiy/area can not be zero or smaller")
            self.report(
                {'WARNING'},
                "Quantiy/Area must be non-zero and positive."
            )
            return {'CANCELLED'}

        return self.execute(context)


def register():
    bpy.types.Scene.pam_area = bpy.props.FloatProperty(
        name="Area",
        default=1.0,
        min=0.0,
        unit="AREA"
    )
    bpy.types.Scene.pam_quantity = bpy.props.IntProperty(
        name="Quantity",
        default=1,
        min=1,
        step=100,
        soft_max=10000000,
        subtype="UNSIGNED"
    )
    bpy.types.Scene.pam_neurons = bpy.props.IntProperty(
        name="Neurons",
        default=0,
        subtype="UNSIGNED"
    )


def unregister():
    del bpy.types.Scene.pam_density
    del bpy.types.Scene.pam_quantity


@utils.profiling
def surface_area(obj):
    """Returns surface area of a mesh

    Important: return value is dependent scene scale"""

    if not obj.type == "MESH":
        raise Exception("Can't calculate area of none-mesh objects")

    return sum([polygon.area for polygon in obj.data.polygons])
