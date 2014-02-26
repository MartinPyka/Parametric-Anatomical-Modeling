"""PAM Measurements Module"""

import logging
import math

import bpy

from . import utils

logger = logging.getLogger(__package__)

# XXX(SK): Are these numbers correct?
# XXX(SK): I guess there's at least a scaling factor missing.
# XXX(SK): quantity on complete layer vs. quantity on measurement unit^2
# TODO(SK): ca2 missing
neuron_density = {
    "dg": 0.000000833,
    "ec": 0.000009091,
    "ca1": 0.000002564,
    "ca3": 0.00004,
}


class PAMMeasureLayer(bpy.types.Operator):
    """Calculates neuron quantity across the active object

    Important:
        * depends on scene scaling
        * implemented only for metric system
    """

    bl_idname = "pam.measure_layer"
    bl_label = "Measure layer"
    bl_description = "Calculates neuron quantity on mesh"

    # TODO(SK): ca2 missing
    type = bpy.props.EnumProperty(
        name="Type",
        items=[
            ("dg", "Dentate Gyrus", "", 0),
            ("ec", "Entorhinal Cortex", "", 1),
            ("ca1", "Cornu Ammonis 1", "", 2),
            ("ca3", "Cornu Ammonis 3", "", 3),
        ],
        default="dg"
    )

    @classmethod
    def poll(cls, context):
        active_obj = context.active_object
        return active_obj.type == "MESH"

    def invoke(self, context, event):
        wm = context.window_manager
        unit_settings = context.scene.unit_settings

        if unit_settings.system == "IMPERIAL":
            logger.warn("imperial metrics not implemented")
            self.report("WARNING", "Imperial metrics are not support.")

            return {'CANCELLED'}

        return wm.invoke_props_dialog(self)

    def execute(self, context):
        active_obj = context.active_object
        unit_settings = context.scene.unit_settings

        density = neuron_density[self.type]
        scale = unit_settings.scale_length
        area = surface_area(active_obj)

        quantity = math.floor(area / (density / scale))

        logger.info(
            "%s of type %s with surface area %f and neuron quantity of %d",
            active_obj,
            self.type,
            area,
            quantity,
        )

        return bpy.ops.pam.popup(
            "INVOKE_DEFAULT",
            label="Quantity",
            value=str(quantity),
            width=200
        )


class PAMPopup(bpy.types.Operator):
    """Displays a popup panel with label and value"""

    bl_idname = "pam.popup"
    bl_label = "Popup panel"

    width = bpy.props.IntProperty()
    label = bpy.props.StringProperty()
    value = bpy.props.StringProperty()

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_popup(self, width=self.width)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        col = row.column()
        col.prop(self, "value", text=self.label)


@utils.profiling
def surface_area(obj):
    """Returns surface area of a mesh

    Important: return value is dependent scene scale"""

    if not obj.type == "MESH":
        raise Exception("Can't calculate area of none-mesh objects")

    return sum([polygon.area for polygon in obj.data.polygons])
