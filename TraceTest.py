from PhotonMap import add_photon_map_to_scene
from objParser import *
from RayTraceCore import *

if __name__ == '__main__':
    with open("monte-carlo.obj", "r") as file:
        scene = parse_obj(file.read())
    with open("monte-carlo.senario") as file:
        parse_senario(file.read(), scene)
    scene.optimize_scene(amount=20)
    #add_photon_map_to_scene(scene, 25000)
    img = progressive_render(scene,batch=100, file="testRender.png")
    show_img(img)
    save_img(img,"testRender.png")