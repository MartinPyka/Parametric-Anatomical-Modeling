import bpy


# TODO(SK): Missing docstring
class MaterialProperty(bpy.types.PropertyGroup):
    material = bpy.props.StringProperty(name="Material")
    materialOption = bpy.props.EnumProperty(
        name="materialOption",
        items=(
            ('DEFAULT', 'Default', 'Creates a default material for you'),
            ('CUSTOM', 'Custom', 'You can choose a custom material for the neurons. Remember to turn on Object Color!')
        ),
        default='DEFAULT'
    )

    colorizingMethod = bpy.props.EnumProperty(
        name = "Colorization method",
        items = (
            ('NONE', 'No colorization', 'The object colors of the spikes will remain unchanged'),
            ('LAYER', 'By layer', 'Gives each spike the color of its source layer'),
            ('SIMULATE', 'By simulation', 'Tries to generate colors by simulating the spiking activity'),
            ('MASK', 'Mask', 'Gives every spike originating from a neuron iside of a specified mask a given color')
        ),
        default = 'NONE'
    )

    maskObject = bpy.props.StringProperty(name = "Mask")
    insideMaskColor = bpy.props.FloatVectorProperty(name = "Spike color inside", default = (1.0, 0.0, 0.0, 1.0), subtype = 'COLOR', size = 4, min = 0.0, max = 1.0)
    outsideMaskColor = bpy.props.FloatVectorProperty(name = "Spike color outside", default = (0.0, 1.0, 0.0, 1.0), subtype = 'COLOR', size = 4, min = 0.0, max = 1.0)

    script = bpy.props.StringProperty(name = "Script")


# TODO(SK): Missing docstring
def register():
    bpy.utils.register_class(MaterialProperty)
    bpy.types.Scene.pam_anim_material = bpy.props.PointerProperty(type=MaterialProperty)


# TODO(SK): Missing docstring
def unregister():
    del bpy.types.Scene.pam_anim_material
    bpy.utils.unregister_class(MaterialProperty)
