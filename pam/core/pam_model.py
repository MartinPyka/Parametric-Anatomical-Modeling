import numpy
import json

import mesh

NG_LIST = []
NG_DICT = {}
CONNECTION_COUNTER = 0
CONNECTION_INDICES = []
CONNECTIONS = []
CONNECTION_RESULTS = []
CONNECTION_ERRORS = []

MESHES = {}
PARTICLES = {}

def loadModel(path):
    """Load model via pickle from given path

    :param str path: filepath

    """
    with open(path, 'r') as f:
        j = json.load(f)

    global NG_LIST
    global NG_DICT
    global CONNECTIONS
    NG_LIST = j[1]
    NG_DICT = j[2]
    CONNECTIONS = j[0]

def loadMesh(path):
    with open(path, mode = 'r') as f:
        polygons = []
        active_poly = []
        for line in f:
            if line.strip() == "":
                continue
            if line.strip().endswith(':'):
                if polygons:
                    polygons.append(active_poly)
                    active_poly = []
                continue

            co = line.split(',')
            if len(co) != 5:
                raise Exception('Mesh invalid\n\t' + line)
            active_poly.append((float(co[0]), float(co[1]), float(co[2]), float(co[3]), float(co[4])))
        polygons.append(active_poly)
        global MESHES
        meshname = f.name.rsplit('/', 1)[1].rsplit('.', 1)[0]
        MESHES[meshname] = mesh.Mesh(polygons, name = meshname)

def loadParticles(path):
    with open(path, mode = 'r') as f:
        particles = []
        for line in f:
            if line.strip() == "":
                continue
            co = line.split(',')
            co = (float(co[0]), float(co[1]), float(co[2]))
            particles.append(co)
        global PARTICLES
        name = f.name.rsplit('/', 1)[1].rsplit('.', 1)[0]
        PARTICLES[name] = particles

if __name__ == "__main__":
    loadModel('/home/herbers/Documents/dev/pam/hippocampus_rat/hippocampus_rat.json')
    loadMesh('/home/herbers/Documents/dev/pam/hippocampus_rat/DG_sg.m')
    loadParticles('/home/herbers/Documents/dev/pam/hippocampus_rat/DG_sg.p')
    print(NG_LIST)
    print(NG_DICT)
    print(CONNECTIONS)