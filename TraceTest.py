from PhotonMap import add_photon_map_to_scene, optimize_photon_map
from objParser import *
from RayTraceCore import *

if __name__ == '__main__':
    with open("house_test.obj", "r") as file:
        scene = parse_obj(file.read())
    with open("tree_obj.senario") as file:
        parse_senario(file.read(), scene)

    # with open("teapot.obj", "r") as file:
    #     scene = parse_obj(file.read())
    # with open("teapot.senario") as file:
    #     parse_senario(file.read(), scene)
    # scene.optimize_scene(amount=20)

    imgs = []
    for _ in range(1):
        #add_photon_map_to_scene(scene, 1000)
        #optimize_photon_map(scene, 50)
        #imgs.append(render(scene, mode="direct"))
        imgs.append(render(scene))



    img = clip(blend(imgs))

    #img = render(scene, True)

    #print(img)
    show_img(img)
    save_img(img,"house1.png")