import bpy

import math
import heapq
import numpy

from .. import pam_vis
from .. import model
from . import data
from . import anim_spikes
from .helper import *

# CONSTANTS
TAU = 20
CURVES = {}
SPIKE_OBJECTS = []
DEFAULT_MAT_NAME = "SpikeMaterial"

# Group names
PATHS_GROUP_NAME = "PATHS"
SPIKE_GROUP_NAME = "SPIKES"


def clearVisualization():
        anim_spikes.deleteNeurons()
        if SPIKE_GROUP_NAME in bpy.data.groups:
                neuronObjects = bpy.data.groups[SPIKE_GROUP_NAME].objects
                for obj in neuronObjects:
                        bpy.context.scene.objects.unlink(obj)
                        bpy.data.objects.remove(obj)

        if PATHS_GROUP_NAME in bpy.data.groups:
                paths = bpy.data.groups[PATHS_GROUP_NAME].objects
                for curve in paths:
                        bpy.context.scene.objects.unlink(curve)
                        data = curve.data
                        bpy.data.objects.remove(curve)
                        bpy.data.curves.remove(data)

        pam_vis.vis_objects = 0

        global CURVES
        global SPIKE_OBJECTS
        CURVES = {}
        SPIKE_OBJECTS = []


def followCurve(curve, startTime, color, meshData):
        op = bpy.context.scene.pam_anim_orientation

        obj = bpy.data.objects.new("Spike", meshData)
        obj.color = color
        bpy.context.scene.objects.link(obj)

        constraint = obj.constraints.new(type="FOLLOW_PATH")
        constraint.offset = startTime / curve.data["timeLength"] * 100
        constraint.target = curve

        startFrame = int(startTime)

        obj.hide = True
        obj.keyframe_insert(data_path="hide", frame=startFrame - 2)
        obj.hide = False
        obj.keyframe_insert(data_path="hide", frame=startFrame - 1)
        obj.hide = True
        obj.keyframe_insert(data_path="hide", frame=math.ceil(startFrame + curve.data["timeLength"]))

        obj.hide_render = True
        obj.keyframe_insert(data_path="hide_render", frame=startFrame - 2)
        obj.hide_render = False
        obj.keyframe_insert(data_path="hide_render", frame=startFrame - 1)
        obj.hide_render = True
        obj.keyframe_insert(data_path="hide_render", frame=math.ceil(startFrame + curve.data["timeLength"]))

        if(op.orientationType == 'FOLLOW'):
                constraint.use_curve_follow = True

        if(op.orientationType == 'OBJECT'):
                # For eventual camera tracking
                camConstraint = obj.constraints.new(type="TRACK_TO")
                camConstraint.target = bpy.data.objects[op.orientationObject]
                camConstraint.track_axis = "TRACK_Z"
                camConstraint.up_axis = "UP_Y"

        return obj


def setAnimationSpeed(curve, animationSpeed):
        curve.eval_time = 0
        curve.keyframe_insert(data_path="eval_time", frame=0)
        curve.eval_time = 100
        curve.keyframe_insert(data_path="eval_time", frame=int(animationSpeed))

        # Set all the keyframes to linear interpolation to ensure a constant speed along the curve
        for key in curve.animation_data.action.fcurves[0].keyframe_points:
                key.interpolation = 'LINEAR'
        # Set the extrapolation of the curve to linear (This is important, without it, neurons with an offset start would not be animated)
        curve.animation_data.action.fcurves[0].extrapolation = 'LINEAR'


def mixLayerValues(layerValue1, layerValue2):
        newValues = {}
        for key in layerValue1:
                if key in layerValue2:
                        newValues[key] = layerValue1[key] + layerValue2[key]
                else:
                        newValues[key] = layerValue1[key]

        for key in layerValue2:
                if key not in layerValue1:
                        newValues[key] = layerValue2[key]

        return newValues


def calculateDecay(layerValues, delta, decayFunc):
        newValues = {}
        for key in layerValues:
                newValues[key] = decayFunc(layerValues[key], delta)
                if newValues[key] < 0:
                        newValues[key] = 0
        return newValues


def decay(value, delta):
        return value * numpy.exp(-delta / TAU)


def getInitialColorValues(neuronGroupID, neuronID):
        ng = data.NEURON_GROUPS[neuronGroupID]

        layerValue = {}
        if neuronID % 2 == 0:
                layerValue["blue"] = 1.0
        else:
                layerValue["red"] = 1.0
        return layerValue


def applyColorValues(obj, layerValues, neuronID, neuronGroupID):
        # Calculate the sum of all values
        col1 = (1.0, 0.1, 0.1)
        col2 = (0.5, 0.6, 0.8)

        if "blue" in layerValues:
                red = col1[0]
                green = col1[1]
                blue = col1[2]
        else:
                red = (0.9 * col1[0] - 0.1 * col2[0])
                green = (0.9 * col1[1] - 0.1 * col2[1])
                blue = (0.9 * col1[2] - 0.1 * col2[2])

                # Prevent black spikes. Do not use random numbers here since
                # spikes of the same type would be colored differently
                if red < 0.1 and green < 0.1 and blue < 0.1:
                        red += (col1[0] * 0.7)
                        green += (col1[1] * 0.5)
                        blue += (col1[2] * 0.4)

        obj.color = (red, blue, green, 1.0)


def createDefaultMaterial():
        options = bpy.context.scene.pam_anim_material
        if options.material != "DEFAULT_MAT_NAME":
                mat = bpy.data.materials.new("DEFAULT_MAT_NAME")
                mat.diffuse_color = (1.0, 1.0, 1.0)
                mat.use_object_color = True
                options.material = mat.name


def visualize(decayFunc=decay, initialColorValuesFunc=getInitialColorValues,
              mixValuesFunc=mixLayerValues, applyColorFunc=applyColorValues):

        n = data.NEURON_GROUPS
        c = data.CONNECTIONS
        t = data.TIMINGS
        d = data.DELAYS

        # Dictionary for generated curves, so we don't need to generate them twice
        global CURVES

        neuronValues = {}
        neuronUpdateQueue = []

        for timing in t:
                neuronID = timing[0]
                neuronGroupID = timing[1]
                fireTime = timing[2]

                neuronGroup = n[neuronGroupID]

                # Update the color values of all neurons with queued updates
                poppedValues = getQueueValues(neuronUpdateQueue, fireTime)
                for elem in poppedValues:
                        updateTime = elem[0]
                        key = elem[1]
                        newLayerValues = elem[2]

                        # If the key already has values, we have to calculate the decay of the values and then mix them with the incoming values
                        if key in neuronValues:
                                oldLayerValues = neuronValues[key][0]
                                lastUpdateTime = neuronValues[key][1]

                                oldLayerValuesDecay = calculateDecay(oldLayerValues, updateTime - lastUpdateTime, decayFunc)
                                updatedLayerValues = mixValuesFunc(oldLayerValuesDecay, newLayerValues)

                                neuronValues[key] = (updatedLayerValues, updateTime)
                        # If not, we don't need to mix the colors together, as this would just darken the color
                        else:
                                neuronValues[key] = (newLayerValues, updateTime)

                if neuronID in neuronValues:
                        # Update this neuron
                        layerValues = neuronValues[neuronID][0]
                        lastUpdateTime = neuronValues[neuronID][1]
                        layerValuesDecay = calculateDecay(layerValues, fireTime - lastUpdateTime, decayFunc)

                        # Now that the neuron has fired, its values go back down to zero
                        del(neuronValues[neuronID])

                else:
                        layerValuesDecay = initialColorValuesFunc(neuronGroupID, neuronID)

                for connectionID in neuronGroup.connections:
                        for index, i in enumerate(c[connectionID[0]]["c"][neuronID]):
                                if (i == -1) | (d[connectionID[0]][neuronID][index] == 0):
                                        continue
                                if (connectionID[0], neuronID, i) not in CURVES.keys():
                                        # If we do not have a curve already generated, we generate a new one with PAM and save it in our dictionary
                                        # print("Calling visualizeOneConnection with " + str(connectionID[0]) + ", " + str(neuronID)+ ", " + str(i))
                                        curve = CURVES[(connectionID[0], neuronID, i)] = pam_vis.visualizeOneConnection(connectionID[0], neuronID, i)

                                        # The generated curve needs the right animation speed, so we set the custom property and generate the animation
                                        curveLength = timeToFrames(d[connectionID[0]][neuronID][index])
                                        # print(curve)
                                        setAnimationSpeed(curve.data, curveLength)
                                        curve.data["timeLength"] = curveLength
                                else:
                                        curve = CURVES[(connectionID[0], neuronID, i)]
                                startFrame = projectTimeToFrames(fireTime)
                                obj = followCurve(curve, startFrame, (0.0, 0.0, 1.0, 1.0), bpy.data.meshes[bpy.context.scene.pam_anim_mesh.mesh])
                                SPIKE_OBJECTS.append(obj)

                                applyColorFunc(obj, layerValuesDecay, neuronID, neuronGroupID)

                                # Queue an update to the connected neuron
                                updateTime = fireTime + d[connectionID[0]][neuronID][index]
                                heapq.heappush(neuronUpdateQueue, (updateTime, i, layerValuesDecay))


# Operators:
class ClearPamAnimOperator(bpy.types.Operator):
        """ Clear Animation """
        bl_idname = "pam_anim.clear_pamanim"
        bl_label = "Clear Animation"
        bl_description = "Deletes the Spike-Animation"

        def execute(self, context):
                clearVisualization()
                return {'FINISHED'}

        def invoke(self, context, event):
                return self.execute(context)


class GenerateOperator(bpy.types.Operator):
        """Generate everything"""

        bl_idname = "pam_anim.generate"
        bl_label = "Generate"
        bl_description = "Generates the animation"

        @classmethod
        def poll(cls, context):

                # Check if a valid mesh has been selected
                if context.scene.pam_anim_mesh.mesh not in bpy.data.meshes:
                        return False

                # Check if a model is loaded into pam
                if not model.NG_LIST:
                        return False

                # Return True if all data is accessible
                return True

        def execute(self, context):
                data.NEURON_GROUPS = []
                data.CONNECTIONS = []
                data.DELAYS = []
                data.TIMINGS = []

                # Clear old objects if available
                clearVisualization()

                # Read data from files
                data.readModelData(bpy.context.scene.pam_anim_data.modelData)
                data.readSimulationData(bpy.context.scene.pam_anim_data.simulationData)

                # Create a default material if needed
                if bpy.context.scene.pam_anim_material.materialOption == "DEFAULT":
                        createDefaultMaterial()

                # Prepare functions
                decayFunc = decay
                getInitialColorValuesFunc = getInitialColorValues
                mixLayerValuesFunc = mixLayerValues
                applyColorValuesFunc = applyColorValues

                # Load any scripts
                script = bpy.context.scene.pam_anim_material.script
                if script in bpy.data.texts:
                        localFuncs = {}
                        exec(bpy.data.texts[script].as_string(), localFuncs)
                        if "decay" in localFuncs:
                                decayFunc = localFuncs['decay']
                        if "getInitialColorValues" in localFuncs:
                                getInitialColorValuesFunc = localFuncs['getInitialColorValues']
                        if "mixLayerValues" in localFuncs:
                                mixLayerValuesFunc = localFuncs['mixLayerValues']
                        if "applyColorValues" in localFuncs:
                                applyColorValuesFunc = localFuncs['applyColorValues']

                # Create the visualization
                visualize(decayFunc, getInitialColorValuesFunc, mixLayerValuesFunc, applyColorValuesFunc)

                # Create groups if they do not already exist
                if PATHS_GROUP_NAME not in bpy.data.groups:
                        bpy.data.groups.new(PATHS_GROUP_NAME)
                if SPIKE_GROUP_NAME not in bpy.data.groups:
                        bpy.data.groups.new(SPIKE_GROUP_NAME)

                # Insert objects into groups
                addObjectsToGroup(bpy.data.groups[PATHS_GROUP_NAME], CURVES)
                addObjectsToGroup(bpy.data.groups[SPIKE_GROUP_NAME], SPIKE_OBJECTS)

                # Apply material to mesh
                mesh = bpy.data.meshes[bpy.context.scene.pam_anim_mesh.mesh]
                mesh.materials.clear()
                mesh.materials.append(bpy.data.materials[bpy.context.scene.pam_anim_material.material])

                # Animate spiking if option is selected
                if bpy.context.scene.pam_anim_mesh.animSpikes is True:
                        for ng in data.NEURON_GROUPS:
                                anim_spikes.generateLayerNeurons(bpy.data.objects[ng.name], ng.particle_system)
                        anim_spikes.animNeuronSpiking(anim_spikes.animNeuronScaling)

                return {'FINISHED'}

        def invoke(self, context, event):

                return self.execute(context)


def register():
        # Custom property for the length of a curve for easy accessibility
        bpy.types.Curve.timeLength = bpy.props.FloatProperty()
        bpy.utils.register_class(GenerateOperator)
        bpy.utils.register_class(ClearPamAnimOperator)


def unregister():
        bpy.utils.unregister_class(GenerateOperator)
        bpy.utils.unregister_class(ClearPamAnimOperator)
