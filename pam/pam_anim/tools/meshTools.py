import bpy


class MeshProperty(bpy.types.PropertyGroup):
    mesh = bpy.props.StringProperty(name="Mesh")
    neuron_object = bpy.props.StringProperty(name="Neuron Object")
    animSpikes = bpy.props.BoolProperty(name="Animate spikes")


def register():
    bpy.utils.register_class(MeshProperty)
    bpy.types.Scene.pam_anim_mesh = bpy.props.PointerProperty(type=MeshProperty)


def unregister():
    del bpy.types.Scene.pam_anim_mesh
    bpy.utils.unregister_class(MeshProperty)
