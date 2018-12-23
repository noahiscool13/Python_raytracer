from MathUtil import *

class Properties:
    def __init__(self,Kd=Vec3(0.4), Ks = Vec3(0.6), Ns = 2, smoothNormal = True):
        self.Kd = Kd
        self.Ks = Ks
        self.Ns = Ns
        self.smoothNormal = smoothNormal

class Point:
    def __init__(self, pos, normal = None):
        self.pos = pos
        if normal:
            self.normal = normal
        else:
            self.normal = Vec3(0)

    def toList(self):
        return self.pos.toList()

class Ray:
    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction

    def intersect(self, other):
        if isinstance(other, Triangle):

            edge1 = other.b.pos - other.a.pos
            edge2 = other.c.pos - other.a.pos

            h = self.direction.cross_product(edge2)
            a = edge1.dot(h)

            if -EPSILON < a < EPSILON:
                return False

            f = 1.0 / a
            s = self.origin - other.a.pos
            u = f * (s.dot(h))

            if u < 0 or u > 1:
                return False

            q = s.cross_product(edge1)
            v = f * self.direction.dot(q)

            if v < 0 or u + v > 1:
                return False

            t = f * edge2.dot(q)

            if t < EPSILON:
                return False

            return t

    def intersect_uv(self, other):
        if isinstance(other, Triangle):
            edge1 = other.b.pos - other.a.pos
            edge2 = other.c.pos - other.a.pos

            h = self.direction.cross_product(edge2)
            a = edge1.dot(h)

            f = 1.0 / a
            s = self.origin - other.a.pos
            u = f * (s.dot(h))

            q = s.cross_product(edge1)
            v = f * self.direction.dot(q)

            return u, v

    def after(self, t):
        return self.origin + self.direction * t


class Triangle():
    def __init__(self, a, b, c, properties = Properties()):
        self.a = a
        self.b = b
        self.c = c
        self.properties = properties

    def add_norm_to_vertices(self):
        norm = self.un_normalized_normal()
        # print(norm,self.a.normal)
        self.a.normal += norm
        self.b.normal += norm
        self.c.normal += norm

    def normal(self):
        return self.un_normalized_normal().unit()

    def un_normalized_normal(self):
        aToB = self.b.pos - self.a.pos
        aToC = self.c.pos - self.a.pos

        return aToB.cross_product(aToC)

    def __str__(self):
        return f"Triangle<{self.a} {self.b} {self.c}>"

    def toList(self):
        return [self.a.toList(), self.b.toList(), self.c.toList()]

    def __iter__(self):
        yield self.a
        yield self.b
        yield self.c


class Light:
    def __init__(self, pos, color):
        self.pos = pos.pos
        self.color = color.pos

    def __str__(self):
        return f"Light<{self.pos} {self.color}>"


class Camera:
    def __init__(self, point):
        self.point = point

class Scene:
    def __init__(self, triangles = [], points = [], lights = [], camera  = None):
        self.triangles = triangles
        self.lights = lights
        self.camera = camera
        self.points = points

    def calc_vertex_normals(self):
        for triangle in self.triangles:
            norm = triangle.un_normalized_normal()
            triangle.a.normal += norm
            triangle.b.normal += norm
            triangle.c.normal += norm

        for point in self.points:
            point.normal.normalize()
