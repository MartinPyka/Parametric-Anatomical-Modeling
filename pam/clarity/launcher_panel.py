import bpy 
from . import detection_launcher


class ClarityDetectorSettings(bpy.types.Panel): 
    bl_idname       = 'clarity_detector_settings_layout'
    # show only when the other PAM tools are shown
    bl_space_type   = 'VIEW_3D'
    bl_region_type  = 'TOOLS'
    bl_category     = 'PAM Neuron Extractor'
    bl_context      = 'objectmode'
    bl_label        = 'Detector Settings'

    def draw(self, context):
        layout = self.layout   
        layout.prop(context.scene,"clarity_thread_count")
        layout.prop(context.scene,"clarity_max_block_size")
        layout.operator("detector.launch")
		
		
		
		
def register( ):
    bpy.utils.register_class(ClarityDetectorSettings)
	
    bpy.types.Scene.clarity_thread_count = bpy.props.IntProperty(name="Thread Count")
    bpy.types.Scene.clarity_max_block_size = bpy.props.IntProperty(name="Max Block Size (MB)")
	
    detection_launcher.register( )


	

def unregister( ):
    bpy.utils.unregister_class(ClarityDetectorSettings)

    detection_launcher.unregister( )
	
    del bpy.types.Scene.clarity_thread_count
    del bpy.types.Scene.clarity_max_block_size