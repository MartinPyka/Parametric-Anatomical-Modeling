import bpy
from ... import model

class LayerItem(bpy.types.PropertyGroup):
    layerName = bpy.props.StringProperty(name = "Layer")
    layerIndex = bpy.props.IntProperty(name = "Layer index")
    layerGenerate = bpy.props.BoolProperty(name = "Generate from", default = True)

# TODO(SK): Missing docstring
class AnimationProperty(bpy.types.PropertyGroup):
    startFrame = bpy.props.IntProperty(name="Start frame", default=0)
    endFrame = bpy.props.IntProperty(name="End frame", default=100)

    startTime = bpy.props.FloatProperty(name="Start time", default=0.0)
    endTime = bpy.props.FloatProperty(name="End time", default=1.0)

    connNumber = bpy.props.IntProperty(name="Max Connection", default=0)

    showPercent = bpy.props.FloatProperty(name="Show percentage", default = 100.0, min = 0.0, max = 100.0, description = "Only generate x% of neurons", subtype = 'PERCENTAGE', precision = 1)

    layerCollection = bpy.props.CollectionProperty(type = LayerItem, name = "Layers")
    activeLayerIndex = bpy.props.IntProperty(name = "Active layer")

class UpdateAvailableLayers(bpy.types.Operator):
    bl_idname = "pam_anim.update_available_layers"
    bl_label = ""
    bl_description = "Update layers from model"

    @classmethod
    def poll(cls, context):
        return len(model.MODEL.ng_list) > 0

    def execute(self, context):
        item = context.scene.pam_anim_animation.layerCollection.clear()
        for index, ng in enumerate(model.NG_LIST):
            name = ng[0]
            item = context.scene.pam_anim_animation.layerCollection.add()
            item.layerName = name
            item.layerIndex = index
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)

# TODO(SK): Missing docstring
def register():
    bpy.utils.register_class(LayerItem)
    bpy.utils.register_class(AnimationProperty)
    bpy.types.Scene.pam_anim_animation = bpy.props.PointerProperty(type=AnimationProperty)


# TODO(SK): Missing docstring
def unregister():
    del bpy.types.Scene.pam_anim_animation
    bpy.utils.unregister_class(AnimationProperty)
