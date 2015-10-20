
import pickle
import numpy
import mesh

NG_LIST = []
NG_DICT = {}
CONNECTION_COUNTER = 0
CONNECTION_INDICES = []
CONNECTIONS = []
CONNECTION_RESULTS = []
CONNECTION_ERRORS = []

MESHES = {}

def loadModel(path):
    """Load model via pickle from given path

    :param str path: filepath

    """
    snapshot = pickle.load(open(path, "rb"))

    global NG_LIST
    global NG_DICT
    global CONNECTION_COUNTER
    global CONNECTION_INDICES
    global CONNECTIONS
    global CONNECTION_RESULTS
    NG_LIST = snapshot.NG_LIST
    NG_DICT = snapshot.NG_DICT
    CONNECTION_COUNTER = snapshot.CONNECTION_COUNTER
    CONNECTION_INDICES = snapshot.CONNECTION_INDICES
    CONNECTIONS = Pickle2Connection(snapshot.CONNECTIONS)
    CONNECTION_RESULTS = convertArray2Vector(snapshot.CONNECTION_RESULTS)
    CONNECTION_ERRORS = []

def loadMesh(path):
    with open(path, mode = 'r') as f:
        polygons = []
        active_poly = []
        for line in f:
            if line.strip() == "":
                continue
            if line.endswith(':') and polygons:
                polygons.append(active_poly)
                active_poly = []
                continue

            co = line.split(',')
            if len(co) != 5:
                raise Exception('Mesh invalid\n\t' + line)
            active_poly.append((float(co[0]), float(co[1]), float(co[2]), float(co[3]), float(co[4])))
        polygons.append(active_poly)
        global MESHES
        meshname = f.name.rsplit('.', 1)[0]
        MESHES[meshname] = Mesh(polygons, meshname)