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


def trace(ray, scene, depth):
    hit = ray.intersect(scene)

    if not hit:
        return Vec3(0.0)

    hit_object, hit_t = hit.obj, hit.t

    posHit = ray.after(hit.t-EPSILON)

    col = Vec3(0.0)

    for light in scene.lights:
        if check_if_in_light(posHit, light, hit_object, scene.objects):
            if hit_object.material.smoothNormal:
                u, v = ray.intersect_uv(hit_object)
                normal = hit_object.b.normal * u + hit_object.c.normal * v + hit_object.a.normal * (1 - u - v)
                if (ray.origin - posHit).dot(normal) < 0:
                    normal = -normal
            else:
                normal = hit_object.normal()

            col += diffuse(normal, posHit, light.pos, hit_object.material) * light.color
            col += specular(normal, posHit, light.pos, ray.origin, hit_object.material) * light.color
            col += emittance(hit_object.material)
            col += ambiant(hit_object.material,scene)
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
            col += trace(ray, settings.scene, 1)
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
    #print(a)
    plt.imshow(a)
    plt.show()
