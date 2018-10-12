import bpy 
from . import detection_launcher


class MetricSettingsPannel(bpy.types.Panel): 
    bl_idname       = 'clarity_metric_settings_layout'
    # show only when the other PAM tools are shown
    bl_space_type   = 'VIEW_3D'
    bl_region_type  = 'TOOLS'
    bl_category     = 'PAM Neuron Extractor'
    bl_context      = 'objectmode'
    bl_label        = 'Metric Settings'
    
    def draw(self, context):
        layout = self.layout   
        layout.prop(context.scene,"clarity_neuron_size")
    
	
	
	
def register():
    bpy.types.Scene.clarity_neuron_size = bpy.props.FloatProperty(name="Neuron Size")
	
    bpy.utils.register_class(MetricSettingsPannel)
	
	
	
	
def unregister():
    bpy.utils.unregister_class(MetricSettingsPannel)
	
    del bpy.types.Scene.clarity_neuron_size