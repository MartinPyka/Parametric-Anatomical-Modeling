import bpy


def CreateLayer(object, sf, name):
    # creates a layer with a given shrink-fatten value and a name for materials and object data
    
    # selec the object to duplicate from
    bpy.ops.object.select_all(action='DESELECT')
    object.select = True
    bpy.context.scene.objects.active = object

    # create duplicate
    bpy.ops.object.duplicate()
    
    # reconfigure it
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.transform.shrink_fatten(value=sf, mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
    bpy.ops.object.editmode_toggle()
    
    # rename it and assign material
    bpy.context.object.data.name = name
    bpy.context.object.name = name
    # bpy.context.object.active_material = bpy.data.materials[name]
    

if __name__ == "__main__":
    sf_value = 0.1   # shrink-fatten value 
    #object = bpy.data.objects['CA3_sp']
    #CreateLayer(object, sf_value, 'CA3_so')
    #CreateLayer(object, -sf_value, 'CA3_sr')
    #CreateLayer(object, -2*sf_value, 'CA3_slm')
    #
    #object = bpy.data.objects['CA1_sp']
    #CreateLayer(object, sf_value, 'CA1_so')
    #CreateLayer(object, -sf_value, 'CA1_sr')
    #CreateLayer(object, -2*sf_value, 'CA1_slm')
    #
    #object = bpy.data.objects['DG_sg']
    #CreateLayer(object, sf_value, 'DG_mo')
    #CreateLayer(object, -sf_value, 'DG_po')

    object = bpy.data.objects['EC_6']
    CreateLayer(object, -sf_value, 'EC_5')
    CreateLayer(object, -2*sf_value, 'EC_4')
    CreateLayer(object, -3*sf_value, 'EC_3')
    CreateLayer(object, -4*sf_value, 'EC_2')

    object = bpy.data.objects['Per_6']
    CreateLayer(object, -sf_value, 'Per_5')
    CreateLayer(object, -2*sf_value, 'Per_4')
    CreateLayer(object, -3*sf_value, 'Per_3')
    CreateLayer(object, -4*sf_value, 'Per_2')