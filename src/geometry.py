import math
import numpy

####################################################################################################

class Polyhedron:
    """"Polyhedron data container."""

    def __init__(self, vertices, triangles, colors=None):
        self.vertices = list() # ordered list of points
        self.lengths = list() # ordered list of lenghts
        self.triangles = triangles # set of triangles defined as tuples of indices

        if colors is None:
            self.colors = [[1.0, 0.0, 0.0] for i in vertices]
        else:
            self.colors = colors

        for vertex in vertices:
            l = math.sqrt(sum([v*v for v in vertex]))
            self.lengths.append(l)
            self.vertices.append(tuple([v/l for v in vertex]))

    def get_vertices(self):
        for vertex in self.vertices:
            yield vertex

    def get_triangles(self):
        for triangle in self.triangles:
            yield triangle

    def get_triangles_and_normal(self):
        for triangle in self.triangles:
            v = [self.lengths[i] * numpy.array(self.vertices[i])
                 for i in triangle]
            c = numpy.cross(v[0]-v[1], v[0]-v[2])
            if numpy.vdot(c, v[2]) < 0:
                c = -c
            yield triangle, c / numpy.linalg.norm(c)

    def get_vertex(self, index):
        return self.vertices[index], self.lengths[index], self.colors[index]

    def set_vertex(self, index, length, color=None):
        self.lengths[index] = length
        if color is not None:
            self.colors[index] = color


####################################################################################################

class Structures:
    """Structures generator class."""

    @staticmethod
    def icosahedron():
        """Icosahedron generation function"""

        f = (math.sqrt(5.0) + 1.0) / 2.0
        b = math.sqrt(2.0 / (5.0 + math.sqrt(5.0)))
        a = b * f

        return Polyhedron(
                 (( 0, b, a), ( 0, b,-a), ( 0,-b, a), ( 0,-b,-a),
                  ( a, 0, b), ( a, 0,-b), (-a, 0, b), (-a, 0,-b),
                  ( b, a, 0), ( b,-a, 0), (-b, a, 0), (-b,-a, 0)),
             set(((0,  2, 4), (0,  2, 6), (1,  3,  5), (1,  3,  7),
                  (4,  5, 8), (4,  5, 9), (6,  7, 10), (6,  7, 11),
                  (8, 10, 0), (8, 10, 1), (9, 11,  2), (9, 11,  3),
                  (4,  8, 0), (5,  8, 1), (4,  9,  2), (5,  9,  3),
                  (6, 10, 0), (7, 10, 1), (6, 11,  2), (7, 11,  3)))
            )

    @staticmethod
    def sphere(n):
        """Sphere generation function"""

        icosahedron = Structures.icosahedron()
        vertices = icosahedron.vertices
        old_triangles = icosahedron.triangles
        indices = {v: i for i, v in enumerate(vertices)}

        def nm(v1, v2):
            vector = [(v1[i] + v2[i])/2.0 for i in range(0, len(v1))]
            length = math.sqrt(sum((v*v for v in vector)))
            return tuple([v / length for v in vector])

        def index(v):
            if v not in indices:
                indices[v] = len(vertices)
                vertices.append(v)

            return indices[v]

        for i in range(0, n):
            new_triangles = set()

            for t in old_triangles:
                v0 = nm(vertices[t[1]], vertices[t[2]])
                v1 = nm(vertices[t[0]], vertices[t[2]])
                v2 = nm(vertices[t[0]], vertices[t[1]])

                p0 = index(v0)
                p1 = index(v1)
                p2 = index(v2)

                new_triangles.update([(t[0], p1, p2)])
                new_triangles.update([(t[1], p0, p2)])
                new_triangles.update([(t[2], p0, p1)])
                new_triangles.update([(p0, p1, p2)])

            old_triangles = new_triangles

        return Polyhedron(vertices, new_triangles)

####################################################################################################

class Matrices:
    """Matrix generator class."""

    @staticmethod
    def projection(fovy, width, height, near, far):
        s = 1.0 / math.tan(math.radians(fovy) / 2.0)
        sx, sy = s * height / width, s
        zz = (far + near) / (near - far)
        zw = 2 * far * near / (near - far)
        return numpy.matrix([
            [sx,  0,  0,  0],
            [ 0, sy,  0,  0],
            [ 0,  0, zz, zw],
            [ 0,  0, -1,  0]
        ], dtype = numpy.float32)

    @staticmethod
    def transposition(transposition):
        x, y, z = transposition[0], transposition[1], transposition[2]
        return numpy.matrix([
            [1, 0, 0, x],
            [0, 1, 0, y],
            [0, 0, 1, z],
            [0, 0, 0, 1]
        ], dtype = numpy.float32)

    @staticmethod
    def rotation_x(a):
        a = math.radians(a)
        c, s = math.cos(a), math.sin(a)
        return numpy.matrix([
            [1.0, 0.0, 0.0, 0.0],
            [0.0,   c,  -s, 0.0],
            [0.0,   s,   c, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ], dtype = numpy.float32)

    @staticmethod
    def rotation_y(a):
        a = math.radians(a)
        c, s = math.cos(a), math.sin(a)
        return numpy.matrix([
            [  c, 0.0,   s, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [ -s, 0.0,   c, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ], dtype = numpy.float32)

    @staticmethod
    def rotation_z(a):
        a = math.radians(a)
        c, s = math.cos(a), math.sin(a)
        return numpy.matrix([
            [  c,  -s, 0.0, 0.0],
            [  s,   c, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ], dtype = numpy.float32)

