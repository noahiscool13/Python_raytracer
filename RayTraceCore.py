# Port from https://www.scratchapixel.com/code.php?id=3&origin=/lessons/3d-basic-rendering/introduction-to-ray-tracing
# https://www.scratchapixel.com/lessons/3d-basic-rendering/ray-tracing-rendering-a-triangle/ray-triangle-intersection-geometric-solution
# https://en.wikipedia.org/wiki/M%C3%B6ller%E2%80%93Trumbore_intersection_algorithm


import numpy as np

try:
    import matplotlib.pyplot as plt
except:
    print("NO MATPLOTLIB")

from PIL import Image

try:
    from tqdm import tqdm
except:
    print("NO TQDM")
    def tqdm(lst):
        for x in lst:
            yield x

from PostProcessing import blend, blur, bloom
from Shaders import *
from MathUtil import *
from SceneObjects import *

from math import *

from multiprocessing import Pool

from random import random


def trace_with_photon_map(ray, scene):
    hit = ray.intersect(scene)

    if not hit:
        return Vec3(0.0)

    hit_object, hit_t = hit.obj, hit.t

    posHit = ray.after(hit_t - EPSILON)

    hit = None
    dist = inf

    for tree in scene.photon_map:
        hit = tree.k_nearest_neighbours_plane(posHit,100,hit_object.normal(),max_dist=0.2)

    col = Vec3(0.0)

    if hit:
        dist_to_photon = hit[-1].distance2(posHit)
        for p in hit:

            #col += p.col / (dist_to_photon * pi) / 150
            col += p.col / (dist_to_photon*pi)/15

    return col



def trace(ray, scene, depth):
    if hasattr(scene, "photon_map"):
        return trace_with_photon_map(ray, scene)

    hit = ray.intersect(scene)

    if not hit:
        return Vec3(0.0)

    hit_object, hit_t = hit.obj, hit.t

    posHit = ray.after(hit.t-EPSILON)

    if hit_object.material.smoothNormal:
        u, v = ray.intersect_uv(hit_object)
        normal = hit_object.b.normal * u + hit_object.c.normal * v + hit_object.a.normal * (1 - u - v)
        if (ray.origin - posHit).dot(normal) < 0:
            normal = -normal
    else:
        normal = hit_object.normal()

    direct_light = Vec3(0.0)

    direct_light += emittance(hit_object.material)
    direct_light += ambiant(hit_object.material, scene)

    for light in scene.lights:
        light.random_translate()
        if check_if_in_light(posHit, light, hit_object, scene.objects):
            direct_light += diffuse(normal, posHit, light.pos, hit_object.material) * light.color
            direct_light += specular(normal, posHit, light.pos, ray.origin, hit_object.material) * light.color

    indirect_light = Vec3(0.0)

    if depth > 0:
        bounce_direction = Vec3.point_on_hemisphere(normal)

        bounce_ray = Ray(posHit, bounce_direction)

        bounce_hit = bounce_ray.intersect(scene)

        if bounce_hit:

            bounce_hit_pos = bounce_ray.after(bounce_hit.t-EPSILON)

            bounce_light = trace(bounce_ray,scene, depth - 1)

            indirect_light += diffuse(normal, posHit, bounce_hit_pos, hit_object.material) * bounce_light

    # print(indirect_light)

    return direct_light/pi + indirect_light*2


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
            col += trace(ray, settings.scene, 3)
        col /= settings.ss
        t[1].append(col.toList())
    return t


def render(scene, doClip = False):
    row_list = []

    width, height = scene.rendersize

    for y in range(0, height):
        row_list.append(RowSettings(scene, width=width, height=height, row=y, ss=scene.ss))
    with Pool(8) as p:
        img = list(tqdm(p.imap(render_row, row_list), total=height))

    img = sorted(img)

    a = []
    for row in img:
        a.append(row[1])

    if doClip:
        a = clip(a)

    # plt.imshow(a)
    # plt.show()

    return a


def progressive_render(scene, batch=1, file = None):
    ss = scene.ss

    scene.ss = batch

    img = render(scene, doClip=False)

    if file:
        save_img(img, file)

    for cycle in tqdm(range((ss-1)//batch)):
        img = blend([img,render(scene, doClip=False)],[1,1/(cycle+1)])
        if file:
            save_img(img, file)

    img = clip(img)

    scene.ss = ss

    return img

    # plt.imshow(img)
    # plt.show()


def show_img(img):
    plt.imshow(img)
    plt.show()

def save_img(img, file):
    image = Image.fromarray((np.array(clip(img)) * 255).astype('uint8'), "RGB")
    image.save("no_bloom.png", "PNG")
    bloom_img = bloom(img)
    image = Image.fromarray((np.array(bloom_img)*255).astype('uint8'),"RGB")
    image.save(file,"PNG")
