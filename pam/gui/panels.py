"""PAM panels module"""

import bpy


class PAMModelDataPanel(bpy.types.Panel):
    """A panel for loading and saving model data"""

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Model data"
    bl_category = "PAM"

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.operator("pam.model_load", text="Load")
        row.operator("pam.model_save", text="Save")


class PAMToolsPanel(bpy.types.Panel):
    """A tools panel inheriting all neuronal modelling operations"""

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Connections"
    bl_category = "PAM"

    def draw(self, context):
        layout = self.layout
        row = layout.column()
        row.operator(
            "pam_vis.visualize_connections_for_neuron",
            "Connections at Cursor"
        )
        row.operator(
            "pam_vis.visualize_unconnected_neurons",
            "Unconnected neurons"
        )
        row.separator()
        row.prop(
            context.scene.pam_visualize,
            "connections",
            text="Connections"
        )
        row.operator(
            "pam_vis.visualize_connections_all",
            "Connections for all mappings"
        )
        row.operator("pam_vis.visualize_clean", "Clear Visualizations")


class PAMVisualizeKernelToolsPanel(bpy.types.Panel):
    """A tools panel for visualization of kernel function """

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Kernel"
    bl_category = "PAM"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        active_obj = context.active_object

        name = mesh_object_name(active_obj)
        customs = context.scene.pam_visualize.customs
        layout = self.layout

        row = layout.row()
        row.prop(context.scene.pam_visualize, "view", text="")

        row = layout.row()
        row.label("Active: %s" % name)

        row = layout.row()
        row.prop(context.scene.pam_visualize, "resolution", text="Resolution")

        row = layout.row()
        row.prop(context.scene.pam_visualize, "kernel", text="")

        row = layout.row()
        row.label("Parameter:")

        row = layout.row()
        row.template_list(
            listtype_name="CustomPropList",
            dataptr=context.scene.pam_visualize,
            propname="customs",
            active_dataptr=context.scene.pam_visualize,
            active_propname="active_index",
            type="DEFAULT",
            rows=6,
        )
        # col = row.column(align=True)
        # col.operator("pam.add_param", icon="ZOOMIN", text="")
        # col.operator("pam.remove_param", icon="ZOOMOUT", text="")

        # row = layout.row(align=True)
        # row.template_preview(context.blend_data.textures.get("pam.temp_texture"))

        row = layout.row(align=True)
        op = row.operator("pam.reset_params", text="Reset parameter")

        layout.separator()

        row = layout.row()
        row.prop(context.scene.pam_visualize, "mode", expand=True)

        row = layout.row()
        op = row.operator("pam.visualize", text="Generate texture")


class PAMModelingPanel(bpy.types.Panel):
    """A panel for loading and saving model data"""

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Modeling Tools"
    bl_category = "PAM"

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.operator("pam.map_via_uv", text="Deform mesh via UV")


class PAMMeasureToolsPanel(bpy.types.Panel):
    """A tools panel inheriting all measurment operations"""

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Measure"
    bl_category = "PAM"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        active_obj = context.active_object

        name = mesh_object_name(active_obj)

        layout = self.layout
        layout.label("Active: %s" % name)

        row = layout.row()
        col = row.column(align=True)
        col.prop(context.scene.pam_measure, "quantity", text="Neurons")
        col.prop(context.scene.pam_measure, "area", text="Area")

        row = layout.row()
        col = row.column()
        op = col.operator("pam.measure_layer", "Calculate")
        col.label("Total neurons: %d" % context.scene.pam_measure.neurons)
        col.label("Total area: %d" % context.scene.pam_measure.total_area)


class PAMMappingToolsPanel(bpy.types.Panel):
    """A tools panel inheriting all mapping functionality"""

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Mapping"
    bl_category = "PAM Mapping"

    def draw(self, context):
        active_obj = context.active_object
        mapping = context.scene.pam_mapping

        layout = self.layout

        # PreSynapticLayer
        layout.label("Pre-Synaptic:")
        box = layout.box()
        box.prop(mapping.presynapse, "object_name", text="Object")
        box.prop(mapping.presynapse, "kernel_function", text="Kernel")
        box.prop(mapping.presynapse, "mapping", text="Mapping")
        box.prop(mapping.presynapse, "distance", text="Distance")

        layout.separator()

        # PreIntermediateLayers
        layout.label("Pre-Intermediates:")
        row = layout.row()
        row.template_list(
            listtype_name="IntermediateLayerList",
            dataptr=mapping,
            propname="preintermediates",
            active_dataptr=mapping,
            active_propname="active_preintermediates",
            type="DEFAULT",
            rows=3,
        )

        layout.separator()

        # SynapticLayer
        layout.label("Synaptic:")
        box = layout.box()
        box.prop(mapping.synapse, "object_name", text="Object")
        box.prop(mapping.synapse, "mapping", text="Mapping")
        box.prop(mapping.synapse, "distance", text="Distance")

        layout.separator()

        # PostIntermediateLayers
        layout.label("Post-Intermediates:")
        row = layout.row()
        row.template_list(
            listtype_name="IntermediateLayerList",
            dataptr=mapping,
            propname="postintermediates",
            active_dataptr=mapping,
            active_propname="active_postintermediates",
            type="DEFAULT",
            rows=3,
        )

        layout.separator()

        # PostSynapticLayer
        layout.label("Post-Synaptic:")
        box = layout.box()
        box.prop(mapping.postsynapse, "object_name", text="Object")
        box.prop(mapping.postsynapse, "kernel_function", text="Kernel")


# TODO(SK): missing docstring
class CustomPropList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        layout.prop(item, "name", text="", emboss=False)
        layout.prop(item, "value", text="", emboss=False, slider=False)


class IntermediateLayerList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        layout.prop(item, "object_name", text="", emboss=False)


# TODO(SK): missing docstring
def mesh_object_name(obj):
    name = ""
    if obj is not None:
        if obj.type == "MESH":
            name = obj.name

    return name
