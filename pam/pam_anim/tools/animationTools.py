import bpy


class AnimationProperty(bpy.types.PropertyGroup):
        startFrame = bpy.props.IntProperty(name="Start frame", default=0)
        endFrame = bpy.props.IntProperty(name="End frame", default=100)

        startTime = bpy.props.FloatProperty(name="Start time", default=0.0)
        endTime = bpy.props.FloatProperty(name="End time", default=1.0)


def register():
        bpy.utils.register_class(AnimationProperty)
        bpy.types.Scene.pam_anim_animation = bpy.props.PointerProperty(type=AnimationProperty)


def unregister():
        del bpy.types.Scene.pam_anim_animation
        bpy.utils.unregister_class(AnimationProperty)
