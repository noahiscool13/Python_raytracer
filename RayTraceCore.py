# Port from https://www.scratchapixel.com/code.php?id=3&origin=/lessons/3d-basic-rendering/introduction-to-ray-tracing
# https://www.scratchapixel.com/lessons/3d-basic-rendering/ray-tracing-rendering-a-triangle/ray-triangle-intersection-geometric-solution
# https://en.wikipedia.org/wiki/M%C3%B6ller%E2%80%93Trumbore_intersection_algorithm


import numpy as np

try:
    import matplotlib.pyplot as plt
except:
    print("NO MATPLOTLIB")

try:
    from tqdm import tqdm
except:
    print("NO TQDM")


    def tqdm(lst):
        for x in lst:
            yield x

from PostProcessing import blend, bloom
from Shaders import *
from SceneObjects import *

from math import *

try:
    from math import inf
except:
    inf = 10 ** 99

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
        hit = tree.k_nearest_neighbours_plane(posHit, 42, hit_object.normal(),
                                              max_dist=0.2)

    col = Vec3(0.0)

    if hit:
        dist_to_photon = hit[-1].distance2(posHit)
        for p in hit:
            # col += p.col / (dist_to_photon * pi) / 150
            col += p.col / (dist_to_photon ** 2 * pi)

    return col


def trace_with_photon_map_indirect(ray, scene):
    hit = ray.intersect(scene)

    if not hit:
        return Vec3(0.0)

    hit_object, hit_t = hit.obj, hit.t

    posHit = ray.after(hit_t - EPSILON)

    new_dir = Vec3.point_on_hemisphere(hit_object.normal())

    return trace_with_photon_map(Ray(posHit, new_dir), scene)


def trace_direct(ray, scene):
    hit = ray.intersect(scene)

    if not hit:
        return Vec3(0.0)

    hit_object, hit_t = hit.obj, hit.t

    posHit = ray.after(hit.t - EPSILON)

    if hit_object.material.smoothNormal:
        u, v = ray.intersect_uv(hit_object)
        normal = hit_object.b.normal * u + hit_object.c.normal * v + hit_object.a.normal * (
                1 - u - v)
        if (ray.origin - posHit).dot(normal) < 0:
            normal = -normal
    else:
        normal = hit_object.normal()

    direct_light = Vec3(0.0)

    direct_light += emittance(hit_object.material)
    direct_light += ambiant(hit_object.material, scene)

    light = scene.random_weighted_light()

    if isinstance(light, Light):

        light.random_translate()

        if check_if_visable(posHit, light.pos, hit_object, scene.objects):
            chance = light.color.length() / scene.total_light()

            light_color = light.color / (
                    (posHit - light.pos).length2() * 4 * pi) / chance

            direct_light += diffuse(normal, posHit, light.pos,
                                    hit_object.material) * light_color
            direct_light += specular(normal, posHit, light.pos, ray.origin,
                                     hit_object.material) * light_color

    elif isinstance(light, Triangle):
        random_surface_point = light.random_point_on_surface()

        if check_if_visable(posHit, random_surface_point, hit_object,
                            scene.objects):
            chance = light.material.Ke.length() * light.area() / scene.total_light()

            triangle_color = light.area() / (
                    (
                            posHit - random_surface_point).length2() * 2 * pi) * light.material.Ke / chance * diffuse(
                light.normal(), random_surface_point, posHit)

            direct_light += diffuse(normal, posHit, random_surface_point,
                                    hit_object.material) * triangle_color
            direct_light += specular(normal, posHit, random_surface_point,
                                     ray.origin,
                                     hit_object.material) * triangle_color

    return direct_light


def trace_initial(ray, scene, depth, light_samples, first=False):
    hit = ray.intersect(scene)

    if not hit:
        return Vec3(0.0)

    hit_object, hit_t = hit.obj, hit.t

    posHit = ray.after(hit_t - EPSILON)

    if hit_object.tex_uv or hit_object.material.smoothNormal:
        u, v = ray.intersect_uv(hit_object)

    if hit_object.tex_uv:
        tex_uv = hit_object.tex_uv
        tex_pos = tex_uv.base + tex_uv.u * u + tex_uv.v * v

    trans_light = Vec3(0)
    if hit_object.material.d:
        if hit_object.material.map_d:
            obj_d = hit_object.material.map_d.get_value(tex_pos)
            obj_d *= obj_d * hit_object.material.d
        else:
            obj_d = hit_object.material.d

        tr = 1-obj_d
        if tr>0:
            skipped_point = ray.after(hit_t + EPSILON)
            new_ray = Ray(skipped_point,ray.direction)

            trans_hit = new_ray.intersect(scene)
            if trans_hit:
                mapped_trans = 1/max(1/(10**20),1-trans_hit.t)-1
                trans_ammount = e**(-mapped_trans*tr)
                trans_light = trace_initial(new_ray,scene,depth,light_samples,False) * trans_ammount

        # if random() >obj_d:
        #     posHit = ray.after(hit_t + EPSILON)
        #     new_ray = Ray(posHit,ray.direction)
        #     return trace_initial(new_ray,scene,depth,light_samples,first)

    if hit_object.material.smoothNormal:
        normal = hit_object.b.normal * u + hit_object.c.normal * v + hit_object.a.normal * (
                1 - u - v)
        if (ray.origin - posHit).dot(normal) < 0:
            normal = -normal
    else:
        normal = hit_object.normal()

    if first and hit_object.material.Ke:
        if hit_object.material.map_Ke:
            obj_emitted = hit_object.material.map_Ke.get_value(tex_pos)
            obj_emitted *= obj_emitted * hit_object.material.Ke
        else:
            obj_emitted = hit_object.material.Ke
    else:
        obj_emitted = Vec3(0)

    total_light = obj_emitted
    total_light += ambiant(hit_object.material, scene)

    if light_samples == "max":
        light_set = scene.all_emmittors_chanced()
    elif light_samples == "positive":
        light_set = scene.all_positive_lights(posHit)
    else:
        light_set = scene.random_weighted_lights(posHit,light_samples)
    direct_light = Vec3(0)
    for src in light_set:
        light = src[0]

        this_light = Vec3(0)

        if isinstance(light, Light):
            light.random_translate()


            if check_if_visable(posHit, light.pos, hit_object, scene):

                if hit_object.material.map_Kd:
                    this_light += diffuse(normal, posHit, light.pos,
                                            hit_object.material) * light.color * \
                                    hit_object.material.map_Kd.get_value(
                                        tex_pos)
                    this_light += specular(normal, posHit, light.pos,
                                             ray.origin,
                                             hit_object.material) * light.color
                else:
                    this_light += diffuse(normal, posHit, light.pos,
                                            hit_object.material) * light.color
                    this_light += specular(normal, posHit, light.pos,
                                             ray.origin,
                                             hit_object.material) * light.color

        elif isinstance(light, Triangle):
            if light == hit_object:
                continue

            light_uv = Vec2.random_uv()
            random_surface_point = light.point_from_uv(light_uv)

            if check_if_visable(posHit, random_surface_point, hit_object,
                                scene):

                if light.material.map_Ke:
                    light_mapped = light.material.map_Kd.get_value(
                                        light_uv)
                else:
                    light_mapped = Vec3(1)

                triangle_color = light.area() * light.material.Ke * diffuse(
                    light.normal(), random_surface_point, posHit) / (2*pi*(random_surface_point-posHit).length2())

                if hit_object.material.map_Kd:
                    this_light += diffuse(normal, posHit, random_surface_point,
                                            hit_object.material) * triangle_color * light_mapped * \
                                    hit_object.material.map_Kd.get_value(
                                        tex_pos)
                else:
                    this_light = diffuse(normal, posHit,
                                            random_surface_point,
                                            hit_object.material) * triangle_color * light_mapped
                this_light += specular(normal, posHit, random_surface_point,
                                     ray.origin,
                                     hit_object.material) * triangle_color * light_mapped
        direct_light += this_light/src[1]
    # direct_light *= len(scene.all_emittors())/len(light_set)

    total_light += direct_light*obj_d + trans_light

    indirect_light = Vec3(0)

    if depth:
        bounce_direction = Vec3.point_on_diffuse_hemisphere(normal)

        indirect_light = trace_initial(Ray(posHit, bounce_direction), scene, depth - 1, light_samples,first=False) * max(bounce_direction.dot(normal), 0) * hit_object.material.Kd

        if hit_object.material.map_Kd:
            indirect_light*= hit_object.material.map_Kd.get_value(
                                        tex_pos)

    return total_light + indirect_light*2


def trace(ray, scene, depth):
    if hasattr(scene, "photon_map"):
        return trace_with_photon_map_indirect(ray, scene)

    hit = ray.intersect(scene)

    if not hit:
        return Vec3(0.0)

    hit_object, hit_t = hit.obj, hit.t

    posHit = ray.after(hit_t - EPSILON)

    if hit_object.material.smoothNormal or hit_object.material.map_Kd or hit_object.material.map_Ke:
        u, v = ray.intersect_uv(hit_object)

    if hit_object.material.map_Kd or hit_object.material.map_Ke:
        tex_uv = hit_object.tex_uv
        tex_pos = tex_uv.base + tex_uv.u * u + tex_uv.v * v

    if hit_object.material.smoothNormal:
        normal = hit_object.b.normal * u + hit_object.c.normal * v + hit_object.a.normal * (
                1 - u - v)
        if (ray.origin - posHit).dot(normal) < 0:
            normal = -normal
    else:
        normal = hit_object.normal()

    direct_light = Vec3(0.0)

    if hit_object.material.map_Ke:
        maped_ke = hit_object.material.map_Ke.get_value(tex_pos)
        direct_light += emittance(hit_object.material) * maped_ke
    else:
        direct_light += emittance(hit_object.material)

    direct_light += ambiant(hit_object.material, scene)

    light = scene.random_weighted_light()

    if isinstance(light, Light):
        # for light in scene.lights:
        light.random_translate()

        if check_if_visable(posHit, light.pos, hit_object, scene.objects):
            if hit_object.material.map_Kd:

                direct_light += diffuse(normal, posHit, light.pos,
                                        hit_object.material,
                                        tex_pos) * light.color
                direct_light += specular(normal, posHit, light.pos, ray.origin,
                                         hit_object.material,
                                         tex_pos) * light.color
            else:
                direct_light += diffuse(normal, posHit, light.pos,
                                        hit_object.material) * light.color
                direct_light += specular(normal, posHit, light.pos, ray.origin,
                                         hit_object.material) * light.color

    elif isinstance(light, Triangle):
        random_surface_point = light.random_point_on_surface()

        if check_if_visable(posHit, random_surface_point, hit_object,
                            scene.objects):
            chance = light.material.Ke.length() * light.area() / scene.total_light()

            triangle_color = light.area() / (
                    (
                            posHit - random_surface_point).length2() * 2 * pi) * light.material.Ke / chance * diffuse(
                light.normal(), random_surface_point, posHit)

            direct_light += diffuse(normal, posHit, random_surface_point,
                                    hit_object.material) * triangle_color
            direct_light += specular(normal, posHit, random_surface_point,
                                     ray.origin,
                                     hit_object.material) * triangle_color

    indirect_light = Vec3(0.0)

    if depth > 0:
        bounce_direction = Vec3.point_on_diffuse_hemisphere(normal)

        indirect_light = trace(Ray(posHit, bounce_direction), scene, depth - 1)

    return direct_light / pi + indirect_light * 2


def render_row(settings):
    y = settings.row
    t = (y, [])
    for x in range(0, settings.width):
        col = Vec3()

        for _ in range(settings.ss):
            x_offset = random()
            y_offset = random()

            xx = (2 * ((
                               x + x_offset + 0.5) * settings.invWidth) - 1) * settings.angle * settings.aspectratio
            yy = (1 - 2 * ((
                                   y + y_offset + 0.5) * settings.invHeight)) * settings.angle

            raydir = Vec3(xx, yy, -1).rotated(Vec3(0, 1, -0.35))
            # raydir = Vec3(xx, yy, -1).rotated(Vec3(0, 1, 0))

            raydir.normalize()
            ray = Ray(settings.scene.camera.point.pos, raydir)

            if settings.mode == "recursive":
                col += trace_initial(ray, settings.scene, 3, light_samples="positive",first=True)
            elif settings.mode == "direct":
                col += trace_direct(ray, settings.scene)

        col /= settings.ss
        t[1].append(col.toList())

    return t


def render(scene, doClip=False, mode="recursive"):
    row_list = []

    width, height = scene.rendersize

    for y in range(0, height):
        row_list.append(
            RowSettings(scene, width=width, height=height, row=y, ss=scene.ss,
                        mode=mode))
    with Pool(7) as p:
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


def progressive_render(scene, batch=1, file=None):
    ss = scene.ss

    scene.ss = batch

    img = render(scene, doClip=False)

    if file:
        save_img(img, file)

    for cycle in tqdm(range((ss - 1) // batch)):
        img = blend([img, render(scene, doClip=False)], [1, 1 / (cycle + 1)])
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
    image = Image.fromarray((np.array(bloom_img) * 255).astype('uint8'), "RGB")
    image.save(file, "PNG")
