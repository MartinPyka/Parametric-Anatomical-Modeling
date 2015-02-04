import bpy


class OrientationProperties(bpy.types.PropertyGroup):
    orientationType = bpy.props.EnumProperty(
        name="materialOption",
        items=(
            ('NONE', 'None', 'Neuron orientation is not influenced'),
            ('OBJECT', 'Object', 'The neurons are tracking a specific object, e.g. a camera'),
            ('FOLLOW', 'Follow Curve', 'The neuron orientation is following the curve')
        ),
        default = 'NONE'
    )
    orientationObject = bpy.props.StringProperty(name="Orientation object")


def register():
    bpy.utils.register_class(OrientationProperties)
    bpy.types.Scene.pam_anim_orientation = bpy.props.PointerProperty(type=OrientationProperties)


def unregister():
    del bpy.types.Scene.pam_anim_orientation
    bpy.utils.unregister_class(OrientationProperties)
