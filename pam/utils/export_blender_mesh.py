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

    pymesh = []

    if uv_layer is None:
        print("Warning:", obj, "has no active uv map")
        for face_index, face in enumerate(mesh.faces):
            poly = []
            for i, (loop, vert) in enumerate(zip(face.loops, face.verts)):
                poly.append((vert.co[0], vert.co[1], vert.co[2], 0, 0))
            pymesh.append(poly)
    else:
        for face_index, face in enumerate(mesh.faces):
            poly = []
            for i, (loop, vert) in enumerate(zip(face.loops, face.verts)):
                poly.append((vert.co[0], vert.co[1], vert.co[2], loop[uv_layer].uv[0], loop[uv_layer].uv[1]))
            pymesh.append(poly)
    
    return pymesh

def writeMesh(pymesh, path):
    with open(path, mode = 'w') as f:
        for i, polygon in enumerate(pymesh):
            f.write(str(i) + ':\n')
            for co in polygon:
                f.write(','.join([str(i) for i in co]))
                f.write('\n')

def writeParticles(particles, path):
    with open(path, 'w') as f:
        for particle in particles:
            co = particle.location.to_tuple()
            f.write(','.join([str(x) for x in co]) + '\n')


if __name__ == "__main__":
    writeMesh(export_object(bpy.context.active_object), bpy.path.abspath('//' + bpy.context.active_object.name + '.m'))