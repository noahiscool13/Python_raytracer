# Port from https://www.scratchapixel.com/code.php?id=3&origin=/lessons/3d-basic-rendering/introduction-to-ray-tracing
# https://www.scratchapixel.com/lessons/3d-basic-rendering/ray-tracing-rendering-a-triangle/ray-triangle-intersection-geometric-solution
# https://en.wikipedia.org/wiki/M%C3%B6ller%E2%80%93Trumbore_intersection_algorithm



import numpy as np

import matplotlib.pyplot as plt
from tqdm import tqdm

from Shaders import *
from MathUtil import *
from SceneObjects import *

from math import *





def trace(ray, tris, lights, depth):
    tnear = inf
    firstTri = None
    for tri in tris:
        intersection = ray.intersect(tri)

        if intersection is not False:
            if intersection < tnear:
                tnear = intersection
                firstTri = tri

    if not firstTri:
        return Vec3(0.0)

    posHit = ray.after(tnear)

    for light in lights:
        if check_if_in_light(posHit,light,tris):
            return diffuse(firstTri,posHit,light)
    return Vec3(0)



def render(objects, lights, camera):
    a = []
    width = 40
    height = 20
    invWidth = 1 / width
    invHeight = 1 / height
    fov = 30
    aspectratio = width / height
    angle = tan(pi * 0.5 * fov / 180)

    for y in tqdm(range(0, height)):
        t = []
        for x in range(0, width):
            xx = (2 * ((x + 0.5) * invWidth) - 1) * angle * aspectratio
            yy = (1 - 2 * ((y + 0.5) * invHeight)) * angle
            raydir = Vec3(xx, yy, -1)
            raydir.normalize()
            #print(raydir)
            ray = Ray(camera.pos, raydir)
            t.append(trace(ray, objects, lights, 1).toList())
        a.append(t)
    a = np.array(a)
    print(a)
    plt.imshow(a)
    plt.show()

if __name__ == '__main__':

    triangles = [Triangle(Vec3(1,1,-2),Vec3(0,0,-5),Vec3(0,1,-5))]
    lights = [Light(Vec3(0,0,0),Vec3(0.4,0.2,0.6))]
    lights = [Light(Vec3(0,0,0),Vec3(1,1,1))]
    render(triangles, lights, 0,0)