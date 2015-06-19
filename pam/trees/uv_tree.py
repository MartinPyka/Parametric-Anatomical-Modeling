import mstree
import mst_blender
import numpy as np
import bpy
import mathutils
from pam import pam

def create_uv_tree(obj, quantity, uv_center, variance = 0.005, balancing_factor = 0.0, build_type = 'MESH'):

    # Generate scattered points
    x = np.random.normal(uv_center[0], variance, quantity)
    y = np.random.normal(uv_center[1], variance, quantity)

    points = np.dstack((x, y))
    np.clip(points, 0., 1., out = points)

    # Run mstree
    root_point = mstree.mstree(points[0], balancing_factor)

    # Convert node positions from uv to 3d
    nodes = mstree.tree_to_list(root_point)
    # print(root_point.pos)
    node_uv_points = [mathutils.Vector((node.pos[0], node.pos[1])) for node in nodes]

    node_3d_points = pam.mapUVPointTo3d(obj, node_uv_points)

    for i, node in enumerate(nodes):
        node.pos = node_3d_points[i]

    if build_type == 'CURVE':
        curve_obj = mst_blender.buildTreeCurve(root_point)
        curve_obj.data.bevel_depth = 0.1
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

if __name__ == '__main__':
    create_uv_tree(bpy.data.objects['CA3_sp_axons_all'], 100, (0.1, 0.2))