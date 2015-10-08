import numpy
#import scipy.spatial.distance

class Mesh():

    def __init__(self, polygons):
        self.polygons = numpy.array(polygons)
        self.uv_quadtree = []
        self.octree = Octree.buildOctree(self.polygons)

    def findClosestPointOnMesh(self, point):
        # Find closest node
        nodes = self.octree.listNodes()
        p = numpy.array(point)
        closest_node = nodes[0]
        node_distance = scipy.spatial.distance.euclidean(p, nodes[0].center)
        for n in nodes:
            d = scipy.spatial.distance.euclidean(p, n.center)
            if d < node_distance:
                closest_node = n
                node_distance = d
        print(closest_node.center)

class Octree():
    """[INSERT DOCSTRING HERE]
    bounds: [-x, +x, -y, +y, -z, +z] 

    bot       top
    +---+---+ +---+---+
    | 2 | 3 | | 6 | 7 |
    +---+---+ +---+---+ ^
    | 0 | 1 | | 4 | 5 | y
    +---+---+ +---+---+ +-x->
    
    """
    def __init__(self, bounds, polygon_reference, parent = None, max_depth = 4):
        self.nodes = [None] * 8
        self.bounds = bounds
        self.polygons = []
        self.max_depth = max_depth
        self.parent = parent
        self.polygon_reference = polygon_reference
        self.center = numpy.array(((self.bounds[0] + self.bounds[1]) / 2,
                       (self.bounds[2] + self.bounds[3]) / 2,
                       (self.bounds[4] + self.bounds[5]) / 2))

    def addPolygon(self, polygon_index):
        if self.max_depth > 0:
            for i in range(8):
                sb = self._getSubtreeBounds(i)
                if polygonInBounds(self.polygon_reference[polygon_index][...,:3], sb):
                    if self.nodes[i] is None:
                        self.nodes[i] = Octree(sb, self.polygon_reference, self, self.max_depth - 1)
                    self.nodes[i].addPolygon(polygon_index)
                    return
        self.polygons.append(polygon_index)

    def getPolygonIndices(self, point):
        if not pointInBounds(point, self.bounds):
            return []
        else:
            result = list(self.polygons)
            for node in self.nodes:
                if node is not None:
                    result.extend(node.getPolygonIndices(point))
            return result

    def _getSubtreeBounds(self, index):
        b = self.bounds
        x = (b[0] + b[1]) / 2
        y = (b[2] + b[3]) / 2
        z = (b[4] + b[5]) / 2
        if index == 0:
            sb = [b[0], x, b[2], y, b[4], z]
        elif index == 1:
            sb = [x, b[1], b[2], y, b[4], z]
        elif index == 2:
            sb = [b[0], x, y, b[3], b[4], z]
        elif index == 3:
            sb = [x, b[1], y, b[3], b[4], z]
        elif index == 4:
            sb = [b[0], x, b[2], y, z, b[5]]
        elif index == 5:
            sb = [x, b[1], b[2], y, z, b[5]]
        elif index == 6:
            sb = [b[0], x, y, b[3], z, b[5]]
        elif index == 7:
            sb = [x, b[1], y, b[3], z, b[5]]
        else:
            raise ValueError("Only indices from [0..7] allowed")
        return sb

    def listNodes(self):
        l = [self]
        for node in self.nodes:
            if node is not None:
                l.extend(node.listNodes())
        return l

    @staticmethod
    def buildOctree(polygons):
        # Find bounds of all polygons
        b = [polygons[0][0][0], polygons[0][0][0], polygons[0][0][1], polygons[0][0][1], polygons[0][0][2], polygons[0][0][2]]
        for poly in polygons:
            for p in poly:
                b[0] = min(b[0], p[0])
                b[1] = max(b[1], p[0])
                b[2] = min(b[2], p[1])
                b[3] = max(b[3], p[1])
                b[4] = min(b[4], p[2])
                b[5] = max(b[5], p[2])

        octree = Octree(b, polygons)
        for poly_index in range(len(polygons)):
            octree.addPolygon(poly_index)
        return octree

def polygonInBounds(polygon, bounds):
    for p in polygon:
        if not pointInBounds(p, bounds):
            return False
    return True

def pointInBounds(point, bounds):
    if point[0] < bounds[0] \
    or point[0] > bounds[1] \
    or point[1] < bounds[2] \
    or point[1] > bounds[3] \
    or point[2] < bounds[4] \
    or point[2] > bounds[5]:
        return False
    return True

def closestPointOnTriangle(point, t1, t2, t3):
    # http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.104.4264&rep=rep1&type=pdf

    # Get Transformation
    mat = calculatePlaneTransformation(t1, t2, t3)

    # Apply to points
    p1 = numpy.reshape(numpy.append(t1, 1), (4,1))
    p2 = numpy.reshape(numpy.append(t2, 1), (4,1))
    p3 = numpy.reshape(numpy.append(t3, 1), (4,1))

    point_transform = numpy.reshape(numpy.append(point, 1), (4,1))

    p1 = (mat * p1)[1:3] # Should be 0,0,0 anyways
    p2 = (mat * p2)[1:3]
    p3 = (mat * p3)[1:3]

    print(p1, p2, p3, sep='\n')

    point_transform = mat * point_transform
    print(point_transform)
    plane_distance = point_transform[0]
    point_plane = point_transform[1:3]

    # Edge equation for edge 1
    print(edge_distance(point_plane, p1, p3))
    print(edge_distance(point_plane, p3, p2))
    print(edge_distance(point_plane, p2, p1))

def edge_distance(point, l1, l2):
    return (point[0] - l1[0]) * (l2[1] - l1[1]) - (point[1] - l2[0]) * (l2[0] - l1[0])

def calculatePlaneTransformation(t1, t2, t3):
    # Translation of p1 to origin
    translation_matrix = numpy.identity(4)
    translation_matrix[0][-1] = -t1[0]
    translation_matrix[1][-1] = -t1[1]
    translation_matrix[2][-1] = -t1[2]

    # Rotation of p2 to point to y-axis
    # http://math.stackexchange.com/questions/180418/calculate-rotation-matrix-to-align-vector-a-to-vector-b-in-3d
    a = (t2 - t1) / numpy.linalg.norm(t2 - t1)
    b = numpy.array((0,1,0))
    v = numpy.cross(a, b)
    v_len = numpy.linalg.norm(v)
    c = numpy.dot(a, b)
    vx = numpy.matrix([[0, -v[2], v[1]],[v[2], 0, -v[0]],[-v[1], v[0], 0]])
    r = numpy.identity(3) + vx + numpy.dot(vx,vx) * ((1-c)/(v_len**2))
    rotation_matrix = numpy.identity(4)
    rotation_matrix[0:3, 0:3] = r

    mat = numpy.dot(rotation_matrix, translation_matrix)

    # Bring p3 onto yz-plane by rotating along y-axis
    a = numpy.array([t3[0], t3[1], t3[2], 1]).reshape((4,1))
    a = numpy.hstack(numpy.dot(mat, a))
    a /= a[3]
    a[1] = 0
    a = a[0:3]
    a /= numpy.linalg.norm(a)
    b = numpy.array((0,0,1))
    v = numpy.cross(a, b)
    sin_t = numpy.linalg.norm(v)
    cos_t = numpy.dot(a, b)
    rot_y = numpy.matrix([[cos_t, 0, -sin_t, 0], [0, 1, 0, 0], [sin_t, 0, cos_t, 0], [0, 0, 0, 1]])
    mat = rot_y * mat
    return mat

if __name__ == "__main__":
    # Testing
    p = [[(1.1749176979064941, 4.809549331665039, 1.7694251537322998, 1.9868213740892315e-08, 0.6666667461395264), (1.1749176979064941, 2.809549331665039, 1.7694251537322998, 0.333333283662796, 0.6666667461395264), (-0.8250824213027954, 2.809549570083618, 1.7694251537322998, 0.3333333134651184, 1.0)], [(-0.8250822424888611, 4.809549331665039, 3.7694251537323, 0.666666567325592, 0.6666667461395264), (-0.8250826597213745, 2.8095498085021973, 3.7694251537323, 0.3333333432674408, 0.6666666865348816), (1.1749169826507568, 2.809548854827881, 3.7694251537323, 0.3333333134651184, 0.33333349227905273)], [(1.1749181747436523, 4.809548854827881, 3.7694251537323, 0.33333340287208557, 0.3333333134651184), (1.1749169826507568, 2.809548854827881, 3.7694251537323, 0.3333333134651184, 0.0), (1.1749176979064941, 2.809549331665039, 1.7694251537322998, 0.6666666269302368, 1.9868211964535476e-08)], [(1.1749169826507568, 2.809548854827881, 3.7694251537323, 0.0, 1.291433733285885e-07), (-0.8250826597213745, 2.8095498085021973, 3.7694251537323, 0.33333322405815125, 0.0), (-0.8250824213027954, 2.809549570083618, 1.7694251537322998, 0.3333333134651184, 0.33333325386047363)], [(-0.8250826597213745, 2.8095498085021973, 3.7694251537323, 0.6666667461395264, 0.3333333134651184), (-0.8250822424888611, 4.809549331665039, 3.7694251537323, 0.6666666865348816, 8.940695295223122e-08), (-0.8250819444656372, 4.809549808502197, 1.7694251537322998, 1.0, 0.0)], [(1.1749176979064941, 4.809549331665039, 1.7694251537322998, 0.333333283662796, 0.33333343267440796), (-0.8250819444656372, 4.809549808502197, 1.7694251537322998, 0.3333333134651184, 0.6666666269302368), (-0.8250822424888611, 4.809549331665039, 3.7694251537323, 2.9802320611338473e-08, 0.6666667461395264)], [(1.1434125900268555, -0.10950565338134766, 1.744723916053772, 0.333333283662796, 0.6666667461395264), (-0.8565876483917236, -0.10950541496276855, 1.744723916053772, 0.3333333134651184, 1.0), (-0.8565871715545654, 1.890494704246521, 1.744723916053772, 0.0, 1.0)], [(-0.8565874099731445, 1.8904943466186523, 3.7447237968444824, 0.666666567325592, 0.6666667461395264), (-0.8565878868103027, -0.10950517654418945, 3.7447237968444824, 0.3333333432674408, 0.6666666865348816), (1.1434118747711182, -0.10950613021850586, 3.7447237968444824, 0.3333333134651184, 0.33333349227905273)], [(1.1434130668640137, 1.8904938697814941, 3.7447237968444824, 0.33333340287208557, 0.3333333134651184), (1.1434118747711182, -0.10950613021850586, 3.7447237968444824, 0.3333333134651184, 0.0), (1.1434125900268555, -0.10950565338134766, 1.744723916053772, 0.6666666269302368, 1.9868211964535476e-08)], [(1.1434118747711182, -0.10950613021850586, 3.7447237968444824, 0.0, 1.291433733285885e-07), (-0.8565878868103027, -0.10950517654418945, 3.7447237968444824, 0.33333322405815125, 0.0), (-0.8565876483917236, -0.10950541496276855, 1.744723916053772, 0.3333333134651184, 0.33333325386047363)], [(-0.8565878868103027, -0.10950517654418945, 3.7447237968444824, 0.6666667461395264, 0.3333333134651184), (-0.8565874099731445, 1.8904943466186523, 3.7447237968444824, 0.6666666865348816, 8.940695295223122e-08), (-0.8565871715545654, 1.890494704246521, 1.744723916053772, 1.0, 0.0)], [(1.1434125900268555, 1.8904943466186523, 1.744723916053772, 0.333333283662796, 0.33333343267440796), (-0.8565871715545654, 1.890494704246521, 1.744723916053772, 0.3333333134651184, 0.6666666269302368), (-0.8565874099731445, 1.8904943466186523, 3.7447237968444824, 2.9802320611338473e-08, 0.6666667461395264)], [(1.1434125900268555, -0.10950565338134766, -0.4854733943939209, 0.333333283662796, 0.6666667461395264), (-0.8565876483917236, -0.10950541496276855, -0.4854733943939209, 0.3333333134651184, 1.0), (-0.8565871715545654, 1.890494704246521, -0.4854733943939209, 0.0, 1.0)], [(-0.8565874099731445, 1.8904943466186523, 1.5145264863967896, 0.666666567325592, 0.6666667461395264), (-0.8565878868103027, -0.10950517654418945, 1.5145264863967896, 0.3333333432674408, 0.6666666865348816), (1.1434118747711182, -0.10950613021850586, 1.5145264863967896, 0.3333333134651184, 0.33333349227905273)], [(1.1434130668640137, 1.8904938697814941, 1.5145264863967896, 0.33333340287208557, 0.3333333134651184), (1.1434118747711182, -0.10950613021850586, 1.5145264863967896, 0.3333333134651184, 0.0), (1.1434125900268555, -0.10950565338134766, -0.4854733943939209, 0.6666666269302368, 1.9868211964535476e-08)], [(1.1434118747711182, -0.10950613021850586, 1.5145264863967896, 0.0, 1.291433733285885e-07), (-0.8565878868103027, -0.10950517654418945, 1.5145264863967896, 0.33333322405815125, 0.0), (-0.8565876483917236, -0.10950541496276855, -0.4854733943939209, 0.3333333134651184, 0.33333325386047363)], [(-0.8565878868103027, -0.10950517654418945, 1.5145264863967896, 0.6666667461395264, 0.3333333134651184), (-0.8565874099731445, 1.8904943466186523, 1.5145264863967896, 0.6666666865348816, 8.940695295223122e-08), (-0.8565871715545654, 1.890494704246521, -0.4854733943939209, 1.0, 0.0)], [(1.1434125900268555, 1.8904943466186523, -0.4854733943939209, 0.333333283662796, 0.33333343267440796), (-0.8565871715545654, 1.890494704246521, -0.4854733943939209, 0.3333333134651184, 0.6666666269302368), (-0.8565874099731445, 1.8904943466186523, 1.5145264863967896, 2.9802320611338473e-08, 0.6666667461395264)], [(1.1434125900268555, 2.8110692501068115, -0.4854733943939209, 0.333333283662796, 0.6666667461395264), (-0.8565876483917236, 2.8110694885253906, -0.4854733943939209, 0.3333333134651184, 1.0), (-0.8565871715545654, 4.811069488525391, -0.4854733943939209, 0.0, 1.0)], [(1.1434130668640137, 4.811068534851074, 1.5145264863967896, 0.6666666269302368, 0.33333340287208557), (-0.8565874099731445, 4.811069488525391, 1.5145264863967896, 0.666666567325592, 0.6666667461395264), (-0.8565878868103027, 2.8110697269439697, 1.5145264863967896, 0.3333333432674408, 0.6666666865348816)], [(1.1434130668640137, 4.811068534851074, 1.5145264863967896, 0.33333340287208557, 0.3333333134651184), (1.1434118747711182, 2.8110687732696533, 1.5145264863967896, 0.3333333134651184, 0.0), (1.1434125900268555, 2.8110692501068115, -0.4854733943939209, 0.6666666269302368, 1.9868211964535476e-08)], [(1.1434118747711182, 2.8110687732696533, 1.5145264863967896, 0.0, 1.291433733285885e-07), (-0.8565878868103027, 2.8110697269439697, 1.5145264863967896, 0.33333322405815125, 0.0), (-0.8565876483917236, 2.8110694885253906, -0.4854733943939209, 0.3333333134651184, 0.33333325386047363)], [(-0.8565878868103027, 2.8110697269439697, 1.5145264863967896, 0.6666667461395264, 0.3333333134651184), (-0.8565874099731445, 4.811069488525391, 1.5145264863967896, 0.6666666865348816, 8.940695295223122e-08), (-0.8565871715545654, 4.811069488525391, -0.4854733943939209, 1.0, 0.0)], [(1.1434125900268555, 4.811069488525391, -0.4854733943939209, 0.333333283662796, 0.33333343267440796), (-0.8565871715545654, 4.811069488525391, -0.4854733943939209, 0.3333333134651184, 0.6666666269302368), (-0.8565874099731445, 4.811069488525391, 1.5145264863967896, 2.9802320611338473e-08, 0.6666667461395264)], [(3.6120681762695312, 2.8110692501068115, -0.4854733943939209, 0.333333283662796, 0.6666667461395264), (1.6120679378509521, 2.8110694885253906, -0.4854733943939209, 0.3333333134651184, 1.0), (1.6120684146881104, 4.811069488525391, -0.4854733943939209, 0.0, 1.0)], [(3.6120686531066895, 4.811068534851074, 1.5145264863967896, 0.6666666269302368, 0.33333340287208557), (1.6120681762695312, 4.811069488525391, 1.5145264863967896, 0.666666567325592, 0.6666667461395264), (1.612067699432373, 2.8110697269439697, 1.5145264863967896, 0.3333333432674408, 0.6666666865348816)], [(3.6120686531066895, 4.811068534851074, 1.5145264863967896, 0.33333340287208557, 0.3333333134651184), (3.612067461013794, 2.8110687732696533, 1.5145264863967896, 0.3333333134651184, 0.0), (3.6120681762695312, 2.8110692501068115, -0.4854733943939209, 0.6666666269302368, 1.9868211964535476e-08)], [(3.612067461013794, 2.8110687732696533, 1.5145264863967896, 0.0, 1.291433733285885e-07), (1.612067699432373, 2.8110697269439697, 1.5145264863967896, 0.33333322405815125, 0.0), (1.6120679378509521, 2.8110694885253906, -0.4854733943939209, 0.3333333134651184, 0.33333325386047363)], [(1.612067699432373, 2.8110697269439697, 1.5145264863967896, 0.6666667461395264, 0.3333333134651184), (1.6120681762695312, 4.811069488525391, 1.5145264863967896, 0.6666666865348816, 8.940695295223122e-08), (1.6120684146881104, 4.811069488525391, -0.4854733943939209, 1.0, 0.0)], [(3.6120681762695312, 4.811069488525391, -0.4854733943939209, 0.333333283662796, 0.33333343267440796), (1.6120684146881104, 4.811069488525391, -0.4854733943939209, 0.3333333134651184, 0.6666666269302368), (1.6120681762695312, 4.811069488525391, 1.5145264863967896, 2.9802320611338473e-08, 0.6666667461395264)], [(3.6120681762695312, -0.10272097587585449, -0.4854733943939209, 0.333333283662796, 0.6666667461395264), (1.6120679378509521, -0.10272073745727539, -0.4854733943939209, 0.3333333134651184, 1.0), (1.6120684146881104, 1.8972793817520142, -0.4854733943939209, 0.0, 1.0)], [(1.6120681762695312, 1.8972790241241455, 1.5145264863967896, 0.666666567325592, 0.6666667461395264), (1.612067699432373, -0.10272049903869629, 1.5145264863967896, 0.3333333432674408, 0.6666666865348816), (3.612067461013794, -0.1027214527130127, 1.5145264863967896, 0.3333333134651184, 0.33333349227905273)], [(3.6120686531066895, 1.8972785472869873, 1.5145264863967896, 0.33333340287208557, 0.3333333134651184), (3.612067461013794, -0.1027214527130127, 1.5145264863967896, 0.3333333134651184, 0.0), (3.6120681762695312, -0.10272097587585449, -0.4854733943939209, 0.6666666269302368, 1.9868211964535476e-08)], [(3.612067461013794, -0.1027214527130127, 1.5145264863967896, 0.0, 1.291433733285885e-07), (1.612067699432373, -0.10272049903869629, 1.5145264863967896, 0.33333322405815125, 0.0), (1.6120679378509521, -0.10272073745727539, -0.4854733943939209, 0.3333333134651184, 0.33333325386047363)], [(1.612067699432373, -0.10272049903869629, 1.5145264863967896, 0.6666667461395264, 0.3333333134651184), (1.6120681762695312, 1.8972790241241455, 1.5145264863967896, 0.6666666865348816, 8.940695295223122e-08), (1.6120684146881104, 1.8972793817520142, -0.4854733943939209, 1.0, 0.0)], [(3.6120681762695312, 1.8972790241241455, -0.4854733943939209, 0.333333283662796, 0.33333343267440796), (1.6120684146881104, 1.8972793817520142, -0.4854733943939209, 0.3333333134651184, 0.6666666269302368), (1.6120681762695312, 1.8972790241241455, 1.5145264863967896, 2.9802320611338473e-08, 0.6666667461395264)], [(3.6120681762695312, -0.10272097587585449, 1.7943341732025146, 0.333333283662796, 0.6666667461395264), (1.6120679378509521, -0.10272073745727539, 1.7943341732025146, 0.3333333134651184, 1.0), (1.6120684146881104, 1.8972793817520142, 1.7943341732025146, 0.0, 1.0)], [(1.6120681762695312, 1.8972790241241455, 3.7943339347839355, 0.666666567325592, 0.6666667461395264), (1.612067699432373, -0.10272049903869629, 3.7943339347839355, 0.3333333432674408, 0.6666666865348816), (3.612067461013794, -0.1027214527130127, 3.7943339347839355, 0.3333333134651184, 0.33333349227905273)], [(3.6120686531066895, 1.8972785472869873, 3.7943339347839355, 0.33333340287208557, 0.3333333134651184), (3.612067461013794, -0.1027214527130127, 3.7943339347839355, 0.3333333134651184, 0.0), (3.6120681762695312, -0.10272097587585449, 1.7943341732025146, 0.6666666269302368, 1.9868211964535476e-08)], [(3.612067461013794, -0.1027214527130127, 3.7943339347839355, 0.0, 1.291433733285885e-07), (1.612067699432373, -0.10272049903869629, 3.7943339347839355, 0.33333322405815125, 0.0), (1.6120679378509521, -0.10272073745727539, 1.7943341732025146, 0.3333333134651184, 0.33333325386047363)], [(1.612067699432373, -0.10272049903869629, 3.7943339347839355, 0.6666667461395264, 0.3333333134651184), (1.6120681762695312, 1.8972790241241455, 3.7943339347839355, 0.6666666865348816, 8.940695295223122e-08), (1.6120684146881104, 1.8972793817520142, 1.7943341732025146, 1.0, 0.0)], [(3.6120681762695312, 1.8972790241241455, 1.7943341732025146, 0.333333283662796, 0.33333343267440796), (1.6120684146881104, 1.8972793817520142, 1.7943341732025146, 0.3333333134651184, 0.6666666269302368), (1.6120681762695312, 1.8972790241241455, 3.7943339347839355, 2.9802320611338473e-08, 0.6666667461395264)], [(-0.8250819444656372, 4.809549808502197, 1.7694251537322998, 0.0, 1.0), (1.1749176979064941, 4.809549331665039, 1.7694251537322998, 1.9868213740892315e-08, 0.6666667461395264), (-0.8250824213027954, 2.809549570083618, 1.7694251537322998, 0.3333333134651184, 1.0)], [(1.1749181747436523, 4.809548854827881, 3.7694251537323, 0.6666666269302368, 0.33333340287208557), (-0.8250822424888611, 4.809549331665039, 3.7694251537323, 0.666666567325592, 0.6666667461395264), (1.1749169826507568, 2.809548854827881, 3.7694251537323, 0.3333333134651184, 0.33333349227905273)], [(1.1749176979064941, 4.809549331665039, 1.7694251537322998, 0.6666666865348816, 0.333333283662796), (1.1749181747436523, 4.809548854827881, 3.7694251537323, 0.33333340287208557, 0.3333333134651184), (1.1749176979064941, 2.809549331665039, 1.7694251537322998, 0.6666666269302368, 1.9868211964535476e-08)], [(1.1749176979064941, 2.809549331665039, 1.7694251537322998, 2.9802320611338473e-08, 0.33333340287208557), (1.1749169826507568, 2.809548854827881, 3.7694251537323, 0.0, 1.291433733285885e-07), (-0.8250824213027954, 2.809549570083618, 1.7694251537322998, 0.3333333134651184, 0.33333325386047363)], [(-0.8250824213027954, 2.809549570083618, 1.7694251537322998, 1.0, 0.3333333134651184), (-0.8250826597213745, 2.8095498085021973, 3.7694251537323, 0.6666667461395264, 0.3333333134651184), (-0.8250819444656372, 4.809549808502197, 1.7694251537322998, 1.0, 0.0)], [(1.1749181747436523, 4.809548854827881, 3.7694251537323, 0.0, 0.33333340287208557), (1.1749176979064941, 4.809549331665039, 1.7694251537322998, 0.333333283662796, 0.33333343267440796), (-0.8250822424888611, 4.809549331665039, 3.7694251537323, 2.9802320611338473e-08, 0.6666667461395264)], [(1.1434125900268555, 1.8904943466186523, 1.744723916053772, 1.9868213740892315e-08, 0.6666667461395264), (1.1434125900268555, -0.10950565338134766, 1.744723916053772, 0.333333283662796, 0.6666667461395264), (-0.8565871715545654, 1.890494704246521, 1.744723916053772, 0.0, 1.0)], [(1.1434130668640137, 1.8904938697814941, 3.7447237968444824, 0.6666666269302368, 0.33333340287208557), (-0.8565874099731445, 1.8904943466186523, 3.7447237968444824, 0.666666567325592, 0.6666667461395264), (1.1434118747711182, -0.10950613021850586, 3.7447237968444824, 0.3333333134651184, 0.33333349227905273)], [(1.1434125900268555, 1.8904943466186523, 1.744723916053772, 0.6666666865348816, 0.333333283662796), (1.1434130668640137, 1.8904938697814941, 3.7447237968444824, 0.33333340287208557, 0.3333333134651184), (1.1434125900268555, -0.10950565338134766, 1.744723916053772, 0.6666666269302368, 1.9868211964535476e-08)], [(1.1434125900268555, -0.10950565338134766, 1.744723916053772, 2.9802320611338473e-08, 0.33333340287208557), (1.1434118747711182, -0.10950613021850586, 3.7447237968444824, 0.0, 1.291433733285885e-07), (-0.8565876483917236, -0.10950541496276855, 1.744723916053772, 0.3333333134651184, 0.33333325386047363)], [(-0.8565876483917236, -0.10950541496276855, 1.744723916053772, 1.0, 0.3333333134651184), (-0.8565878868103027, -0.10950517654418945, 3.7447237968444824, 0.6666667461395264, 0.3333333134651184), (-0.8565871715545654, 1.890494704246521, 1.744723916053772, 1.0, 0.0)], [(1.1434130668640137, 1.8904938697814941, 3.7447237968444824, 0.0, 0.33333340287208557), (1.1434125900268555, 1.8904943466186523, 1.744723916053772, 0.333333283662796, 0.33333343267440796), (-0.8565874099731445, 1.8904943466186523, 3.7447237968444824, 2.9802320611338473e-08, 0.6666667461395264)], [(1.1434125900268555, 1.8904943466186523, -0.4854733943939209, 1.9868213740892315e-08, 0.6666667461395264), (1.1434125900268555, -0.10950565338134766, -0.4854733943939209, 0.333333283662796, 0.6666667461395264), (-0.8565871715545654, 1.890494704246521, -0.4854733943939209, 0.0, 1.0)], [(1.1434130668640137, 1.8904938697814941, 1.5145264863967896, 0.6666666269302368, 0.33333340287208557), (-0.8565874099731445, 1.8904943466186523, 1.5145264863967896, 0.666666567325592, 0.6666667461395264), (1.1434118747711182, -0.10950613021850586, 1.5145264863967896, 0.3333333134651184, 0.33333349227905273)], [(1.1434125900268555, 1.8904943466186523, -0.4854733943939209, 0.6666666865348816, 0.333333283662796), (1.1434130668640137, 1.8904938697814941, 1.5145264863967896, 0.33333340287208557, 0.3333333134651184), (1.1434125900268555, -0.10950565338134766, -0.4854733943939209, 0.6666666269302368, 1.9868211964535476e-08)], [(1.1434125900268555, -0.10950565338134766, -0.4854733943939209, 2.9802320611338473e-08, 0.33333340287208557), (1.1434118747711182, -0.10950613021850586, 1.5145264863967896, 0.0, 1.291433733285885e-07), (-0.8565876483917236, -0.10950541496276855, -0.4854733943939209, 0.3333333134651184, 0.33333325386047363)], [(-0.8565876483917236, -0.10950541496276855, -0.4854733943939209, 1.0, 0.3333333134651184), (-0.8565878868103027, -0.10950517654418945, 1.5145264863967896, 0.6666667461395264, 0.3333333134651184), (-0.8565871715545654, 1.890494704246521, -0.4854733943939209, 1.0, 0.0)], [(1.1434130668640137, 1.8904938697814941, 1.5145264863967896, 0.0, 0.33333340287208557), (1.1434125900268555, 1.8904943466186523, -0.4854733943939209, 0.333333283662796, 0.33333343267440796), (-0.8565874099731445, 1.8904943466186523, 1.5145264863967896, 2.9802320611338473e-08, 0.6666667461395264)], [(1.1434125900268555, 4.811069488525391, -0.4854733943939209, 1.9868213740892315e-08, 0.6666667461395264), (1.1434125900268555, 2.8110692501068115, -0.4854733943939209, 0.333333283662796, 0.6666667461395264), (-0.8565871715545654, 4.811069488525391, -0.4854733943939209, 0.0, 1.0)], [(1.1434118747711182, 2.8110687732696533, 1.5145264863967896, 0.3333333134651184, 0.33333349227905273), (1.1434130668640137, 4.811068534851074, 1.5145264863967896, 0.6666666269302368, 0.33333340287208557), (-0.8565878868103027, 2.8110697269439697, 1.5145264863967896, 0.3333333432674408, 0.6666666865348816)], [(1.1434125900268555, 4.811069488525391, -0.4854733943939209, 0.6666666865348816, 0.333333283662796), (1.1434130668640137, 4.811068534851074, 1.5145264863967896, 0.33333340287208557, 0.3333333134651184), (1.1434125900268555, 2.8110692501068115, -0.4854733943939209, 0.6666666269302368, 1.9868211964535476e-08)], [(1.1434125900268555, 2.8110692501068115, -0.4854733943939209, 2.9802320611338473e-08, 0.33333340287208557), (1.1434118747711182, 2.8110687732696533, 1.5145264863967896, 0.0, 1.291433733285885e-07), (-0.8565876483917236, 2.8110694885253906, -0.4854733943939209, 0.3333333134651184, 0.33333325386047363)], [(-0.8565876483917236, 2.8110694885253906, -0.4854733943939209, 1.0, 0.3333333134651184), (-0.8565878868103027, 2.8110697269439697, 1.5145264863967896, 0.6666667461395264, 0.3333333134651184), (-0.8565871715545654, 4.811069488525391, -0.4854733943939209, 1.0, 0.0)], [(1.1434130668640137, 4.811068534851074, 1.5145264863967896, 0.0, 0.33333340287208557), (1.1434125900268555, 4.811069488525391, -0.4854733943939209, 0.333333283662796, 0.33333343267440796), (-0.8565874099731445, 4.811069488525391, 1.5145264863967896, 2.9802320611338473e-08, 0.6666667461395264)], [(3.6120681762695312, 4.811069488525391, -0.4854733943939209, 1.9868213740892315e-08, 0.6666667461395264), (3.6120681762695312, 2.8110692501068115, -0.4854733943939209, 0.333333283662796, 0.6666667461395264), (1.6120684146881104, 4.811069488525391, -0.4854733943939209, 0.0, 1.0)], [(3.612067461013794, 2.8110687732696533, 1.5145264863967896, 0.3333333134651184, 0.33333349227905273), (3.6120686531066895, 4.811068534851074, 1.5145264863967896, 0.6666666269302368, 0.33333340287208557), (1.612067699432373, 2.8110697269439697, 1.5145264863967896, 0.3333333432674408, 0.6666666865348816)], [(3.6120681762695312, 4.811069488525391, -0.4854733943939209, 0.6666666865348816, 0.333333283662796), (3.6120686531066895, 4.811068534851074, 1.5145264863967896, 0.33333340287208557, 0.3333333134651184), (3.6120681762695312, 2.8110692501068115, -0.4854733943939209, 0.6666666269302368, 1.9868211964535476e-08)], [(3.6120681762695312, 2.8110692501068115, -0.4854733943939209, 2.9802320611338473e-08, 0.33333340287208557), (3.612067461013794, 2.8110687732696533, 1.5145264863967896, 0.0, 1.291433733285885e-07), (1.6120679378509521, 2.8110694885253906, -0.4854733943939209, 0.3333333134651184, 0.33333325386047363)], [(1.6120679378509521, 2.8110694885253906, -0.4854733943939209, 1.0, 0.3333333134651184), (1.612067699432373, 2.8110697269439697, 1.5145264863967896, 0.6666667461395264, 0.3333333134651184), (1.6120684146881104, 4.811069488525391, -0.4854733943939209, 1.0, 0.0)], [(3.6120686531066895, 4.811068534851074, 1.5145264863967896, 0.0, 0.33333340287208557), (3.6120681762695312, 4.811069488525391, -0.4854733943939209, 0.333333283662796, 0.33333343267440796), (1.6120681762695312, 4.811069488525391, 1.5145264863967896, 2.9802320611338473e-08, 0.6666667461395264)], [(3.6120681762695312, 1.8972790241241455, -0.4854733943939209, 1.9868213740892315e-08, 0.6666667461395264), (3.6120681762695312, -0.10272097587585449, -0.4854733943939209, 0.333333283662796, 0.6666667461395264), (1.6120684146881104, 1.8972793817520142, -0.4854733943939209, 0.0, 1.0)], [(3.6120686531066895, 1.8972785472869873, 1.5145264863967896, 0.6666666269302368, 0.33333340287208557), (1.6120681762695312, 1.8972790241241455, 1.5145264863967896, 0.666666567325592, 0.6666667461395264), (3.612067461013794, -0.1027214527130127, 1.5145264863967896, 0.3333333134651184, 0.33333349227905273)], [(3.6120681762695312, 1.8972790241241455, -0.4854733943939209, 0.6666666865348816, 0.333333283662796), (3.6120686531066895, 1.8972785472869873, 1.5145264863967896, 0.33333340287208557, 0.3333333134651184), (3.6120681762695312, -0.10272097587585449, -0.4854733943939209, 0.6666666269302368, 1.9868211964535476e-08)], [(3.6120681762695312, -0.10272097587585449, -0.4854733943939209, 2.9802320611338473e-08, 0.33333340287208557), (3.612067461013794, -0.1027214527130127, 1.5145264863967896, 0.0, 1.291433733285885e-07), (1.6120679378509521, -0.10272073745727539, -0.4854733943939209, 0.3333333134651184, 0.33333325386047363)], [(1.6120679378509521, -0.10272073745727539, -0.4854733943939209, 1.0, 0.3333333134651184), (1.612067699432373, -0.10272049903869629, 1.5145264863967896, 0.6666667461395264, 0.3333333134651184), (1.6120684146881104, 1.8972793817520142, -0.4854733943939209, 1.0, 0.0)], [(3.6120686531066895, 1.8972785472869873, 1.5145264863967896, 0.0, 0.33333340287208557), (3.6120681762695312, 1.8972790241241455, -0.4854733943939209, 0.333333283662796, 0.33333343267440796), (1.6120681762695312, 1.8972790241241455, 1.5145264863967896, 2.9802320611338473e-08, 0.6666667461395264)], [(3.6120681762695312, 1.8972790241241455, 1.7943341732025146, 1.9868213740892315e-08, 0.6666667461395264), (3.6120681762695312, -0.10272097587585449, 1.7943341732025146, 0.333333283662796, 0.6666667461395264), (1.6120684146881104, 1.8972793817520142, 1.7943341732025146, 0.0, 1.0)], [(3.6120686531066895, 1.8972785472869873, 3.7943339347839355, 0.6666666269302368, 0.33333340287208557), (1.6120681762695312, 1.8972790241241455, 3.7943339347839355, 0.666666567325592, 0.6666667461395264), (3.612067461013794, -0.1027214527130127, 3.7943339347839355, 0.3333333134651184, 0.33333349227905273)], [(3.6120681762695312, 1.8972790241241455, 1.7943341732025146, 0.6666666865348816, 0.333333283662796), (3.6120686531066895, 1.8972785472869873, 3.7943339347839355, 0.33333340287208557, 0.3333333134651184), (3.6120681762695312, -0.10272097587585449, 1.7943341732025146, 0.6666666269302368, 1.9868211964535476e-08)], [(3.6120681762695312, -0.10272097587585449, 1.7943341732025146, 2.9802320611338473e-08, 0.33333340287208557), (3.612067461013794, -0.1027214527130127, 3.7943339347839355, 0.0, 1.291433733285885e-07), (1.6120679378509521, -0.10272073745727539, 1.7943341732025146, 0.3333333134651184, 0.33333325386047363)], [(1.6120679378509521, -0.10272073745727539, 1.7943341732025146, 1.0, 0.3333333134651184), (1.612067699432373, -0.10272049903869629, 3.7943339347839355, 0.6666667461395264, 0.3333333134651184), (1.6120684146881104, 1.8972793817520142, 1.7943341732025146, 1.0, 0.0)], [(3.6120686531066895, 1.8972785472869873, 3.7943339347839355, 0.0, 0.33333340287208557), (3.6120681762695312, 1.8972790241241455, 1.7943341732025146, 0.333333283662796, 0.33333343267440796), (1.6120681762695312, 1.8972790241241455, 3.7943339347839355, 2.9802320611338473e-08, 0.6666667461395264)]]
    m = Mesh(p)
    p1 = (2,2,3)
    p2 = numpy.array((3.208115816116333, 2.262561798095703, 2.304555892944336))
    p3 = numpy.array((2.2930221557617188, 0.4895104169845581, 4.062463760375977))
    # mat = calculatePlaneTransformation(p1, p2, p3)
    # a = numpy.dot(mat, numpy.array((p3[0], p3[1], p3[2], 1)).reshape(4,1))
    # a /= a[3]
    # print(mat, a, sep=('\n'))
    # m.findClosestPointOnMesh((-1,-1,-1))
    closestPointOnTriangle((1.8,0.2,1), p1, p2, p3)