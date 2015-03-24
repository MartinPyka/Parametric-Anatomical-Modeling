"""PAM menus module"""

import bpy

from .. import mapping


class PAMMappingMenu(bpy.types.Menu):
    bl_idname = "pam.mapping_menu"
    bl_label = "Mapping"

    def draw(self, context):
        layout = self.layout

        pie = layout.menu_pie()

        for (key, name, _, _, _) in mapping.LAYER_TYPES[1:]:
            pie.operator("pam.mapping_layer_set", "Add layer as %s" % name).type = key

        pie.operator("pam.mapping_self_inhibition", "Add layer as self-inhibition mapping")


def register():
    if not bpy.app.background:
        wm = bpy.context.window_manager
        km = wm.keyconfigs.addon.keymaps.new(name="3D View Generic", space_type="VIEW_3D")
        kmi = km.keymap_items.new("wm.call_menu_pie", "SPACE", "PRESS", shift=True, ctrl=True)
        kmi.properties.name = "pam.mapping_menu"


def unregister():
    if not bpy.app.background:
        wm = bpy.context.window_manager
        km = wm.keyconfigs.addon.keymaps.find(name="3D View Generic", space_type="VIEW_3D")
        kmi = km.keymap_items["wm.call_menu_pie"]
        km.keymap_items.remove(kmi)
