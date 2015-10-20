import bpy
import bmesh as bm
import numpy as np

def export_object(obj):
    mesh = bm.new()
    mesh.from_object(obj, bpy.context.scene, deform = True)
    mesh.transform(obj.matrix_world)

    # Triangulate because we only want tris
    bm.ops.triangulate(mesh, faces = mesh.faces)

    # Determine active uv-map
    uv_layer = mesh.loops.layers.uv.active
    if uv_layer is None:
        raise Exception("No active UV map (uv)")

    pymesh = []
    for face_index, face in enumerate(mesh.faces):
        poly = []
        for i, (loop, vert) in enumerate(zip(face.loops, face.verts)):
            poly.append((vert.co[0], vert.co[1], vert.co[2], loop[uv_layer].uv[0], loop[uv_layer].uv[1]))
        pymesh.append(poly)
    
    return pymesh

def write(pymesh, path):
    with open(path, mode = 'w') as f:
        for i, polygon in enumerate(pymesh):
            f.write(str(i) + ':\n')
            for co in polygon:
                f.write(','.join([str(i) for i in co]))
                f.write('\n')


if __name__ == "__main__":
    write(export_object(bpy.context.active_object), bpy.path.abspath('//' + bpy.context.active_object.name + '.m'))