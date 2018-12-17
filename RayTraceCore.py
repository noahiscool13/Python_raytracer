# Port from https://www.scratchapixel.com/code.php?id=3&origin=/lessons/3d-basic-rendering/introduction-to-ray-tracing
# https://www.scratchapixel.com/lessons/3d-basic-rendering/ray-tracing-rendering-a-triangle/ray-triangle-intersection-geometric-solution

from math import tan, pi, sqrt
import numbers

import numpy as np

import matplotlib.pyplot as plt

EPSILON = 0.00001


class Triangle:
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c

    def normal(self):
        aToB = self.b - self.a
        aToC = self.c - self.a

        return aToB.cross_product(aToC).unit()


class Ray:
    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction

    def intersect(self, other):
        if isinstance(other, Triangle):


            normal = other.normal()

            normalDotRayDir = normal.dot(self.direction)

            if abs(normalDotRayDir) < EPSILON:
                return False

            d = normal.dot(other.a)

            t = (normal.dot(self.origin) + d) / normalDotRayDir

            if t < 0:
                return False

            p = self.origin + t * self.direction

            edge0 = other.b - other.a
            vp0 = p - other.a
            c = edge0.cross_product(vp0)
            if normal.dot(c) < 0:
                return False

            edge1 = other.c - other.b
            vp1 = p - other.b
            c = edge1.cross_product(vp1)
            if normal.dot(c) < 0:
                return False

            edge2 = other.a - other.c
            vp2 = p - other.c
            c = edge2.cross_product(vp2)
            if normal.dot(c) < 0:
                return False

            return t

    def after(self,t):
        return self.origin+self.direction*t



class Vec2:

    def __init__(self, xx=None, yy=None):
        if xx is None:
            self.x = 0
            self.y = 0
        elif yy is None:
            self.x = xx
            self.y = xx
        else:
            self.x = xx
            self.y = yy

    def normalize(self):
        length = self.length()
        self.x /= length
        self.y /= length

    def unit(self):
        length = self.length()
        return Vec3(self.x / length, self.y / length)

    def __mul__(self, other):
        if isinstance(other, numbers.Number):
            return Vec2(self.x * other, self.y * other)
        elif isinstance(other, Vec2):
            return Vec2(self.x * other.x, self.y * other.y)

    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def __sub__(self, other):
        return Vec2(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)

    def __neg__(self):
        return Vec2(-self.x, -self.y)

    def length2(self):
        return self.x ** 2 + self.y ** 2

    def length(self):
        return sqrt(self.length2())

    def __rmul__(self, other):
        return self * other

    def __str__(self):
        return f"Vec2<{self.x} {self.y}>"


class Vec3:

    def __init__(self, xx=None, yy=None, zz=None):
        if xx is None:
            self.x = 0
            self.y = 0
            self.z = 0
        elif yy is None:
            self.x = xx
            self.y = xx
            self.z = xx
        else:
            self.x = xx
            self.y = yy
            self.z = zz

    def normalize(self):
        length = self.length()
        self.x /= length
        self.y /= length
        self.z /= length

    def unit(self):
        length = self.length()
        return Vec3(self.x / length, self.y / length, self.z / length)

    def __mul__(self, other):
        if isinstance(other, numbers.Number):
            return Vec3(self.x * other, self.y * other, self.z * other)
        elif isinstance(other, Vec3):
            return Vec3(self.x * other.x, self.y * other.y, self.z * other.z)

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def __sub__(self, other):
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __add__(self, other):
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __neg__(self):
        return Vec3(-self.x, -self.y, -self.z)

    def length2(self):
        return self.x ** 2 + self.y ** 2 + self.z ** 2

    def length(self):
        return sqrt(self.length2())

    def cross_product(self, other):
        return Vec3(self.y * other.z - other.y * self.z,
                    self.z * other.x - other.z * self.x,
                    self.x * other.y - other.x * self.y)

    def __rmul__(self, other):
        return self * other

    def __str__(self):
        return f"Vec3<{self.x} {self.y} {self.z}>"

    def toList(self):
        return [self.x,self.y,self.z]


def trace(ray, tris, depth):
    tnear = 10 ** 10
    firstTri = None
    for tri in tris:
        intersection = ray.intersect(tri)

        if intersection is not False:
            if intersection < tnear:
                tnear = intersection
                firstTri = tri

    if not firstTri:
        return Vec3(0,0,0)

    posHit = ray.after(tnear)
    normalHit = firstTri.normal()

    bias = 1e-4

    return Vec3(1,1,1)*1.0



def render(tris, camPos, camDir):
    a = []
    width = 200
    height = 100
    invWidth = 1 / width
    invHeight = 1 / height
    fov = 30
    aspectratio = width / height
    angle = tan(pi * 0.5 * fov / 180)

    for y in range(0, height):
        t = []
        for x in range(0, width):
            xx = (2 * ((x + 0.5) * invWidth) - 1) * angle * aspectratio
            yy = (1 - 2 * ((y + 0.5) * invHeight)) * angle
            raydir = Vec3(xx, yy, -1)
            raydir.normalize()
            ray = Ray(Vec3(0), raydir)
            t.append(trace(ray, tris, 1).toList())
        a.append(t)
    a = np.array(a)
    print(a)
    plt.imshow(a)
    plt.show()

render([Triangle(Vec3(1,1,-1),Vec3(0,0,-1),Vec3(0,1,-1))],0,0)