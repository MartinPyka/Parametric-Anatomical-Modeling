import mstree
import mst_blender
import numpy as np
import bpy
import mathutils
from pam import pam

def create_uv_tree(obj, quantity, uv_center, mean = [0.0, 0.0], variance = [0.005, 0.005], balancing_factor = 0.0, build_type = 'CURVE'):

    # Generate scattered points
    x = [uv_center[0]]
    y = [uv_center[1]]
    x = np.concatenate((x, np.random.normal(uv_center[0], variance[0], quantity) + mean[0]))
    y = np.concatenate((y, np.random.normal(uv_center[1], variance[1], quantity) + mean[1]))

    points = np.dstack((x, y))
    print(points)
    np.clip(points, 0., 1., out = points)
    # all items are stored in the first list-item of the output
    points = points[0]
    
    # Run mstree
    root_point = mstree.mstree(points, balancing_factor)

    # Convert node positions from uv to 3d
    nodes = mstree.tree_to_list(root_point)
    node_uv_points = [mathutils.Vector((node.pos[0], node.pos[1])) for node in nodes]
    print(len(node_uv_points))

    node_3d_points = pam.mapUVPointTo3d(obj, node_uv_points)
    print(len(node_3d_points))

    for i, node in enumerate(nodes):
        node.pos = node_3d_points[i]

    if build_type == 'CURVE':
        curve_obj = mst_blender.buildTreeCurve(root_point)
        curve_obj.data.bevel_depth = 0.001
    elif build_type == 'MESH':
        mesh_obj = mst_blender.buildTreeMesh(root_point)

def export_swc(root_node, outfilename, structure_identifier = 2):
    nodes = mstree.tree_to_list(root_node)
    f = open(outfilename, 'w')
    index = 0
    for node in nodes:
        node.index = index
        index += 1

        if node.parent is not None:
            parent_index = node.parent.index
        else:
            parent_index = -1

        f.write(' '.join((str(node.index), str(structure_identifier), str(node.pos[0]), str(node.pos[1]), str(node.pos[2]), str(0), str(parent_index))))
        f.write('\n')
    f.close()
    
def createAxons(p_obj, s_obj, quantity, mean, variance):
    for p in p_obj.particle_systems[0].particles:
        uv = pam.map3dPointToUV(p_obj, s_obj, p.location)
        create_uv_tree(s_obj, quantity, uv, mean, variance)

#if __name__ == '__main__':
#create_uv_tree(bpy.data.objects['CA3_sp_axons_all'], 100, (0.3, 0.5), [-0.1, 0.], [0.02, 0.005])
ca3 = bpy.data.objects['CA3_sp']
ca3_s = bpy.data.objects['CA3_sp_axons_all']
createAxons(ca3, ca3_s, 100, [-0.1, 0.0], [0.02, 0.005])