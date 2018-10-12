import bpy
from . import preview_updater

class ClarityPreviewSettingsPanel(bpy.types.Panel): 
    bl_idname       = 'preview_settings_layout'
    # show only when the other PAM tools are shown
    bl_space_type   = 'VIEW_3D'
    bl_region_type  = 'TOOL_PROPS'
    bl_category     = 'PAM Neuron Extractor'
    bl_context      = 'objectmode'
    bl_label        = 'Preview Settings'
    
    def draw(self, context):
        layout = self.layout    
        
        if(context.scene.prev_type == "SLICED"):
            layout.prop(context.scene, "clarity_preview_slice_id")
			
			
        if(context.scene.prev_type == "LRVOLUME"):
            layout.prop(context.scene, "clarity_preview_transparency")
			
			
        if(context.scene.prev_type == "SUBVOLUME"):
            layout.prop(context.scene, "clarity_preview_transparency")
            layout.prop(context.scene, "clarity_preview_width_begin")
            layout.prop(context.scene, "clarity_preview_width_end")
            layout.prop(context.scene, "clarity_preview_height_begin")
            layout.prop(context.scene, "clarity_preview_height_end")
            layout.prop(context.scene, "clarity_preview_depth_begin")
            layout.prop(context.scene, "clarity_preview_depth_end")
		
        layout.operator("clarity_preview.update")
 


def register():    
    preview_updater.register( )

    bpy.types.Scene.clarity_preview_slice_id = bpy.props.IntProperty(name="Current Slice", min=0)
	
    bpy.types.Scene.clarity_preview_width_begin = bpy.props.IntProperty(name="Width begin", min=0)
    bpy.types.Scene.clarity_preview_width_end = bpy.props.IntProperty(name="Width End", min=0)
    bpy.types.Scene.clarity_preview_height_begin = bpy.props.IntProperty(name="Height Begin", min=0)
    bpy.types.Scene.clarity_preview_height_end = bpy.props.IntProperty(name="Height End", min=0)
    bpy.types.Scene.clarity_preview_depth_begin = bpy.props.IntProperty(name="Depth Begin", min=0)
    bpy.types.Scene.clarity_preview_depth_end = bpy.props.IntProperty(name="Depth End", min=0)
	
    bpy.types.Scene.clarity_preview_transparency = bpy.props.FloatProperty(name="Transparency", min=0.0, max=1.0)
	
    bpy.utils.register_class(ClarityPreviewSettingsPanel)
    

	

def unregister():
    bpy.utils.unregister_class(ClarityPreviewSettingsPanel)

    del bpy.types.Scene.clarity_preview_slice_id
    
    del bpy.types.Scene.clarity_preview_width_begin
    del bpy.types.Scene.clarity_preview_width_end
    del bpy.types.Scene.clarity_preview_height_begin
    del bpy.types.Scene.clarity_preview_height_end
    del bpy.types.Scene.clarity_preview_depth_begin
    del bpy.types.Scene.clarity_preview_depth_end

    del bpy.types.Scene.clarity_preview_transparency

    preview_updater.unregister( )
    