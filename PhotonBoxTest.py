import unittest
from SceneObjects import *


class PhotonBoxTest(unittest.TestCase):
    def test_nearest_neighbour_one_element(self):
        photons = [Photon(Vec3(0,0,0),Vec3(),Vec3())]
        p_list = PhotonList(photons)
        p_box = PhotonBox(p_list)

        nearest = p_box.nearest_neighbour(Vec3(1,1,1))

        self.assertEqual(nearest.obj, Photon(Vec3(0,0,0),Vec3(),Vec3()), "Cant find photon")

    def test_nearest_neighbour_two_elements(self):
        photons = [Photon(Vec3(0,0,0),Vec3(),Vec3()), Photon(Vec3(3,0,0),Vec3(),Vec3())]
        p_list = PhotonList(photons)
        p_box = PhotonBox(p_list)

        nearest = p_box.nearest_neighbour(Vec3(2,0,0))

        self.assertEqual(nearest.obj, Photon(Vec3(3,0,0),Vec3(),Vec3()))


if __name__ == '__main__':
    unittest.main()
