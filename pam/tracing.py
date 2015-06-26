import bpy
import numpy

from . import pam
from . import pam_vis
from . import model

MAX_FACTOR = 5
MAX_STEP_SIZE = 1

def getNeuralObjects():
    '''returns all objects that are used in PAM connections and have a particle system
    '''
    neuralObjects = []
    for (i, c) in enumerate(model.CONNECTIONS):  #go through all connections defined in pam
        for (ii, cc) in enumerate(c[0]):         #look at all objects used in the connection
            if len(cc.particle_systems):          #check if there are neurons in the object (if not, it is an intermediate or synapse layer)
                if cc not in neuralObjects:      #check if object is not already in the list
                    neuralObjects.append(cc)     #append found object to list and continue
    return neuralObjects

def getObjectColor(obj, force_color=None):
    '''returns material color if there is a material set, otherwise returns object color
       if force_color is set, that color is returned instead (then this function does just a conversion)
       list conversion is done because diffuse-color and object-color are different format
'''
    if force_color:
        return [force_color[0], force_color[1], force_color[2], 1.0]
    if not obj.active_material:
        col = obj.color
        return [col[0], col[1], col[2], col[3]]
    if obj.active_material.use_object_color:
        col = obj.color
        return [col[0], col[1], col[2], col[3]]
    col = obj.active_material.diffuse_color
    return [col[0], col[1], col[2], 1.0]

def getInjectionSiteNeurons(obj_list, location, radius):
    '''returns a list containing all particles affected by an injection in [location] with a given [radius]
       [obj_list] is a list of objects (not object names) that shall be taken into account
       return value is a list of lists, one inner list for each object given, containing particle numbers for the respective object
    '''

    neuronsPerObject = [ ]
    
    for (i, o) in enumerate(obj_list):
        templist=[]                           #for each object make a temporary list
        for (ii, p) in enumerate(o.particle_systems[0].particles):      #iterate through the object's neurons
            if (p.location - location).length < radius:                #if neuron is less than [radius] away from location
                templist.append(ii)                                    #then add neuron to list
        neuronsPerObject.append(templist)                       #when all neurons of an object are processed, add templist to return list
    return neuronsPerObject

def visualizeNeuronsColor(neural_objects, inj_neurons, inj_color=None):
    '''Visualizes all neurons given by list as returned by getInjectionSiteNeurons.
    The color is either the color of the objet the neuron is contained in or [inj_color], if specified
'''
    if not 'color_mat' in bpy.data.materials:       
        bpy.data.materials.new('color_mat')       #make material if not already exists
    mat = bpy.data.materials['color_mat']
    mat.use_object_color = True                   #set it to use object color (otherwise several materials were neccessary)
    #print(inj_neurons)
    for (ind_obj, neuron_list) in enumerate(inj_neurons):     #iterate through neuron lists (one for each object)
        neural_obj = neural_objects[ind_obj]                  #get corresponding object
        obj_col = getObjectColor(neural_obj, inj_color)
        for ne in neuron_list:                                #iterate through object's neurons
            pam_vis.visualizePoint(neural_obj.particle_systems[0].particles[ne].location)  #visualize neuron and color it in
            obj = bpy.context.selected_objects[0]
            obj.active_material = mat
            obj.color = obj_col

def visualizeNeuronsHitCount(hit_count_list, neural_objects):
    '''Visualizes neurons from a hit count list containing a neuron list for each object.
       Each neuron list contains the number of connections for each neuron
       The larger the connection number the bigger the drawn sphere
'''
    max_hit = max(max(hit_count_list))
    steps = max_hit-1
    range_h = MAX_FACTOR-1
    stepsize = min(range_h/steps,MAX_STEP_SIZE)
    for (obj_ind, hit_counts) in enumerate(hit_count_list):    #iterate through list
        post_obj = neural_objects[obj_ind]                     #and get object
        for (post_number, hit_count) in enumerate(hit_counts):              #for each object, iterate through neuron hit count list
            if hit_count:                                              #if 0 hits do nothing
                pam_vis.visualizePoint(post_obj.particle_systems[0].particles[post_number].location)
                resize_factor = 1+(hit_count-1)*stepsize
                bpy.ops.transform.resize(value=(numpy.sqrt(resize_factor), numpy.sqrt(resize_factor), numpy.sqrt(resize_factor))) #resize neuron according to hit count
                obj_col = getObjectColor(post_obj)
                obj = bpy.context.selected_objects[0]
                mat = bpy.data.materials['color_mat']
                obj.active_material = mat
                obj.color = obj_col


def anterograde_tracing(location, radius, inj_color=None):
    '''performs anterograde tracing at injection site with defined [radius] around given [location]
'''
    neural_objects = getNeuralObjects()
    inj_neurons = getInjectionSiteNeurons(neural_objects, location, radius)
    visualizeNeuronsColor(neural_objects, inj_neurons, inj_color)        #visualize injection site neurons

    #PREDEFINE HIT_COUNT_LIST: Number of afferent connections from injection site for each neuron
    hit_count_list = []
    for o in neural_objects:
        hit_count_list.append([0]*o.particle_systems[0].settings.count)   #hit_count_list: 1 list for each object, containing a 0 for each neuron

    #CALCULATE HIT_COUNT_LIST
    for (i, pre_obj) in enumerate(neural_objects):        #iterate through pre objects
        pre_list = inj_neurons[i]
        #print(pre_list)
        for (i_c, conn_def) in enumerate(model.CONNECTIONS):     #iterate through all connection definitions in the model
            #print(conn_def[0])
            if pre_obj == conn_def[0][0]:                        #and continue for those starting with the current pre_object
                post_obj = conn_def[0][-1]                     #get post_object
                post_obj_ind = neural_objects.index(post_obj)  #and its index in neural_objects list
                c = model.CONNECTION_RESULTS[i_c]['c']      #get list containing post_neuron list for each pre_neuron
                for pre_number in pre_list:                      #iterating through injection neurons of current pre_object
                    post_list = c[pre_number]               #get post_neurons for pre_neuron
                    for post_number in post_list:                #iterating through post_neurons
                        hit_count_list[post_obj_ind][post_number] += 1
    #print(hit_count_list)
                
    #VISUALIZE LABELLED NEURONS
    visualizeNeuronsHitCount(hit_count_list, neural_objects)

def retrograde_tracing(location, radius, inj_color=None):
    '''performs retrograde tracing at injection site with defined [radius] around given [location]
'''
    neural_objects = getNeuralObjects()
    inj_neurons = getInjectionSiteNeurons(neural_objects, location, radius)
    visualizeNeuronsColor(neural_objects, inj_neurons, inj_color)        #visualize injection site neurons

    #PREDEFINE HIT_COUNT_LIST: Number of efferent connections to injection site for each neuron
    hit_count_list = []
    for o in neural_objects:
        hit_count_list.append([0]*o.particle_systems[0].settings.count)   #hit_count_list: 1 list for each object, containing a 0 for each neuron

    #CALCULATE HIT_COUNT_LIST
    for (i, post_obj) in enumerate(neural_objects):        #iterate through post objects
        inj_list = inj_neurons[i]
        #print(pre_list)
        for (i_c, conn_def) in enumerate(model.CONNECTIONS):     #iterate through all connection definitions in the model
            #print(conn_def[0])
            if post_obj == conn_def[0][-1]:                        #and continue for those ending with the current post_object
                pre_obj = conn_def[0][0]                     #get pre_object
                pre_obj_ind = neural_objects.index(pre_obj)  #and its index in neural_objects list
                c = model.CONNECTION_RESULTS[i_c]['c']      #get list containing post_neuron list for each pre_neuron
                for (pre_number, post_list) in enumerate(c):   #iterating through connection vectors. injection neurons are searched for in the post_lists
                    for inj_number in inj_list:                  #iterating through injection neurons of current post_object
                        hits = sum(post_list==inj_number)  #how many hits?
                        hit_count_list[pre_obj_ind][pre_number] += hits     #add the number of connections to hit count list

    #print(hit_count_list)
                
    #VISUALIZE LABELLED NEURONS
    visualizeNeuronsHitCount(hit_count_list, neural_objects)
