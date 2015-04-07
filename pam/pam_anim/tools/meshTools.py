import bpy


# TODO(SK): Missing docstring
class MeshProperty(bpy.types.PropertyGroup):
    mesh = bpy.props.StringProperty(name="Mesh")
    neuron_object = bpy.props.StringProperty(name="Neuron Object")
    animPaths = bpy.props.BoolProperty(name="Animate paths", default=True)
    animSpikes = bpy.props.BoolProperty(name="Animate spikes")


# TODO(SK): Missing docstring
def register():
    bpy.utils.register_class(MeshProperty)
    bpy.types.Scene.pam_anim_mesh = bpy.props.PointerProperty(type=MeshProperty)


# TODO(SK): Missing docstring
def unregister():
    del bpy.types.Scene.pam_anim_mesh
    bpy.utils.unregister_class(MeshProperty)
