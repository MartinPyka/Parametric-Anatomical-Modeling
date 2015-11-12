import numpy

class Mesh():
    """Represents a collection of polygons"""
    def __init__(self, polygons, name = ''):
        """
        :param polygons: The polygons of the mesh. Can only be 3d triangles.
        :type polygons: List of polygons, which are a list of 3 points, which are a list of 5 floats (x, y, z, u, v)
        :param name: The name of the mesh as an identifier
        :type name: string
        """
        self.polygons = numpy.array(polygons)
        self.uv_quadtree = Quadtree.buildUVQuadtreeFromMesh(self.polygons)
        self.octree = Octree.buildOctree(self.polygons)
        self.polygon_transformation_cache = [None] * len(self.polygons)
        self.name = name

    def closest_point_on_mesh(self, point):
        """Finds the closest point to the given point on the mesh

        :param point: The point to which to find the closest point on the mesh
        :type point: List of 3 floats

        :return: (The closest point, The index of the polygon this point is on, The barycentric coordinates of the point on the face)
        :rtype: (array of 3 floats, int, list of 3 floats)"""
        # Find closest node
        nodes = self.octree.listNodes()
        p = numpy.array(point)
        closest_node = nodes[0]
        node_distance = distance_sqr(p, nodes[0].center)
        for n in nodes:
            d = distance_sqr(p, n.center)
            if d < node_distance:
                closest_node = n
                node_distance = d
        polygons = closest_node.getPolygonsUpwards()
        node_distance_extended = numpy.square(numpy.sqrt(node_distance) + numpy.sqrt(distance_sqr(numpy.array((closest_node.bounds[0], closest_node.bounds[2], closest_node.bounds[4])), closest_node.center)))
        poly_lookup = [False] * len(self.polygons)
        for n in nodes:
            if distance_sqr(p, n.center) < node_distance_extended:
                polys = n.getPolygonsUpwards()
                for poly in polys:
                    poly_lookup[poly] = True
        polygons = [i for i in range(len(self.polygons)) if poly_lookup[i]]
        closest_distance = numpy.inf
        closest_point = None
        closest_barycentric_coords = None
        for poly_index in polygons:
            triangle_point, barycentric_coords = self._cachedClosestPointOnTriangle(point, poly_index)
            d = distance_sqr(triangle_point, point)
            if d < closest_distance:
                closest_distance = d
                polygon_index = poly_index
                closest_point = triangle_point
                closest_barycentric_coords = barycentric_coords
        # print(len(polygons), '/', len(self.polygons), "polygons checked")
        return closest_point, polygon_index, closest_barycentric_coords

    def _cachedClosestPointOnTriangle(self, point, polygon_index):
        """Finds the closest point on a triangle in the mesh using cached transformation matrices

        :param point: The point
        :type point: List of 3 floats
        :param polygon_index: The index of the polygon/triangle in the mesh
        :type polygon_index: int

        :return: (The point on the triangle, the barycentric coordinates)
        :rtype: (float[3], float[3])
        """

        # http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.104.4264&rep=rep1&type=pdf

        t1 = self.polygons[polygon_index][0][:3]
        t2 = self.polygons[polygon_index][1][:3]
        t3 = self.polygons[polygon_index][2][:3]

        if self.polygon_transformation_cache[polygon_index] is not None:
            # Get Transformation if cached
            mat = self.polygon_transformation_cache[polygon_index]
        else:
            # Else generate new and cache it
            mat = calculatePlaneTransformation(t1, t2, t3)
            self.polygon_transformation_cache[polygon_index] = mat

        # Apply to points
        p1 = multiply_4d_matrix(mat, t1)[1:3]
        p2 = multiply_4d_matrix(mat, t2)[1:3]
        p3 = multiply_4d_matrix(mat, t3)[1:3]

        point_transform = multiply_4d_matrix(mat, point)
        plane_distance = point_transform[0]
        point_plane = point_transform[1:3]

        polygon_point = closestPointOnTriangle2d(point_plane, p1, p2, p3)
        l1, l2, l3 = toBarycentricCoordinates(polygon_point, p1, p2, p3)

        point_3d = fromBarycentricCoordinates(l1, l2, l3, t1, t2, t3)
        return point_3d, (l1, l2, l3)

    def raycast(self, origin, direction):
        """Finds a point on the mesh using a raycast

        :param origin: The origin vector of the ray
        :type origin: List of 3 floats
        :param direction: The driection of the ray
        :type direction: List of 3 floats

        :return: (The point of closest intersection, The index of the hit polygon, The distance from origin to hit, The barycentric coordinates on the hit triangle)
        :rtype: (float[3], int, float, float[3])"""
        # TODO octree optimization, only check polys that are inside hit cubes
        closest_poly_index = None
        closest_distance_sqr = numpy.inf
        closest_intersection = None
        closest_barycentric_coords = None
        for i, poly in enumerate(self.polygons):
            intersection = intersectRayTri(origin, direction, poly[0][:3], poly[1][:3], poly[2][:3])
            if intersection is not None:
                d = distance_sqr(intersection[0], origin)
                if d < closest_distance_sqr:
                    closest_distance_sqr = d
                    closest_poly_index = i
                    closest_intersection = intersection[0]
                    closest_barycentric_coords = intersection[1]
        return closest_intersection, closest_poly_index, numpy.sqrt(closest_distance_sqr), closest_barycentric_coords

    def getNormalFromFaceIndex(self, faceIndex):
        """Gives the normal of a face within the mesh

        :param faceIndex: The index of the face in the mesh
        :type faceIndex: int

        :return: The normal vector of the face
        :rtype: float[3]"""
        poly = self.polygons[faceIndex]
        normal = numpy.cross(poly[1][:3] - poly[0][:3], poly[2][:3] - poly[0][:3])
        return normal / numpy.linalg.norm(normal)

    def map3dPointToUV(self, point, normal = None):
        """Wrapper for map3dPointToUV"""
        return map3dPointToUV(self, point, normal)

    def mapUVPointTo3d(self, uv):
        """Wrapper for mapUVPointTo3d"""
        return mapUVPointTo3d(self, uv)

    def map3dPointTo3d(self, mesh, point, normal = None):
        """Wrapper for map3dPointTo3d"""
        return map3dPointTo3d(self, mesh, point, normal)

    def closest_point_on_mesh_normal(self, point):
        """Same as closest_point_on_mesh(), but also gives you the face normal"""
        p, f, _ = self.closest_point_on_mesh(point)
        return p, self.getNormalFromFaceIndex(f), f

class Octree():
    """Implements a basic octree for faster polygon checks.

    Use buildOctree to build an Octree from a list of polygons. You can add new polygons later, 
    but you also have to add them to the list of polygons (e.g. the Mesh) and then use its index to add it.

    bounds: [-x, +x, -y, +y, -z, +z] 

    bot       top
    +---+---+ +---+---+
    | 2 | 3 | | 6 | 7 |
    +---+---+ +---+---+ ^
    | 0 | 1 | | 4 | 5 | y
    +---+---+ +---+---+ +-x->
    
    """
    def __init__(self, bounds, polygon_reference, parent = None, max_depth = 4):
        """Creates a new octree object

        The octree does not have any polygons inside and is not initialized using this, for easier access use buildOctree()

        :param bounds: The maximum and minimum bounds of the octree
        :type bounds: float[6]
        :param polygon_reference: A reference to a list of polygons from which polgons can be added to the octree """
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
        """Inserts a polygon from the polygon reference list into the octree.

        :param polygon_index: The index of the polygon in the reference list
        :type polygon_index: int"""
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
        """Returns a list of all Polygons that are in the space partition of the point
        :param point: The point in the octree
        :type point: float[3]

        :return: A list of the polygon indices on the reference list
        :rtype: list of integers"""
        if not pointInBounds(point, self.bounds):
            return []
        else:
            result = list(self.polygons)
            for node in self.nodes:
                if node is not None:
                    result.extend(node.getPolygonIndices(point))
            return result

    def _getSubtreeBounds(self, index):
        """Returns the bounds of a branch of this octree

        :param index: The index of the branch
        :type index: int
        :return: the subtree bounds
        :rtype: float[6]
        """
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
        """Returns a list of all subtree nodes using recursion

        :return: a list of Octree nodes
        :rtype: list of Octree"""
        l = [self]
        for node in self.nodes:
            if node is not None:
                l.extend(node.listNodes())
        return l

    def getPolygonsUpwards(self):
        """Returns a list of all polygons in this node and all parent nodes up to the root

        :return: A list of polygon indices
        :rtype: list of integers"""
        if self.parent is not None:
            l = list(self.polygons)
            l.extend(self.parent.getPolygonsUpwards())
            return l
        else:
            return self.polygons

    @staticmethod
    def buildOctree(polygons):
        """Builds and fills an octree from the given polygons

        :param polygons: list of polygons that will be saved as a reference
        :type polygons: list of triangles

        :return: A filled octree
        :rtype: mesh.Octree"""
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

class Quadtree:
    """Represents a node in the quadtree in which Polygons can be inserted.
    A Polygon is a list of 3 Points, which consist of 5 floats (x, y, z, u, v).
    Only the uv-coordinates are used for sorting into the quadtree, the rest is 
    for quick access."""
    def __init__(self, left, top, right, bottom):
        """Left, top, right, bottom are the boundaries of this quad"""
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom
        self.children = [None, None, None, None]
        self.polygons = []

    def addPolygon(self, polygon):
        """Inserts a polygon into the quadtree."""
        if self.children[0]:
            if self.children[0].addPolygon(polygon):
                return True
            if self.children[1].addPolygon(polygon):
                return True
            if self.children[2].addPolygon(polygon):
                return True
            if self.children[3].addPolygon(polygon):
                return True
        for p in polygon[...,3:]:
            if p[0] < self.left or p[0] > self.right or p[1] < self.top or p[1] > self.bottom:
                return False
        self.polygons.append(polygon)
        return True

    def getPolygons(self, point):
        """Gives a list of all polygons in the quadtree that may contain the point"""
        p = point
        if p[0] < self.left or p[0] > self.right or p[1] < self.top or p[1] > self.bottom:
            return []
        else:
            result = list(self.polygons)
            if all(self.children):
                result.extend(self.children[0].getPolygons(p))
                result.extend(self.children[1].getPolygons(p))
                result.extend(self.children[2].getPolygons(p))
                result.extend(self.children[3].getPolygons(p))
            return result

    @staticmethod
    def buildQuadtree(depth = 2, left = 0.0, top = 0.0, right = 1.0, bottom = 1.0):
        """Builds a new quadtree recursively with the given depth."""
        node = Quadtree(left, top, right, bottom)
        if depth > 0:
            v = (top + bottom) / 2
            h = (left + right) / 2
            node.children[0] = Quadtree.buildQuadtree(depth - 1, left, top, h, v)
            node.children[1] = Quadtree.buildQuadtree(depth - 1, h, top, right, v)
            node.children[2] = Quadtree.buildQuadtree(depth - 1, left, v, h, bottom)
            node.children[3] = Quadtree.buildQuadtree(depth - 1, h, v, right, bottom)
        return node

    @staticmethod
    def buildUVQuadtreeFromMesh(polygons, depth = 2):
        left  = 0.0
        right = 1.0
        top = 0.0
        bot = 1.0

        for uvs in polygons[...,3:]:
            for uv in uvs:
                left = min(left, uv[0])
                right = max(right, uv[0])
                top = min(top, uv[1])
                bot = max(bot, uv[1])
        qtree = Quadtree.buildQuadtree(depth, left = left, right = right, top = top, bottom = bot)
        for polygon in polygons:
            qtree.addPolygon(polygon)
        return qtree

def polygonInBounds(polygon, bounds):
    """Checks if a polygon is inside of a bounding box

    :param polygon: The polygon to check
    :type polygon: List of 3d-Points
    :param bounds: The sides of the bounding box
    :type bounds: float[6]

    :return: True if the polygon is inside of the bounding box, otherwise False
    :rtype: bool"""
    for p in polygon:
        if not pointInBounds(p, bounds):
            return False
    return True

def pointInBounds(point, bounds):
    """Checks if a given 3d-point is inside of a bounding box
    :param polygon: The point to check
    :type polygon: float[3]
    :param bounds: The sides of the bounding box
    :type bounds: float[6]

    :return: True if the point is inside of the bounding box, otherwise False
    :rtype: bool"""
    if point[0] < bounds[0] \
    or point[0] > bounds[1] \
    or point[1] < bounds[2] \
    or point[1] > bounds[3] \
    or point[2] < bounds[4] \
    or point[2] > bounds[5]:
        return False
    return True

def closestPointOnTriangle(point, t1, t2, t3):
    """Returns the closest point on a triangle to a given point

    :param point: The point
    :type point: float[3]
    :param t1, t2, t3: The points of the triangle
    :type t1, t2, t3: float[3]

    :return: (The point on the triangle, The barycentric coordinates)
    :rtype: (float[3], float[3])
    """
    # http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.104.4264&rep=rep1&type=pdf

    # Get Transformation
    mat = calculatePlaneTransformation(t1, t2, t3)

    # Apply to points
    p1 = multiply_4d_matrix(mat, t1)[1:3]
    p2 = multiply_4d_matrix(mat, t2)[1:3]
    p3 = multiply_4d_matrix(mat, t3)[1:3]

    point_transform = multiply_4d_matrix(mat, point)
    plane_distance = point_transform[0]
    point_plane = point_transform[1:3]

    polygon_point = closestPointOnTriangle2d(point_plane, p1, p2, p3)
    l1, l2, l3 = toBarycentricCoordinates(polygon_point, p1, p2, p3)

    point_3d = fromBarycentricCoordinates(l1, l2, l3, t1, t2, t3)
    return point_3d, (l1, l2, l3)

def closestPointOnTriangle2d(point, p1, p2, p3):
    """Returns the closest point on a 2d triangle

    :param point: The 2d Point in the plane
    :type point: float[2]
    :param p1, p2, p3: The points of the triangle
    :type p1, p2, p3: float[2]

    :return: The point on the triangle that is closest
    :rtype: float[2]"""
    p1p2 = edge_distance(point, p1, p2)
    p2p3 = edge_distance(point, p2, p3)
    p3p1 = edge_distance(point, p3, p1)
    if p1p2 >= 0 and p2p3 >= 0 and p3p1 >= 0:
        return numpy.array(point)
    p1p2_p = _edge_distance_perpendicular(point, p1, p2)
    p2p1_p = _edge_distance_perpendicular(point, p2, p1)
    p2p3_p = _edge_distance_perpendicular(point, p2, p3)
    p3p2_p = _edge_distance_perpendicular(point, p3, p2)
    p3p1_p = _edge_distance_perpendicular(point, p3, p1)
    p1p3_p = _edge_distance_perpendicular(point, p1, p3)

    if p1p2 < 0 and p1p2_p < 0 and p2p1_p < 0:
        return getClosestPointOnLine(point, p1, p2)
    elif p2p3 < 0 and p2p3_p < 0 and p3p2_p < 0:
        return getClosestPointOnLine(point, p2, p3)
    elif p3p1 < 0 and p3p1_p < 0 and p1p3_p < 0:
        return getClosestPointOnLine(point, p3, p1)
    elif p1p2_p > 0 and p1p3_p > 0:
        return numpy.array(p1)
    elif p2p3_p > 0 and p2p1_p > 0:
        return numpy.array(p2)
    elif p3p1_p > 0 and p3p2_p > 0:
        return numpy.array(p3)
    return None

def intersectPointTri2d(point, p1, p2, p3):
    """Checks, if a point is inside of a triangle

    :param point: The 2d Point in the plane
    :type point: float[2]
    :param p1, p2, p3: The points of the triangle
    :type p1, p2, p3: float[2]

    :return: True if the point is inside of the triangle, False if not
    :rtype: bool"""
    p1p2 = edge_distance(point, p1, p2)
    p2p3 = edge_distance(point, p2, p3)
    p3p1 = edge_distance(point, p3, p1)
    if ((p1p2 >= 0) == (p2p3 >= 0) == (p3p1 >= 0)):
        return True
    else:
        return False

def intersectRayTri(p, v, t1, t2, t3):
    """Checks if a Ray intersects a triangle in 3d

    :param p: The origin of the ray
    :type p: float[3]
    :param v: The direction of the ray
    :type v: float[3]
    :param t1, t2, t3: The points of the triangle
    :type t1, t2, t3: float[3]

    :return: (The point of intersection, The barycentric coordinates of the intersection)
    :rtype: (float[3], float[3])"""
    mat = getRotationMatrix(v)
    p1 = numpy.dot(mat, t1)[1:3]
    p2 = numpy.dot(mat, t2)[1:3]
    p3 = numpy.dot(mat, t3)[1:3]
    p = numpy.dot(mat, p)[1:3]
    if intersectPointTri2d(p, p1, p2, p3):
        l1, l2, l3 = toBarycentricCoordinates(p, p1, p2, p3)
        return fromBarycentricCoordinates(l1, l2, l3, t1, t2, t3), (l1, l2, l3)
    return None

def getClosestPointOnLine(point, p1, p2):
    """Returns the closest point to a given point on a line in 2d

    :param point: The point
    :type point: float[2]
    :param p1, p2: The two points defining the line
    :type p1, p2: float[2]

    :return: The closest point on the line
    :rtype: float[2]"""
    p1_point = point - p1
    p1_p2 = p2 - p1
    p1_p2_dist2 = p1_p2[0]**2 + p1_p2[1]**2

    dot = numpy.dot(p1_point, p1_p2)

    t = dot / p1_p2_dist2

    return numpy.array((p1[0] + p1_p2[0] * t, p1[1] + p1_p2[1] * t))

def edge_distance(point, l1, l2):
    """Gives the distance of a point to an edge in 2d

    :param point: The point
    :type point: float[2]
    :param l1, l2: The points defining the line
    :type l1, l2: float[2]

    :return: The distance to the line. This value is negative if the point is to the left of the line
    :rtype: float"""
    return (point[0] - l1[0]) * (l2[1] - l1[1]) - (point[1] - l1[1]) * (l2[0] - l1[0])

def _edge_distance_perpendicular(point, l1, l2):
    """Gives the distance of a point to an edge in 2d, while first transforming the edge by 90 degrees to the right around l1

    :param point: The point
    :type point: float[2]
    :param l1, l2: The points defining the line
    :type l1, l2: float[2]

    :return: The distance to the line. This value is negative if the point is to the left of the line
    :rtype: float"""
    return (point[0] - l1[0]) * (l1[0] - l2[0]) - (point[1] - l1[1]) * (l2[1] - l1[1])

def multiply_4d_matrix(mat, vec):
    """Multiplies a 4d matrix with a vector

    :param mat: The 4d matrix to multiply with
    :type mat: A numpy array with dimensions (4, 4)
    :param vec: The vector to multiply with
    :type vec: A list of floats with 1-4 elements. The vector will be filled with zeros for missing elements 1-3 and with a 1 for element 4

    :return: The multiplied vector in 3d
    :rtype: float[3]"""
    v = numpy.array((0.,0.,0.,1.), dtype=numpy.float32)
    v[0:len(vec)] = vec
    v = numpy.dot(mat, v)
    v /= v[3]
    return v[:3]

def calculatePlaneTransformation(t1, t2, t3):
    """Calculates the transformation matrix of a plane defined by 3 points, that, when multiplied, 
    places t1 on the origin point and rotates it so that the normal is facing the x-Axis

    :param t1, t2, t3: The points of the triangle that define the plane
    :type t1, t2, t3: float[3]

    :return: A 4d matrix describing the transformation
    :rtype: A numpy array with dimensions (4, 4)"""

    # Translation of p1 to origin
    translation_matrix = numpy.identity(4)
    translation_matrix[0][-1] = -t1[0]
    translation_matrix[1][-1] = -t1[1]
    translation_matrix[2][-1] = -t1[2]

    # Rotation of normal to point to x-axis
    # http://math.stackexchange.com/questions/180418/calculate-rotation-matrix-to-align-vector-a-to-vector-b-in-3d
    # TODO: Optimize for 0-values
    a = numpy.cross(t3 - t1, t2 - t1)
    r = getRotationMatrix(a)
    rotation_matrix = numpy.identity(4)
    rotation_matrix[0:3, 0:3] = r

    mat = numpy.dot(rotation_matrix, translation_matrix)
    return mat

def getRotationMatrix(vector):
    """Calculates a rotation matrix for rotating a given vector to the vector (1, 0, 0)

    :param vector: The vector
    :type vector: float[3]

    :return: The rotation matrix
    :rtype: numpy array with dimensions (3, 3)"""
    a = numpy.array(vector, dtype=numpy.float32)
    a_len = numpy.linalg.norm(vector)
    if a_len == 0:
        return numpy.identity(3)
    a /= a_len
    b = numpy.array((1,0,0))
    v = numpy.cross(a, b)
    v_len_2 = numpy.dot(v,v)
    if v_len_2 == 0:
        return numpy.identity(3)
    c = numpy.dot(a, b)
    vx = numpy.array([[0, -v[2], v[1]],[v[2], 0, -v[0]],[-v[1], v[0], 0]])
    r = numpy.identity(3) + vx + numpy.dot(vx,vx) * ((1-c)/(v_len_2))
    return r

def toBarycentricCoordinates(point, t1, t2, t3):
    """Transforms a 2d point into barycentric coordinates of a triangle

    :param point: The point
    :type point: float[2]
    :param t1, t2, t3: The points of the triangle
    :type t1, t2, t3: float[2]

    :return: The barycentric coordinates of the point
    :rtype: float[3]"""
    det = ((t2[1] - t3[1]) * (t1[0] - t3[0]) + (t3[0] - t2[0]) * (t1[1] - t3[1]))
    l1 = ((t2[1] - t3[1]) * (point[0] - t3[0]) + (t3[0] - t2[0]) * (point[1] - t3[1])) / det
    l2 = ((t3[1] - t1[1]) * (point[0] - t3[0]) + (t1[0] - t3[0]) * (point[1] - t3[1])) / det
    l3 = 1 - l1 - l2
    return (l1, l2, l3)

def fromBarycentricCoordinates(l1, l2, l3, t1, t2, t3):
    """Transforms barycentric coordinates of a triangle to a 2d point

    :param l1, l2, l3: The barycentric coordinates
    :type l1, l2, l3: float
    :param t1, t2, t3: The points of the triangle
    :type t1, t2, t3: float[2]

    :return: The 2d-point
    :rtype: float[3]"""
    return l1 * t1 + l2 * t2 + l3 * t3

def distance_sqr(p1, p2):
    """The squared distance between two points

    :param p1, p2: The two points
    :type p1, p2: float[3] or float[2]
    
    :return: The squared distance
    :rtype: float"""
    p = p2 - p1
    return numpy.dot(p, p)

def map3dPointToUV(mesh, point, normal = None):
    """Convert a given 3d-point into uv-coordinates

    :param mesh: The source 3d-mesh on which to project the point before mapping
    :type mesh: Mesh
    :param point: The 3d point which to project onto uv
    :type point: numpy.array (should be 3d)

    :return: The transformed point in uv-space
    :rtype: numpy.array (2d)
    """

    # if normal is None, we don't worry about orthogonal projections
    if normal is None:
        # get point, normal and face of closest point to a given point
        p, f, b = mesh.closest_point_on_mesh(point)
    else:
        p, f, d, b = mesh.raycast(point, normal)
        # if no collision could be detected, return None
        if f == -1:
            return None

    # get the uv-coordinate of the first triangle of the polygon
    A = mesh.polygons[f][0][:3]
    B = mesh.polygons[f][1][:3]
    C = mesh.polygons[f][2][:3]

    # and the uv-coordinates of the first triangle
    uvs = mesh.polygons[f][...,3:]
    U = uvs[0]
    V = uvs[1]
    W = uvs[2]

    # convert 3d-coordinates of point p to uv-coordinates
    p_uv = fromBarycentricCoordinates(b[0], b[1], b[2], U, V, W)

    p_uv_2d = p_uv[:2]

    return numpy.array(p_uv_2d)

def mapUVPointTo3d(mesh, uv):
    """Convert a list of uv-points into 3d. 
    This function is mostly used by interpolateUVTrackIn3D. Note, that 
    therefore, not all points can and have to be converted to 3d points. 
    The return list can therefore have less points than the uv-list. 
    This cleanup can be deactivated by setting cleanup = False. Then, 
    the return-list may contain some [] elements.

    This function makes use of a quadtree cache managed in pam.model.

    :param mesh: The mesh with the uv-map
    :type mesh: Mesh
    :param uv_list: The list of uv-coordinates to convert
    :type uv_list: List of numpy.array (arrays should be 2d)
    :param cleanup: If set to False, unmapped uv-coordinates are 
        removed from the return list
    :type cleanup: bool

    :return: List of converted 3d-points
    :rtype: list of numpy.array or []
    """

    point_3d = None

    # Get uv-quadtree from mesh
    qtree = mesh.uv_quadtree

    point = uv
    polygons = qtree.getPolygons(point)
    for polygon in polygons:
        uvs = polygon[...,3:]
        p3ds = polygon[...,:3]
        result = intersectPointTri2d(
            point,
            uvs[0],
            uvs[2],
            uvs[1]
        )

        if (result):
            l1, l2, l3 = toBarycentricCoordinates(point, uvs[0], uvs[1], uvs[2])
            point_3d = fromBarycentricCoordinates(l1, l2, l3, p3ds[0], p3ds[1], p3ds[2])
            break

    return point_3d

def map3dPointTo3d(mesh1, mesh2, point, normal=None):
    """Map a 3d-point on a given object on another object. Both objects must have the
    same topology. The closest point on the mesh of the first object is projected onto 
    the mesh of the second object.

    :param o1: The source object
    :type o1: bpy.types.Object
    :param o2: The target object
    :type o2: bpy.types.Object
    :param point: The point to transform
    :type point: mathutils.Vector
    :param normal: If a normal is given, the point on the target mesh is not determined 
        by the closest point on the mesh, but by raycast along the normal
    :type normal: mathutils.Vector

    :return: The transformed point
    :rtype: mathutils.Vector
    """

    # if normal is None, we don't worry about orthogonal projections
    if normal is None or numpy.linalg.norm(normal) == 0:
        # get point, normal and face of closest point to a given point
        p, f, b = mesh1.closest_point_on_mesh(point)
    else:
        p, f, d, b = mesh1.raycast(point, normal)
        # if no collision could be detected, return None
        if f == -1:
            return None

    # if o1 and o2 are identical, there is nothing more to do
    if (mesh1 == mesh2):
        return p

    A2 = o2.polygons[f][0][:3]
    B2 = o2.polygons[f][1][:3]
    C2 = o2.polygons[f][2][:3]

    # convert 3d-coordinates of the point
    fromBarycentricCoordinates(b[0], b[1], b[2], A2, B2, C3)
    return p_new
