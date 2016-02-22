import bpy 


class ClarityPreviewObserver(bpy.types.Operator):
    bl_idname = "clarity_preview.update"
    bl_label = "Update Preview"
    bl_description = "Re-render the preview with the new settings."
 
    def execute(self, context):
        #todo update the preview texture
        return {'FINISHED'}
    
	
	
	
def register():
    bpy.utils.register_class(ClarityPreviewObserver)
	
	
	
	
def unregister():
    bpy.utils.unregister_class(ClarityPreviewObserver)