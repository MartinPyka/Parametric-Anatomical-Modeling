"""PAM menus module"""

import bpy


class PAMMappingMenu(bpy.types.Menu):
    bl_idname = "pam.mapping_menu"
    bl_label = "Mapping"

    def draw(self, context):
        layout = self.layout

        layout.operator("pam.mapping_set_layer", "Set as presynapse").layer = "presynapse"
        layout.operator("pam.mapping_set_layer", "Add to preintermediate").layer = "preintermediates"
        layout.operator("pam.mapping_set_layer", "Set as synapse").layer = "synapse"
        layout.operator("pam.mapping_set_layer", "Add to postintermediates").layer = "postintermediates"
        layout.operator("pam.mapping_set_layer", "Set as postsynapse").layer = "postsynapse"
