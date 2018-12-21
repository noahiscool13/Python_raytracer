from MathUtil import *

class Ray:
    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction

    def intersect(self, other):
        if isinstance(other, Triangle):

            edge1 = other.b - other.a
            edge2 = other.c - other.a

            h = self.direction.cross_product(edge2)
            a = edge1.dot(h)

            if -EPSILON < a < EPSILON:
                return False

            f = 1.0 / a
            s = self.origin - other.a
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

    def after(self, t):
        return self.origin + self.direction * t


class Triangle():
    def __init__(self, a, b, c, Kd=Vec3(0.4), Ks = Vec3(0.6), Ns = 2):
        self.a = a
        self.b = b
        self.c = c
        self.Kd = Kd
        self.Ks = Ks
        self.Ns = Ns

    def normal(self):
        aToB = self.b - self.a
        aToC = self.c - self.a

        return aToB.cross_product(aToC).unit()

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
        self.pos = pos
        self.color = color

    def __str__(self):
        return f"Light<{self.pos} {self.color}>"


class Camera:
    def __init__(self, pos, direction):
        self.pos = pos
        self.direction = direction.unit()


class Scene:
    def __init__(self, triangles, lights, camera):
        self.triangles = triangles
        self.lights = lights
        self.camera = camera
