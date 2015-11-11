import numpy
import json
import os

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
                if active_poly:
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

def loadAllMeshFiles(path):
    """Load all meshes in a given path"""
    for f in os.listdir(path):
        if f.endswith('.m'):
            print("Loading " + f)
            loadMesh(path + f)

def loadAllParticleFiles(path):
    """Loads all particle in a given path"""
    for f in os.listdir(path):
        if f.endswith('.p'):
            print("Loading " + f)
            loadParticles(path + f)

def test():
    loadModel('/home/herbers/Documents/dev/pam/hippocampus_rat/hippocampus_rat.json')
    loadAllMeshFiles('/home/herbers/Documents/dev/pam/hippocampus_rat/mesh/')
    loadAllParticleFiles('/home/herbers/Documents/dev/pam/hippocampus_rat/mesh/')
    print(NG_LIST)
    print(NG_DICT)
    print(CONNECTIONS)

if __name__ == "__main__":
    test()