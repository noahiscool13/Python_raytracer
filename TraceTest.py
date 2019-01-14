from PhotonMap import add_photon_map_to_scene, optimize_photon_map
from objParser import *
from RayTraceCore import *

if __name__ == '__main__':
    with open("monte-carlo.obj", "r") as file:
        scene = parse_obj(file.read())
    with open("monte-carlo.senario") as file:
        parse_senario(file.read(), scene)
    scene.optimize_scene(amount=20)
    imgs = []
    for _ in range(3):
        add_photon_map_to_scene(scene, 10000)
        optimize_photon_map(scene, 50)
        imgs.append(render(scene))

    img = clip(blend(imgs))

    print(img)
    show_img(img)
    save_img(img,"cornellBox3.png")