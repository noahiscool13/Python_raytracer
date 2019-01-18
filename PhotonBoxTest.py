import unittest
from SceneObjects import *


class PhotonBoxTest(unittest.TestCase):
    def test_nearest_neighbour_one_element(self):
        photons = [Photon(Vec3(0, 0, 0), Vec3(), Vec3())]
        p_list = PhotonList(photons)
        p_box = PhotonBox(p_list)

        nearest = p_box.nearest_neighbour(Vec3(1, 1, 1))

        self.assertEqual(nearest.obj, Photon(Vec3(0, 0, 0), Vec3(), Vec3()), "Cant find photon")

    def test_nearest_neighbour_two_elements(self):
        photons = [Photon(Vec3(0, 0, 0), Vec3(), Vec3()), Photon(Vec3(3, 0, 0), Vec3(), Vec3())]
        p_list = PhotonList(photons)
        p_box = PhotonBox(p_list)

        nearest = p_box.nearest_neighbour(Vec3(2, 0, 0))

        self.assertEqual(nearest.obj, Photon(Vec3(3, 0, 0), Vec3(), Vec3()),
                         "Does not pick closest photon with 2 photons")

    def test_nearest_neighbour_two_elements_dist(self):
        photons = [Photon(Vec3(0, 0, 0), Vec3(), Vec3()), Photon(Vec3(3, 0, 0), Vec3(), Vec3())]
        p_list = PhotonList(photons)
        p_box = PhotonBox(p_list)

        nearest = p_box.nearest_neighbour(Vec3(2, 0, 0))

        self.assertEqual(nearest.t, 1, "Incorrect distance")

    def test_k_nearest_neighbours_count(self):
        photons = [Photon(Vec3(0, 0, 0), Vec3(), Vec3()),
                   Photon(Vec3(1, 0, 0), Vec3(), Vec3()),
                   Photon(Vec3(2, 0, 0), Vec3(), Vec3()),
                   Photon(Vec3(3, 0, 0), Vec3(), Vec3()),
                   Photon(Vec3(4, 0, 0), Vec3(), Vec3()),
                   Photon(Vec3(5, 0, 0), Vec3(), Vec3())]

        p_list = PhotonList(photons)
        p_box = PhotonBox(p_list)

        hits = p_box.k_nearest_neighbours(Vec3(3, 0, 0), 3)

        self.assertEqual(len(hits), 3, "Wrong number of photons found")

    def test_k_nearest_neighbours_1(self):
        photons = [Photon(Vec3(0, 0, 0), Vec3(), Vec3()),
                   Photon(Vec3(1, 0, 0), Vec3(), Vec3()),
                   Photon(Vec3(2, 0, 0), Vec3(), Vec3()),
                   Photon(Vec3(3, 0, 0), Vec3(), Vec3()),
                   Photon(Vec3(4, 0, 0), Vec3(), Vec3()),
                   Photon(Vec3(5, 0, 0), Vec3(), Vec3())]

        p_list = PhotonList(photons)
        p_box = PhotonBox(p_list)

        hits = p_box.k_nearest_neighbours(Vec3(3, 0, 0), 3)

        self.assertEqual(hits[0].t, 0, "Wrong distance to first photon")
        self.assertEqual(hits[0].obj, Photon(Vec3(3, 0, 0), Vec3(), Vec3()), "Wrong first photon")

        findable_photons = [Photon(Vec3(2, 0, 0), Vec3(), Vec3()),
                            Photon(Vec3(4, 0, 0), Vec3(), Vec3())]

        print(hits[2].obj)

        self.assertIn(hits[1].obj, findable_photons, "Wrong second Photon")
        self.assertIn(hits[2].obj, findable_photons, "Wrong third Photon")



if __name__ == '__main__':
    unittest.main()
