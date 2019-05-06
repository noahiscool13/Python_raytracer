from math import floor
from MathUtil import *

from SceneObjects import KDtree, CompositeObject, Light, Triangle, Photon, Ray, PhotonList, PhotonBox, AAbox
from objParser import parse_obj, parse_senario


class PhotonMap:
    def __init__(self, max_photons):
        self.stored_photons = 0
        self.max_photons = max_photons

        self.photons = []

        self.box = AAbox.large_box()

    def irradiance_estimate(self, pos, normal, max_dist, n_photons):
        iradiance = Vec3()

        nearest_photons = self.locate_photons(pos, n_photons, max_dist)

    def locate_photons(self, pos, n_photons, max_dist):
        dists = [0]*(n_photons+1)
        indexes = [0] * (n_photons + 1)
        dist2 = max_dist**2

    def balance(self):
        if self.stored_photons>1:
            pass

    def balance_segment(self):
        pass


def create_photon_map(scene, global_photons):
    emittors = scene.all_emittors()

    total_light_in_scene = scene.total_light()

    photons_per_light = global_photons / total_light_in_scene

    photon_bounces = []

    for obj in emittors:
        if isinstance(obj, Triangle):
            emitable_photons = floor(obj.material.Ke.avg() * obj.area() * photons_per_light)

            for _ in range(emitable_photons):
                power_per_photon = 1/emitable_photons*obj.material.Ke.avg() * obj.area()

                photon = Photon.generate_random_on_object(obj, power_per_photon, EPSILON)

                photon_bounces += photon.forward(scene, 10)

    return photon_bounces


def add_photon_map_to_scene(scene, global_photons):
    photon_map = create_photon_map(scene, global_photons)
    scene.photon_map = photon_map


def optimize_photon_map(scene, depth):
    scene.photon_map = [KDtree.build(depth, PhotonBox(PhotonList(scene.photon_map)))]


if __name__ == '__main__':
    with open("monte-carlo.obj", "r") as file:
        scene = parse_obj(file.read())
    with open("monte-carlo.senario") as file:
        parse_senario(file.read(), scene)
    scene.optimize_scene(amount=20)

    map = create_photon_map(scene,50)

    map = PhotonList(map)
    map = PhotonBox(map)

    map = KDtree.build(5, map)

    print(map)
