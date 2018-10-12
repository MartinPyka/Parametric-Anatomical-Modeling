import bpy 


# This is the operator which bridges the communication between a possible cluster
# and blender to execute the algorithm.
class DetectionLauncher(bpy.types.Operator):
    bl_idname = "neuron_detector.launch"
    bl_label = "Launch"
    bl_description = "Launches the detection algorithm on a selected CLARITY file."
 
    def execute(self, context):
        #todo call launcher fuction
        return {'FINISHED'}
    
	
	
	
def register():
    bpy.utils.register_class(DetectionLauncher)
	
	
	
	
def unregister():
    bpy.utils.unregister_class(DetectionLauncher)