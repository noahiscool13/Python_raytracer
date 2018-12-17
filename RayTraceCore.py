# Port from https://www.scratchapixel.com/code.php?id=3&origin=/lessons/3d-basic-rendering/introduction-to-ray-tracing
# https://www.scratchapixel.com/lessons/3d-basic-rendering/ray-tracing-rendering-a-triangle/ray-triangle-intersection-geometric-solution

from math import tan, pi

import numpy as np

import matplotlib.pyplot as plt

from Shaders import *
from MathUtil import *
from SceneObjects import *

EPSILON = 0.00001

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





def trace(ray, tris, lights, depth):
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

    for light in lights:
        return diffuse(firstTri,posHit,light)

    return Vec3(1,1,1)*1.0



def render(objects, lights, camPos, camDir):
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
            t.append(trace(ray, objects, lights, 1).toList())
        a.append(t)
    a = np.array(a)
    print(a)
    plt.imshow(a)
    plt.show()


triangles = [Triangle(Vec3(1,1,-2),Vec3(0,0,-5),Vec3(0,1,-5))]
lights = [Light(Vec3(0,0,0),Vec3(0.4,0.2,0.6))]
lights = [Light(Vec3(0,0,0),Vec3(1,1,1))]
render(triangles, lights, 0,0)