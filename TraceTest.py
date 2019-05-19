from PhotonMap import add_photon_map_to_scene, optimize_photon_map
from PostProcessing import sigmoid_scale, basic_tone_map_scale
from objParser import *
from RayTraceCore import *

if __name__ == '__main__':
    with open("glass.obj", "r") as file:
        scene = parse_obj(file.read())
    with open("scenes/north.scenario") as file:
        parse_senario(file.read(), scene)

    # with open("teapot.obj", "r") as file:
    #     scene = parse_obj(file.read())
    # with open("teapot.senario") as file:
    #     parse_senario(file.read(), scene)
    # scene.optimize_scene(amount=20)


    img = render(scene)


    img_a = sigmoid_scale(img)
    img_a = clip(img_a)

    #img = render(scene, True)

    #print(img)
    show_img(img_a)
    save_img(img_a,"r1.png")

    img_b = clip(img)
    show_img(img_b)
    save_img(img_b, "r2.png")