import bpy
import heapq


def projectTimeToFrames(t):
    op = bpy.context.scene.pam_anim_animation
    # Projection algorithm
    frame = (t - op.startTime) / (op.endTime - op.startTime) * (op.endFrame - op.startFrame) + op.startFrame
    return frame


def timeToFrames(t):
    op = bpy.context.scene.pam_anim_animation
    return t * (op.endFrame - op.startFrame) / (op.endTime - op.startTime)


def addObjectsToGroup(group, elements):
    if type(elements) is dict:
        elements = elements.values()
    for e in elements:
        group.objects.link(e)


def getQueueValues(queue, t):
    elementsBelowThreshold = []
    while queue and queue[0][0] <= t:
        elementsBelowThreshold.append(heapq.heappop(queue))
    return elementsBelowThreshold
