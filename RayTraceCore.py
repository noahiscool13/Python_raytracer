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

from multiprocessing import Pool

from random import random


def trace(ray, tris, lights, depth):
    tnear = inf
    firstTri = None
    for tri in tris:
        intersection = ray.intersect(tri)

        if intersection is not False:
            if intersection.t < tnear:
                tnear = intersection.t
                firstTri = intersection.obj

    if not firstTri:
        return Vec3(0.0)

    posHit = ray.after(tnear-EPSILON)

    col = Vec3(0.0)

    for light in lights:
        if check_if_in_light(posHit, light, tris):
            if firstTri.material.smoothNormal:
                u, v = ray.intersect_uv(firstTri)
                normal = firstTri.b.normal * u + firstTri.c.normal * v + firstTri.a.normal * (1 - u - v)
                if (ray.origin - posHit).dot(normal) < 0:
                    normal = -normal
            else:
                normal = firstTri.normal()

            col += diffuse(normal, posHit, light.pos, firstTri.material) * light.color
            col += specular(normal, posHit, light.pos, ray.origin, firstTri.material) * light.color
    return col


def render_row(settings):
    y = settings.row
    t = (y, [])
    for x in range(0, settings.width):
        col = Vec3()
        for _ in range(settings.ss):
            x_offset = random()
            y_offset = random()
            xx = (2 * ((x + x_offset + 0.5) * settings.invWidth) - 1) * settings.angle * settings.aspectratio
            yy = (1 - 2 * ((y + y_offset + 0.5) * settings.invHeight)) * settings.angle
            raydir = Vec3(xx, yy, -1)
            raydir.normalize()
            ray = Ray(settings.scene.camera.point.pos, raydir)
            col += trace(ray, settings.scene.objects, settings.scene.lights, 1)
        col /= settings.ss
        t[1].append(clip(col.toList()))
    return t


def render(scene):
    row_list = []

    width, height = scene.rendersize

    for y in range(0, height):
        row_list.append(RowSettings(scene, width=width, height=height, row=y, ss=scene.ss))
    with Pool() as p:
        img = list(tqdm(p.imap(render_row, row_list), total=height))

    img = sorted(img)

    a = []
    for row in img:
        a.append(row[1])
    print(a)
    plt.imshow(a)
    plt.show()
