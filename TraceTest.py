from objParser import *
from RayTraceCore import *

if __name__ == '__main__':
    with open("teapot.obj", "r") as file:
        scene = parse_obj(file.read())
    with open("teapot.senario") as file:
        parse_senario(file.read(), scene)
    scene.optimize_scene(amount=20)
    triangles = scene.objects
    lights = scene.lights
    camera = scene.camera

    # for x in triangles:
    #     print(x)
    # print(lights[0])
    render(scene)
