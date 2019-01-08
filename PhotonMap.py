from math import floor

from SceneObjects import KDtree, CompositeObject, Light, Triangle, Photon, Ray
from objParser import parse_obj, parse_senario


def all_emittors(scene):
    emittors = []

    for light in scene.lights:
        emittors.append(light)

    for obj in scene.objects:
        if isinstance(obj, CompositeObject):
            for objc in obj.objects:
                if objc.material.Ke.length2() > 0:
                    emittors.append(objc)
        else:
            if obj.material.Ke > 0:
                emittors.append(obj)

    return emittors


def total_light(emittors):
    total = 0

    for obj in emittors:
        if isinstance(obj, Light):
            total += obj.color.length()

        elif isinstance(obj, Triangle):
            total += obj.material.Ke.length() * obj.area()

    return total


def create_photon_map(scene, global_photons):
    emittors = all_emittors(scene)

    total_light_in_scene = total_light(emittors)

    photons_per_light = global_photons / total_light_in_scene

    photon_bounces = []

    for obj in emittors:
        if isinstance(obj, Triangle):
            emitable_photons = floor(obj.material.Ke.length() * obj.area() * photons_per_light)

            for _ in range(emitable_photons):
                power_per_photon = 1/emitable_photons*obj.material.Ke.length() * obj.area()

                photon = Photon.generate_random_on_object(obj, power_per_photon)

                photon_bounces += photon.forward(scene, 10)

    return photon_bounces


def add_photon_map_to_scene(scene, global_photons):
    photon_map = create_photon_map(scene, global_photons)
    scene.photon_map = photon_map


if __name__ == '__main__':
    with open("monte-carlo.obj", "r") as file:
        scene = parse_obj(file.read())
    with open("monte-carlo.senario") as file:
        parse_senario(file.read(), scene)
    scene.optimize_scene(amount=20)

    print(create_photon_map(scene,50))
    print(len(create_photon_map(scene,50)))