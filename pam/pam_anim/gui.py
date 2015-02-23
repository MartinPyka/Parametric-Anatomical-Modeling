"""PAM-anim GUI module"""

import bpy

from .. import model


class PamAnimDataPane(bpy.types.Panel):
        """Panel for loading the Model Data"""

        bl_space_type = "VIEW_3D"
        bl_region_type = "TOOLS"
        bl_context = "objectmode"
        bl_label = "Model data"
        bl_category = "PAM-Anim"

        def draw(self, context):
                layout = self.layout
                row = layout.column()
                row.prop(context.scene.pam_anim_data, "modelData")
                row.prop(context.scene.pam_anim_data, "simulationData")


class PamAnimMaterialPane(bpy.types.Panel):
        """Panel for choosing the used Material"""

        bl_space_type = "VIEW_3D"
        bl_region_type = "TOOLS"
        bl_context = "objectmode"
        bl_label = "Material"
        bl_category = "PAM-Anim"

        def draw(self, context):
                layout = self.layout

                options = bpy.context.scene.pam_anim_material

                row = layout.row()
                row.prop(bpy.context.scene.pam_anim_material, 'materialOption', expand=True)

                if(options.materialOption == "CUSTOM"):
                        row = layout.row()
                        row.prop_search(context.scene.pam_anim_material, "material", bpy.data, "materials")


class PamAnimOrientationPane(bpy.types.Panel):
        """Panel for choosing object orientation"""

        bl_space_type = "VIEW_3D"
        bl_region_type = "TOOLS"
        bl_context = "objectmode"
        bl_label = "Object orientation"
        bl_category = "PAM-Anim"

        def draw(self, context):
                layout = self.layout

                options = bpy.context.scene.pam_anim_orientation

                row = layout.row()
                row.prop(options, 'orientationType', expand=True)

                if(options.orientationType == 'OBJECT'):
                        row = layout.row()
                        row.prop_search(options, 'orientationObject', bpy.data, "objects")


class PamAnimMeshPane(bpy.types.Panel):
        """Panel for choosing the used Mesh"""

        bl_space_type = "VIEW_3D"
        bl_region_type = "TOOLS"
        bl_context = "objectmode"
        bl_label = "Mesh"
        bl_category = "PAM-Anim"

        def draw(self, context):
                layout = self.layout

                options = bpy.context.scene.pam_anim_mesh

                row = layout.row()
                row.prop_search(options, 'mesh', bpy.data, 'meshes')

                row = layout.row()
                row.prop(options, 'animSpikes')

                row = layout.row()
                row.prop_search(options, 'neuron_object', bpy.data, 'objects')


class PamAnimAnimPane(bpy.types.Panel):
        """Panel for selecting the animation frames and speed"""
        bl_space_type = "VIEW_3D"
        bl_region_type = "TOOLS"
        bl_context = "objectmode"
        bl_label = "Animation"
        bl_category = "PAM-Anim"

        def draw(self, context):
                layout = self.layout

                options = bpy.context.scene.pam_anim_animation

                row = layout.row()
                col = row.column()
                sub = col.column(align=True)
                sub.label(text="Frames:")
                sub.prop(options, "startFrame")
                sub.prop(options, "endFrame")

                row = layout.row()
                col = row.column()
                sub = col.column(align=True)
                sub.label(text="Time:")
                sub.prop(options, "startTime")
                sub.prop(options, "endTime")

                row = layout.row()
                row.prop(options, "connNumber")


class PamAnimLayerPane(bpy.types.Panel):
        """Panel for choosing layer colors"""

        bl_space_type = "VIEW_3D"
        bl_region_type = "TOOLS"
        bl_context = "objectmode"
        bl_label = "Layer colors"
        bl_category = "PAM-Anim"

        def draw(self, context):
                layout = self.layout

                options = bpy.context.scene.pam_anim_material

                row = layout.row()
                row.prop_search(options, "script", bpy.data, "texts")


class PamAnimGeneratePanel(bpy.types.Panel):
        """Panel for the generate-button"""

        bl_space_type = "VIEW_3D"
        bl_region_type = "TOOLS"
        bl_context = "objectmode"
        bl_label = "Generate"
        bl_category = "PAM-Anim"

        def draw(self, context):
                layout = self.layout

                row = layout.row()
                # row.scale_y = 2.0
                row.operator("pam_anim.generate")
                row = layout.row()
                row.operator("pam_anim.clear_pamanim")
