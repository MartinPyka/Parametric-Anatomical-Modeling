import bpy


class ClarityFileSelectionPanel(bpy.types.Panel): 
    bl_idname       = 'clarity_file_seletion_layout'
    # show only when the other PAM tools are shown
    bl_space_type   = 'VIEW_3D'
    bl_region_type  = 'TOOLS'
    bl_category     = 'PAM Neuron Extractor'
    bl_context      = 'objectmode'
    bl_label        = 'CLARITY File Settings'

    def draw(self, context):
        # create a preview texture if not available
        try:
            bpy.data.textures['clarity_preview_image']
        except KeyError:
            # create clarity preview image
            bpy.data.textures.new(name = 'clarity_preview_image', type = 'IMAGE')        
        
        layout = self.layout
        layout.template_preview(bpy.data.textures['clarity_preview_image'])        
        layout.prop(context.scene,"clarity_file_in")
        layout.prop(context.scene,"clarity_file_out")
        layout.prop(context.scene,"prev_type")
		


# console access and path manipulation utils
import os.path
import sys


def prepare_clarity_file(self,context):
    wm = context.window_manager
    
    #@todo validate if this file exists and is a clarity file
    #@todo get preview data from file, if it exists
    
    #dummy variable to work with the "progress bars"
    steps = 10000
    
    #example progress bar on mouse
    """
    wm.progress_begin(0, steps)
    for i in range(steps):
        wm.progress_update(i)
    wm.progress_end()
    """
    
    #example progress bar in console
    """
    sys.stdout.write("Preparing clarity preview: ")
    for i in range(steps+1):
        msg = "Step %i of %i" % (i, steps)
        sys.stdout.write(msg)
        #chr(8) is a backspace character to move the cursor back in the console 
        sys.stdout.write(chr(8) * len(msg))
        sys.stdout.flush()
    print("DONE")
    """
     
    
    #@todo if not, generate preview data via opengl(bgl) or cycles: render a pointcloud into a texture via perspective projection
    """
    bpy.data.textures['clarity_preview'].image = ...
    """   
		
	
	
	
def register():
    bpy.types.Scene.clarity_file_in  = bpy.props.StringProperty(name="Clarity File", subtype="FILE_PATH", update=prepare_clarity_file)
    bpy.types.Scene.clarity_file_out = bpy.props.StringProperty(name="Output Directory", subtype="DIR_PATH")
    bpy.types.Scene.prev_type = bpy.props.EnumProperty( name="Preview type", items=[
    ("SLICED", "Sliced", "", 1),
    ("LRVOLUME", "Low-resolution volume", "", 2),
    ("SUBVOLUME", "Subvolume", "", 3),])
   
	
    bpy.utils.register_class(ClarityFileSelectionPanel)
	
	
	
	
def unregister():
    bpy.utils.unregister_class(ClarityFileSelectionPanel)
	
    del bpy.types.Scene.clarity_file_in
    del bpy.types.Scene.clarity_file_out
    del bpy.types.Scene.prev_type
	
    #@todo remove preview texture