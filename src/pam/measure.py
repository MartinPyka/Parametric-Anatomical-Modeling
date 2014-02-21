"""PAM Measurements Module"""

import logging

import bpy

logger = logging.getLogger(__package__)


class PAMMeasureMesh(bpy.types.Operator):
    """Computes neuron distribution across the active object"""

    bl_idname = "pam.measure_mesh"
    bl_label = "Measure mesh"
    bl_description = "Computes neuron distribution on mesh"

    @classmethod
    def poll(cls, context):
        active_obj = context.active_object
        return active_obj.type == "MESH"

    def execute(self, context):
        active_obj = context.active_object

        return {'FINISHED'}
